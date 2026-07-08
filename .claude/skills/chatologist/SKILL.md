---
name: "Chatologist"
description: "Analyze user-provided OpenAI, Anthropic, Claude, ChatGPT, or generic LLM chat exports into audits of usage, value, automation, verification burden, and human judgment. Use when users ask what they, their company, or their family are using AI for; what value they derive; what AI is taking over; or how usage differs across finance, education, engineering, research, software, or custom domains."
---

# Chatologist

## What This Skill Does

This skill audits user-provided LLM chat exports. It normalizes messages, selects or creates a domain pack from the user's request, samples only the requested percentage when cost matters, creates multi-agent labeling batches, validates labels, aggregates results, exports evidence tables, and runs privacy scans.

Do not scrape accounts. The user must provide an OpenAI/Anthropic/Claude/ChatGPT export file or extracted export directory.

## Quick Start

From the repository root:

```bash
python scripts/run_pipeline.py \
  --input /path/to/export.zip \
  --output-dir audit_output \
  --audit-request "Audit how I use AI in education work" \
  --domain auto \
  --sample-percent 10
```

Smoke test:

```bash
python scripts/run_pipeline.py \
  --input examples/sample_claude_export/conversations.json \
  --output-dir tmp/sample_finance \
  --audit-request "Audit finance work and verification burden" \
  --domain auto \
  --baseline-label
```

## Required Process

1. Use the user's request and the active AI model's judgment to select the domain pack.
2. Respect `--sample-percent` and `--max-messages` to control token cost.
3. Ingest only data the user exports and provides.
4. Generate batches with `scripts/make_batches.py`.
5. Have one or more model/agent reviewers label each batch.
6. Validate with `scripts/validate_labels.py`.
7. Aggregate with `scripts/aggregate_results.py`.
8. Export evidence with `scripts/export_evidence_table.py`.
9. Scan outputs with `scripts/privacy_scan.py` before sharing.

## References

Use the root repository references:

- `references/workflow.md`
- `references/domain_selection.md`
- `references/schema.md`
- `references/multi_agent_labeling.md`
- `references/privacy.md`
- `references/domains/`

## Validity Rules

- Baseline labels are only for smoke tests.
- Do not quote raw private messages in external reports.
- Keep excluded rows in audit outputs but outside domain conclusions.
- Treat outputs as descriptive unless the user provides a causal design.
