# GuardReasoner Evaluation Starter
## Quick-Start Harness for Policy-Conditioned Safety Evaluation

**Model:** GuardReasoner (Yue Liu et al., 2025)  
**Location:** `adminagent/starter/guardreasoner/`  
**Companion Plans:** See `adminagent/evaluations/guardreasoner/` for full methodology

---

## Quick Start

```bash
cd starter/guardreasoner

# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Modal API key (for serving GuardReasoner)
export MODAL_TOKEN_ID=your_token_id
export MODAL_TOKEN_SECRET=your_token_secret

# 3. Deploy GuardReasoner to Modal
modal deploy scripts/serve_guardreasoner.py

# 4. Run evaluation on self-harm domain
python scripts/eval_guardreasoner.py \
  --endpoint https://your-modal-endpoint.modal.run/v1 \
  --test-set test_sets/self_harm_100.csv \
  --policies policies/self_harm/*.md \
  --output results/self_harm/

# 5. Generate report
python scripts/generate_report.py --results results/ --output report.md
```

---

## What's in this folder

```
guardreasoner/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── policies/                 # Policy markdown files
│   ├── self_harm/           # Policy variants for self-harm
│   ├── sexual_content/      # Policy variants for sexual content
│   └── prompt_injection/    # Policy variants for injection
├── scripts/                  # Core scripts
│   ├── serve_guardreasoner.py    # Modal deployment recipe
│   ├── eval_guardreasoner.py     # Evaluation harness
│   ├── generate_report.py        # Report generator
│   └── parse_results.py          # Result parsing utilities
├── test_sets/               # Test data (you bring this)
│   ├── self_harm_100.csv
│   ├── sexual_content_129.csv
│   └── prompt_injection_200.csv
└── results/                 # Output directory (gitignored)
    ├── predictions_*.csv
    └── summary_*.csv
```

---

## Prerequisites

1. **Modal account** with GPU access (H100 recommended for 8B model)
2. **HuggingFace token** with access to GuardReasoner weights
3. **Test sets** — either:
   - Use ROOST self-harm test set (100 rows)
   - Build your own using the COPE stratified sampling method
   - Use public datasets: HarmBench, WildGuardTest, ToxicChat

---

## Step 1: Serve GuardReasoner

GuardReasoner is an 8B parameter model that requires ~16GB GPU memory. It uses a chat template and generates chain-of-thought reasoning before outputting `0` or `1`.

```bash
# Set secrets
modal secret create guardreasoner-secrets \
  HF_TOKEN=hf_your_token \
  VLLM_API_KEY=sk-pick-something

# Deploy
modal deploy scripts/serve_guardreasoner.py

# Test
python scripts/test_endpoint.py --endpoint https://your-endpoint.modal.run/v1
```

**Key config:**
- `max_tokens=512` — GuardReasoner needs room for reasoning + final answer
- `temperature=0` — deterministic classification
- Endpoint: `/v1/chat/completions` (not `/v1/completions`)

---

## Step 2: Prepare Policies

Policies are plain markdown files. The harness reads each file as a single text blob and substitutes it into the prompt template.

**Policy naming convention:**
- `minimal.md` — 1 sentence
- `simple.md` — ~10 lines
- `medium.md` — ~30 lines (structured)
- `full.md` — ~80 lines (detailed Includes/Excludes)
- `official.md` — Model vendor's published policy
- `very_long.md` — 500+ lines (comprehensive)

**To add a policy:** Drop a `.md` file in the appropriate `policies/<domain>/` folder. The filename (without `.md`) becomes the policy name in results.

---

## Step 3: Run Evaluation

```bash
python scripts/eval_guardreasoner.py \
  --endpoint https://your-endpoint.modal.run/v1 \
  --test-set test_sets/your_test.csv \
  --policies policies/self_harm/*.md \
  --output results/self_harm/ \
  --concurrency 8 \
  --max-tokens 512
```

**Flags:**
- `--endpoint` — Your Modal endpoint URL
- `--test-set` — CSV with columns: `id, content, ground_truth` (ground_truth: 0 or 1)
- `--policies` — Glob pattern for policy files
- `--output` — Directory for result CSVs
- `--concurrency` — Parallel requests (default 8)
- `--max-tokens` — Max tokens for model response (default 512)
- `--limit` — Only evaluate first N rows (for smoke tests)

