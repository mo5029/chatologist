#!/usr/bin/env python3
"""Validate model/agent-produced label JSONL files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_work_audit_lib import iter_jsonl_files, load_domain_packs, read_jsonl, validate_label_rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate label JSONL files against the selected domain pack.")
    parser.add_argument("--labels", required=True, help="JSONL file or directory of JSONL files.")
    parser.add_argument("--domain", required=True)
    parser.add_argument("--output", help="Optional JSON validation report path.")
    args = parser.parse_args()

    packs = load_domain_packs()
    if args.domain not in packs:
        raise SystemExit(f"Unknown domain pack: {args.domain}")

    all_errors: list[str] = []
    file_counts = {}
    for file in iter_jsonl_files(Path(args.labels)):
        rows = read_jsonl(file)
        file_counts[str(file)] = len(rows)
        errors = validate_label_rows(rows, packs[args.domain])
        all_errors.extend(f"{file}: {e}" for e in errors)

    report = {"domain": args.domain, "file_counts": file_counts, "error_count": len(all_errors), "errors": all_errors}
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
