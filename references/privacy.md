# Privacy And Data Handling

## Data Input

Only use files the user exported and provided:

- OpenAI/ChatGPT export ZIP or `conversations.json`
- Anthropic/Claude export JSON
- Generic JSON/JSONL/CSV-derived JSON supplied by the user

Do not scrape live accounts, sidebars, websites, or browser sessions.

## Output Safety

Public or shareable outputs should use:

- counts;
- labels;
- paraphrased examples;
- de-identified evidence;
- privacy scan reports.

Avoid publishing raw messages.

## Sensitive Data

Run:

```bash
python scripts/privacy_scan.py --path audit_output --output-dir audit_output/privacy
```

The scanner catches obvious:

- emails;
- URLs;
- phone-like strings;
- local private file paths;
- key-like tokens.

It is not a complete privacy guarantee. A human must still review examples before sharing.

## High-Risk Domains

Use more conservative settings for:

- finance;
- education involving minors;
- health or medical chats;
- legal or compliance chats;
- security;
- proprietary code or company data.

## Evidence Table Rule

Evidence rows should say things like:

> User asks for a spreadsheet forecast check and source verification.

Not:

> Raw quote with customer names, numbers, or internal filenames.

## Retention

If the user wants a shareable repo or paper:

- keep raw exports out of git;
- commit only templates, scripts, and fully de-identified examples;
- add raw export patterns to `.gitignore`;
- keep generated audit outputs out of git unless reviewed.
