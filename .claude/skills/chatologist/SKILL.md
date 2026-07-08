---
name: "Chatologist"
description: "Analyze user-provided OpenAI, Anthropic, Claude, ChatGPT, or generic LLM chat exports into audits of usage, value, automation, verification burden, learning, and human judgment. Use when users ask what they, their company, their class, or their family are using AI for; what value they derive; what AI is taking over; or how a custom domain-specific codebook should classify their chat history."
---

# Chatologist

## What This Skill Does

This skill audits user-provided LLM chat exports. It normalizes messages, builds a per-user domain admin from the user's request and sampled messages, creates multi-agent labeling batches, validates labels, aggregates results, exports evidence tables, and runs privacy scans.

Do not scrape accounts. The user must provide an OpenAI/Anthropic/Claude/ChatGPT export file or extracted export directory.

## Quick Start

From the repository root:

```bash
python scripts/run_pipeline.py \
  --input /path/to/export.zip \
  --output-dir audit_output \
  --audit-request "Audit how I use AI for my work or studies" \
  --sample-percent 10
```

Smoke test:

```bash
python scripts/run_pipeline.py \
  --input examples/sample_openai_export/conversations.json \
  --output-dir tmp/sample_student \
  --audit-request "Audit student learning and technical problem-solving with AI" \
  --sample-percent 100 \
  --baseline-label
```

## Required Process

1. If needed, explain how to export data.
   - ChatGPT: profile menu -> `Settings` -> `Data controls` -> `Export data`.
   - Claude: web app or Claude Desktop -> initials -> `Settings` -> `Privacy` -> `Export data`.
2. Respect `--sample-percent` and `--max-messages` to control token cost.
3. Ingest only data the user exports and provides.
4. Build a generated domain admin with `scripts/build_domain_admin.py` or `scripts/run_pipeline.py`.
5. Review `setup/domain_admin.md` and refine `setup/domain_admin.json` before serious labeling.
6. Generate batches with `scripts/make_batches.py`, passing the generated `--domain-admin`.
7. Have one or more model/agent reviewers label each batch.
8. Validate with `scripts/validate_labels.py`.
9. Aggregate with `scripts/aggregate_results.py`.
10. Export evidence with `scripts/export_evidence_table.py`.
11. Scan outputs with `scripts/privacy_scan.py` before sharing.

## References

Use the root repository references:

- `references/domain_admin_process.md`
- `references/domain_admin_schema.md`
- `references/workflow.md`
- `references/schema.md`
- `references/multi_agent_labeling.md`
- `references/privacy.md`

## Validity Rules

- There are no bundled domain packs; generate one admin per user and dataset.
- Baseline labels are only for smoke tests.
- Do not quote raw private messages in external reports.
- Keep excluded rows in audit outputs but outside domain conclusions.
- Treat outputs as descriptive unless the user provides a causal design.
