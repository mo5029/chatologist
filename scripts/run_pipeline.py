#!/usr/bin/env python3
"""Run the Chatologist pipeline end to end.

Use --baseline-label for smoke tests and demos. For research-grade analysis,
omit --baseline-label, send the generated batches to model/agent reviewers, then
run aggregate_results.py and export_evidence_table.py on the returned labels.
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
    parser = argparse.ArgumentParser(description="Run ingest -> domain selection -> sampling/batching -> optional baseline/report.")
    parser.add_argument("--input", required=True, help="User-provided export ZIP/JSON/JSONL/directory.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--audit-request", dest="audit_request", default="", help="User analysis request used for domain selection and labeling instructions.")
    parser.add_argument("--prompt", dest="audit_request", help=argparse.SUPPRESS)
    parser.add_argument("--audit-request-file", dest="audit_request_file")
    parser.add_argument("--prompt-file", dest="audit_request_file", help=argparse.SUPPRESS)
    parser.add_argument("--model-hint", default="", help="Optional user's AI model/work context.")
    parser.add_argument("--domain", default="auto", help="Explicit domain pack or auto.")
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
    run([sys.executable, str(HERE / "select_domain_pack.py"), *request_args, "--model-hint", args.model_hint, "--domain", args.domain, "--output-dir", str(setup)])
    selected = load_selected_domain(setup)
    batch_cmd = [
        sys.executable,
        str(HERE / "make_batches.py"),
        "--messages-csv",
        str(normalized / "messages.csv"),
        "--output-dir",
        str(setup),
        "--domain",
        selected,
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
        run([sys.executable, str(HERE / "baseline_label.py"), "--batches", str(setup / "batches"), "--domain", selected, "--output-dir", str(labels)])
        run([sys.executable, str(HERE / "validate_labels.py"), "--labels", str(labels), "--domain", selected, "--output", str(report / "label_validation.json")])
        run([sys.executable, str(HERE / "aggregate_results.py"), "--labels", str(labels), "--domain", selected, "--output-dir", str(report)])
        run([sys.executable, str(HERE / "export_evidence_table.py"), "--labels", str(labels), "--output-dir", str(evidence)])
        run([sys.executable, str(HERE / "privacy_scan.py"), "--path", str(evidence), "--output-dir", str(privacy)])

    manifest = {
        "output_dir": str(output),
        "selected_domain_pack": selected,
        "baseline_label": args.baseline_label,
        "next_step": "If baseline_label is false, send setup/batches/*.jsonl and setup/labeling_instructions.md to model/agent reviewers, then aggregate the returned labels.",
    }
    (output / "pipeline_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
