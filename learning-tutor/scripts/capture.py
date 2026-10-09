"""Opt-in transcript adapters. Never discover or scan unrelated conversations."""
import hashlib
import json
from pathlib import Path
import time

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
        elif kind not in {"session_meta", "turn_context", "event_msg", "compacted", "world_state", "token_usage_record", "thread.started", "turn.started", "turn.completed", "turn.failed", "item.started", "item.updated", "error"}:
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
    if message["role"] == "user" and (text.strip() == "/learn-stop" or text.startswith("/learn-start ")):
        return None
    result = dict(role=message["role"], text=text, attachments=attachments, origin="host-transcript", host=host)
    if host == "codex" and message.get("channel"):
        result["channel"] = message["channel"]
    return result


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
                    if host == "codex" and record.get("type") == "turn_context":
                        native = record.get("payload", {}).get("turn_id")
                        if isinstance(native, str):
                            store.set_meta("source_turn:" + binding["session"], native)
                    if message:
                        native = store.meta("source_turn:" + binding["session"])
                        if host == "codex" and native:
                            message["turn_id"] = native
                        # Physical position, not content hash, preserves repeated identical answers.
                        store._append(binding["topic"], binding["session"], "message", message, source="transcript-byte:" + str(offset))
                        count += 1
                    if host == "codex" and record.get("type") == "event_msg":
                        payload = record.get("payload", {})
                        if isinstance(payload, dict) and payload.get("type") == "task_complete":
                            from delivery import complete
                            complete(store, host, external, payload.get("turn_id"), payload.get("last_agent_message"))
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


def await_stop_capture(store, host, external):
    # Hosts may launch synchronous and asynchronous handlers in parallel. Wait
    # briefly for the local proof, never infer a new proof from an old callback.
    deadline = time.monotonic() + 1
    while time.monotonic() < deadline:
        binding = store.binding(host, external)
        if not binding:
            return
        row = store.db.execute("SELECT t.state,t.proof FROM delivery_runs r JOIN delivery_turns t ON t.session=r.session AND t.id=r.turn WHERE r.session=?", (binding["session"],)).fetchone()
        if row and (row["state"] != "pending" or row["proof"] is not None):
            return
        time.sleep(0.02)


def hook(store, host, payload, phase="all"):
    """Capture is synchronous; Stop uploads finish boundedly before host teardown."""
    if not isinstance(payload, dict):
        raise LedgerError("Hook input must be an object")
    external = payload.get("session_id")
    if not isinstance(external, str) or not external:
        raise LedgerError("Hook has no host session identity")
    event = payload.get("hook_event_name")
    prompt = payload.get("prompt", "") if event == "UserPromptSubmit" else ""
    if phase != "upload" and isinstance(prompt, str) and prompt.startswith("/learn-start "):
        parts = prompt.strip().split(maxsplit=2)
        if len(parts) != 3 or not payload.get("transcript_path"):
            raise LedgerError("Use /learn-start TOPIC_KEY Title in a host with a transcript path")
        state = store.start(parts[1], parts[2], host, external, payload["transcript_path"], allow_missing=True)
        return {"systemMessage": "学习记录已开启：完整轮次结束后自动同步；没有常驻 worker。",
                "hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "Use learning-tutor. Learning session: " + state["session"] + "; topic: " + state["topic"]}}
    if isinstance(prompt, str) and prompt.strip() == "/learn-stop":
        if phase == "upload" or not store.binding(host, external):
            return {}
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
        return {"systemMessage": "学习记录及新上传已停止。待传完整轮次留在本地，下次明确开启同一聊天时补传。" + (" Capture gap: " + gap if gap else "")}
    binding = store.binding(host, external)
    if not binding:
        return {}
    if payload.get("transcript_path") and str(Path(payload["transcript_path"]).resolve()) != binding["path"]:
        raise LedgerError("Host transcript path changed; explicitly reconcile before rebinding")
    from delivery import complete, deliver, notice, consume_notice
    try:
        result = drain(store, host, external)
        if event in {"Interrupt", "StopFailure"}:
            with store.db:
                store.db.execute("UPDATE delivery_turns SET state='incomplete' WHERE session=? AND state='pending'", (binding["session"],))
        # An old asynchronous callback may run after the next user turn began.
        # Only the synchronous host event can attach a completion proof.
        if event == "Stop" and phase != "upload":
            complete(store, host, external, payload.get("turn_id"), payload.get("last_assistant_message"))
        elif event == "Stop" and phase == "upload":
            await_stop_capture(store, host, external)
            drain(store, host, external)  # Settle proof if the final line landed meanwhile.
    except LedgerError as e:
        warning = notice(store, (host, external, "capture"), str(e))
        return {"systemMessage": warning} if warning else {}
    capture_notice = notice(store, (host, external, "capture"), None)
    report = None
    if phase != "capture" and event not in {"SessionEnd", "Interrupt", "StopFailure"}:
        report = deliver(store, host, external, wait_for_lock=event == "Stop")
    delivery_notice = consume_notice(store, (host, external)) if phase != "upload" else (report.get("notice") if report else None)
    if phase == "upload" and event == "Stop" and delivery_notice:
        consume_notice(store, (host, external))  # Synchronous Stop already displays this notice.
    warnings = [v for v in (capture_notice, delivery_notice) if v]
    if warnings:
        return {"systemMessage": "\n".join(warnings)}
    # Stop expects JSON; no stdout chatter, continuation decisions, or model-generated capture.
    return {}
