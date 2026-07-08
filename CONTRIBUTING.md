# Contributing to Chatologist

Thanks for considering a contribution. Chatologist is a local-first skill/toolkit for turning exported AI chats into evidence about usage, value, automation, learning, verification, and human judgment.

Most contributions fall into one of five buckets:

1. **Import formats** — better handling for ChatGPT, Claude, or generic JSON/JSONL exports.
2. **Domain admin quality** — better generated codebooks, review instructions, validation, or schema clarity.
3. **Labeling workflow** — batch generation, multi-agent instructions, adjudication, and quality checks.
4. **Privacy and security** — safer defaults, stronger scans, clearer handling of sensitive outputs.
5. **Documentation** — install paths, friend testing, examples, and research usage notes.

Small focused PRs are better than large rewrites.

---

## Quick Orientation

Chatologist is intentionally lightweight:

- no runtime dependencies beyond Python stdlib;
- no backend;
- no account scraping;
- no telemetry;
- no fixed industry domain packs.

The normal pipeline is:

```text
export -> normalize -> build domain admin -> batch -> label -> validate -> report -> privacy scan
```

## What To Edit

| I want to change... | Edit this |
|---|---|
| Core parsing, domain-admin generation, labels, reports | `scripts/ai_work_audit_lib.py` |
| One-command pipeline | `scripts/run_pipeline.py` |
| Export ingestion CLI | `scripts/ingest_chat_export.py` |
| Domain admin CLI | `scripts/build_domain_admin.py` |
| Batch creation | `scripts/make_batches.py` |
| Validation | `scripts/validate_labels.py` |
| Aggregation | `scripts/aggregate_results.py` |
| Evidence export | `scripts/export_evidence_table.py` |
| Privacy scan | `scripts/privacy_scan.py` |
| Codex skill instructions | `SKILL.md` |
| Claude Code skill wrapper | `.claude/skills/chatologist/SKILL.md` |
| Portable skill package | `skills/chatologist/SKILL.md` |
| User docs | `README.md`, `INSTALL.md`, `FRIEND_TESTING.md`, `references/` |
| Tests | `tests/test_pipeline.py` |

## Source Of Truth

For now, the skill instructions are deliberately duplicated for easy use in different agents:

- `SKILL.md` supports root-folder Codex installation.
- `.claude/skills/chatologist/SKILL.md` supports project-local Claude Code use.
- `skills/chatologist/SKILL.md` supports skill-registry-style packaging.

If you change behavior rules, update all relevant copies in the same PR.

## Running Tests

```bash
python3 -m unittest discover -s tests
```

Run a full smoke test:

```bash
python3 scripts/run_pipeline.py \
  --input examples/sample_openai_export/conversations.json \
  --output-dir tmp/sample_student \
  --audit-request "Audit student learning and technical problem-solving with AI" \
  --sample-percent 100 \
  --baseline-label
```

Expected:

- validation returns zero errors;
- `tmp/sample_student/setup/domain_admin.md` exists;
- `tmp/sample_student/report/domain_report.md` exists;
- `tmp/sample_student/evidence/evidence_table.md` exists.

## Privacy Rules For Contributors

- Never commit private exports or real user audit outputs.
- Use synthetic examples only.
- Do not quote raw private messages in docs, tests, fixtures, or issues.
- Prefer paraphrased evidence.
- If adding tests for sensitive categories, create toy data.

## Pull Request Guidelines

- Keep one concern per PR.
- Include a short before/after explanation for behavior or documentation changes.
- Add or update tests when scripts change.
- Run the smoke test when touching pipeline behavior.
- Mention privacy implications if the change reads, writes, or exposes data differently.

## Style

- Keep scripts stdlib-only unless there is a strong reason to add a dependency.
- Prefer explicit, readable JSON/CSV contracts.
- Use stable output paths.
- Preserve backward-compatible flags where reasonable.
- Treat baseline labels as smoke-test labels, never as academic labels.
- Keep GitHub-facing docs friendly but precise.
