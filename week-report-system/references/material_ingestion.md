# Material Ingestion

This document defines how to capture weekly report materials in a structured way.

## Why Materials Instead of Only Chat Logs

Weekly reports should be built from reusable work materials, not just raw conversation snippets.

## Hard Rules

1. If the user explicitly asks to include something in the weekly report materials, capture is mandatory.
2. The canonical record must be a structured JSONL material event.
3. `*.txt` is only a readable digest and must not replace JSONL as the canonical source.
4. Preserve date-based file splitting even when the same session GUID spans multiple calendar days.

Supported material types:

- `conversation`: normal work discussion with the AI
- `document`: plan, experiment note, meeting summary, design note, review note
- `repo_activity`: recent commits, PRs, issues, or reviews from a repository

## Recommended Trigger Phrases

Use this workflow when the user says things like:

- "把这次讨论纳入周报素材"
- "把这个 plan 记到本周周报"
- "把这个 experiment 总结成周报素材"
- "看这个 repo 最近 3 天提交，纳入本周周报"
- "把这份文档按项目整理进周报素材"

## Material Schema

Each captured event should contain the following fields whenever possible:

```json
{
  "timestamp": "2026-04-03T20:35:00+08:00",
  "source_type": "document",
  "project": "rayneo_hotword_tflm",
  "title": "Xtensa FC per-channel 对齐排查",
  "summary": "确认问题已收敛到 FC per-channel 路径识别和实现差异。",
  "evidence": [
    "commit:abc1234",
    "doc:plans/xtensa-debug-plan.md"
  ],
  "tags": ["debug", "tflite", "xtensa"],
  "outcome": "完成问题收敛和下一步排查方向定义。",
  "next_actions": [
    "确认运行时是否进入 pointwise conv 路径"
  ],
  "content": "Optional longer compressed source content",
  "metadata": {
    "repo": "wangyendt/week-reports",
    "days": 3
  }
}
```

## Storage Layout

Within the week directory:

```text
{year}/week{WW}/
├── materials/
│   └── {YYYYMMDD}-{guid}.jsonl
├── {YYYYMMDD}-{guid}.txt
└── report-{YYYYMMDD}-{HHmmss}.md
```

- `materials/*.jsonl`: source-of-truth material events
- `*.txt`: human-readable digest, useful for quick review and backward compatibility
- `report-*.md`: generated weekly reports
- The same session GUID can appear on different dates, but each calendar day gets its own file prefix

## Capture Rules

### Conversation

Capture:
- compressed user intent
- assistant outcome summary
- optional inferred project and tags

Do not capture:
- full code blocks
- long stack traces unless they are the main evidence

### Document

Capture:
- document type and topic
- project/workstream
- distilled summary
- concrete decisions, outcomes, next steps

Recommended evidence:
- `doc:path/to/file.md`
- `note:meeting-20260403`

### Repo Activity

Capture:
- repository name
- date range or commit range
- main workstreams
- concrete evidence such as commit SHAs or PR numbers

Recommended evidence:
- `commit:abc1234`
- `pr:123`
- `issue:456`

## Privacy Rules

Skip capture only when the content contains strong indicators such as:

- `password`
- `private key`
- `api key`
- `personal access token`
- `credential`
- `不要记录`
- `off record`

Do not skip merely because generic words like `token` or `private` appear in a normal engineering context.

## CLI Examples

### Ingest a conversation

```bash
python week-report-system/scripts/material_ingestor.py conversation \
  --project rayneo_hotword_tflm \
  --user-message "定位在线离线 TFLite 输出不一致" \
  --assistant-response "已确认问题收敛到 Xtensa FC per-channel 路径实现差异" \
  --tag debug \
  --tag tflite
```

### Ingest a document

```bash
python week-report-system/scripts/material_ingestor.py document \
  --project rayneo_hotword_tflm \
  --title "实验计划：Xtensa FC 对齐" \
  --summary "整理了 FC 对齐实验路径、验证点和后续步骤" \
  --evidence doc:plans/xtensa_fc_plan.md \
  --tag experiment \
  --tag plan
```

### Ingest repo activity

```bash
python week-report-system/scripts/material_ingestor.py repo-activity \
  --project rayneo_hotword_tflm \
  --title "最近 3 天提交总结" \
  --summary "提炼了模型对齐与 Xtensa 调试相关提交" \
  --evidence commit:abc1234 \
  --evidence commit:def5678 \
  --metadata repo=rayneo_hotword_tflm \
  --metadata days=3
```
