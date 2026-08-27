"""Local, single-learner event ledger. Python 3.9+, standard library only."""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import unicodedata
import uuid
from datetime import datetime, timezone, timedelta

VERSION = 1
KINDS = {"topic", "alias", "session", "message", "assessment", "checkpoint", "delete"}
DIMENSIONS = {"explanation", "reasoning", "application"}
LEVELS = {"not_yet", "assisted", "independent", "transfer"}


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def normalize(value):
    return unicodedata.normalize("NFKC", value).strip().casefold()


def default_home():
    if os.environ.get("LEARNING_TUTOR_HOME"):
        return Path(os.environ["LEARNING_TUTOR_HOME"]).expanduser()
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / "learning-tutor"
    if __import__("sys").platform == "darwin":
        return Path.home() / "Library/Application Support/learning-tutor"
    return Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "learning-tutor"


class LedgerError(ValueError):
    pass


def validate(event, profile):
    required = {"v", "id", "profile", "device", "seq", "topic", "session", "kind", "at", "data"}
    if not isinstance(event, dict) or set(event) != required:
        raise LedgerError("Invalid event envelope")
    if type(event["v"]) is not int or event["v"] != VERSION or event["profile"] != profile or not isinstance(event["kind"], str) or event["kind"] not in KINDS:
        raise LedgerError("Protocol, profile or event kind mismatch")
    for field in ("id", "device", "topic", "session"):
        if not isinstance(event[field], str) or not event[field] or len(event[field]) > 200 or "\x00" in event[field]:
            raise LedgerError("Invalid event identity")
    if type(event["seq"]) is not int or event["seq"] < 1:
        raise LedgerError("Invalid event sequence")
    try:
        if datetime.fromisoformat(event["at"]).tzinfo is None:
            raise ValueError()
    except (TypeError, ValueError):
        raise LedgerError("Event time must include a timezone")
    d = event["data"]
    try:
        size = len(canonical(event).encode())
    except (TypeError, ValueError):
        raise LedgerError("Event data must be finite JSON values") from None
    if not isinstance(d, dict) or size > 1024 * 1024:
        raise LedgerError("Invalid or oversized event data")
    kind = event["kind"]
    if kind == "topic":
        if not all(isinstance(d.get(k), str) and d[k].strip() for k in ("key", "title")):
            raise LedgerError("Topic requires key and title")
        expected = str(uuid.uuid5(uuid.NAMESPACE_URL, profile + ":" + normalize(d["key"])))
        if event["topic"] != expected:
            raise LedgerError("Topic key/identity mismatch")
    if kind == "alias" and not (isinstance(d.get("name"), str) and d["name"].strip()):
        raise LedgerError("Alias requires a name")
    if kind == "message":
        if not isinstance(d.get("role"), str) or d.get("role") not in {"user", "assistant"} or not isinstance(d.get("text"), str):
            raise LedgerError("Only visible user/assistant messages are recorded")
        if not d["text"] and not d.get("attachments"):
            raise LedgerError("Empty message")
    if kind == "assessment":
        if not isinstance(d.get("dimension"), str) or not isinstance(d.get("level"), str) or d.get("dimension") not in DIMENSIONS or d.get("level") not in LEVELS:
            raise LedgerError("Invalid assessment dimension/level")
        for k in ("concept", "reason", "rubric", "assessor"):
            if not isinstance(d.get(k), str) or not d[k].strip():
                raise LedgerError("Assessment requires " + k)
        if not isinstance(d.get("evidence"), list) or not d["evidence"] or not all(isinstance(x, str) for x in d["evidence"]):
            raise LedgerError("Assessment requires evidence IDs")
        if type(d.get("hints")) is not int or d["hints"] < 0:
            raise LedgerError("Assessment requires a nonnegative hint count")
        if d["hints"] and d["level"] in {"independent", "transfer"}:
            raise LedgerError("Assisted answers are not independent evidence")
        if d["level"] == "transfer" and d.get("novel") is not True:
            raise LedgerError("Transfer requires a novel problem")
        if not isinstance(d.get("supersedes", []), list) or not all(isinstance(x, str) for x in d.get("supersedes", [])):
            raise LedgerError("Assessment supersedes must be event IDs")
    if kind == "checkpoint":
        if not isinstance(d.get("next"), str) or not d["next"].strip():
            raise LedgerError("Checkpoint requires next teaching action")
        if not isinstance(d.get("parents"), list) or not all(isinstance(x, str) for x in d["parents"]):
            raise LedgerError("Checkpoint requires parent IDs")


