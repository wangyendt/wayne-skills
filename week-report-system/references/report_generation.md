# Weekly Report Generation

This document describes how to generate weekly reports from structured materials.

## Source Priority

When generating a report for `{year}/week{WW}`, use sources in this order:

1. `materials/*.jsonl`
2. legacy `*.txt` conversation digests
3. ad-hoc evidence the user asks to include during the current request

The structured materials are the source of truth whenever they exist.

## Hard Rules

1. You must inspect `materials/*.jsonl` before reading legacy `*.txt`.
2. If any readable structured materials exist, they must drive the main analysis.
3. Legacy `*.txt` is fallback-only and must not be the sole basis of the report when materials are present.
4. If both sources exist and disagree, prefer the structured material and use `*.txt` only as supporting context.

## Report Structure

Keep the report concise, work-focused, and evidence-backed.

```markdown
# 周工作汇报 - {YYYY}年第{WW}周
> 报告周期: {start_date} 至 {end_date}
> 生成时间: {generation_time}

## 📋 本周工作概览

[2-3 sentences: main projects, outcomes, overall status]

---

## 📊 分项目工作详情

### {Project Name}

- [Concrete progress]
- [Outcome or decision]
- [Evidence-backed result]

---

## 🎯 本周亮点

1. **[Achievement]**: [Impact]
2. **[Achievement]**: [Impact]
3. **[Achievement]**: [Impact]

---

## 📝 总结与下周计划

**总结:** [1-2 sentences]

**下周计划:**
- [ ] [Plan 1]
- [ ] [Plan 2]
- [ ] [Plan 3]
```

## Writing Rules

- Prefer project outcomes over raw chat history
- Use evidence when available: commits, PRs, docs, experiments, milestones
- Do not include code-line statistics
- Keep project sections factual and short
- Deduplicate repeated conversations that refer to the same outcome

## Generation Process

### Step 1: Parse the target week

Support:

- "总结2026年第14周"
- "本周工作总结"
- "上周周报"

### Step 2: Pull latest data

Use `scripts/git_operations.py` to update the local report repository.

### Step 3: Read structured materials

Read all JSON lines from:

```text
{year}/week{WW}/materials/*.jsonl
```

Normalize fields:

- `project`
- `source_type`
- `title`
- `summary`
- `evidence`
- `tags`
- `outcome`
- `next_actions`

### Step 4: Fallback to legacy digest files

Only if materials are missing or unreadable, read:

```text
{year}/week{WW}/*.txt
```

Use them as supporting context, not the primary source.

### Step 5: Group and deduplicate

Group items by:

- `project`
- workstream or topic
- time window

Merge duplicates when multiple entries describe the same work item with incremental updates.

### Step 6: Generate the report

For each project, answer:

- What changed this week?
- What concrete outcome was achieved?
- What evidence supports that claim?
- What is the next step?

## Suggested Project Analysis Prompt

```text
Read the weekly materials and produce a concise work report.

Requirements:
- Group by project/workstream
- Prefer concrete outcomes and decisions
- Mention evidence when available
- Keep each project section within 3-6 bullets
- Avoid code metrics such as lines changed
```

## Saving Reports

Save generated reports as:

```text
{year}/week{WW}/report-{YYYYMMDD}-{HHmmss}.md
```

Use a timestamped filename to avoid collisions between agents or devices.
