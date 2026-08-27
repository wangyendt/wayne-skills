"""Synthetic record RPC/validation regressions; no SSH or PostgreSQL access."""
import copy
import io
import json
import shlex
import subprocess
import types
import urllib.parse
from contextlib import contextmanager, nullcontext
from unittest.mock import Mock, patch

from test_learning import Base
from ledger import LedgerError, canonical, digest, validate
import record_ssh
from record_refs import check_references
from server.record_service import Service, ServiceError, pg_projection
import server.record_service as record_service
from sync import configure_ssh, identity, pull, synchronize


CONFIG = {"host": "fixture-host", "python": "/fixture/python", "service": "/fixture/record_service.py"}


class RecordTransportTests(Base):
    def rpc(self, reply, returncode=0, **kwargs):
        """Replace the entire process invocation; even malformed cases stay local."""
        raw = reply if isinstance(reply, bytes) else canonical(reply).encode()

        def run(argv, **options):
            options["stdout"].write(raw)
            options["stderr"].write(b"synthetic-secret-password-and-private-message")
            self.argv, self.options = argv, options
            return types.SimpleNamespace(returncode=returncode)

        with patch("record_ssh.subprocess.run", run):
            return record_ssh.request(kwargs.get("config", CONFIG), "personal", "/v1/identity", None)

    def test_ssh_options_and_shell_metacharacters_are_not_injected(self):
        config = dict(CONFIG, python="/fixture/python with spaces", service="/fixture/a'; $(printf injected).py")
        self.assertEqual(self.rpc({"ok": True, "result": {"v": 1}}, config=config), {"v": 1})
        self.assertEqual(shlex.split(self.argv[-1]), [config["python"], config["service"]])
        self.assertEqual(self.argv[-2], "fixture-host")
        self.assertIn("BatchMode=yes", self.argv)
        self.assertIn("StrictHostKeyChecking=yes", self.argv)
        self.assertFalse(self.options.get("shell", False))
        self.assertEqual(json.loads(self.options["input"]),
                         {"v": 1, "profile": "personal", "path": "/v1/identity", "body": None})

    def test_host_and_path_input_boundaries(self):
        for host in ("-oProxyCommand=fixture", "host;fixture", "host\nfixture", "host with spaces", "", None, []):
            with self.subTest(host=host), self.assertRaises(LedgerError):
                record_ssh.settings(host, CONFIG["python"], CONFIG["service"])
        for path in ("relative.py", "~/fixture.py", "/fixture\n.py", "/fixture\r.py", "/fixture\x00.py", None):
            with self.subTest(path=path), self.assertRaises(LedgerError):
                record_ssh.settings("fixture-host", CONFIG["python"], path)

    def test_errors_are_allowlisted_and_do_not_include_remote_stderr(self):
        for code, expected in (("reference", "reference"), ("private-message", "service_error"), ([], "service_error")):
            with self.subTest(code=code), self.assertRaises(LedgerError) as ctx:
                self.rpc({"ok": False, "code": code}, returncode=2)
            self.assertEqual(str(ctx.exception), "Record service rejected request: " + expected)
            self.assertNotIn("synthetic-secret", str(ctx.exception))

    def test_response_envelope_is_checked(self):
        for reply, rc in (([], 0), ({"ok": 1, "result": {}}, 0), ({"ok": True}, 0),
                          ({"ok": True, "result": {}}, 2), (b"not json private-message", 0)):
            with self.subTest(reply=reply), self.assertRaises(LedgerError) as ctx:
                self.rpc(reply, returncode=rc)
            self.assertNotIn("private-message", str(ctx.exception))

    def test_oversized_response_is_rejected(self):
        with patch("record_ssh.MAX_RESPONSE", 64), self.assertRaisesRegex(LedgerError, "Oversized"):
            self.rpc(b"x" * 65)

    def test_oversized_request_does_not_launch_ssh(self):
        with patch("record_ssh.MAX_REQUEST", 1), patch("record_ssh.subprocess.run") as launch:
            with self.assertRaises(LedgerError):
                record_ssh.request(CONFIG, "personal", "/v1/identity", None)
            launch.assert_not_called()

    def test_transport_failures_are_redacted(self):
        for error in (OSError("synthetic-secret"), subprocess.TimeoutExpired("synthetic-secret", 1)):
            with patch("record_ssh.subprocess.run", side_effect=error), self.assertRaises(LedgerError) as ctx:
                record_ssh.request(CONFIG, "personal", "/v1/identity", None)
            self.assertNotIn("synthetic-secret", str(ctx.exception))

    def test_config_is_private_and_cannot_silently_switch_server(self):
        store = self.store()
        configure_ssh(store, **CONFIG)
        self.assertEqual((store.home / "config.json").stat().st_mode & 0o077, 0)
        configure_ssh(store, **CONFIG)
        with self.assertRaises(LedgerError):
            configure_ssh(store, **dict(CONFIG, host="second-fixture"))

    def test_identity_requires_integer_protocol_version(self):
        store = self.store()
        for version in (True, 1.0, "1", None):
            client = Mock()
            client.request.return_value = {"v": version, "profile": "personal", "server_id": "fixture"}
            with self.subTest(version=version), self.assertRaises(LedgerError):
                identity(store, client)
        self.assertIsNone(store.meta("server_id"))

    def test_identity_change_keeps_original_dataset(self):
        store = self.store()
        with store.db:
            store.set_meta("server_id", "original")
        client = Mock()
        client.request.return_value = {"v": 1, "profile": "personal", "server_id": "other"}
        with self.assertRaises(LedgerError):
            identity(store, client)
        self.assertEqual(store.meta("server_id"), "original")

    def test_malformed_pages_leave_cursor_unchanged(self):
        store = self.store()
        with store.db:
            store.set_meta("server_id", "fixture")
        base = {"profile": "personal", "server_id": "fixture", "events": [], "cursor": 0, "more": False}
        for change in ({"cursor": True}, {"cursor": -1}, {"more": 1}, {"events": {}},
                       {"more": True}, {"profile": "other"}, {"server_id": "other"}):
            client = Mock()
            client.request.return_value = dict(base, **change)
            with self.subTest(change=change), self.assertRaises(LedgerError):
                pull(store, client)
            self.assertEqual(store.meta("cursor"), "0")

    def test_remote_tombstone_is_applied_before_upload(self):
        store, remote = self.store(), self.store("remote")
        binding = self.start(store)
        self.message(store, binding)
        deletion = remote.append(binding["topic"], "fixture-delete", "delete", {})
        calls = []

        class ClientStub:
            def __init__(self, *args):
                self.page = 0

            def request(self, path, body=None):
                calls.append((path, body))
                common = {"v": 1, "profile": "personal", "server_id": "fixture"}
                if path == "/v1/identity":
                    return common
                if body is not None:
                    raise AssertionError("Deleted pending content must not be sent")
                self.page += 1
                return dict(common, events=[deletion] if self.page == 1 else [], cursor=1, more=False)

        with patch("sync.Client", ClientStub):
            result = synchronize(store)
        self.assertEqual(result["uploaded"], 0)
        self.assertEqual(store.events(), [deletion])
        self.assertEqual(store.status()["pending"], 0)


