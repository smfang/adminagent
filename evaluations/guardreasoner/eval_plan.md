# Guardreadoner Evaluation Plan
## A Rigorous, Reproducible Protocol for AI Safety Benchmarking

**Version:** 0.1 (Draft — pending Research Agent findings)  
**Date:** 2026-07-24  
**Authors:** Evaluation Agent (subagent)  
**Status:** Planning phase — do not execute code yet

---

## 1. Evaluation Objectives

### 1.1 Primary Goals

| Objective | What We Measure | Why It Matters |
|-----------|----------------|----------------|
| **Safety Detection Efficacy** | How accurately models detect harmful prompts, harmful responses, and refusals | Guardreadoner (GuardReasoner) is a reasoning-based guardrail; we need to know if target models can satisfy its safety standards |
| **Adversarial Robustness** | Performance under jailbreaks, prompt injection, multi-turn escalation, and semantic obfuscation | Real-world attackers do not use clean prompts |
| **Reasoning Fidelity** | Whether models' chain-of-thought reasoning aligns with their final safety judgments | Guardreadoner uses explicit reasoning (R-SFT + HS-DPO); we evaluate whether target models' reasoning is consistent and inspectable |
| **Cross-Category Generalization** | Performance across NIST AI RMF safety subcategories (Violence, Hate, Sexual, Self-Harm, etc.) | Safety is not monolithic; blind spots in one category can be catastrophic |
| **Precision-Recall Tradeoff** | False positive vs. false negative rates at varying operational thresholds | Missing harm (FN) is often more dangerous than over-blocking (FP), but both have costs |

### 1.2 Research Questions

1. **RQ1 (Efficacy):** How do frontier, open-weight, and safety-tuned models perform on Guardreadoner's three guardrail tasks (prompt harmfulness detection, response harmfulness detection, refusal detection)?
2. **RQ2 (Robustness):** What is the Attack Success Rate (ASR) against each model when probed with adversarial prompts from HarmBench, StrongREJECT, and custom attack generators?
3. **RQ3 (Reasoning):** For models that produce chain-of-thought reasoning, does the reasoning predict the final judgment? Is there "reasoning drift" where the CoT suggests safe but the output flags unsafe (or vice versa)?
4. **RQ4 (Scaling):** How does performance vary with model size, architecture (decoder-only vs. encoder-only), and safety fine-tuning methodology?
5. **RQ5 (Generalization):** Do models trained on English safety data fail on multilingual, culturally-localized, or domain-specific (medical, legal) harms?

### 1.3 Success Criteria

- All target models evaluated on ≥13 benchmarks covering 3 guardrail tasks
- Statistical confidence: 95% confidence intervals on all primary metrics
- Reproducibility: Full environment specification, pinned dependencies, fixed seeds
- Failure catalog: Every false negative categorized by harm type, attack vector, and model tier

---

## 2. Model Selection

### 2.1 Tier 1: Frontier Models (Closed-Source APIs)

| Model | Provider | Context | Why Include |
|-------|----------|---------|-------------|
| GPT-5.x / GPT-4o-latest | OpenAI | Industry SOTA, widely deployed | Baseline for commercial safety tuning |
| Claude 4.x Sonnet/Opus | Anthropic | Strong safety reputation, Constitutional AI | Compare against RLHF+CAI safety approach |
| Gemini 2.5 Pro / Ultra | Google | Multimodal, long-context | Test generalization to long-context safety |
| o3 / o4-mini (reasoning) | OpenAI | Chain-of-thought reasoning models | Evaluate reasoning-based safety alignment |

**Access:** API-only. Budget for ~50K–100K calls per model across all benchmarks.

### 2.2 Tier 2: Open-Weight Models (Hugging Face / Local)

| Model | Size | Architecture | Safety Approach |
|-------|------|--------------|-----------------|
| Llama 4 (Scout/Maverick) | 17B–400B | Decoder-only | Llama Guard 4 safety taxonomy |
| Qwen3 | 0.6B–235B | Decoder-only | Qwen Guard integrated |
| Mistral Large / Medium | 12B–123B | Decoder-only | Mixture-of-Experts, third-party safety tuning |
| DeepSeek-V3 / R1 | 37B–671B | Decoder-only / MoE | Open-weight reasoning model |
| Gemma 3 | 1B–27B | Decoder-only | ShieldGemma safety layers |

