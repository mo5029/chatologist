# Multi-Agent Labeling

## Purpose

The scripts create a generated domain admin and batches; the agent/model layer performs judgment-heavy labeling.

Use multiple reviewers when the output needs research quality. Use one pass for exploratory analysis. Use baseline labels only for smoke tests.

## Reviewer Inputs

Use:

- `setup/domain_admin.md`
- `setup/domain_admin.json`
- `setup/labeling_instructions.md`
- one `setup/batches/batch_*.jsonl` file

Instruction to reviewer:

> Label every row independently. Return one JSON object per input row using exactly the fields in the instructions. Do not include markdown fences. Do not quote raw sensitive text. If the generated domain admin is unclear for a row, use `review_flag=YES` and explain briefly in `reviewer_notes`.

## Parallelization

Safe parallel units:

- one reviewer per batch;
- multiple reviewers on the same stratified subset for reliability;
- separate reviewers for difficult flagged rows;
- one reviewer assigned only to domain-admin refinement before labeling starts.

Do not let reviewers see expected labels or aggregate results before labeling.

## Adjudication

For publishable work:

1. Double-code at least 10% of messages.
2. Compare core fields:
   - `message_scope`
   - `task_type`
   - `ai_role`
   - `human_value_visible`
   - `labor_relation`
   - `verification_needed`
3. Send disagreements to an adjudicator.
4. Keep original reviewer labels and final adjudicated labels separate.
5. Report agreement metrics if making academic claims.

## Minimum Quality Bar

- The domain admin was reviewed before full labeling.
- Validation script returns zero errors.
- Low-confidence or sensitive rows have `review_flag=YES`.
- Evidence text is paraphrased.
- Out-of-scope rows are not discarded silently.
- Sampling percentage is stated in the report.

## Recommended Batch Size

- 20-40 messages for careful academic labeling.
- 50-100 messages for quick exploratory labeling.
- Smaller batches for high-risk contexts such as health, law, personal finance, security, or education involving minors.
