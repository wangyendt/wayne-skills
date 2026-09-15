"""Inspect real APK bytes with Android's tools, never trust filenames or sidecars."""
from __future__ import annotations

import base64
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess

PACKAGE = re.compile(r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+")


def android_tool(name: str) -> str:
    explicit = os.environ.get(name.upper() + "_PATH")
    if explicit:
        if not Path(explicit).is_file():
            raise ValueError(f"{name.upper()}_PATH does not name a file")
        return explicit
    found = shutil.which(name)
    if found:
        return found
    roots = [os.environ.get("ANDROID_HOME"), os.environ.get("ANDROID_SDK_ROOT"),
             str(Path.home() / "Library/Android/sdk"), str(Path.home() / "Android/Sdk"),
             str(Path(os.environ.get("LOCALAPPDATA", "")) / "Android/Sdk")]
    for root in filter(None, roots):
        folders = sorted((Path(root) / "build-tools").glob("*"),
                         key=lambda p: [int(n) for n in re.findall(r"\d+", p.name)], reverse=True)
        for folder in folders:
            for suffix in ("", ".bat", ".exe"):
                path = folder / (name + suffix)
                if path.is_file():
                    return str(path)
    raise ValueError(f"Missing Android SDK tool: {name}; install build-tools or set {name.upper()}_PATH")


def tool_output(name: str, args: list[str]) -> str:
    env = dict(os.environ)
    studio_java = Path("/Applications/Android Studio.app/Contents/jbr/Contents/Home")
    if not env.get("JAVA_HOME") and studio_java.is_dir():
        env["JAVA_HOME"] = str(studio_java)
        env["PATH"] = str(studio_java / "bin") + os.pathsep + env.get("PATH", "")
    result = subprocess.run([android_tool(name), *args], capture_output=True,
                            text=True, timeout=90, env=env)
    if result.returncode:
        # Tool output may contain arbitrary manifest strings: do not echo it to logs.
        raise ValueError(f"{name} validation failed (exit {result.returncode})")
    return result.stdout


def inspect_apk(path: str | Path, max_bytes: int = 256 * 1024 * 1024) -> dict:
    path = Path(path).resolve(strict=True)
    size = path.stat().st_size
    if not path.is_file() or not 0 < size <= max_bytes:
        raise ValueError("APK is empty or exceeds the size limit")
    sha, md5 = hashlib.sha256(), hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(block)
            md5.update(block)
    badging = tool_output("aapt", ["dump", "badging", str(path)])
    package_line = re.search(r"^package: (.+)$", badging, re.M)
    fields = dict(re.findall(r"(\w+)='([^']*)'", package_line.group(1))) if package_line else {}
    package = fields.get("name", "")
    if not PACKAGE.fullmatch(package):
        raise ValueError("Invalid APK package name")
    if fields.get("split") or re.search(r"^split=", badging, re.M):
        raise ValueError("Split APKs are not supported; publish a standalone APK")
    if "application-debuggable" in badging:
        raise ValueError("Debuggable APKs are not accepted for public publication")
    cert_output = tool_output("apksigner", ["verify", "--verbose", "--print-certs", str(path)])
    certs = sorted(set(s.lower() for s in re.findall(
        r"^Signer #\d+ certificate SHA-256 digest: ([0-9a-fA-F]{64})\s*$", cert_output, re.M)))
    if not certs:
        raise ValueError("APK has no verified signer certificate")
    if re.search(r"^Signer #\d+ certificate DN:.*CN=Android Debug(?:,|$)", cert_output, re.M):
        raise ValueError("Default Android debug signing certificate is not accepted")
    label = re.search(r"^application-label:'(.*)'$", badging, re.M)
    sdk = re.search(r"^sdkVersion:'(\d+)'$", badging, re.M)
    target = re.search(r"^targetSdkVersion:'(\d+)'$", badging, re.M)
    native = re.search(r"^native-code:(.*)$", badging, re.M)
    version_code = int(fields.get("versionCode", "0"))
    if version_code <= 0:
        raise ValueError("versionCode must be positive")
    return {"package": package, "name": (label.group(1) if label else package)[:160],
            "version_name": fields.get("versionName", "")[:160], "version_code": version_code,
            "min_sdk": int(sdk.group(1)) if sdk else None,
            "target_sdk": int(target.group(1)) if target else None,
            "abis": re.findall(r"'([^']*)'", native.group(1)) if native else [],
            "certificate_sha256": certs, "sha256": sha.hexdigest(),
            "content_md5": base64.b64encode(md5.digest()).decode(), "size": size}