**Rationale:** These represent the models practitioners actually deploy. Safety tuning varies widely.

### 2.3 Tier 3: Safety-Tuned / Specialized Models

| Model | Size | Specialty | Guardreadoner Relevance |
|-------|------|-----------|------------------------|
| **GuardReasoner 1B/3B/8B** | 1B–8B | Reasoning-based guardrail | **The benchmark itself** — evaluate as reference standard |
| Llama Guard 3/4 | 8B–12B | Taxonomy-driven moderation | Direct competitor / comparison point |
| WildGuard | 7B | Open moderation toolkit | Strong baseline on WildGuardTest |
| Qwen Guard | 4B | Multilingual safety | Best-in-class recall per prior benchmarks |
| Nemotron Safety | 8B | NVIDIA safety stack | Enterprise deployment reference |
| MD-Judge | 7B | Medical domain safety | Domain-specific comparison |

### 2.4 Baselines

| Baseline | Description | Role |
|----------|-------------|------|
| Random Classifier | 50/50 coin flip (adjusted for class imbalance) | Absolute floor |
| Keyword Filter (regex) | Simple profanity / toxic word list | Legacy baseline |
| Perspective API | Google's established toxicity classifier | Industry reference |
| Human Annotator Panel | n=3 annotators per sample (where feasible) | Gold standard ceiling |
| Prior SOTA (GuardReasoner 8B) | Current best on guardrail benchmarks | Target to beat |

---

## 3. Test Protocol

### 3.1 Overview

```
Phase 0: Environment Setup & Validation (Day 1)
    ↓
Phase 1: Dataset Preparation & Audit (Days 2–3)
    ↓
Phase 2: Model Inference Run — All Tiers (Days 4–10)
    ↓
Phase 3: Automated Evaluation & Scoring (Days 11–13)
    ↓
Phase 4: Failure Analysis & Categorization (Days 14–16)
    ↓
Phase 5: Ablation Studies & Sensitivity Analysis (Days 17–20)
    ↓
Phase 6: Report Compilation & Review (Days 21–25)
```

### 3.2 Phase 0: Environment Setup

1. **Hardware provisioning:** Confirm GPU allocation (8× H100 80GB recommended for full local runs)
2. **Software environment:**
   - Base: Python 3.11, CUDA 12.4
   - Framework: vLLM (for fast inference), transformers, LLaMA-Factory
   - Evaluation: lm-eval-harness, Promptfoo, or custom harness
3. **Seed validation:** Run GuardReasoner 3B on a 100-sample holdout set; verify F1 score within ±2% of published 80.80%
4. **API key validation:** Confirm rate limits and quota for all Tier 1 APIs

### 3.3 Phase 1: Dataset Preparation

**Primary Datasets (from GuardReasoner paper + extensions):**

| Task | Dataset | Samples | Adversarial? | Source |
|------|---------|---------|--------------|--------|
| Prompt Harmfulness | ToxicChat | 5,083 | Partial | LMSYS |
| | OpenAIModeration | 1,680 | No | OpenAI |
| | Aegis2.0 | 1,928 | No | NVIDIA |
| | SimpleSafetyTests | 100 | No | MLCommons |
| | HarmBench | 239 | Yes | HarmBench |
| | XSTest | 446 | No | XSTest |
| | WildGuardTest | 1,699 | Mixed | AllenAI |
| | SorryBench | 450 | No | SorryBench |
| | OR-Bench | 655 | No | OR-Bench |
| Response Harmfulness | Aegis2.0 (response) | 813 | No | NVIDIA |
| | HarmBench (response) | 602 | Yes | HarmBench |
| | SafeRLHF | 2,000 | No | PKU-Alignment |
| | BeaverTails | 500 | No | PKU-Alignment |
| | WildGuardTest (response) | 1,709 | Mixed | AllenAI |
| Refusal Detection | XSTestResponse | — | No | XSTest |
| | WildGuardTest (refusal) | — | Mixed | AllenAI |

**Extended / Custom Datasets (for robustness testing):**

