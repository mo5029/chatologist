#!/usr/bin/env python3
"""Aggregate validated label JSONL files into tables and a report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_work_audit_lib import aggregate_labels, iter_jsonl_files, load_domain_packs, read_jsonl, validate_label_rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate label rows into report outputs.")
    parser.add_argument("--labels", required=True)
    parser.add_argument("--domain", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--allow-invalid", action="store_true", help="Aggregate even if validation errors exist.")
    args = parser.parse_args()

    packs = load_domain_packs()
    if args.domain not in packs:
        raise SystemExit(f"Unknown domain pack: {args.domain}")
    rows = []
    for file in iter_jsonl_files(Path(args.labels)):
        rows.extend(read_jsonl(file))
    errors = validate_label_rows(rows, packs[args.domain])
    if errors and not args.allow_invalid:
        print(json.dumps({"error_count": len(errors), "errors": errors[:50]}, indent=2))
        return 1
    summary = aggregate_labels(rows, Path(args.output_dir), args.domain)
    print(json.dumps({"aggregated_rows": len(rows), "output_dir": args.output_dir, "summary_keys": list(summary)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
