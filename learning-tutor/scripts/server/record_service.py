#!/usr/bin/env python3
"""PostgreSQL teaching-event service. JSON RPC over SSH, with no listening port."""
import json
import os
from pathlib import Path
import sys
import urllib.parse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ledger import LedgerError, canonical, digest, validate
from record_refs import check_references

MAX_BATCH = 4 * 1024 * 1024
MAX_REQUEST = MAX_BATCH + 4096


def pg_projection(value):
    """PostgreSQL cannot represent NUL in text/JSONB; never change the envelope."""
    if isinstance(value, str):
        return value.replace("\x00", "\\u0000")
    if isinstance(value, list):
        return [pg_projection(x) for x in value]
    if isinstance(value, dict):
        return {pg_projection(k): pg_projection(v) for k, v in value.items()}
    return value


class ServiceError(LedgerError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


class Service:
    def __init__(self, config_dir=None):
        import psycopg
        from psycopg.rows import dict_row
        root = Path(config_dir or Path.home() / ".config/learning-tutor")
        path = root / "record-database.json"
        if path.is_symlink() or not path.is_file() or (os.name != "nt" and path.stat().st_mode & 0o077):
            raise ServiceError("storage")
        config = json.loads(path.read_text(encoding="utf-8"))
        self.profile = config.pop("profile")
        self.db = psycopg.connect(**config, autocommit=True, row_factory=dict_row, connect_timeout=8,
                                  options="-c statement_timeout=30000 -c lock_timeout=10000 -c idle_in_transaction_session_timeout=30000")

    def close(self):
        self.db.close()

    def identity(self, lock=False):
        row = self.db.execute("SELECT server_id,cursor FROM learning.profiles WHERE profile=%s" + (" FOR UPDATE" if lock else ""), (self.profile,)).fetchone()
        if not row:
            raise ServiceError("identity")
        return dict(v=1, profile=self.profile, server_id=str(row["server_id"])), row["cursor"]

    def event(self, eid):
        row = self.db.execute("SELECT envelope FROM learning.events WHERE profile=%s AND id=%s", (self.profile, eid)).fetchone()
        return json.loads(row["envelope"]) if row else None

    def topic_exists(self, topic):
        return bool(self.db.execute("SELECT 1 FROM learning.topics WHERE profile=%s AND topic=%s", (self.profile, topic)).fetchone())

    def insert(self, event, cursor):
        from psycopg.types.json import Jsonb
        h = digest(event)
        old = self.db.execute("SELECT hash FROM learning.receipts WHERE profile=%s AND id=%s", (self.profile, event["id"])).fetchone()
        if old and old["hash"] != h:
            raise ServiceError("conflict")
        tombstone = self.db.execute("SELECT 1 FROM learning.tombstones WHERE profile=%s AND topic=%s", (self.profile, event["topic"])).fetchone()
        if old:
            return ("deleted" if tombstone and event["kind"] != "delete" else "duplicate"), cursor
        used = self.db.execute("SELECT 1 FROM learning.receipts WHERE profile=%s AND device=%s AND seq=%s", (self.profile, event["device"], event["seq"])).fetchone()
        if used:
            raise ServiceError("conflict")
        self.db.execute("INSERT INTO learning.receipts(profile,id,hash,device,seq) VALUES(%s,%s,%s,%s,%s)",
                        (self.profile, event["id"], h, event["device"], event["seq"]))
        if tombstone and event["kind"] != "delete":
            return "deleted", cursor
        try:
            check_references(event, self.event, self.topic_exists, LedgerError)
        except LedgerError:
            raise ServiceError("reference") from None
        if event["kind"] == "delete":
            self.db.execute("INSERT INTO learning.tombstones(profile,topic,event_id) VALUES(%s,%s,%s) ON CONFLICT DO NOTHING", (self.profile, event["topic"], event["id"]))
            self.db.execute("DELETE FROM learning.events WHERE profile=%s AND topic=%s AND kind <> 'delete'", (self.profile, event["topic"]))
            self.db.execute("DELETE FROM learning.topics WHERE profile=%s AND topic=%s", (self.profile, event["topic"]))
        elif event["kind"] == "topic":
            self.db.execute("INSERT INTO learning.topics(profile,topic,key,title) VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                            (self.profile, event["topic"], pg_projection(event["data"]["key"]), pg_projection(event["data"]["title"])))
        cursor += 1
        projection = pg_projection(event["data"])
        self.db.execute("""INSERT INTO learning.events(profile,id,cursor,topic,session,device,seq,kind,at,envelope,data,projection_escaped,hash)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (self.profile, event["id"], cursor, event["topic"], event["session"], event["device"], event["seq"], event["kind"], event["at"], canonical(event), Jsonb(projection), projection != event["data"], h))
        return "accepted", cursor

    def post(self, body):
        if (not isinstance(body, dict) or type(body.get("v")) is not int or body["v"] != 1
                or body.get("profile") != self.profile or not isinstance(body.get("events"), list)
                or not 1 <= len(body["events"]) <= 100 or len(canonical(body).encode()) > MAX_BATCH):
            raise ServiceError("invalid_request")
        events = body["events"]
        try:
            for event in events:
                validate(event, self.profile)
                if event["seq"] > 9223372036854775807:
                    raise LedgerError("Sequence exceeds supported range")
            if len({e["id"] for e in events}) != len(events):
                raise LedgerError("Duplicate IDs in one request")
        except (LedgerError, TypeError, ValueError):
            raise ServiceError("invalid_event") from None
        receipts = []
        with self.db.transaction():
            info, cursor = self.identity(lock=True)
            for event in sorted(events, key=lambda e: e["kind"] != "delete"):
                status, cursor = self.insert(event, cursor)
                receipts.append(dict(id=event["id"], hash=digest(event), status=status))
            self.db.execute("UPDATE learning.profiles SET cursor=%s WHERE profile=%s", (cursor, self.profile))
        return {**info, "receipts": receipts}  # commit has completed

    def page(self, parsed, topic=None):
        try:
            query = urllib.parse.parse_qs(parsed.query, strict_parsing=True) if parsed.query else {}
            if set(query) - {"after", "limit", "max_bytes"} or any(len(x) != 1 for x in query.values()):
                raise ValueError()
            after = int(query.get("after", ["0"])[0])
            limit = int(query.get("limit", ["100"])[0])
            budget = int(query.get("max_bytes", [str(MAX_BATCH)])[0])
            if not 0 <= after <= 9223372036854775807 or not 1 <= limit <= 100 or not 2048 <= budget <= MAX_BATCH:
                raise ValueError()
        except (ValueError, TypeError):
            raise ServiceError("invalid_request") from None
        with self.db.transaction():
            self.db.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            info, highwater = self.identity()
            if after > highwater:
                raise ServiceError("identity")
            sql = "SELECT cursor,envelope FROM learning.events WHERE profile=%s AND cursor>%s"
            params = [self.profile, after]
            if topic is not None:
                sql += " AND topic=%s"
                params.append(topic)
            rows = self.db.execute(sql + " ORDER BY cursor LIMIT %s", params + [limit + 1]).fetchall()
            events, used, cursor = [], 1024, after
            for row in rows[:limit]:
                size = len(row["envelope"].encode()) + 1
                if used + size > budget:
                    if not events:
                        raise ServiceError("page_budget")
                    break
                events.append(json.loads(row["envelope"]))
                used += size
                cursor = row["cursor"]
            more = len(rows) > len(events)
            if not more:
                cursor = highwater  # safely skip physically removed/deleted feed rows
            return {**info, "events": events, "cursor": cursor, "more": more}

    def handle(self, request):
        if not isinstance(request, dict) or set(request) != {"v", "profile", "path", "body"} or type(request["v"]) is not int or request["v"] != 1 or request["profile"] != self.profile:
            raise ServiceError("identity")
        path, body = request["path"], request["body"]
        if not isinstance(path, str) or len(path) > 2048:
            raise ServiceError("invalid_request")
        parsed = urllib.parse.urlsplit(path)
        if parsed.scheme or parsed.netloc or parsed.fragment:
            raise ServiceError("invalid_request")
        if body is not None:
            if path != "/v1/events":
                raise ServiceError("invalid_request")
            return self.post(body)
        if path == "/v1/identity":
            return self.identity()[0]
        if parsed.path == "/v1/events":
            return self.page(parsed)
        parts = parsed.path.split("/")
        if len(parts) == 5 and parts[1:3] == ["v1", "topics"] and parts[4] == "events":
            topic = urllib.parse.unquote(parts[3])
            if not topic or len(topic) > 200:
                raise ServiceError("invalid_request")
            return self.page(parsed, topic)
        raise ServiceError("invalid_request")


def main():
    service = None
    try:
        raw = sys.stdin.buffer.read(MAX_REQUEST + 1)
        if len(raw) > MAX_REQUEST:
            raise ServiceError("invalid_request")
        request = json.loads(raw)
        service = Service(os.environ.get("LEARNING_RECORD_CONFIG"))
        print(canonical({"ok": True, "result": service.handle(request)}))
        return 0
    except Exception as e:
        code = e.code if isinstance(e, ServiceError) else "invalid_request" if isinstance(e, (ValueError, TypeError)) else "storage"
        print(canonical({"ok": False, "code": code}))
        return 2
    finally:
        if service:
            service.close()


if __name__ == "__main__":
    sys.exit(main())
