import json
import os
from pathlib import Path
import subprocess
import sys
from contextlib import nullcontext
from unittest.mock import patch

from test_learning import Base
import test_learning as fixtures
from capture import drain, hook
from delivery import complete, deliver, event_complete, notice, upload_lock
from fixture_api import FixtureAPI
from sync import configure, synchronize
from ledger import LedgerError
from learn import install_hooks
import assets


class EventDeliveryTests(Base):
    def bound(self, host="claude", name="chat", key="optics/vergence"):
        store = self.store(name)
        path = self.root / (name + ".jsonl")
        path.write_bytes(b"")
        b = store.start(key, "Optics", host, name, path)
        return store, path, b

    def append(self, path, host, text, role="user", **fields):
        record = fixtures.CaptureTests.line(self, host, text, role)
        record.update(fields)
        with path.open("a") as f:
            f.write(json.dumps(record) + "\n")

    def round(self, store, path, host="claude", name="chat", text="answer"):
        self.append(path, host, "question")
        self.append(path, host, text, "assistant")
        drain(store, host, name)
        self.assertTrue(complete(store, host, name, last_text=text))

    def test_incomplete_local_not_uploaded_or_assessed(self):
        a, path, b = self.bound()
        self.append(path, "claude", "unfinished question")
        drain(a, "claude", "chat")
        message = [e for e in a.events() if e["kind"] == "message"][0]
        self.assertFalse(event_complete(a, message["id"]))
        self.assertNotIn(message["id"], {e["id"] for e in a.pending()})
        with self.assertRaises(LedgerError):
            self.assessment(a, b, message)
        a.stop("claude", "chat")
        self.assertEqual(a.status()["delivery"]["turns"], {"incomplete": 1})

    def test_stop_proof_waits_for_delayed_final_text(self):
        a, path, b = self.bound()
        self.append(path, "claude", "question")
        self.append(path, "claude", "tool commentary", "assistant")
        drain(a, "claude", "chat")
        self.assertFalse(complete(a, "claude", "chat", last_text="final answer"))
        self.assertFalse(any(e["kind"] == "message" for e in a.pending()))
        self.append(path, "claude", "final answer", "assistant")
        drain(a, "claude", "chat")
        self.assertEqual(sum(e["kind"] == "message" for e in a.pending()), 3)

    def test_malformed_source_rolls_back_turn_gates_as_well(self):
        a, path, b = self.bound()
        self.append(path, "claude", "question")
        with path.open("a") as f:
            f.write("broken\n")
        with self.assertRaises(LedgerError):
            drain(a, "claude", "chat")
        self.assertEqual(a.db.execute("SELECT count(*) FROM delivery_turns").fetchone()[0], 0)
        self.assertEqual(a.binding("claude", "chat")["offset"], 0)

    @patch.dict(os.environ, {"LEARNING_FIXTURE_TOKEN": "fixture-token"})
    def test_stop_freezes_restart_thaws_only_same_chat_and_reuses_ids(self):
        a, path, b = self.bound()
        self.round(a, path)
        original = {e["id"] for e in a.events() if e["kind"] == "message"}
        a.stop("claude", "chat")
        with FixtureAPI(self.root / "server") as server:
            configure(a, server.url, "LEARNING_FIXTURE_TOKEN", True)
            self.assertEqual(deliver(a, "claude", "chat")["state"], "frozen")
            self.assertEqual(server.posts, 0)
            # A different active chat doesn't thaw this one.
            other = self.root / "other.jsonl"; other.write_bytes(b"")
            a.start("other", "Other", "claude", "other", other)
            self.assertFalse(any(e["id"] in original for e in a.pending(scope=("claude", "other"))))
            # Restart here models process/OS restart without altering the persistent binding.
            reopened = self.store("chat")
            reopened.start("optics/vergence", "Optics", "claude", "chat", path)
            report = deliver(reopened, "claude", "chat")
            self.assertEqual(report["state"], "attempted")
            self.assertFalse(reopened.pending(scope=("claude", "chat")))
            self.assertTrue(original <= {e["id"] for e in reopened.events()})

    @patch.dict(os.environ, {"LEARNING_FIXTURE_TOKEN": "fixture-token"})
    def test_ack_loss_retry_does_not_duplicate_complete_turn(self):
        a, path, b = self.bound()
        self.round(a, path)
        with FixtureAPI(self.root / "server") as server:
            configure(a, server.url, "LEARNING_FIXTURE_TOKEN", True)
            server.drop_ack = True
            first = deliver(a, "claude", "chat")
            self.assertEqual(first["state"], "failed")
            self.assertTrue(first["notice"])
            second = deliver(a, "claude", "chat")
            self.assertEqual(second["state"], "attempted")
            self.assertIn("恢复", second["notice"])
            central = self.store("server")
            self.assertEqual(sum(e["kind"] == "message" for e in central.events()), 2)

    def test_notices_deduplicate_and_recover(self):
        a = self.store()
        scope = ("claude", "chat")
        self.assertTrue(notice(a, scope, "network"))
        self.assertIsNone(notice(a, scope, "network"))
        self.assertTrue(notice(a, scope, "authentication"))
        self.assertIn("恢复", notice(a, scope, None))
        self.assertIsNone(notice(a, scope, None))

    def test_async_failure_is_relayed_by_next_synchronous_hook(self):
        a, path, b = self.bound()
        self.round(a, path)
        deliver(a, "claude", "chat")  # No server configured.
        result = hook(a, "claude", {"session_id": "chat", "transcript_path": str(path), "hook_event_name": "UserPromptSubmit", "prompt": "next"}, phase="capture")
        self.assertIn("失败", result["systemMessage"])
        self.assertEqual(hook(a, "claude", {"session_id": "chat", "hook_event_name": "UserPromptSubmit", "prompt": "next"}, phase="capture"), {})

    def test_upload_lock_is_single_instance_and_released(self):
        a = self.store()
        with upload_lock(a) as first:
            self.assertTrue(first)
            with upload_lock(a) as second:
                self.assertFalse(second)
        with upload_lock(a) as third:
            self.assertTrue(third)

    def test_image_bytes_held_until_turn_complete_then_frozen_on_stop(self):
        a, path, b = self.bound()
        self.append(path, "claude", "draw a diagram")
        drain(a, "claude", "chat")
        image = self.root / "image.bin"; image.write_bytes(b"fixture image bytes")
        queued = assets.enqueue(a, "optics/vergence", image, "diagram", None, {}, b["session"])
        image.unlink()
        with patch("assets.remote") as send:
            assets.flush(a)
            send.assert_not_called()
        self.append(path, "claude", "diagram answer", "assistant")
        drain(a, "claude", "chat")
        complete(a, "claude", "chat", last_text="diagram answer")
        a.stop("claude", "chat")
        with patch("assets.remote") as send:
            assets.flush(a)
            send.assert_not_called()
        a.start("optics/vergence", "Optics", "claude", "chat", path)
        with patch("assets.remote", side_effect=lambda s, r: {**r["metadata"], "state": "ready", "oss_key": "fixture.png"}):
            result = assets.flush(a)
        self.assertEqual(result["results"][0]["asset_id"], queued["asset_id"])
        self.assertIsNone(a.db.execute("SELECT image FROM asset_jobs").fetchone()[0])

    def test_codex_native_completion_and_commentary_not_final(self):
        a, path, b = self.bound("codex")
        self.append(path, "codex", "question")
        with path.open("a") as f:
            f.write(json.dumps({"type": "turn_context", "payload": {"turn_id": "native"}}) + "\n")
            f.write(json.dumps({"type": "response_item", "payload": {"type": "message", "role": "assistant", "channel": "final", "content": "answer"}}) + "\n")
            f.write(json.dumps({"type": "event_msg", "payload": {"type": "task_complete", "turn_id": "native", "last_agent_message": "answer"}}) + "\n")
        drain(a, "codex", "chat")
        self.assertEqual(sum(e["kind"] == "message" for e in a.pending()), 2)
        self.append(path, "codex", "next question")
        with path.open("a") as f:
            f.write(json.dumps({"type": "response_item", "payload": {"type": "message", "role": "assistant", "channel": "commentary", "content": "working"}}) + "\n")
        drain(a, "codex", "chat")
        self.assertFalse(complete(a, "codex", "chat", last_text="working"))

    def test_stop_control_message_and_later_chat_are_excluded(self):
        a, path, b = self.bound()
        self.round(a, path)
        self.append(path, "claude", "/learn-stop")
        with patch("delivery.deliver") as send:
            hook(a, "claude", {"session_id": "chat", "hook_event_name": "UserPromptSubmit", "prompt": "/learn-stop"})
            send.assert_not_called()
        self.append(path, "claude", "private later")
        hook(a, "claude", {"session_id": "chat", "hook_event_name": "Stop"})
        self.assertNotIn("private later", json.dumps(a.events()))
        self.assertNotIn("/learn-stop", json.dumps(a.events()))

    def test_initiating_user_included_without_earlier_history(self):
        a = self.store()
        path = self.root / "start.jsonl"; path.write_bytes(b"")
        self.append(path, "claude", "private before")
        self.append(path, "claude", "old answer", "assistant")
        self.append(path, "claude", "start learning now")
        a.start("optics/vergence", "Optics", "claude", "chat", path, include_last_user=True)
        drain(a, "claude", "chat")
        messages = [e["data"]["text"] for e in a.events() if e["kind"] == "message"]
        self.assertEqual(messages, ["start learning now"])

    def test_old_async_stop_does_not_complete_new_identical_answer(self):
        a, path, b = self.bound()
        self.round(a, path, text="same answer")
        self.append(path, "claude", "next question")
        self.append(path, "claude", "same answer", "assistant")
        with patch("delivery.deliver", return_value={}):
            hook(a, "claude", {"session_id": "chat", "hook_event_name": "Stop", "last_assistant_message": "same answer"}, phase="upload")
        self.assertEqual(a.status()["delivery"]["turns"], {"complete": 1, "pending": 1})
        hook(a, "claude", {"session_id": "chat", "hook_event_name": "Stop", "last_assistant_message": "same answer"}, phase="capture")
        self.assertEqual(a.status()["delivery"]["turns"], {"complete": 2})
        self.assertEqual(sum(e["kind"] == "message" for e in a.pending()), 4)

    def test_codex_start_keeps_preceding_native_turn_identity(self):
        a = self.store()
        path = self.root / "native-start.jsonl"
        path.write_text(json.dumps({"type": "turn_context", "payload": {"turn_id": "native-start"}}) + "\n")
        self.append(path, "codex", "start learning")
        a.start("optics/vergence", "Optics", "codex", "chat", path, include_last_user=True)
        self.append(path, "codex", "answer", "assistant")
        drain(a, "codex", "chat")
        self.assertTrue(complete(a, "codex", "chat", turn_id="native-start", last_text="answer"))

    @patch.dict(os.environ, {"LEARNING_FIXTURE_TOKEN": "fixture-token"})
    def test_history_pull_never_uploads_even_active_completed_turns(self):
        a, path, b = self.bound()
        self.round(a, path)
        with FixtureAPI(self.root / "server") as server:
            configure(a, server.url, "LEARNING_FIXTURE_TOKEN", True)
            result = synchronize(a, pull_only=True)
            self.assertEqual(result["uploaded"], 0)
            self.assertEqual(server.posts, 0)
            self.assertEqual(sum(e["kind"] == "message" for e in a.pending()), 2)

    def test_legacy_pending_turns_and_images_remain_unverified(self):
        a, path, b = self.bound()
        self.round(a, path)
        image = self.root / "legacy.bin"; image.write_bytes(b"legacy bytes")
        assets.enqueue(a, "optics/vergence", image, "legacy", None, {}, b["session"])
        # Emulate a pre-gating database without touching any user state.
        with a.db:
            for table in ("delivery_events", "delivery_turns", "delivery_runs", "delivery_assets"):
                a.db.execute("DELETE FROM " + table)
        reopened = self.store("chat")
        self.assertFalse(any(e["kind"] == "message" for e in reopened.pending()))
        with patch("assets.remote") as send:
            assets.flush(reopened)
            send.assert_not_called()
        self.assertEqual(reopened.status()["delivery"]["turns"], {"incomplete": 1})
        self.assertIsNotNone(reopened.db.execute("SELECT image FROM asset_jobs").fetchone()[0])

    def test_host_entrypoints_preview_and_local_execution(self):
        a = self.store()
        for host, failure in (("codex", "Interrupt"), ("claude", "StopFailure")):
            config = self.root / (host + ".json")
            config.write_text(json.dumps({"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "existing-handler"}]}]}}))
            preview = install_hooks(a, host, config)
            self.assertNotIn(failure, json.loads(config.read_text())["hooks"])
            self.assertIn(failure, preview["config"]["hooks"])
            handlers = preview["config"]["hooks"]["Stop"][-1]["hooks"]
            self.assertIn(host + ".py", handlers[0]["command"])
            self.assertFalse(handlers[1]["async"])
            self.assertTrue(preview["config"]["hooks"]["PostToolUse"][-1]["hooks"][1]["async"])
            self.assertEqual(preview["config"]["hooks"]["Stop"][0]["hooks"][0]["command"], "existing-handler")
            entry = Path(assets.__file__).parent / "hooks" / (host + ".py")
            result = subprocess.run([sys.executable, str(entry), "--home", str(a.home), "hook", "--phase", "capture"],
                                    input=json.dumps({"session_id": "inactive", "hook_event_name": "Stop"}), text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {})

    def test_stop_between_identity_and_upload_prevents_new_requests(self):
        a, path, b = self.bound()
        self.round(a, path)
        def request(client, route, body=None):
            if route == "/v1/identity":
                a.stop("claude", "chat")
                return {"v": 1, "profile": a.profile, "server_id": "fixture-server"}
            self.fail("A new request was issued after recording stopped")
        with patch("sync.load_config", return_value={"transport": "ssh", "host": "fixture", "python": "/python", "service": "/service"}), patch("record_ssh.request", side_effect=lambda c, p, route, body, timeout: request(None, route, body)):
            with self.assertRaises(LedgerError):
                synchronize(a, scope=("claude", "chat"))

    def test_async_stop_waits_for_parallel_synchronous_capture(self):
        a, path, b = self.bound()
        self.append(path, "claude", "question")
        self.append(path, "claude", "answer", "assistant")
        payload = {"session_id": "chat", "hook_event_name": "Stop", "last_assistant_message": "answer"}
        def parallel_capture(_):
            hook(a, "claude", payload, phase="capture")
        def upload(store, host, name, **kwargs):
            self.assertEqual(store.status()["delivery"]["turns"], {"complete": 1})
            return {}
        with patch("capture.time.sleep", side_effect=parallel_capture), patch("delivery.deliver", side_effect=upload) as send:
            hook(a, "claude", payload, phase="upload")
            send.assert_called_once()

    def test_native_start_binds_before_transcript_exists(self):
        a = self.store()
        path = self.root / "not-created-yet.jsonl"
        result = hook(a, "claude", {"session_id": "chat", "hook_event_name": "UserPromptSubmit", "prompt": "/learn-start optics/vergence Optics", "transcript_path": str(path)}, phase="capture")
        self.assertIn("已开启", result["systemMessage"])
        self.assertFalse(path.exists())
        self.append(path, "claude", "question")
        self.append(path, "claude", "answer", "assistant")
        hook(a, "claude", {"session_id": "chat", "hook_event_name": "Stop", "last_assistant_message": "answer"}, phase="capture")
        self.assertEqual(a.status()["delivery"]["turns"], {"complete": 1})

    def test_codex_current_nonvisible_metadata_is_skipped(self):
        a, path, b = self.bound("codex")
        with path.open("a") as f:
            for kind in ("world_state", "token_usage_record"):
                f.write(json.dumps({"type": kind, "payload": {"private": "not a visible message"}}) + "\n")
        self.round(a, path, host="codex")
        self.assertEqual(sum(e["kind"] == "message" for e in a.pending()), 2)
        self.assertNotIn("not a visible message", json.dumps(a.events()))

    def test_claude_command_install_is_explicit_and_preserves_custom_commands(self):
        a = self.store()
        directory = self.root / "commands"
        config = self.root / "claude.json"
        preview = install_hooks(a, "claude", config, commands_dir=directory)
        self.assertFalse(directory.exists())
        self.assertEqual(len(preview["command_files"]), 2)
        install_hooks(a, "claude", config, True, directory)
        self.assertIn("learning-tutor owned command", (directory / "learn-start.md").read_text())
        (directory / "learn-stop.md").write_text("custom command")
        previous = config.read_bytes()
        with self.assertRaises(LedgerError):
            install_hooks(a, "claude", config, True, directory)
        self.assertEqual(config.read_bytes(), previous)
        self.assertEqual((directory / "learn-stop.md").read_text(), "custom command")

    def test_stop_awaits_inflight_lock_within_one_delivery_budget(self):
        a, path, b = self.bound()
        self.round(a, path)
        with patch("delivery.upload_lock", side_effect=[nullcontext(False), nullcontext(True)]), patch("delivery.time.sleep") as pause, patch("sync.synchronize", return_value={"uploaded": 4}) as sync, patch("assets.flush", return_value={"results": []}):
            report = deliver(a, "claude", "chat", wait_for_lock=True)
            self.assertEqual(report["state"], "attempted")
            pause.assert_called_once()
            self.assertIsNotNone(sync.call_args.kwargs["deadline"])

    def test_claude_hook_metadata_errors_and_sidechain_are_not_messages(self):
        a, path, b = self.bound()
        with path.open("a") as f:
            for kind in ("attachment", "mode"):
                f.write(json.dumps({"type": kind, "attachment": {"type": "hook_additional_context", "content": "private context"}}) + "\n")
        self.append(path, "claude", "API error", "assistant", isApiErrorMessage=True)
        self.append(path, "claude", "sidechain", "user", isSidechain=True)
        self.round(a, path)
        self.assertEqual(sum(e["kind"] == "message" for e in a.events()), 2)
