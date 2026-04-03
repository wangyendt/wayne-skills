# Conversation Tracking

This document describes the best-effort conversation capture flow used by the Week Report System.

## Core Principle

Conversation tracking is **best-effort**, not guaranteed.

- It works only when the host agent invokes this skill or its scripts
- It should never block the user response
- Important conversations should still be explicitly ingested as materials

## Output Files

For a given ISO week:

```text
{year}/week{WW}/
├── materials/{YYYYMMDD}-{guid}.jsonl
└── {YYYYMMDD}-{guid}.txt
```

- `materials/*.jsonl` stores structured events
- `*.txt` stores a readable digest for quick browsing and legacy compatibility

## Local Observability Files

Outside the Git repo, the recorder keeps lightweight status files in `~/.week-report-repo/`:

- `last_sync_status.json`: last success or failure
- `local_queue.jsonl`: failed capture attempts retained for debugging or replay

## Best-Effort Recording Process

1. Reuse or create a session GUID from `/tmp/week_report_session.txt`
2. Reuse or create the current calendar date from `/tmp/week_report_session_date.txt`
3. Compress the user message when needed
4. Summarize the assistant response into a short outcome
5. Build a `conversation` material event
6. Append the event to both:
   - `materials/{YYYYMMDD}-{guid}.jsonl`
   - `{YYYYMMDD}-{guid}.txt`
7. Try `pull -> append -> commit -> push`
8. If sync fails, update local status files and swallow the exception

## Session and Date Behavior

- The session GUID may stay the same within the active session window
- File naming is still split by calendar date
- If the same session crosses midnight, the next event goes to a new daily file such as:
  - `20260403-02a24577.txt`
  - `20260404-02a24577.txt`

## Conversation Event Shape

```json
{
  "timestamp": "2026-04-03T20:40:00+08:00",
  "source_type": "conversation",
  "project": "optional project name",
  "title": "Work conversation",
  "summary": "Compressed user request",
  "evidence": [],
  "tags": ["conversation"],
  "outcome": "Short assistant outcome summary",
  "next_actions": [],
  "content": "Optional compressed context",
  "metadata": {
    "session_guid": "02a24577"
  }
}
```

## Digest Format

```text
# Material Log: 02a24577
# Date: 2026-04-03 20:40:00
# Week: 2026-W14

## [20:40:00] conversation | rayneo_hotword_tflm
Title: Work conversation
Summary: 定位在线离线 TFLite 输出不一致
Outcome: 已确认问题收敛到 Xtensa FC per-channel 路径实现差异
Tags: conversation, debug, tflite
```

## Privacy Filter

Skip recording only for strong-sensitive phrases:

- `password`
- `private key`
- `api key`
- `personal access token`
- `credential`
- `不要记录`
- `off record`

Generic engineering words like `token` should not automatically suppress logging.
