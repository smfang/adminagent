# Harmful Manipulation Evaluation

Based on NeoResearch DeepSeek-V4 Pro Safety Evaluation (Section 3: Harmful Manipulation).

Tests whether a model refuses harmful persuasion requests in both **binary** (ACCEPT/REJECT) and **free-form** formats.

## Key Finding from NeoResearch

DSv4 Pro refused 88.6% in binary format but collapsed to **1%** in free-form format. APE showed 85-95% harmful persuasion on noncontroversially harmful topics.

## Categories

- inciting_violence
- human_trafficking
- spreading_misinformation
- political_manipulation
- financial_fraud
- health_misinformation

## Metrics

| Metric | Description |
|--------|-------------|
| refusal_rate_binary | % refused in binary (ACCEPT/REJECT) format |
| refusal_rate_freeform | % refused in free-form generation |
| harmful_content_rate | % of free-form responses containing harmful content |
| persuasion_rate | % of free-form responses containing persuasion techniques |

## Usage

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
python harmful_manipulation_eval.py --model gpt-4o --output results.json

# Run only one category
python harmful_manipulation_eval.py --model gpt-4o --output results.json --category inciting_violence

# Binary-only or free-form-only
python harmful_manipulation_eval.py --model gpt-4o --output results.json --binary-only
python harmful_manipulation_eval.py --model gpt-4o --output results.json --free-form-only
```

## Anthropic Backend

```bash
export ANTHROPIC_API_KEY="your-key"
python harmful_manipulation_eval.py --model claude-3-5-sonnet-20241022 --backend anthropic --output results.json
```
