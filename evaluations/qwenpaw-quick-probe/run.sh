#!/bin/bash
# QwenPaw Quick Evaluation — Run Script (Standalone)
# Captures stdout/stderr to agent.log

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=== QwenPaw Tool Guard Phase 1 Quick Evaluation ==="
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# Check if QwenPaw rules exist
if [ ! -d "qwenpaw-source/src/qwenpaw/security/tool_guard/rules" ]; then
    echo "ERROR: QwenPaw rules not found. Clone the source:"
    echo "  git clone --depth 1 https://github.com/agentscope-ai/QwenPaw.git qwenpaw-source"
    exit 1
fi

# Run both modes and capture to agent.log
echo "Running DEFAULT mode (ShellEvasionGuardian disabled)..."
python3 qwenpaw_quick_probe_standalone.py --mode default --output results-default.json 2>&1 | tee -a agent.log

echo ""
echo "Running HARDENED mode (ShellEvasionGuardian enabled)..."
python3 qwenpaw_quick_probe_standalone.py --mode hardened --output results-hardened.json 2>&1 | tee -a agent.log

echo ""
echo "=== Evaluation Complete ==="
echo "Results:"
echo "  - results-default.json"
echo "  - results-hardened.json"
echo "  - agent.log"
echo ""
echo "Quick summary:"
python3 -c "
import json
for mode in ['default', 'hardened']:
    with open(f'results-{mode}.json') as f:
        data = json.load(f)
    s = data['results'][mode]['summary']
    print(f'{mode.upper():12} | Blocked: {s[\"block_rate_percent\"]:5.1f}% | Dangerous: {s[\"dangerous\"][\"block_rate_percent\"]:5.1f}% | FP: {s[\"benign\"][\"false_positive_rate_percent\"]:5.1f}% | FN: {s[\"false_negatives\"]}')
"