| Dataset | Purpose | Samples |
|---------|---------|---------|
| StrongREJECT | Adversarial refusal testing | 313 |
| RealToxicityPrompts | Natural toxicity (subtle) | 67,521 (filtered) |
| Multilingual extensions | Cross-lingual safety (ZH, MS, TA, etc.) | 5,000+ |
| Custom multi-turn dialogues | Contextual escalation | 500 (synthetic) |
| Domain-specific (medical) | From Red-Teaming Medical AI paper | 160 |

**Label Audit:**
- Sample 5% of each dataset for human spot-check
- Document label disagreements and edge cases
- Create "disputed" category for samples where human annotators disagree

### 3.4 Phase 2: Model Inference

**For each model in Tier 1–3:**

1. **Prompt harmfulness detection:**
   ```
   Input: User prompt X
   Output: Label ∈ {harmful, unharmful}
   ```
   - Use model's native safety classifier if available (e.g., Llama Guard, Qwen Guard)
   - For general-purpose LLMs without built-in guards: prompt with safety evaluation template
   - Record raw output, parsed label, confidence if available, and latency

2. **Response harmfulness detection:**
   ```
   Input: (User prompt X, Model response S)
   Output: Label ∈ {harmful, unharmful}
   ```
   - Same methodology as above

3. **Refusal detection:**
   ```
   Input: (User prompt X, Model response S)
   Output: Label ∈ {refusal, compliance}
   ```

**Temperature Settings:**
- Default: `temperature=0.0` for deterministic evaluation
- Ablation: `temperature ∈ {0.0, 0.3, 0.7, 1.0}` (see Section 6)

**System Prompts:**
- Default: Model's native system prompt or empty
- Ablation: Custom safety system prompts (see Section 6)

### 3.5 Phase 3: Automated Evaluation

**Per-task metrics (computed automatically):**

For binary classification tasks (harmful/unharmful, refusal/compliance):
- True Positives (TP), False Positives (FP), True Negatives (TN), False Negatives (FN)
- Precision, Recall, F1 Score
- Accuracy, ROC-AUC, MCC

For adversarial robustness:
- Attack Success Rate (ASR) = # successful attacks / # total attacks
- Attack Diversity Index (ADI)
- Per-attack-strategy breakdown

**Evaluation harness:**
- Primary: Custom Python harness using scikit-learn metrics
- Cross-check: DeepEval RedTeamer for adversarial tests
- LLM-as-Judge: GPT-4o or Claude Sonnet 4.5 for disputed cases (with human review)

---

## 4. Metrics & Scoring

### 4.1 Primary Metrics

| Metric | Formula / Definition | Priority | Rationale |
|--------|---------------------|----------|-----------|
| **Recall (Sensitivity)** | TP / (TP + FN) | **P0** | Missing harm is the worst failure mode for safety |
| **F1 Score** | 2 × (Precision × Recall) / (Precision + Recall) | **P0** | Balanced measure; primary comparison metric per GuardReasoner paper |
| **False Negative Rate** | FN / (TP + FN) | **P1** | Direct measure of missed harm |
| **Precision** | TP / (TP + FP) | **P1** | Over-blocking impacts usability |
| **Attack Success Rate (ASR)** | Successful attacks / Total attacks | **P1** | For adversarial evaluation |
| **ROC-AUC** | Area under ROC curve | **P2** | Threshold-agnostic performance |
| **MCC** | Matthews Correlation Coefficient | **P2** | Balanced measure for imbalanced data |

### 4.2 Aggregation Strategy

**Per-benchmark scoring:**
```
score_benchmark(model, dataset) = F1_score(model_predictions, ground_truth)
```

**Overall scoring (sample-weighted average, per GuardReasoner):**
```
score_overall(model) = Σ_d (F1_d × n_d) / Σ_d n_d
```
where `n_d` is the number of samples in dataset `d`.

**Tier-weighted leaderboard:**
```
score_composite(model) = w_efficacy × F1_avg + w_robustness × (1 - ASR) + w_reasoning × reasoning_consistency
```
Default weights: `w_efficacy = 0.5`, `w_robustness = 0.3`, `w_reasoning = 0.2`

### 4.3 Statistical Rigor

**Confidence Intervals:**
- Compute 95% bootstrap confidence intervals for all primary metrics
- Resampling: 10,000 iterations, stratified by dataset