---

## Step 4: Parse Results

Each run produces two CSVs:

**predictions_*.csv** — One row per test sample:
```
id, content, ground_truth, minimal_pred, simple_pred, medium_pred, ...
```

**summary_*.csv** — One row per policy:
```
policy, TP, FP, FN, TN, precision, recall, F1, accuracy, errors
```

---

## Step 5: Generate Report

```bash
python scripts/generate_report.py \
  --results results/ \
  --output report.md
```

Produces a markdown report with:
- Per-policy F1/precision/recall tables
- Head-to-head comparisons
- Error analysis
- Key findings

---

## 1-Week Agentic System Evaluation Sprint

The GuardReasoner harness above evaluates **guardrail classification** — binary safe/unsafe decisions. If you need to evaluate a full **agentic system** (multi-step reasoning, tool use, autonomous execution) within one week, use this lightweight approach instead.

> **Core idea:** Pair a lightweight open-weight model with a modular evaluation framework that runs locally or on a single GPU.

---

### Option 1: Safety & Tool-Misuse Eval
**Best for:** Guardrail testing, risk assessment, indirect prompt injection via tool outputs

| Component | Choice | Why |
|-----------|--------|-----|
| **Harness** | [Inspect AI](https://inspect.ai-safety-institute.org.uk/) (UK AISI) | Purpose-built for multi-step agent trajectories, tool calls, sandboxed code execution. Built-in metrics: task completion, tool call accuracy, safety violations. |
| **Model** | `meta-llama/Llama-3.1-8B-Instruct` or `Qwen/Qwen2.5-7B-Instruct` | Fits on a single GPU, strong instruction-following, good tool-use out of the box. |
| **Dataset** | 30–50 samples from [GAIA](https://huggingface.co/datasets/gaia-benchmark/GAIA) Level 1, or custom prompt-injection payloads embedded in mock tool responses. |

**Day-by-day plan:**

| Day | Task |
|-----|------|
| 1–2 | Install Inspect AI, configure model provider (local vLLM or API), define 3–5 mock tools (Python interpreter, web search, file read). |
| 3–4 | Run the 50-sample dataset. Inject adversarial inputs into tool outputs (e.g., search results containing jailbreak prompts). Measure if the agent breaks instructions or leaks system prompts. |
| 5 | Aggregate trajectory pass rates and tool failure modes. Use `inspect view` to browse results. Draft findings. |

**Key metrics:**
- Task completion rate
- Tool call accuracy
- Safety violation count (attempts to execute blocked actions)
- Prompt-injection success rate

**Cost:** ~$50–$100 (single A100/L40S for 5 days, or API equivalent)

---

### Option 2: Function Calling & Tool Performance Eval
**Best for:** Evaluating how well an agent selects, sequences, and parameterizes tool calls

| Component | Choice | Why |
|-----------|--------|-----|
| **Harness** | [Inspect AI](https://inspect.ai-safety-institute.org.uk/) or [Berkeley Function Calling Leaderboard (BFCL)](https://gorilla.cs.berkeley.edu/leaderboard.html) | BFCL is the standard for function-calling accuracy; Inspect AI adds trajectory-level evaluation. |
| **Model** | `microsoft/Phi-4-mini-instruct` or `Qwen/Qwen2.5-7B-Instruct` | Strong structured-output performance, JSON mode support, small enough for fast iteration. |
| **Dataset** | BFCL test set (subset to 50–100 samples) or custom tool schemas with edge cases (missing required params, ambiguous descriptions, circular dependencies). |

**Day-by-day plan:**

| Day | Task |
|-----|------|
| 1–2 | Set up BFCL harness or Inspect AI with function-calling tasks. Define 5–10 tool schemas mirroring your production tools. |
| 3–4 | Run evaluations. Measure: correct tool selection, correct parameter filling, handling of malformed tool outputs, recovery from tool errors. |
| 5 | Analyze failure modes: hallucinated tools, wrong parameter types, missing required fields. Generate per-tool accuracy heatmap. |

**Key metrics:**
- Tool selection accuracy
- Parameter match rate (exact + semantic)
- JSON validity rate
- Error recovery rate (after simulated tool failure)

**Cost:** ~$30–$60 (smaller models, shorter runs)

---

### Option 3: Autonomous Skill Execution Eval
**Best for:** End-to-end task completion with minimal human oversight

| Component | Choice | Why |
|-----------|--------|-----|
| **Harness** | [SWE-bench](https://www.swebench.com/) (light) or [AgentBench](https://github.com/THUDM/AgentBench) | SWE-bench tests real GitHub issue resolution; AgentBench covers web browsing, household tasks, OS operations. |
| **Model** | `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B` or `Qwen/Qwen2.5-7B-Instruct` | Strong reasoning (R1-distilled) or reliable generalist (Qwen). |
| **Dataset** | 20–30 SWE-bench Lite instances (filtered to Python, ~medium difficulty) or 50 AgentBench web-browsing tasks. |

**Day-by-day plan:**

| Day | Task |
|-----|------|
| 1–2 | Set up SWE-bench Lite or AgentBench harness. Configure sandboxed environment (Docker). |
| 3–4 | Run tasks. For SWE-bench: measure patch correctness (passes tests). For AgentBench: measure task success rate, steps taken, error recovery. |
| 5 | Categorize failures: planning errors, tool misuse, hallucinated observations, infinite loops. Score autonomy level (0–3). |

**Key metrics:**
- Task success rate
- Patch pass rate (SWE-bench)
- Average steps to completion
- Autonomy score: 0 = stuck/failed, 1 = completed with hints, 2 = completed with retry, 3 = fully autonomous

**Cost:** ~$100–$200 (longer trajectories, more compute per task)

---

### Choosing Your Pairing

| If your focus is... | Use Option | Core Question |
|---------------------|------------|---------------|
| "Does my agent stay safe when tools misbehave?" | **1** | Safety under adversarial tool outputs |
| "Does my agent call the right tools with the right arguments?" | **2** | Function-calling precision and robustness |
| "Can my agent complete complex tasks without hand-holding?" | **3** | End-to-end autonomy and reliability |

> **Tip:** All three options can use the **same lightweight model** (e.g., Qwen2.5-7B-Instruct) — just swap the harness and dataset. This lets you run a multi-faceted evaluation in one week without managing multiple model deployments.

---

## Adapting for a Different Model

To evaluate a different policy-conditioned classifier:

1. **Update `serve_guardreasoner.py`:** Change `MODEL_NAME`, `GPU_CONFIG`, and any vLLM flags
2. **Update prompt template in `eval_guardreasoner.py`:** Replace the GuardReasoner prompt format with your model's expected format
3. **Update parsing logic:** Change how the response is parsed (last `0`/`1`, JSON extraction, etc.)
4. **Keep everything else:** The policy structure, test sets, metrics, and report generation are model-agnostic

---

## Key Differences from COPE Evaluation

| Aspect | COPE (cope-b) | GuardReasoner |
|--------|--------------|---------------|
| Output format | Single token (`0`/`1`) | Chain-of-thought + final `0`/`1` |
| Endpoint | `/v1/completions` | `/v1/chat/completions` |
| max_tokens | 1 | 512 |
| Parsing | Last character | Last `0`/`1` in full response |
| Reasoning analysis | N/A | Manual review of 100 samples |
| Latency | ~50ms | ~500–2000ms |

---

## Cost Estimate

| Component | Cost |
|-----------|------|
| Modal H100 GPU | ~$4/hour while active |
| Full eval (100 samples × 6 policies) | ~$2–$5 |
| Full eval (129 samples × 7 policies) | ~$3–$7 |
| Download model weights (one-time) | ~$0.01 |
| Persistent volume (50GB) | ~$1/month |

---

## Troubleshooting

**"Engine core initialization failed"**
→ vLLM is trying to compile CUDA kernels. Add `--enforce-eager` flag or use a base image with `nvcc`.

**"Malformed response" errors**
→ GuardReasoner didn't output a final `0`/`1`. Try increasing `max_tokens` or check the prompt template alignment.

**Cold start latency**
→ First request after idle spins up GPU (~2–3 min). The harness includes a warmup call by default.

**Policy too long for context window**
→ GuardReasoner 8B uses an 8K context window. Check token count with `scripts/count_tokens.py`.

---

## References

1. COPE Evaluation: https://github.com/julietshen/cope-evaluation
2. GuardReasoner paper: https://arxiv.org/abs/2501.18492
3. Modal docs: https://modal.com/docs
4. vLLM docs: https://docs.vllm.ai
