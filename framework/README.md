# Framework

Methodological frameworks, governance structures, and evaluation protocols for agentic AI safety.

These documents define **how** evaluations are structured, scored, and reported — not the code that runs them (see `../evaluation/`) nor the specific results (see `../finding/`).

---

## Documents

| Document | Purpose |
|----------|---------|
| `agentic-ai-evaluation-framework-v0.1.md` | Full-stack security evaluation protocol for autonomy Level 2–3 agentic systems. 8 threat categories, 4 lifecycle phases, test harness specification, CI/CD integration template. |
| `safer-llm-framework.md` | Unified evaluation protocol merging UK AISI Safeguards Principles and Redwood AI Control. Six-phase SAFER-LLM protocol with practical implementation guide for teams at MVP and mature stages. |

## Design Principles

1. **Lifecycle coverage.** Security must be evaluated at every phase — planning, development, deployment, operations — not just at deployment.
2. **Assumed breach.** Evaluate what happens after safeguards fail. Defense in depth, cascade containment.
3. **Evidence diversity.** No single test is sufficient. Each safety claim requires multiple independent lines of evidence.
4. **Usefulness-safety tradeoff.** Measure both. A perfectly safe system that cannot complete tasks is not useful; a perfectly useful system that is unsafe is not deployable.

## Relationship to Other Sections

- **`evaluation/`** implements the test harnesses and benchmarks described in these frameworks
- **`finding/`** documents the concrete discoveries produced by applying these frameworks to specific systems
