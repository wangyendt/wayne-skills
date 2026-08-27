"""Opt-in transcript adapters. Never discover or scan unrelated conversations."""
import hashlib
import json
from pathlib import Path

from ledger import LedgerError, now

MAX_LINE = 2 * 1024 * 1024


def visible(content):
    if isinstance(content, str):
        return content, []
    if not isinstance(content, list):
        raise LedgerError("Unsupported visible-message content shape")
    texts, attachments = [], []
    for block in content:
        if not isinstance(block, dict):
            raise LedgerError("Unsupported message block")
        kind = block.get("type")
        if not isinstance(kind, str):
            raise LedgerError("Message block type is not a string")
        if kind in {"text", "input_text", "output_text"}:
            if not isinstance(block.get("text"), str):
                raise LedgerError("Text block has no text")
            texts.append(block["text"])
        elif kind in {"image", "image_url", "input_image", "file", "document", "audio", "input_audio"}:
            # Keep a content digest/descriptor, never embed raw binary/base64 or credentials in URLs.
            raw = json.dumps(block, sort_keys=True, ensure_ascii=False).encode()
            attachments.append({"type": kind, "sha256": hashlib.sha256(raw).hexdigest(), "availability": "reference-only; original stays with host"})
        elif kind in {"thinking", "redacted_thinking", "reasoning", "tool_use", "tool_result", "toolCall", "toolResult"}:
            continue
        else:
            raise LedgerError("Unknown content block type; capture needs an adapter update")
    return "\n".join(texts), attachments


def parse_record(host, record):
    """Return only visible user/assistant messages, excluding analysis and tool payloads."""
    kind = record.get("type")
    if not isinstance(kind, str):
        raise LedgerError("Transcript record type is not a string")
    message = None
    if host == "codex":
        # Read the canonical response_item stream, not duplicate event_msg notifications.
        if kind == "response_item":
            payload = record.get("payload")
            if not isinstance(payload, dict):
                raise LedgerError("Codex response_item payload is not an object")
            if payload.get("type") == "message":
                message = payload
        elif kind == "item.completed":  # codex exec --json assistant events
            item = record.get("item")
            if not isinstance(item, dict):
                raise LedgerError("Codex item.completed item is not an object")
            if item.get("type") == "agent_message":
                message = {"role": "assistant", "content": item.get("text")}
        elif kind not in {"session_meta", "turn_context", "event_msg", "compacted", "thread.started", "turn.started", "turn.completed", "turn.failed", "item.started", "item.updated", "error"}:
            raise LedgerError("Unknown Codex transcript record; inspect adapter compatibility")
    elif host == "claude":
        if kind in {"user", "assistant"}:
            if record.get("isMeta") or record.get("isCompactSummary"):
                return None
            message = record.get("message")
            if not isinstance(message, dict):
                raise LedgerError("Claude message record has no message object")
        elif kind not in {"system", "progress", "file-history-snapshot", "queue-operation", "summary", "last-prompt", "custom-title", "agent-name", "pr-link", "bridge-pointer", "saved_hook_context"}:
            raise LedgerError("Unknown Claude transcript record; inspect adapter compatibility")
    elif host == "openclaw":
        if kind == "message":
            message = record.get("message")
            if not isinstance(message, dict):
                raise LedgerError("OpenClaw message record has no message object")
        elif kind not in {"session", "model_change", "thinking_level_change", "custom", "custom_message", "compaction", "branch_summary", "label"}:
            raise LedgerError("Unknown OpenClaw transcript record; inspect adapter compatibility")
    else:
        raise LedgerError("Unsupported transcript host")
    if message is None:
        return None
    if not isinstance(message, dict):
        raise LedgerError("Invalid message record")
    if not isinstance(message.get("role"), str):
        raise LedgerError("Message role is not a string")
    if message.get("role") not in {"user", "assistant"}:
        return None
    if message.get("channel") is not None and not isinstance(message["channel"], str):
        raise LedgerError("Message channel is not a string")
    if message.get("channel") in {"analysis", "summary", "justify", "confidence"}:
        return None
    text, attachments = visible(message.get("content", []))
    if not text and not attachments:
        return None
    return dict(role=message["role"], text=text, attachments=attachments, origin="host-transcript", host=host)


