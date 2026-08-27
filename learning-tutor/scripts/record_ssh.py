"""Record RPC over an explicitly configured, authenticated OpenSSH connection."""
import json
import re
import shlex
import subprocess
import tempfile

from ledger import LedgerError, canonical

MAX_REQUEST = 4 * 1024 * 1024 + 4096
MAX_RESPONSE = 16 * 1024 * 1024


def settings(host, python, service):
    if not isinstance(host, str) or not re.fullmatch(r"[a-zA-Z0-9_][a-zA-Z0-9_.@-]{0,199}", host):
        raise LedgerError("Use an SSH alias or user@hostname")
    for path in (python, service):
        if not isinstance(path, str) or not path.startswith("/") or any(c in path for c in "\r\n\x00"):
            raise LedgerError("Remote Python and service require absolute POSIX paths")
    return dict(transport="ssh", host=host, python=python, service=service)


def request(config, profile, path, body, timeout=90):
    config = settings(config.get("host"), config.get("python"), config.get("service"))
    payload = canonical(dict(v=1, profile=profile, path=path, body=body)).encode()
    if len(payload) > MAX_REQUEST:
        raise LedgerError("Record request exceeds size limit")
    command = shlex.quote(config["python"]) + " " + shlex.quote(config["service"])
    # Temporary files avoid buffering an arbitrary SSH stderr/response in RAM.
    with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
        try:
            result = subprocess.run(["ssh", "-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
                                     "-o", "ConnectTimeout=8", config["host"], command],
                                    input=payload, stdout=output, stderr=errors, timeout=timeout)
        except (OSError, subprocess.TimeoutExpired):
            raise LedgerError("Record SSH connection failed; local events remain pending") from None
        output.seek(0)
        raw = output.read(MAX_RESPONSE + 1)
    if len(raw) > MAX_RESPONSE:
        raise LedgerError("Oversized record response")
    try:
        response = json.loads(raw)
    except (ValueError, UnicodeError):
        raise LedgerError("Record service returned invalid JSON; check SSH/service") from None
    if not isinstance(response, dict) or response.get("ok") is not True or result.returncode:
        code = response.get("code") if isinstance(response, dict) else None
        safe_codes = {"invalid_request", "invalid_event", "conflict", "reference", "identity", "storage", "page_budget"}
        suffix = code if isinstance(code, str) and code in safe_codes else "service_error"
        raise LedgerError("Record service rejected request: " + suffix)
    if "result" not in response:
        raise LedgerError("Record service omitted its result")
    return response["result"]
