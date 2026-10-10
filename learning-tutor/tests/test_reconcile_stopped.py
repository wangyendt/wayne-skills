import copy
import json
from unittest.mock import patch

from test_learning import Base
import test_learning as fixtures
from ledger import LedgerError, now
from capture import drain
from delivery import stopped_snapshot, event_complete, upload_lock
from reconcile import epoch, reconcile_stopped
import assets


class StoppedRecoveryTests(Base):
    def fixture(self):
        store = self.store()
        path = self.root / "codex.jsonl"; path.write_bytes(b"")
        b = store.start("optics/vergence", "Optics", "codex", "chat", path)
        start = epoch(now())
        path.write_text(json.dumps(fixtures.CaptureTests.line(self, "codex", "aborted old question")) + "\n")
        drain(store, "codex", "chat")
        old = [e for e in store.events() if e["kind"] == "message"][0]
        image_path = self.root / "image.bin"; image_path.write_bytes(b"fixture bytes")
        image = assets.enqueue(store, "optics/vergence", image_path, "diagram", None, {}, b["session"])
        checkpoint = store.append(b["topic"], b["session"], "checkpoint", {"next": "read diagram", "parents": []})
        end = epoch(now())
        store.stop("codex", "chat")
        packet = {"source": "codex_app.read_thread", "threadId": "chat", "turn": {
            "id": "recovered-native", "status": "completed", "error": None, "startedAt": start, "completedAt": end,
            "items": [{"type": "userMessage", "id": "native-user", "content": [{"type": "text", "text": "new question"}]},
                      {"type": "agentMessage", "id": "native-final", "phase": "final_answer", "text": "completed final"},
                      {"type": "commandExecution", "id": "enqueue-tool", "status": "completed", "exitCode": 0,
                       "output": {"truncated": False, "text": json.dumps(image)}}]},
            "assets": [{"asset_id": image["asset_id"], "host_item_id": "enqueue-tool"}]}
        return store, b, old, image, checkpoint, packet

    def test_verified_missing_turn_recovered_without_rewriting_aborted_turn(self):
        store, b, old, image, cp, packet = self.fixture()
        before = dict(store.db.execute("SELECT * FROM captures").fetchone())
        with patch("assets.remote") as send:
            receipt = reconcile_stopped(store, "codex", "chat", packet)
        send.assert_not_called()
        self.assertFalse(event_complete(store, old["id"]))
        self.assertTrue(event_complete(store, receipt["turn"]))
        self.assertTrue(event_complete(store, cp["id"]))
        snapshot = stopped_snapshot(store, "codex", "chat")
        self.assertTrue(set(receipt["events"]) <= snapshot.events)
        self.assertTrue(__import__("delivery").asset_allowed(store, image["asset_id"], snapshot.scope, snapshot))
        self.assertEqual(dict(store.db.execute("SELECT * FROM captures").fetchone()), before)

    def test_recovery_is_idempotent_and_evidence_cannot_change(self):
        store, b, old, image, cp, packet = self.fixture()
        reconcile_stopped(store, "codex", "chat", packet)
        count = len(store.events())
        self.assertEqual(reconcile_stopped(store, "codex", "chat", packet)["state"], "already reconciled")
        self.assertEqual(len(store.events()), count)
        changed = copy.deepcopy(packet); changed["turn"]["items"][1]["text"] = "different final"
        with self.assertRaises(LedgerError):
            reconcile_stopped(store, "codex", "chat", changed)

    def test_failed_or_post_stop_or_wrong_thread_reads_do_not_mutate_ledger(self):
        store, b, old, image, cp, packet = self.fixture()
        variants = []
        for field, value in (("status", "interrupted"), ("error", "API failure"), ("completedAt", epoch(now()) + 600)):
            p = copy.deepcopy(packet); p["turn"][field] = value; variants.append(p)
        p = copy.deepcopy(packet); p["threadId"] = "other"; variants.append(p)
        p = copy.deepcopy(packet); p["turn"]["items"][1]["phase"] = "commentary"; variants.append(p)
        before = store.events()
        for p in variants:
            with self.assertRaises(LedgerError):
                reconcile_stopped(store, "codex", "chat", p)
            self.assertEqual(store.events(), before)
            self.assertIsNone(store.binding("codex", "chat"))

    def test_unproven_asset_id_or_truncated_tool_output_is_rejected(self):
        store, b, old, image, cp, packet = self.fixture()
        for truncated in (True, None):
            p = copy.deepcopy(packet); p["turn"]["items"][2]["output"]["truncated"] = truncated
            with self.assertRaises(LedgerError):
                reconcile_stopped(store, "codex", "chat", p)
        p = copy.deepcopy(packet); p["assets"][0]["asset_id"] = "unrelated"
        with self.assertRaises(LedgerError):
            reconcile_stopped(store, "codex", "chat", p)
        self.assertFalse(event_complete(store, old["id"]))

    def test_recovery_rejects_active_chat_and_control_commands(self):
        store, b, old, image, cp, packet = self.fixture()
        p = copy.deepcopy(packet); p["turn"]["items"][0]["content"][0]["text"] = "/learn-stop"
        with self.assertRaises(LedgerError):
            reconcile_stopped(store, "codex", "chat", p)
        path = self.root / "new.jsonl"; path.write_bytes(b"")
        store.start("optics/vergence", "Optics", "codex", "chat", path)
        with self.assertRaises(LedgerError):
            reconcile_stopped(store, "codex", "chat", packet)

    def test_late_checkpoint_is_not_in_recovered_snapshot(self):
        store, b, old, image, cp, packet = self.fixture()
        late = store.append(b["topic"], b["session"], "checkpoint", {"next": "private later", "parents": []})
        reconcile_stopped(store, "codex", "chat", packet)
        snapshot = stopped_snapshot(store, "codex", "chat")
        self.assertNotIn(late["id"], snapshot.events)

    def test_parallel_upload_or_recovery_blocks_offline_mutation(self):
        store, b, old, image, cp, packet = self.fixture()
        before = store.events()
        with upload_lock(store), self.assertRaises(LedgerError):
            reconcile_stopped(store, "codex", "chat", packet)
        self.assertEqual(store.events(), before)
