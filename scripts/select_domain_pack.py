#!/usr/bin/env python3
"""Compatibility wrapper for generating a domain admin from a request.

Prefer build_domain_admin.py when normalized messages are available. This
script remains so old command snippets fail gracefully and produce the new file
shape instead of referring to removed built-in domain packs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_work_audit_lib import build_generated_domain_admin, domain_admin_markdown


def read_audit_request(value: str | None, request_file: str | None) -> str:
    if request_file:
        return Path(request_file).read_text(encoding="utf-8")
    return value or ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a request-only domain admin compatibility manifest.")
    parser.add_argument("--audit-request", dest="audit_request", default="", help="User's analysis request.")
    parser.add_argument("--prompt", dest="audit_request", help=argparse.SUPPRESS)
    parser.add_argument("--audit-request-file", dest="audit_request_file", help="File containing the user's analysis request.")
    parser.add_argument("--prompt-file", dest="audit_request_file", help=argparse.SUPPRESS)
    parser.add_argument("--model-hint", default="", help="Optional model/work context hint.")
    parser.add_argument("--domain", default="auto", help="Optional generated domain ID, or auto.")
    parser.add_argument("--domain-id", default="", help="Optional generated domain ID.")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    audit_request = read_audit_request(args.audit_request, args.audit_request_file)
    if args.model_hint:
        audit_request = f"{audit_request}\n\nModel/work context hint: {args.model_hint}".strip()
    domain_id_hint = args.domain_id or ("" if args.domain in {"", "auto"} else args.domain)
    selected, packs, admin = build_generated_domain_admin(audit_request, [], domain_id_hint or None)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "domain_admin.json").write_text(json.dumps(packs, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "domain_admin_manifest.json").write_text(json.dumps(admin, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "domain_admin.md").write_text(domain_admin_markdown(admin), encoding="utf-8")
    result = {
        "selected_domain_pack": selected,
        "generated": True,
        "domain_admin_path": str(output_dir / "domain_admin.json"),
        "domain_description": packs[selected]["description"],
        "inferred_terms": admin.get("inferred_terms", []),
        "note": "Generated from the request only. Prefer build_domain_admin.py with normalized messages for a fuller domain admin.",
    }
    (output_dir / "domain_selection.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "domain_selection.md").write_text(
        f"# Generated Domain Admin\n\nGenerated domain ID: `{selected}`\n\n{packs[selected]['description']}\n\n"
        "This compatibility command did not inspect messages. Use build_domain_admin.py after ingest for the full workflow.\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
