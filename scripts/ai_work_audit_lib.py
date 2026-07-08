#!/usr/bin/env python3
"""Shared utilities for Chatologist.

The library is intentionally stdlib-only so the skill can run inside Codex,
Claude Code, CI, or a clean Python environment.
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
import re
import sqlite3
import statistics
import textwrap
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DOMAIN_ADMIN_TEMPLATE_JSON = ROOT / "references" / "domain_admin_template.json"


BASE_LABEL_FIELDS = [
    "message_uid",
    "domain_pack",
    "message_scope",
    "exclusion_label",
    "message_author",
    "message_function",
    "work_domain",
    "task_type",
    "ai_role",
    "artifact_type",
    "human_value_visible",
    "value_mechanism",
    "labor_relation",
    "verification_needed",
    "judgment_required",
    "risk_domain",
    "skill_level",
    "confidence",
    "review_flag",
    "paraphrased_evidence",
    "reviewer_notes",
]


@dataclass
class NormalizedMessage:
    message_uid: str
    conversation_id: str
    conversation_title: str
    source_format: str
    message_index: int
    author: str
    timestamp: str
    text: str

    def row(self) -> dict[str, Any]:
        return {
            "message_uid": self.message_uid,
            "conversation_id": self.conversation_id,
            "conversation_title": self.conversation_title,
            "source_format": self.source_format,
            "message_index": self.message_index,
            "author": self.author,
            "timestamp": self.timestamp,
            "text": self.text,
        }


def slug(value: str, fallback: str = "untitled") -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return value or fallback


def stable_id(*parts: str, length: int = 12) -> str:
    raw = "\n".join(parts).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()[:length]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json_records(path: Path) -> Any:
    """Load JSON, JSONL, ZIP containing JSON, or a directory export."""
    path = Path(path)
    if path.is_dir():
        preferred = [
            path / "conversations.json",
            path / "messages.json",
            path / "claude_conversations.json",
        ]
        for candidate in preferred:
            if candidate.exists():
                return load_json_records(candidate)
        json_files = sorted(path.glob("*.json"))
        if len(json_files) == 1:
            return load_json_records(json_files[0])
        if json_files:
            return [load_json_records(p) for p in json_files]
        raise FileNotFoundError(f"No JSON export found in directory: {path}")

    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            names = sorted(zf.namelist())
            preferred_names = [n for n in names if n.endswith("conversations.json")]
            json_names = preferred_names or [n for n in names if n.endswith(".json")]
            if not json_names:
                raise FileNotFoundError(f"No JSON files found inside ZIP: {path}")
            with zf.open(json_names[0]) as fh:
                return json.loads(fh.read().decode("utf-8"))

    if path.suffix.lower() == ".jsonl":
        records = []
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def text_from_content(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(text_from_content(item) for item in content if item is not None).strip()
    if isinstance(content, dict):
        if "parts" in content:
            return text_from_content(content.get("parts"))
        if "text" in content:
            return text_from_content(content.get("text"))
        if "content" in content:
            return text_from_content(content.get("content"))
        if "value" in content:
            return text_from_content(content.get("value"))
        if "type" in content and content.get("type") == "text":
            return text_from_content(content.get("text", ""))
        return "\n".join(text_from_content(v) for v in content.values()).strip()
    return str(content)


def normalize_author(role: Any) -> str:
    role_text = str(role or "unknown").strip().lower()
    mapping = {
        "human": "user",
        "user": "user",
        "assistant": "assistant",
        "ai": "assistant",
        "bot": "assistant",
        "system": "system",
        "tool": "tool",
    }
    return mapping.get(role_text, role_text or "unknown")


def normalize_openai_chatgpt(conversations: list[dict[str, Any]]) -> list[NormalizedMessage]:
    messages: list[NormalizedMessage] = []
    for conv_num, conv in enumerate(conversations, start=1):
        title = str(conv.get("title") or conv.get("name") or f"Conversation {conv_num}")
        conv_id = str(conv.get("id") or conv.get("conversation_id") or f"CHATGPT_{conv_num:05d}")
        mapping = conv.get("mapping") or {}
        nodes = []
        if isinstance(mapping, dict):
            for node in mapping.values():
                msg = node.get("message") if isinstance(node, dict) else None
                if msg:
                    nodes.append(msg)
        else:
            nodes = conv.get("messages") or []
        nodes.sort(key=lambda m: (m.get("create_time") is None, m.get("create_time") or 0))
        idx = 0
        for msg in nodes:
            author = normalize_author((msg.get("author") or {}).get("role") or msg.get("role"))
            text = text_from_content(msg.get("content")).strip()
            if not text:
                continue
            idx += 1
            uid = f"{slug(conv_id, 'chatgpt')}:{idx}"
            timestamp = str(msg.get("create_time") or msg.get("created_at") or "")
            messages.append(
                NormalizedMessage(uid, conv_id, title, "openai_chatgpt", idx, author, timestamp, text)
            )
    return messages


def normalize_message_array(
    records: list[dict[str, Any]],
    source_format: str,
    default_prefix: str,
) -> list[NormalizedMessage]:
    messages: list[NormalizedMessage] = []
    for conv_num, conv in enumerate(records, start=1):
        title = str(conv.get("title") or conv.get("name") or conv.get("summary") or f"Conversation {conv_num}")
        conv_id = str(conv.get("uuid") or conv.get("id") or conv.get("conversation_id") or f"{default_prefix}_{conv_num:05d}")
        raw_messages = conv.get("messages") or conv.get("chat_messages") or conv.get("turns") or []
        idx = 0
        for msg in raw_messages:
            author = normalize_author(msg.get("role") or msg.get("sender") or msg.get("author"))
            text = text_from_content(msg.get("text") or msg.get("content") or msg.get("message")).strip()
            if not text:
                continue
            idx += 1
            uid = f"{slug(conv_id, default_prefix.lower())}:{idx}"
            timestamp = str(msg.get("created_at") or msg.get("timestamp") or msg.get("create_time") or "")
            messages.append(NormalizedMessage(uid, conv_id, title, source_format, idx, author, timestamp, text))
    return messages


def normalize_flat_messages(records: list[dict[str, Any]]) -> list[NormalizedMessage]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        conv_id = str(row.get("conversation_id") or row.get("chat_id") or row.get("thread_id") or "conversation")
        grouped[conv_id].append(row)
    messages: list[NormalizedMessage] = []
    for conv_num, (conv_id, rows) in enumerate(grouped.items(), start=1):
        rows.sort(key=lambda r: str(r.get("timestamp") or r.get("created_at") or ""))
        title = str(rows[0].get("conversation_title") or rows[0].get("title") or f"Conversation {conv_num}")
        for idx, row in enumerate(rows, start=1):
            text = text_from_content(row.get("text") or row.get("content") or row.get("message")).strip()
            if not text:
                continue
            author = normalize_author(row.get("author") or row.get("role") or row.get("sender"))
            timestamp = str(row.get("timestamp") or row.get("created_at") or "")
            uid = str(row.get("message_uid") or f"{slug(conv_id, 'flat')}:{idx}")
            messages.append(NormalizedMessage(uid, conv_id, title, "generic_flat", idx, author, timestamp, text))
    return messages


def normalize_export(data: Any) -> list[NormalizedMessage]:
    if isinstance(data, dict):
        if "mapping" in data:
            return normalize_openai_chatgpt([data])
        for key in ("conversations", "chats", "data"):
            if isinstance(data.get(key), list):
                return normalize_export(data[key])
        if "messages" in data or "chat_messages" in data:
            return normalize_message_array([data], "generic_conversation", "GENERIC")
        raise ValueError("Unrecognized JSON object export. Expected conversations, chats, mapping, or messages.")

    if isinstance(data, list):
        if not data:
            return []
        if all(isinstance(item, dict) and "mapping" in item for item in data):
            return normalize_openai_chatgpt(data)
        if any(isinstance(item, dict) and ("messages" in item or "chat_messages" in item or "turns" in item) for item in data):
            source = "claude_or_generic_messages"
            return normalize_message_array(data, source, "CHAT")
        if all(isinstance(item, dict) and ("text" in item or "content" in item or "message" in item) for item in data):
            return normalize_flat_messages(data)
    raise ValueError("Unsupported export structure.")


def write_messages(messages: list[NormalizedMessage], output_dir: Path) -> None:
    ensure_dir(output_dir)
    fields = ["message_uid", "conversation_id", "conversation_title", "source_format", "message_index", "author", "timestamp", "text"]
    with (output_dir / "messages.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for msg in messages:
            writer.writerow(msg.row())
    with (output_dir / "messages.jsonl").open("w", encoding="utf-8") as fh:
        for msg in messages:
            fh.write(json.dumps(msg.row(), ensure_ascii=False) + "\n")
    conn = sqlite3.connect(output_dir / "messages.sqlite3")
    conn.execute("drop table if exists messages")
    conn.execute(
        "create table messages (message_uid text primary key, conversation_id text, conversation_title text, source_format text, message_index integer, author text, timestamp text, text text)"
    )
    conn.executemany(
        "insert into messages values (:message_uid,:conversation_id,:conversation_title,:source_format,:message_index,:author,:timestamp,:text)",
        [msg.row() for msg in messages],
    )
    conn.commit()
    conn.close()


def read_messages_csv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def load_domain_packs(path: Path | None = None) -> dict[str, Any]:
    """Load a generated domain admin JSON file.

    The public workflow builds a per-user domain admin in `setup/domain_admin.json`.
    A small template remains in `references/domain_admin_template.json` only as a
    schema/default fallback; it is not a built-in domain library.
    """
    path = Path(path) if path else DOMAIN_ADMIN_TEMPLATE_JSON
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


DOMAIN_STOPWORDS = {
    "about", "above", "after", "again", "against", "also", "and", "are", "audit", "because",
    "before", "being", "between", "build", "can", "chat", "chats", "check", "company", "could",
    "derive", "derived", "does", "doing", "domain", "each", "export", "family", "figure", "for",
    "from", "had", "has", "have", "history", "how", "into", "make", "message", "messages", "model",
    "more", "not", "off", "our", "out", "over", "really", "report", "request", "should", "than",
    "that", "the", "their", "them", "there", "these", "things", "this", "through", "use", "used",
    "using", "value", "was", "what", "when", "where", "which", "while", "who", "why", "with", "work",
    "would", "you", "your", "youre", "user", "users", "usage",
}


def clean_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def extract_terms(texts: Iterable[str], limit: int = 18) -> list[str]:
    counter: Counter[str] = Counter()
    for text in texts:
        for token in re.findall(r"[A-Za-z][A-Za-z0-9_+-]{2,}", text.lower()):
            token = clean_token(token)
            if len(token) < 3 or token in DOMAIN_STOPWORDS:
                continue
            if token.isdigit():
                continue
            counter[token] += 1
    return [term for term, _ in counter.most_common(limit)]


def label_from_text(value: str, suffix: str = "") -> str:
    words = [clean_token(w) for w in re.findall(r"[A-Za-z][A-Za-z0-9_+-]{2,}", value)]
    words = [w for w in words if w and w not in DOMAIN_STOPWORDS]
    label = "_".join(words[:4]).upper()
    if suffix and label and not label.endswith(suffix):
        label = f"{label}_{suffix}"
    return label or f"CUSTOM_{suffix or 'LABEL'}"


def unique_values(values: Iterable[str], fallback: list[str]) -> list[str]:
    out: list[str] = []
    for value in values:
        clean = str(value).strip().upper().replace("-", "_").replace(" ", "_")
        clean = re.sub(r"[^A-Z0-9_]+", "", clean)
        if clean and clean not in out:
            out.append(clean)
    for value in fallback:
        if value not in out:
            out.append(value)
    return out


def build_generated_domain_admin(
    user_request: str,
    sampled_rows: list[dict[str, str]],
    domain_id: str | None = None,
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """Create a per-user domain admin from the user's request and sample rows.

    This is a deterministic draft. Research-grade use should have a model or
    human reviewer inspect and refine `domain_admin.json` before full labeling.
    """
    request_terms = extract_terms([user_request], limit=8)
    if request_terms:
        relevant_conversations = set()
        for row in sampled_rows:
            haystack = f"{row.get('conversation_title', '')} {row.get('text', '')}".lower()
            if any(term in haystack for term in request_terms):
                relevant_conversations.add(row.get("conversation_id", ""))
        relevant_rows = [row for row in sampled_rows if row.get("conversation_id", "") in relevant_conversations] or sampled_rows
    else:
        relevant_rows = sampled_rows
    title_texts = [row.get("conversation_title", "") for row in relevant_rows]
    message_texts = [row.get("text", "") for row in relevant_rows]
    sample_terms = extract_terms([*title_texts, *message_texts], limit=18)
    terms = list(dict.fromkeys([*request_terms, *sample_terms]))[:18]
    domain_id = slug(domain_id or " ".join(extract_terms([user_request], limit=5)) or "user-domain", "user-domain")
    work_seed_terms = request_terms[:6] or sample_terms[:6]
    topic_labels = [label_from_text(term, "WORK") for term in work_seed_terms]
    request_label = label_from_text(user_request, "FOCUS")

    pack = {
        "description": (
            f"Generated domain admin for this audit request: {user_request.strip() or 'user-provided AI chat export'}"
        ),
        "selection_keywords": terms[:16] or ["custom", "audit", "chat"],
        "exclusion_labels": [
            "PERSONAL_ADMIN",
            "HEALTH_MEDICAL",
            "LEGAL_OR_FINANCIAL_SENSITIVE",
            "CREATIVE_LEISURE",
            "TRAVEL_LOGISTICS",
            "ACCOUNT_META",
            "OTHER_OUT_OF_SCOPE",
            "INSUFFICIENT_CONTEXT",
        ],
        "work_domains": unique_values(
            [request_label, *topic_labels],
            ["PRIMARY_WORK", "ADJACENT_WORK", "LEARNING_OR_EXPLANATION", "PLANNING_OR_OPERATIONS", "OTHER_IN_SCOPE"],
        ),
        "task_types": [
            "ASK_EXPLAIN",
            "LEARN_OR_STUDY",
            "DRAFT_OR_WRITE",
            "DEBUG_OR_FIX",
            "ANALYZE_OR_COMPARE",
            "PLAN_OR_DECIDE",
            "SUMMARIZE_OR_SYNTHESIZE",
            "GENERATE_ARTIFACT",
            "REVIEW_OR_VERIFY",
            "SEARCH_OR_RESEARCH",
            "AUTOMATE_OR_EXECUTE",
            "OTHER_IN_SCOPE",
        ],
        "ai_roles": [
            "TUTOR",
            "ASSISTANT",
            "ANALYST",
            "DRAFTER",
            "REVIEWER",
            "DEBUGGER",
            "PLANNER",
            "SEARCH_SYNTHESIZER",
            "AGENT_EXECUTOR",
            "CRITIC",
        ],
        "artifact_types": [
            "NONE",
            "EXPLANATION",
            "TEXT_DRAFT",
            "CODE_OR_SCRIPT",
            "DATA_TABLE",
            "PLAN_OR_CHECKLIST",
            "DECISION_NOTE",
            "REVIEW_NOTES",
            "MIXED",
        ],
        "human_value_sources": [
            "PROBLEM_FRAMING",
            "CONTEXT_SELECTION",
            "DOMAIN_JUDGMENT",
            "VERIFICATION",
            "TASTE_OR_PREFERENCE",
            "STAKEHOLDER_CONTEXT",
            "RISK_OWNERSHIP",
            "LEARNING_CAPITAL",
        ],
        "value_mechanisms": [
            "TIME_SAVING",
            "QUALITY_IMPROVEMENT",
            "UNBLOCKING",
            "LEARNING_UPSKILLING",
            "OPTION_GENERATION",
            "RISK_REDUCTION",
            "AUTOMATION",
            "COORDINATION",
        ],
        "verification_types": [
            "SOURCE_CHECK",
            "RUN_OR_TEST_OUTPUT",
            "NUMERICAL_RECALCULATION",
            "DOMAIN_EXPERT_REVIEW",
            "SECURITY_PRIVACY_REVIEW",
            "STAKEHOLDER_REVIEW",
            "NONE_LOW",
            "UNKNOWN",
        ],
        "risk_domains": [
            "CORRECTNESS",
            "PRIVACY",
            "SECURITY",
            "LEGAL_FINANCIAL",
            "MEDICAL_SAFETY",
            "ACADEMIC_INTEGRITY",
            "REPUTATION",
            "NONE",
        ],
        "skill_levels": [
            "NOVICE",
            "LEARNER_OR_STUDENT",
            "JUNIOR",
            "MIDLEVEL",
            "SENIOR_OR_EXPERT",
            "MANAGER_OR_OWNER",
            "NONE_UNCLEAR",
        ],
    }
    admin = {
        "domain_id": domain_id,
        "generated": True,
        "audit_request": user_request,
        "sampled_messages_used": len(sampled_rows),
        "inferred_terms": terms,
        "pack": {domain_id: pack},
        "review_status": "draft_needs_human_or_model_review",
        "process_note": (
            "This generated domain admin is a draft codebook. Before full labeling, inspect the terms, "
            "tighten inclusion/exclusion boundaries, add or remove labels, then run validation."
        ),
    }
    return domain_id, {domain_id: pack}, admin


def domain_admin_markdown(admin: dict[str, Any]) -> str:
    domain_id = admin["domain_id"]
    pack = admin["pack"][domain_id]
    terms = ", ".join(admin.get("inferred_terms") or ["none"])

    def bullet(values: list[str]) -> str:
        return "\n".join(f"- `{value}`" for value in values)

    return f"""# Domain Admin: `{domain_id}`

