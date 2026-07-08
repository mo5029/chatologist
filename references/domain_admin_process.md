# Domain Admin Process

Chatologist no longer ships fixed industry domain packs. Each audit creates its own domain admin: a small, editable codebook built from the user's audit request and a controlled sample of their normalized chat messages.

The goal is to make the labels fit the user's real world instead of forcing the user into Chatologist's preset categories.

## What A Domain Admin Is

A domain admin is the audit-specific authority for:

- which messages count as in-scope;
- which messages should be excluded but still counted for transparency;
- what work domains, tasks, AI roles, artifacts, human-value sources, verification burdens, risks, and skill levels reviewers may assign;
- how sensitive material should be handled;
- what the reviewer should inspect before full labeling.

The generated files live in:

```text
audit_output/setup/domain_admin.json
audit_output/setup/domain_admin_manifest.json
audit_output/setup/domain_admin.md
```

`domain_admin.json` is the machine-readable codebook used by batching, validation, baseline labels, and aggregation. `domain_admin.md` is the human-readable review guide. `domain_admin_manifest.json` records the generation context.

## Default Generation Step

The one-command pipeline runs this automatically after ingestion:

```bash
python scripts/build_domain_admin.py \
  --messages-csv audit_output/normalized/messages.csv \
  --output-dir audit_output/setup \
  --audit-request "Audit how my team uses AI for customer research and product decisions" \
  --admin-sample-percent 15 \
  --admin-min-messages 25 \
  --admin-max-messages 200
```

The admin builder:

1. Reads the user's audit request.
2. Samples normalized messages using the same cost-control logic as the main pipeline, with a small minimum sample when enough messages are available.
3. Extracts repeated terms from the request, conversation titles, and sampled message text.
4. Derives a readable domain ID.
5. Creates inclusion keywords.
6. Creates a first-pass set of work-domain labels shaped by the request and sampled terms.
7. Adds universal task, role, value, verification, risk, and skill-level dimensions.
8. Writes a reviewable codebook and compatibility `domain_selection.json`.

## Human Or Model Review

Before research-grade labeling, inspect `domain_admin.md` and edit `domain_admin.json`.

Check:

- the domain ID names the user's actual audit lens;
- `selection_keywords` are specific enough to find the right messages without swallowing unrelated ones;
- `work_domains` are meaningful in the user's context;
- `task_types` split behaviors that matter for the research question;
- `exclusion_labels` keep medical, personal, legal, account, and unrelated messages visible but outside conclusions;
- `human_value_sources` capture the scarce human inputs the user cares about;
- `verification_types` name how a real user would check the output;
- `risk_domains` cover the likely failure modes;
- labels are short, uppercase, stable, and easy for reviewers to apply consistently.

If the draft feels generic, edit it. A good domain admin should feel like it belongs to that user's dataset.

## Using The Admin Downstream

Pass the generated admin to every downstream command:

```bash
python scripts/make_batches.py \
  --messages-csv audit_output/normalized/messages.csv \
  --output-dir audit_output/setup \
  --domain "$(python - <<'PY'
import json
print(json.load(open('audit_output/setup/domain_selection.json'))['selected_domain_pack'])
PY
)" \
  --domain-admin audit_output/setup/domain_admin.json \
  --user-audit-request "Audit how my team uses AI for customer research and product decisions" \
  --sample-percent 10
```

Validation and aggregation use the same admin:

```bash
python scripts/validate_labels.py \
  --labels audit_output/labels \
  --domain your-generated-domain-id \
  --domain-admin audit_output/setup/domain_admin.json \
  --output audit_output/report/label_validation.json

python scripts/aggregate_results.py \
  --labels audit_output/labels \
  --domain your-generated-domain-id \
  --domain-admin audit_output/setup/domain_admin.json \
  --output-dir audit_output/report
```

## Quality Bar

A domain admin is ready when:

- another reviewer can explain what each label means without asking the original user;
- out-of-scope categories are explicit;
- sensitive categories are handled conservatively;
- no field is so broad that most rows collapse into one label;
- no label depends on private information that cannot be paraphrased safely;
- the admin can be reused to validate labels deterministically.

## Template Only

`references/domain_admin_template.json` is not a domain pack library. It exists only as a neutral fallback and schema example. Real audits should generate and review their own `setup/domain_admin.json`.
