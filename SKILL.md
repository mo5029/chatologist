---
name: "chatologist"
description: "Analyze user-provided OpenAI, Anthropic, Claude, ChatGPT, or generic LLM chat exports into message-level audits of usage, value, automation, verification burden, and human judgment. Use when the user asks to figure out what they, their company, or their family are using AI for; what value they are deriving; what AI is taking over; or how AI use differs across finance, education, engineering, research, software, or custom domains."
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
  --audit-request "Audit how I use AI for finance work" \
  --domain auto \
  --sample-percent 10
```

For a smoke test with rough baseline labels:

```bash
python scripts/run_pipeline.py \
  --input examples/sample_openai_export/conversations.json \
  --output-dir tmp/sample_engineering \
  --audit-request "Audit engineering student AI use" \
  --domain auto \
  --sample-percent 100 \
  --baseline-label
```

Baseline labels prove the pipeline runs. They are not research-grade labels. For real analysis, generate batches, label them with model/agent reviewers, validate, aggregate, and export evidence.

## Required Workflow

1. Clarify the user's audit request and cost limit.
   - If they specify "only check X%", pass `--sample-percent X`.
   - If they specify a hard cap, pass `--max-messages N`.
   - Default to a small sample first when exports are large.
2. Select the domain pack using the active AI model's judgment from the user's request.
   - Use `engineering`, `finance`, `education`, `research`, `software`, or `general-work` when appropriate.
   - If none fit, create a custom domain pack before batching.
   - `scripts/select_domain_pack.py` is a fallback suggestion, not the final authority.
3. Ingest only user-provided data.
   - Use `scripts/ingest_chat_export.py`.
4. Create sampled batches and labeling instructions.
   - Use `scripts/make_batches.py`.
5. Run multi-agent or multi-pass model labeling.
   - Give reviewers `setup/labeling_instructions.md` and one or more `setup/batches/*.jsonl`.
   - Require one JSON object per input message.
6. Validate labels.
   - Use `scripts/validate_labels.py`.
7. Aggregate results.
   - Use `scripts/aggregate_results.py`.
8. Export an anonymized evidence table.
   - Use `scripts/export_evidence_table.py`.
9. Run privacy scan before sharing.
   - Use `scripts/privacy_scan.py`.

## Domain Pack Rule

The user's AI model and the user's request determine the domain pack. Do not force a fixed domain from keywords alone. Use keyword selection only as a fallback.

Read these when needed:

- Domain selection: `references/domain_selection.md`
- Workflow details: `references/workflow.md`
- Label schema: `references/schema.md`
- Multi-agent labeling: `references/multi_agent_labeling.md`
- Privacy rules: `references/privacy.md`
- Domain definitions: `references/domains/`

## Output Contract

A complete audit should produce:

- `normalized/messages.csv`
- `normalized/messages.jsonl`
- `normalized/messages.sqlite3`
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
- Keep excluded/out-of-scope messages visible in audit files but out of domain-specific conclusions.
- Do not present baseline labels as academic labels.