This file is the audit-specific domain admin for this user and this dataset. It replaces bundled domain packs.

## Audit Request

> {admin.get("audit_request", "").strip() or "No audit request provided."}

## How This Draft Was Built

1. Normalize the exported chat data into message-level rows.
2. Sample messages using the requested cost controls.
3. Extract repeated terms from the audit request, conversation titles, and sampled message text.
4. Generate a first-pass domain ID, inclusion keywords, task labels, value labels, risk labels, and verification labels.
5. Save the editable codebook in `domain_admin.json`.
6. Ask a human or model reviewer to refine this file before full labeling.

Sampled messages used for this draft: **{admin.get("sampled_messages_used", 0)}**

Inferred terms: {terms}

## Required Review Before Full Labeling

Check these items before sending batches to reviewers:

- The domain ID clearly names the user's actual audit lens.
- `selection_keywords` capture the user's context without being too broad.
- `work_domains` describe the user's world, not a generic industry list.
- `task_types` distinguish the behaviors you actually want to measure.
- `exclusion_labels` remove medical, personal, legal, account, or unrelated content when needed.
- `human_value_sources` reflect the scarce human inputs you care about.
- `verification_types` describe how outputs should be checked in this domain.
- Sensitive categories are marked so evidence can be paraphrased safely.

