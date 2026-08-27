#!/usr/bin/env python3
"""Single-user SSH stdin/stdout image service; no listener or public endpoint.

Deploy beside ../asset_common.py. Only this server reads OSS/DB credentials.
"""
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import warnings

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from asset_common import AssetError, MAX_IMAGE, MAX_WIRE, canonical, decode_image, identity, metadata, object_key


def inspect_image(data):
    from PIL import Image
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(io.BytesIO(data)) as im:
            formats = {"PNG": ("image/png", "png"), "JPEG": ("image/jpeg", "jpg"), "WEBP": ("image/webp", "webp")}
            if im.format not in formats or getattr(im, "n_frames", 1) != 1 or im.width * im.height > 32_000_000:
                raise AssetError("Use a static PNG/JPEG/WebP image within 32 megapixels")
            mime, ext = formats[im.format]
            width, height = im.size
            im.verify()
        with Image.open(io.BytesIO(data)) as im:
            im.load()
    return {"mime_type": mime, "extension": ext, "width": width, "height": height, "byte_size": len(data)}


def public_row(row):
    return {k: str(v) if k in {"asset_id", "topic_id", "session_id", "created_at", "updated_at"} and v is not None else v
            for k, v in row.items() if k != "payload_hash"}


class Service:
    def __init__(self, config_dir=None):
        import oss2
        import psycopg
        from psycopg.rows import dict_row
        root = Path(config_dir or Path.home() / ".config/learning-tutor")
        configs = []
        for name in ("oss.json", "database.json"):
            path = root / name
            if path.is_symlink() or (os.name != "nt" and path.stat().st_mode & 0o077):
                raise AssetError("Server credentials require private regular files (0600)")
            configs.append(json.loads(path.read_text(encoding="utf-8")))
        c, db = configs
        self.profile = db.pop("profile")
        self.prefix, self.bucket_name = c["prefix"], c["bucket"]
        self.bucket = oss2.Bucket(oss2.Auth(c["access_key_id"], c["access_key_secret"]), c["endpoint"], c["bucket"], connect_timeout=15)
        self.db = psycopg.connect(**db, autocommit=True, row_factory=dict_row,
                                  connect_timeout=8, options="-c statement_timeout=60000 -c lock_timeout=10000")

    def close(self):
        self.db.close()

    def upload(self, request):
        from psycopg.types.json import Jsonb
        import oss2
        m = metadata(request.get("metadata"))
        if m["profile"] != self.profile:
            raise AssetError("Learner profile mismatch")
        if self.db.execute("SELECT 1 FROM learning.asset_tombstones WHERE asset_id=%s", (m["asset_id"],)).fetchone():
            raise AssetError("Asset was deleted; it will not be resurrected")
        data = decode_image(request.get("bytes_b64"), m["sha256"])
        facts = inspect_image(data)
        key = object_key(self.prefix, self.profile, m["topic_id"], m["asset_id"], facts.pop("extension"))
        payload_hash = hashlib.sha256(canonical(m).encode()).hexdigest()
        values = {**m, **facts, "payload_hash": payload_hash, "bucket": self.bucket_name, "oss_key": key}
        values["provenance"] = Jsonb(values["provenance"])
        # Durable reservation before OSS I/O. Crashes leave an idempotently retryable row.
        self.db.execute("""INSERT INTO learning.assets
            (asset_id,profile,topic_id,topic_key,session_id,caption,alt_text,provenance,sha256,mime_type,width,height,byte_size,payload_hash,bucket,oss_key)
            VALUES (%(asset_id)s,%(profile)s,%(topic_id)s,%(topic_key)s,%(session_id)s,%(caption)s,%(alt_text)s,%(provenance)s,%(sha256)s,%(mime_type)s,%(width)s,%(height)s,%(byte_size)s,%(payload_hash)s,%(bucket)s,%(oss_key)s)
            ON CONFLICT(asset_id) DO NOTHING""", values)
        with self.db.transaction():
            row = self._row(m["asset_id"], lock=True)
            if row["payload_hash"] != payload_hash or row["oss_key"] != key:
                raise AssetError("Asset identity/content conflict")
            if row["state"] == "deleted":
                raise AssetError("Asset was deleted; it will not be resurrected")
            if row["state"] == "ready":
                return public_row(row)
            try:
                head = self.bucket.head_object(key)
            except oss2.exceptions.NoSuchKey:
                head = None
            if head is None:
                self.bucket.put_object(key, data, headers={
                    "Content-Type": facts["mime_type"], "x-oss-object-acl": "private",
                    "x-oss-forbid-overwrite": "true", "x-oss-meta-sha256": m["sha256"]})
                head = self.bucket.head_object(key)
            if head.content_length != len(data) or head.headers.get("x-oss-meta-sha256") != m["sha256"]:
                raise AssetError("Stored object does not match reservation; not overwritten")
            if self.bucket.get_object_acl(key).acl != "private":
                raise AssetError("Stored object ACL is not private")
            # Verify bytes, not only an uploader-supplied hash in an OSS header.
            if hashlib.sha256(self._bytes(key)).hexdigest() != m["sha256"]:
                raise AssetError("OSS read-back hash mismatch")
            row = self.db.execute("""UPDATE learning.assets SET state='ready',etag=%s,version_id=%s,updated_at=now()
                WHERE asset_id=%s RETURNING *""", (head.etag, head.headers.get("x-oss-version-id"), m["asset_id"])).fetchone()
        return public_row(row)  # Returned only after the transaction commits.

    def _row(self, asset_id, lock=False):
        row = self.db.execute("SELECT * FROM learning.assets WHERE asset_id=%s AND profile=%s" + (" FOR UPDATE" if lock else ""),
                              (identity(asset_id), self.profile)).fetchone()
        if not row:
            raise AssetError("Asset not found")
        if row["bucket"] != self.bucket_name or not row["oss_key"].startswith(self.prefix + "assets/"):
            raise AssetError("Asset is outside this storage configuration")
        return row

    def _bytes(self, key, version=None):
        result = self.bucket.get_object(key, params={"versionId": version} if version else None)
        try:
            data = result.read(MAX_IMAGE + 1)
        finally:
            result.resp.response.close()
        if len(data) > MAX_IMAGE:
            raise AssetError("Stored image exceeds size limit")
        return data

    def handle(self, request):
        if not isinstance(request, dict) or request.get("profile") != self.profile:
            raise AssetError("Learner profile mismatch")
        action = request.get("action")
        asset_id = metadata(request.get("metadata"))["asset_id"] if action == "upload" else request.get("asset_id")
        if action in {"upload", "delete"}:
            # Session lock spans the durable reservation and the OSS/DB commit.
            # It also serializes deletion of an ID whose upload has not arrived yet.
            lock_key = self.profile + ":" + identity(asset_id)
            self.db.execute("SELECT pg_advisory_lock(hashtextextended(%s,0))", (lock_key,))
            try:
                return self._handle(request)
            finally:
                self.db.execute("SELECT pg_advisory_unlock(hashtextextended(%s,0))", (lock_key,))
        return self._handle(request)

    def _handle(self, request):
        action = request.get("action")
        if action == "upload":
            return self.upload(request)
        if action == "list":
            topic = identity(request.get("topic_id"))
            after = request.get("after", "00000000-0000-0000-0000-000000000000")
            rows = self.db.execute("""SELECT * FROM learning.assets WHERE profile=%s AND topic_id=%s
                AND state <> 'deleted' AND asset_id>%s ORDER BY asset_id LIMIT 101""", (self.profile, topic, identity(after))).fetchall()
            return {"items": [public_row(r) for r in rows[:100]], "more": len(rows) > 100,
                    "after": str(rows[99]["asset_id"]) if len(rows) > 100 else None}
        if action not in {"get", "download", "delete"}:
            raise AssetError("Unknown image operation")
        with self.db.transaction():
            if action == "delete":
                self.db.execute("INSERT INTO learning.asset_tombstones(asset_id,profile) VALUES(%s,%s) ON CONFLICT DO NOTHING",
                                (identity(request.get("asset_id")), self.profile))
                if not self.db.execute("SELECT 1 FROM learning.assets WHERE asset_id=%s AND profile=%s", (request["asset_id"], self.profile)).fetchone():
                    return {"asset_id": request["asset_id"], "state": "deleted"}
            row = self._row(request.get("asset_id"), lock=True)
            if action == "delete":
                if row["state"] != "deleted":
                    # An interrupted upload may already have an OSS version; discover it.
                    import oss2
                    version = row["version_id"]
                    try:
                        head = self.bucket.head_object(row["oss_key"])
                        if head.headers.get("x-oss-meta-sha256") != row["sha256"]:
                            raise AssetError("Delete target hash metadata mismatch")
                        version = version or head.headers.get("x-oss-version-id")
                    except oss2.exceptions.NoSuchKey:
                        pass
                    self.bucket.delete_object(row["oss_key"], params={"versionId": version} if version else None)
                    self.db.execute("""UPDATE learning.assets SET state='deleted',caption='',alt_text='',provenance='{}',
                        topic_key='',session_id=NULL,updated_at=now() WHERE asset_id=%s""", (row["asset_id"],))
                return {"asset_id": str(row["asset_id"]), "state": "deleted"}
            if row["state"] != "ready":
                raise AssetError("Image is not ready")
            result = public_row(row)
            if action == "download":
                data = self._bytes(row["oss_key"], row["version_id"])
                if hashlib.sha256(data).hexdigest() != row["sha256"]:
                    raise AssetError("Stored image hash mismatch")
                result["bytes_b64"] = base64.b64encode(data).decode("ascii")
            return result


def main():
    service = None
    try:
        raw = sys.stdin.buffer.read(MAX_WIRE + 1)
        if len(raw) > MAX_WIRE:
            raise AssetError("Request exceeds size limit")
        request = json.loads(raw)
        service = Service(os.environ.get("LEARNING_ASSET_CONFIG"))
        print(canonical({"ok": True, "result": service.handle(request)}))
        return 0
    except Exception as e:
        # SDK and database exceptions can contain credentials, SQL values or response bodies.
        safe = str(e) if isinstance(e, AssetError) else type(e).__name__
        print(canonical({"ok": False, "error": safe}))
        return 2
    finally:
        if service:
            service.close()


if __name__ == "__main__":
    sys.exit(main())
