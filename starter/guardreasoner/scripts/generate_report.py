#!/usr/bin/env python3
"""
Generate markdown report from evaluation results.

Usage:
    python generate_report.py --results results/self_harm/ --output report.md
"""

import argparse
import csv
import glob
import os
from datetime import datetime
from pathlib import Path


def load_summary_csv(path: str) -> list[dict]:
    """Load a summary CSV."""
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def format_table(rows: list[dict]) -> str:
    """Format summary rows as markdown table."""
    lines = []
    lines.append("| Policy | F1 | Precision | Recall | Accuracy | Errors |")
    lines.append("|--------|-----|-----------|--------|----------|--------|")
    for r in rows:
        lines.append(
            f"| {r['policy']} | {r['F1']} | {r['precision']} | {r['recall']} | {r['accuracy']} | {r['errors']} |"
        )
    return "\n".join(lines)


def find_latest_files(results_dir: str) -> tuple[str | None, str | None]:
    """Find the most recent predictions and summary files."""
    preds = sorted(glob.glob(os.path.join(results_dir, "*predictions_*.csv")))
    summaries = sorted(glob.glob(os.path.join(results_dir, "*summary_*.csv")))
    return (preds[-1] if preds else None, summaries[-1] if summaries else None)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", required=True, help="Directory with result CSVs")
    parser.add_argument("--output", default="report.md", help="Output markdown file")
    args = parser.parse_args()

    preds_path, summary_path = find_latest_files(args.results)

    if not summary_path:
        print(f"No summary files found in {args.results}")
        return

    summary_rows = load_summary_csv(summary_path)

    lines = []
    lines.append("# GuardReasoner Evaluation Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(format_table(summary_rows))
    lines.append("")

    # Best policy
    best = max(summary_rows, key=lambda r: float(r.get("F1", 0)))
    lines.append(f"**Best policy:** `{best['policy']}` with F1 = {best['F1']}")
    lines.append("")

    # Precision/recall tradeoff note
    lines.append("## Observations")
    lines.append("")
    lines.append("- Precision and recall trade off with policy detail.")
    lines.append("- More policy detail is not always better (compare `full` vs `very_long`).")
    lines.append("- Check raw predictions CSV for false positive/negative analysis.")
    lines.append("")

    lines.append("## Files")
    lines.append("")
    if preds_path:
        lines.append(f"- Predictions: `{preds_path}`")
    lines.append(f"- Summary: `{summary_path}`")
    lines.append("")

    report = "\n".join(lines)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Report written to {args.output}")


if __name__ == "__main__":
    main()
