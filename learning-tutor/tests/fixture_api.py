"""Loopback-only test peer. NOT a deployment server or PostgreSQL implementation."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import urllib.parse

from ledger import Ledger, LedgerError, canonical, digest, now, validate


class FixtureAPI:
    def __init__(self, home, token="fixture-token"):
        self.home, self.token = Path(home), token
        self.lock = threading.Lock()
        self.drop_ack = False
        self.corrupt_ack = False
        self.reverse_cursor = False
        self.posts = 0
        store = Ledger(home)
        store.db.execute("CREATE TABLE IF NOT EXISTS feed(seq INTEGER PRIMARY KEY AUTOINCREMENT,topic TEXT NOT NULL,event TEXT)")
        store.db.commit()
        store.close()
        peer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def send_json(self, body, code=200):
                data = canonical(body).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def auth(self):
                if self.headers.get("Authorization") != "Bearer " + peer.token:
                    self.send_json({"error": "auth"}, 401)
                    return False
                return True

            def do_GET(self):
                if not self.auth():
                    return
                with peer.lock:
                    store = Ledger(peer.home)
                    try:
                        p = urllib.parse.urlsplit(self.path)
                        common = {"profile": "personal", "server_id": "local-fixture-1"}
                        if p.path == "/v1/identity":
                            self.send_json(dict(v=1, **common))
                            return
                        qs = urllib.parse.parse_qs(p.query)
                        after, limit = int(qs.get("after", [0])[0]), min(int(qs.get("limit", [100])[0]), 100)
                        max_bytes = min(int(qs.get("max_bytes", [4194304])[0]), 4194304)
                        topic = None
                        if p.path.startswith("/v1/topics/"):
                            topic = p.path.split("/")[3]
                        elif p.path != "/v1/events":
                            self.send_json({}, 404)
                            return
                        query = "SELECT seq,event FROM feed WHERE seq>?"
                        args = [after]
                        if topic:
                            query += " AND topic=?"
                            args.append(topic)
                        rows = store.db.execute(query + " ORDER BY seq LIMIT ?", args + [limit + 1]).fetchall()
                        shown, used = [], 1024
                        for row in rows[:limit]:
                            size = len(row[1].encode()) + 1 if row[1] else 0
                            if used + size > max_bytes:
                                break
                            shown.append(row)
                            used += size
                        cursor = shown[-1][0] if shown else after
                        if peer.reverse_cursor:
                            cursor = -1
                        self.send_json(dict(events=[json.loads(r[1]) for r in shown if r[1]], cursor=cursor, more=len(rows) > len(shown), **common))
                    finally:
                        store.close()

            def do_POST(self):
                if not self.auth():
                    return
                if self.path != "/v1/events":
                    self.send_json({}, 404)
                    return
                with peer.lock:
                    store = Ledger(peer.home)
                    try:
                        length = int(self.headers.get("Content-Length", "0"))
                        if length > 16 * 1024 * 1024:
                            raise LedgerError("too large")
                        batch = json.loads(self.rfile.read(length))
                        if batch.get("profile") != "personal" or batch.get("v") != 1 or len(batch["events"]) > 100:
                            raise LedgerError("bad batch")
                        receipts = []
                        with store.db:
                            store.db.execute("BEGIN IMMEDIATE")
                            for event in batch["events"]:
                                validate(event, "personal")
                            for event in sorted(batch["events"], key=lambda e: e["kind"] != "delete"):
                                status = store._insert(event, ack=now())
                                if status == "accepted":
                                    if event["kind"] == "delete":
                                        store.db.execute("UPDATE feed SET event=NULL WHERE topic=?", (event["topic"],))
                                    store.db.execute("INSERT INTO feed(topic,event) VALUES(?,?)", (event["topic"], canonical(event)))
                                receipts.append({"id": event["id"], "hash": digest(event), "status": status})
                        peer.posts += 1
                        if peer.drop_ack:
                            peer.drop_ack = False
                            self.close_connection = True
                            return
                        if peer.corrupt_ack and receipts:
                            receipts[0]["hash"] = "wrong"
                        self.send_json({"profile": "personal", "server_id": "local-fixture-1", "receipts": receipts})
                    except (LedgerError, ValueError, KeyError):
                        self.send_json({"error": "invalid event batch"}, 409)
                    finally:
                        store.close()

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = "http://127.0.0.1:" + str(self.httpd.server_port)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join()
