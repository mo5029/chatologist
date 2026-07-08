#!/usr/bin/env python3
"""Sample normalized messages and create JSONL batches for multi-agent labeling."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_work_audit_lib import (
    generate_label_instructions,
    load_domain_packs,
    read_messages_csv,
    sample_messages,
    write_batches,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create sampled labeling batches.")
    parser.add_argument("--messages-csv", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--domain", required=True)
    parser.add_argument("--domain-admin", help="Generated domain_admin.json for this audit.")
    parser.add_argument("--user-audit-request", dest="user_audit_request", default="")
    parser.add_argument("--user-prompt", dest="user_audit_request", help=argparse.SUPPRESS)
    parser.add_argument("--user-audit-request-file", dest="user_audit_request_file")
    parser.add_argument("--user-prompt-file", dest="user_audit_request_file", help=argparse.SUPPRESS)
    parser.add_argument("--sample-percent", type=float, default=100.0, help="Percent of messages to check, 0-100.")
    parser.add_argument("--max-messages", type=int, help="Optional hard cap after percentage sampling.")
    parser.add_argument("--batch-size", type=int, default=40)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    packs = load_domain_packs(Path(args.domain_admin) if args.domain_admin else None)
    if args.domain not in packs:
        raise SystemExit(f"Unknown domain admin ID: {args.domain}")
    user_request = Path(args.user_audit_request_file).read_text(encoding="utf-8") if args.user_audit_request_file else args.user_audit_request
    rows = read_messages_csv(Path(args.messages_csv))
    sampled = sample_messages(rows, args.sample_percent, args.max_messages, args.seed)
    output_dir = Path(args.output_dir)
    batch_dir = output_dir / "batches"
    batch_paths = write_batches(sampled, batch_dir, args.batch_size, args.domain, user_request)
    instructions = generate_label_instructions(args.domain, packs[args.domain], user_request)
    (output_dir / "labeling_instructions.md").write_text(instructions, encoding="utf-8")
    manifest = {
        "source_messages_csv": str(Path(args.messages_csv)),
        "domain": args.domain,
        "domain_admin": args.domain_admin,
        "sample_percent": args.sample_percent,
        "max_messages": args.max_messages,
        "batch_size": args.batch_size,
        "seed": args.seed,
        "total_messages": len(rows),
        "sampled_messages": len(sampled),
        "batch_count": len(batch_paths),
        "batches": [str(p) for p in batch_paths],
    }
    (output_dir / "batch_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
