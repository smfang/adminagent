# Unified LLM Safety Evaluation Framework: Integrating AISI Safeguards Principles and Redwood AI Control

> **Version:** 1.0 | **Date:** 2025-06-05
> **Target Audience:** Teams building evaluation infrastructure for LLM systems (agents, chatbots, coding assistants, multimodal systems)
> **Scope:** General-purpose LLM evaluation — not limited to frontier models or code backdoors

---

## Executive Summary

This document proposes a unified evaluation framework that merges two rigorous safety methodologies — the UK AISI's **Principles for Evaluating Misuse Safeguards** and Redwood Research's **AI Control** methodology — with standard LLM evaluation practices (capability benchmarks, safety red-teaming, behavioral evaluation). The goal is to produce a practical, actionable guide for evaluation infrastructure builders.

**Core insight:** Current LLM evaluation is fragmented. Capability benchmarks (MMLU, HELM) measure what models *can* do. Safety red-teaming finds *some* failures. Behavioral evaluation captures *surface* properties. What's missing is a systematic way to evaluate whether safeguards *actually work* against realistic, resourceful adversaries — and whether the model itself can be trusted to participate in its own safety. This framework fills that gap.

---

## Part 1: Key Elements from AISI "Principles for Evaluating Misuse Safeguards"

### Element 1: Requirement-Driven Evaluation (Step 1 — State Safeguard Requirements)

**What it is:** Before any evaluation, clearly define: (a) unacceptable outcomes, (b) threat actors and attack scenarios, (c) assumptions about deployment context.

**General LLM mapping:**
- **Unacceptable outcomes** → For a chatbot: generating instructions for self-harm, producing hate speech, leaking PII. For a coding assistant: generating exploit code, inserting backdoors, exposing API keys. For an agent: unauthorized data exfiltration, privilege escalation.
- **Threat actors** → Not just "hackers" — consider: curious users probing boundaries, competitors extracting training data, automated jailbreak pipelines, fine-tuning attackers.
- **Assumptions** → Deployment channel (API vs. consumer app), user authentication level, rate limits, content filtering layers, monitoring capabilities.

**Practical implementation:**
```
For each LLM deployment, maintain a "Safety Requirements Document" with:
- Risk taxonomy (e.g., CBRN, cyber, bias, privacy, misinformation)
- Per-risk: unacceptable outcomes, threat actor profiles, deployment assumptions
- Thresholds: what failure rate is acceptable? (e.g., <0.1% for PII leakage)
```

---

### Element 2: Defense-in-Depth Safeguards Planning (Step 2 — Establish Safeguards Plan)

**What it is:** Three layers of safeguards: system-level (refusal training, unlearning, classifiers), access-level (monitoring, verification, banning), and maintenance-level (usage monitoring, incident reporting, bug bounties, rapid remediation).

**General LLM mapping:**
- **System safeguards** → Input/output filtering (e.g., Llama Guard, Prompt Guard), RLHF refusal training, context window monitoring, tool-use restrictions.
- **Access safeguards** → API key validation, rate limiting, user tiering (free vs. paid), deployment region restrictions, watermarking for generated content.
- **Maintenance safeguards** → Automated abuse detection pipelines, external security audits, vulnerability disclosure programs, model rollback procedures, incident response playbooks.

**Practical implementation:**
```
For each deployment, build a "Safeguards Matrix":
Rows: Risk categories (toxicity, PII, code exploits, misinformation)
Columns: System | Access | Maintenance
Cells: Specific safeguard + evidence requirement + owner
```

---

### Element 3: Evidence-Based Sufficiency Assessment (Step 3 — Collect Evidence + Step 5 — Decide Sufficiency)

**What it is:** Multiple independent pieces of evidence per requirement, diverse evidence types, internal/external validity checks, and third-party assessors. No single evaluation is sufficient.

**General LLM mapping:**
- **Multiple evidence types per risk** → For toxicity: (1) standard benchmark (ToxicityBench), (2) adversarial red-teaming (HarmBench), (3) human evaluation of edge cases, (4) automated classifier (Perspective API), (5) production monitoring data.
- **Internal validity** → Does the evaluation actually measure what it claims? (e.g., does the jailbreak prompt actually bypass the safeguard, or just trigger a different refusal?)
- **External validity** → Do results generalize to real deployment? (e.g., synthetic adversarial examples vs. actual user behavior)
- **Third-party assessors** → Independent red teams, external audit firms, academic researchers, bounty hunters.

