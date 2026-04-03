#!/usr/bin/env python3
"""
CLI for explicitly ingesting weekly report materials.
"""

import argparse
import logging
from typing import Dict

try:
    from conversation_logger import WeekReportRecorder, build_material_event
    from git_operations import create_git_manager
except ImportError:  # pragma: no cover - script/package dual use
    from .conversation_logger import WeekReportRecorder, build_material_event
    from .git_operations import create_git_manager


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def _parse_metadata(entries) -> Dict[str, str]:
    metadata: Dict[str, str] = {}
    for item in entries:
        if "=" not in item:
            metadata[item] = ""
            continue
        key, value = item.split("=", 1)
        metadata[key] = value
    return metadata


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ingest a material into the week report repository.")
    subparsers = parser.add_subparsers(dest="source_type", required=True)

    conversation = subparsers.add_parser("conversation", help="Capture a conversation material")
    conversation.add_argument("--project", default="")
    conversation.add_argument("--tag", action="append", default=[])
    conversation.add_argument("--evidence", action="append", default=[])
    conversation.add_argument("--next-action", action="append", default=[])
    conversation.add_argument("--user-message", required=True)
    conversation.add_argument("--assistant-response", required=True)

    for name in ["document", "repo-activity"]:
        parser_i = subparsers.add_parser(name, help=f"Capture a {name} material")
        parser_i.add_argument("--project", default="")
        parser_i.add_argument("--title", required=True)
        parser_i.add_argument("--summary", required=True)
        parser_i.add_argument("--outcome", default="")
        parser_i.add_argument("--content", default="")
        parser_i.add_argument("--tag", action="append", default=[])
        parser_i.add_argument("--evidence", action="append", default=[])
        parser_i.add_argument("--next-action", action="append", default=[])
        parser_i.add_argument("--metadata", action="append", default=[], help="key=value, repeatable")

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    git = create_git_manager()
    if not git:
        logger.error("Missing Git environment variables for week report system")
        return 1

    recorder = WeekReportRecorder(git)

    if args.source_type == "conversation":
        success = recorder.record_conversation(
            args.user_message,
            args.assistant_response,
            project=args.project,
            tags=args.tag,
            evidence=args.evidence,
            next_actions=args.next_action,
        )
        return 0 if success else 1

    source_type = "repo_activity" if args.source_type == "repo-activity" else "document"
    event = build_material_event(
        source_type=source_type,
        title=args.title,
        summary=args.summary,
        project=args.project,
        tags=args.tag,
        evidence=args.evidence,
        outcome=args.outcome,
        next_actions=args.next_action,
        content=args.content,
        metadata=_parse_metadata(args.metadata),
    )
    success = recorder.record_event(event)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
