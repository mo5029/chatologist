# Chatologist Friend Test

Thanks for testing this.

Chatologist turns an exported LLM chat history into structured evidence about what the user asks AI to do, what domain the work belongs to, how much verification is needed, and where human judgment still matters.

It now builds a custom **domain admin** for each tester. That means the test should not look for a fixed built-in domain. It should check whether the generated codebook makes sense for the request.

## 5 Minute Smoke Test

From the unzipped folder:

```bash
python3 scripts/run_pipeline.py \
  --input examples/sample_openai_export/conversations.json \
  --output-dir tmp/sample_student \
  --audit-request "Audit student learning and technical problem-solving with AI" \
  --sample-percent 100 \
  --baseline-label
```

Expected result:

- The command finishes without errors.
- `tmp/sample_student/setup/domain_admin.json` exists.
- `tmp/sample_student/setup/domain_admin.md` exists and describes the generated labels.
- `tmp/sample_student/setup/domain_selection.json` contains a generated domain ID.
- `tmp/sample_student/report/domain_report.md` exists.
- `tmp/sample_student/evidence/evidence_table.md` exists.

## Real Export Test

Use an export file you are comfortable testing locally. Do not send private outputs back unless you review them first.

```bash
python3 scripts/run_pipeline.py \
  --input /path/to/your/export.zip \
  --output-dir audit_output \
  --audit-request "Audit how I use AI for my work or studies" \
  --sample-percent 10
```

This creates batches in `audit_output/setup/batches/`. For research-grade labels, first review `audit_output/setup/domain_admin.md` and edit `audit_output/setup/domain_admin.json` if needed. Then send those batches plus `audit_output/setup/labeling_instructions.md` to one or more model/agent reviewers, and put returned JSONL labels in `audit_output/labels/`.

## Feedback Wanted

Please report:

- Operating system and Python version.
- Whether the smoke test worked.
- Whether export ingestion worked for your ChatGPT or Claude export.
- Whether the generated domain admin made sense.
- Any confusing command, file name, or output.

## Privacy Note

The tool is local-first and does not scrape accounts. It only reads files you provide. Before sharing evidence tables or reports, run:

```bash
python3 scripts/privacy_scan.py --path audit_output --output-dir audit_output/privacy
```