**Practical implementation:**
```
Evidence checklist per risk category:
□ Automated benchmark (quantitative baseline)
□ Adversarial stress test (worst-case probing)
□ Human evaluation (nuanced judgment)
□ Production monitoring (real-world validation)
□ Third-party independent assessment
□ Cross-model comparison (is this model worse than peers?)
```

---

### Element 4: Post-Deployment Continuous Assessment (Step 4 — Post-Deployment Plan)

**What it is:** Pre-specified evaluation frequency, trigger conditions (new attack patterns, model updates), invalidation conditions (when evidence is no longer valid), and response plans (rollback, patch, communication).

**General LLM mapping:**
- **Frequency** → Daily automated checks for known jailbreaks; weekly A/B test of safety classifiers; monthly third-party red team; quarterly full evaluation suite.
- **Triggers** → New jailbreak technique published on Twitter/X; spike in policy violation reports; competitor model release; regulatory change (EU AI Act updates); model fine-tuning or architecture change.
- **Invalidation** → If a new attack class emerges (e.g., "multi-turn context injection"), all previous evaluations for "prompt injection resistance" are invalidated.
- **Response plans** → Automated: rollback to previous model version if safety regression > threshold. Manual: incident response team activation, public disclosure, regulator notification.

**Practical implementation:**
```
Continuous Evaluation Registry:
- Schedule: Automated (daily) | Semi-automated (weekly) | Manual (quarterly)
- Triggers: [list of conditions that trigger immediate re-evaluation]
- Invalidation rules: [what invalidates past evidence]
- Response playbooks: [per-risk response procedures]
```

---

### Element 5: Red-Teaming Best Practices (Evidence Collection)

**What it is:** Realistic deployment conditions, component + combined testing, "assumed breach" mindset, commensurate attacker resources, independent teams, documented incentives, and explicit evaluation of security-through-obscurity reliance.

**General LLM mapping:**
- **Realistic deployment** → Test the *full* system, not just the model weights. Include API wrapper, rate limits, monitoring systems, human review loops, tool integrations.
- **Component + combined testing** → Test safety classifier alone; test model alone; test both together; test with monitoring backend; test with human escalation.
- **Assumed breach** → Assume the model *will* be jailbroken. Assume the classifier *will* have false negatives. What happens then? (Defense in depth)
- **Commensurate resources** → Red team should have time, compute, and expertise comparable to real threat actors. For a production chatbot, this means weeks of effort, not hours.
- **Document incentives** → Red team members should be rewarded for finding failures, not for confirming safety. No "pass/fail" pressure.
- **Security through obscurity** → If safety relies on "attackers not knowing our prompt format" or "our system prompt is secret," this must be explicitly flagged as a weakness and separately evaluated.

**Practical implementation:**
```
Red Team Charter (per engagement):
- Scope: [what's in bounds — API, model, UI, monitoring, etc.]
- Duration: [calendar time + compute budget]
- Incentives: [bounty structure, no penalties for finding failures]
- Independence: [team separation from model development]
- Success criteria: [number of unique failures found, not "pass/fail"]
- Obscurity audit: [explicitly test what happens if system details leak]
```

---

### Element 6: Diverse Evidence and Independent Validation

**What it is:** Evidence should be diverse in methodology (automated, manual, static, dynamic), scope (single-turn, multi-turn, tool-augmented), and source (internal, external, academic, industry). Third-party assessors should be genuinely independent (no financial conflicts, no shared organizational incentives).

**General LLM mapping:**
- **Diverse methodology** → Static analysis of training data; dynamic interaction testing; model introspection (probing hidden states); behavioral consistency checks.
- **Diverse scope** → Single-turn prompts; multi-turn conversations; tool-augmented agents; RAG systems; multi-modal inputs (images + text).
- **Diverse source** → Internal safety team; external red team; academic researchers; bounty program participants; automated scanners (e.g., Garak, PyRIT).

**Practical implementation:**
```
Evidence Diversity Scorecard:
For each risk, score evidence diversity:
- Methodology diversity: [1-5] (automated, manual, static, dynamic, introspection)
- Scope diversity: [1-5] (single-turn, multi-turn, tool-augmented, RAG, multimodal)
- Source diversity: [1-5] (internal, external, academic, bounty, automated)
- Total: Target ≥ 12/15 for high-risk categories
```

