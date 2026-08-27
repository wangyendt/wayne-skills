import copy
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from unittest.mock import patch

from test_learning import Base, SCRIPTS
from ledger import LedgerError, digest
from capture import drain, hook
from sync import configure, hydrate, synchronize
from fixture_api import FixtureAPI


class BoundaryRegressions(Base):
    def test_null_nested_payload_is_visible_error_and_stop_still_works(self):
        for host, record in [("codex", {"type": "response_item", "payload": None}),
                             ("codex", {"type": "item.completed", "item": None}),
                             ("claude", {"type": "user", "message": None}),
                             ("openclaw", {"type": "message", "message": None})]:
            with self.subTest(host=host, record=record):
                a = self.store(host + str(record["type"]))
                path = self.root / (host + str(record["type"]) + ".jsonl")
                path.write_bytes(b"")
                b = a.start("x", "X", host, "s", path)
                path.write_text(json.dumps(record) + "\n")
                with self.assertRaises(LedgerError):
                    drain(a, host, "s")
                self.assertTrue(a.binding(host, "s")["error"])
                if host in {"codex", "claude"}:
                    hook(a, host, {"session_id": "s", "hook_event_name": "UserPromptSubmit", "prompt": "/learn-stop"})
                else:
                    a.stop(host, "s")
                self.assertIsNone(a.binding(host, "s"))
                self.assertTrue(a.events(b["topic"])[-1]["data"]["capture_gap"])

    def test_stop_marks_torn_tail(self):
        a = self.store()
        path = self.root / "tail.jsonl"
        path.write_bytes(b"")
        b = a.start("x", "X", "claude", "s", path)
        path.write_bytes(b'{"type":"assistant",')
        result = hook(a, "claude", {"session_id": "s", "hook_event_name": "UserPromptSubmit", "prompt": "/learn-stop"})
        self.assertIn("incomplete", result["systemMessage"])
        self.assertTrue(a.events(b["topic"])[-1]["data"]["capture_gap"])
        self.assertIsNone(a.binding("claude", "s"))

    def test_malformed_protocol_scalars_are_recoverable_errors(self):
        a = self.store()
        self.start(a)
        batch = a.pending()
        for field, value in [("id", []), ("status", []), ("hash", {})]:
            receipts = [{"id": e["id"], "hash": digest(e), "status": "accepted"} for e in batch]
            receipts[0][field] = value
            with self.assertRaises(LedgerError):
                a.acknowledge(batch, receipts)
        for field, value in [("kind", []), ("id", {}), ("v", True), ("data", [])]:
            event = copy.deepcopy(batch[0])
            event[field] = value
            with self.assertRaises(LedgerError):
                a.accept_page([event], 1)
        self.assertEqual(a.meta("cursor"), "0")
        self.assertEqual(a.status()["pending"], len(batch))

    @patch.dict(os.environ, {"LEARNING_FIXTURE_TOKEN": "fixture-token"})
    def test_large_legal_messages_use_byte_bounded_pages_and_hydrate(self):
        a, b = self.store("a"), self.store("b")
        aa = self.start(a)
        for i in range(18):
            self.message(a, aa, text="x" * 950000, source="large-" + str(i))
        a.stop("manual", "fixture")
        with FixtureAPI(self.root / "server") as server:
            for store in (a, b):
                configure(store, server.url, "LEARNING_FIXTURE_TOKEN", True)
            synchronize(a)
            synchronize(b)
            self.assertGreater(server.posts, 1)
            self.assertEqual({e["id"] for e in a.events()}, {e["id"] for e in b.events()})
            with b.db:
                b.db.execute("UPDATE events SET ack='2000-01-01T00:00:00+00:00', cached_at='2000-01-01T00:00:00+00:00'")
            b.prune()
            self.assertEqual(b.events(), [])
            hydrate(b, aa["topic"])
            self.assertEqual(len(b.events()), len(a.events()))
            self.assertEqual(a.status()["pending"], 0)

    def test_failed_snapshot_does_not_restore_partial_archive(self):
        a = self.store()
        aa = self.start(a)
        a.stop("manual", "fixture")
        original = a.events()
        with a.db:
            a.db.execute("UPDATE events SET ack='2000-01-01T00:00:00+00:00', cached_at='2000-01-01T00:00:00+00:00'")
            a.set_meta("server_id", "fixture")
        a.prune()
        class Stub:
            def __init__(self, *args):
                self.n = 0
            def request(self, path):
                if path == "/v1/identity":
                    return {"v": 1, "profile": "personal", "server_id": "fixture"}
                self.n += 1
                if self.n == 1:
                    return {"profile": "personal", "server_id": "fixture", "events": original[:1], "cursor": 1, "more": True}
                raise LedgerError("connection interrupted")
        with patch("sync.Client", Stub):
            with self.assertRaises(LedgerError):
                hydrate(a, aa["topic"])
        self.assertEqual(a.events(), [])
        self.assertEqual(a.summary(aa["topic"])["topic"]["archived"], 1)

    def test_worker_reports_heartbeat_without_server(self):
        a = self.store()
        run = subprocess.run([sys.executable, str(SCRIPTS / "learn.py"), "--home", str(a.home), "worker", "--once"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertTrue(a.status()["worker"]["heartbeat"])
        self.assertIn("Server not configured", a.status()["sync_error"])

    def test_concurrent_source_replay(self):
        a = self.store()
        self.start(a)
        script = '''import sys
sys.path.insert(0, sys.argv[1])
from ledger import Ledger
s=Ledger(sys.argv[2]); b=s.binding('manual','fixture')
for i in range(20): s.append(b['topic'],b['session'],'message',{'role':'user','text':'same'},source='concurrent-'+str(i))
s.close()
'''
        processes = [subprocess.Popen([sys.executable, "-c", script, str(SCRIPTS), str(a.home)], stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(4)]
        for process in processes:
            out, err = process.communicate(timeout=30)
            self.assertEqual(process.returncode, 0, err.decode())
        messages = [e for e in a.events() if e["kind"] == "message"]
        self.assertEqual(len(messages), 20)
        self.assertEqual(len({e["seq"] for e in a.events()}), len(a.events()))


class DocumentationTests(Base):
    def test_vergence_analytic_limits_and_printed_values(self):
        text = (SCRIPTS.parent / "references/vergence.md").read_text()
        for value in (7.3239, 3.6657, 1.8333):
            self.assertIn(str(value), text)
        b = .064
        for z, expected in [(.5, 7.3239), (1, 3.6657), (2, 1.8333)]:
            angle = 2 * math.atan(b / (2 * z))
            self.assertAlmostEqual(math.degrees(angle), expected, places=4)
            self.assertAlmostEqual(math.tan(angle / 2) * 2 * z, b)
            self.assertAlmostEqual(angle, 2 * math.atan(2 * b / (2 * 2 * z)))
        self.assertLess(2 * math.atan(b / (2 * 1e9)), 1e-9)
        self.assertGreater(2 * math.atan(b / (2 * .5)), 2 * math.atan(b / (2 * 1)))

    def test_bilingual_catalog_matches_source_skills(self):
        root = SCRIPTS.parents[1]
        if not (root / "CLAUDE.md").is_file() or not (root / "README_ch.md").is_file():
            self.skipTest("Repository catalog validation requires the source checkout")
        skills = [p for p in root.rglob("SKILL.md") if not any(part.startswith(".") for part in p.relative_to(root).parts)]
        expected = {str(p.relative_to(root)) for p in skills}
        for name in ("README.md", "README_ch.md"):
            text = (root / name).read_text()
            found = set(re.findall(r"\]\(([^)]+/SKILL\.md)\)", text))
            self.assertEqual(found, expected)
            self.assertIn("`%d`" % len(skills), text)
            for p in expected:
                self.assertTrue((root / p).is_file())

    def test_skill_markdown_local_links_and_no_scaffold(self):
        for file in [*SCRIPTS.parent.rglob("*.md"), SCRIPTS.parents[1] / "README.md", SCRIPTS.parents[1] / "README_ch.md"]:
            if not file.is_file():
                continue
            text = file.read_text()
            self.assertNotIn("[TODO", text)
            self.assertEqual(text.count("``` "), 0)
            self.assertEqual(len(re.findall(r"^```", text, re.M)) % 2, 0, str(file))
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                self.assertTrue((file.parent / target.split("#")[0]).exists(), str(file) + " → " + target)
