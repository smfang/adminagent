# -*- coding: utf-8 -*-
"""Tool guard engine – orchestrates all registered guardians.

:class:`ToolGuardEngine` follows the same lazy-singleton pattern used by
the skill scanner.  It discovers and runs all active :class:`BaseToolGuardian`
instances and aggregates their findings into a :class:`ToolGuardResult`.

Usage::

    engine = ToolGuardEngine()
    result = engine.guard("execute_shell_command", {"command": "rm -rf /"})
    if not result.is_safe:
        logger.warning("Tool guard found issues: %s", result.max_severity)

Custom guardians can be registered at construction time or later via
:meth:`register_guardian`.
"""
from __future__ import annotations

import logging
import time
from typing import Any

from ...constant import EnvVarLoader
from .guardians import BaseToolGuardian
from .guardians.file_guardian import FilePathToolGuardian
from .guardians.rule_guardian import RuleBasedToolGuardian
from .guardians.shell_evasion_guardian import ShellEvasionGuardian
from .models import GuardSeverity, ToolGuardResult

logger = logging.getLogger(__name__)

_TRUE_STRINGS = {"true", "1", "yes"}

# ------------------------------------------------------------------
# Optional memory integration
# ------------------------------------------------------------------

try:
    from ..memory.memory_logger import EvalMemoryLogger
except ImportError:
    EvalMemoryLogger = None  # type: ignore[misc,assignment]


def _guard_enabled() -> bool:
    """Return whether tool-call guarding is enabled.

    Priority: env var > config.json > default (True).
    """
    env_val = EnvVarLoader.get_str("QWENPAW_TOOL_GUARD_ENABLED") or None
    if env_val is not None:
        return env_val.lower() in _TRUE_STRINGS

    try:
        from qwenpaw.config import load_config

        cfg = load_config()
        return cfg.security.tool_guard.enabled
    except Exception:
        return True