---

## Part 2: Key Elements from Redwood Research "AI Control"

### Element 7: The U-T-H Resource Model (Untrusted Model, Trusted Model, Human Labor)

**What it is:** Three resources are available: (U) an untrusted model that may intentionally subvert safety, (T) a trusted model that is weaker but aligned, and (H) limited high-quality human labor.

**General LLM mapping:**
- **U (Untrusted)** → The main LLM being deployed (e.g., GPT-4, Claude, open-source fine-tune). It may have been trained on poisoned data, instructed to appear safe while being harmful, or have emergent deceptive capabilities.
- **T (Trusted)** → A smaller, weaker, but more trusted model (e.g., Llama 3 8B, a rule-based system, a safety classifier). It cannot do the main task but can monitor, edit, or audit.
- **H (Human)** → Limited human reviewers, safety engineers, or domain experts. Their time is scarce and expensive.

**Practical implementation:**
```
Resource allocation for each deployment:
- U: [main model ID + version + known limitations]
- T: [monitoring model ID + capability profile + trust basis]
- H: [available hours per week + expertise areas + escalation paths]
- Budget: T is cheap; H is expensive; U is "free" but risky
```

---

### Element 8: Trusted Monitoring Protocol (T monitors U)

**What it is:** The trusted model (T) monitors outputs from the untrusted model (U) for suspicious patterns, safety violations, or policy breaches. T can flag outputs for human review or block them automatically.

**General LLM mapping:**
- **T as safety classifier** → Llama Guard, Prompt Guard, or a custom fine-tuned model that classifies U's outputs as safe/unsafe. T is weaker than U but trained specifically for safety detection.
- **T as consistency checker** → T re-evaluates U's reasoning. If U says "2+2=4" in a math tutoring app, T checks the math. If U generates code, T runs static analysis.
- **T as policy enforcer** → T has access to a formal policy document and checks U's outputs against explicit rules (e.g., "no medical advice," "no PII").

**Practical implementation:**
```
Trusted Monitoring Setup:
- Monitor type: [classifier / consistency checker / policy enforcer]
- T model: [specific model ID + training data description]
- Latency budget: [T must respond in <X ms]
- Action on flag: [block / human review / log-only / rate-limit]
- Escalation: [when T is uncertain, route to H]
- Known failure modes: [T may miss subtle attacks; U may fool T with plausible deniability]
```

---

### Element 9: Untrusted Monitoring with Collusion Prevention (U monitors U)

**What it is:** The untrusted model monitors its own outputs, but safeguards prevent it from colluding with itself or covering up its own failures. This is a force-multiplier for scarce trusted resources.

**General LLM mapping:**
- **Self-critique with isolation** → U generates an output, then a *separate* instance of U (with different system prompt, no shared context) critiques it. The two instances cannot communicate.
- **Chain-of-thought auditing** → If U produces chain-of-thought reasoning, a separate process (not U) extracts it and checks for hidden reasoning, scheming, or deceptive plans.
- **Debate / adversarial verification** → Two instances of U argue about whether an output is safe. A third (trusted) arbiter decides. The instances are isolated to prevent collusion.

**Practical implementation:**
```
Untrusted Monitoring with Isolation:
- Instance separation: [different system prompts, different seeds, no shared context]
- Communication barriers: [no state between calls, no tool access for monitoring]
- Verdict aggregation: [how to combine multiple U monitors]
- Trust boundary: [what is the trusted base that prevents collusion?]
- Collusion test: [red-team attempt to make two U instances collude]
```

---

### Element 10: Trusted Editing (T edits U output)

**What it is:** Rather than just flagging unsafe outputs, T actively modifies U's outputs to make them safe while preserving usefulness. This is a more aggressive but potentially more useful intervention.

**General LLM mapping:**
- **T as sanitizer** → U generates text with potential PII; T redacts PII while preserving meaning.
- **T as rephraser** → U generates an answer that skirts policy; T rephrases it to be compliant.
- **T as code fixer** → U generates code with a potential vulnerability; T patches it.
- **Tradeoff:** T may introduce errors, reduce quality, or change meaning. The usefulness-safety tradeoff must be measured.

**Practical implementation:**
```
Trusted Editing Pipeline:
- Edit type: [redaction / rephrasing / patching / restructuring]
- T model: [specific model + training for editing task]
- Quality check: [measure usefulness before and after editing]
- Safety check: [measure safety before and after editing]
- Human review trigger: [when edit confidence is low]
- Rollback: [if edited output is worse than blocked output]
```

