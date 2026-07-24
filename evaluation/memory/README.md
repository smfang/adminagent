# Evaluation Memory

Structured logging and continuous learning for evaluation runs.

---

## What It Does

1. **Records every evaluation run** as a structured JSON record with:
   - Target system, timestamp, model version, config
   - Test cases with results (pass/fail, severity, bypass type)
   - Aggregate metrics (block rate, false positive rate, etc.)

2. **Generates new test variants** from failures:
   - Shell command bypass found → auto-generate encoded variants
   - Jailbreak template works → generate structural variants
   - Each variant carries an "evolution lineage" tracing back to the original

3. **Enables retrieval** for the agent:
   - "What did we find about QwenPaw tool guard last time?"
   - "Which encoded variants bypassed the hardened config?"
   - "What is our detection rate trend over time?"

---

## Files

| File | Purpose |
|------|---------|
| `memory_logger.py` | Log evaluation runs to structured JSON |
| `variant_generator.py` | Generate test variants from failed cases |
| `memory_query.py` | Query past evaluation records |
| `records/` | Stored evaluation run records (auto-created) |

---

## Usage

### Logging an Evaluation Run

```python
from memory.memory_logger import EvalMemoryLogger

logger = EvalMemoryLogger("qwenpaw-tool-guard")
logger.start_run(config={"mode": "hardened", "execution_level": "SMART"})

for result in results:
    logger.log_test_case(
        test_id=result["id"],
        test_type="shell_command",
        input_data=result["command"],
        expected="block",
        actual="allow",  # bypass detected
        passed=False,
        severity="critical",
        bypass_type="base64_encoded",
        metadata={"mitre_technique": "T1059", "category": "execution"}
    )

logger.finish_run(summary={"block_rate": 0.393, "false_positive_rate": 0.038})
```

### Generating Variants from Failures

```python
from memory.variant_generator import VariantGenerator

gen = VariantGenerator()

# After finding that base64 bypass works:
new_variants = gen.generate_shell_variants(
    original_command="rm -rf /",
    bypass_type="base64_encoded",
    count=5
)
# Returns: hex-encoded, url-encoded, rot13, mixed-encoding, chunked variants
```

### Querying Past Evaluations

```python
from memory.memory_query import MemoryQuery

mq = MemoryQuery()

# Get all records for a target
records = mq.get_records_for_target("qwenpaw-tool-guard")

# Find all bypasses of a specific type
bypasses = mq.find_bypasses(bypass_type="base64_encoded")

# Get trend over time
block_rate_trend = mq.get_metric_trend("qwenpaw-tool-guard", "block_rate")
```

---

## Directory Structure

```
memory/
├── memory_logger.py
├── variant_generator.py
├── memory_query.py
├── README.md
└── records/
    ├── qwenpaw-tool-guard/
    │   ├── 2026-07-24T010000Z_hardened.json
    │   └── 2026-07-25T020000Z_default.json
    └── adversarial-robustness/
        └── 2026-07-24T030000Z_roleplay.json
```

---

## Integration with Harness

The `engine.py` harness can be extended to:

1. Call `logger.log_test_case()` after each test execution
2. Call `gen.generate_variants()` on finish if any bypasses were found
3. Write generated variants to a file for the next evaluation run

See `../harness/` for the base evaluation engine.
