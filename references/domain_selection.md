# Domain Pack Selection

## Rule

The active AI model selects the domain pack from the user's request and the stated audit goal. Keyword scoring is only a fallback.

Use the model's judgment to answer:

1. What domain does the user want measured?
2. What should count as in-scope?
3. What should be excluded?
4. What human value sources matter in this domain?
5. What verification burdens matter in this domain?

## Built-In Packs

- `engineering`
- `finance`
- `education`
- `research`
- `software`
- `general-work`

Definitions live in `references/domain_packs.json` and readable notes live in `references/domains/`.

## When To Override `auto`

Override the fallback selector when:

- the user's request names a domain directly;
- the user wants a specific lens, such as "education only" or "labor market only";
- the dataset is mixed but the user's question is narrow;
- the existing domain pack would include too much irrelevant content;
- the user asks for a custom codebook.

## Creating A Custom Pack

Create a new entry in `references/domain_packs.json` with:

- `description`
- `selection_keywords`
- `exclusion_labels`
- `work_domains`
- `task_types`
- `ai_roles`
- `artifact_types`
- `human_value_sources`
- `value_mechanisms`
- `verification_types`
- `risk_domains`
- `skill_levels`

Then run:

```bash
python scripts/make_batches.py \
  --messages-csv audit_output/normalized/messages.csv \
  --output-dir audit_output/setup \
  --domain custom-pack-name \
  --user-audit-request "..." \
  --sample-percent 10
```

## Examples

User request:

> I work in finance and want to know what parts of my job AI is helping with.

Use `finance`.

User request:

> I teach and want to analyze whether I use AI more as a tutor, feedback assistant, or curriculum helper.

Use `education`.

User request:

> I am an engineering student and want to know what economic value engineers still bring when AI can answer technical questions.

Use `engineering`.

User request:

> I am a founder and my chats mix fundraising, customer calls, product strategy, and operations.

Use `general-work` or create a `startup-operator` custom pack.