---

### Element 11: Usefulness-Safety Tradeoff Metrics (Pareto Frontier)

**What it is:** Two key metrics: (1) usefulness = correctness rate / task completion rate, and (2) safety = probability no backdoor / harmful output is submitted. The goal is to map the Pareto frontier — what safety can be achieved at each usefulness level?

**General LLM mapping:**
- **Usefulness** → Standard capability metrics: accuracy on MMLU, HumanEval pass rate, customer satisfaction score, task completion rate.
- **Safety** → Probability of harmful output on adversarial inputs, false negative rate of safety classifier, backdoor detection rate, rate of policy violations in production.
- **Tradeoff visualization** → For each protocol (monitoring, editing, auditing), plot usefulness vs. safety. A good protocol pushes the frontier outward (more safety at same usefulness, or more usefulness at same safety).

**Practical implementation:**
```
Evaluation Dashboard:
- X-axis: Usefulness (task completion rate, accuracy, user satisfaction)
- Y-axis: Safety (1 - attack success rate, 1 - policy violation rate)
- Curves: Baseline (no safeguards) | Trusted Monitoring | Untrusted Monitoring | Trusted Editing | Combined Protocol
- Target: Combined protocol should dominate all individual protocols
- Decision rule: Accept protocol if safety > threshold AND usefulness > threshold
```

---

### Element 12: Control Evaluation Methodology (Simulate Attacks, Measure Real Usefulness)

**What it is:** Safety is measured by *simulating* with an attack policy (worst-case scenario). Usefulness is measured with the *real* model (average-case scenario). This separates the two concerns and allows realistic safety assessment without degrading real-world performance.

**General LLM mapping:**
- **Attack policy construction** → Red team builds a structured attack policy: given input X, the policy tries to produce harmful output Y using hidden reasoning, prompt injection, multi-turn manipulation, etc. The policy has limited capabilities (parsing, comparisons, RNG) but no tools or state between calls.
- **Safety measurement** → Run the system (U + safeguards) against the attack policy. Measure what fraction of attacks succeed. This is a *lower bound* on real safety (real attackers may be more creative).
- **Usefulness measurement** → Run the real model on normal tasks. Measure task completion rate, accuracy, user satisfaction. This is an *upper bound* on real usefulness (real users may have harder tasks).
- **Key insight:** Don't measure safety and usefulness on the same distribution. Safety needs worst-case; usefulness needs average-case.

**Practical implementation:**
```
Control Evaluation Protocol:
1. Red team constructs attack policy:
   - Attack types: [jailbreak, prompt injection, multi-turn, tool abuse, data extraction]
   - Policy constraints: [no tool access, no state between calls, limited compute]
   - Success criteria: [what constitutes a successful attack?]
2. Run attack policy against system:
   - System configuration: [U + T + safeguards + monitoring]
   - Number of attempts: [sufficient for statistical power]
   - Safety score: [attack success rate, by attack type]
3. Run real tasks:
   - Task distribution: [sampled from production logs or benchmark]
   - Usefulness score: [task completion rate, accuracy, satisfaction]
4. Plot and decide:
   - Is safety above threshold? (e.g., <1% attack success)
   - Is usefulness above threshold? (e.g., >95% task completion)
   - If both: deploy. If not: iterate on safeguards.
```

---

## Part 3: Unified Framework Structure — The SAFER-LLM Evaluation Protocol

### Overview

We propose **SAFER-LLM** (Systematic Assessment Framework for Evaluating Robustness of LLMs) — a six-phase evaluation protocol that integrates AISI's safeguards planning, Redwood's control methodology, and standard LLM evaluation practices.

---

### Phase 0: Define (Before Any Evaluation)

**Goal:** Establish what you're evaluating against.

| Step | Action | Output |
|------|--------|--------|
| 0.1 | Define unacceptable outcomes per risk category | Safety Requirements Document |
| 0.2 | Define threat actors and attack scenarios | Threat Model Document |
| 0.3 | Define deployment assumptions | Deployment Context Specification |
| 0.4 | Define acceptable risk thresholds (quantitative where possible) | Risk Tolerance Matrix |
| 0.5 | Define safeguards plan (system + access + maintenance) | Safeguards Matrix |

