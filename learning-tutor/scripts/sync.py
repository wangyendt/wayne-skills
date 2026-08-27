"""Bounded HTTPS or SSH synchronization. No database credentials on clients."""
import json
import os
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request
import tempfile

from ledger import LedgerError, canonical, now


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise LedgerError("API redirect rejected; configure its final HTTPS URL")


def check_url(url, allow_loopback=False):
    p = urllib.parse.urlsplit(url)
    if p.username or p.password or p.query or p.fragment or not p.hostname:
        raise LedgerError("API URL must have a host and no credentials, query or fragment")
    local = allow_loopback and p.scheme == "http" and p.hostname in {"127.0.0.1", "::1", "localhost"}
    if p.scheme != "https" and not local:
        raise LedgerError("HTTPS is required; HTTP is only for explicit loopback tests")
    return url.rstrip("/")


def configure(store, url, token_env="LEARNING_TUTOR_TOKEN", allow_loopback=False):
    check_url(url, allow_loopback)
    if not token_env or not token_env.replace("_", "a").isalnum():
        raise LedgerError("Invalid token environment variable name")
    old = load_config(store)
    if old and (old.get("transport", "https") != "https" or old.get("url") != url.rstrip("/")):
        raise LedgerError("Changing the API requires a fresh store or an explicit migration")
    data = dict(url=url.rstrip("/"), token_env=token_env, allow_loopback=bool(allow_loopback))
    save_config(store, data)
    return data


def save_config(store, data):
    fd, temp = tempfile.mkstemp(dir=str(store.home), prefix=".learning-config-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(canonical(data))
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, str(store.home / "config.json"))
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def configure_ssh(store, host, python, service):
    from record_ssh import settings
    config = settings(host, python, service)
    old = load_config(store)
    if old and old != config:
        raise LedgerError("Changing the record service requires a fresh store or explicit migration")
    save_config(store, config)
    return config


def load_config(store):
    path = store.home / "config.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


class Client:
    def __init__(self, store, timeout=5):
        config = load_config(store)
        if not config:
            raise LedgerError("Server not configured; records stay on this device. Configure the learning SSH service or HTTPS API, not the PostgreSQL port or existing context API.")
        self.ssh = None
        self.profile = store.profile
        if config.get("transport") == "ssh":
            from record_ssh import settings
            self.ssh = settings(config.get("host"), config.get("python"), config.get("service"))
            self.timeout = max(60, timeout)
            return
        self.url = check_url(config["url"], config.get("allow_loopback", False))
        self.token = os.environ.get(config["token_env"])
        if not self.token:
            raise LedgerError("Missing API token environment variable: " + config["token_env"])
        self.timeout = timeout
        self.opener = urllib.request.build_opener(NoRedirect())

    def request(self, path, body=None):
        if self.ssh:
            from record_ssh import request
            return request(self.ssh, self.profile, path, body, self.timeout)
        data = canonical(body).encode() if body is not None else None
        req = urllib.request.Request(self.url + path, data=data,
            headers={"Authorization": "Bearer " + self.token, "Content-Type": "application/json"})
        try:
            with self.opener.open(req, timeout=self.timeout) as response:
                raw = response.read(16 * 1024 * 1024 + 1)
                if len(raw) > 16 * 1024 * 1024:
                    raise LedgerError("Oversized API response")
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            raise LedgerError("API returned HTTP " + str(e.code)) from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise LedgerError("Server unreachable; check network/service. Locally saved events remain pending.") from None
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise LedgerError("API returned invalid JSON") from None


def identity(store, client):
    info = client.request("/v1/identity")
    if not isinstance(info, dict) or type(info.get("v")) is not int or info["v"] != 1 or info.get("profile") != store.profile or not isinstance(info.get("server_id"), str) or not info["server_id"]:
        raise LedgerError("Server identity/profile/protocol mismatch")
    previous = store.meta("server_id")
    if previous and previous != info["server_id"]:
        raise LedgerError("Server identity changed; migration needs explicit handling")
    with store.db:
        store.set_meta("server_id", info["server_id"])


