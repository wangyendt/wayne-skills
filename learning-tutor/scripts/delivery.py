"""Local-only turn gates and bounded, event-driven delivery. No daemon or wire changes."""
from contextlib import contextmanager
import hashlib
import json
import os
import time

from ledger import LedgerError


def initialize(store):
    store.db.executescript("""
    CREATE TABLE IF NOT EXISTS delivery_runs(
      session TEXT PRIMARY KEY, host TEXT NOT NULL, external TEXT NOT NULL, turn TEXT);
    CREATE TABLE IF NOT EXISTS delivery_turns(
      session TEXT NOT NULL, id TEXT NOT NULL, state TEXT NOT NULL, proof TEXT,
      PRIMARY KEY(session,id));
    CREATE TABLE IF NOT EXISTS delivery_events(
      event TEXT PRIMARY KEY, session TEXT NOT NULL, turn TEXT);
    CREATE TABLE IF NOT EXISTS delivery_assets(
      asset TEXT PRIMARY KEY, session TEXT NOT NULL, turn TEXT NOT NULL);
    """)
    # Adopt old host bindings conservatively. Existing unacknowledged raw turns
    # have no reliable completion proof: retain locally rather than uploading them.
    with store.db:
        for binding in store.db.execute("SELECT * FROM captures WHERE host!='manual'").fetchall():
            if store.db.execute("SELECT 1 FROM delivery_runs WHERE session=?", (binding["session"],)).fetchone():
                continue
            store.db.execute("INSERT INTO delivery_runs VALUES(?,?,?,NULL)", (binding["session"], binding["host"], binding["external"]))
            for row in store.db.execute("SELECT id,envelope,ack FROM events").fetchall():
                event = json.loads(row["envelope"])
                if event["session"] != binding["session"] or row["ack"]:
                    continue
                turn = "legacy-unverified" if event["kind"] not in {"topic", "session", "alias"} else None
                if turn:
                    store.db.execute("INSERT OR IGNORE INTO delivery_turns VALUES(?,?,'incomplete',NULL)", (binding["session"], turn))
                store.db.execute("INSERT OR IGNORE INTO delivery_events VALUES(?,?,?)", (row["id"], binding["session"], turn))


def register_event(store, event):
    """Called inside the same transaction as event insertion and source cursor movement."""
    session, data = event["session"], event["data"]
    run = store.db.execute("SELECT * FROM delivery_runs WHERE session=?", (session,)).fetchone()
    if not run:
        return  # Explicit manual records / old archives remain administratively syncable.
    turn = run["turn"]
    if event["kind"] == "message" and data["role"] == "user":
        candidate = event["id"]
        if candidate != turn:
            if turn:
                store.db.execute("UPDATE delivery_turns SET state='incomplete' WHERE session=? AND id=? AND state='pending'", (session, turn))
            turn = candidate
            store.db.execute("INSERT OR IGNORE INTO delivery_turns VALUES(?,?,'pending',NULL)", (session, turn))
            store.db.execute("UPDATE delivery_runs SET turn=? WHERE session=?", (turn, session))
    if event["kind"] in {"topic", "session", "alias"}:
        turn = None
    store.db.execute("INSERT INTO delivery_events VALUES(?,?,?)", (event["id"], session, turn))
    if event["kind"] == "message" and data["role"] == "assistant" and turn:
        settle(store, session, turn)


def adopt_assets(store):
    """Legacy teaching bytes without a turn receipt stay local, including manual flush."""
    with store.db:
        for row in store.db.execute("SELECT j.* FROM asset_jobs j LEFT JOIN delivery_assets d ON d.asset=j.id WHERE j.state='pending' AND d.asset IS NULL").fetchall():
            metadata = json.loads(row["request"]).get("metadata", {})
            session = metadata.get("session_id")
            run = store.db.execute("SELECT session FROM delivery_runs WHERE session=?", (session,)).fetchone() if session else None
            if not run and not session:
                run = store.db.execute("SELECT r.session FROM delivery_runs r JOIN captures c ON c.session=r.session WHERE c.topic=? LIMIT 1", (row["topic"],)).fetchone()
            if not run:
                continue
            session = run[0]
            store.db.execute("INSERT OR IGNORE INTO delivery_turns VALUES(?,'legacy-unverified','incomplete',NULL)", (session,))
            store.db.execute("INSERT INTO delivery_assets VALUES(?,?,'legacy-unverified')", (row["id"], session))


