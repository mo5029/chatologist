<p align="center">
  <img src="assets/chatologist-logo-banner.svg" alt="Chatologist" width="720">
</p>

<p align="center">
  <strong>your AI chat history, turned into evidence</strong>
</p>

<p align="center">
  Export chats. Generate a custom codebook. Label usage, value, takeover, and human judgment.<br>
  Local-first. No scraping. No telemetry. No backend.
</p>

<p align="center">
  <a href="LICENSE">MIT License</a> ·
  <a href="SECURITY.md">Security policy</a> ·
  <a href="INSTALL.md">Codex + Claude Code</a>
</p>

<p align="center">
  <a href="#what-it-does">What it does</a> ·
  <a href="#install">Install</a> ·
  <a href="#get-your-chat-export">Export data</a> ·
  <a href="#run-an-audit">Run audit</a> ·
  <a href="#security--privacy">Security</a> ·
  <a href="#contributing">Contributing</a>
</p>

---

Chatologist is a local-first skill/toolkit for Codex, Claude Code, and plain Python. It turns exported ChatGPT, Claude, or generic LLM conversations into structured evidence about what AI is being used for, where value appears, what work is being delegated, and what human judgment still matters.

## What it does

Most people have thousands of AI conversations and almost no map of what those conversations mean. Chatologist audits the export itself.

| Step | Output |
|---|---|
| **Export** | Use a user-provided ChatGPT, Claude, JSON, JSONL, or ZIP export. |
| **Normalize** | Convert conversations into message-level CSV, JSONL, and SQLite. |
| **Build domain admin** | Generate a per-user codebook from the audit request and sampled messages. |
| **Batch** | Create sampled JSONL files for model/agent reviewers. |
| **Validate** | Check labels against the generated domain admin. |
| **Report** | Produce summary stats, coded messages, anonymized evidence, and privacy findings. |

![Chatologist workflow](assets/workflow-map.svg)

## Why use it

- **Usage:** what tasks, workflows, and recurring requests show up?
- **Value:** where does AI save time, teach, unblock, improve quality, or help decide?
- **Takeover:** where is AI doing bounded work a human used to do directly?
- **Human edge:** where do problem framing, context selection, judgment, taste, and verification still matter?
- **Risk:** where do correctness, privacy, security, academic integrity, or professional standards need review?

## What makes it different

Chatologist does **not** ship fixed industry domain packs. Every audit creates its own **domain admin**: an editable codebook generated from the user's audit request plus a controlled sample of their normalized messages.

That means a student, founder, analyst, teacher, researcher, or team each gets labels shaped around their real context instead of being forced into generic categories.

Generated admin files:

```text
audit_output/setup/domain_admin.json
audit_output/setup/domain_admin_manifest.json
audit_output/setup/domain_admin.md
```

Review `domain_admin.md` and edit `domain_admin.json` before serious labeling. The generated draft is transparent by design.

## Install

See [INSTALL.md](INSTALL.md) for the full install and testing guide.

### Codex

Use the repository root as a skill folder, or copy it into your Codex skills directory:

```bash
cp -R chatologist ~/.codex/skills/chatologist
```

Restart Codex and invoke it as:

```text
$chatologist
```

### Claude Code

This repo includes:

```text
.claude/skills/chatologist/SKILL.md
```

Keep `.claude/skills/chatologist` in the repo and run commands from the repository root.

### Plain Python

Chatologist is stdlib-only. Python 3.10+ is enough:

```bash
python3 -m unittest discover -s tests
```

## Get your chat export

Chatologist works from files you export yourself. It does not log into your account, scrape the sidebar, or read live chats.

### ChatGPT

