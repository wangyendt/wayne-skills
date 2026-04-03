#!/usr/bin/env python3
"""
Conversation and material logger for the Week Report System.

This module stores structured weekly-report materials in JSONL form and keeps a
human-readable digest for quick inspection and backward compatibility.
"""

import argparse
import json
import logging
import os
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from git_operations import create_git_manager
except ImportError:  # pragma: no cover - script/package dual use
    from .git_operations import create_git_manager


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SessionManager:
    """Manage a coarse-grained session id shared across one active chat session."""

    SESSION_FILE = "/tmp/week_report_session.txt"
    SESSION_DATE_FILE = "/tmp/week_report_session_date.txt"
    SESSION_TTL_SECONDS = 86400

    @classmethod
    def _read_recent_value(cls, path: str) -> Optional[str]:
        if not os.path.exists(path):
            return None

        try:
            file_time = os.path.getmtime(path)
            if (datetime.now().timestamp() - file_time) >= cls.SESSION_TTL_SECONDS:
                return None

            with open(path, 'r', encoding='utf-8') as handle:
                value = handle.read().strip()
            return value or None
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to read session file %s: %s", path, exc)
            return None

    @classmethod
    def _write_value(cls, path: str, value: str) -> None:
        try:
            with open(path, 'w', encoding='utf-8') as handle:
                handle.write(value)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to write session file %s: %s", path, exc)

    @classmethod
    def get_or_create_guid(cls) -> str:
        guid = cls._read_recent_value(cls.SESSION_FILE)
        if guid:
            return guid

        guid = uuid.uuid4().hex[:8]
        cls._write_value(cls.SESSION_FILE, guid)
        return guid

    @classmethod
    def get_or_create_start_date(cls, reference_dt: Optional[datetime] = None) -> str:
        current_date = (reference_dt or datetime.now()).strftime("%Y%m%d")
        start_date = cls._read_recent_value(cls.SESSION_DATE_FILE)
        if start_date == current_date:
            return start_date

        # Split files by calendar day even if the same session crosses midnight.
        cls._write_value(cls.SESSION_DATE_FILE, current_date)
        return current_date

    @classmethod
    def reset(cls) -> None:
        for path in [cls.SESSION_FILE, cls.SESSION_DATE_FILE]:
            if os.path.exists(path):
                os.remove(path)


class PrivacyFilter:
    """Skip only for strong-sensitive phrases to reduce false positives."""

    SKIP_PHRASES = [
        'password',
        'private key',
        'api key',
        'personal access token',
        'credential',
        "don't record",
        'off record',
        'off the record',
        '不要记录',
        '跳过记录',
        '私密',
    ]

    @classmethod
    def should_skip(cls, texts: List[str]) -> bool:
        combined = "\n".join(text for text in texts if text).lower()
        return any(phrase in combined for phrase in cls.SKIP_PHRASES)


class MessageCompressor:
    """Compress long user-provided content into a reusable material summary."""

    MAX_LENGTH = 500

    @classmethod
    def compress(cls, message: str) -> str:
        if len(message) <= cls.MAX_LENGTH:
            return message.strip()

        # Keep lines with obvious requests, outcomes, or constraints.
        lines = [line.strip() for line in message.splitlines() if line.strip()]
        indicators = [
            '需要', '要求', '请', '帮我', '如何', '怎么', '总结', '纳入', 'repo',
            'plan', 'experiment', 'debug', 'issue', 'pr', 'commit',
            'need', 'please', 'help', 'how', 'why', 'summary'
        ]

        selected: List[str] = []
        for line in lines:
            lowered = line.lower()
            if any(indicator in lowered for indicator in indicators):
                selected.append(line)
            if len(" ".join(selected)) >= cls.MAX_LENGTH:
                break

        compressed = " ".join(selected) if selected else " ".join(lines[:5])
        compressed = re.sub(r'\s+', ' ', compressed).strip()

        if len(compressed) > cls.MAX_LENGTH:
            compressed = compressed[:cls.MAX_LENGTH - 3] + "..."

        return compressed or message[:cls.MAX_LENGTH - 3] + "..."


class ResponseSummarizer:
    """Condense an assistant response into a short outcome statement."""

    MAX_CHARS = 300

    @classmethod
    def summarize(cls, response: str) -> str:
        text = re.sub(r'```.*?```', ' ', response, flags=re.S)
        text = re.sub(r'\s+', ' ', text).strip()
        if not text:
            return "AI provided assistance."

        # Split conservatively and keep the first few meaningful fragments.
        fragments = [frag.strip() for frag in re.split(r'[。！？!?]\s*', text) if frag.strip()]
        summary = "。".join(fragments[:3]).strip()
        if not summary:
            summary = text
        if len(summary) > cls.MAX_CHARS:
            summary = summary[:cls.MAX_CHARS - 3] + "..."
        return summary


