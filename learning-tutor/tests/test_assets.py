import base64
import copy
import hashlib
import json
import subprocess
import uuid
from unittest.mock import patch

from test_learning import Base
from asset_common import AssetError, decode_image, metadata, object_key, topic_id
import assets


class ImageOutboxTests(Base):
    def picture(self):
        # Transport tests use opaque fixture bytes; server separately validates image codecs.
        path = self.root / "fixture.bin"
        path.write_bytes(b"synthetic-image-transport-fixture")
        return path

    def queue(self, store):
        return assets.enqueue(store, "optics/vergence", self.picture(), "Vergence geometry", "Two rays meeting", {"kind": "synthetic-test"})

    @staticmethod
    def receipt(request):
        return {**request["metadata"], "state": "ready", "oss_key": "learning-tutor/assets/fixture.png"}

    def test_offline_bytes_survive_restart_then_ack_clears_bytes(self):
        store = self.store()
        queued = self.queue(store)
        result = assets.flush(store)
        self.assertEqual(result["status"]["jobs"], {"pending": 1})
        self.assertIsNotNone(store.db.execute("SELECT image FROM asset_jobs").fetchone()[0])
        # Separate SQLite connection sees the committed queue.
        from ledger import Ledger
        reopened = Ledger(store.home)
        try:
            with patch("assets.remote", side_effect=lambda s, r: self.receipt(r)):
                result = assets.flush(reopened)
            self.assertEqual(result["results"][0]["asset_id"], queued["asset_id"])
            self.assertEqual(result["status"]["jobs"], {"ready": 1})
            self.assertIsNone(reopened.db.execute("SELECT image FROM asset_jobs").fetchone()[0])
        finally:
            reopened.close()

    def test_ack_loss_reuses_asset_identity_and_bytes(self):
        store = self.store()
        self.queue(store)
        requests = []
        def send(s, request):
            requests.append(copy.deepcopy(request))
            if len(requests) == 1:
                raise AssetError("ACK lost")
            return self.receipt(request)
        with patch("assets.remote", side_effect=send):
            assets.flush(store)
            assets.flush(store)
        self.assertEqual(requests[0], requests[1])

    def test_bad_receipt_never_discards_local_image(self):
        store = self.store()
        self.queue(store)
        for field, value in (("asset_id", str(uuid.uuid4())), ("sha256", "0" * 64), ("topic_id", str(uuid.uuid4())), ("state", "pending")):
            with patch("assets.remote", side_effect=lambda s, r: {**self.receipt(r), field: value}):
                assets.flush(store)
            self.assertEqual(assets.status(store)["jobs"], {"pending": 1})
            self.assertIsNotNone(store.db.execute("SELECT image FROM asset_jobs").fetchone()[0])

    def test_delete_racing_upload_is_not_replaced_by_upload_ack(self):
        store = self.store()
        queued = self.queue(store)
        def send(s, request):
            assets.queue_delete(store, queued["asset_id"])
            return self.receipt(request)
        with patch("assets.remote", side_effect=send):
            assets.flush(store)
        self.assertEqual(assets.status(store)["jobs"], {"delete-pending": 1})
        with patch("assets.remote", return_value={"asset_id": queued["asset_id"], "state": "deleted"}):
            assets.flush(store)
        self.assertEqual(assets.status(store)["jobs"], {"deleted": 1})

    def test_deleted_topic_converts_queued_upload_to_deletion(self):
        store = self.store()
        queued = self.queue(store)
        topic = store.topic_id("optics/vergence")
        store.append(topic, "delete", "delete", {})
        with patch("assets.remote") as send:
            assets.flush(store)
            send.assert_not_called()
        self.assertEqual(assets.status(store)["jobs"], {"delete-pending": 1})
        self.assertIsNone(store.db.execute("SELECT image FROM asset_jobs WHERE id=?", (queued["asset_id"],)).fetchone()[0])

    def test_metadata_rejects_wrong_topic_hash_and_nonfinite_json(self):
        store = self.store()
        self.queue(store)
        m = json.loads(store.db.execute("SELECT request FROM asset_jobs").fetchone()[0])["metadata"]
        self.assertEqual(metadata(m), m)
        for field, value in (("topic_id", str(uuid.uuid4())), ("sha256", "bad"), ("session_id", "../"), ("caption", None), ("provenance", {"x": float("nan")})):
            with self.assertRaises(AssetError):
                metadata({**m, field: value})

    def test_safe_key_is_generated_not_taken_from_filename(self):
        aid = str(uuid.uuid4())
        tid = topic_id("learner/中文", "optics/vergence")
        key = object_key("learning-tutor/", "learner/中文", tid, aid, "png")
        self.assertTrue(key.startswith("learning-tutor/assets/"))
        self.assertNotIn("中文", key)
        for prefix in ("/", "../", "a/../", "a//"):
            with self.assertRaises(AssetError):
                object_key(prefix, "personal", tid, aid, "png")

    def test_download_checks_hash_and_never_overwrites(self):
        store = self.store()
        aid = str(uuid.uuid4())
        data = b"synthetic download"
        response = {"asset_id": aid, "profile": store.profile, "state": "ready", "sha256": hashlib.sha256(data).hexdigest(), "bytes_b64": base64.b64encode(data).decode()}
        path = self.root / "download.png"
        with patch("assets.remote", side_effect=lambda *a: dict(response)):
            assets.download(store, aid, path)
            with self.assertRaises(FileExistsError):
                assets.download(store, aid, path)
        self.assertEqual(path.read_bytes(), data)
        with self.assertRaises(AssetError):
            decode_image(response["bytes_b64"], "0" * 64)

    def test_config_rejects_ssh_option_injection(self):
        store = self.store()
        with self.assertRaises(AssetError):
            assets.configure(store, "-oProxyCommand=bad", "/python", "/service")
        with self.assertRaises(AssetError):
            assets.configure(store, "HOST", "relative", "/service")
        result = assets.configure(store, "user@HOST", "/python path/python", "/service path/app.py")
        self.assertEqual(result["host"], "user@HOST")

    def test_transport_does_not_echo_remote_errors(self):
        store = self.store()
        assets.configure(store, "HOST", "/python", "/service")
        result = subprocess.CompletedProcess([], 2, b'{"ok": false, "error":"secret fixture"}', b"secret fixture")
        with patch("assets.subprocess.run", return_value=result):
            with self.assertRaises(AssetError) as error:
                assets.remote(store, {"action": "get"})
        self.assertNotIn("secret fixture", str(error.exception))
