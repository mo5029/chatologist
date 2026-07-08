#!/usr/bin/env python3
"""Generate cheap baseline labels for smoke tests and demos.

These labels are intentionally low confidence and review-flagged. They prove the
pipeline runs; they are not research-grade labels.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_work_audit_lib import baseline_label, iter_jsonl_files, load_domain_packs, read_jsonl


def main() -> int:
    parser = argparse.ArgumentParser(description="Create baseline labels for batches.")
    parser.add_argument("--batches", required=True, help="Batch JSONL file or batch directory.")
    parser.add_argument("--domain", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    packs = load_domain_packs()
    if args.domain not in packs:
        raise SystemExit(f"Unknown domain pack: {args.domain}")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    total = 0
    outputs = []
    for batch in iter_jsonl_files(Path(args.batches)):
        rows = read_jsonl(batch)
        labels = [baseline_label(row, args.domain, packs[args.domain]) for row in rows]
        out = output_dir / batch.name
        with out.open("w", encoding="utf-8") as fh:
            for label in labels:
                fh.write(json.dumps(label, ensure_ascii=False) + "\n")
        total += len(labels)
        outputs.append(str(out))
    manifest = {"domain": args.domain, "baseline_labels": total, "outputs": outputs}
    (output_dir / "baseline_label_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
