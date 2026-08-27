#!/usr/bin/env python3
"""Teaching ledger CLI; use --help. No external Python dependencies."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from ledger import Ledger, LedgerError, canonical, now
from capture import drain, drain_all, hook
from sync import configure, configure_ssh, hydrate, load_config, synchronize


def read_json(path):
    text = sys.stdin.read(1024 * 1024 + 1) if path == "-" else Path(path).read_text(encoding="utf-8")
    if len(text.encode()) > 1024 * 1024:
        raise LedgerError("JSON input exceeds one MiB")
    return json.loads(text)


def output(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--home", help="Private local state directory, outside Git")
    p.add_argument("--profile", default="personal", help="Same learner namespace on all devices")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    sub.add_parser("status")
    sub.add_parser("doctor")
    a = sub.add_parser("start")
    a.add_argument("key")
    a.add_argument("title")
    a.add_argument("--host", choices=["manual", "codex", "claude", "openclaw"], default="manual")
    a.add_argument("--host-session")
    a.add_argument("--transcript")
    for name in ("stop", "capture"):
        a = sub.add_parser(name)
        a.add_argument("--host", required=True)
        a.add_argument("--host-session", required=True)
    a = sub.add_parser("record", help="Explicit/manual evidence; not proof of automatic capture")
    a.add_argument("--host", default="manual")
    a.add_argument("--host-session", required=True)
    a.add_argument("--json", required=True, help="{role,text,...} JSON path, or - for stdin")
    a.add_argument("--source-id", required=True, help="Unique message identity; not its content hash")
    a = sub.add_parser("assess")
    a.add_argument("--host", default="manual")
    a.add_argument("--host-session", required=True)
    a.add_argument("--json", required=True)
    a = sub.add_parser("checkpoint")
    a.add_argument("--host", default="manual")
    a.add_argument("--host-session", required=True)
    a.add_argument("--json", required=True, help="{next,parents,misconceptions?,sources?}")
    a = sub.add_parser("search")
    a.add_argument("query")
    for name in ("resume", "hydrate", "export", "delete-topic"):
        a = sub.add_parser(name)
        a.add_argument("key")
        if name == "delete-topic":
            a.add_argument("--confirm-key", required=True)
        if name == "export":
            a.add_argument("--output", required=True)
    a = sub.add_parser("alias")
    a.add_argument("key")
    a.add_argument("name")
    a = sub.add_parser("configure")
    a.add_argument("--url", required=True)
    a.add_argument("--token-env", default="LEARNING_TUTOR_TOKEN")
    a.add_argument("--allow-loopback-http", action="store_true")
    a = sub.add_parser("configure-ssh", help="Connect to the PostgreSQL record service using existing SSH authentication")
    a.add_argument("--ssh", required=True)
    a.add_argument("--python", required=True)
    a.add_argument("--service", required=True)
    sub.add_parser("sync")
    a = sub.add_parser("worker", help="Foreground capture/sync worker; Ctrl-C to stop")
    a.add_argument("--once", action="store_true")
    a.add_argument("--interval", type=float, default=2)
    a = sub.add_parser("prune")
    a.add_argument("--days", type=int, default=30)
    a = sub.add_parser("hook")
    a.add_argument("--host", required=True, choices=["codex", "claude"])
    a = sub.add_parser("install-hooks")
    a.add_argument("--host", choices=["codex", "claude"], required=True)
    a.add_argument("--config", required=True, help="Exact hooks.json / settings.json path")
    a.add_argument("--apply", action="store_true", help="Default is preview only; existing entries preserved")
    return p


def install_hooks(store, host, config_path, apply=False):
    import shlex
    import tempfile
    path = Path(config_path).expanduser().resolve()
    previous = path.read_text(encoding="utf-8") if path.exists() else "{}"
    config = json.loads(previous)
    if not isinstance(config, dict) or not isinstance(config.get("hooks", {}), dict):
        raise LedgerError("Hook configuration must be an object")
    args = [sys.executable, str(Path(__file__).resolve()), "--home", str(store.home), "--profile", store.profile, "hook", "--host", host]
    command = subprocess.list2cmdline(args) if os.name == "nt" else " ".join(shlex.quote(x) for x in args)
    hooks = config.setdefault("hooks", {})
    for event in ("SessionStart", "UserPromptSubmit", "PostToolUse", "Stop", "SessionEnd"):
        entries = hooks.setdefault(event, [])
        if not isinstance(entries, list):
            raise LedgerError("Hook entries must be lists")
        if not any(any(h.get("command") == command for h in row.get("hooks", [])) for row in entries):
            entries.append({"hooks": [{"type": "command", "command": command}]})
    result = {"mode": "preview", "path": str(path), "config": config,
              "note": "Host restart/reload and real-turn verification required. Run worker for tail recovery; no server upload inside hooks."}
    if apply:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            # Exclusive backup creation; never overwrite an earlier rollback copy.
            backup = path.with_name(path.name + ".learning-tutor-" + str(time.time_ns()) + ".bak")
            with backup.open("x", encoding="utf-8") as f:
                f.write(previous)
            if os.name != "nt":
                backup.chmod(0o600)
            result["backup"] = str(backup)
        fd, temp = tempfile.mkstemp(dir=str(path.parent), prefix=".learning-hooks-")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(json.dumps(config, ensure_ascii=False, indent=2) + "\n")
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp, str(path))
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
        result["mode"] = "applied; host verification pending"
    return result


def doctor(store):
    from assets import status as image_status
    versions = {}
    for host in ("codex", "claude", "openclaw"):
        executable = shutil.which(host)
        if not executable:
            versions[host] = "not found"
            continue
        try:
            r = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=10)
            versions[host] = r.stdout.strip()[:180] if r.returncode == 0 else "version command failed"
        except (OSError, subprocess.TimeoutExpired):
            versions[host] = "version check failed"
    return {"python": sys.version.split()[0], "platform": sys.platform, "home": str(store.home),
            "sqlite_check": store.db.execute("PRAGMA quick_check").fetchone()[0],
            "server_configured": bool(load_config(store)), "host_versions": versions,
            "capture_assurance": "fixture-tested adapters; real host/OS coverage must be tested separately",
            "images": image_status(store), "status": store.status()}


def execute(args, store):
    cmd = args.command
    if cmd == "init":
        return {"home": str(store.home), "profile": store.profile, "device": store.device,
                "state": "local-only until API is configured", "next": "Explicitly start a learning session; install adapters and run worker for automatic capture."}
    if cmd == "status":
        from assets import status as image_status
        return {**store.status(), "images": image_status(store)}
    if cmd == "doctor":
        return doctor(store)
    if cmd == "start":
        if args.host != "manual" and (not args.host_session or not args.transcript):
            raise LedgerError("Host capture requires an explicit host-session ID and transcript path")
        return store.start(args.key, args.title, args.host, args.host_session, args.transcript)
    if cmd in {"stop", "capture"}:
        binding = store.binding(args.host, args.host_session)
        try:
            result = drain(store, args.host, args.host_session) if binding and binding["path"] else {"state": "manual mode" if binding else "not recording"}
        except LedgerError as e:
            if cmd != "stop":
                raise
            result = {"capture_gap": str(e)}
        if cmd == "stop":
            if result.get("partial_tail"):
                result["capture_gap"] = "Stopped with an incomplete transcript tail"
                with store.db:
                    store.db.execute("UPDATE captures SET error=? WHERE host=? AND external=?", (result["capture_gap"], args.host, args.host_session))
            store.stop(args.host, args.host_session)
        return {"action": cmd, **result}
    if cmd in {"record", "assess", "checkpoint"}:
        binding = store.binding(args.host, args.host_session)
        if not binding:
            raise LedgerError("Explicitly start this learning session first")
        if binding["path"]:
            drain(store, args.host, args.host_session)
        data = read_json(args.json)
        if not isinstance(data, dict):
            raise LedgerError("Event data must be an object")
        if cmd == "record":
            data["origin"] = "explicit-manual"
        return store.append(binding["topic"], binding["session"], {"record": "message", "assess": "assessment", "checkpoint": "checkpoint"}[cmd], data,
                            ("manual:" + args.source_id) if cmd == "record" else None)
    if cmd == "search":
        return store.search(args.query)
    if cmd in {"resume", "export", "delete-topic", "alias", "hydrate"}:
        topic = store.topic_id(args.key)
        if cmd == "resume":
            return store.summary(topic)
        if cmd == "hydrate":
            return hydrate(store, topic)
        if cmd == "alias":
            return store.append(topic, "catalog", "alias", {"name": args.name})
        if cmd == "delete-topic":
            if args.key != args.confirm_key:
                raise LedgerError("Confirmation key does not match")
            return store.append(topic, "deletion", "delete", {})
        export = {"summary": store.summary(topic), "events": store.events(topic)}
        fd = os.open(str(Path(args.output).expanduser()), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(canonical(export))
        return {"exported": str(Path(args.output).resolve()), "note": "Contains private learning evidence; not encrypted"}
    if cmd == "configure":
        return configure(store, args.url, args.token_env, args.allow_loopback_http)
    if cmd == "configure-ssh":
        return configure_ssh(store, args.ssh, args.python, args.service)
    if cmd == "sync":
        return synchronize(store)
    if cmd == "prune":
        return store.prune(args.days)
    if cmd == "hook":
        return hook(store, args.host, read_json("-"))
    if cmd == "install-hooks":
        return install_hooks(store, args.host, args.config, args.apply)
    if cmd == "worker":
        from assets import flush as flush_images
        if args.interval < 0.2:
            raise LedgerError("Worker interval must be at least 0.2 seconds")
        retry_after, failures, last_report = 0, 0, None
        sync_report = {}
        while True:
            with store.db:
                store.set_meta("worker_pid", os.getpid())
                store.set_meta("worker_heartbeat", now())
            report = {"capture": drain_all(store)}
            if time.monotonic() >= retry_after:
                if store.meta("asset_ssh"):
                    # Independent image outbox. One image per pass.
                    report["images"] = flush_images(store, 1)
                try:
                    sync_report = {"sync": synchronize(store)}
                    failures = 0
                    today = now()[:10]
                    if store.meta("last_prune") != today:
                        store.prune()
                        with store.db:
                            store.set_meta("last_prune", today)
                except LedgerError as e:
                    failures += 1
                    sync_report = {"sync_error": str(e)}
                retry_after = time.monotonic() + min(60, max(5, 2 ** min(failures, 6)))
            report.update(sync_report)
            signature = canonical(report)
            if signature != last_report:
                output(report)
                sys.stdout.flush()
                last_report = signature
            if args.once:
                return {"worker": "one pass completed", "status": store.status()}
            time.sleep(args.interval)
    raise LedgerError("Unknown command")


def main():
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    args = parser().parse_args()
    store = None
    try:
        store = Ledger(args.home, args.profile)
        result = execute(args, store)
        output(result)
        return 0
    except KeyboardInterrupt:
        return 130
    except (LedgerError, OSError, ValueError, __import__("sqlite3").Error) as e:
        # Do not print local data, tokens, or HTTP response bodies in diagnostics.
        message = str(e) if isinstance(e, LedgerError) else type(e).__name__ + ": local operation failed; check input/storage"
        if args.command == "hook":
            output({"decision": "block", "reason": "Learning capture failed: " + message})
        print("learning-tutor: " + message, file=sys.stderr)
        return 2
    finally:
        if store:
            store.close()


if __name__ == "__main__":
    sys.exit(main())
