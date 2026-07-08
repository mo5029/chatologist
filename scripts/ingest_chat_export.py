#!/usr/bin/env python3
"""Ingest a user-provided OpenAI/Anthropic/generic chat export."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_work_audit_lib import load_json_records, normalize_export, write_messages


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize a chat export into message-level CSV/JSONL/SQLite files.")
    parser.add_argument("--input", required=True, help="Path to export ZIP, JSON, JSONL, or extracted export directory.")
    parser.add_argument("--output-dir", required=True, help="Output directory for normalized files.")
    args = parser.parse_args()

    data = load_json_records(Path(args.input))
    messages = normalize_export(data)
    output_dir = Path(args.output_dir)
    write_messages(messages, output_dir)
    meta = {
        "input": str(Path(args.input)),
        "output_dir": str(output_dir),
        "normalized_messages": len(messages),
        "conversation_count": len({m.conversation_id for m in messages}),
        "source_formats": sorted({m.source_format for m in messages}),
    }
    (output_dir / "ingest_manifest.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
