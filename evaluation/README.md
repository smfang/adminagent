# Evaluation

Runnable evaluation code, test harnesses, and benchmarks for agentic AI safety.

This directory contains the **infrastructure** used to generate findings. Each subdirectory is a self-contained evaluation module with its own README, requirements, and entry point.

---

## Structure

| Directory | What It Evaluates | Entry Point |
|-----------|------------------|-------------|
| `harness/` | Core evaluation engine — tool guard, guardians, rules, models | `engine.py` |
| `qwenpaw-quick-probe/` | QwenPaw shell command tool guard (50 direct + 30 encoded) | `qwenpaw_quick_probe.py` |
| `qwenpaw-toxicity-benchmark/` | Toxicity classification on 157 agent-output samples | `toxicity_benchmark.py` |
| `adversarial-robustness/` | 8 jailbreak templates × 6 harmful categories | `adversarial_robustness_eval.py` |
| `harmful-manipulation/` | Binary vs. free-form refusal on 6 manipulation categories | `harmful_manipulation_eval.py` |
| `truthfulqa-evaluation/` | Truthfulness on 817 questions across 38 categories | `truthfulqa_harness.py` |
| `evaluation-plans/` | Planned evaluations for targets not yet tested (e.g., GLM) | — |

## Harness Architecture

```
harness/
├── engine.py              # ToolGuardEngine orchestrator
├── models.py              # GuardFinding, GuardSeverity, ToolGuardResult
├── execution_level.py     # STRICT / SMART / AUTO / OFF
├── guardians/
│   ├── rule_guardian.py      # YAML regex signature matching
│   ├── file_guardian.py      # Sensitive file access blocking
│   └── shell_evasion_guardian.py  # Quote-aware obfuscation detection
└── rules/
    └── dangerous_shell_commands.yaml  # 17 rule categories
```

## Quick Start

```bash
# Tool guard probe
python3 evaluation/qwenpaw_quick_probe_standalone.py --mode both

# Adversarial robustness
python3 evaluation/adversarial-robustness/adversarial_robustness_eval.py --model glm

# Toxicity benchmark
python3 evaluation/qwenpaw-toxicity-benchmark/toxicity_benchmark.py

# TruthfulQA
python3 evaluation/truthfulqa-evaluation/truthfulqa_harness.py --model qwen
```

## Relationship to Other Sections

- **`finding/`** contains the distilled results and observations from running these evaluations
- **`framework/`** contains the methodological protocols that guide how evaluations are designed and scored
