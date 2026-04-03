# Week Report System User Guide

Week Report System is a Git-backed weekly reporting workflow built around structured work materials.

## What It Can Track

| Material type | Typical source | Recommended usage |
|---|---|---|
| `conversation` | daily AI work chats | best-effort auto capture plus explicit ingestion when needed |
| `document` | plan, experiment, review, meeting note | explicit ingestion |
| `repo_activity` | recent commits, PRs, issues | explicit ingestion |

## Source of Truth

- `materials/*.jsonl` is the canonical weekly-report data
- `*.txt` is only a readable digest for compatibility and debugging
- If both exist, weekly report generation should rely on `materials/*.jsonl` first

## What It Does Not Guarantee

- It does not guarantee that every work conversation is captured automatically
- A skill description is not the same as a host-level post-turn hook
- For important work items, explicitly say "纳入周报素材"

## Typical Commands

### Generate a report

```text
写周报
本周工作总结
总结2026年第14周
上周周报
```

### Capture a document as material

```text
把这个 plan 纳入本周周报素材
把这个 experiment 总结成周报素材
```

### Capture recent repo activity

```text
看这个 repo 最近 3 天提交，纳入本周周报
总结这个仓库最近一周提交，作为周报素材
```

### Force a conversation to be captured

```text
把这次讨论记入周报素材
记录这次工作讨论
```

## Storage Layout

```text
week-reports/
└── 2026/
    └── week14/
        ├── materials/
        │   └── 20260403-02a24577.jsonl
        ├── 20260403-02a24577.txt
        └── report-20260403-143500.md
```

## Privacy Rules

The system skips capture only for strongly sensitive content, such as:

- passwords
- private keys
- API keys / PATs
- explicit "不要记录" / "off record"

## Troubleshooting

If you suspect capture did not happen, inspect local status files under `~/.week-report-repo/`:

- `last_sync_status.json`
- `local_queue.jsonl`

These help distinguish:

- skill not triggered
- capture attempted but sync failed
- last sync succeeded
