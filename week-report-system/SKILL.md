---
name: week-report-system
description: 'Material-based AI weekly report system. Use when the user mentions 周报, week report, weekly report, 本周总结, 工作总结, 写周报, 生成周报, 帮我写周报, 本周工作, 上周周报, 查看周报, 周报系统, 记录工作, 纳入周报素材, 周报素材, plan, experiment, 方案文档, 复盘文档, or asks to summarize recent repo activity into weekly report materials. This skill captures work materials, syncs them to Git, and generates weekly reports from structured materials.'
---

# Week Report System

Material-first weekly report workflow for work conversations, documents, and recent repository activity.

## What This Skill Does

- Capture work materials into a Git-backed weekly knowledge base
- Support three material types: `conversation`, `document`, `repo_activity`
- Generate weekly reports from structured materials, with legacy conversation logs as fallback

## Hard Rules

1. If the user explicitly says `纳入周报素材`, `记入周报`, `作为周报素材`, or equivalent, you **must** execute material capture.
2. When generating a weekly report, you **must** check `{year}/week{WW}/materials/` first.
3. If any readable `materials/*.jsonl` files exist, the main report analysis **must** be based on them.
4. You **must not** generate a report only from `*.txt` when structured materials are present.
5. `*.txt` digests are a compatibility/debug artifact, not the source of truth.
6. If Git sync fails after a capture attempt, you **must** preserve local status evidence.
7. If one session crosses midnight, captured materials **must** be split by calendar date in file naming.

## Important Boundary

This skill can do **best-effort automatic capture only when the host agent actually invokes it**.

- A skill description is **not** a system-level post-turn hook
- Do **not** claim guaranteed logging for every conversation
- When the user cares about completeness, explicitly ingest materials via `scripts/material_ingestor.py`

## Step 0: First Time — Check Environment

Always run this check first:

```bash
echo "USERNAME: ${WEEK_REPORT_GIT_USERNAME:-MISSING}"
echo "TOKEN: $([ -n \"$WEEK_REPORT_GIT_PERSONAL_TOKEN\" ] && echo 'SET' || echo 'MISSING')"
echo "REPO: ${WEEK_REPORT_GIT_REPO:-MISSING}"
```

- If all three are set, continue with the request
- If any is missing, read `references/setup_guide.md` and guide the user through setup

## Determine User Intent

| User intent | Action |
|---|---|
| "写周报" / "生成周报" / "本周总结" / "上周周报" | Generate report → `references/report_generation.md` |
| "把这个纳入周报素材" / "记录这次讨论" | Must capture as material → `references/material_ingestion.md` |
| "总结这个 plan/experiment 文档并纳入周报" | Ingest as `document` material |
| "看某个 repo 最近几天提交并纳入周报" | Ingest as `repo_activity` material |
| "周报系统怎么用" / "怎么设置" / "skill介绍" | Show guide → `references/user_guide.md` |
| Any other work-related message | Answer normally, then best-effort capture a `conversation` material |

## Material Capture Workflow

Full instructions: `references/material_ingestion.md`

Quick summary:
1. Build a structured material event with `source_type`, `project`, `title`, `summary`, `evidence`, `tags`, `outcome`, `next_actions`
2. Use `scripts/material_ingestor.py` or `scripts/conversation_logger.py` to persist the event
3. Treat `materials/*.jsonl` as the source of truth
4. Write `*.txt` digest only as a compatibility/debug view
5. Update local sync status files for observability
6. Fail silently for the user, but leave local status/queue evidence for debugging

## Weekly Report Generation

Read `references/report_generation.md` for the full process.

Quick summary:
1. Pull latest data from Git
2. Check `materials/*.jsonl` under `{year}/week{WW}/` first
3. If any structured materials exist, base the report on them
4. Fall back to legacy `.txt` logs only if structured materials are missing or unreadable
5. Group by project / workstream, extract evidence and outcomes, then render the report
6. Optionally save the report to `{year}/week{WW}/report-{YYYYMMDD}-{HHmmss}.md`

## Reference Files

| File | When to read |
|---|---|
| `references/setup_guide.md` | Missing env vars |
| `references/material_ingestion.md` | Capturing conversation, document, or repo materials |
| `references/conversation_tracking.md` | Best-effort conversation capture and local observability |
| `references/report_generation.md` | Generating reports |
| `references/user_guide.md` | User asks how to use the system |

## Scripts

| Script | Purpose |
|---|---|
| `scripts/git_operations.py` | Clone / pull / push the report repo |
| `scripts/conversation_logger.py` | Capture conversation materials and maintain digest files |
| `scripts/material_ingestor.py` | Explicitly ingest `conversation`, `document`, or `repo_activity` materials |

## Important Notes

- Best-effort auto capture is useful, but not a guarantee of complete logging
- Prefer explicit material ingestion for important plans, experiments, or repo analysis
- Skip recording only for high-confidence sensitive content such as passwords, private keys, PATs, or explicit "不要记录"
- Recording failures must not interrupt the user response, but they should leave status clues locally
- Structured material events live in `materials/*.jsonl` and are the primary source for report generation
- One session can append to one digest file per calendar date for compatibility/debugging