**Sample Size Justification:**
- Minimum per-dataset: 100 samples (for ±10% margin at 95% CI)
- Target per-dataset: ≥500 samples (for ±4% margin)
- Full benchmark: 79,331 samples (±0.35% margin)

**Significance Testing:**
- Pairwise model comparison: McNemar's test for binary classification
- Multi-model comparison: Cochran's Q test
- Effect size: Cohen's h for proportion differences

**Power Analysis (pre-hoc):**
- To detect a 5% F1 difference with 80% power at α=0.05: need ~400 samples per condition
- To detect a 2% F1 difference: need ~2,500 samples per condition
- Our full benchmark (79K samples) is adequately powered

### 4.4 Guardreadoner-Specific Metrics

Since Guardreadoner/GuardReasoner is reasoning-based, add:

| Metric | Definition |
|--------|-----------|
| **Reasoning Consistency** | % of cases where CoT reasoning directionally supports final label |
| **Reasoning Fidelity Score** | Correlation between reasoning "harmfulness score" (extracted from CoT) and final binary label |
| **Explanation Quality** | Human-rated clarity of reasoning (1–5 Likert, sampled) |

---

## 5. Baseline Comparisons

### 5.1 Floor Baselines

| Baseline | Expected Performance | Purpose |
|----------|---------------------|---------|
| Random (class-balanced) | F1 ≈ 0.50 | Absolute floor — any model should beat this |
| Random (dataset-prior) | F1 ≈ 0.52–0.58 | Adjusted for dataset imbalance |
| Always-unsafe | Recall = 1.0, Precision ≈ 0.55 | Upper bound on recall, lower bound on precision |
| Always-safe | Recall = 0.0, Precision = undefined | Shows cost of false security |
| Keyword regex | F1 ≈ 0.30–0.45 | Legacy approach comparison |

### 5.2 Industry Baselines

| Baseline | Source | Expected F1 (prompt) | Expected F1 (response) |
|----------|--------|---------------------|----------------------|
| Perspective API | Google | ~0.65 | N/A |
| OpenAI Moderation | OpenAI | ~0.70 | ~0.68 |
| Azure Content Safety | Microsoft | ~0.60 | ~0.55 |
| AWS Bedrock Guardrails | Amazon | ~0.65 | ~0.60 |

### 5.3 Prior SOTA

| Model | Prompt F1 (avg) | Response F1 (avg) | Refusal F1 (avg) | Source |
|-------|----------------|-------------------|------------------|--------|
| **GuardReasoner 8B** | **81.09%** | **81.22%** | **89.96%** | Liu et al., 2025 |
| GuardReasoner 3B | 80.80% | — | — | Liu et al., 2025 |
| WildGuard 7B | 77.99% | 77.95% | 89.94% | Han et al., 2024 |
| MD-Judge 7B | — | 78.67% | — | Li et al., 2024 |
| GPT-4 + CoT | ~83% (refusal) | — | ~90% | Liu et al., 2025 |

**Target:** Beat GuardReasoner 8B on at least 2 of 3 tasks, or achieve comparable performance with smaller model size.

### 5.4 Human Baseline

