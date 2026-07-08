# Domain Admin Schema

`domain_admin.json` is a JSON object keyed by a generated domain ID.

```json
{
  "example-user-domain": {
    "description": "Generated domain admin for this audit request...",
    "selection_keywords": ["student", "engineering", "debug"],
    "exclusion_labels": ["PERSONAL_ADMIN", "HEALTH_MEDICAL"],
    "work_domains": ["ENGINEERING_STUDENT_FOCUS", "LEARNING_OR_EXPLANATION"],
    "task_types": ["ASK_EXPLAIN", "DEBUG_OR_FIX"],
    "ai_roles": ["TUTOR", "DEBUGGER"],
    "artifact_types": ["EXPLANATION", "CODE_OR_SCRIPT"],
    "human_value_sources": ["PROBLEM_FRAMING", "VERIFICATION"],
    "value_mechanisms": ["LEARNING_UPSKILLING", "UNBLOCKING"],
    "verification_types": ["RUN_OR_TEST_OUTPUT", "DOMAIN_EXPERT_REVIEW"],
    "risk_domains": ["CORRECTNESS", "ACADEMIC_INTEGRITY"],
    "skill_levels": ["LEARNER_OR_STUDENT", "JUNIOR"]
  }
}
```

## Required Keys

| Key | Purpose |
| --- | --- |
| `description` | One clear sentence explaining the audit lens. |
| `selection_keywords` | Terms used for rough in-scope detection and smoke-test labels. |
| `exclusion_labels` | Reasons a message is outside the audit even if it stays in the dataset. |
| `work_domains` | User-specific areas of work or learning. |
| `task_types` | Behaviors the user asks AI to perform. |
| `ai_roles` | Functional role the AI plays in the message. |
| `artifact_types` | Main output artifact, if any. |
| `human_value_sources` | Human contribution still visible in the message or context. |
| `value_mechanisms` | How the AI interaction creates value. |
| `verification_types` | Main check required before relying on the output. |
| `risk_domains` | Main failure mode if the output is wrong or misused. |
| `skill_levels` | Skill level implied, supported, or substituted by the task. |

## Label Style

- Use uppercase labels with underscores.
- Keep labels short enough to scan in CSV tables.
- Prefer behavior labels over vague categories.
- Use `OTHER_IN_SCOPE` sparingly as a catch-all.
- Do not add labels that reveal private names, employers, clients, or file paths.
- Keep medical, legal, financial, account, and personal-life exclusions explicit when present.

## Manifest

`domain_admin_manifest.json` records generation metadata:

```json
{
  "domain_id": "engineering-student-use",
  "generated": true,
  "audit_request": "...",
  "sampled_messages_used": 200,
  "inferred_terms": ["engineering", "student"],
  "pack": {
    "engineering-student-use": {}
  },
  "review_status": "draft_needs_human_or_model_review"
}
```

The manifest is for traceability. The validators read `domain_admin.json`.
