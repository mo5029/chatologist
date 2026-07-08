import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    def run_cmd(self, args):
        result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
        if result.returncode != 0:
            self.fail(f"command failed: {' '.join(args)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
        return result

    def test_openai_sample_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "openai"
            self.run_cmd(
                [
                    sys.executable,
                    "scripts/run_pipeline.py",
                    "--input",
                    "examples/sample_openai_export/conversations.json",
                    "--output-dir",
                    str(out),
                    "--audit-request",
                    "Audit engineering student AI use",
                    "--domain",
                    "auto",
                    "--sample-percent",
                    "100",
                    "--baseline-label",
                ]
            )
            self.assertTrue((out / "normalized/messages.csv").exists())
            self.assertTrue((out / "setup/domain_admin.json").exists())
            self.assertTrue((out / "setup/domain_admin.md").exists())
            self.assertTrue((out / "setup/labeling_instructions.md").exists())
            self.assertTrue((out / "report/domain_report.md").exists())
            manifest = json.loads((out / "pipeline_manifest.json").read_text())
            domain_admin = json.loads((out / "setup/domain_admin.json").read_text())
            self.assertIn(manifest["selected_domain_pack"], domain_admin)
            self.assertTrue(json.loads((out / "setup/domain_selection.json").read_text())["generated"])
            with (out / "report/coded_messages.csv").open() as fh:
                rows = list(csv.DictReader(fh))
            self.assertGreaterEqual(len(rows), 3)

    def test_claude_sample_pipeline_finance(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "claude"
            self.run_cmd(
                [
                    sys.executable,
                    "scripts/run_pipeline.py",
                    "--input",
                    "examples/sample_claude_export/conversations.json",
                    "--output-dir",
                    str(out),
                    "--audit-request",
                    "Audit finance work and verification burden",
                    "--domain",
                    "auto",
                    "--sample-percent",
                    "100",
                    "--baseline-label",
                ]
            )
            manifest = json.loads((out / "pipeline_manifest.json").read_text())
            domain_admin = json.loads((out / "setup/domain_admin.json").read_text())
            self.assertIn(manifest["selected_domain_pack"], domain_admin)
            self.assertTrue((out / "evidence/evidence_table.md").exists())

    def test_sampling_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            norm = Path(tmp) / "norm"
            setup = Path(tmp) / "setup"
            self.run_cmd(
                [
                    sys.executable,
                    "scripts/ingest_chat_export.py",
                    "--input",
                    "examples/sample_openai_export/conversations.json",
                    "--output-dir",
                    str(norm),
                ]
            )
            self.run_cmd(
                [
                    sys.executable,
                    "scripts/build_domain_admin.py",
                    "--messages-csv",
                    str(norm / "messages.csv"),
                    "--output-dir",
                    str(setup),
                    "--audit-request",
                    "Audit engineering work",
                    "--domain-id",
                    "engineering-work",
                ]
            )
            self.run_cmd(
                [
                    sys.executable,
                    "scripts/make_batches.py",
                    "--messages-csv",
                    str(norm / "messages.csv"),
                    "--output-dir",
                    str(setup),
                    "--domain",
                    "engineering-work",
                    "--domain-admin",
                    str(setup / "domain_admin.json"),
                    "--user-audit-request",
                    "Audit engineering work",
                    "--sample-percent",
                    "50",
                    "--max-messages",
                    "1",
                ]
            )
            manifest = json.loads((setup / "batch_manifest.json").read_text())
            self.assertEqual(manifest["sampled_messages"], 1)


if __name__ == "__main__":
    unittest.main()