Official guide: [Exporting your ChatGPT history and data](https://help.openai.com/en/articles/7260999-how-do-i-export-my-chatgpt-history-and-data).

1. Sign in to ChatGPT.
2. Open your profile menu.
3. Go to `Settings`.
4. Open `Data controls`.
5. Under `Export data`, select `Export`.
6. Confirm the export.
7. Wait for the email or SMS from OpenAI, then download the ZIP while signed in to the same account.

OpenAI says exports can take up to 7 days to arrive and the download link expires 24 hours after delivery. Chatologist can read the ZIP directly.

### Claude

Official guide: [Export your Claude data](https://support.claude.com/en/articles/9450526-export-your-claude-data).

1. Open Claude on the web app or Claude Desktop.
2. Click your initials in the lower-left corner.
3. Select `Settings`.
4. Go to `Privacy`.
5. Click `Export data`.
6. Wait for the email from Claude, then download the export while signed in.

Claude notes that individual exports are available for Free, Pro, and Max users with active accounts. Team or Enterprise exports are handled by the organization's Primary Owner. Claude export links expire 24 hours after delivery.

## Run an audit

Start with a small sample to control cost:

```bash
python3 scripts/run_pipeline.py \
  --input /path/to/openai-or-claude-export.zip \
  --output-dir audit_output \
  --audit-request "Figure out what my company is using AI for, what value we get, and what work AI is taking over" \
  --sample-percent 10
```

This creates:

```text
audit_output/setup/domain_admin.json
audit_output/setup/domain_admin.md
audit_output/setup/batches/*.jsonl
audit_output/setup/labeling_instructions.md
```

Before full labeling, open `audit_output/setup/domain_admin.md`. If the labels are too generic, edit `audit_output/setup/domain_admin.json` and rerun batching.

For higher-quality results, send the batch files and instructions to one or more model/agent reviewers. Save returned JSONL labels in:

```text
audit_output/labels/
```

Then validate and aggregate:

```bash
DOMAIN_ID=$(python3 - <<'PY'
import json
print(json.load(open("audit_output/setup/domain_selection.json"))["selected_domain_pack"])
PY
)

python3 scripts/validate_labels.py \
  --labels audit_output/labels \
  --domain "$DOMAIN_ID" \
  --domain-admin audit_output/setup/domain_admin.json \
  --output audit_output/report/label_validation.json

python3 scripts/aggregate_results.py \
  --labels audit_output/labels \
  --domain "$DOMAIN_ID" \
  --domain-admin audit_output/setup/domain_admin.json \
  --output-dir audit_output/report

python3 scripts/export_evidence_table.py \
  --labels audit_output/labels \
  --output-dir audit_output/evidence

python3 scripts/privacy_scan.py \
  --path audit_output/evidence \
  --output-dir audit_output/privacy
```

## 5 minute smoke test

```bash
python3 scripts/run_pipeline.py \
  --input examples/sample_openai_export/conversations.json \
  --output-dir tmp/sample_student \
  --audit-request "Audit student learning and technical problem-solving with AI" \
  --sample-percent 100 \
  --baseline-label
```

Expected outputs:

- `tmp/sample_student/setup/domain_admin.json`
- `tmp/sample_student/setup/domain_admin.md`
- `tmp/sample_student/setup/labeling_instructions.md`
- `tmp/sample_student/report/domain_report.md`
- `tmp/sample_student/evidence/evidence_table.md`

`--baseline-label` proves the pipeline runs. It is not research-grade labeling.

## Output layout

```text
audit_output/
├── normalized/
│   ├── messages.csv
│   ├── messages.jsonl
│   └── messages.sqlite3
├── setup/
│   ├── domain_admin.json
│   ├── domain_admin_manifest.json
│   ├── domain_admin.md
│   ├── domain_selection.json
│   ├── labeling_instructions.md
│   ├── batch_manifest.json
│   └── batches/
├── labels/
├── report/
├── evidence/
└── privacy/
```

## Security & privacy

Chatologist has no telemetry, no backend, and no account login flow. Runtime scripts read local files and write local outputs. Nothing is uploaded by Chatologist.

Chatologist's runtime requires no network access. The links to the official
ChatGPT and Claude export guides above are documentation for users to open
manually; the skill and its scripts never contact those endpoints. Optional
external model labeling is outside the local pipeline and must not receive
chat data without the user's explicit approval.

Important rules:

- Use only exports the user provides.
- Do not scrape live accounts.
- Do not commit private exports, `audit_output/`, `raw_exports/`, or `private_exports/`.
- Run `scripts/privacy_scan.py` before sharing evidence tables or reports.
- Do not quote raw private messages in public reports.

Read [SECURITY.md](SECURITY.md) for the full security and privacy model.

## References

- [Install guide](INSTALL.md)
- [Domain admin process](references/domain_admin_process.md)
- [Domain admin schema](references/domain_admin_schema.md)
- [Workflow](references/workflow.md)
- [Label schema](references/schema.md)
- [Multi-agent labeling](references/multi_agent_labeling.md)
- [Privacy rules](references/privacy.md)
- [Friend testing](FRIEND_TESTING.md)

## Contributing

Contributions are welcome, especially around import formats, label quality, documentation, and privacy hardening. Read [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) first.

## License

MIT. In plain English: people can use, copy, modify, share, and commercially use Chatologist as long as they keep the license notice. The software is provided as-is, without warranty. See [LICENSE](LICENSE) for the full legal text.
