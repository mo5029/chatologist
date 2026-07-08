# Label Schema

Each output label is one JSON object per input message.

## Required Fields

| Field | Meaning |
| --- | --- |
| `message_uid` | Stable ID from normalized messages. |
| `domain_pack` | Selected domain pack. |
| `message_scope` | `IN_SCOPE`, `DOMAIN_ADJACENT`, `OUT_OF_SCOPE`, `UNREADABLE_OR_EMPTY`, or `DUPLICATE`. |
| `exclusion_label` | Reason for exclusion, or `NA_IN_SCOPE`. |
| `message_author` | `user`, `assistant`, `system`, `tool`, or `unknown`. |
| `message_function` | What the message does: request, answer, correction, artifact, etc. |
| `work_domain` | Domain-specific work area. |
| `task_type` | Domain-specific task type. |
| `ai_role` | Role the AI is playing or being asked to play. |
| `artifact_type` | Main output artifact. |
| `human_value_visible` | Human-side contribution visible in the message or immediate context. |
| `value_mechanism` | How value is created. |
| `labor_relation` | Task-level relationship between AI and human work. |
| `verification_needed` | Main check required before real use. |
| `judgment_required` | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`, or `NA_OUT_OF_SCOPE`. |
| `risk_domain` | Main risk if output is used incorrectly. |
| `skill_level` | Whose skill level the task resembles or supports. |
| `confidence` | `HIGH`, `MEDIUM`, or `LOW`. |
| `review_flag` | `YES` or `NO`. |
| `paraphrased_evidence` | Privacy-safe paraphrase of why the label was assigned. |
| `reviewer_notes` | Internal note. Do not include raw sensitive text. |

## Labor Relation

| Label | Meaning |
| --- | --- |
| `LEARNING_AUGMENTATION` | AI mainly helps the user learn or build skill. |
| `COMPLEMENT` | AI helps the human do better/faster work, but the human still provides meaningful judgment, context, verification, or integration. |
| `PARTIAL_SUBSTITUTION` | AI performs a bounded task that a human would otherwise do, but still needs review or integration. |
| `SUBSTITUTION_LIKE` | AI produces an end-to-end, low-risk deliverable with little visible human contribution. Use rarely. |
| `SUPERVISION_HEAVY` | AI output may help, but only under substantial oversight. |
| `OUT_OF_SCOPE` | Outside the selected domain. |
| `UNCLEAR` | Not enough context. |

## Scope Rule

Only `IN_SCOPE` and `DOMAIN_ADJACENT` rows enter the domain findings. Keep out-of-scope rows for denominator/audit transparency.

## Privacy Rule

`paraphrased_evidence` must summarize. Do not quote:

- names;
- emails;
- phone numbers;
- file paths;
- credentials;
- personal health details;
- raw proprietary code;
- third-party private information.