def drain(store, host, external):
    binding = store.binding(host, external)
    if not binding:
        return {"captured": 0, "state": "not recording"}
    if not binding["path"]:
        raise LedgerError("Active session has no transcript binding; use a verified native capture route")
    try:
        # Cursor, imported messages and fingerprint are committed together.
        with store.db:
            store.db.execute("BEGIN IMMEDIATE")
            binding = store.binding(host, external)
            if not binding:
                return {"captured": 0, "state": "not recording"}
            count, partial_tail = 0, False
            with open(binding["path"], "rb") as f:
                h, remaining = hashlib.sha256(), binding["offset"]
                while remaining:
                    chunk = f.read(min(remaining, 1024 * 1024))
                    if not chunk:
                        break
                    h.update(chunk)
                    remaining -= len(chunk)
                if remaining or h.hexdigest() != binding["prefix"]:
                    raise LedgerError("Transcript was truncated/replaced; capture paused, rebind explicitly")
                offset = binding["offset"]
                while True:
                    line = f.readline(MAX_LINE + 1)
                    if not line:
                        break
                    if len(line) > MAX_LINE:
                        raise LedgerError("Transcript line exceeds capture limit")
                    if not line.endswith(b"\n"):
                        partial_tail = True
                        break  # Torn tail remains pending for the next drain.
                    try:
                        record = json.loads(line)
                    except (ValueError, UnicodeDecodeError):
                        raise LedgerError("Malformed complete transcript line; cursor not advanced") from None
                    if not isinstance(record, dict):
                        raise LedgerError("Transcript record is not an object")
                    message = parse_record(host, record)
                    if message:
                        # Physical position, not content hash, preserves repeated identical answers.
                        store._append(binding["topic"], binding["session"], "message", message, source="transcript-byte:" + str(offset))
                        count += 1
                    offset += len(line)
                    h.update(line)
                store.db.execute("UPDATE captures SET offset=?, prefix=?, error=NULL, checked=? WHERE host=? AND external=?", (offset, h.hexdigest(), now(), host, external))
            return {"captured": count, "state": "complete lines locally persisted", "partial_tail": partial_tail, "offset": offset}
    except (OSError, LedgerError) as e:
        # Diagnostics intentionally exclude message text and file contents.
        detail = str(e) if isinstance(e, LedgerError) else "Transcript read failed; check local path/access"
        with store.db:
            store.db.execute("UPDATE captures SET error=?,checked=? WHERE host=? AND external=?", (detail, now(), host, external))
        raise LedgerError(detail) from None


def drain_all(store):
    result = []
    for row in store.db.execute("SELECT host,external FROM captures WHERE active=1 AND path IS NOT NULL").fetchall():
        try:
            result.append(dict(host=row[0], external=row[1], **drain(store, *row)))
        except LedgerError as e:
            result.append(dict(host=row[0], external=row[1], error=str(e)))
    return result


def hook(store, host, payload):
    if not isinstance(payload, dict):
        raise LedgerError("Hook input must be an object")
    external = payload.get("session_id")
    if not isinstance(external, str) or not external:
        raise LedgerError("Hook has no host session identity")
    event = payload.get("hook_event_name")
    prompt = payload.get("prompt", "") if event == "UserPromptSubmit" else ""
    if isinstance(prompt, str) and prompt.startswith("/learn-start "):
        parts = prompt.strip().split(maxsplit=2)
        if len(parts) != 3 or not payload.get("transcript_path"):
            raise LedgerError("Use /learn-start TOPIC_KEY Title in a host with a transcript path")
        state = store.start(parts[1], parts[2], host, external, payload["transcript_path"])
        return {"systemMessage": "Learning recording enabled from this boundary; local storage ready. Run worker for capture/sync between hooks.",
                "hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "Use learning-tutor. Learning session: " + state["session"] + "; topic: " + state["topic"]}}
    binding = store.binding(host, external)
    if not binding:
        return {}
    if isinstance(prompt, str) and prompt.strip() == "/learn-stop":
        gap = None
        try:
            result = drain(store, host, external)
            if result.get("partial_tail"):
                gap = "Stopped with an incomplete transcript tail"
        except LedgerError as e:
            gap = str(e)
        if gap:
            with store.db:
                store.db.execute("UPDATE captures SET error=? WHERE host=? AND external=?", (gap, host, external))
        store.stop(host, external)
        return {"systemMessage": "Learning recording stopped; pending records remain queued." + (" Capture gap: " + gap if gap else "")}
    if payload.get("transcript_path") and str(Path(payload["transcript_path"]).resolve()) != binding["path"]:
        raise LedgerError("Host transcript path changed; explicitly reconcile before rebinding")
    result = drain(store, host, external)
    # SessionEnd is not an opt-out: retaining the binding permits post-crash/final-tail recovery.
    if event == "UserPromptSubmit":
        return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": "Learning capture checkpoint: " + result["state"] + ". Query ledger status; do not imply server confirmation."}}
    return {}
