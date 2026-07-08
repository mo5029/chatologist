# Chatologist Workflow

## Inputs

The user must provide an exported chat archive:

- OpenAI/ChatGPT export ZIP or extracted `conversations.json`
- Anthropic/Claude export JSON or extracted directory
- Generic JSON/JSONL with messages or conversations

Do not scrape browser sidebars, account pages, inboxes, or live chats.

## Exporting Data

Chatologist starts from a user-provided export file. If the user has not exported data yet, guide them through the official export flow.

### ChatGPT Export

Official guide: https://help.openai.com/en/articles/7260999-how-do-i-export-my-chatgpt-history-and-data

1. Sign in to ChatGPT.
2. Open the profile menu.
3. Select `Settings`.
4. Select `Data controls`.
5. Under `Export data`, select `Export`.
6. Confirm the export.
7. Download the ZIP from the email or SMS when it arrives.

Notes:

- OpenAI says exports can take up to 7 days.
- The download link expires 24 hours after delivery.
- The user should download while signed in to the same account.
- The ZIP can be passed directly to `--input`, or unzipped and supplied as a folder or `conversations.json`.

### Claude Export

Official guide: https://support.claude.com/en/articles/9450526-export-your-claude-data

1. Open Claude on the web app or Claude Desktop.
2. Click the initials in the lower-left corner.
3. Select `Settings`.
4. Navigate to `Privacy`.
5. Click `Export data`.
6. Download the export from the email when it arrives.

Notes:

- Individual exports are available for Free, Pro, and Max users with active accounts.
- Team or Enterprise exports are handled by the organization's Primary Owner.
- Claude export links expire 24 hours after delivery.
- Claude mobile apps cannot start the export flow.
- The downloaded ZIP or extracted JSON folder can be passed to `--input`.

## Cost Control

Large chat histories can drain tokens. Always confirm or infer a sampling plan:

- `--sample-percent 5` labels 5% of normalized messages.
- `--sample-percent 25` labels 25%.
- `--sample-percent 100` labels all messages.
- `--max-messages N` adds a hard cap after percentage sampling.

For first-pass audits, prefer 5-15% unless the user explicitly requests full coverage.

## Standard Commands

### 1. Ingest

```bash
python scripts/ingest_chat_export.py \
  --input /path/to/export.zip \
  --output-dir audit_output/normalized
```

### 2. Build Domain Admin

```bash
python scripts/build_domain_admin.py \
  --messages-csv audit_output/normalized/messages.csv \
  --output-dir audit_output/setup \
  --audit-request "Audit how I use AI for work, learning, value creation, and verification burden" \
  --admin-sample-percent 15 \
  --admin-min-messages 25 \
  --admin-max-messages 200
```

Review:

```text
audit_output/setup/domain_admin.md
audit_output/setup/domain_admin.json
```

Edit `domain_admin.json` before full labeling if the generated categories do not fit the user's real context.

### 3. Batch

```bash
DOMAIN_ID=$(python - <<'PY'
import json
print(json.load(open("audit_output/setup/domain_selection.json"))["selected_domain_pack"])
PY
)

python scripts/make_batches.py \
  --messages-csv audit_output/normalized/messages.csv \
  --output-dir audit_output/setup \
  --domain "$DOMAIN_ID" \
  --domain-admin audit_output/setup/domain_admin.json \
  --user-audit-request "Audit how I use AI for work, learning, value creation, and verification burden" \
  --sample-percent 10 \
  --batch-size 40
```

### 4. Label

Send these files to model/agent reviewers:

```text
audit_output/setup/domain_admin.md
audit_output/setup/labeling_instructions.md
audit_output/setup/batches/*.jsonl
```

Save reviewer outputs into:

```text
audit_output/labels/
```

For a demo only:

```bash
python scripts/baseline_label.py \
  --batches audit_output/setup/batches \
  --domain "$DOMAIN_ID" \
  --domain-admin audit_output/setup/domain_admin.json \
  --output-dir audit_output/labels
```

### 5. Validate

```bash
python scripts/validate_labels.py \
  --labels audit_output/labels \
  --domain "$DOMAIN_ID" \
  --domain-admin audit_output/setup/domain_admin.json \
  --output audit_output/report/label_validation.json
```

### 6. Aggregate

```bash
python scripts/aggregate_results.py \
  --labels audit_output/labels \
  --domain "$DOMAIN_ID" \
  --domain-admin audit_output/setup/domain_admin.json \
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
  --audit-request "Audit student learning and technical problem-solving with AI" \
  --sample-percent 100 \
  --baseline-label
```

## Completion Criteria

A complete audit has:

- normalized messages;
- generated and reviewed domain admin;
- sampled batch manifest;
- model/agent label files;
- validation report with zero errors;
- summary stats and report;
- anonymized evidence table;
- privacy scan report.
