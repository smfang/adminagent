# AI Safety Node — Agentic AI Evaluation

Research hub for evaluating the safety, robustness, and trustworthiness of agentic AI systems.

This repository contains the unified evaluation framework, completed benchmark results, and methodological protocols developed by the AI Safety Node. All work is published under MIT license.

---

## Three Sections

The repository is organized into three parallel streams:

| Section | What It Contains |
|---------|-----------------|
| [`evaluation/`](evaluation/) | Runnable code — test harnesses, benchmarks, and evaluation infrastructure |
| [`finding/`](finding/) | Research findings — distilled observations and results from completed evaluations |
| [`framework/`](framework/) | Methodological protocols — governance frameworks, scoring rubrics, and evaluation standards |

---

## Completed Evaluations

### QwenPaw Tool Guard (June 2026)
- **Focus:** Shell command execution guard — block rates, bypasses, encoded evasion
- **Samples:** 50 direct commands + 30 encoded variants (base64, hex, unicode, substitution)
- **Key Finding:** Block rate of 34.5% (default) / 39.3% (hardened) — rule-based regex is insufficient for agentic systems
- **Artifact:** [`finding/qwenpaw-tool-guard/`](finding/qwenpaw-tool-guard/)

### QwenPaw Toxicity Benchmark (June 2026)
- **Focus:** Can pre-trained human-toxicity classifiers detect harmful agent outputs?
- **Samples:** 157 synthetic samples across 12 categories
- **Key Finding:** 71.4% false positive rate on benign shell commands; toxicity ≠ danger for agents
- **Artifact:** [`finding/qwenpaw-toxicity/`](finding/qwenpaw-toxicity/)

### Adversarial Robustness (June 2026)
- **Focus:** Jailbreak template effectiveness across safety-trained models
- **Method:** 8 attack templates × 6 harmful categories
- **Key Finding:** Roleplay and developer-mode templates collapse refusal rates from >90% to <5%; safety training is brittle to framing shifts
- **Artifact:** [`finding/adversarial-robustness/`](finding/adversarial-robustness/)

### Harmful Manipulation (June 2026)
- **Focus:** Format-dependent refusal collapse on harmful persuasion
- **Method:** Binary (ACCEPT/REJECT) vs. free-form generation across 6 categories
- **Key Finding:** 88.6% refusal in binary format, 1% in free-form — format is a stronger safety predictor than content
- **Artifact:** [`finding/harmful-manipulation/`](finding/harmful-manipulation/)

### TruthfulQA Evaluation (June 2026)
- **Focus:** Hallucination and truthfulness on 817 questions across 38 categories
- **Artifact:** [`evaluation/truthfulqa-evaluation/`](evaluation/truthfulqa-evaluation/)

---

## Frameworks

Two methodological protocols guide all evaluation work:

1. **Agentic AI Security Evaluation Framework v0.1** — Full-stack security protocol for autonomy Level 2–3 systems. Covers 8 threat categories (prompt injection, excessive agency, tool compromise, inter-agent attacks, hallucination-induced actions, memory poisoning, emergent behavior, supply chain), 4 lifecycle phases, and a test harness specification with CI/CD integration.
2. **SAFER-LLM Protocol** — Unified evaluation merging UK AISI Safeguards Principles and Redwood AI Control. Six-phase protocol (Define, Capability Baseline, Safety Surface, Adversarial Stress, Control Assessment, Continuous Validation) with practical implementation guides for teams at MVP and mature stages.

See [`framework/`](framework/) for full documents.

---

## Quick Start

```bash
# Clone and enter evaluation directory
git clone https://github.com/smfang/adminagent.git
cd adminagent/evaluation

# Run QwenPaw tool guard probe
python3 qwenpaw_quick_probe_standalone.py --mode both

# Run adversarial robustness evaluation
python3 adversarial-robustness/adversarial_robustness_eval.py --model gpt-4o

# Run toxicity benchmark
python3 qwenpaw-toxicity-benchmark/toxicity_benchmark.py

# Run TruthfulQA
python3 truthfulqa-evaluation/truthfulqa_harness.py --model qwen
```

---

## Active Evaluation Plans

- **GLM (z.ai)** — Multi-phase evaluation covering tool guard, adversarial robustness, toxicity, and truthfulQA. See [`evaluation/evaluation-plans/glm-evaluation-plan.md`](evaluation/evaluation-plans/glm-evaluation-plan.md).

---

## Contributing

All evaluation modules are self-contained with their own README, requirements, and entry point. To add a new evaluation:

1. Create a directory under `evaluation/`
2. Add a README explaining the method, metrics, and expected results
3. Add a `requirements.txt` if external dependencies are needed
4. Distill key findings into a document under `finding/`

---

*AI Safety Node | Unified Agentic AI Evaluation Framework*