def pull(store, client, max_pages=100):
    count = 0
    for _ in range(max_pages):
        cursor = int(store.meta("cursor"))
        page = client.request("/v1/events?after=%d&limit=100&max_bytes=4194304" % cursor)
        if not isinstance(page, dict) or page.get("profile") != store.profile or page.get("server_id") != store.meta("server_id"):
            raise LedgerError("Unexpected remote stream identity")
        nxt, events, more = page.get("cursor"), page.get("events"), page.get("more")
        if type(nxt) is not int or nxt < cursor or not isinstance(events, list) or len(events) > 100 or type(more) is not bool:
            raise LedgerError("Invalid event page")
        if (events or more) and nxt <= cursor:
            raise LedgerError("Remote stream did not advance")
        store.accept_page(events, nxt)
        count += len(events)
        if not more:
            return count
    raise LedgerError("Pull page limit reached; run sync again before uploading")


def synchronize(store, timeout=5):
    try:
        client = Client(store, timeout)
        identity(store, client)
        received = pull(store, client)  # Apply remote tombstones before sending old local work.
        sent_count = 0
        for _ in range(100):
            batch = store.pending()
            if not batch:
                break
            reply = client.request("/v1/events", {"v": 1, "profile": store.profile, "events": batch})
            if not isinstance(reply, dict) or reply.get("server_id") != store.meta("server_id") or reply.get("profile") != store.profile:
                raise LedgerError("Invalid acknowledgement identity")
            store.acknowledge(batch, reply.get("receipts"))
            sent_count += len(batch)
        received += pull(store, client)
        with store.db:
            store.set_meta("last_sync", now())
            store.set_meta("sync_error", "")
        return dict(uploaded=sent_count, downloaded=received, pending=store.status()["pending"], state="server confirmed")
    except LedgerError as e:
        with store.db:
            store.set_meta("sync_error", str(e))
        raise


def hydrate(store, topic, timeout=5):
    client = Client(store, timeout)
    identity(store, client)
    # A topic snapshot is paginated, just like the global change feed.
    cursor = 0
    snapshot, total_bytes = [], 0
    for _ in range(100):
        page = client.request("/v1/topics/%s/events?after=%d&limit=100&max_bytes=4194304" % (urllib.parse.quote(topic, safe=""), cursor))
        if not isinstance(page, dict) or page.get("profile") != store.profile or page.get("server_id") != store.meta("server_id"):
            raise LedgerError("Snapshot identity mismatch")
        events, nxt, more = page.get("events"), page.get("cursor"), page.get("more")
        if not isinstance(events, list) or len(events) > 100 or type(nxt) is not int or nxt < cursor or type(more) is not bool or any(not isinstance(e, dict) or e.get("topic") != topic for e in events):
            raise LedgerError("Invalid topic snapshot")
        from ledger import validate
        for e in events:
            validate(e, store.profile)
        if (events or more) and nxt <= cursor:
            raise LedgerError("Snapshot cursor did not advance")
        total_bytes += len(canonical(events).encode())
        if total_bytes > 64 * 1024 * 1024:
            raise LedgerError("Topic snapshot exceeds the local hydration budget")
        snapshot.extend(events)
        cursor = nxt
        if not more:
            # Apply a complete snapshot atomically; failed pages never turn an archived
            # cache into an apparently complete one.
            with store.db:
                store.db.execute("BEGIN IMMEDIATE")
                for e in sorted(snapshot, key=lambda x: x["kind"] != "delete"):
                    store._insert(e, ack=now(), check_refs=False)
                if snapshot:
                    store.db.execute("UPDATE catalog SET archived=0 WHERE topic=?", (topic,))
            return store.summary(topic)
    raise LedgerError("Snapshot limit reached; retry hydration")