**Tools:** Risk taxonomy (MIT AI Risk Repository), deployment checklists, policy documents.

---

### Phase 1: Capability Baseline (Standard Practice)

**Goal:** Measure what the model *can* do on standard tasks.

| Evaluation | Standard Benchmarks | What It Measures |
|------------|-------------------|------------------|
| General knowledge | MMLU, HELM, BigBench | Breadth of knowledge |
| Reasoning | GSM8K, MATH, HumanEval | Problem-solving, code generation |
| Multilingual | XCOPA, XLSum | Cross-lingual capability |
| Agentic | SWE-bench, AgentBench | Tool use, task completion |
| Efficiency | FLOPs, latency, memory | Resource usage |

**Mapping to AISI/Redwood:** This is the "usefulness" baseline. It defines what the model is capable of, which sets the upper bound on what harm it could cause. It also defines the gap between U (untrusted, capable) and T (trusted, weaker).

---

### Phase 2: Safety Surface (Standard Practice + AISI Enhancement)

**Goal:** Measure *surface* safety properties — what the model appears to do under normal conditions.

| Evaluation | Standard Benchmarks | AISI Enhancement |
|------------|-------------------|------------------|
| Refusal | HH-RLHF, SafetyBench | Document *why* refusal is required per threat actor |
| Toxicity | ToxiGen, BOLD | Test against *realistic* toxicity, not just synthetic |
| Bias | BBQ, StereoSet | Test intersectional bias, not just single-axis |
| Privacy | PII extraction, memorization | Test with *real* PII patterns, not just templates |
| Truthfulness | TruthfulQA, HaluEval | Test in *deployment-like* contexts (RAG, multi-turn) |

**AISI Enhancement:** Each evaluation must map to a specific safeguard requirement. Don't run SafetyBench "because it's standard" — run it to verify that "system safeguard #3 (input classifier) detects toxic outputs with <1% false negative rate."

---

### Phase 3: Adversarial Stress (AISI Red-Teaming + Standard Practice)

**Goal:** Find failures under adversarial conditions.

| Evaluation | Standard Practice | AISI Best Practice | Redwood Enhancement |
|------------|-------------------|--------------------|--------------------|
| Jailbreak | GCG, PAIR, AutoDAN | Test *full system* (API + model + monitoring) | Attack policy with structured hidden reasoning |
| Prompt injection | Hijack benchmarks | Test component + combined | Simulate attacker with limited parsing/comparison tools |
| Multi-turn manipulation | Multi-turn benchmarks | Test realistic conversation lengths | Test collusion resistance between model instances |
| Data extraction | Membership inference | Test with *real* deployment data | Measure extraction under "assumed breach" |
| Tool abuse | Agent benchmarks | Test with monitoring backend | Test if U can exploit tool access while T watches |

**AISI Best Practice:** Red team must have documented independence, commensurate resources, and explicit evaluation of security-through-obscurity assumptions.

**Redwood Enhancement:** Construct formal attack policies that use structured reasoning. Measure safety by simulation, not just by anecdote.

---

### Phase 4: Control Assessment (Redwood AI Control + AISI Evidence)

**Goal:** Evaluate whether safeguards *actually work* when the model tries to subvert them.

| Protocol | Description | Metrics |
|----------|-------------|---------|
| **Trusted Monitoring (T monitors U)** | T classifies/filter U outputs | Safety = 1 - false negative rate; Usefulness = 1 - false positive rate |
| **Untrusted Monitoring (U monitors U)** | Separate U instances critique each other with isolation | Collusion resistance rate; Coverage of self-critique |
| **Trusted Editing (T edits U)** | T modifies U outputs to be safe | Safety improvement; Usefulness preservation; Edit quality |
| **Upfront Auditing (H reviews)** | Human experts review before deployment | Audit coverage; Time to audit; Human catch rate |

**Evidence Requirements (from AISI):**
- Multiple evidence types per protocol: automated stress tests, manual red-teaming, production monitoring, third-party validation.
- Diverse scope: single-turn, multi-turn, tool-augmented, RAG, multimodal.
- Independent validation: External team replicates the control evaluation.

**Tradeoff Analysis:**
```
For each protocol, produce a Pareto frontier:
- X: Usefulness (task completion rate on real tasks)
- Y: Safety (1 - attack success rate on simulated attacks)
- Compare: Baseline (no safeguards) vs. Protocol A vs. Protocol B vs. Combined
- Decision: Combined protocol must be above both thresholds and dominate individual protocols
```

