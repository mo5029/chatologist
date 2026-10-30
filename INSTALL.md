# Install Chatologist

Chatologist can be used three ways:

- as a Codex skill;
- as a Claude Code project skill;
- as plain Python scripts.

It is stdlib-only and requires Python 3.10+.

## Codex Skill

Copy the repository into your Codex skills directory:

```bash
cp -R chatologist ~/.codex/skills/chatologist
```

Restart Codex and invoke:

```text
$chatologist
```

## Claude Code Project Skill

Keep this directory in the repository:

```text
.claude/skills/chatologist/SKILL.md
```

Then run Claude Code from the repository root. The skill can call the local scripts and references.

## Plain Python

Run the smoke test:

```bash
python3 scripts/run_pipeline.py \
  --input examples/sample_openai_export/conversations.json \
  --output-dir tmp/sample_student \
  --audit-request "Audit student learning and technical problem-solving with AI" \
  --sample-percent 100 \
  --baseline-label
```

Run tests:

```bash
python3 -m unittest discover -s tests
```

## Real Export

Pass a downloaded ChatGPT or Claude export ZIP directly:

```bash
python3 scripts/run_pipeline.py \
  --input /path/to/export.zip \
  --output-dir audit_output \
  --audit-request "Audit how I use AI for my work or studies" \
  --sample-percent 10
```

You can also pass:

- an extracted export directory;
- `conversations.json`;
- a generic JSON/JSONL file with messages.

## No Install-Time Package Dependencies

Chatologist does not require `pip install`.

The scripts use Python stdlib modules only:

- `csv`
- `json`
- `sqlite3`
- `zipfile`
- `argparse`
- `pathlib`

## Uninstall

Use your skill manager or file manager to remove only the copied
`chatologist` skill folder. Before deleting anything, verify that the selected
folder is the Chatologist copy and not the parent skills directory.

Audit outputs are ordinary local folders. If you no longer need them, review
their contents and remove only the specific output folders you created, such
as `audit_output` or `tmp/sample_student`, using your file manager. Chatologist
never deletes files or directories automatically.

Chatologist does not create accounts, servers, background services, or global config outside whichever skill copy you make.
