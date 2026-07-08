#!/usr/bin/env python3
"""Build a per-user domain admin/codebook for a Chatologist audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_work_audit_lib import (
    build_generated_domain_admin,
    domain_admin_markdown,
    read_messages_csv,
    sample_messages,
)


def read_audit_request(value: str | None, request_file: str | None) -> str:
    if request_file:
        return Path(request_file).read_text(encoding="utf-8")
    return value or ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an audit-specific domain admin from the user's request and sampled messages.")
    parser.add_argument("--messages-csv", required=True, help="Normalized messages CSV from ingest_chat_export.py.")
    parser.add_argument("--output-dir", required=True, help="Directory where domain admin files should be written.")
    parser.add_argument("--audit-request", dest="audit_request", default="", help="User's analysis request.")
    parser.add_argument("--prompt", dest="audit_request", help=argparse.SUPPRESS)
    parser.add_argument("--audit-request-file", dest="audit_request_file", help="File containing the user's analysis request.")
    parser.add_argument("--prompt-file", dest="audit_request_file", help=argparse.SUPPRESS)
    parser.add_argument("--domain-id", default="", help="Optional explicit ID for the generated domain admin.")
    parser.add_argument("--domain", default="", help=argparse.SUPPRESS)
    parser.add_argument("--admin-sample-percent", type=float, default=15.0, help="Percent of messages used to draft the admin.")
    parser.add_argument("--admin-min-messages", type=int, default=25, help="Minimum messages used for admin drafting when available.")
    parser.add_argument("--admin-max-messages", type=int, default=200, help="Hard cap for admin-building sample.")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    audit_request = read_audit_request(args.audit_request, args.audit_request_file)
    domain_id_hint = args.domain_id or ("" if args.domain in {"", "auto"} else args.domain)
    rows = read_messages_csv(Path(args.messages_csv))
    sampled = sample_messages(rows, args.admin_sample_percent, args.admin_max_messages, args.seed)
    target_min = min(len(rows), args.admin_min_messages, args.admin_max_messages)
    if len(sampled) < target_min:
        sampled = sample_messages(rows, 100.0, target_min, args.seed)
    domain_id, packs, admin = build_generated_domain_admin(audit_request, sampled, domain_id_hint or None)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "domain_admin.json").write_text(json.dumps(packs, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "domain_admin_manifest.json").write_text(json.dumps(admin, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "domain_admin.md").write_text(domain_admin_markdown(admin), encoding="utf-8")

    compatibility = {
        "selected_domain_pack": domain_id,
        "generated": True,
        "domain_admin_path": str(output_dir / "domain_admin.json"),
        "domain_admin_manifest_path": str(output_dir / "domain_admin_manifest.json"),
        "domain_description": packs[domain_id]["description"],
        "inferred_terms": admin.get("inferred_terms", []),
        "sampled_messages_used": admin.get("sampled_messages_used", 0),
        "note": "Generated per-user domain admin. Inspect and refine setup/domain_admin.json before full labeling.",
    }
    (output_dir / "domain_selection.json").write_text(json.dumps(compatibility, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "domain_selection.md").write_text(
        "# Generated Domain Admin\n\n"
        f"Generated domain ID: `{domain_id}`\n\n"
        f"{packs[domain_id]['description']}\n\n"
        "Review `domain_admin.md` and edit `domain_admin.json` before full labeling if the categories are too broad, too narrow, or missing the user's real context.\n",
        encoding="utf-8",
    )
    print(json.dumps(compatibility, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
