#!/usr/bin/env python3
"""Export a privacy-safe evidence table from labels."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_work_audit_lib import (
    BASE_LABEL_FIELDS,
    iter_jsonl_files,
    read_jsonl,
    sample_evidence_rows,
    write_csv,
    write_markdown_evidence,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create anonymized evidence table from label rows.")
    parser.add_argument("--labels", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--rows", type=int, default=30)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    labels = []
    for file in iter_jsonl_files(Path(args.labels)):
        labels.extend(read_jsonl(file))
    sample = sample_evidence_rows(labels, args.rows, args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    fields = [f for f in BASE_LABEL_FIELDS if f in {"message_uid", "message_scope", "task_type", "ai_role", "labor_relation", "human_value_visible", "verification_needed", "risk_domain", "confidence", "paraphrased_evidence"}]
    write_csv(sample, output_dir / "evidence_table.csv", fields)
    write_markdown_evidence(sample, output_dir / "evidence_table.md")
    manifest = {"source_label_rows": len(labels), "evidence_rows": len(sample), "outputs": ["evidence_table.csv", "evidence_table.md"]}
    (output_dir / "evidence_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