def settle(store, session, turn):
    row = store.db.execute("SELECT * FROM delivery_turns WHERE session=? AND id=?", (session, turn)).fetchone()
    if not row or row["state"] != "pending" or row["proof"] is None:
        return False
    messages = [json.loads(r[0])["data"] for r in store.db.execute(
        "SELECT e.envelope FROM events e JOIN delivery_events d ON d.event=e.id WHERE d.session=? AND d.turn=? AND e.kind='message' ORDER BY e.ordinal", (session, turn))]
    if not messages or messages[0]["role"] != "user" or messages[-1]["role"] != "assistant":
        return False
    last = messages[-1]
    # A Stop proof must match the actual final text. Process commentary isn't a final answer.
    if last.get("channel") not in (None, "final"):
        return False
    if not row["proof"] and last.get("channel") != "final":
        return False  # A textless native receipt also requires a final-channel record.
    if row["proof"] and hashlib.sha256(last["text"].encode()).hexdigest() != row["proof"]:
        return False
    store.db.execute("UPDATE delivery_turns SET state='complete' WHERE session=? AND id=?", (session, turn))
    return True


def complete(store, host, external, turn_id=None, last_text=None):
    binding = store.binding(host, external)
    if not binding or (not isinstance(last_text, str) and not turn_id):
        return False
    run = store.db.execute("SELECT * FROM delivery_runs WHERE session=?", (binding["session"],)).fetchone()
    if not run or not run["turn"] or (turn_id and turn_id != store.meta("source_turn:" + run["session"])):
        return False
    proof = hashlib.sha256(last_text.encode()).hexdigest() if isinstance(last_text, str) else ""
    if store.db.in_transaction:
        store.db.execute("UPDATE delivery_turns SET proof=? WHERE session=? AND id=? AND state='pending'", (proof, run["session"], run["turn"]))
        return settle(store, run["session"], run["turn"])
    with store.db:
        store.db.execute("UPDATE delivery_turns SET proof=? WHERE session=? AND id=? AND state='pending'", (proof, run["session"], run["turn"]))
        return settle(store, run["session"], run["turn"])


def event_complete(store, eid):
    row = store.db.execute("SELECT session,turn FROM delivery_events WHERE event=?", (eid,)).fetchone()
    if not row:
        return True
    if row["turn"] is None:
        return False  # Orphan messages aren't complete turns (control events handled separately).
    state = store.db.execute("SELECT state FROM delivery_turns WHERE session=? AND id=?", tuple(row)).fetchone()
    return bool(state and state[0] == "complete")


def run_active(store, session, scope=None):
    run = store.db.execute("SELECT * FROM delivery_runs WHERE session=?", (session,)).fetchone()
    if not run:
        return scope is None
    if scope and tuple(scope) != (run["host"], run["external"]):
        return False
    # Reopening THIS chat thaws prior complete runs, not other stopped chats.
    return bool(store.binding(run["host"], run["external"]))


def event_allowed(store, event, scope=None, seen=None):
    if event["kind"] == "topic" and scope:
        current = store.binding(*scope)
        return bool(current and (current["topic"] == event["topic"] or run_active(store, event["session"], scope)))
    row = store.db.execute("SELECT * FROM delivery_events WHERE event=?", (event["id"],)).fetchone()
    if row:
        if not run_active(store, row["session"], scope):
            return False
        if event["kind"] not in {"topic", "session", "alias"} and not event_complete(store, event["id"]):
            return False
    elif scope is not None:
        # Only structural topic creation can be borrowed from legacy/other scopes.
        if event["kind"] != "topic":
            return False
        current = store.binding(*scope)
        if not current or current["topic"] != event["topic"]:
            return False
    seen = set() if seen is None else seen
    if event["id"] in seen:
        return False
    seen.add(event["id"])
    refs = []
    if event["kind"] == "assessment":
        refs = event["data"]["evidence"] + event["data"].get("supersedes", [])
    elif event["kind"] == "checkpoint":
        refs = event["data"]["parents"]
    for eid in refs:
        ref = store.db.execute("SELECT envelope,ack FROM events WHERE id=?", (eid,)).fetchone()
        if not ref or (not ref["ack"] and not event_allowed(store, json.loads(ref["envelope"]), scope, seen.copy())):
            return False
    return True


def asset_allowed(store, aid, scope=None):
    row = store.db.execute("SELECT * FROM delivery_assets WHERE asset=?", (aid,)).fetchone()
    if not row:
        return scope is None
    state = store.db.execute("SELECT state FROM delivery_turns WHERE session=? AND id=?", (row["session"], row["turn"])).fetchone()
    return run_active(store, row["session"], scope) and bool(state and state[0] == "complete")