@dataclass
class MaterialEvent:
    timestamp: str
    source_type: str
    title: str
    summary: str
    project: str = ""
    evidence: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    outcome: str = ""
    next_actions: List[str] = field(default_factory=list)
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_json_line(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False) + "\n"

    @property
    def dt(self) -> datetime:
        return datetime.fromisoformat(self.timestamp)


class SyncStatusTracker:
    """Persist local sync status for observability."""

    ROOT = Path.home() / ".week-report-repo"
    STATUS_FILE = ROOT / "last_sync_status.json"
    QUEUE_FILE = ROOT / "local_queue.jsonl"

    @classmethod
    def _ensure_root(cls) -> None:
        cls.ROOT.mkdir(parents=True, exist_ok=True)

    @classmethod
    def update_success(cls, payload: Dict[str, Any]) -> None:
        cls._ensure_root()
        status = {
            "status": "success",
            "updated_at": datetime.now().isoformat(timespec='seconds'),
            **payload,
        }
        cls.STATUS_FILE.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding='utf-8')

    @classmethod
    def update_failure(cls, payload: Dict[str, Any]) -> None:
        cls._ensure_root()
        status = {
            "status": "failed",
            "updated_at": datetime.now().isoformat(timespec='seconds'),
            **payload,
        }
        cls.STATUS_FILE.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding='utf-8')
        with cls.QUEUE_FILE.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(status, ensure_ascii=False) + "\n")


class MaterialFormatter:
    """Derive repo-relative paths and digest content."""

    @staticmethod
    def get_week_path(ts: datetime) -> str:
        week = ts.isocalendar()
        return f"{week[0]}/week{week[1]:02d}"

    @staticmethod
    def material_path(ts: datetime, start_date: str, guid: str) -> str:
        week_path = MaterialFormatter.get_week_path(ts)
        return f"{week_path}/materials/{start_date}-{guid}.jsonl"

    @staticmethod
    def digest_path(ts: datetime, start_date: str, guid: str) -> str:
        week_path = MaterialFormatter.get_week_path(ts)
        return f"{week_path}/{start_date}-{guid}.txt"

    @staticmethod
    def format_digest_header(guid: str, ts: datetime) -> str:
        week = ts.isocalendar()
        return (
            f"# Material Log: {guid}\n"
            f"# Date: {ts.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"# Week: {week[0]}-W{week[1]:02d}\n\n"
        )

    @staticmethod
    def format_digest_entry(event: MaterialEvent) -> str:
        ts = event.dt.strftime("%H:%M:%S")
        project = event.project or "-"
        tags = ", ".join(event.tags) if event.tags else "-"
        evidence = ", ".join(event.evidence) if event.evidence else "-"
        next_actions = "; ".join(event.next_actions) if event.next_actions else "-"

        return (
            f"## [{ts}] {event.source_type} | {project}\n"
            f"Title: {event.title}\n"
            f"Summary: {event.summary}\n"
            f"Outcome: {event.outcome or '-'}\n"
            f"Evidence: {evidence}\n"
            f"Tags: {tags}\n"
            f"Next: {next_actions}\n\n"
        )