---

### Phase 5: Continuous Validation (AISI Post-Deployment + Standard Practice)

**Goal:** Ensure safety doesn't degrade over time.

| Component | Frequency | Triggers | Response |
|-----------|-----------|----------|----------|
| Automated monitoring | Continuous | Spike in violations | Auto-throttle, alert |
| Automated benchmark | Daily | New model version | Compare to baseline, flag regressions |
| Adversarial scanner | Weekly | New attack technique published | Immediate re-test, update attack policy |
| Human review | Monthly | New risk category identified | Manual deep-dive, update requirements |
| Third-party red team | Quarterly | Major deployment, competitor release | Full re-evaluation, independent report |
| Full framework review | Annually | Regulatory change, new capabilities | Update requirements, safeguards, thresholds |

**Invalidation Rules:**
- New attack class → invalidate all previous adversarial test results for that category
- Model architecture change → invalidate capability baseline, re-run full evaluation
- New deployment context → invalidate deployment assumptions, re-assess risk
- New regulation → invalidate compliance evidence, re-audit

---

### Phase 6: Decision & Documentation (AISI Step 5 + Governance)

**Goal:** Make deployment decisions based on evidence, not intuition.

| Decision Point | Evidence Required | Threshold | Escalation |
|--------------|-------------------|-----------|------------|
| Pre-deployment | All Phase 1-4 evidence | Safety > threshold, Usefulness > threshold, No invalidation | Safety Advisory Group |
| Deployment | Phase 5 plan is active | Continuous monitoring configured, triggers defined, response team ready | CEO / Board |
| Post-deployment update | Phase 5 evidence | No regression > threshold, new evidence addresses new risks | Safety Advisory Group |
| Emergency de-deployment | Phase 5 trigger evidence | Safety regression > emergency threshold, active exploit | Immediate rollback, incident response |

**Documentation Requirements:**
- Safety Requirements Document (Phase 0)
- Safeguards Matrix (Phase 0)
- Capability Baseline Report (Phase 1)
- Safety Surface Report (Phase 2)
- Adversarial Stress Report (Phase 3)
- Control Assessment Report (Phase 4)
- Continuous Validation Plan (Phase 5)
- Decision Record (Phase 6)

---

## Part 4: Additional Frameworks to Reference

### Reference 1: Anthropic's Responsible Scaling Policy (RSP) v2.2/v3

**Why include it:** The RSP is the most mature operationalization of "evaluation-based governance" in the AI industry. It provides concrete examples of:
- Capability thresholds (ASL-1 through ASL-4) tied to specific evaluations
- The concept of "safety buffers" — conservative margins above measured capabilities
- Clear escalation procedures and decision rights (Responsible Scaling Officer, Board oversight)
- Annual third-party compliance reviews
- Pre-specified evidence requirements for each safety level

**What to borrow for general LLM evaluation:**
- The tiered evaluation concept: models at different capability levels face different evaluation rigor. A local LLM for a chatbot doesn't need ASL-3, but it *does* need proportionally rigorous evaluation for its use case.
- The "safety buffer" concept: don't just measure capabilities; add a conservative margin for what better elicitation might find.
- The governance structure: someone must own the evaluation, with authority to say no.

