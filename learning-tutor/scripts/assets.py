#!/usr/bin/env python3
"""Private image outbox + SSH transport. Client needs only Python 3.9 and OpenSSH."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import uuid

from asset_common import AssetError, MAX_IMAGE, MAX_WIRE, canonical, decode_image, identity, metadata
from ledger import Ledger, LedgerError, now


def initialize(store):
    store.db.execute("""CREATE TABLE IF NOT EXISTS asset_jobs(
        id TEXT PRIMARY KEY,topic TEXT NOT NULL,request TEXT NOT NULL,image BLOB,
        state TEXT NOT NULL,receipt TEXT,error TEXT,created TEXT NOT NULL)""")
    store.db.commit()


def status(store):
    exists = store.db.execute("SELECT 1 FROM sqlite_master WHERE name='asset_jobs'").fetchone()
    counts = dict(store.db.execute("SELECT state,count(*) FROM asset_jobs GROUP BY state").fetchall()) if exists else {}
    return {"configured": bool(store.meta("asset_ssh")), "jobs": counts,
            "note": "Image outbox is separate from text event sync; pending bytes remain in local SQLite."}


def configure(store, host, python, service):
    if not re.fullmatch(r"[a-zA-Z0-9_][a-zA-Z0-9_.@-]{0,199}", host):
        raise AssetError("Use an SSH config alias or user@hostname")
    for path in (python, service):
        if not path.startswith("/") or any(c in path for c in "\r\n\x00"):
            raise AssetError("Remote Python and service require absolute POSIX paths")
    config = {"host": host, "python": python, "service": service}
    with store.db:
        store.set_meta("asset_ssh", canonical(config))
    return {"configured": True, "transport": "SSH; existing authentication/known_hosts required", **config}


def remote(store, request):
    config = store.meta("asset_ssh")
    if not config:
        raise AssetError("Image server is not configured; image remains queued locally")
    c = json.loads(config)
    command = shlex.quote(c["python"]) + " " + shlex.quote(c["service"])
    try:
        p = subprocess.run(["ssh", "-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
                            "-o", "ConnectTimeout=8", c["host"], command],
                           input=canonical({**request, "profile": store.profile}).encode(),
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90)
    except (OSError, subprocess.TimeoutExpired):
        raise AssetError("Image server connection failed; check SSH/network, then retry") from None
    if len(p.stdout) > MAX_WIRE:
        raise AssetError("Image server response exceeds size limit")
    try:
        result = json.loads(p.stdout)
    except (ValueError, UnicodeError):
        raise AssetError("Image server returned an invalid response; check SSH/server") from None
    if not isinstance(result, dict) or result.get("ok") is not True or p.returncode:
        # No untrusted remote stderr or response body in diagnostics.
        raise AssetError("Image server operation failed; check service credentials/permissions and input")
    if "result" not in result:
        raise AssetError("Image server omitted its receipt")
    return result["result"]


def enqueue(store, key, path, caption, alt_text, provenance, session=None):
    initialize(store)
    topic = store.topic_id(key)
    if store.db.execute("SELECT 1 FROM tombstones WHERE topic=?", (topic,)).fetchone():
        raise AssetError("Topic was deleted")
    with Path(path).expanduser().open("rb") as f:
        data = f.read(MAX_IMAGE + 1)
    if not data or len(data) > MAX_IMAGE:
        raise AssetError("Image must be nonempty and at most 25 MiB")
    m = metadata({"asset_id": str(uuid.uuid4()), "profile": store.profile, "topic_id": topic,
                  "topic_key": key, "session_id": session, "caption": caption, "alt_text": alt_text or caption,
                  "provenance": provenance, "sha256": hashlib.sha256(data).hexdigest()})
    with store.db:
        store.db.execute("INSERT INTO asset_jobs VALUES(?,?,?,?,?,NULL,NULL,?)",
                         (m["asset_id"], topic, canonical({"action": "upload", "metadata": m}), data, "pending", now()))
    return {"asset_id": m["asset_id"], "state": "local-pending", "sha256": m["sha256"]}


def flush(store, limit=1):
    initialize(store)
    results = []
    for job in store.db.execute("SELECT * FROM asset_jobs WHERE state IN ('pending','delete-pending') ORDER BY created,id LIMIT ?", (limit,)).fetchall():
        request = json.loads(job["request"])
        if request["action"] == "upload" and store.db.execute("SELECT 1 FROM tombstones WHERE topic=?", (job["topic"],)).fetchone():
            # Do not upload bytes after local topic deletion. If a prior ACK was lost,
            # an object may already exist: send an explicit asset delete instead.
            queue_delete(store, job["id"])
            continue
        if request["action"] == "upload":
            request["bytes_b64"] = base64.b64encode(job["image"]).decode("ascii")
        try:
            receipt = remote(store, request)
            expected = "ready" if request["action"] == "upload" else "deleted"
            if not isinstance(receipt, dict) or receipt.get("asset_id") != job["id"] or receipt.get("state") != expected:
                raise AssetError("Image receipt does not match this operation")
            if expected == "ready":
                m = request["metadata"]
                if (receipt.get("sha256") != m["sha256"] or receipt.get("profile") != store.profile
                        or receipt.get("topic_id") != job["topic"] or not receipt.get("oss_key")):
                    raise AssetError("Image receipt identity/hash mismatch")
            # If another process queued deletion while upload ran, never replace it.
            with store.db:
                store.db.execute("UPDATE asset_jobs SET state=?,receipt=?,image=NULL,error=NULL WHERE id=? AND state=? AND request=?",
                                 (expected, canonical(receipt), job["id"], job["state"], job["request"]))
            results.append(receipt)
        except AssetError as e:
            with store.db:
                store.db.execute("UPDATE asset_jobs SET error=? WHERE id=?", (str(e), job["id"]))
            results.append({"asset_id": job["id"], "state": job["state"], "error": str(e)})
            break
    return {"results": results, "status": status(store)}


def queue_delete(store, asset_id):
    initialize(store)
    identity(asset_id)
    request = canonical({"action": "delete", "asset_id": asset_id})
    with store.db:
        store.db.execute("""INSERT INTO asset_jobs VALUES(?, '', ?, NULL, 'delete-pending', NULL, NULL, ?)
            ON CONFLICT(id) DO UPDATE SET request=excluded.request,state='delete-pending',image=NULL,error=NULL""", (asset_id, request, now()))


def download(store, asset_id, destination):
    identity(asset_id)
    result = remote(store, {"action": "download", "asset_id": asset_id})
    if not isinstance(result, dict) or result.get("asset_id") != asset_id or result.get("profile") != store.profile or result.get("state") != "ready":
        raise AssetError("Image download identity mismatch")
    data = decode_image(result.pop("bytes_b64", None), result.get("sha256"))
    target = Path(destination).expanduser().resolve()
    fd = os.open(str(target), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    return {"file": str(target), "asset": result}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--home")
    p.add_argument("--profile", default="personal")
    sub = p.add_subparsers(dest="command", required=True)
    a = sub.add_parser("configure")
    a.add_argument("--ssh", required=True)
    a.add_argument("--python", required=True)
    a.add_argument("--service", required=True)
    sub.add_parser("status")
    sub.add_parser("retry")
    a = sub.add_parser("upload")
    a.add_argument("key")
    a.add_argument("file")
    a.add_argument("--caption", required=True)
    a.add_argument("--alt-text")
    a.add_argument("--session")
    a.add_argument("--provenance", help="JSON file: tool, model, prompt, source URLs; no credentials")
    a = sub.add_parser("list")
    a.add_argument("key")
    a.add_argument("--after")
    for name in ("get", "download", "delete"):
        a = sub.add_parser(name)
        a.add_argument("asset_id")
        if name == "download":
            a.add_argument("--output", required=True)
        if name == "delete":
            a.add_argument("--confirm-id", required=True)
    return p


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    args = parser().parse_args()
    store = None
    try:
        store = Ledger(args.home, args.profile)
        if args.command == "configure":
            result = configure(store, args.ssh, args.python, args.service)
        elif args.command == "status":
            result = status(store)
        elif args.command == "retry":
            result = flush(store, 5)
        elif args.command == "upload":
            provenance = json.loads(Path(args.provenance).read_text(encoding="utf-8")) if args.provenance else {}
            queued = enqueue(store, args.key, args.file, args.caption, args.alt_text, provenance, args.session)
            result = {"queued": queued, "upload": flush(store, 5)}
        elif args.command == "download":
            result = download(store, args.asset_id, args.output)
        elif args.command == "delete":
            if args.confirm_id != args.asset_id:
                raise AssetError("Deletion confirmation does not match")
            queue_delete(store, args.asset_id)
            result = flush(store, 5)
        elif args.command == "list":
            request = {"action": "list", "topic_id": store.topic_id(args.key)}
            if args.after:
                request["after"] = identity(args.after)
            result = remote(store, request)
        else:
            result = remote(store, {"action": "get", "asset_id": identity(args.asset_id)})
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (AssetError, LedgerError, OSError, ValueError, __import__("sqlite3").Error) as e:
        print("learning-assets: " + (str(e) if isinstance(e, (AssetError, LedgerError)) else type(e).__name__), file=sys.stderr)
        return 2
    finally:
        if store:
            store.close()


if __name__ == "__main__":
    sys.exit(main())
