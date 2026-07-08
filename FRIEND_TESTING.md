# Chatologist Friend Test

Thanks for testing this.

Chatologist turns an exported LLM chat history into structured evidence about what the user asks AI to do, what domain the work belongs to, how much verification is needed, and where human judgment still matters.

## 5 Minute Smoke Test

From the unzipped folder:

```bash
python3 scripts/run_pipeline.py \
  --input examples/sample_openai_export/conversations.json \
  --output-dir tmp/sample_education \
  --audit-request "Audit education and student learning use" \
  --domain auto \
  --sample-percent 100 \
  --baseline-label
```

Expected result:

- The command finishes without errors.
- `tmp/sample_education/report/domain_report.md` exists.
- `tmp/sample_education/setup/domain_selection.json` selects `education`.
- `tmp/sample_education/evidence/evidence_table.md` exists.

## Real Export Test

Use an export file you are comfortable testing locally. Do not send private outputs back unless you review them first.

```bash
python3 scripts/run_pipeline.py \
  --input /path/to/your/export.zip \
  --output-dir audit_output \
  --audit-request "Audit how I use AI for my work or studies" \
  --domain auto \
  --sample-percent 10
```

This creates batches in `audit_output/setup/batches/`. For research-grade labels, send those batches plus `audit_output/setup/labeling_instructions.md` to one or more model/agent reviewers, then put returned JSONL labels in `audit_output/labels/`.

## Feedback Wanted

Please report:

- Operating system and Python version.
- Whether the smoke test worked.
- Whether export ingestion worked for your ChatGPT or Claude export.
- Whether the selected domain pack made sense.
- Any confusing command, file name, or output.

## Privacy Note

The tool is local-first and does not scrape accounts. It only reads files you provide. Before sharing evidence tables or reports, run:

```bash
python3 scripts/privacy_scan.py --path audit_output --output-dir audit_output/privacy
```