## Generated Description

{pack.get("description", "")}

## Selection Keywords

{bullet(pack.get("selection_keywords", []))}

## Work Domains

{bullet(pack.get("work_domains", []))}

## Task Types

{bullet(pack.get("task_types", []))}

## AI Roles

{bullet(pack.get("ai_roles", []))}

## Human Value Sources

{bullet(pack.get("human_value_sources", []))}

## Value Mechanisms

{bullet(pack.get("value_mechanisms", []))}

## Verification Types

{bullet(pack.get("verification_types", []))}

## Risk Domains

{bullet(pack.get("risk_domains", []))}

## Edit Rule

If this domain admin feels generic, edit it before labeling. The goal is not to fit the user into Chatologist's categories. The goal is to make categories that fit the user's real AI usage.
"""


def sample_messages(
    rows: list[dict[str, str]],
    sample_percent: float = 100.0,
    max_messages: int | None = None,
    seed: int = 7,
) -> list[dict[str, str]]:
    if sample_percent <= 0:
        raise ValueError("sample_percent must be > 0")
    if sample_percent > 100:
        raise ValueError("sample_percent must be <= 100")
    target = max(1, round(len(rows) * sample_percent / 100.0)) if rows else 0
    if max_messages is not None:
        target = min(target, max_messages)
    if target >= len(rows):
        return list(rows)

    rng = random.Random(seed)
    by_conversation: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_conversation[row["conversation_id"]].append(row)
    selected: list[dict[str, str]] = []
    conv_ids = list(by_conversation)
    rng.shuffle(conv_ids)
    while len(selected) < target and conv_ids:
        for conv_id in list(conv_ids):
            bucket = by_conversation[conv_id]
            if not bucket:
                conv_ids.remove(conv_id)
                continue
            selected.append(bucket.pop(0))
            if len(selected) >= target:
                break
    return selected


def write_batches(
    rows: list[dict[str, str]],
    output_dir: Path,
    batch_size: int,
    domain_pack: str,
    user_request: str,
) -> list[Path]:
    ensure_dir(output_dir)
    paths: list[Path] = []
    for idx in range(0, len(rows), batch_size):
        batch_num = idx // batch_size + 1
        path = output_dir / f"batch_{batch_num:05d}.jsonl"
        with path.open("w", encoding="utf-8") as fh:
            for row in rows[idx : idx + batch_size]:
                item = dict(row)
                item["domain_pack"] = domain_pack
                item["user_research_request"] = user_request
                fh.write(json.dumps(item, ensure_ascii=False) + "\n")
        paths.append(path)
    return paths


def label_allowed_values(domain_pack: dict[str, Any]) -> dict[str, list[str]]:
    values = {
        "message_scope": ["IN_SCOPE", "DOMAIN_ADJACENT", "OUT_OF_SCOPE", "UNREADABLE_OR_EMPTY", "DUPLICATE"],
        "exclusion_label": ["NA_IN_SCOPE"] + domain_pack.get("exclusion_labels", []),
        "message_author": ["user", "assistant", "system", "tool", "unknown"],
        "message_function": ["REQUEST", "CONTEXT", "CORRECTION", "QUESTION", "ANSWER", "ARTIFACT", "EVALUATION", "TOOL_RESULT", "OTHER"],
        "work_domain": domain_pack.get("work_domains", []) + ["NA_OUT_OF_SCOPE", "OTHER"],
        "task_type": domain_pack.get("task_types", []) + ["NA_OUT_OF_SCOPE", "OTHER"],
        "ai_role": domain_pack.get("ai_roles", []) + ["NA_OUT_OF_SCOPE", "OTHER"],
        "artifact_type": domain_pack.get("artifact_types", []) + ["NA_OUT_OF_SCOPE", "OTHER"],
        "human_value_visible": domain_pack.get("human_value_sources", []) + ["NONE_VISIBLE", "NA_OUT_OF_SCOPE", "OTHER"],
        "value_mechanism": domain_pack.get("value_mechanisms", []) + ["NO_CLEAR_VALUE", "NA_OUT_OF_SCOPE", "OTHER"],
        "labor_relation": ["LEARNING_AUGMENTATION", "COMPLEMENT", "PARTIAL_SUBSTITUTION", "SUBSTITUTION_LIKE", "SUPERVISION_HEAVY", "OUT_OF_SCOPE", "UNCLEAR"],
        "verification_needed": domain_pack.get("verification_types", []) + ["NONE_LOW", "UNKNOWN", "NA_OUT_OF_SCOPE", "OTHER"],
        "judgment_required": ["LOW", "MEDIUM", "HIGH", "CRITICAL", "NA_OUT_OF_SCOPE"],
        "risk_domain": domain_pack.get("risk_domains", []) + ["NONE", "OTHER"],
        "skill_level": domain_pack.get("skill_levels", []) + ["NONE_UNCLEAR", "OUT_OF_SCOPE", "OTHER"],
        "confidence": ["HIGH", "MEDIUM", "LOW"],
        "review_flag": ["YES", "NO"],
    }
    return {k: list(dict.fromkeys(v)) for k, v in values.items()}


def generate_label_instructions(domain_name: str, domain_pack: dict[str, Any], user_request: str) -> str:
    allowed = label_allowed_values(domain_pack)
    lines = [
        f"# Message Labeling Instructions: {domain_name}",
        "",
        "Label each JSONL row independently. Use nearby title/context fields, but assign labels to the target message only.",
        "The user's audit request is:",
        "",
        f"> {user_request.strip()}",
        "",
        "Return one JSON object per input message. Do not include markdown fences.",
        "Use exactly these output fields:",
        "",
        ", ".join(BASE_LABEL_FIELDS),
        "",
        "Allowed values:",
    ]
    for field, vals in allowed.items():
        lines.append(f"- `{field}`: {', '.join(vals)}")
    lines.extend(
        [
            "",
            "Rules:",
            "- If the message is outside the selected domain, set `message_scope` to `OUT_OF_SCOPE`, set `labor_relation` to `OUT_OF_SCOPE`, and use `NA_OUT_OF_SCOPE` where available.",
            "- Do not quote private raw text in `paraphrased_evidence`; summarize safely.",
            "- Use `review_flag=YES` for low confidence, sensitive content, or ambiguous labor relation.",
            "- Treat labor relation as task-level, not occupation-level.",
            "- Prefer conservative labels when evidence is weak.",
        ]
    )
    return "\n".join(lines) + "\n"


generate_label_prompt = generate_label_instructions


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
    return rows


def iter_jsonl_files(path: Path) -> Iterable[Path]:
    path = Path(path)
    if path.is_file():
        yield path
    else:
        for file in sorted(path.glob("*.jsonl")):
            yield file


def validate_label_rows(label_rows: list[dict[str, Any]], domain_pack: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    allowed = label_allowed_values(domain_pack)
    for i, row in enumerate(label_rows, start=1):
        for field in BASE_LABEL_FIELDS:
            if field not in row:
                errors.append(f"row {i}: missing field {field}")
        for field, vals in allowed.items():
            if field in row and str(row[field]) not in vals:
                errors.append(f"row {i} {row.get('message_uid','?')}: invalid {field}={row[field]!r}")
    return errors


def write_csv(rows: list[dict[str, Any]], path: Path, fields: list[str] | None = None) -> None:
    ensure_dir(path.parent)
    fields = fields or sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def counter_rows(counter: Counter[str], denominator: int | None = None) -> list[dict[str, Any]]:
    total = denominator if denominator is not None else sum(counter.values())
    return [
        {"label": label, "n": n, "pct": round(100 * n / total, 1) if total else 0.0}
        for label, n in counter.most_common()
    ]


def aggregate_labels(label_rows: list[dict[str, Any]], output_dir: Path, domain_name: str) -> dict[str, Any]:
    ensure_dir(output_dir)
    write_csv(label_rows, output_dir / "coded_messages.csv", BASE_LABEL_FIELDS)
    summary = {
        "domain_pack": domain_name,
        "labeled_messages": len(label_rows),
        "scope_distribution": counter_rows(Counter(str(r.get("message_scope", "")) for r in label_rows)),
        "task_distribution": counter_rows(Counter(str(r.get("task_type", "")) for r in label_rows if r.get("message_scope") in {"IN_SCOPE", "DOMAIN_ADJACENT"})),
        "ai_role_distribution": counter_rows(Counter(str(r.get("ai_role", "")) for r in label_rows if r.get("message_scope") in {"IN_SCOPE", "DOMAIN_ADJACENT"})),
        "labor_relation_distribution": counter_rows(Counter(str(r.get("labor_relation", "")) for r in label_rows if r.get("message_scope") in {"IN_SCOPE", "DOMAIN_ADJACENT"})),
        "verification_distribution": counter_rows(Counter(str(r.get("verification_needed", "")) for r in label_rows if r.get("message_scope") in {"IN_SCOPE", "DOMAIN_ADJACENT"})),
        "human_value_distribution": counter_rows(Counter(str(r.get("human_value_visible", "")) for r in label_rows if r.get("message_scope") in {"IN_SCOPE", "DOMAIN_ADJACENT"})),
        "risk_distribution": counter_rows(Counter(str(r.get("risk_domain", "")) for r in label_rows if r.get("message_scope") in {"IN_SCOPE", "DOMAIN_ADJACENT"})),
    }
    for key, rows in summary.items():
        if key.endswith("_distribution") and isinstance(rows, list):
            write_csv(rows, output_dir / f"{key}.csv", ["label", "n", "pct"])
    with (output_dir / "summary_stats.json").open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
    write_report(summary, output_dir / "domain_report.md")
    return summary


def table_md(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._\n"
    out = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(row.get(c, "")).replace("|", "\\|") for c in columns) + " |")
    return "\n".join(out) + "\n"


def write_report(summary: dict[str, Any], path: Path) -> None:
    in_scope = 0
    for row in summary.get("scope_distribution", []):
        if row["label"] in {"IN_SCOPE", "DOMAIN_ADJACENT"}:
            in_scope += row["n"]
    lines = [
        f"# Chatologist Report: {summary.get('domain_pack')}",
        "",
        f"Labeled messages: **{summary.get('labeled_messages', 0)}**",
        f"In-scope or domain-adjacent messages: **{in_scope}**",
        "",
        "## Scope Distribution",
        "",
        table_md(summary.get("scope_distribution", []), ["label", "n", "pct"]),
        "## Task Distribution",
        "",
        table_md(summary.get("task_distribution", []), ["label", "n", "pct"]),
        "## AI Role Distribution",
        "",
        table_md(summary.get("ai_role_distribution", []), ["label", "n", "pct"]),
        "## Labor Relation",
        "",
        table_md(summary.get("labor_relation_distribution", []), ["label", "n", "pct"]),
        "## Human Value Visible",
        "",
        table_md(summary.get("human_value_distribution", []), ["label", "n", "pct"]),
        "## Verification Burden",
        "",
        table_md(summary.get("verification_distribution", []), ["label", "n", "pct"]),
        "## Risk Domains",
        "",
        table_md(summary.get("risk_distribution", []), ["label", "n", "pct"]),
        "## Interpretation Limits",
        "",
        "- This report is descriptive unless the user adds an explicit causal design.",
        "- Sampling percentage and labeling quality determine how much confidence to place in the counts.",
        "- Private raw message text should not be quoted externally without separate review.",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


SENSITIVE_PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "url": re.compile(r"https?://[^\s)>\"]+"),
    "phone_like": re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)"),
    "private_path": re.compile(r"(/Users/|C:\\\\Users\\\\|/home/)[^\s]+"),
    "api_key_like": re.compile(r"\b(?:sk|api|key|token|secret)[-_]?[A-Za-z0-9]{16,}\b", re.IGNORECASE),
}


def privacy_scan_text(text: str) -> dict[str, int]:
    return {name: len(pattern.findall(text)) for name, pattern in SENSITIVE_PATTERNS.items()}


def privacy_scan_path(path: Path, extensions: tuple[str, ...] = (".md", ".csv", ".json", ".jsonl", ".txt")) -> list[dict[str, Any]]:
    findings = []
    paths = [path] if path.is_file() else [p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in extensions]
    for file in paths:
        text = file.read_text(encoding="utf-8", errors="ignore")
        counts = privacy_scan_text(text)
        if any(counts.values()):
            row = {"path": str(file)}
            row.update(counts)
            findings.append(row)
    return findings


def baseline_label(row: dict[str, str], domain_name: str, domain_pack: dict[str, Any]) -> dict[str, Any]:
    """A cheap smoke-test labeler. Not a replacement for model/agent labeling."""
    text = row.get("text", "").lower()
    title = row.get("conversation_title", "").lower()
    haystack = f"{title} {text}"
    selection_keywords = [k.lower() for k in domain_pack.get("selection_keywords", [])]
    in_scope = any(k in haystack for k in selection_keywords)
    excluded = "NA_IN_SCOPE" if in_scope else (domain_pack.get("exclusion_labels") or ["OTHER_OUT_OF_SCOPE"])[0]
    task = "OTHER"
    for candidate in domain_pack.get("task_types", []):
        tokens = candidate.lower().replace("_", " ").split()
        if any(tok in haystack for tok in tokens):
            task = candidate
            break
    if task == "OTHER":
        if any(w in haystack for w in ["explain", "learn", "why", "how"]):
            task = "ASK_EXPLAIN" if "ASK_EXPLAIN" in domain_pack.get("task_types", []) else domain_pack.get("task_types", ["OTHER"])[0]
        elif any(w in haystack for w in ["debug", "error", "fix"]):
            task = "DEBUG_OR_FIX" if "DEBUG_OR_FIX" in domain_pack.get("task_types", []) else domain_pack.get("task_types", ["OTHER"])[0]
        elif any(w in haystack for w in ["write", "draft", "summarize"]):
            task = "DRAFT_OR_WRITE" if "DRAFT_OR_WRITE" in domain_pack.get("task_types", []) else domain_pack.get("task_types", ["OTHER"])[0]
    role = "TUTOR" if any(w in haystack for w in ["explain", "learn", "how"]) else (domain_pack.get("ai_roles", ["OTHER"])[0])
    if row.get("author") == "user":
        function = "REQUEST"
    elif row.get("author") == "assistant":
        function = "ANSWER"
    else:
        function = "OTHER"
    return {
        "message_uid": row["message_uid"],
        "domain_pack": domain_name,
        "message_scope": "IN_SCOPE" if in_scope else "OUT_OF_SCOPE",
        "exclusion_label": excluded,
        "message_author": row.get("author", "unknown"),
        "message_function": function,
        "work_domain": (domain_pack.get("work_domains") or ["OTHER"])[0] if in_scope else "NA_OUT_OF_SCOPE",
        "task_type": task if in_scope else "NA_OUT_OF_SCOPE",
        "ai_role": role if in_scope else "NA_OUT_OF_SCOPE",
        "artifact_type": (domain_pack.get("artifact_types") or ["OTHER"])[0] if in_scope else "NA_OUT_OF_SCOPE",
        "human_value_visible": (domain_pack.get("human_value_sources") or ["NONE_VISIBLE"])[0] if in_scope else "NA_OUT_OF_SCOPE",
        "value_mechanism": (domain_pack.get("value_mechanisms") or ["NO_CLEAR_VALUE"])[0] if in_scope else "NA_OUT_OF_SCOPE",
        "labor_relation": "LEARNING_AUGMENTATION" if in_scope and role == "TUTOR" else ("COMPLEMENT" if in_scope else "OUT_OF_SCOPE"),
        "verification_needed": "UNKNOWN" if in_scope else "NA_OUT_OF_SCOPE",
        "judgment_required": "MEDIUM" if in_scope else "NA_OUT_OF_SCOPE",
        "risk_domain": "NONE",
        "skill_level": (domain_pack.get("skill_levels") or ["NONE_UNCLEAR"])[0] if in_scope else "OUT_OF_SCOPE",
        "confidence": "LOW",
        "review_flag": "YES",
        "paraphrased_evidence": "Baseline auto-label for smoke testing only.",
        "reviewer_notes": "Generated by baseline_label.py; replace with model/agent labels for real analysis.",
    }


def write_markdown_evidence(rows: list[dict[str, Any]], path: Path) -> None:
    columns = [
        "message_uid",
        "message_scope",
        "task_type",
        "ai_role",
        "labor_relation",
        "human_value_visible",
        "verification_needed",
        "paraphrased_evidence",
    ]
    path.write_text("# Anonymized Evidence Table\n\n" + table_md(rows, columns), encoding="utf-8")


def sample_evidence_rows(label_rows: list[dict[str, Any]], n: int = 30, seed: int = 7) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in label_rows:
        grouped[str(row.get("task_type") or row.get("message_scope") or "OTHER")].append(row)
    sample: list[dict[str, Any]] = []
    keys = list(grouped)
    rng.shuffle(keys)
    while len(sample) < n and keys:
        for key in list(keys):
            bucket = grouped[key]
            if not bucket:
                keys.remove(key)
                continue
            sample.append(bucket.pop(0))
            if len(sample) >= n:
                break
    return sample
