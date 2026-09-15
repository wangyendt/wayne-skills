import os
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "android-app-publisher/scripts"))
import publisher


def test_private_config_permissions_and_url_validation(tmp_path, monkeypatch):
    monkeypatch.setenv("ANDROID_APP_PUBLISHER_CONFIG", str(tmp_path))
    publisher.private_write(tmp_path / "token", "a secret")
    assert (tmp_path / "token").stat().st_mode & 0o777 == 0o600
    for url in ("http://host", "https://user:secret@host", "https://host?token=secret", "https://host/path"):
        with pytest.raises(ValueError):
            publisher.canonical_url(url)



def test_qr_does_not_accept_signed_url(tmp_path):
    for url in ("https://example.com/a.apk?Signature=secret", "https://user:secret@example.com/a.apk", "https://example.com/a.apk#secret"):
        with pytest.raises(ValueError):
            publisher.qr({"download_url": url}, tmp_path / "qr.png")



def test_build_rejects_stale_artifact(tmp_path, monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setenv("ANDROID_APP_PUBLISHER_CONFIG", str(tmp_path / "private"))
    project = tmp_path / "project"
    project.mkdir()
    output = project / "old.apk"
    output.write_bytes(b"old")
    os.utime(output, (1, 1))
    (project / "gradlew").write_text("#!/bin/sh\nexit 0\n")
    (project / "gradlew").chmod(0o755)
    args = SimpleNamespace(project=str(project), apk_output="old.apk", gradle_task=["test"])
    with pytest.raises(ValueError, match="predates"):
        publisher.build(args)
