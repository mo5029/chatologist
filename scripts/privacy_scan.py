#!/usr/bin/env python3
"""Scan outputs for obvious privacy leaks before sharing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_work_audit_lib import privacy_scan_path, write_csv


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan files/directories for obvious emails, URLs, paths, phone-like strings, and key-like tokens.")
    parser.add_argument("--path", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--fail-on-findings", action="store_true")
    args = parser.parse_args()

    findings = privacy_scan_path(Path(args.path))
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(findings, output_dir / "privacy_findings.csv", ["path", "email", "url", "phone_like", "private_path", "api_key_like"])
    report = {"scanned_path": args.path, "finding_files": len(findings), "output": str(output_dir / "privacy_findings.csv")}
    (output_dir / "privacy_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if args.fail_on_findings and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
