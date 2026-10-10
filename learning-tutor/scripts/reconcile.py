"""Explicit, offline repair from a verified Codex host read, never live capture.

The agent must obtain the packet from codex_app.read_thread, not invent it.
This is a provenance-labelled administrative import, not hook coverage proof.
"""
import hashlib
import json
from datetime import datetime

from ledger import LedgerError, canonical
from delivery import settle, upload_lock


def epoch(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def reconcile_stopped(store, host, external, packet):
    with upload_lock(store) as acquired:
        if not acquired:
            raise LedgerError("Another upload or recovery is in flight; retry explicitly")
        return _reconcile_stopped(store, host, external, packet)


def _reconcile_stopped(store, host, external, packet):
    if host != "codex" or not isinstance(packet, dict) or packet.get("source") != "codex_app.read_thread" or packet.get("threadId") != external:
        raise LedgerError("Recovery requires a verified read of this exact Codex thread")
    turn = packet.get("turn")
    if not isinstance(turn, dict) or turn.get("status") != "completed" or turn.get("error") is not None:
        raise LedgerError("Recovery needs a successful completed host turn")
    native = turn.get("id")
    start, end = turn.get("startedAt"), turn.get("completedAt")
    if not isinstance(native, str) or not native or any(type(t) not in (int, float) for t in (start, end)) or not 0 < start <= end:
        raise LedgerError("Invalid host turn identity or timestamps")
    items = turn.get("items")
    if not isinstance(items, list) or any(not isinstance(i, dict) for i in items):
        raise LedgerError("Invalid host read items")
    users = [i for i in items if i.get("type") == "userMessage"]
    finals = [i for i in items if i.get("type") == "agentMessage" and i.get("phase") == "final_answer"]
    if len(users) != 1 or len(finals) != 1:
        raise LedgerError("Recovery requires one unambiguous user and final assistant message")
    user, final = users[0], finals[0]
    content = user.get("content")
    if not isinstance(content, list) or not content or any(not isinstance(c, dict) or c.get("type") != "text" or not isinstance(c.get("text"), str) for c in content):
        raise LedgerError("Recovery currently accepts complete text messages only")
    text = "\n".join(c["text"] for c in content)
    if not text.strip() or text.strip() == "/learn-stop" or text.startswith("/learn-start ") or not isinstance(final.get("text"), str) or not final["text"]:
        raise LedgerError("Invalid recovery message or control command")
    if any(not isinstance(i.get("id"), str) or not i["id"] for i in (user, final)) or user["id"] == final["id"]:
        raise LedgerError("Host message identities must be distinct and nonempty")
    proofs = packet.get("assets", [])
    if not isinstance(proofs, list) or any(not isinstance(p, dict) or not isinstance(p.get("asset_id"), str) or not isinstance(p.get("host_item_id"), str) for p in proofs):
        raise LedgerError("Invalid asset recovery proofs")
    if len({p["asset_id"] for p in proofs}) != len(proofs):
        raise LedgerError("Duplicate asset recovery proof")
    # Each ID must appear in a non-truncated successful host tool result,
    # not merely in an agent's claim or the final reply's prose.
    proven = {}
    for i in items:
        out = i.get("output", {})
        if i.get("type") != "commandExecution" or i.get("status") != "completed" or i.get("exitCode") != 0 or not isinstance(out, dict) or out.get("truncated") is not False:
            continue
        if not isinstance(out.get("text"), str):
            continue
        for line in out["text"].splitlines():
            try:
                value = json.loads(line)
            except ValueError:
                continue
            if isinstance(value, dict) and isinstance(value.get("asset_id"), str) and value.get("state") == "local-pending":
                proven.setdefault(i.get("id"), set()).add(value["asset_id"])
    if any(p["asset_id"] not in proven.get(p["host_item_id"], set()) for p in proofs):
        raise LedgerError("Asset has no successful host enqueue receipt in this turn")
    packet_hash = hashlib.sha256(canonical(packet).encode()).hexdigest()
    with store.db:
        store.db.execute("BEGIN IMMEDIATE")
        binding = store.db.execute("SELECT * FROM captures WHERE host=? AND external=?", (host, external)).fetchone()
        if not binding or binding["active"]:
            raise LedgerError("Recovery requires an existing stopped chat; capture stays closed")
        session = binding["session"]
        receipt_key = "host_recovery:" + session + ":" + native
        previous = store.meta(receipt_key)
        if previous:
            previous = json.loads(previous)
            if previous["sha256"] != packet_hash:
                raise LedgerError("Recovery identity already has different host evidence")
            return {"state": "already reconciled", **previous}
        rows = store.db.execute("SELECT e.envelope FROM events e JOIN delivery_events d ON d.event=e.id WHERE d.session=? AND e.kind='session' ORDER BY e.ordinal", (session,)).fetchall()
        controls = [json.loads(r[0]) for r in rows]
        starts = [e for e in controls if e["data"].get("state") == "started"]
        stops = [e for e in controls if e["data"].get("state") == "stopped"]
        if not starts or not stops or not epoch(starts[0]["at"]) <= start <= end <= epoch(stops[-1]["at"]):
            raise LedgerError("Recovered turn lies outside the recorded start/stop interval")
        existing = [json.loads(r[0]) for r in store.db.execute("SELECT envelope FROM events WHERE topic=? AND kind='message'", (binding["topic"],))]
        if any(e["data"].get("turn_id") == native for e in existing):
            raise LedgerError("Host turn already has local messages; reconcile its native transcript instead")
        for p in proofs:
            row = store.db.execute("SELECT j.created,j.state,j.request,d.session,d.turn,t.state AS turn_state FROM asset_jobs j JOIN delivery_assets d ON d.asset=j.id JOIN delivery_turns t ON t.session=d.session AND t.id=d.turn WHERE j.id=?", (p["asset_id"],)).fetchone()
            if not row or row["session"] != session or row["state"] != "pending" or row["turn_state"] == "complete" or not start <= epoch(row["created"]) <= end:
                raise LedgerError("Asset is outside this incomplete session/host turn")
        # Preserve native identities, including repeated identical text. Never
        # rewrite the aborted old turn or infer completion from matching text.
        recovered = []
        for i, role, body, ts in ((user, "user", text, start), (final, "assistant", final["text"], end)):
            data = {"role": role, "text": body, "host": host, "origin": "host-read-recovery", "turn_id": native,
                    "host_message_id": i["id"], "host_timestamp": ts, "recovery_source": packet["source"]}
            if role == "assistant":
                data["channel"] = "final"
            recovered.append(store._append(binding["topic"], session, "message", data, source="host-read:" + i["id"]))
        turn_id = recovered[0]["id"]
        store.db.execute("UPDATE delivery_turns SET proof=? WHERE session=? AND id=?", (hashlib.sha256(final["text"].encode()).hexdigest(), session, turn_id))
        if not settle(store, session, turn_id):
            raise LedgerError("Recovered final did not satisfy normal turn completeness checks")
        ids = [e["id"] for e in recovered]
        # Agent assessments/checkpoints made during the recovered host turn
        # were associated with a stale transcript cursor. Rebind only those
        # existing administrative events inside the verified time interval.
        for row in store.db.execute("SELECT e.id,e.envelope FROM events e JOIN delivery_events d ON d.event=e.id WHERE d.session=? AND e.kind IN ('assessment','checkpoint')", (session,)).fetchall():
            e = json.loads(row["envelope"])
            if start <= epoch(e["at"]) <= end:
                store.db.execute("UPDATE delivery_events SET turn=? WHERE event=?", (turn_id, row["id"]))
                ids.append(row["id"])
        for p in proofs:
            store.db.execute("UPDATE delivery_assets SET turn=? WHERE asset=?", (turn_id, p["asset_id"]))
        receipt = {"source": packet["source"], "sha256": packet_hash, "stop_event": stops[-1]["id"], "native_turn": native,
                   "turn": turn_id, "events": ids, "assets": [p["asset_id"] for p in proofs]}
        store.set_meta(receipt_key, canonical(receipt))
        return {"state": "reconciled locally; no upload or capture", **receipt}
