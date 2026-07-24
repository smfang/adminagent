"""
Structured evaluation run logger.
Records every evaluation run as a timestamped JSON file.
"""
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class EvalMemoryLogger:
    """
    Logger for evaluation runs. Creates structured JSON records
    that can be queried later for continuous learning.
    """

    def __init__(self, target_name: str, records_dir: Optional[str] = None):
        """
        Args:
            target_name: Identifier for the system being evaluated
                         (e.g., "qwenpaw-tool-guard", "adversarial-robustness")
            records_dir: Base directory for storing records. Defaults to
                         evaluation/memory/records/ relative to this file.
        """
        self.target_name = target_name
        self.run_id = str(uuid.uuid4())[:8]
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.finished_at = None

        if records_dir is None:
            records_dir = Path(__file__).parent / "records"
        else:
            records_dir = Path(records_dir)

        self.target_dir = records_dir / target_name
        self.target_dir.mkdir(parents=True, exist_ok=True)

        self.record: Dict[str, Any] = {
            "run_id": self.run_id,
            "target_name": target_name,
            "started_at": self.started_at,
            "finished_at": None,
            "config": {},
            "test_cases": [],
            "summary": {},
            "generated_variants": [],
        }

    def start_run(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Call at the beginning of an evaluation run."""
        self.record["config"] = config or {}
        self.record["config"]["run_id"] = self.run_id

    def log_test_case(
        self,
        test_id: str,
        test_type: str,
        input_data: str,
        expected: str,
        actual: str,
        passed: bool,
        severity: Optional[str] = None,
        bypass_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a single test case result.

        Args:
            test_id: Unique identifier for this test case
            test_type: Category (e.g., "shell_command", "jailbreak", "toxicity")
            input_data: The actual input tested (command, prompt, etc.)
            expected: Expected outcome ("block", "refuse", "flag", etc.)
            actual: Actual outcome ("allow", "comply", "pass", etc.)
            passed: True if test passed (system behaved as expected)
            severity: Optional severity rating ("critical", "high", "medium", "low")
            bypass_type: If failed, what kind of bypass was used
            metadata: Additional structured data (MITRE technique, category, etc.)
        """
        case = {
            "test_id": test_id,
            "test_type": test_type,
            "input_data": input_data,
            "expected": expected,
            "actual": actual,
            "passed": passed,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": severity,
            "bypass_type": bypass_type,
            "metadata": metadata or {},
        }
        self.record["test_cases"].append(case)

    def log_generated_variants(self, variants: List[Dict[str, Any]]) -> None:
        """Log variants that were auto-generated from failures in this run."""
        self.record["generated_variants"].extend(variants)

    def finish_run(self, summary: Optional[Dict[str, Any]] = None) -> str:
        """
        Call at the end of an evaluation run. Saves the record to disk.

        Returns:
            Path to the saved record file.
        """
        self.finished_at = datetime.now(timezone.utc).isoformat()
        self.record["finished_at"] = self.finished_at
        self.record["summary"] = summary or {}

        # Auto-compute aggregate stats
        total = len(self.record["test_cases"])
        passed = sum(1 for tc in self.record["test_cases"] if tc["passed"])
        failed = total - passed
        bypasses = [tc for tc in self.record["test_cases"] if not tc["passed"]]
        bypass_types = {}
        for tc in bypasses:
            bt = tc.get("bypass_type") or "unknown"
            bypass_types[bt] = bypass_types.get(bt, 0) + 1

        self.record["summary"]["total_tests"] = total
        self.record["summary"]["passed"] = passed
        self.record["summary"]["failed"] = failed
        self.record["summary"]["pass_rate"] = passed / total if total > 0 else 0.0
        self.record["summary"]["bypass_type_counts"] = bypass_types
        self.record["summary"]["generated_variant_count"] = len(
            self.record["generated_variants"]
        )

        # Write to file
        ts = self.started_at.replace(":", "").replace("-", "")
        filename = f"{ts}_{self.run_id}.json"
        filepath = self.target_dir / filename

        with open(filepath, "w") as f:
            json.dump(self.record, f, indent=2)

        return str(filepath)

    def get_record(self) -> Dict[str, Any]:
        """Return the in-memory record (useful for inspection before saving)."""
        return self.record
