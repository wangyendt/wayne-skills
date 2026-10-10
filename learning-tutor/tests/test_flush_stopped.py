"""Explicit frozen-chat delivery; fixtures never touch personal state or OSS."""
import json
import os
import subprocess
import sys
import time
from unittest.mock import patch

from test_learning import Base, SCRIPTS
import test_learning as fixtures
from fixture_api import FixtureAPI
from capture import drain
from ledger import LedgerError
from sync import Client, configure, synchronize
import assets
import delivery


class FrozenFlushTests(Base):
    def bound(self, name="chat", key="optics/vergence"):
        store = self.store()
        path = self.root / (name + ".jsonl")
        path.write_bytes(b"")
        binding = store.start(key, "Optics", "claude", name, path)
        return store, path, binding

    def line(self, path, text, role="user"):
        with path.open("a") as f:
            f.write(json.dumps(fixtures.CaptureTests.line(self, "claude", text, role)) + "\n")

    def round(self, store, path, name="chat"):
        self.line(path, "question")
        self.line(path, "answer", "assistant")
        drain(store, "claude", name)
        self.assertTrue(delivery.complete(store, "claude", name, last_text="answer"))

    def image(self, store, binding):
        path = self.root / "image.bin"
        path.write_bytes(b"synthetic transport bytes")
        return assets.enqueue(store, "optics/vergence", path, "diagram", None, {}, binding["session"])

    def capture_row(self, store):
        return dict(store.db.execute("SELECT * FROM captures WHERE external='chat'").fetchone())

    @patch.dict(os.environ, {"LEARNING_FIXTURE_TOKEN": "fixture-token"})
    def test_text_flush_keeps_capture_closed_and_excludes_later_messages(self):
        store, path, b = self.bound()
        self.round(store, path)
        store.stop("claude", "chat")
        before = self.capture_row(store)
        self.line(path, "private after stop")
        # A late administrative event must not sneak into the frozen snapshot.
        late = store.append(b["topic"], b["session"], "checkpoint", {"next": "late", "parents": []})
        with FixtureAPI(self.root / "server") as server:
            configure(store, server.url, "LEARNING_FIXTURE_TOKEN", True)
            report = delivery.flush_stopped(store, "claude", "chat")
            self.assertEqual(report["state"], "confirmed")
            self.assertEqual(report["text"]["uploaded"], 5)
            remote = self.store("server")
            self.assertEqual(sum(e["kind"] == "message" for e in remote.events()), 2)
            self.assertNotIn(late["id"], {e["id"] for e in remote.events()})
            self.assertNotIn("private after stop", json.dumps(remote.events()))
            self.assertEqual(self.capture_row(store), before)
            again = delivery.flush_stopped(store, "claude", "chat")
            self.assertEqual(again["state"], "confirmed")
            self.assertEqual(server.posts, 1)

    def test_incomplete_turn_and_image_stay_local_without_fake_completion(self):
        store, path, b = self.bound()
        self.line(path, "unfinished")
        drain(store, "claude", "chat")
        image = self.image(store, b)
        store.stop("claude", "chat")
        before = dict(store.db.execute("SELECT * FROM delivery_turns").fetchone())
        with patch("sync.synchronize", return_value={"uploaded": 0}), patch("assets.remote") as send:
            report = delivery.flush_stopped(store, "claude", "chat")
        send.assert_not_called()
        self.assertEqual(report["state"], "partial")
        self.assertEqual(report["remaining"]["images_blocked"], [image["asset_id"]])
        self.assertEqual(dict(store.db.execute("SELECT * FROM delivery_turns").fetchone()), before)
        self.assertIsNotNone(store.db.execute("SELECT image FROM asset_jobs").fetchone()[0])

    def test_image_failure_survives_restart_and_retries_with_same_id(self):
        store, path, b = self.bound()
        self.line(path, "draw")
        drain(store, "claude", "chat")
        image = self.image(store, b)
        self.line(path, "answer", "assistant")
        drain(store, "claude", "chat")
        delivery.complete(store, "claude", "chat", last_text="answer")
        store.stop("claude", "chat")
        with patch("sync.synchronize", return_value={"uploaded": 0}), patch("assets.remote", side_effect=assets.AssetError("offline")):
            report = delivery.flush_stopped(store, "claude", "chat")
        self.assertEqual(report["state"], "failed")
        self.assertIsNotNone(store.db.execute("SELECT image FROM asset_jobs").fetchone()[0])
        reopened = self.store()
        with patch("sync.synchronize", return_value={"uploaded": 0}), patch("assets.remote", side_effect=lambda s, r, **kw: {**r["metadata"], "state": "ready", "oss_key": "fixture.png"}):
            report = delivery.flush_stopped(reopened, "claude", "chat")
        self.assertEqual(report["images"]["results"][0]["asset_id"], image["asset_id"])
        self.assertIsNone(store.db.execute("SELECT image FROM asset_jobs").fetchone()[0])
        self.assertIsNone(reopened.binding("claude", "chat"))

    @patch.dict(os.environ, {"LEARNING_FIXTURE_TOKEN": "fixture-token"})
    def test_text_ack_loss_retry_is_idempotent_while_stopped(self):
        store, path, b = self.bound()
        self.round(store, path)
        store.stop("claude", "chat")
        with FixtureAPI(self.root / "server") as server:
            configure(store, server.url, "LEARNING_FIXTURE_TOKEN", True)
            server.drop_ack = True
            self.assertEqual(delivery.flush_stopped(store, "claude", "chat")["state"], "failed")
            self.assertEqual(delivery.flush_stopped(store, "claude", "chat")["state"], "confirmed")
            self.assertEqual(sum(e["kind"] == "message" for e in self.store("server").events()), 2)

    def test_snapshot_excludes_other_chat_and_late_events_and_assets(self):
        store, path, b = self.bound()
        self.round(store, path)
        store.stop("claude", "chat")
        snapshot = delivery.stopped_snapshot(store, "claude", "chat")
        late = store.append(b["topic"], b["session"], "checkpoint", {"next": "later", "parents": []})
        other = self.root / "other.jsonl"; other.write_bytes(b"")
        store.start("optics/vergence", "Optics", "claude", "other", other)
        self.round(store, other, "other")
        self.assertNotIn(late["id"], {e["id"] for e in store.pending(scope=snapshot.scope, snapshot=snapshot)})
        self.assertEqual({e["session"] for e in store.pending(scope=snapshot.scope, snapshot=snapshot)}, {b["session"]})
        self.assertFalse(delivery.asset_allowed(store, "unknown", snapshot.scope, snapshot))
        self.assertEqual(delivery.deliver(store, "claude", "chat")["state"], "frozen")

    def test_active_and_missing_chats_are_rejected(self):
        store, path, b = self.bound()
        for name in ("chat", "missing"):
            with self.assertRaises(LedgerError):
                delivery.flush_stopped(store, "claude", name)

    def test_reopening_revokes_snapshot_before_next_network_request(self):
        store, path, b = self.bound()
        self.round(store, path)
        store.stop("claude", "chat")
        snapshot = delivery.stopped_snapshot(store, "claude", "chat")
        def request(c, p, route, body, timeout):
            self.assertEqual(route, "/v1/identity")
            store.start("optics/vergence", "Optics", "claude", "chat", path)
            return {"v": 1, "profile": store.profile, "server_id": "fixture"}
        with patch("sync.load_config", return_value={"transport": "ssh", "host": "fixture", "python": "/python", "service": "/service"}), patch("record_ssh.request", side_effect=request) as send:
            with self.assertRaises(LedgerError):
                synchronize(store, scope=snapshot.scope, snapshot=snapshot)
        self.assertEqual(send.call_count, 1)
        self.assertFalse(snapshot.valid(store, snapshot.scope))

    def test_missing_stop_boundary_is_not_assumed(self):
        store, path, b = self.bound()
        self.round(store, path)
        with store.db:
            store.db.execute("UPDATE captures SET active=0")
        with self.assertRaises(LedgerError):
            delivery.stopped_snapshot(store, "claude", "chat")

    def test_corrupt_image_receipt_keeps_bytes_and_reports_failure(self):
        store, path, b = self.bound()
        self.line(path, "draw"); drain(store, "claude", "chat")
        self.image(store, b)
        self.line(path, "answer", "assistant"); drain(store, "claude", "chat")
        delivery.complete(store, "claude", "chat", last_text="answer")
        store.stop("claude", "chat")
        with patch("sync.synchronize", return_value={"uploaded": 0}), patch("assets.remote", return_value={"state": "ready", "asset_id": "wrong"}):
            report = delivery.flush_stopped(store, "claude", "chat")
        self.assertEqual(report["state"], "failed")
        self.assertIsNotNone(store.db.execute("SELECT image FROM asset_jobs").fetchone()[0])

    def test_busy_lock_and_invalid_budget_do_not_start_delivery(self):
        store, path, b = self.bound()
        self.round(store, path); store.stop("claude", "chat")
        with delivery.upload_lock(store), patch("sync.synchronize") as send:
            self.assertEqual(delivery.flush_stopped(store, "claude", "chat")["state"], "busy")
            send.assert_not_called()
        for budget in (0, -1, 601, float("nan")):
            with self.assertRaises(LedgerError):
                delivery.flush_stopped(store, "claude", "chat", budget)

    @patch.dict(os.environ, {"LEARNING_FIXTURE_TOKEN": "fixture-token"})
    def test_cli_flush_and_second_invocation_never_open_recording(self):
        store, path, b = self.bound()
        self.round(store, path); store.stop("claude", "chat")
        with FixtureAPI(self.root / "server") as server:
            configure(store, server.url, "LEARNING_FIXTURE_TOKEN", True)
            cmd = [sys.executable, str(SCRIPTS / "learn.py"), "--home", str(store.home), "flush", "--host", "claude", "--host-session", "chat"]
            for _ in range(2):
                result = subprocess.run(cmd, text=True, capture_output=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)["state"], "confirmed")
            self.assertEqual(server.posts, 1)
            self.assertIsNone(store.binding("claude", "chat"))

    @patch.dict(os.environ, {"LEARNING_FIXTURE_TOKEN": "fixture-token"})
    def test_all_closed_runs_of_same_chat_flush_with_original_ids(self):
        store, path, b = self.bound()
        self.round(store, path); store.stop("claude", "chat")
        store.start("optics/vergence", "Optics", "claude", "chat", path)
        self.round(store, path); store.stop("claude", "chat")
        with FixtureAPI(self.root / "server") as server:
            configure(store, server.url, "LEARNING_FIXTURE_TOKEN", True)
            self.assertEqual(delivery.flush_stopped(store, "claude", "chat")["state"], "confirmed")
            remote = self.store("server")
            self.assertEqual(sum(e["kind"] == "message" for e in remote.events()), 4)
            self.assertIsNone(store.binding("claude", "chat"))

    @patch.dict(os.environ, {"LEARNING_FIXTURE_TOKEN": "fixture-token"})
    def test_shared_topic_creation_is_borrowed_without_owner_chat_messages(self):
        store, owner, b = self.bound("owner")
        self.round(store, owner, "owner")
        target = self.root / "target.jsonl"; target.write_bytes(b"")
        store.start("optics/vergence", "Optics", "claude", "target", target)
        self.round(store, target, "target"); store.stop("claude", "target")
        with FixtureAPI(self.root / "server") as server:
            configure(store, server.url, "LEARNING_FIXTURE_TOKEN", True)
            self.assertEqual(delivery.flush_stopped(store, "claude", "target")["state"], "confirmed")
            remote = self.store("server")
            self.assertEqual(sum(e["kind"] == "topic" for e in remote.events()), 1)
            self.assertEqual(sum(e["kind"] == "message" for e in remote.events()), 2)
            self.assertFalse(any(e["session"] == b["session"] and e["kind"] != "topic" for e in remote.events()))

    def test_expired_foreground_budget_starts_no_network_request(self):
        store, path, b = self.bound()
        self.round(store, path); store.stop("claude", "chat")
        snapshot = delivery.stopped_snapshot(store, "claude", "chat")
        with patch("sync.load_config", return_value={"transport": "ssh", "host": "fixture", "python": "/python", "service": "/service"}), patch("record_ssh.request") as send:
            client = Client(store, timeout=60, scope=snapshot.scope, snapshot=snapshot, deadline=time.monotonic()-1)
            with self.assertRaises(LedgerError):
                client.request("/v1/identity")
            send.assert_not_called()
