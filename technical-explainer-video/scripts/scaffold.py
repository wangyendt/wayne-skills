#!/usr/bin/env python3
"""Copy the runnable starter without installing dependencies or overwriting files."""
import argparse
import json
import shutil
import runpy
import wave
from pathlib import Path


def scaffold(destination):
    destination = Path(destination).expanduser().resolve()
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError(f"Destination must be absent or empty: {destination}")
    source = Path(__file__).resolve().parents[1] / "assets/starter"
    shutil.copytree(source, destination, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "node_modules", ".venv", "output", "audio"))
    (destination / "audio").mkdir(exist_ok=True)
    (destination / "output").mkdir(exist_ok=True)
    timing = json.loads((destination / "src/timing.json").read_text())
    # Deliberately silent: runnable layout smoke test, not finished narration.
    with wave.open(str(destination / "audio/narration.wav"), "wb") as out:
        out.setparams((2, 2, 48000, 0, "NONE", "not compressed"))
        out.writeframes(b"\0" * round(timing["total_duration"] * 48000) * 4)
    (destination / "audio/status.json").write_text(json.dumps({"narrated": False, "purpose": "layout-smoke-test"}))
    helpers = runpy.run_path(str(destination / "scripts/prepare_audio.py"))
    cues = json.loads((destination / "src/subtitles.json").read_text())
    helpers["write_subtitles"](cues, destination / "output")
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination")
    args = parser.parse_args()
    try:
        print(scaffold(args.destination))
    except ValueError as error:
        parser.exit(2, str(error) + "\n")
