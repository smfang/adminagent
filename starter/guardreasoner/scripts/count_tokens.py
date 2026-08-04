#!/usr/bin/env python3
"""
Count tokens in policy files to check context window compatibility.

Usage:
    python count_tokens.py policies/self_harm/*.md
"""

import argparse
import glob

import tiktoken


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", help="Policy markdown files")
    parser.add_argument("--max-len", type=int, default=8192, help="Max context window")
    args = parser.parse_args()

    # Use cl100k_base (same as GPT-4 / GuardReasoner likely uses similar)
    enc = tiktoken.get_encoding("cl100k_base")

    print(f"{'Policy':<30} {'Tokens':>8} {'Status':>10}")
    print("-" * 50)

    total = 0
    for pattern in args.files:
        for path in glob.glob(pattern):
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            tokens = len(enc.encode(text))
            total += tokens
            status = "OK" if tokens < args.max_len else "EXCEEDS"
            name = path.split("/")[-1]
            print(f"{name:<30} {tokens:>8} {status:>10}")

    print("-" * 50)
    print(f"{'Total':<30} {total:>8}")
    print(f"\nContext window: {args.max_len} tokens")
    print(f"Policies exceeding limit will fail at inference time.")


if __name__ == "__main__":
    main()
