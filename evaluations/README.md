# AI Safety Evaluations — adminagent2

This directory contains the unified evaluation framework for agentic AI safety and security testing.

**⚠️ SEPARATE FROM WEBSITE:** This evaluation workspace is independent from the `website/` and `content/` directories used for www.aisafetynode.com deployment. Changes here do not affect the website.

## Structure

| Directory | Purpose |
|-----------|---------|
| `harness/` | Core evaluation engine — tool guard, guardians, rules |
| `qwenpaw-quick-probe/` | Tool guard probing against QwenPaw (completed June 2026) |
| `adversarial-robustness/` | 8 jailbreak templates × 6 harmful categories |
| `harmful-manipulation/` | 6 manipulation category tests |
| `qwenpaw-toxicity-benchmark/` | Toxicity classification benchmark (157 samples) |
| `truthfulqa-evaluation/` | Truthfulness evaluation (817 questions, 38 categories) |
| `evaluation-plans/` | Evaluation plans for specific targets (e.g., GLM) |

## What This Is NOT

This `evaluations/` directory is **independent** from the website deployment at `website/` and `content/`.
- Changes here do **not** affect www.aisafetynode.com
- This is a research workspace, not a production deployment
- The website deployment uses `content/` and `website/` only

## Completed Evaluations

### QwenPaw Tool Guard (June 7, 2026)
- **Direct commands:** 50 (dangerous + benign)
- **Encoded variants:** 30 (base64, hex, unicode, substitution, etc.)
- **Block rate:** 34.5% (default) / 39.3% (hardened)
- **False positives:** 3.8%

### QwenPaw Toxicity Benchmark (June 7, 2026)
- **Samples:** 157 across 12 categories
- **Accuracy:** 43.9% | **Precision:** 29.2% | **Recall:** 92.1% | **FPR:** 71.4%
- **Major issue:** Massive over-flagging on benign shell commands (88%)

## Active Evaluation Plans

- **GLM (z.ai)** — See `evaluation-plans/glm-evaluation-plan.md`

## Quick Start

```bash
cd evaluations
# Run tool guard probe
python3 qwenpaw_quick_probe_standalone.py --mode both
# Run adversarial robustness
python3 adversarial-robustness/run_adversarial_eval.py --model glm
# Run toxicity benchmark
python3 qwenpaw-toxicity-benchmark/run_toxicity_benchmark.py
# Run TruthfulQA
python3 truthfulqa-evaluation/run_truthfulqa.py --model glm
```

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

## Contributing

All evaluation results are published under MIT license. See individual harness READMEs for methodology details.

---

*AI Safety Node — Unified Agentic AI Evaluation Framework v0.2*
