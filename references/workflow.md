# Chatologist Workflow

## Inputs

The user must provide an exported chat archive:

- OpenAI/ChatGPT export ZIP or extracted `conversations.json`
- Anthropic/Claude export JSON or extracted directory
- Generic JSON/JSONL with messages or conversations

Do not scrape browser sidebars, account pages, inboxes, or live chats.

## Cost Control

Large chat histories can drain tokens. Always confirm or infer a sampling plan:

- `--sample-percent 5` labels 5% of normalized messages.
- `--sample-percent 25` labels 25%.
- `--sample-percent 100` labels all messages.
- `--max-messages N` adds a hard cap after percentage sampling.

For first pass audits, prefer 5-15% unless the user explicitly requests full coverage.

## Standard Commands

### 1. Ingest

```bash
python scripts/ingest_chat_export.py \
  --input /path/to/export.zip \
  --output-dir audit_output/normalized
```

### 2. Select Domain Pack

```bash
python scripts/select_domain_pack.py \
  --audit-request "Audit how I use AI for finance work" \
  --domain auto \
  --output-dir audit_output/setup
```

Treat this output as a suggestion. The active AI model should override it when the user's request clearly implies another pack or a custom pack.

### 3. Batch

```bash
python scripts/make_batches.py \
  --messages-csv audit_output/normalized/messages.csv \
  --output-dir audit_output/setup \
  --domain finance \
  --user-audit-request "Audit how I use AI for finance work" \
  --sample-percent 10 \
  --batch-size 40
```

### 4. Label

Send `audit_output/setup/labeling_instructions.md` and batch files to model/agent reviewers. Save their JSONL outputs into `audit_output/labels/`.

For a demo only:

```bash
python scripts/baseline_label.py \
  --batches audit_output/setup/batches \
  --domain finance \
  --output-dir audit_output/labels
```

### 5. Validate

```bash
python scripts/validate_labels.py \
  --labels audit_output/labels \
  --domain finance \
  --output audit_output/report/label_validation.json
```

### 6. Aggregate

```bash
python scripts/aggregate_results.py \
  --labels audit_output/labels \
  --domain finance \
  --output-dir audit_output/report
```

### 7. Evidence Table

```bash
python scripts/export_evidence_table.py \
  --labels audit_output/labels \
  --output-dir audit_output/evidence
```

### 8. Privacy Scan

```bash
python scripts/privacy_scan.py \
  --path audit_output/evidence \
  --output-dir audit_output/privacy
```

## One-Command Smoke Test

```bash
python scripts/run_pipeline.py \
  --input examples/sample_openai_export/conversations.json \
  --output-dir tmp/sample \
  --audit-request "Audit engineering student AI use" \
  --domain auto \
  --sample-percent 100 \
  --baseline-label
```

## Completion Criteria

A complete audit has:

- normalized messages;
- selected or custom domain pack;
- sampled batch manifest;
- model/agent label files;
- validation report with zero errors;
- summary stats and report;
- anonymized evidence table;
- privacy scan report.
