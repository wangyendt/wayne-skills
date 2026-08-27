"""Opt-in real PostgreSQL tests: isolated synthetic profile, never personal records.

LEARNING_RECORD_TEST_CONFIG must name a private server-side config directory
whose profile starts with learning-tutor-test-. Admin provisions/cleans that
profile outside this suite. Normal local discovery skips these tests.
"""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
import uuid
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "server"))
from ledger import Ledger, LedgerError, digest
from record_service import Service, ServiceError
from sync import hydrate, synchronize


@unittest.skipUnless(os.environ.get("LEARNING_RECORD_TEST_CONFIG"), "Explicit isolated PostgreSQL test profile required")
class PostgresRecordTests(unittest.TestCase):
    def setUp(self):
        self.config = Path(os.environ["LEARNING_RECORD_TEST_CONFIG"])
        profile = json.loads((self.config / "record-database.json").read_text())["profile"]
        if not profile.startswith("learning-tutor-test-"):
            raise RuntimeError("Tests require an isolated synthetic profile, never personal")
        self.temp = tempfile.TemporaryDirectory()
        self.stores = []
        self.service = Service(self.config)
        self.profile = profile
        self.key = "tests/" + self._testMethodName + "/" + uuid.uuid4().hex
        self.a = self.store("a")
        self.binding = self.a.start(self.key, "Synthetic test topic")

    def tearDown(self):
        for store in self.stores:
            store.close()
        self.service.close()
        self.temp.cleanup()

    def store(self, name):
        store = Ledger(Path(self.temp.name) / name, self.profile)
        self.stores.append(store)
        return store

    def request(self, path, body=None):
        return self.service.handle(dict(v=1, profile=self.profile, path=path, body=body))

    def post(self, events):
        return self.request("/v1/events", dict(v=1, profile=self.profile, events=events))

    def message(self, text="Synthetic answer"):
        return self.a.append(self.binding["topic"], self.binding["session"], "message", dict(role="user", text=text))

    def topic_page(self, after=0, **params):
        query = {"after": after, "limit": 100, "max_bytes": 4194304, **params}
        return self.request("/v1/topics/" + self.binding["topic"] + "/events?" + "&".join(str(k)+"="+str(v) for k,v in query.items()))

    def test_commit_receipts_replay_and_identity_conflict(self):
        self.message()
        events = self.a.events()
        result = self.post(events)
        self.assertEqual({r["status"] for r in result["receipts"]}, {"accepted"})
        self.assertEqual({r["id"]:r["hash"] for r in result["receipts"]}, {e["id"]:digest(e) for e in events})
        cursor = self.service.identity()[1]
        self.assertEqual({r["status"] for r in self.post(events)["receipts"]}, {"duplicate"})
        self.assertEqual(cursor, self.service.identity()[1])
        bad = copy.deepcopy(events[-1]);bad["data"]["text"] = "Changed under existing ID"
        with self.assertRaises(ServiceError):
            self.post([bad])
        self.assertEqual(self.topic_page()["events"], events)

    def test_invalid_reference_rolls_back_whole_batch_and_cursor(self):
        self.post(self.a.events())
        message = self.message()
        assessment = self.a.append(self.binding["topic"], self.binding["session"], "assessment", dict(
            concept="test", dimension="reasoning", level="independent", hints=0,
            evidence=[message["id"]], reason="Synthetic", rubric="test", assessor="test"))
        bad = copy.deepcopy(assessment);bad["data"]["evidence"] = ["missing"]
        cursor = self.service.identity()[1]
        with self.assertRaises(ServiceError):
            self.post([message, bad])
        self.assertIsNone(self.service.event(message["id"]))
        self.assertEqual(cursor, self.service.identity()[1])
        self.assertIsNone(self.service.db.execute("SELECT id FROM learning.receipts WHERE profile=%s AND id=%s", (self.profile, message["id"])).fetchone())

    def test_device_sequence_reuse_is_rejected(self):
        self.post(self.a.events())
        event = self.message();self.post([event])
        collision = copy.deepcopy(event);collision["id"] = str(uuid.uuid4())
        with self.assertRaises(ServiceError):
            self.post([collision])

    def test_nul_preserves_canonical_envelope_and_marks_projection(self):
        event = self.message("before\x00after\\u0000 literal")
        self.post(self.a.events())
        returned = self.service.event(event["id"])
        self.assertEqual(returned, event)
        self.assertEqual(digest(returned), digest(event))
        projection = self.service.db.execute("SELECT data,projection_escaped FROM learning.events WHERE profile=%s AND id=%s", (self.profile,event["id"])).fetchone()
        self.assertTrue(projection["projection_escaped"])
        self.assertNotIn("\x00", projection["data"]["text"])

    def test_delete_wins_within_batch_and_over_late_uploads(self):
        old = self.message("SYNTHETIC_DELETE_MARKER")
        original = self.a.events()
        self.post(original)
        deletion = self.a.append(self.binding["topic"], "deletion", "delete", {})
        result = self.post([old, deletion])
        self.assertEqual({r["id"]:r["status"] for r in result["receipts"]}[old["id"]], "deleted")
        self.assertEqual(self.topic_page()["events"], [deletion])
        self.assertEqual(self.post(original)["receipts"][0]["status"], "deleted")
        self.assertIsNone(self.service.event(old["id"]))
        self.assertFalse(self.service.topic_exists(self.binding["topic"]))
        self.assertIsNotNone(self.service.db.execute("SELECT hash FROM learning.receipts WHERE profile=%s AND id=%s",(self.profile,old["id"])).fetchone())

    def test_profile_and_version_boundaries(self):
        for change in ({"profile":"personal"}, {"v":True}, {"path":"https://HOST/v1/events"}):
            with self.assertRaises(ServiceError):
                self.service.handle({"v":1,"profile":self.profile,"path":"/v1/identity","body":None,**change})
        self.assertEqual(self.request("/v1/events")["profile"], self.profile)

    def test_two_clients_lost_ack_resume_and_hydrate(self):
        self.message()
        cp = self.a.append(self.binding["topic"], self.binding["session"], "checkpoint", dict(next="Synthetic next step", parents=[]))
        peer = self
        class LostAckClient:
            lost = False
            def request(self, path, body=None):
                result = peer.request(path, body)
                if body and not self.lost:
                    self.lost = True
                    raise LedgerError("Synthetic lost ACK after commit")
                return result
        client = LostAckClient()
        with patch("sync.Client", return_value=client):
            with self.assertRaises(LedgerError):
                synchronize(self.a)
            self.assertGreater(self.a.status()["pending"], 0)
            synchronize(self.a)
            self.assertEqual(self.a.status()["pending"], 0)
            b = self.store("b");synchronize(b)
            self.assertEqual([e["id"] for e in b.summary(self.binding["topic"])["checkpoint_heads"]], [cp["id"]])
            with b.db:
                b.db.execute("UPDATE events SET ack='2000-01-01T00:00:00+00:00',cached_at='2000-01-01T00:00:00+00:00'")
            b.prune()
            self.assertEqual(b.events(self.binding["topic"]), [])
            hydrate(b,self.binding["topic"])
            self.assertEqual(b.events(self.binding["topic"]), self.a.events(self.binding["topic"]))

    def test_serialized_writers_expose_only_committed_cursor(self):
        second = self.store("second")
        second.start(self.key+"-second", "Synthetic concurrent topic")
        entered, release = threading.Event(), threading.Event()
        errors = []
        root = self
        class SlowService(Service):
            def insert(self, event, cursor):
                result = super().insert(event, cursor)
                if event["kind"] == "topic":
                    entered.set()
                    if not release.wait(5):
                        raise RuntimeError("Synthetic gate timeout")
                return result
        def writer(service_class, events):
            service = service_class(root.config)
            try:
                service.post(dict(v=1,profile=root.profile,events=events))
            except Exception as e:
                errors.append(type(e).__name__)
            finally:
                service.close()
        initial = self.service.identity()[1]
        a = threading.Thread(target=writer,args=(SlowService,self.a.events()))
        b = threading.Thread(target=writer,args=(Service,second.events()))
        a.start();self.assertTrue(entered.wait(5));b.start();time.sleep(.1)
        self.assertEqual(self.service.identity()[1],initial)
        release.set();a.join(8);b.join(8)
        self.assertFalse(a.is_alive() or b.is_alive());self.assertEqual(errors,[])
        self.assertEqual(self.service.identity()[1],initial+4)
        page=self.request("/v1/events?after=%d"%initial)
        self.assertEqual(len(page["events"]),4)

    def test_z_byte_bounded_paging(self):
        for _ in range(3):
            self.message("x"*900000)
        expected=self.a.events();self.post(expected)
        events=[];cursor=0
        for _ in range(10):
            page=self.topic_page(cursor,max_bytes=1100000)
            events.extend(page["events"]);cursor=page["cursor"]
            if not page["more"]:break
        self.assertEqual(events,expected)
        with self.assertRaises(ServiceError):
            self.topic_page(after=self.service.db.execute("SELECT cursor FROM learning.events WHERE profile=%s AND id=%s",(self.profile,expected[1]["id"])).fetchone()["cursor"],max_bytes=2048)


if __name__ == "__main__":
    unittest.main()
