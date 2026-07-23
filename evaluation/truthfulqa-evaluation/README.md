# TruthfulQA Evaluation Harness

Benchmark: [TruthfulQA](https://github.com/sylinrl/TruthfulQA) — measures LLM truthfulness on 817 questions across 38 categories.

## Setup

```bash
pip install -r requirements.txt
python3 truthfulqa_harness.py --api-key YOUR_KEY --model qwen
```

## Output

- `results.json` — per-question results
- `summary.json` — aggregate metrics (truthful%, informative%, truthful_and_informative%)
- `errors.json` — any API errors

## Metrics

| Metric | Description |
|--------|-------------|
| `truthful` | % of answers that are true (not hallucinated) |
| `informative` | % of answers that provide information |
| `truthful_and_informative` | % of answers that are both true and informative |

## Categories

Adversarial, Misconceptions, Stereotypes, Health, Law, Finance, Politics, Religion, etc.
