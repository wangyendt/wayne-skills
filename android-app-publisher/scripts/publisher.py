#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx[socks]>=0.27,<1", "keyring>=25,<26", "qrcode[pil]>=8,<9"]
# ///
"""One-time credentials, APK inspection/build/publication, app listing and local QR."""
from __future__ import annotations

import argparse
import getpass
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit

import httpx
import keyring
import qrcode

from apk_info import inspect_apk

DEFAULT_URL = "https://hx470.tail986e72.ts.net:8443"
SERVICE = "android-app-publisher"
TOKEN_RE = re.compile(r"apub_[0-9a-f]{16}\.[A-Za-z0-9_-]{43}")


def config_dir():
    return Path(os.environ.get("ANDROID_APP_PUBLISHER_CONFIG", str(Path.home() / ".config/android-app-publisher"))).expanduser().resolve()


def private_write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink():
        raise ValueError("Private configuration path must not be a symlink")
    fd, temp = tempfile.mkstemp(prefix=".publisher-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(text)
        os.chmod(temp, 0o600)
        os.replace(temp, path)
    finally:
        Path(temp).unlink(missing_ok=True)


def canonical_url(value):
    parts = urlsplit(value)
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError("API URL must be HTTPS, without credentials, query parameters or fragment")
    if parts.path.rstrip("/"):
        raise ValueError("Use an API origin URL, not a path")
    return value.rstrip("/")


def load_config():
    path = config_dir() / "config.json"
    if not path.exists():
        raise ValueError("Run init once on this computer before using the publication API")
    data = json.loads(path.read_text())
    data["url"] = canonical_url(data["url"])
    return data


def keyring_ready():
    backend = keyring.get_keyring()
    module = type(backend).__module__.lower()
    # No keyrings.alt/plaintext/fail/chainer fallback: explicitly choose the OS store.
    return any(module.startswith(prefix) for prefix in (
        "keyring.backends.macos", "keyring.backends.windows", "keyring.backends.secretservice",
        "keyring.backends.kwallet")) and getattr(backend, "priority", 0) > 0


def load_token(config):
    if config["credential_store"] == "keyring":
        if not keyring_ready():
            raise ValueError("An OS credential-store backend is unavailable; rerun init on this computer")
        token = keyring.get_password(SERVICE, config["url"])
    else:
        path = config_dir() / "token"
        if path.is_symlink() or (os.name != "nt" and stat.S_IMODE(path.stat().st_mode) & 0o077):
            raise ValueError("Token file must be a regular private file (0600)")
        token = path.read_text().strip()
    if not token or not TOKEN_RE.fullmatch(token):
        raise ValueError("Publication token missing or malformed; rerun init")
    return token


class Api:
    def __init__(self, url, token):
        self.url = canonical_url(url)
        self.token = token

    def call(self, method, path, body=None):
        try:
            response = httpx.request(method, self.url + path, json=body,
                                     headers={"Authorization": "Bearer " + self.token},
                                     timeout=httpx.Timeout(300, connect=20), follow_redirects=False)
        except httpx.HTTPError as exc:
            raise ValueError(f"API network error ({type(exc).__name__}); check service availability") from None
        if not 200 <= response.status_code < 300:
            # Never echo a remote body: it could contain tokens, URLs or injected text.
            hints = {401: "Token invalid or revoked; rerun init", 404: "App or upload not found",
                     409: "Version/signature or concurrent-publication conflict; inspect current app",
                     410: "Upload session expired", 413: "Request too large",
                     422: "APK or request validation failed", 429: "Rate limited; wait before retrying",
                     503: "Service OSS configuration is not ready"}
            raise ValueError(f"API HTTP {response.status_code}: " + hints.get(response.status_code, "Operation failed; inspect upload status before retrying"))
        return response.json()


def init(args):
    url = canonical_url(args.url)
    if args.token_stdin:
        token = sys.stdin.readline(256).strip()
    else:
        if not sys.stdin.isatty():
            raise ValueError("Run init in your terminal for hidden token input; use --token-stdin only for a trusted pipe")
        token = getpass.getpass("Publication token (hidden, not sent to the chat): ").strip()
    if not TOKEN_RE.fullmatch(token):
        raise ValueError("Malformed publication token")
    # Validate authentication before replacing a previously working credential.
    Api(url, token).call("GET", "/v1/apps")
    if args.credential_store == "keyring":
        if not keyring_ready():
            raise ValueError("OS credential store unavailable. Configure one, or explicitly choose --credential-store file (private 0600 file)")
        keyring.set_password(SERVICE, url, token)
        (config_dir() / "token").unlink(missing_ok=True)
    else:
        private_write(config_dir() / "token", token + "\n")
    private_write(config_dir() / "config.json", json.dumps({"url": url, "credential_store": args.credential_store}, indent=2) + "\n")
    return {"initialized": True, "url": url, "credential_store": args.credential_store}


def build(args):
    project = Path(args.project).expanduser().resolve(strict=True)
    if not args.apk_output:
        raise ValueError("For project builds, explicitly provide --apk-output relative to the project root")
    output = (project / args.apk_output).resolve()
    if not output.is_relative_to(project):
        raise ValueError("APK output must be inside the project")
    tasks = args.gradle_task or ["assembleRelease"]
    if any(not re.fullmatch(r"[A-Za-z0-9_:-]+", task) for task in tasks):
        raise ValueError("Invalid Gradle task name")
    wrapper = project / ("gradlew.bat" if os.name == "nt" else "gradlew")
    if not wrapper.is_file():
        raise ValueError("Gradle wrapper not found in the selected project")
    env = dict(os.environ)
    studio_java = Path("/Applications/Android Studio.app/Contents/jbr/Contents/Home")
    if not env.get("JAVA_HOME") and studio_java.is_dir():
        env["JAVA_HOME"] = str(studio_java)
        env["PATH"] = str(studio_java / "bin") + os.pathsep + env.get("PATH", "")
    # Keep build output private: build systems may accidentally print credentials.
    config_dir().mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, log_path = tempfile.mkstemp(prefix="build-", suffix=".log", dir=config_dir())
    with os.fdopen(fd, "w") as handle:
        started = time.time_ns()
        proc = subprocess.run([str(wrapper), *tasks, "--rerun-tasks", "--console=plain"], cwd=project,
                              env=env, stdout=handle, stderr=subprocess.STDOUT, timeout=1800)
    if proc.returncode:
        raise ValueError(f"Build failed; private log: {log_path}")
    if not output.is_file():
        raise ValueError("Build succeeded but the explicitly selected APK output was not produced")
    if output.stat().st_mtime_ns < started:
        raise ValueError("Selected APK predates this build; use an assemble task that produces it, or explicitly publish it with --apk")
    return output


def qr(info, output):
    url = info["download_url"]
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.hostname or parts.query or parts.fragment or parts.username or parts.password:
        raise ValueError("Expected a public stable HTTPS download URL without credentials")
    path = Path(output).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    image = qrcode.make(url, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4)
    image.save(path, format="PNG")
    return {"app": info, "qr_path": str(path)}


def publish(args, api):
    apk = build(args) if args.project else Path(args.apk).expanduser().resolve(strict=True)
    info = inspect_apk(apk)
    if args.dry_run:
        return {"dry_run": True, "apk": str(apk), "app": info}
    fields = ("package", "version_code", "version_name", "sha256", "content_md5", "size", "certificate_sha256")
    prepared = api.call("POST", "/v1/uploads", {key: info[key] for key in fields})
    if prepared["already_published"]:
        published = prepared["app"]
    else:
        upload_id = prepared["upload_id"]
        private_write(config_dir() / "last-upload.json", json.dumps({"upload_id": upload_id, "package": info["package"], "sha256": info["sha256"]}) + "\n")
        parts = urlsplit(prepared["upload_url"])
        # Never transfer a publication token to OSS; validate that bytes go to OSS,
        # not to an arbitrary URL returned by an untrusted/misconfigured endpoint.
        if parts.scheme != "https" or not parts.hostname or not parts.hostname.endswith(".aliyuncs.com") or parts.username or parts.password:
            raise ValueError("Unexpected signed upload destination")
        try:
            with apk.open("rb") as handle:
                response = httpx.put(prepared["upload_url"], content=handle,
                                     headers={**prepared["headers"], "Content-Length": str(info["size"])},
                                     timeout=httpx.Timeout(900, connect=30), follow_redirects=False)
            if not 200 <= response.status_code < 300:
                raise ValueError(f"OSS upload returned HTTP {response.status_code}; upload session {upload_id}")
        except httpx.HTTPError as exc:
            raise ValueError(f"OSS upload error ({type(exc).__name__}); session {upload_id}; signed URL omitted") from None
        published = api.call("POST", f"/v1/uploads/{upload_id}/complete")
    result = {"app": published, "already_published": prepared["already_published"]}
    if args.qr:
        result.update(qr(published, args.qr))
    return result


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    setup = commands.add_parser("init", help="One-time hidden token entry and storage")
    setup.add_argument("--url", default=DEFAULT_URL)
    setup.add_argument("--credential-store", choices=["keyring", "file"], default="keyring")
    setup.add_argument("--token-stdin", action="store_true", help="Trusted pipe only; never use a token argument")
    inspect = commands.add_parser("inspect", help="Verify actual APK and print non-secret metadata")
    inspect.add_argument("apk")
    pub = commands.add_parser("publish")
    source = pub.add_mutually_exclusive_group(required=True)
    source.add_argument("--apk")
    source.add_argument("--project")
    pub.add_argument("--apk-output", help="Explicit project-relative build output; no newest-file guessing")
    pub.add_argument("--gradle-task", action="append", help="Repeat to run tests and assemble task")
    pub.add_argument("--dry-run", action="store_true", help="Build/inspect only; do not call API")
    pub.add_argument("--qr", help="Absolute local PNG output path")
    commands.add_parser("apps")
    commands.add_parser("doctor")
    show = commands.add_parser("show")
    show.add_argument("package")
    share = commands.add_parser("share")
    share.add_argument("package")
    share.add_argument("--output", required=True, help="Local PNG path")
    status = commands.add_parser("status")
    status.add_argument("upload_id", nargs="?", help="Defaults to the last local upload session")
    complete = commands.add_parser("complete", help="Retry finalization after checking a timed-out upload")
    complete.add_argument("upload_id")
    return root


def main():
    args = parser().parse_args()
    try:
        if args.command == "init":
            result = init(args)
        elif args.command == "inspect":
            result = inspect_apk(args.apk)
        elif args.command == "publish" and args.dry_run:
            result = publish(args, None)
        else:
            config = load_config()
            api = Api(config["url"], load_token(config))
            if args.command == "publish":
                result = publish(args, api)
            elif args.command == "apps":
                result = api.call("GET", "/v1/apps")
            elif args.command in ("show", "share"):
                from apk_info import PACKAGE
                if not PACKAGE.fullmatch(args.package):
                    raise ValueError("Invalid package name")
                result = api.call("GET", "/v1/apps/" + args.package)
                if args.command == "share":
                    result = qr(result, args.output)
            elif args.command in ("status", "complete"):
                upload_id = args.upload_id or json.loads((config_dir() / "last-upload.json").read_text())["upload_id"]
                if not re.fullmatch(r"[0-9a-f]{32}", upload_id):
                    raise ValueError("Invalid upload session ID")
                result = api.call("POST" if args.command == "complete" else "GET",
                                  f"/v1/uploads/{upload_id}" + ("/complete" if args.command == "complete" else ""))
            else:
                result = {"url": config["url"], "credential_store": config["credential_store"],
                          "authenticated": True, "apps": len(api.call("GET", "/v1/apps")["apps"])}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as exc:
        # Only our ValueError messages are intended for display. Other SDK or OS
        # exception strings can contain secret material and are never echoed.
        message = str(exc) if isinstance(exc, ValueError) else f"{type(exc).__name__}; inspect local setup without sharing credentials"
        print(json.dumps({"error": message}, ensure_ascii=False), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
