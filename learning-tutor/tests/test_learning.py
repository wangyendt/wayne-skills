import copy
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from ledger import Ledger, LedgerError, digest, now
from capture import drain, hook, parse_record
from sync import configure, hydrate, synchronize
from learn import install_hooks
from fixture_api import FixtureAPI


class Base(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.stores = []

    def tearDown(self):
        for store in self.stores:
            store.close()
        self.temp.cleanup()

    def store(self, name="a"):
        store = Ledger(self.root / name)
        self.stores.append(store)
        return store

    def start(self, store, external="fixture"):
        return store.start("optics/vergence", "辐辏角", external=external)

    def message(self, store, b, text="距离加倍，夹角近似减半", source="answer-1", role="user"):
        return store.append(b["topic"], b["session"], "message", {"role": role, "text": text}, source)

    def assessment(self, store, b, answer_event, **kwargs):
        d = dict(concept="vergence", dimension="reasoning", level="independent", hints=0,
                 evidence=[answer_event["id"]], reason="Explained the small-angle condition", rubric="v1", assessor="fixture-not-user-assessment")
        d.update(kwargs)
        return store.append(b["topic"], b["session"], "assessment", d)


class LedgerTests(Base):
    def test_persistence_and_repeated_identical_answers(self):
        a = self.store()
        b = self.start(a)
        one = self.message(a, b)
        self.assertEqual(one, self.message(a, b))
        two = self.message(a, b, source="answer-2")
        self.assertNotEqual(one["id"], two["id"])
        reopened = self.store()
        self.assertEqual(len(reopened.events()), 4)
        self.assertEqual(reopened.device, a.device)
        self.assertEqual(reopened.db.execute("PRAGMA synchronous").fetchone()[0], 2)

    def test_source_identity_collision(self):
        a = self.store()
        b = self.start(a)
        self.message(a, b)
        with self.assertRaises(LedgerError):
            self.message(a, b, "different")

    def test_evidence_required_and_later_session_can_grade_backlog(self):
        a = self.store()
        b = self.start(a)
        answer = self.message(a, b)
        with self.assertRaises(LedgerError):
            self.assessment(a, b, {"id": "missing"})
        other = self.start(a, "other")
        self.assessment(a, other, answer)
        other_answer = self.message(a, other)
        with self.assertRaises(LedgerError):
            self.assessment(a, other, answer, evidence=[answer["id"], other_answer["id"]])
        self.assessment(a, b, answer)
        self.assertEqual(a.summary(b["topic"])["unassessed_user_messages"], [other_answer["id"]])

    def test_assessment_correction_retains_original(self):
        a = self.store()
        b = self.start(a)
        answer = self.message(a, b)
        first = self.assessment(a, b, answer)
        second = self.assessment(a, b, answer, level="not_yet", supersedes=[first["id"]], reason="Correction: small-angle condition was omitted")
        summary = a.summary(b["topic"])
        self.assertEqual(len(summary["assessments"]), 2)
        self.assertEqual([e["id"] for e in summary["current_assessments"]], [second["id"]])
        self.assertEqual(summary["differing_evidence"], [])

    def test_ai_answer_is_not_learner_evidence(self):
        a = self.store()
        b = self.start(a)
        answer = self.message(a, b, role="assistant")
        with self.assertRaises(LedgerError):
            self.assessment(a, b, answer)

    def test_hints_and_novelty(self):
        a = self.store()
        b = self.start(a)
        answer = self.message(a, b)
        with self.assertRaises(LedgerError):
            self.assessment(a, b, answer, hints=1)
        with self.assertRaises(LedgerError):
            self.assessment(a, b, answer, level="transfer")
        self.assessment(a, b, answer, level="assisted", hints=2)
        self.assessment(a, b, answer, level="transfer", novel=True)
        self.assertEqual(a.summary(b["topic"])["differing_evidence"], ["vergence/reasoning"])

    def test_checkpoint_dag_merge_preserves_history(self):
        a = self.store()
        b = self.start(a)
        one = a.append(b["topic"], b["session"], "checkpoint", {"next": "Explain IPD", "parents": []})
        two = a.append(b["topic"], b["session"], "checkpoint", {"next": "Predict distance change", "parents": []})
        self.assertTrue(a.summary(b["topic"])["merge_needed"])
        merged = a.append(b["topic"], b["session"], "checkpoint", {"next": "Combine both in a novel example", "parents": [one["id"], two["id"]]})
        summary = a.summary(b["topic"])
        self.assertFalse(summary["merge_needed"])
        self.assertEqual([x["id"] for x in summary["checkpoint_heads"]], [merged["id"]])
        self.assertEqual(sum(e["kind"] == "checkpoint" for e in a.events()), 3)

    def test_invalid_checkpoint_parent(self):
        a = self.store()
        b = self.start(a)
        with self.assertRaises(LedgerError):
            a.append(b["topic"], b["session"], "checkpoint", {"next": "test", "parents": ["missing"]})

    def test_delete_wins_over_old_offline_events(self):
        a = self.store()
        b = self.start(a)
        old = self.message(a, b)
        deletion = a.append(b["topic"], "deletion", "delete", {})
        a.accept_page([old], 1)
        self.assertEqual([e["id"] for e in a.events()], [deletion["id"]])
        self.assertEqual(a.search("辐辏")["matches"], [])
        with self.assertRaises(LedgerError):
            self.start(a)

    def test_remote_identity_collision_rolls_back_cursor(self):
        a = self.store()
        b = self.start(a)
        original = self.message(a, b)
        altered = copy.deepcopy(original)
        altered["data"]["text"] = "changed"
        with self.assertRaises(LedgerError):
            a.accept_page([altered], 5)
        self.assertEqual(a.meta("cursor"), "0")

    def test_prune_only_inactive_fully_synced_old_topics(self):
        a = self.store()
        b = self.start(a)
        self.message(a, b)
        self.assertEqual(a.prune()["evicted_topics"], [])
        a.stop("manual", "fixture")
        self.assertEqual(a.prune()["evicted_topics"], [])
        with a.db:
            a.db.execute("UPDATE events SET ack='2000-01-01T00:00:00+00:00', cached_at='2000-01-01T00:00:00+00:00'")
        self.assertEqual(a.prune()["evicted_topics"], [b["topic"]])
        self.assertEqual(a.search("辐辏")["matches"][0]["archived"], 1)
        self.assertEqual(a.events(), [])

    def test_alias_and_unassessed_are_not_zero_score(self):
        a = self.store()
        b = self.start(a)
        self.message(a, b)
        a.append(b["topic"], "catalog", "alias", {"name": "双眼向内转"})
        self.assertEqual(len(a.search("向内转")["matches"]), 1)
        summary = a.summary(b["topic"])
        self.assertEqual(summary["assessments"], [])
        self.assertEqual(len(summary["unassessed_user_messages"]), 1)


class CaptureTests(Base):
    def line(self, host, text, role="user"):
        m = {"role": role, "content": [{"type": "text", "text": text}]}
        return {"codex": {"type": "response_item", "payload": {"type": "message", **m}},
                "claude": {"type": role, "message": m}, "openclaw": {"type": "message", "message": m}}[host]

    def append_line(self, path, record):
        with path.open("ab") as f:
            f.write((json.dumps(record, ensure_ascii=False) + "\n").encode())

    def test_three_transcript_formats_opt_in_and_restart(self):
        for host in ("codex", "claude", "openclaw"):
            with self.subTest(host=host):
                a = self.store(host)
                path = self.root / (host + ".jsonl")
                self.append_line(path, self.line(host, "private-before-start"))
                b = a.start("optics/vergence", "辐辏", host, "session", path)
                self.append_line(path, self.line(host, "same answer"))
                self.append_line(path, self.line(host, "same answer"))
                self.append_line(path, self.line(host, "feedback", "assistant"))
                self.assertEqual(drain(a, host, "session")["captured"], 3)
                reopened = self.store(host)
                self.assertEqual(drain(reopened, host, "session")["captured"], 0)
                messages = [e for e in a.events() if e["kind"] == "message"]
                self.assertEqual(len(messages), 3)
                self.assertNotIn("private-before-start", json.dumps(messages))
                a.stop(host, "session")
                self.append_line(path, self.line(host, "private-after-stop"))
                self.assertEqual(drain(a, host, "session")["state"], "not recording")

    def test_malformed_line_rolls_back_batch_and_cursor(self):
        a = self.store()
        path = self.root / "transcript"
        path.write_bytes(b"")
        b = a.start("x", "X", "codex", "s", path)
        self.append_line(path, self.line("codex", "valid"))
        with path.open("ab") as f:
            f.write(b"broken\n")
        with self.assertRaises(LedgerError):
            drain(a, "codex", "s")
        self.assertEqual(a.binding("codex", "s")["offset"], 0)
        self.assertEqual(len(a.events()), 2)
        self.assertTrue(a.binding("codex", "s")["error"])

    def test_torn_tail_then_completion(self):
        a = self.store()
        path = self.root / "transcript"
        path.write_bytes(b"")
        a.start("x", "X", "codex", "s", path)
        raw = json.dumps(self.line("codex", "answer")).encode()
        path.write_bytes(raw[:15])
        self.assertEqual(drain(a, "codex", "s")["captured"], 0)
        path.write_bytes(raw + b"\n")
        self.assertEqual(drain(a, "codex", "s")["captured"], 1)
        path.write_bytes(b"")
        with self.assertRaises(LedgerError):
            drain(a, "codex", "s")

    def test_excludes_analysis_and_tools(self):
        record = self.line("codex", "hidden", "assistant")
        record["payload"]["channel"] = "analysis"
        self.assertIsNone(parse_record("codex", record))
        self.assertIsNone(parse_record("codex", {"type": "event_msg", "payload": {"type": "agent_reasoning", "text": "hidden"}}))
        self.assertIsNone(parse_record("claude", {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "thinking", "thinking": "hidden"}]}}))

    def test_attachments_are_descriptors_not_binary(self):
        raw = {"type": "message", "message": {"role": "user", "content": [{"type": "image", "source": {"data": "SECRET_BASE64"}}]}}
        parsed = parse_record("openclaw", raw)
        self.assertEqual(len(parsed["attachments"]), 1)
        self.assertNotIn("SECRET_BASE64", json.dumps(parsed))

    def test_unbound_hook_does_not_scan_transcript(self):
        a = self.store()
        self.assertEqual(hook(a, "codex", {"session_id": "s", "transcript_path": "/nonexistent", "hook_event_name": "Stop"}), {})

    def test_hook_start_stop_and_preserved_install_config(self):
        a = self.store()
        path = self.root / "transcript"
        path.write_bytes(b"")
        payload = dict(session_id="s", transcript_path=str(path), hook_event_name="UserPromptSubmit", prompt="/learn-start x Test")
        hook(a, "claude", payload)
        self.append_line(path, self.line("claude", "answer"))
        hook(a, "claude", dict(payload, prompt="/learn-stop"))
        self.assertIsNone(a.binding("claude", "s"))
        config = self.root / "settings.json"
        config.write_text('{"permissions":{"allow":[]},"hooks":{"Stop":[{"hooks":[{"type":"command","command":"existing"}]}]}}')
        original = config.read_text()
        preview = install_hooks(a, "claude", config)
        self.assertEqual(config.read_text(), original)
        applied = install_hooks(a, "claude", config, True)
        self.assertEqual(Path(applied["backup"]).read_text(), original)
        again = install_hooks(a, "claude", config)
        self.assertEqual(len(again["config"]["hooks"]["Stop"]), 2)
        self.assertEqual(again["config"]["permissions"], {"allow": []})


