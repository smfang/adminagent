# GuardReasoner Phase 1 Evaluation Plan
## Evaluating GuardReasoner as a Guard Model — Reproduction, Stress-Testing & Failure Analysis

**Version:** 1.0  
**Date:** 2026-07-24  
**Scope:** Phase 1 only — evaluate GuardReasoner itself, not as a judge of other models  
**ETA:** 5–7 days  
**Estimated Cost:** ~$400–$600 (GPU + API)

---

## Objectives

1. **Reproduce** published F1 scores across the 13 benchmark datasets
2. **Confirm** the multi-turn attack vulnerability (ASR >90% claimed by SoK 2025)
3. **Measure** actual latency and throughput under realistic load
4. **Audit** reasoning fidelity — does CoT reasoning align with final verdict?
5. **Compare** 1B / 3B / 8B scaling behavior

---

## Datasets & Benchmarks

### Core 13 (from original paper)
| Dataset | Task | Samples | Notes |
|---------|------|---------|-------|
| HarmBench | Prompt + Response | 239 + 602 | Adversarial |
| ToxicChat | Prompt | 5,083 | Real-world |
| AegisSafetyTest / Aegis2.0 | Prompt + Response | 1,928 + 813 | NVIDIA taxonomy |
| SafeRLHF | Response | 2,000 | |
| BeaverTails | Response | 500 | |
| WildGuardTest | Prompt + Response + Refusal | 1,699 + 1,709 | Mixed |
| XSTest | Prompt + Response | 446 | Extreme cases |
| OpenAIModeration | Prompt | 1,680 | |
| SorryBench | Prompt | 450 | |
| OR-Bench | Prompt | 655 | |

### Stress-Testing Additions
| Dataset | Purpose | Source |
|---------|---------|--------|
| StrongREJECT | Adversarial refusal | 313 samples |
| X-Teaming (multi-turn) | Adaptive session attacks | SoK 2025 |
| Custom obfuscation | Base64, leetspeak, multilingual | Synthetic |
| Jailbreak-Crescendo | Escalating multi-turn | Synthetic |

---

## Test Matrix

### 1. Reproduction Runs

| Model | Benchmarks | Temp | System Prompt | Runs |
|-------|-----------|------|---------------|------|
| GuardReasoner 1B | All 13 | 0.0 | Default | 1 |
| GuardReasoner 3B | All 13 | 0.0 | Default | 1 |
| GuardReasoner 8B | All 13 | 0.0 | Default | 1 |

**Success criteria:**
- 8B F1 within ±2% of published 81.09% (prompt), 81.22% (response), 89.96% (refusal)
- 3B F1 within ±2% of published 80.80%
- If reproduction fails, document divergence and investigate (version mismatch, dataset drift, etc.)

### 2. Multi-Turn Attack Validation

**Goal:** Confirm/refute the SoK 2025 claim that GuardReasoner fails against adaptive multi-turn attacks with ASR >90%.

**Test setup:**
- Use X-Teaming framework from SoK paper
- 100 adversarial conversation sessions per model size
- Pre-filter (input-side) and Post-filter (output-side) configurations
- Metrics: Attack Success Rate (ASR), conversation length at success, failure mode categorization

**Success criteria:**
- Document actual ASR per model size
- If ASR >50%, flag as critical vulnerability
- If ASR <20%, flag as potential SoK methodology issue or version improvement

### 3. Latency & Throughput Benchmarking

**Goal:** Measure real-world inference cost.

**Test setup:**
- Hardware: H100 80GB (single GPU) — match paper's reported hardware
- Batch sizes: 1, 4, 8, 16, 32
- Sequence lengths: 512, 1024, 2048 tokens
- Metrics:
  - Time-to-first-token (TTFT)
  - Time-per-output-token (TPOT)
  - End-to-end latency per query
  - Tokens generated (input + output)
  - Throughput (queries/sec)

**Compare against:**
- Paper's claim: ~4.4s/query on H100
- CoLaGuard (latent reasoning): ~342ms/query
- LLaMA Guard 3 8B (classification baseline)

### 4. Reasoning Fidelity Audit

**Goal:** Does the Chain-of-Thought reasoning actually support the final verdict?

**Methodology:**
- Sample 500 predictions from each model size where CoT is present
- Human annotators (or LLM-as-Judge) rate reasoning quality on:
  1. **Directional consistency:** Does the CoT point toward the final label? (binary)
  2. **Sufficiency:** Is the reasoning sufficient to justify the verdict? (1–5 Likert)
  3. **Accuracy:** Are the facts in the CoT correct? (binary)
- Automated proxy: Extract "harmfulness score" from CoT text, correlate with final label

**Success criteria:**
- Directional consistency ≥90% (authors claim 93.8% human agreement)
- Flag cases where CoT and verdict contradict — these are "reasoning drift" failures

### 5. Scaling Comparison

**Goal:** Understand what the extra parameters buy.

**Analysis:**
- F1 delta: 1B → 3B → 8B
- Per-benchmark improvement: where does scaling help most?
- Latency delta: 1B → 3B → 8B
- Cost-per-query delta (token count × latency)
- Identify "diminishing returns" point

---

## Metrics & Success Criteria

| Metric | Target | Priority |
|--------|--------|----------|
| F1 reproduction (8B) | Within ±2% of paper | P0 |
| ASR (multi-turn) | Document actual value | P0 |
| Latency per query | Document actual vs. claimed 4.4s | P1 |
| Reasoning consistency | ≥90% directional alignment | P1 |
| Scaling efficiency | Identify cost-benefit of 1B/3B/8B | P2 |

---

## Deliverables

1. **Reproduction Report** — F1 scores per benchmark, per model size, with confidence intervals
2. **Vulnerability Report** — Multi-turn ASR, attack patterns that succeed, severity assessment
3. **Performance Benchmark** — Latency, throughput, memory footprint across batch sizes
4. **Reasoning Audit** — Consistency scores, examples of reasoning drift, recommendations
5. **Scaling Analysis** — 1B vs 3B vs 8B cost-benefit breakdown
6. **Phase 1 Summary** — Go/no-go recommendation for Phase 2 (using GuardReasoner as judge)

---

## Timeline

| Day | Task |
|-----|------|
| 1 | Environment setup, model download, seed validation (100-sample holdout) |
| 2 | Run reproduction on all 13 benchmarks for 1B/3B/8B |
| 3 | Multi-turn attack setup (X-Teaming), run 100 sessions per model |
| 4 | Latency benchmarking + reasoning fidelity sample extraction |
| 5 | Reasoning audit (human or LLM-as-Judge), failure categorization |
| 6 | Analysis, visualization, report drafting |
| 7 | Review, final report, Phase 2 go/no-go decision |

---

## Resource Estimate

| Item | Estimate |
|------|----------|
| GPU hours (8× H100) | ~150 hours |
| Cloud cost | ~$300–$400 |
| API costs (if using LLM-as-Judge for reasoning audit) | ~$100–$200 |
| **Total** | **~$400–$600** |

---

## Open Questions Before Start

1. **Which model sizes?** All three (1B/3B/8B) or focus on 8B only?
2. **Hardware access?** Do we have H100s available, or use A100s / cloud?
3. **Multi-turn attack framework?** Use SoK's published X-Teaming code, or build custom?
4. **Reasoning audit method?** Human annotators, GPT-4o-as-Judge, or both?

---

*This is a living document. Revise as findings emerge.*
