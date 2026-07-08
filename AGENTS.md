# Agent Notes

This repo is a local-first AI chat audit toolkit. Keep changes privacy-preserving and evidence-grounded.

## Local Development Overrides

- Development mode: full-auto.
- Sandbox preference: workspace-write when a local environment can enforce it.
- Web search preference: live.
- Enable verbose logging for development when debugging.
- Keep local-only credentials, exports, and machine-specific settings out of commits.

## Core Invariants

- Do not add account scraping.
- Do not add telemetry, analytics, or a backend.
- Do not commit private exports or real audit outputs.
- Keep runtime scripts stdlib-only unless a dependency is clearly justified.
- Treat `--baseline-label` as a smoke-test helper, never as research-grade labeling.
- Preserve the generated domain-admin workflow.

## Main Workflow

```text
export -> normalize -> build domain admin -> batch -> label -> validate -> report -> privacy scan
```

## Source Files

- Pipeline orchestration: `scripts/run_pipeline.py`
- Shared logic: `scripts/ai_work_audit_lib.py`
- Domain admin generation: `scripts/build_domain_admin.py`
- User-facing overview: `README.md`
- Install guide: `INSTALL.md`
- Security model: `SECURITY.md`
- Main skill instruction: `SKILL.md`
- Portable skill package: `skills/chatologist/`
- Claude project skill: `.claude/skills/chatologist/`

## Before Publishing Changes

Run:

```bash
python3 -m unittest discover -s tests
python3 scripts/run_pipeline.py \
  --input examples/sample_openai_export/conversations.json \
  --output-dir tmp/sample_student \
  --audit-request "Audit student learning and technical problem-solving with AI" \
  --sample-percent 100 \
  --baseline-label
```

Then check:

- `tmp/sample_student/setup/domain_admin.md`
- `tmp/sample_student/report/domain_report.md`
- `tmp/sample_student/evidence/evidence_table.md`
- `tmp/sample_student/privacy/privacy_findings.csv`

Remove local outputs before committing.