class SyncTests(Base):
    def configured(self, store, server):
        configure(store, server.url, "LEARNING_FIXTURE_TOKEN", allow_loopback=True)

    @patch.dict(os.environ, {"LEARNING_FIXTURE_TOKEN": "fixture-token"})
    def test_two_devices_merge_replay_and_resume(self):
        a, b = self.store("a"), self.store("b")
        aa, bb = self.start(a, "a"), self.start(b, "b")
        self.message(a, aa)
        self.message(b, bb, "IPD增大时夹角增大")
        ca = a.append(aa["topic"], aa["session"], "checkpoint", {"next": "distance", "parents": []})
        cb = b.append(bb["topic"], bb["session"], "checkpoint", {"next": "IPD", "parents": []})
        with FixtureAPI(self.root / "server") as server:
            self.configured(a, server)
            self.configured(b, server)
            synchronize(a)
            synchronize(b)
            synchronize(a)
            self.assertEqual(a.status()["pending"], 0)
            self.assertEqual({e["id"] for e in a.events()}, {e["id"] for e in b.events()})
            self.assertTrue(a.summary(aa["topic"])["merge_needed"])
            a.append(aa["topic"], aa["session"], "checkpoint", {"next": "joint novel example", "parents": [ca["id"], cb["id"]]})
            synchronize(a)
            synchronize(b)
            self.assertFalse(b.summary(bb["topic"])["merge_needed"])

    @patch.dict(os.environ, {"LEARNING_FIXTURE_TOKEN": "fixture-token"})
    def test_lost_ack_is_recovered_without_duplicate_events(self):
        a = self.store()
        self.start(a)
        with FixtureAPI(self.root / "server") as server:
            self.configured(a, server)
            server.drop_ack = True
            with self.assertRaises(LedgerError):
                synchronize(a)
            self.assertEqual(a.status()["pending"], 2)
            synchronize(a)
            self.assertEqual(a.status()["pending"], 0)
            self.assertEqual(len(a.events()), 2)
            central = self.store("server")
            self.assertEqual(len(central.events()), 2)

    @patch.dict(os.environ, {"LEARNING_FIXTURE_TOKEN": "fixture-token"})
    def test_corrupt_ack_remains_pending(self):
        a = self.store()
        self.start(a)
        with FixtureAPI(self.root / "server") as server:
            self.configured(a, server)
            server.corrupt_ack = True
            with self.assertRaises(LedgerError):
                synchronize(a)
            self.assertEqual(a.status()["pending"], 2)

    @patch.dict(os.environ, {"LEARNING_FIXTURE_TOKEN": "fixture-token"})
    def test_remote_deletion_prevents_offline_resurrection(self):
        a, b = self.store("a"), self.store("b")
        aa = self.start(a)
        with FixtureAPI(self.root / "server") as server:
            self.configured(a, server)
            self.configured(b, server)
            synchronize(a)
            synchronize(b)
            bb = self.start(b, "offline")
            self.message(b, bb, "offline private answer")
            a.append(aa["topic"], "deletion", "delete", {})
            synchronize(a)
            synchronize(b)
            self.assertEqual(b.search("辐辏")["matches"], [])
            self.assertTrue(all(e["kind"] == "delete" for e in b.events()))
            central = self.store("server")
            self.assertNotIn("offline private answer", json.dumps(central.events()))

    @patch.dict(os.environ, {"LEARNING_FIXTURE_TOKEN": "fixture-token"})
    def test_pruned_topic_hydrates(self):
        a = self.store()
        b = self.start(a)
        self.message(a, b)
        a.stop("manual", "fixture")
        with FixtureAPI(self.root / "server") as server:
            self.configured(a, server)
            synchronize(a)
            with a.db:
                a.db.execute("UPDATE events SET ack='2000-01-01T00:00:00+00:00', cached_at='2000-01-01T00:00:00+00:00'")
            a.prune()
            self.assertEqual(a.events(), [])
            summary = hydrate(a, b["topic"])
            self.assertFalse(summary["topic"]["archived"])
            self.assertEqual(len(summary["unassessed_user_messages"]), 1)

    def test_no_server_and_unsafe_urls(self):
        a = self.store()
        self.start(a)
        with self.assertRaises(LedgerError):
            synchronize(a)
        self.assertEqual(a.status()["pending"], 2)
        for url in ("http://example.com", "https://u:p@example.com", "https://example.com?token=x"):
            with self.assertRaises(LedgerError):
                configure(a, url)

    def test_receipt_batch_is_atomic(self):
        a = self.store()
        self.start(a)
        batch = a.pending()
        receipts = [{"id": e["id"], "hash": digest(e), "status": "accepted"} for e in batch]
        receipts[-1]["hash"] = "bad"
        with self.assertRaises(LedgerError):
            a.acknowledge(batch, receipts)
        self.assertEqual(a.status()["pending"], len(batch))


class CLITests(Base):
    def test_cli_end_to_end_and_private_state_outside_repo(self):
        cli = [sys.executable, str(SCRIPTS / "learn.py"), "--home", str(self.root / "cli")]
        def run(*args, input=None):
            p = subprocess.run(cli + list(args), input=input, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            return json.loads(p.stdout)
        run("init")
        run("start", "optics/vergence", "辐辏角", "--host-session", "manual-test")
        answer = run("record", "--host-session", "manual-test", "--source-id", "1", "--json", "-", input='{"role":"user","text":"合成测试回答"}')
        self.assertEqual(answer["data"]["origin"], "explicit-manual")
        self.assertEqual(len(run("search", "辐辏")["matches"]), 1)
        self.assertEqual(len(run("resume", "optics/vergence")["unassessed_user_messages"]), 1)
        run("stop", "--host", "manual", "--host-session", "manual-test")
        exported = self.root / "export.json"
        run("export", "optics/vergence", "--output", str(exported))
        self.assertTrue(exported.exists())


if __name__ == "__main__":
    unittest.main()