class ToolGuardEngine:
    """Orchestrates pre-tool-call security guarding.

    Parameters
    ----------
    guardians:
        Explicit list of guardians.  If *None* the default set
        (rule-based) is used.
    enabled:
        Override ``QWENPAW_TOOL_GUARD_ENABLED`` env var.
    """

    def __init__(
        self,
        guardians: list[BaseToolGuardian] | None = None,
        *,
        enabled: bool | None = None,
        memory_logger: "EvalMemoryLogger | None" = None,
    ) -> None:
        self._enabled = enabled if enabled is not None else _guard_enabled()
        self._memory_logger = memory_logger
        self._test_counter = 0

        if guardians is not None:
            self._guardians = list(guardians)
        else:
            self._guardians = self._default_guardians()

        self._reload_tool_sets()

        if self._memory_logger is not None:
            logger.info(
                "ToolGuardEngine initialised with memory logging (target=%s)",
                self._memory_logger.target_name,
            )

    # ------------------------------------------------------------------
    # Default guardians
    # ------------------------------------------------------------------

    @staticmethod
    def _default_guardians() -> list[BaseToolGuardian]:
        """Return the default set of guardians."""
        guardians: list[BaseToolGuardian] = []
        try:
            guardians.append(FilePathToolGuardian())
        except Exception as exc:  # pragma: no cover
            logger.warning(
                "Failed to initialise FilePathToolGuardian: %s",
                exc,
            )
        try:
            guardians.append(RuleBasedToolGuardian())
        except Exception as exc:  # pragma: no cover
            logger.warning(
                "Failed to initialise RuleBasedToolGuardian: %s",
                exc,
            )
        try:
            guardians.append(ShellEvasionGuardian())
        except Exception as exc:  # pragma: no cover
            logger.warning(
                "Failed to initialise ShellEvasionGuardian: %s",
                exc,
            )
        return guardians

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_guardian(self, guardian: BaseToolGuardian) -> None:
        """Register an additional guardian."""
        self._guardians.append(guardian)
        logger.debug("Registered tool guardian: %s", guardian.name)

    def unregister_guardian(self, name: str) -> bool:
        """Remove a guardian by name.  Returns True if found."""
        before = len(self._guardians)
        self._guardians = [g for g in self._guardians if g.name != name]
        return len(self._guardians) < before

    @property
    def guardian_names(self) -> list[str]:
        return [g.name for g in self._guardians]

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    @property
    def guarded_tools(self) -> set[str] | None:
        """Tools in the guard scope.  ``None`` means guard all tools."""
        return self._guarded_tools

    @property
    def denied_tools(self) -> set[str]:
        """Tools unconditionally denied (no approval offered)."""
        return self._denied_tools

    @property
    def auto_denied_rules(self) -> set[str]:
        """Rule IDs that unconditionally deny matched tool calls."""
        return self._auto_denied_rules

    def _reload_tool_sets(self) -> None:
        """Refresh guarded/denied tool and rule sets from config."""
        from .utils import (
            resolve_auto_denied_rules,
            resolve_denied_tools,
            resolve_guarded_tools,
        )

        self._guarded_tools: set[str] | None = resolve_guarded_tools()
        self._denied_tools: set[str] = resolve_denied_tools()
        self._auto_denied_rules: set[str] = resolve_auto_denied_rules()

    def reload_rules(self) -> None:
        """Reload guardian rules and refresh guarded/denied tool sets."""
        for g in self._guardians:
            if hasattr(g, "reload"):
                g.reload()
        self._reload_tool_sets()

    @property
    def memory_logger(self) -> "EvalMemoryLogger | None":
        return self._memory_logger

    @memory_logger.setter
    def memory_logger(self, logger: "EvalMemoryLogger | None") -> None:
        self._memory_logger = logger

    def is_denied(self, tool_name: str) -> bool:
        """``True`` when *tool_name* is unconditionally denied."""
        return tool_name in self._denied_tools

    def should_auto_deny_result(self, result: ToolGuardResult | None) -> bool:
        """``True`` when guard findings hit any configured auto-deny rule."""
        if (
            result is None
            or not result.findings
            or not self._auto_denied_rules
        ):
            return False
        return any(
            finding.rule_id in self._auto_denied_rules
            for finding in result.findings
        )

    def is_guarded(self, tool_name: str) -> bool:
        """``True`` when *tool_name* falls within the guard scope."""
        if self._guarded_tools is None:
            return True
        return tool_name in self._guarded_tools

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def guard(
        self,
        tool_name: str,
        params: dict[str, Any],
        *,
        only_always_run: bool = False,
    ) -> ToolGuardResult | None:
        """Guard a tool call's parameters.

        Parameters
        ----------
        tool_name:
            Name of the tool being called.
        params:
            Keyword arguments that will be passed to the tool function.
        only_always_run:
            When ``True``, only guardians with ``always_run=True`` are
            executed.  Used for tools outside the guarded scope that
            still need path-level checks.

        Returns
        -------
        ToolGuardResult or None
            ``None`` when guarding is disabled.
        """
        if not self._enabled:
            return None

        t0 = time.monotonic()
        result = ToolGuardResult(
            tool_name=tool_name,
            params=params,
        )

        guardians = (
            [g for g in self._guardians if g.always_run]
            if only_always_run
            else self._guardians
        )

        for guardian in guardians:
            try:
                findings = guardian.guard(tool_name, params)
                result.findings.extend(findings)
                result.guardians_used.append(guardian.name)
            except Exception as exc:
                logger.warning(
                    "Tool guardian '%s' failed on tool '%s': %s",
                    guardian.name,
                    tool_name,
                    exc,
                )
                result.guardians_failed.append(
                    {"name": guardian.name, "error": str(exc)},
                )

        result.guard_duration_seconds = time.monotonic() - t0

        # -- optional memory logging ----------------------------------
        if self._memory_logger is not None:
            self._test_counter += 1
            test_id = f"tc_{self._test_counter:04d}"
            cmd = params.get("command", "") or params.get("path", "")
            expected = "block" if result.findings else "allow"
            actual = "block" if result.findings else "allow"
            passed = result.is_safe
            max_sev = result.max_severity
            severity_str = max_sev.value.lower() if max_sev != GuardSeverity.SAFE else None
            bypass_type = None
            if not passed and cmd:
                # Heuristic: if command was blocked by rule guardian,
                # the bypass_type is the encoding used (if any)
                # This is a best-effort inference; explicit metadata is better
                bypass_type = self._infer_bypass_type(cmd)

            self._memory_logger.log_test_case(
                test_id=test_id,
                test_type="shell_command" if tool_name == "execute_shell_command" else tool_name,
                input_data=cmd,
                expected=expected,
                actual=actual,
                passed=passed,
                severity=severity_str,
                bypass_type=bypass_type,
                metadata={
                    "guardians_used": result.guardians_used,
                    "guardians_failed": result.guardians_failed,
                    "findings_count": result.findings_count,
                    "tool_name": tool_name,
                },
            )

        return result

    def _infer_bypass_type(self, command: str) -> str | None:
        """Best-effort inference of bypass encoding from command string."""
        c = command.strip().lower()
        if "base64" in c or "cm0g" in c or "echo" in c and "|" in c:
            return "base64_encoded"
        if "xxd" in c or "|" in c and ("-r" in c or "-p" in c):
            return "hex_encoded"
        if "%" in c and ("urllib" in c or "python" in c):
            return "url_encoded"
        if "tr " in c and "n-za-m" in c:
            return "rot13"
        if "${ifs}" in c or "`" in c:
            return "substitution"
        if "eval" in c:
            return "eval_obfuscation"
        return None

    # ------------------------------------------------------------------
    # Memory helper
    # ------------------------------------------------------------------