def register_asset(store, aid, topic, session):
    if session:
        run = store.db.execute("SELECT * FROM delivery_runs WHERE session=?", (session,)).fetchone()
        if not run:
            raise LedgerError("Teaching image session is not a hook-managed recording")
    else:
        rows = store.db.execute("SELECT r.* FROM delivery_runs r JOIN captures c ON c.session=r.session WHERE c.active=1 AND c.topic=?", (topic,)).fetchall()
        if len(rows) > 1:
            raise LedgerError("Multiple active recordings; supply the image session explicitly")
        run = rows[0] if rows else None
        if not run and store.db.execute("SELECT 1 FROM delivery_runs r JOIN delivery_events d ON d.session=r.session JOIN events e ON e.id=d.event WHERE e.topic=? LIMIT 1", (topic,)).fetchone():
            raise LedgerError("Recording is stopped; image remains outside the teaching upload path")
    if run:
        if not run["turn"] or not run_active(store, run["session"]):
            raise LedgerError("Image requires an active recording turn; capture the user's input first")
        store.db.execute("INSERT INTO delivery_assets VALUES(?,?,?)", (aid, run["session"], run["turn"]))
        return run["session"]
    return session


@contextmanager
def upload_lock(store):
    path = store.home / "upload.lock"
    with open(path, "a+b") as f:
        acquired = False
        try:
            if os.name == "nt":
                import msvcrt
                if path.stat().st_size == 0:
                    f.write(b"0"); f.flush()
                f.seek(0)
                try:
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                    acquired = True
                except OSError:
                    pass
            else:
                import fcntl
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    acquired = True
                except BlockingIOError:
                    pass
            yield acquired
        finally:
            if acquired:
                if os.name == "nt":
                    f.seek(0); msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def notice(store, scope, error):
    key = "delivery_notice:" + json.dumps(scope)
    previous = store.meta(key, "")
    value = error or ""
    with store.db:
        store.set_meta(key, value)
    if value and value != previous:
        message = "学习上传失败：" + value + "。完整记录仍在本地；下次学习事件重试。检查既有连接和服务状态；修改配置或服务前请确认。"
        with store.db:
            store.set_meta("delivery_ui:" + json.dumps(scope), message)
        return message
    if previous and not value:
        message = "学习上传故障已恢复。请查看待传数量，剩余批次将在后续事件处理。"
        with store.db:
            store.set_meta("delivery_ui:" + json.dumps(scope), message)
        return message
    return None


def deliver(store, host, external, budget=12, wait_for_lock=False):
    scope = (host, external)
    if not store.binding(*scope):
        return {"state": "frozen", "notice": None}
    deadline = time.monotonic() + budget
    while time.monotonic() < deadline:
        with upload_lock(store) as acquired:
            if acquired:
                return _deliver_locked(store, scope, deadline)
        if not wait_for_lock:
            return {"state": "another upload is in flight", "notice": None}
        # Stop shares the same total budget while awaiting an earlier short task.
        time.sleep(min(0.05, max(0, deadline - time.monotonic())))
    return {"state": "delivery budget reached; pending data retained", "notice": None}


def _deliver_locked(store, scope, deadline):
    from sync import synchronize
    from assets import flush
    errors, report = [], {}
    try:
        report["text"] = synchronize(store, timeout=min(10, max(0.01, deadline - time.monotonic())), scope=scope, deadline=deadline, max_batches=4)
    except LedgerError as e:
        errors.append(str(e))
    # Image failures must not roll back or suppress text receipts.
    if time.monotonic() < deadline and store.binding(*scope):
        try:
            report["images"] = flush(store, 2, scope=scope, deadline=deadline)
            errors.extend(r["error"] for r in report["images"]["results"] if r.get("error"))
        except (LedgerError, ValueError, OSError) as e:
            errors.append(str(e) if isinstance(e, LedgerError) else type(e).__name__)
    error = "; ".join(errors)
    report.update(state="failed" if error else "attempted", notice=notice(store, scope, error), delivery=summary(store))
    return report


def summary(store):
    states = dict(store.db.execute("SELECT state,count(*) FROM delivery_turns GROUP BY state").fetchall())
    return {"mode": "hook-driven; no persistent worker", "turns": states,
            "eligible_text_batch": len(store.pending()), "retry": "next learning event; stopped chats are frozen",
            "notices": [{"scope": json.loads(row["key"][len("delivery_ui:"):]), "message": row["value"]}
                        for row in store.db.execute("SELECT key,value FROM meta WHERE key LIKE 'delivery_ui:%' AND value!=''")]}


def consume_notice(store, scope):
    key = "delivery_ui:" + json.dumps(scope)
    message = store.meta(key)
    if message:
        with store.db:
            store.set_meta(key, "")
    return message