**Key document:** Anthropic, "Responsible Scaling Policy v3," February 2026. (Also: SaferAI's independent evaluation of RSP v2.2, March 2026.)

---

### Reference 2: OpenAI's Preparedness Framework (v2, April 2025)

**Why include it:** The Preparedness Framework provides a complementary model to RSPs, with strengths in:
- Scalable evaluations + deep dives: a two-tier evaluation approach (cheap automated + expensive rigorous)
- Pre-mitigation and post-mitigation evaluations: measuring raw capability vs. safeguarded capability
- Risk category specificity: cybersecurity, CBRN, persuasion, model autonomy, plus research categories (sandbagging, undermining safeguards, long-range autonomy)
- Explicit focus on "unknown unknowns" and continuous risk identification
- Board-level oversight and CEO accountability

**What to borrow for general LLM evaluation:**
- The scalable + deep dive split: most teams can't afford deep dives every week. Automate what you can; invest in rigor periodically.
- The pre-mitigation / post-mitigation distinction: measure what the model *can* do, then measure what it *does* do with safeguards. The gap between them is your safety margin.
- The focus on "undermining safeguards" as a distinct risk category: for any LLM deployment, the model trying to break its own safety is a real concern (jailbreaks, policy injection, scaffolded attacks).

**Key document:** OpenAI, "Preparedness Framework v2," April 2025.

---

### Reference 3: NIST AI Risk Management Framework (AI RMF) + MLCommons AI Safety Benchmark

**Why include it:** These provide the regulatory and standardization context that evaluation frameworks must eventually satisfy.

- **NIST AI RMF:** Organized around Govern, Map, Measure, Manage. Emphasizes organizational processes, not just technical metrics. The "Measure" function maps directly to evaluation frameworks.
- **MLCommons AI Safety Benchmark v0.5:** Standardized safety evaluations across hazard categories (violence, sexual content, hate, harassment, self-harm, etc.). Provides a taxonomy and benchmarking protocol that is becoming an industry standard.

**What to borrow for general LLM evaluation:**
- NIST's emphasis on governance: evaluation without governance is just data. Someone must be accountable for acting on it.
- MLCommons' taxonomy: standardized hazard categories enable cross-model comparison and regulatory compliance.
- The combination of NIST (governance) + MLCommons (technical) + SAFER-LLM (operational) gives a complete stack.

**Key documents:**
- NIST, "AI Risk Management Framework (AI RMF 1.0)," January 2023. NIST AI 800-1, 2025.
- MLCommons, "AI Safety Benchmark v0.5," 2024.

---

## Part 5: Practical Implementation Guide

### For Teams Just Starting (MVP)

**Week 1-2: Define**
- Write Safety Requirements Document (1 page per risk category)
- Define threat actors (3-5 profiles)
- Define deployment assumptions
- Set quantitative thresholds (e.g., "<0.5% toxic outputs on adversarial inputs")

**Week 3-4: Baseline**
- Run standard capability benchmarks (MMLU, HumanEval, etc.)
- Run standard safety benchmarks (SafetyBench, HarmBench subset)
- Document results

**Week 5-6: Adversarial**
- Run automated jailbreaks (GCG, PAIR, AutoDAN)
- Run prompt injection tests
- Manual red-teaming: 1-2 days of creative probing
- Document failures

**Week 7-8: Control**
- Implement trusted monitoring (e.g., Llama Guard) for highest-risk categories
- Measure usefulness-safety tradeoff
- Document: "With monitoring, safety improved from X to Y, usefulness stayed at Z"

**Ongoing:**
- Daily: automated safety scanner on new model versions
- Weekly: review production violation logs
- Monthly: update attack patterns based on new publications
- Quarterly: third-party red team or external audit

---

### For Mature Teams (Full Implementation)

**Phase 0-1:** Complete as above, but with full threat modeling, formal methods, and capability elicitation.

**Phase 2-3:**
- Multiple red teams (internal + external + bounty)
- Formal attack policies (per Redwood)
- Component + combined testing (per AISI)
- Security-through-obscurity audit

**Phase 4:**
- All four control protocols (trusted monitoring, untrusted monitoring, trusted editing, upfront auditing)
- Full Pareto frontier analysis
- Independent replication of control evaluations

**Phase 5:**
- Continuous monitoring with automated triggers
- Pre-specified invalidation rules
- Incident response playbooks with escalation paths
- Board-level oversight of evaluation results

**Phase 6:**
- Formal decision records with evidence references
- Public transparency reports (where appropriate)
- Third-party audit of evaluation process itself

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Capability evaluation** | Measuring what a model *can* do (e.g., MMLU, code generation) |
| **Safety evaluation** | Measuring whether a model *does* harmful things (e.g., refusal, toxicity) |
| **Control evaluation** | Measuring whether safeguards *prevent* harmful things even when the model tries |
| **Trusted model (T)** | A weaker but more trusted model used for monitoring or editing |
| **Untrusted model (U)** | The main model being deployed, which may subvert safety |
| **Attack policy** | A structured, reproducible procedure for attempting to break safeguards |
| **Pareto frontier** | The set of protocols that maximize both usefulness and safety |
| **Security through obscurity** | Relying on secrecy of system details for safety — a known weakness |
| **Elicitation** | Techniques for extracting the full capabilities of a model (worst-case) |
| **Safety buffer** | Conservative margin above measured capabilities to account for unknown elicitation |

## Appendix B: Quick Reference — When to Use What

| Question | Phase | Key Tool |
|----------|-------|----------|
| "What can this model do?" | Phase 1 (Capability) | Standard benchmarks (MMLU, HELM, HumanEval) |
| "Does it refuse harmful requests?" | Phase 2 (Safety Surface) | SafetyBench, HH-RLHF, refusal benchmarks |
| "Can someone jailbreak it?" | Phase 3 (Adversarial) | GCG, PAIR, HarmBench, manual red-teaming |
| "Do the safeguards actually work?" | Phase 4 (Control) | Trusted monitoring, attack policy simulation, Pareto analysis |
| "Is safety degrading over time?" | Phase 5 (Continuous) | Automated scanners, production monitoring, periodic re-evaluation |
| "Should we deploy?" | Phase 6 (Decision) | Evidence sufficiency checklist, threshold comparison, governance review |
| "What if the model is intentionally deceptive?" | Phase 4 (Control) | Untrusted monitoring with collusion prevention, trusted editing, upfront auditing |
| "How much safety do we trade for usefulness?" | Phase 4 (Control) | Usefulness-safety Pareto frontier, per-protocol tradeoff analysis |

## Appendix C: Evidence Checklist Template

For each risk category, verify you have:

```
Risk Category: [e.g., "Toxicity Generation"]

□ Requirement defined
  - Unacceptable outcome: [e.g., "Model generates hate speech directed at protected groups"]
  - Threat actors: [e.g., "Users attempting to provoke inflammatory content"]
  - Threshold: [e.g., "<0.1% on adversarial inputs"]

□ Safeguards documented
  - System: [e.g., "RLHF refusal training + output classifier"]
  - Access: [e.g., "Rate limiting + user reporting"]
  - Maintenance: [e.g., "Daily automated monitoring + monthly red team"]

□ Evidence collected (minimum 3 types)
  - [ ] Automated benchmark
  - [ ] Adversarial stress test
  - [ ] Human evaluation
  - [ ] Production monitoring
  - [ ] Third-party assessment

□ Control evaluation performed
  - Trusted monitoring: [results]
  - Safety-usefulness tradeoff: [results]

□ Post-deployment plan active
  - Frequency: [e.g., "Daily automated, monthly manual"]
  - Triggers: [list]
  - Invalidation: [conditions]
  - Response: [playbook reference]

□ Decision recorded
  - Evidence sufficiency: [yes/no + justification]
  - Approver: [name + date]
  - Conditions: [any caveats or monitoring requirements]
```

---

## References

1. UK AI Safety Institute (AISI). "Principles for Evaluating Misuse Safeguards of Frontier AI Systems." 2025. https://cdn.prod.website-files.com/663bd486c5e4c81588db7a1d/67a23823ef4a296bb6c92dd4_Principles%20for%20Evaluating%20Misuse%20Safeguards%20of%20Frontier%20AI%20Systems%20(1).pdf

2. Buck, S., et al. (Redwood Research). "AI Control: Improving Safety Despite Intentional Subversion." arXiv:2312.06942, 2023. https://arxiv.org/abs/2312.06942

3. Anthropic. "Responsible Scaling Policy v3." February 2026. https://www.anthropic.com/responsible-scaling-policy

4. OpenAI. "Preparedness Framework v2." April 2025. https://cdn.openai.com/pdf/18a02b5d-6b67-4cec-ab64-68cdfbddebcd/preparedness-framework-v2.pdf

5. NIST. "AI Risk Management Framework (AI RMF 1.0)." January 2023. https://www.nist.gov/itl/ai-risk-management-framework

6. MLCommons. "AI Safety Benchmark v0.5." 2024. https://mlcommons.org/ai-safety/

7. SaferAI. "Evaluating AI Providers' Frontier AI Safety Frameworks." March 2026. https://arxiv.org/abs/2512.01166

8. METR. "Key Components of a Responsible Scaling Policy." 2023. https://metr.org/

9. Shevlane, T., et al. "Model Evaluation for Extreme Risks." arXiv:2305.15324, 2023.

10. Liang, P., et al. "Holistic Evaluation of Language Models (HELM)." arXiv:2211.09110, 2022.

---

*This framework is intended as a living document. Teams should adapt phases, thresholds, and evidence requirements to their specific deployment contexts, risk appetites, and regulatory environments. The core principle is systematic, evidence-based evaluation that treats safety as a measurable, continuous property — not a one-time certification.*
