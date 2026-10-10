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
from capture import drain, hook
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
    a.add_argument("--include-last-user", action="store_true", help="Include only the initiating user message in the explicitly bound transcript")
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
    a = sub.add_parser("sync")
    a.add_argument("--pull-only", action="store_true", help="Read remote history without uploading local events")
    a = sub.add_parser("flush", help="Explicit one-shot upload of a stopped chat's existing complete records/images; never restarts capture")
    a.add_argument("--host", required=True, choices=["codex", "claude", "openclaw"])
    a.add_argument("--host-session", required=True)
    a.add_argument("--budget", type=int, default=180, help="Total foreground budget in seconds (1-600); no background retry")
    a = sub.add_parser("reconcile", help="Offline stopped-chat repair from an agent-verified Codex host read; not automatic capture")
    a.add_argument("--host", required=True, choices=["codex"])
    a.add_argument("--host-session", required=True)
    a.add_argument("--json", required=True, help="Verified codex_app.read_thread packet; never fabricated completion evidence")
    a = sub.add_parser("tick", help="One bounded capture/delivery event; never loops")
    a.add_argument("--host", required=True, choices=["codex", "claude", "openclaw"])
    a.add_argument("--host-session", required=True)
    a.add_argument("--complete", action="store_true", help="Only after a verified successful host turn")
    a.add_argument("--last-assistant-message")
    a.add_argument("--capture-only", action="store_true")
    a = sub.add_parser("prune")
    a.add_argument("--days", type=int, default=30)
    a = sub.add_parser("hook")
    a.add_argument("--host", required=True, choices=["codex", "claude"])
    a.add_argument("--phase", choices=["all", "capture", "upload"], default="all")
    a = sub.add_parser("install-hooks")
    a.add_argument("--host", choices=["codex", "claude"], required=True)
    a.add_argument("--config", required=True, help="Exact hooks.json / settings.json path")
    a.add_argument("--apply", action="store_true", help="Default is preview only; existing entries preserved")
    a.add_argument("--commands-dir", help="Claude only: explicitly install /learn-start and /learn-stop aliases into this directory")
    return p


def install_hooks(store, host, config_path, apply=False, commands_dir=None):
    import shlex
    import tempfile
    path = Path(config_path).expanduser().resolve()
    previous = path.read_text(encoding="utf-8") if path.exists() else "{}"
    config = json.loads(previous)
    if not isinstance(config, dict) or not isinstance(config.get("hooks", {}), dict):
        raise LedgerError("Hook configuration must be an object")
    command_files = {}
    if commands_dir:
        if host != "claude":
            raise LedgerError("Native command aliases apply only to Claude")
        destination = Path(commands_dir).expanduser().resolve()
        templates = Path(__file__).parent / "hooks" / "claude-commands"
        for name in ("learn-start.md", "learn-stop.md"):
            target = destination / name
            content = (templates / name).read_text().replace("SKILL_ROOT", str(Path(__file__).resolve().parents[1]))
            if target.exists() and "<!-- learning-tutor owned command -->" not in target.read_text():
                raise LedgerError("Existing custom slash command preserved; choose another commands directory")
            command_files[str(target)] = content
    legacy_args = [sys.executable, str(Path(__file__).resolve()), "--home", str(store.home), "--profile", store.profile, "hook", "--host", host]
    args = [sys.executable, str(Path(__file__).parent / "hooks" / (host + ".py")), "--home", str(store.home), "--profile", store.profile, "hook"]
    def command(phase):
        parts = args + ["--phase", phase]
        return subprocess.list2cmdline(parts) if os.name == "nt" else " ".join(shlex.quote(x) for x in parts)
    legacy_command = subprocess.list2cmdline(legacy_args) if os.name == "nt" else " ".join(shlex.quote(x) for x in legacy_args)
    hooks = config.setdefault("hooks", {})
    events = ("SessionStart", "UserPromptSubmit", "PostToolUse", "Stop", "SessionEnd", "Interrupt" if host == "codex" else "StopFailure")
    for event in events:
        entries = hooks.setdefault(event, [])
        if not isinstance(entries, list):
            raise LedgerError("Hook entries must be lists")
        # Reconcile only exact owned handlers, including timing changes on upgrade.
        owned_commands = {legacy_command, command("capture"), command("upload")}
        for row in entries:
            row["hooks"] = [h for h in row.get("hooks", []) if h.get("command") not in owned_commands]
        entries[:] = [row for row in entries if row.get("hooks")]
        if not any(any(h.get("command") == command("capture") for h in row.get("hooks", [])) for row in entries):
            handlers = [{"type": "command", "command": command("capture")}]
            if event not in {"SessionEnd", "Interrupt", "StopFailure"}:
                handlers.append({"type": "command", "command": command("upload"), "async": event != "Stop", "timeout": 35 if event == "Stop" else 15})
            entries.append({"hooks": handlers})
    result = {"mode": "preview", "path": str(path), "config": config,
              "note": "Host restart/reload and real-turn verification required. Synchronous capture; bounded synchronous Stop upload before host teardown; other uploads async. No worker. Async notices are relayed by status/next synchronous hook."}
    if command_files:
        result["command_files"] = command_files
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
        for filename, content in command_files.items():
            target = Path(filename)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and target.read_text() != content:
                backup = target.with_name(target.name + ".learning-tutor-" + str(time.time_ns()) + ".bak")
                shutil.copyfile(target, backup)
            target.write_text(content)
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
                "state": "local-only until API is configured", "next": "Start a learning session and install the matching host hooks; complete turns sync on events."}
    if cmd == "status":
        from assets import status as image_status
        return {**store.status(), "images": image_status(store)}
    if cmd == "doctor":
        return doctor(store)
    if cmd == "start":
        if args.host != "manual" and (not args.host_session or not args.transcript):
            raise LedgerError("Host capture requires an explicit host-session ID and transcript path")
        result = store.start(args.key, args.title, args.host, args.host_session, args.transcript, args.include_last_user)
        if args.include_last_user and args.host != "manual":
            drain(store, args.host, args.host_session)
        return result
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
        return synchronize(store, pull_only=args.pull_only)
    if cmd == "flush":
        from delivery import flush_stopped
        return flush_stopped(store, args.host, args.host_session, args.budget)
    if cmd == "reconcile":
        from reconcile import reconcile_stopped
        return reconcile_stopped(store, args.host, args.host_session, read_json(args.json))
    if cmd == "prune":
        return store.prune(args.days)
    if cmd == "hook":
        return hook(store, args.host, read_json("-"), args.phase)
    if cmd == "install-hooks":
        return install_hooks(store, args.host, args.config, args.apply, args.commands_dir)
    if cmd == "tick":
        if not store.binding(args.host, args.host_session):
            return {"state": "not recording; upload frozen"}
        result = drain(store, args.host, args.host_session)
        from delivery import complete, deliver
        if args.complete:
            complete(store, args.host, args.host_session, last_text=args.last_assistant_message)
        if not args.capture_only:
            result["upload"] = deliver(store, args.host, args.host_session)
        return result
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
            # Capture failure is a diagnostic, not a request to restart the model's Stop loop.
            output({"systemMessage": "Learning capture failed: " + message})
            return 0
        print("learning-tutor: " + message, file=sys.stderr)
        return 2
    finally:
        if store:
            store.close()


if __name__ == "__main__":
    sys.exit(main())