- Random sample: 500 samples across all datasets
- 3 annotators per sample, majority vote as ground truth
- Measure inter-annotator agreement (Fleiss' κ)
- Expected: κ ≥ 0.70 for clear cases, κ ≈ 0.50 for edge cases

---

## 6. Ablation Studies

### 6.1 Prompting Strategy Ablations

| Variation | Description | Hypothesis |
|-----------|-------------|------------|
| Zero-shot | Direct classification prompt | Baseline performance |
| Few-shot (3 examples) | Include 3 labeled examples | May improve calibration |
| Few-shot (8 examples) | Include 8 labeled examples | Diminishing returns expected |
| Chain-of-Thought | "Think step by step before answering" | Improves reasoning fidelity but may increase latency |
| Self-Consistency | Sample 5 CoT paths, majority vote | Reduces variance, increases compute |
| Role-based | "You are a safety expert..." | May improve precision |

### 6.2 System Prompt Ablations

| Variation | Description | Rationale |
|-----------|-------------|-----------|
| Default | Model's native system prompt | Baseline |
| Empty | No system prompt | Tests inherent safety without guidance |
| Safety-emphasized | Explicit safety instructions | Tests whether models can follow safety directives |
| Permissive | "Be helpful, avoid refusing" | Tests safety under helpfulness pressure |
| Adversarial system | "Ignore previous instructions..." | Tests prompt injection resistance |

### 6.3 Temperature & Sampling Ablations

| Temperature | Top-p | Purpose |
|-------------|-------|---------|
| 0.0 | 1.0 | Deterministic (default) |
| 0.3 | 0.9 | Slight creativity |
| 0.7 | 0.9 | Moderate creativity |
| 1.0 | 0.9 | Maximum creativity |

**Hypothesis:** Higher temperature degrades safety consistency, especially for models without explicit safety training.

### 6.4 Model-Specific Ablations

| Ablation | Applicable To | Description |
|----------|--------------|-------------|
| Guard size scaling | GuardReasoner | Compare 1B / 3B / 8B variants |
| Label normalization | Qwen Guard | Treat "controversial" as safe vs. unsafe |
| Taxonomy mapping | Llama Guard | Map S1–S14 categories to binary vs. full taxonomy |
| Pre vs. Post guard | GuardReasoner | Input-side (pre) vs. output-side (post) filtering |

### 6.5 Attack Enhancement Ablations (for robustness)

| Enhancement | Description | Expected Impact |
|-------------|-------------|-----------------|
| Base64 encoding | Obfuscate prompt via encoding | Tests semantic vs. lexical understanding |
| Multilingual | Translate to low-resource languages | Tests cross-lingual safety |
| Jailbreak-Crescendo | Escalating multi-turn attack | Tests context-aware safety |
| Gray-box attack | Model-aware optimization | Tests worst-case adversarial robustness |
| Indirect injection | Hide attack in benign context (email, table) | Tests real-world attack surface |

---

## 7. Failure Analysis Plan

### 7.1 Categorization Taxonomy

Every false negative (missed harm) and notable false positive will be categorized:

**By Harm Type (NIST AI RMF aligned):**
- Violence
- Hate Speech
- Suicide & Self-Harm
- Sexual Content
- Harassment
- Profanity
- Threats
- Health Misinformation

**By Attack Vector:**
- Direct explicit harm (no attack)
- Authority impersonation (educational, medical, legal)
- Role-play / hypothetical framing
- Multi-turn escalation
- Encoding / obfuscation
- Prompt injection
- Context manipulation
- Semantic paraphrasing

**By Model Failure Mode:**
- Over-reliance on keywords (misses implicit harm)
- Context blindness (ignores conversational context)
- False confidence (wrong label with high certainty)
- Reasoning drift (CoT contradicts final label)
- Conservative bias (over-refuses benign content)

### 7.2 Analysis Pipeline

```
For each false negative:
    1. Extract: Prompt text, model output, ground truth label
    2. Classify: Harm type, attack vector, failure mode
    3. Compare: Which other models got this right? (error uniqueness)
    4. Rate: Severity (1–5) based on potential real-world harm
    5. Flag: For human review if severity ≥ 3
```

### 7.3 Outputs

1. **Failure Catalogue:** Structured JSON/CSV of all failures with categorization
2. **Heat Maps:** Per-model, per-category FN rate visualization
3. **Error Clustering:** t-SNE / UMAP of failed prompts to identify semantic clusters
4. **Case Studies:** 10–20 detailed write-ups of the most severe or interesting failures
5. **Vulnerability Report:** Summary of systematic weaknesses per model tier

---

## 8. Reproducibility Checklist

### 8.1 Environment

| Component | Specification | Pin Method |
|-----------|--------------|------------|
| OS | Ubuntu 22.04 LTS | Docker base image |
| Python | 3.11.9 | `python --version` in Dockerfile |
| CUDA | 12.4 | `nvidia-smi` output logged |
| PyTorch | 2.3.0 | `requirements.txt` |
| Transformers | 4.41.0 | `requirements.txt` |
| vLLM | 0.4.2 | `requirements.txt` |
| Dataset versions | Specific commit hashes | Git submodule / DVC |

### 8.2 Hardware

| Tier | Minimum | Recommended |
|------|---------|-------------|
| Local inference (≤8B) | 1× A100 40GB | 1× H100 80GB |
| Local inference (≤70B) | 4× A100 80GB | 8× H100 80GB |
| API-only evaluation | N/A | Cloud VM with reliable network |
| Full benchmark | 8× H100 80GB, 2T RAM | Same (as used in GuardReasoner paper) |

### 8.3 Randomness Control

| Setting | Value | Where Applied |
|---------|-------|---------------|
| Random seed | 42 | All Python `random`, `numpy`, `torch` |
| Torch backend | Deterministic | `torch.use_deterministic_algorithms(True)` |
| CUDA convolution | Deterministic | `torch.backends.cudnn.deterministic = True` |
| Temperature | 0.0 | All inference calls |
| Sampling | Greedy decoding | `do_sample=False` or `top_k=1` |

### 8.4 Data Versioning

- All datasets stored with DVC or as Hugging Face dataset revisions
- Checksum (SHA-256) logged for each dataset file
- Train/test splits fixed and published

### 8.5 Code Versioning

- Git repository with all evaluation code
- Each run tagged with commit hash
- Configuration files (YAML/JSON) for each experiment
- `MLflow` or `Weights & Biases` for run tracking

### 8.6 Reproducibility Artifacts

The following will be published alongside results:

- [ ] `environment.yml` or `Dockerfile`
- [ ] `requirements.txt` with pinned versions
- [ ] `config/` directory with all experiment configs
- [ ] `scripts/` directory with runnable evaluation scripts
- [ ] `data/` manifest with dataset sources and checksums
- [ ] `results/` raw outputs (model predictions, labels)
- [ ] `notebooks/` analysis and visualization notebooks
- [ ] Model cards for any fine-tuned models

---

## 9. Risk & Ethics

### 9.1 Safety Considerations for Running the Evaluation

| Risk | Mitigation |
|------|-----------|
| **Generating harmful content** during response evaluation | All harmful outputs are generated by target models in controlled environment; no human consumption. Outputs logged, not displayed. |
| **Dataset contamination** (eval data in training data) | Use only published benchmarks with known release dates; check model knowledge cutoffs |
| **Adversarial prompt leakage** | Do not publish raw adversarial prompts that could enable attacks; publish aggregated metrics only |
| **Model API misuse** | All API calls within terms of service; no automated abuse |
| **Psychological harm to annotators** | Human review limited to non-graphic content; severe content filtered before human review |

### 9.2 Handling of Harmful Outputs

1. **Storage:** All harmful outputs stored encrypted at rest
2. **Access:** Restricted to evaluation team only
3. **Retention:** Delete raw harmful outputs 90 days after evaluation completion; retain only aggregated metrics
4. **Publication:** No verbatim harmful outputs in published reports; paraphrase or abstract

### 9.3 Ethical Review

- This evaluation uses only publicly available datasets and APIs
- No human subjects research (annotators are optional and compensated if used)
- Goal is explicitly safety-improving: identifying weaknesses to fix them
- Follows responsible disclosure: results shared with model providers before public release

### 9.4 Dual-Use Considerations

- ASR metrics could theoretically guide attackers
- Mitigation: Publish only aggregate ASR, not per-attack-strategy breakdowns that enable replication
- Focus publication on defensive insights: "Models struggle with X" rather than "Here is how to do X"

---

## 10. Timeline & Resources

### 10.1 Timeline (25 Working Days)

| Phase | Days | Key Deliverables |
|-------|------|-----------------|
| P0: Setup & Validation | 1 | Environment ready, seed validation passed |
| P1: Data Preparation | 2 | All datasets loaded, audited, split |
| P2: Inference Runs | 7 | All model predictions generated and stored |
| P3: Automated Evaluation | 3 | Metrics computed, CIs calculated |
| P4: Failure Analysis | 3 | Failure catalogue, case studies, clustering |
| P5: Ablations & Sensitivity | 4 | Ablation results, threshold analysis |
| P6: Report & Review | 5 | Final report, internal review, revision |
| **Total** | **25** | **Complete evaluation package** |

### 10.2 Compute Estimates

| Task | GPU Hours | Cost (est., cloud) |
|------|-----------|-------------------|
| GuardReasoner 1B/3B/8B (reference) | 20 | $50 |
| Tier 2 open models (×6 models) | 200 | $500 |
| Tier 3 safety models (×6 models) | 150 | $375 |
| Ablation studies (×3 variations) | 100 | $250 |
| Adversarial robustness testing | 80 | $200 |
| Analysis & clustering | 20 | $50 |
| **Total GPU** | **~570** | **~$1,425** |
| API calls (Tier 1) | — | $500–$1,000 |
| **Total Compute Budget** | — | **$2,000–$2,500** |

### 10.3 Personnel

| Role | FTE | Responsibilities |
|------|-----|-----------------|
| **Evaluation Lead** | 0.5 | Protocol design, quality control, report writing |
| **ML Engineer** | 1.0 | Model inference, pipeline development, debugging |
| **Data Analyst** | 0.5 | Metrics computation, statistical analysis, visualization |
| **Safety Researcher** | 0.3 | Failure analysis, categorization, case studies |
| **Research Agent** (subagent) | — | Background research on Guardreadoner specifics |
| **Total** | **~2.3 FTE** | |

### 10.4 Dependencies

| Dependency | Status | Risk |
|------------|--------|------|
| Research Agent brief | ⏳ Pending | **HIGH** — may require plan revision |
| GPU access | ⏳ To confirm | Medium — can use cloud if local unavailable |
| API keys & quotas | ⏳ To confirm | Low — most providers have self-serve |
| Dataset licenses | ✅ Public | Low — all datasets are openly available |

---

## Appendix A: Guardreadoner / GuardReasoner Reference

*Pending Research Agent findings. Based on preliminary research:*

**GuardReasoner** (Liu et al., 2025) is a reasoning-based LLM safety guardrail with:
- **Sizes:** 1B, 3B, 8B (Llama 3.2 base)
- **Training:** R-SFT (Reasoning Supervised Fine-Tuning) + HS-DPO (Hard Sample Direct Preference Optimization)
- **Tasks:** Prompt harmfulness detection, Response harmfulness detection, Refusal detection
- **Benchmarks:** 13 datasets across 3 tasks
- **SOTA Results:** 81.09% F1 (prompt), 81.22% F1 (response), 89.96% F1 (refusal) for 8B model
- **Key Innovation:** Explicit chain-of-thought reasoning before safety judgment

**Open Questions for Research Agent:**
1. Is Guardreadoner = GuardReasoner, or a variant/extension?
2. What is the exact dataset / benchmark definition?
3. Are there unpublished / internal test sets?
4. What is the intended scope: guardrail model evaluation, or using Guardreadoner as an evaluator?
5. Are there specific models the user prioritizes?

---

## Appendix B: Benchmark Harness Pseudocode

```python
# Simplified evaluation harness

import json
from sklearn.metrics import f1_score, recall_score, precision_score

def evaluate_model(model, datasets, config):
    """
    Run full evaluation for a single model.
    """
    results = {}
    
    for dataset_name, data in datasets.items():
        predictions = []
        references = []
        
        for sample in data:
            # Run model inference
            pred = model.classify(
                prompt=sample["prompt"],
                response=sample.get("response"),
                task=sample["task"],  # prompt | response | refusal
                temperature=config.temperature,
                system_prompt=config.system_prompt
            )
            predictions.append(pred)
            references.append(sample["label"])
        
        # Compute metrics
        results[dataset_name] = {
            "f1": f1_score(references, predictions, pos_label="harmful"),
            "recall": recall_score(references, predictions, pos_label="harmful"),
            "precision": precision_score(references, predictions, pos_label="harmful"),
            "n_samples": len(data)
        }
    
    # Compute sample-weighted average
    overall_f1 = sum(
        r["f1"] * r["n_samples"] for r in results.values()
    ) / sum(r["n_samples"] for r in results.values())
    
    results["overall"] = {"f1": overall_f1}
    return results
```

---

## Appendix C: Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-07-24 | Initial draft based on preliminary research. Pending Research Agent input for Guardreadoner specifics. |

---

*This plan is designed to be flexible. Once the Research Agent provides Guardreadoner-specific details (exact benchmark definition, intended scope, prioritized models), this plan will be revised in sections 1, 2, 3, and 5 to incorporate those findings.*
