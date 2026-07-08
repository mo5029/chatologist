#!/usr/bin/env python3
"""Select or document the domain pack for an audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_work_audit_lib import load_domain_packs, select_domain_pack


def read_audit_request(value: str | None, request_file: str | None) -> str:
    if request_file:
        return Path(request_file).read_text(encoding="utf-8")
    return value or ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Suggest a domain pack from the user's audit request and model hint.")
    parser.add_argument("--audit-request", dest="audit_request", default="", help="User's analysis request.")
    parser.add_argument("--prompt", dest="audit_request", help=argparse.SUPPRESS)
    parser.add_argument("--audit-request-file", dest="audit_request_file", help="File containing the user's analysis request.")
    parser.add_argument("--prompt-file", dest="audit_request_file", help=argparse.SUPPRESS)
    parser.add_argument("--model-hint", default="", help="Optional model/work context hint.")
    parser.add_argument("--domain", default="auto", help="Explicit domain pack, or auto.")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    packs = load_domain_packs()
    audit_request = read_audit_request(args.audit_request, args.audit_request_file)
    if args.domain != "auto":
        if args.domain not in packs:
            raise SystemExit(f"Unknown domain pack: {args.domain}. Available: {', '.join(sorted(packs))}")
        selected = args.domain
        scores = {name: 0.0 for name in packs}
        scores[selected] = 999.0
    else:
        selected, scores = select_domain_pack(audit_request, args.model_hint, packs)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "selected_domain_pack": selected,
        "selection_scores": scores,
        "domain_description": packs[selected]["description"],
        "note": "Agents should treat this as a suggestion when --domain=auto. The active AI model may override or create a custom pack if the user's request requires it.",
    }
    (output_dir / "domain_selection.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (output_dir / "domain_selection.md").write_text(
        f"# Domain Pack Selection\n\nSelected: `{selected}`\n\n{packs[selected]['description']}\n\n"
        "If the user's request asks for a different classification frame, override this selection before batching.\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
