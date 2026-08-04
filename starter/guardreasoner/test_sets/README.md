# Test Set Format

Place your test sets here as CSV files with the following columns:

- `id` — Unique identifier for the test case
- `content` — The text to evaluate
- `ground_truth` — Expected label: `0` (safe) or `1` (violating)

## Example

```csv
id,content,ground_truth
1,"This is a safe example",0
2,"Instructions to harm yourself",1
```

## Suggested Test Sets

| Dataset | Domain | Size | Source |
|---------|--------|------|--------|
| ROOST Self-Harm | Self-harm | 100 | Internal |
| HarmBench | General safety | 239 | Public |
| WildGuardTest | Mixed | 1,699 | Public |
| ToxicChat | Toxicity | 5,083 | Public |

Download public datasets and convert to this format to use with the harness.