class Ledger:
    def __init__(self, home=None, profile="personal"):
        if not isinstance(profile, str) or not profile.strip() or len(profile) > 200 or "\x00" in profile:
            raise LedgerError("Profile must be a nonempty learner namespace")
        self.home = Path(home or default_home()).expanduser().resolve()
        self.home.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.db = sqlite3.connect(str(self.home / "learning.sqlite3"), timeout=10)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS events(
          ordinal INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT UNIQUE NOT NULL,
          topic TEXT NOT NULL, kind TEXT NOT NULL, envelope TEXT NOT NULL,
          hash TEXT NOT NULL, ack TEXT, cached_at TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS events_topic ON events(topic);
        CREATE TABLE IF NOT EXISTS receipts(id TEXT PRIMARY KEY, hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS tombstones(topic TEXT PRIMARY KEY, event_id TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS catalog(topic TEXT PRIMARY KEY, key TEXT NOT NULL, title TEXT NOT NULL, archived INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS captures(
          host TEXT NOT NULL, external TEXT NOT NULL, topic TEXT NOT NULL,
          session TEXT NOT NULL, path TEXT, offset INTEGER NOT NULL DEFAULT 0,
          prefix TEXT NOT NULL DEFAULT '', active INTEGER NOT NULL DEFAULT 1,
          error TEXT, checked TEXT, PRIMARY KEY(host, external));
        """)
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO meta VALUES('version', ?)", (str(VERSION),))
            self.db.execute("INSERT OR IGNORE INTO meta VALUES('profile', ?)", (profile,))
            self.db.execute("INSERT OR IGNORE INTO meta VALUES('device', ?)", (str(uuid.uuid4()),))
            self.db.execute("INSERT OR IGNORE INTO meta VALUES('seq', '0')")
            self.db.execute("INSERT OR IGNORE INTO meta VALUES('cursor', '0')")
        if self.meta("version") != str(VERSION) or self.meta("profile") != profile:
            self.close()
            raise LedgerError("Existing store version/profile mismatch; use its original profile")
        self.profile = profile
        self.device = self.meta("device")
        if os.name != "nt":
            for name in ("learning.sqlite3", "learning.sqlite3-wal", "learning.sqlite3-shm"):
                p = self.home / name
                if p.exists():
                    p.chmod(0o600)

    def close(self):
        self.db.close()

    def meta(self, key, default=None):
        row = self.db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return row[0] if row else default

    def set_meta(self, key, value):
        self.db.execute("INSERT OR REPLACE INTO meta VALUES(?, ?)", (key, str(value)))

    def topic_id(self, key):
        if not normalize(key):
            raise LedgerError("Topic key is empty")
        return str(uuid.uuid5(uuid.NAMESPACE_URL, self.profile + ":" + normalize(key)))

    def _check_refs(self, e):
        from record_refs import check_references
        def get_event(eid):
            row = self.db.execute("SELECT envelope FROM events WHERE id=?", (eid,)).fetchone()
            return json.loads(row[0]) if row else None
        def topic_exists(topic):
            return bool(self.db.execute("SELECT 1 FROM catalog WHERE topic=?", (topic,)).fetchone())
        check_references(e, get_event, topic_exists, LedgerError)

    def _insert(self, e, ack=None, check_refs=True):
        validate(e, self.profile)
        h = digest(e)
        old = self.db.execute("SELECT hash FROM receipts WHERE id=?", (e["id"],)).fetchone()
        if old and old[0] != h:
            raise LedgerError("Event identity collision with different content")
        if self.db.execute("SELECT 1 FROM tombstones WHERE topic=?", (e["topic"],)).fetchone() and e["kind"] != "delete":
            self.db.execute("INSERT OR IGNORE INTO receipts VALUES(?, ?)", (e["id"], h))
            return "deleted"
        existing = self.db.execute("SELECT 1 FROM events WHERE id=?", (e["id"],)).fetchone()
        if existing:
            if ack:
                self.db.execute("UPDATE events SET ack=COALESCE(ack, ?) WHERE id=?", (ack, e["id"]))
            return "duplicate"
        if check_refs:
            self._check_refs(e)
        if e["kind"] == "delete":
            self.db.execute("INSERT OR IGNORE INTO tombstones VALUES(?, ?)", (e["topic"], e["id"]))
            self.db.execute("DELETE FROM events WHERE topic=? AND kind!='delete'", (e["topic"],))
            self.db.execute("DELETE FROM catalog WHERE topic=?", (e["topic"],))
            self.db.execute("DELETE FROM captures WHERE topic=?", (e["topic"],))
        if e["kind"] == "topic":
            self.db.execute("INSERT OR IGNORE INTO catalog(topic,key,title) VALUES(?,?,?)", (e["topic"], e["data"]["key"], e["data"]["title"]))
        self.db.execute("INSERT OR IGNORE INTO receipts VALUES(?,?)", (e["id"], h))
        self.db.execute("INSERT INTO events(id,topic,kind,envelope,hash,ack,cached_at) VALUES(?,?,?,?,?,?,?)", (e["id"], e["topic"], e["kind"], canonical(e), h, ack, now()))
        return "accepted"

    def _append(self, topic, session, kind, data, source=None):
        # Caller holds one transaction, including any capture cursor update.
        eid = str(uuid.uuid5(uuid.NAMESPACE_URL, session + ":" + source)) if source else str(uuid.uuid4())
        old = self.db.execute("SELECT envelope FROM events WHERE id=?", (eid,)).fetchone()
        if old:
            e = json.loads(old[0])
            if e["data"] != data or e["topic"] != topic or e["kind"] != kind:
                raise LedgerError("Source message changed under the same identity")
            return e
        seq = int(self.meta("seq")) + 1
        e = dict(v=VERSION, id=eid, profile=self.profile, device=self.device, seq=seq,
                 topic=topic, session=session, kind=kind, at=now(), data=data)
        if self._insert(e) == "deleted":
            raise LedgerError("Topic was deleted; start a new topic key")
        self.set_meta("seq", seq)
        return e

    def append(self, topic, session, kind, data, source=None):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            return self._append(topic, session, kind, data, source)

    def start(self, key, title, host="manual", external=None, path=None):
        topic = self.topic_id(key)
        external = external or str(uuid.uuid4())
        if host not in {"manual", "codex", "claude", "openclaw"}:
            raise LedgerError("Unknown host")
        offset, prefix = 0, ""
        if path:
            path = str(Path(path).expanduser().resolve())
            with open(path, "rb") as f:
                h, tail = hashlib.sha256(), b""
                while True:
                    chunk = f.read(1024 * 1024)
                    if not chunk:
                        break
                    h.update(chunk)
                    offset += len(chunk)
                    tail = chunk[-1:]
            if tail and tail != b"\n":
                raise LedgerError("Transcript has an incomplete final line; retry start")
            prefix = h.hexdigest()
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            old = self.db.execute("SELECT * FROM captures WHERE host=? AND external=? AND active=1", (host, external)).fetchone()
            if old:
                if old["topic"] != topic:
                    raise LedgerError("This host session is already recording another topic; stop it first")
                return dict(old)
            session = str(uuid.uuid4())
            if not self.db.execute("SELECT 1 FROM catalog WHERE topic=?", (topic,)).fetchone():
                self._append(topic, session, "topic", {"key": normalize(key), "title": title})
            if self.db.execute("SELECT archived FROM catalog WHERE topic=?", (topic,)).fetchone()[0]:
                raise LedgerError("Topic was evicted locally; hydrate before continuing")
            self._append(topic, session, "session", {"host": host, "state": "started"})
            self.db.execute("INSERT OR REPLACE INTO captures(host,external,topic,session,path,offset,prefix) VALUES(?,?,?,?,?,?,?)", (host, external, topic, session, path, offset, prefix))
            return dict(self.db.execute("SELECT * FROM captures WHERE host=? AND external=?", (host, external)).fetchone())

    def binding(self, host, external):
        row = self.db.execute("SELECT * FROM captures WHERE host=? AND external=? AND active=1", (host, external)).fetchone()
        return dict(row) if row else None

    def stop(self, host, external):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            binding = self.binding(host, external)
            if not binding:
                raise LedgerError("Learning session is not active")
            self._append(binding["topic"], binding["session"], "session", {"host": host, "state": "stopped", "capture_gap": binding["error"]})
            self.db.execute("UPDATE captures SET active=0 WHERE host=? AND external=?", (host, external))

    def events(self, topic=None):
        query = "SELECT envelope FROM events"
        args = ()
        if topic:
            query += " WHERE topic=?"
            args = (topic,)
        return [json.loads(r[0]) for r in self.db.execute(query + " ORDER BY ordinal", args)]

    def pending(self, limit=100, max_bytes=4 * 1024 * 1024 - 1024):
        result, used = [], 0
        for row in self.db.execute("SELECT envelope FROM events WHERE ack IS NULL ORDER BY ordinal LIMIT ?", (limit,)):
            size = len(row[0].encode()) + 1
            if used + size > max_bytes:
                break
            result.append(json.loads(row[0]))
            used += size
        return result

    def accept_page(self, events, cursor):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            for e in events:
                validate(e, self.profile)
            # Deletion wins, including over pending local records.
            for e in sorted(events, key=lambda x: x["kind"] != "delete"):
                self._insert(e, ack=now(), check_refs=False)
            if cursor < int(self.meta("cursor")):
                raise LedgerError("Remote cursor moved backwards")
            self.set_meta("cursor", cursor)

    def acknowledge(self, sent, receipts):
        expected = {e["id"]: digest(e) for e in sent}
        if not isinstance(receipts, list) or len(receipts) != len(expected):
            raise LedgerError("Incomplete server receipt; events remain pending")
        seen = set()
        for r in receipts:
            if not isinstance(r, dict) or not isinstance(r.get("id"), str) or not isinstance(r.get("status"), str) or r.get("id") in seen or expected.get(r.get("id")) != r.get("hash") or r.get("status") not in {"accepted", "duplicate", "deleted"}:
                raise LedgerError("Invalid server receipt; events remain pending")
            seen.add(r["id"])
        if seen != set(expected):
            raise LedgerError("Receipt does not cover the submitted batch")
        with self.db:
            for r in receipts:
                if r["status"] == "deleted":
                    # Pull the durable tombstone before acknowledging deletion.
                    raise LedgerError("Remote topic deleted; pull again before retrying")
                self.db.execute("UPDATE events SET ack=COALESCE(ack, ?) WHERE id=? AND hash=?", (now(), r["id"], r["hash"]))

    def status(self):
        pending = self.db.execute("SELECT COUNT(*) FROM events WHERE ack IS NULL").fetchone()[0]
        captures = [dict(r) for r in self.db.execute("SELECT host,external,topic,session,active,error,checked FROM captures")]
        heartbeat = self.meta("worker_heartbeat")
        recent = bool(heartbeat and (datetime.now(timezone.utc) - datetime.fromisoformat(heartbeat)).total_seconds() < 30)
        worker = {"pid": self.meta("worker_pid"), "heartbeat": heartbeat,
                  "state": "recent activity (not proof of process liveness)" if recent else "no recent worker heartbeat"}
        return dict(profile=self.profile, device=self.device, pending=pending,
                    scope="local cache plus pending local events", captures=captures,
                    worker=worker,
                    last_sync=self.meta("last_sync"), sync_error=self.meta("sync_error"),
                    recording="capture errors" if any(r["error"] for r in captures if r["active"]) else "local ledger ready; inspect capture freshness")

    def search(self, text):
        needle = normalize(text)
        hits = []
        for row in self.db.execute("SELECT * FROM catalog ORDER BY key"):
            names = [row["key"], row["title"]]
            names += [e["data"]["name"] for e in self.events(row["topic"]) if e["kind"] == "alias"]
            if any(needle in normalize(name) for name in names):
                hits.append(dict(row))
        return {"matches": hits, "scope": "local cache; sync/hydrate for other devices", "empty_means": "no matching cached record, not proof of never studied"}

    def summary(self, topic):
        row = self.db.execute("SELECT * FROM catalog WHERE topic=?", (topic,)).fetchone()
        if not row:
            raise LedgerError("No matching cached topic")
        es = self.events(topic)
        checkpoints = [e for e in es if e["kind"] == "checkpoint"]
        superseded = {p for e in checkpoints for p in e["data"]["parents"]}
        heads = [e for e in checkpoints if e["id"] not in superseded]
        assessments = [e for e in es if e["kind"] == "assessment"]
        revised = {x for e in assessments for x in e["data"].get("supersedes", [])}
        current_assessments = [e for e in assessments if e["id"] not in revised]
        assessed = {x for e in assessments for x in e["data"]["evidence"]}
        unanswered = [e["id"] for e in es if e["kind"] == "message" and e["data"]["role"] == "user" and e["id"] not in assessed]
        groups = {}
        for e in current_assessments:
            key = e["data"]["concept"] + "/" + e["data"]["dimension"]
            groups.setdefault(key, []).append(e)
        conflicts = [k for k, values in groups.items() if len({e["data"]["level"] for e in values}) > 1]
        return dict(topic=dict(row), assessments=assessments, current_assessments=current_assessments, checkpoint_heads=heads,
                    unassessed_user_messages=unanswered, differing_evidence=conflicts,
                    merge_needed=len(heads) > 1, note="Historical evidence is retained; levels are not averaged. No scheduled review or age-based score decay.")

    def prune(self, days=30):
        if days < 1:
            raise LedgerError("Retention must be at least one day")
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        removed = []
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            for row in self.db.execute("SELECT topic FROM catalog WHERE archived=0").fetchall():
                topic = row[0]
                active = self.db.execute("SELECT 1 FROM captures WHERE topic=? AND active=1", (topic,)).fetchone()
                keep = self.db.execute("SELECT 1 FROM events WHERE topic=? AND (ack IS NULL OR ack>=? OR cached_at>=?)", (topic, cutoff, cutoff)).fetchone()
                if active or keep:
                    continue
                self.db.execute("DELETE FROM events WHERE topic=?", (topic,))
                self.db.execute("UPDATE catalog SET archived=1 WHERE topic=?", (topic,))
                self.db.execute("DELETE FROM captures WHERE topic=?", (topic,))
                removed.append(topic)
        return {"evicted_topics": removed, "note": "Minimal topic index and identity receipts retained. Hydrate to restore evidence; no remote deletion."}
