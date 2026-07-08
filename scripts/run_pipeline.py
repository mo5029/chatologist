#!/usr/bin/env python3
"""Run the Chatologist pipeline end to end.

Every run now builds a per-user domain admin before batching. Use
--baseline-label for smoke tests and demos. For research-grade analysis, omit
--baseline-label, review the generated domain admin, send the generated batches
to model/agent reviewers, then run aggregate_results.py and
export_evidence_table.py on the returned labels.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def run(cmd: list[str]) -> None:
    print("+ " + " ".join(cmd))
    subprocess.run(cmd, check=True)


def load_selected_domain(path: Path) -> str:
    data = json.loads((path / "domain_selection.json").read_text(encoding="utf-8"))
    return data["selected_domain_pack"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ingest -> domain admin -> sampling/batching -> optional baseline/report.")
    parser.add_argument("--input", required=True, help="User-provided export ZIP/JSON/JSONL/directory.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--audit-request", dest="audit_request", default="", help="User analysis request used for domain selection and labeling instructions.")
    parser.add_argument("--prompt", dest="audit_request", help=argparse.SUPPRESS)
    parser.add_argument("--audit-request-file", dest="audit_request_file")
    parser.add_argument("--prompt-file", dest="audit_request_file", help=argparse.SUPPRESS)
    parser.add_argument("--model-hint", default="", help="Optional user's AI model/work context.")
    parser.add_argument("--domain-id", default="", help="Optional explicit ID for the generated domain admin.")
    parser.add_argument("--domain", default="auto", help=argparse.SUPPRESS)
    parser.add_argument("--admin-sample-percent", type=float, default=15.0, help="Percent of messages used to draft the domain admin.")
    parser.add_argument("--admin-min-messages", type=int, default=25, help="Minimum messages used to draft the domain admin when available.")
    parser.add_argument("--admin-max-messages", type=int, default=200, help="Hard cap for domain-admin drafting sample.")
    parser.add_argument("--sample-percent", type=float, default=100.0)
    parser.add_argument("--max-messages", type=int)
    parser.add_argument("--batch-size", type=int, default=40)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--baseline-label", action="store_true", help="Generate rough labels for smoke testing.")
    args = parser.parse_args()

    output = Path(args.output_dir)
    normalized = output / "normalized"
    setup = output / "setup"
    labels = output / "labels"
    report = output / "report"
    evidence = output / "evidence"
    privacy = output / "privacy"
    output.mkdir(parents=True, exist_ok=True)

    request_args = ["--audit-request", args.audit_request]
    if args.audit_request_file:
        request_args = ["--audit-request-file", args.audit_request_file]

    run([sys.executable, str(HERE / "ingest_chat_export.py"), "--input", args.input, "--output-dir", str(normalized)])
    domain_id = args.domain_id or ("" if args.domain in {"", "auto"} else args.domain)
    domain_cmd = [
        sys.executable,
        str(HERE / "build_domain_admin.py"),
        "--messages-csv",
        str(normalized / "messages.csv"),
        "--output-dir",
        str(setup),
        "--admin-sample-percent",
        str(args.admin_sample_percent),
        "--admin-min-messages",
        str(args.admin_min_messages),
        "--admin-max-messages",
        str(args.admin_max_messages),
        "--seed",
        str(args.seed),
    ]
    if domain_id:
        domain_cmd += ["--domain-id", domain_id]
    domain_cmd += request_args
    run(domain_cmd)
    selected = load_selected_domain(setup)
    domain_admin = setup / "domain_admin.json"
    batch_cmd = [
        sys.executable,
        str(HERE / "make_batches.py"),
        "--messages-csv",
        str(normalized / "messages.csv"),
        "--output-dir",
        str(setup),
        "--domain",
        selected,
        "--domain-admin",
        str(domain_admin),
        "--sample-percent",
        str(args.sample_percent),
        "--batch-size",
        str(args.batch_size),
        "--seed",
        str(args.seed),
    ]
    if args.audit_request_file:
        batch_cmd += ["--user-audit-request-file", args.audit_request_file]
    else:
        batch_cmd += ["--user-audit-request", args.audit_request]
    if args.max_messages is not None:
        batch_cmd += ["--max-messages", str(args.max_messages)]
    run(batch_cmd)

    if args.baseline_label:
        run([sys.executable, str(HERE / "baseline_label.py"), "--batches", str(setup / "batches"), "--domain", selected, "--domain-admin", str(domain_admin), "--output-dir", str(labels)])
        run([sys.executable, str(HERE / "validate_labels.py"), "--labels", str(labels), "--domain", selected, "--domain-admin", str(domain_admin), "--output", str(report / "label_validation.json")])
        run([sys.executable, str(HERE / "aggregate_results.py"), "--labels", str(labels), "--domain", selected, "--domain-admin", str(domain_admin), "--output-dir", str(report)])
        run([sys.executable, str(HERE / "export_evidence_table.py"), "--labels", str(labels), "--output-dir", str(evidence)])
        run([sys.executable, str(HERE / "privacy_scan.py"), "--path", str(evidence), "--output-dir", str(privacy)])

    manifest = {
        "output_dir": str(output),
        "selected_domain_pack": selected,
        "domain_admin": str(domain_admin),
        "baseline_label": args.baseline_label,
        "next_step": "If baseline_label is false, review setup/domain_admin.md and setup/domain_admin.json, then send setup/batches/*.jsonl and setup/labeling_instructions.md to model/agent reviewers.",
    }
    (output / "pipeline_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
