# Security Policy

## Supported Versions

Only the latest `main` branch and latest published ZIP are supported with security fixes.

## Reporting a Vulnerability

If you find a security issue in Chatologist, please do **not** open a public issue with exploit details or private data.

Use GitHub private vulnerability reporting if available:

https://github.com/mo5029/chatologist/security/advisories/new

If that is unavailable, open a minimal public issue saying you need a private security contact, without including the vulnerability details.

## Privacy & Telemetry

**Chatologist has no telemetry.** No analytics, no crash reporting, no phone-home, no accounts, no API keys collected, and no Chatologist backend.

Chatologist is designed for local analysis of user-provided exports:

- It does not log into ChatGPT, Claude, or any other account.
- It does not scrape browser sidebars, account pages, or live chats.
- It reads only the export path you pass with `--input`.
- It writes outputs only to the output directory you choose.
- It is stdlib-only and does not require package installation.

## Runtime Network Model

After you have cloned or downloaded the repo, the analysis scripts are local-only. The scripts do not call HTTP APIs, upload files, or fetch remote resources.

Typical runtime command:

```bash
python3 scripts/run_pipeline.py \
  --input /path/to/export.zip \
  --output-dir audit_output \
  --audit-request "Audit how I use AI"
```

Data flow:

```text
user export on disk -> local Python scripts -> local output directory
```

Nothing is uploaded by Chatologist.

## Install-Time Network Model

Network activity can happen only when the user chooses a network-based install or export path:

- `git clone` or GitHub ZIP download fetches this repository.
- ChatGPT or Claude export downloads happen through the vendor's official export flow, outside Chatologist.
- Badge images in `README.md` load from shields.io when GitHub renders the page.

The runtime audit pipeline itself is local.

## What Stays On Your Machine

The following can contain private or sensitive content and should not be committed or shared without review:

- raw export ZIPs or extracted exports;
- `audit_output/`;
- `tmp/`;
- `raw_exports/`;
- `private_exports/`;
- normalized message CSV, JSONL, or SQLite files;
- label files;
- evidence tables and reports.

The default `.gitignore` excludes common private export and output paths, but you are still responsible for reviewing outputs before sharing them.

## Sensitive Content

AI chat exports can contain:

- personal health details;
- names, emails, and phone numbers;
- credentials or API keys;
- file paths;
- proprietary code;
- legal, financial, or employment information;
- third-party private information.

Run the privacy scanner before sharing outputs:

```bash
python3 scripts/privacy_scan.py \
  --path audit_output \
  --output-dir audit_output/privacy
```

The scanner is a convenience check, not a guarantee. Human review is still required before publishing evidence tables or reports.

## About Scanner Warnings

Static scanners may flag Chatologist because it:

- reads local files supplied by the user;
- writes CSV, JSONL, SQLite, and Markdown outputs;
- parses ZIP files;
- can process sensitive text if the user supplies sensitive exports.

These are expected capabilities for a local audit tool. They are not hidden network or telemetry behavior.
