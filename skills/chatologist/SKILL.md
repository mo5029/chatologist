---
name: "chatologist"
description: "Analyze user-provided OpenAI, Anthropic, Claude, ChatGPT, or generic LLM chat exports into message-level audits of usage, value, automation, verification burden, learning, and human judgment. Use when the user asks to figure out what they, their company, their class, or their family are using AI for; what value they derive; what AI is taking over; or how a custom domain-specific codebook should classify their chat history."
---

# Chatologist

## Purpose

Turn a user-provided LLM chat export into a structured audit: what the user asks AI to do, what domain the work belongs to, where AI substitutes or complements human work, what value is being created, what human value remains visible, and what requires verification.

Never scrape a user's account. Require the user to provide an export ZIP, JSON, JSONL, or extracted export directory from OpenAI/ChatGPT, Anthropic/Claude, or another source.

## Quick Start

```bash
python scripts/run_pipeline.py \
  --input /path/to/export.zip \
  --output-dir audit_output \
  --audit-request "Audit how I use AI for my work or studies" \
  --sample-percent 10
```

For a smoke test with rough baseline labels:

```bash
python scripts/run_pipeline.py \
  --input examples/sample_openai_export/conversations.json \
  --output-dir tmp/sample_student \
  --audit-request "Audit student learning and technical problem-solving with AI" \
  --sample-percent 100 \
  --baseline-label
```

Baseline labels prove the pipeline runs. They are not research-grade labels. For real analysis, generate batches, label them with model/agent reviewers, validate, aggregate, and export evidence.

## Required Workflow

1. If the user does not already have an export, explain how to get one.
   - ChatGPT: profile menu -> `Settings` -> `Data controls` -> `Export data`.
   - Claude: web app or Claude Desktop -> initials -> `Settings` -> `Privacy` -> `Export data`.
   - Never scrape live accounts or sidebars.
2. Clarify the user's audit request and cost limit.
   - If they specify "only check X%", pass `--sample-percent X`.
   - If they specify a hard cap, pass `--max-messages N`.
   - Default to a small sample first when exports are large.
3. Ingest only user-provided data.
   - Use `scripts/ingest_chat_export.py`.
4. Build a user-specific domain admin.
   - Use `scripts/build_domain_admin.py` or the one-command pipeline.
   - Review `setup/domain_admin.md`.
   - Edit `setup/domain_admin.json` if labels are too generic, too narrow, or missing the user's real context.
5. Create sampled batches and labeling instructions.
   - Use `scripts/make_batches.py`.
   - Pass `--domain-admin setup/domain_admin.json`.
6. Run multi-agent or multi-pass model labeling.
   - Give reviewers `setup/domain_admin.md`, `setup/labeling_instructions.md`, and one or more `setup/batches/*.jsonl`.
   - Require one JSON object per input message.
7. Validate labels.
   - Use `scripts/validate_labels.py` with `--domain-admin setup/domain_admin.json`.
8. Aggregate results.
   - Use `scripts/aggregate_results.py` with `--domain-admin setup/domain_admin.json`.
9. Export an anonymized evidence table.
   - Use `scripts/export_evidence_table.py`.
10. Run privacy scan before sharing.
   - Use `scripts/privacy_scan.py`.

## Domain Admin Rule

There are no bundled industry domain packs. Every audit should generate its own domain admin from the user's request and sampled messages.

The generated admin should be treated as a draft codebook. For serious or academic work, review and refine it before full labeling.

Read these when needed:

- Domain admin process: `references/domain_admin_process.md`
- Domain admin schema: `references/domain_admin_schema.md`
- Workflow details: `references/workflow.md`
- Label schema: `references/schema.md`
- Multi-agent labeling: `references/multi_agent_labeling.md`
- Privacy rules: `references/privacy.md`
- Security policy: `SECURITY.md`

## Output Contract

A complete audit should produce:

- `normalized/messages.csv`
- `normalized/messages.jsonl`
- `normalized/messages.sqlite3`
- `setup/domain_admin.json`
- `setup/domain_admin_manifest.json`
- `setup/domain_admin.md`
- `setup/domain_selection.json`
- `setup/labeling_instructions.md`
- `setup/batches/*.jsonl`
- `labels/*.jsonl` after model/agent labeling
- `report/coded_messages.csv`
- `report/summary_stats.json`
- `report/domain_report.md`
- `evidence/evidence_table.csv`
- `evidence/evidence_table.md`
- `privacy/privacy_findings.csv`

## Safety And Validity

- Do not quote raw private messages in public outputs.
- Treat findings as descriptive unless the user has a real causal design.
- Report sampling percentage prominently.
- Keep excluded/out-of-scope messages visible in audit outputs but out of domain-specific conclusions.
- Do not present baseline labels as academic labels.
