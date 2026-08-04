#!/usr/bin/env python3
"""
Parse and compare evaluation result CSVs.

Usage:
    python parse_results.py --summary results/self_harm/summary_*.csv
"""

import argparse
import csv
import glob


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True, help="Glob pattern for summary CSVs")
    parser.add_argument("--sort-by", default="F1", help="Column to sort by")
    args = parser.parse_args()

    files = sorted(glob.glob(args.summary))
    if not files:
        print(f"No files matched: {args.summary}")
        return

    all_rows = []
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                row["_source"] = f.split("/")[-1]
                all_rows.append(row)

    all_rows.sort(key=lambda r: float(r.get(args.sort_by, 0)), reverse=True)

    print(f"{'Policy':<30} {'F1':>6} {'Prec':>6} {'Rec':>6} {'Acc':>6} {'Err':>4} {'Source':<20}")
    print("-" * 80)
    for r in all_rows:
        print(
            f"{r['policy']:<30} {float(r['F1']):>6.3f} {float(r['precision']):>6.3f} "
            f"{float(r['recall']):>6.3f} {float(r['accuracy']):>6.3f} {r['errors']:>4} {r['_source']:<20}"
        )


if __name__ == "__main__":
    main()
