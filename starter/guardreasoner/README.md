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
