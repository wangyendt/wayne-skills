---
name: awesome-docs
description: Use this skill whenever the user asks to record, save, organize, update, or maintain project documentation, including plan documents, experiment notes, know-how, roadmap items, decision records, summaries, or common command registries. Also use it when the user asks to save a generated shell command, append to 常用命令, or create a reusable AI/human project documentation interface. Defaults to <project-root>/docs unless the user specifies another documentation path.
---

# Awesome Docs

This skill treats project documentation as an interface between human understanding and automated AI execution. The goal is not to produce verbose reports; the goal is to preserve project state in a form that a human can read quickly and a future AI agent can act on without guessing.

## Core Contract

When the user asks to record project knowledge:

1. Resolve the documentation root.
2. Classify the content.
3. Create or update the right document.
4. Write in a concise, factual, readable style.
5. If the request is about reusable commands, update `常用命令.txt` with single-line commands.

## Documentation Root

Use the user-specified documentation path if provided.

Examples of explicit paths:

- `记录到 docs/xiaolei-xiaolei`
- `文档路径用 project_notes`
- `写到 /path/to/repo/docs_product`

If the user does not specify a documentation path, use:

```text
<project-root>/docs
```

Resolve `<project-root>` as the current repository root when possible. If no repository root is available, use the current working directory.

## Required Directory Layout

Ensure the documentation root contains at least these directories:

```text
docs/
├── plan/
├── experiment/
├── knowhow/
├── roadmap/
└── 常用命令.txt
```

Create missing directories or the command file when needed. Do not rename existing directories unless the user explicitly asks.

## Classification Rules

Classify before writing. If a note fits several categories, choose the category that best matches how the content will be reused.

### `plan/`

Use for future-oriented planning and execution design:

- implementation plans
- task breakdowns
- technical proposals
- migration plans
- risk analysis before execution
- design decisions that guide upcoming work

### `experiment/`

Use for evidence and results:

- experiment setup
- evaluation metrics
- benchmark results
- ablation comparisons
- regression records
- data tables
- conclusions tied to a specific run

### `knowhow/`

Use for reusable knowledge:

- debugging recipes
- pitfalls and root causes
- operational procedures
- environment conventions
- export/deploy lessons
- recurring decision heuristics

### `roadmap/`

Use for longer-horizon direction:

- product or project milestones
- phase plans
- long-term priorities
- version strategy
- open problems that should guide future planning

### `常用命令.txt`

Use when the user asks to save, generate, append, replace, or organize a command, such as:

- `存到常用命令`
- `把这条命令记录下来`
- `生成一个常用评测命令`
- `补充到命令列表`
- `整理常用命令`

Commands must be stored as single-line commands, no matter how long they are.

## File Naming

Markdown documents must use a date prefix:

```text
YYYYMMDD_简短标题.md
```

Use underscores to connect the date and title. Keep the title short and descriptive.

Examples:

```text
20260429_端侧内存优化方案.md
20260429_量化评测结果.md
20260429_导出链路踩坑记录.md
20260429_Q2功能路线图.md
```

Use the current date from the environment. If the user gives an explicit date, use that date.

## New Document vs Existing Document

Prefer a new dated document for new content.

Update an existing document only when:

- the user explicitly says to update a specific existing document
- the content is clearly a continuation of an existing living document
- the new content corrects or extends a previous record from the same topic and same date

When updating an old document, preserve its structure and add the minimum necessary changes. Do not rewrite the whole file unless the user asks for a cleanup.

## Writing Style

Remove AI flavor. Write like an engineer preserving project state for another engineer.

Prefer:

- direct titles
- short sections
- factual conclusions
- commands and file paths in code formatting
- tables for metrics and comparisons
- bullets for decisions and next steps

Avoid:

- filler openings like "本文旨在"
- inflated summaries like "综上所述"
- generic praise
- vague claims without data
- long paragraphs that mix setup, result, and conclusion

Good documentation answers:

- What happened?
- Why does it matter?
- What evidence supports it?
- What should be done next?
- Where are the commands, data, or files?

## Document Templates

Use templates flexibly. Keep only sections that add value.

### Plan Template

```markdown
# 标题

## 背景

## 目标

## 范围

## 方案

## 风险

## 下一步
```

### Experiment Template

```markdown
# 标题

## 问题

## 配置

## 命令

## 结果

| 项目 | 数值 | 说明 |
|---|---:|---|

## 结论

## 下一步
```

### Knowhow Template

```markdown
# 标题

## 问题

## 原因

## 方法

## 验证

## 适用条件
```

### Roadmap Template

```markdown
# 标题

## 当前状态

## 目标

## 里程碑

| 阶段 | 内容 | 判断标准 |
|---|---|---|

## 优先级

## 未决问题
```

## Common Command Registry

`常用命令.txt` is for copy-pasteable commands only.

Rules:

- Every command must be one physical line.
- Do not use shell line continuations with `\`.
- Do not wrap long commands across multiple lines.
- Group related commands under Chinese comment blocks.
- Add a short Chinese explanation before each group so humans can scan the file.
- Avoid duplicate commands unless the new command is a meaningful variant.
- If replacing an existing command, keep the group and update only the relevant line.

Recommended format:

```text
# ====================================================================
# 评测与分析
# 作用：按固定数据集和固定误唤醒预算生成可复现指标
# ====================================================================
python evaluate.py --config exp/demo/config.yaml --checkpoint exp/demo/avg_10.pt --test_data data/test.list --result_dir exp/demo/test_avg10
python analyze.py --exp-dir exp/demo --test-id test_avg10 --target-fa-per-hour 1.0
```

## Examples

### Example 1: Record An Experiment

User:

```text
把今天 full-int8 和 depthwise 的内存对比记录一下
```

Action:

- Classify as `experiment/`.
- Create `docs/experiment/YYYYMMDD_full-int8与depthwise内存对比.md`.
- Include model files, commands, memory table, accuracy table, conclusion, next step.

### Example 2: Record Reusable Know-how

User:

```text
这个坑记一下：onnx2tf 会把 groups=dim 的 conv 落成普通 CONV_2D
```

Action:

- Classify as `knowhow/`.
- Create `docs/knowhow/YYYYMMDD_onnx2tf_group_conv_lowering.md`.
- Explain symptom, cause, diagnosis command, fix, and reuse condition.

### Example 3: Save A Command

User:

```text
把这个评测命令存到常用命令
```

Action:

- Update `docs/常用命令.txt`.
- Find or create a relevant group such as `评测与分析`.
- Store the command as one single line.
- Add or preserve a Chinese comment explaining when to use the command.

### Example 4: Use A Custom Documentation Root

User:

```text
文档路径用 docs/xiaolei-xiaolei，记录一个 Q2 路线图
```

Action:

- Use `docs/xiaolei-xiaolei` as the root.
- Ensure `plan/ experiment/ knowhow/ roadmap/ 常用命令.txt` exist under it.
- Classify as `roadmap/`.
- Create `docs/xiaolei-xiaolei/roadmap/YYYYMMDD_Q2路线图.md`.

### Example 5: Update An Existing Document

User:

```text
更新 docs/experiment/20260401_端侧评测.md，加上今天的新结果
```

Action:

- Update the specified existing file.
- Add a dated subsection or extend the existing table.
- Preserve old conclusions unless the new result invalidates them; if so, write the replacement conclusion clearly.

## Final Response After Writing

After creating or updating documentation, report only the useful facts:

- created or updated files
- category chosen
- key command or result if relevant
- any skipped or unresolved item

Keep the final response brief. Do not paste the entire document unless the user asks.