class WeekReportRecorder:
    """Capture structured materials and sync them to the Git-backed repository."""

    def __init__(self, git_manager):
        self.git = git_manager

    def record_event(
        self,
        event: MaterialEvent,
        *,
        session_guid: Optional[str] = None,
        session_start_date: Optional[str] = None,
        max_retries: int = 3,
    ) -> bool:
        if PrivacyFilter.should_skip([event.title, event.summary, event.outcome, event.content]):
            logger.info("Skipping material capture for privacy")
            SyncStatusTracker.update_success({
                "reason": "skipped_privacy",
                "source_type": event.source_type,
                "title": event.title,
            })
            return True

        guid = session_guid or SessionManager.get_or_create_guid()
        start_date = session_start_date or SessionManager.get_or_create_start_date(event.dt)
        material_path = MaterialFormatter.material_path(event.dt, start_date, guid)
        digest_path = MaterialFormatter.digest_path(event.dt, start_date, guid)
        week_path = MaterialFormatter.get_week_path(event.dt)

        try:
            self.git.pull()

            digest_full_path = os.path.join(self.git.repo_path, digest_path)
            if not os.path.exists(digest_full_path):
                self.git.append_to_file(digest_path, MaterialFormatter.format_digest_header(guid, event.dt))

            self.git.append_to_file(material_path, event.to_json_line())
            self.git.append_to_file(digest_path, MaterialFormatter.format_digest_entry(event))

            commit_message = f"Capture {event.source_type} {guid} [{week_path}]"
            success = self.git.commit_and_push(commit_message, max_retries=max_retries)

            payload = {
                "source_type": event.source_type,
                "project": event.project,
                "title": event.title,
                "guid": guid,
                "week_path": week_path,
                "material_path": material_path,
                "digest_path": digest_path,
            }
            if success:
                SyncStatusTracker.update_success(payload)
                logger.info("Captured material: %s", material_path)
            else:
                SyncStatusTracker.update_failure({**payload, "error": "commit_or_push_failed"})
                logger.warning("Failed to sync material after retries: %s", material_path)
            return success
        except Exception as exc:  # pragma: no cover - defensive
            payload = {
                "source_type": event.source_type,
                "project": event.project,
                "title": event.title,
                "guid": guid,
                "week_path": week_path,
                "material_path": material_path,
                "digest_path": digest_path,
                "error": str(exc),
                "event": asdict(event),
            }
            SyncStatusTracker.update_failure(payload)
            logger.error("Error capturing material: %s", exc)
            return False

    def record_conversation(
        self,
        user_message: str,
        assistant_response: str,
        *,
        project: str = "",
        tags: Optional[List[str]] = None,
        evidence: Optional[List[str]] = None,
        next_actions: Optional[List[str]] = None,
    ) -> bool:
        event = MaterialEvent(
            timestamp=datetime.now().isoformat(timespec='seconds'),
            source_type="conversation",
            title="Work conversation",
            summary=MessageCompressor.compress(user_message),
            project=project,
            evidence=evidence or [],
            tags=['conversation', *(tags or [])],
            outcome=ResponseSummarizer.summarize(assistant_response),
            next_actions=next_actions or [],
            content=MessageCompressor.compress(user_message),
            metadata={"session_guid": SessionManager.get_or_create_guid()},
        )
        return self.record_event(event)

    def load_week_materials(self, year: int, week: int) -> List[Dict[str, Any]]:
        """Read structured materials for a week from the local repo clone."""
        week_root = Path(self.git.repo_path) / f"{year}/week{week:02d}/materials"
        if not week_root.exists():
            return []

        items: List[Dict[str, Any]] = []
        for path in sorted(week_root.glob("*.jsonl")):
            with path.open('r', encoding='utf-8') as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        items.append(json.loads(line))
                    except json.JSONDecodeError:
                        logger.warning("Skipping malformed JSONL line in %s", path)
        items.sort(key=lambda item: item.get("timestamp", ""))
        return items


def build_material_event(
    source_type: str,
    title: str,
    summary: str,
    *,
    project: str = "",
    tags: Optional[List[str]] = None,
    evidence: Optional[List[str]] = None,
    outcome: str = "",
    next_actions: Optional[List[str]] = None,
    content: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> MaterialEvent:
    return MaterialEvent(
        timestamp=datetime.now().isoformat(timespec='seconds'),
        source_type=source_type,
        title=title,
        summary=MessageCompressor.compress(summary),
        project=project,
        evidence=evidence or [],
        tags=tags or [],
        outcome=ResponseSummarizer.summarize(outcome) if outcome else "",
        next_actions=next_actions or [],
        content=MessageCompressor.compress(content) if content else "",
        metadata=metadata or {},
    )


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Capture a conversation material for week reports.")
    parser.add_argument("--project", default="", help="Project or workstream name")
    parser.add_argument("--tag", action="append", default=[], help="Tag, repeatable")
    parser.add_argument("--evidence", action="append", default=[], help="Evidence item, repeatable")
    parser.add_argument("--next-action", action="append", default=[], help="Next action, repeatable")
    parser.add_argument("--user-message", required=True, help="Original user message")
    parser.add_argument("--assistant-response", required=True, help="Assistant response")
    return parser


def main() -> int:
    parser = _build_arg_parser()
    args = parser.parse_args()

    git = create_git_manager()
    if not git:
        logger.error("Missing Git environment variables for week report system")
        return 1

    recorder = WeekReportRecorder(git)
    success = recorder.record_conversation(
        args.user_message,
        args.assistant_response,
        project=args.project,
        tags=args.tag,
        evidence=args.evidence,
        next_actions=args.next_action,
    )
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