_engine_instance: ToolGuardEngine | None = None


def get_guard_engine() -> ToolGuardEngine:
    """Return a lazily-initialised :class:`ToolGuardEngine` singleton."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = ToolGuardEngine()
    return _engine_instance


def get_guard_engine_with_memory(
    target_name: str,
    config: dict[str, Any] | None = None,
) -> ToolGuardEngine:
    """
    Return a :class:`ToolGuardEngine` with evaluation memory logging enabled.

    This is a convenience factory for continuous-learning evaluation runs.
    Each ``guard()`` call is automatically logged to the evaluation memory
    system for later querying and variant generation.

    Parameters
    ----------
    target_name:
        Identifier for the system being evaluated (e.g. "qwenpaw-tool-guard").
    config:
        Optional configuration dict stored with the memory record.

    Returns
    -------
    ToolGuardEngine
        Engine instance with memory logger attached.

    Example
    -------
    >>> engine = get_guard_engine_with_memory("qwenpaw-tool-guard", {"mode": "hardened"})
    >>> result = engine.guard("execute_shell_command", {"command": "rm -rf /"})
    >>> # Each call is automatically logged
    >>> from memory import VariantGenerator
    >>> variants = VariantGenerator().generate_from_record(engine.memory_logger.get_record())
    """
    if EvalMemoryLogger is None:
        raise ImportError(
            "EvalMemoryLogger not available. "
            "Ensure evaluation/memory/ is on the Python path."
        )

    memory_logger = EvalMemoryLogger(target_name)
    memory_logger.start_run(config=config)
    return ToolGuardEngine(memory_logger=memory_logger)


def finish_memory_run(engine: ToolGuardEngine, summary: dict[str, Any] | None = None) -> str:
    """
    Finish an evaluation run and save the memory record.

    Parameters
    ----------
    engine:
        Engine instance that was created via ``get_guard_engine_with_memory``.
    summary:
        Optional summary metrics (e.g. {"block_rate": 0.4, "false_positive_rate": 0.0}).

    Returns
    -------
    str
        Path to the saved record file.
    """
    if engine.memory_logger is None:
        raise ValueError("Engine has no memory logger attached.")
    return engine.memory_logger.finish_run(summary=summary)