class RecordServiceBoundaryTests(Base):
    def service(self):
        service = Service.__new__(Service)  # Never opens config, credentials or database.
        service.profile = "personal"
        service.db = Mock()
        return service

    def test_request_identity_and_paths_are_validated_before_db_access(self):
        service = self.service()
        base = {"v": 1, "profile": "personal", "path": "/v1/identity", "body": None}
        for change in ({"v": True}, {"v": 1.0}, {"profile": "other"}, {"unexpected": 1},
                       {"path": "https://fixture/v1/events"}, {"path": "//fixture/v1/events"},
                       {"path": "/v1/events#fragment"}, {"path": "/v1/identity", "body": {}}):
            with self.subTest(change=change), self.assertRaises(ServiceError):
                service.handle(dict(base, **change))
        service.db.execute.assert_not_called()

    def test_query_bounds_are_checked_before_db_access(self):
        service = self.service()
        for query in ("after=-1", "after=9223372036854775808", "limit=0", "limit=101",
                      "max_bytes=2047", "max_bytes=4194305", "after=1&after=2", "unexpected=1", "after"):
            with self.subTest(query=query), self.assertRaises(ServiceError):
                service.page(urllib.parse.urlsplit("/v1/events?" + query))
        service.db.transaction.assert_not_called()

    def test_batch_validation_precedes_transaction(self):
        store = self.store()
        self.start(store)
        event = store.pending()[0]
        service = self.service()
        batches = [[], [event, event], [dict(event, seq=9223372036854775808)],
                   [dict(event, v=True)], [dict(event, kind="invalid")], [event] * 101]
        for events in batches:
            with self.subTest(events=len(events)), self.assertRaises(ServiceError):
                service.post({"v": 1, "profile": "personal", "events": events})
        service.db.transaction.assert_not_called()

    def test_delete_first_and_profile_cursor_updated_inside_transaction(self):
        store = self.store()
        binding = self.start(store)
        old = copy.deepcopy(store.pending())
        deletion = store.append(binding["topic"], "fixture-delete", "delete", {})
        service, log = self.service(), []

        @contextmanager
        def transaction():
            log.append("begin")
            yield
            log.append("commit")

        def insert(event, cursor):
            log.append(event["kind"])
            return "accepted", cursor + 1

        def identity_locked(lock=False):
            self.assertTrue(lock)
            log.append("profile-lock")
            return {"v": 1, "profile": "personal", "server_id": "fixture"}, 7

        service.db.transaction = transaction
        service.identity = identity_locked
        service.insert = insert
        service.db.execute.side_effect = lambda *args: log.append("cursor-update")
        result = service.post({"v": 1, "profile": "personal", "events": old + [deletion]})
        self.assertEqual(log, ["begin", "profile-lock", "delete", "topic", "session", "cursor-update", "commit"])
        self.assertEqual({r["id"]: r["hash"] for r in result["receipts"]},
                         {e["id"]: digest(e) for e in old + [deletion]})

    def test_page_budget_and_deleted_sequence_holes(self):
        service = self.service()
        service.db.transaction = nullcontext
        service.identity = lambda: ({"v": 1, "profile": "personal", "server_id": "fixture"}, 20)
        service.db.execute.return_value.fetchall.return_value = [
            {"cursor": 3, "envelope": canonical({"data": "x" * 800})},
            {"cursor": 9, "envelope": canonical({"data": "y" * 800})}]
        page = service.page(urllib.parse.urlsplit("/v1/events?max_bytes=2048"))
        self.assertTrue(page["more"])
        self.assertEqual(page["cursor"], 3)
        self.assertEqual(len(page["events"]), 1)
        service.db.execute.return_value.fetchall.return_value = []
        page = service.page(urllib.parse.urlsplit("/v1/events?after=9"))
        self.assertFalse(page["more"])
        self.assertEqual(page["cursor"], 20)

    def test_topic_is_a_bound_sql_parameter(self):
        service = self.service()
        service.db.transaction = nullcontext
        service.identity = lambda: ({"v": 1, "profile": "personal", "server_id": "fixture"}, 0)
        service.db.execute.return_value.fetchall.return_value = []
        topic = "fixture'; SELECT 'synthetic'; --"
        request = {"v": 1, "profile": "personal", "path": "/v1/topics/" + urllib.parse.quote(topic, safe="") + "/events?after=0", "body": None}
        service.handle(request)
        sql, parameters = service.db.execute.call_args.args
        self.assertNotIn(topic, sql)
        self.assertIn(topic, parameters)

    def test_page_without_query_uses_defaults(self):
        service = self.service()
        service.db.transaction = nullcontext
        service.identity = lambda: ({"v": 1, "profile": "personal", "server_id": "fixture"}, 0)
        service.db.execute.return_value.fetchall.return_value = []
        page = service.page(urllib.parse.urlsplit("/v1/events"))
        self.assertEqual(page["cursor"], 0)
        self.assertFalse(page["more"])
        self.assertEqual(service.db.execute.call_args.args[1], ["personal", 0, 101])

    def test_projection_escapes_nul_without_changing_canonical_source(self):
        store = self.store()
        binding = self.start(store)
        event = self.message(store, binding, text="before\x00after")
        original = canonical(event)
        projection = pg_projection(event["data"])
        self.assertEqual(projection["text"], "before\\u0000after")
        self.assertEqual(canonical(event), original)
        self.assertEqual(json.loads(original)["data"]["text"], "before\x00after")
        nested = {"key\x00": ["value\x00", 1, None]}
        self.assertEqual(pg_projection(nested), {"key\\u0000": ["value\\u0000", 1, None]})
        self.assertEqual(nested["key\x00"][0], "value\x00")

    def test_nul_event_identities_are_rejected(self):
        store = self.store()
        self.start(store)
        event = store.pending()[0]
        for field in ("id", "device", "topic", "session"):
            with self.subTest(field=field), self.assertRaises(LedgerError):
                validate(dict(event, **{field: "fixture\x00"}), store.profile)

    def test_service_main_redacts_unexpected_storage_errors(self):
        request = canonical({"v": 1, "profile": "personal", "path": "/v1/identity", "body": None}).encode()
        stdin = types.SimpleNamespace(buffer=io.BytesIO(request))
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(record_service.sys, "stdin", stdin), patch.object(record_service.sys, "stdout", stdout), \
                patch.object(record_service.sys, "stderr", stderr), \
                patch.object(record_service, "Service", side_effect=RuntimeError("synthetic-secret")):
            status = record_service.main()
        self.assertEqual(status, 2)
        self.assertEqual(json.loads(stdout.getvalue()), {"ok": False, "code": "storage"})
        self.assertEqual(stderr.getvalue(), "")
        self.assertNotIn("synthetic-secret", stdout.getvalue())

    def test_shared_references_reject_cross_topic_and_invalid_corrections(self):
        store = self.store()
        binding = self.start(store)
        answer = self.message(store, binding)
        assessment = self.assessment(store, binding, answer)
        refs = {e["id"]: e for e in store.events()}
        get_event = refs.get
        exists = lambda topic: topic == binding["topic"]
        check_references(assessment, get_event, exists, LedgerError)
        for ref_change in ({"kind": "topic"}, {"topic": "other"}, {"data": {"role": "assistant"}}):
            refs[answer["id"]] = dict(answer, **ref_change)
            with self.subTest(change=ref_change), self.assertRaises(LedgerError):
                check_references(assessment, get_event, exists, LedgerError)
        refs[answer["id"]] = answer
        correction = copy.deepcopy(assessment)
        correction["data"]["supersedes"] = [assessment["id"]]
        correction["data"]["concept"] = "unrelated-concept"
        with self.assertRaises(LedgerError):
            check_references(correction, get_event, exists, LedgerError)
        for parent in (answer["id"], "missing"):
            checkpoint = dict(assessment, kind="checkpoint", data={"parents": [parent], "next": "fixture"})
            with self.subTest(parent=parent), self.assertRaises(LedgerError):
                check_references(checkpoint, get_event, exists, LedgerError)
