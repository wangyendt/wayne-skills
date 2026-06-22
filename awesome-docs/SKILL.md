---
name: awesome-docs
description: Use this skill whenever the user asks to record, save, organize, update, or maintain project documentation, including plan documents, todo documents, temporary ideas, project risks, next actions, experiment notes, know-how, roadmap items, decision records, summaries, story-telling documentation polish, technical book chapters, thesis-style derivations, or common command registries. Also use it when the user asks to save a generated shell command, append to 常用命令, or create a reusable AI/human project documentation interface. Defaults to <project-root>/docs unless the user specifies another documentation path.
---

# Awesome Docs

This skill treats project documentation as an interface between human understanding and automated AI execution. The goal is not to produce verbose reports; the goal is to preserve project state in a form that a human can read quickly and a future AI agent can act on without guessing.

## Core Contract

When the user asks to record project knowledge:

1. Resolve the documentation root.
2. Classify the content.
3. Create or update the right document.
4. Write in a concise, factual, readable style with a clear story line.
5. Re-read the full document after writing and run the post-write checklist for readability, consistent structure, complete required modules, evidence, conclusions, and next steps.
6. If the request is about reusable commands, update `常用命令.txt` with single-line commands.

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
├── todo/
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

### `todo/`

Use for lightweight, living work queues and unresolved project state:

- temporary ideas that are not ready for a full plan
- project risks that need follow-up, monitoring, or mitigation
- next actions discovered during implementation, review, or debugging
- open questions, blockers, and assumptions to revisit
- small task lists that are too tactical for `roadmap/`

Choose `todo/` instead of `plan/` when the content is a loose backlog, risk watchlist, or next-action list rather than an execution design. Promote a todo item into `plan/`, `roadmap/`, `experiment/`, or `knowhow/` only after it becomes substantial enough to deserve its own document.

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
20260429_模型导出待办.md
```

Use the current date from the environment. If the user gives an explicit date, use that date.

## New Document vs Existing Document

Prefer a new dated document for new content.

Update an existing document only when:

- the user explicitly says to update a specific existing document
- the content is clearly a continuation of an existing living document
- the new content corrects or extends a previous record from the same topic and same date

When updating an old document, preserve its structure and add the minimum necessary changes. Do not rewrite the whole file unless the user asks for a cleanup.

## Todo Documents

Todo documents are living documents. Prefer updating an existing same-topic todo document instead of creating a new dated file for every small item.

Create a new `todo/` document when:

- the user asks to record loose future work, a temporary idea, or a next-action list
- a project has several risks or unresolved questions that need tracking
- the content is actionable but not mature enough for a plan or roadmap
- no existing same-topic todo document exists

Update an existing `todo/` document when:

- a new idea, risk, blocker, or next action belongs to the same topic
- an item is completed, invalidated, deferred, or promoted into another document
- new evidence changes the priority, risk level, owner, trigger, mitigation, or next step
- a plan, experiment, or review creates follow-up work that should not be lost

Recommended item fields:

- `状态`: `open`, `doing`, `blocked`, `done`, `dropped`, or `promoted`
- `来源`: date, conversation, command, file, PR, issue, experiment, or decision that created the item
- `内容`: one concrete idea, risk, question, or action
- `下一步`: the smallest useful action that moves the item forward
- `风险处理`: for risks, include impact, trigger, and mitigation when known

Keep open items near the top. Do not delete completed items unless the user asks for cleanup; move them to a short `已处理` section with the completion date. If an item is promoted into another document, mark it as `promoted` and link or name the destination document.

## Writing Style

Remove AI flavor. Write like an engineer preserving project state for another engineer.

Use story-telling as the organizing principle: context -> tension or question -> action -> evidence -> conclusion -> next move. The document should feel like a clear engineering narrative, not a pile of notes.

Prefer:

- direct titles
- short sections
- factual conclusions
- commands and file paths in code formatting
- tables for metrics and comparisons
- bullets for decisions and next steps
- one idea per paragraph
- explicit transitions between background, evidence, and conclusion

Avoid:

- filler openings like "本文旨在"
- inflated summaries like "综上所述"
- generic praise
- vague claims without data
- long paragraphs that mix setup, result, and conclusion
- orphaned details that are not tied back to the main question
- dumping raw logs without explaining what they prove

Good documentation answers:

- What happened?
- Why does it matter?
- What evidence supports it?
- What should be done next?
- Where are the commands, data, or files?

## Quality Bar By Document Type

### Experiments

Experiment documents must be organized, self-contained, and comparable. A future reader should understand the question before the numbers and should be able to compare scenarios without decoding different table shapes.

Always make clear:

- the project context, regression, or decision that triggered the experiment
- the experiment question, hypothesis, and compared systems or configurations
- the dataset, generated data, model, environment, commands, commit, and key parameters
- what changed and what stayed fixed
- metric definitions, units, which direction is better, and known metric limitations
- result tables with consistent columns, scenario order, and units across comparable runs
- a short reading conclusion after each table or scenario explaining what the numbers mean
- what the results prove, what they do not prove, and the next experiment if any

For Ceres/Kalibr-style calibration comparisons or any multi-scenario benchmark, prefer this shape:

1. Background and comparison intent.
2. Comparison scope: tools, datasets, sensor setup, parameters, and outputs being compared.
3. Metric glossary: time, extrinsic error, rotation error, translation error, timeshift error, residuals, success/failure conditions.
4. Result overview table with the same columns for every scenario.
5. Per-scenario sections with the same structure: scenario meaning -> configuration -> result table -> interpretation.
6. Cross-scenario analysis explaining trends, failure modes, and when a number is not directly comparable.
7. Limitations, reproducibility notes, and concrete next actions.

If a document contains historical diagnostic records, add a reading map near the top. Preserve the evidence, but label stale or superseded conclusions so they cannot be mistaken for the current conclusion.

### Know-how

Know-how documents should be easy to reuse under pressure. Start with the practical situation, then explain the symptom, root cause, procedure, verification method, and boundary conditions.

The reader should leave knowing when to apply the recipe, when not to apply it, and which command or file confirms the fix.

Use this structure unless a shorter one is clearly enough:

- scenario and trigger
- symptom or failure signal
- root cause or current best explanation
- procedure or decision rule
- verification command, expected output, or file to inspect
- boundary conditions, traps, and rollback or alternative path

### Plans

Plan documents should turn ambiguity into an executable path. Start from the background and constraint story, then explain the goal, scope, proposed approach, sequence of work, risks, decision points, and checkpoints.

Prefer readable section flow over exhaustive task dumps. If the plan contains many tasks, group them by phase and explain the reason for each phase.

### Roadmaps

Roadmap documents should explain direction, not just list milestones. Start with the current state and why the direction matters, then describe the target state, sequencing logic, milestones, priorities, dependencies, risks, and unresolved questions.

Make each milestone testable: a future reader should know what evidence proves the milestone is done.

### Todos

Todo documents should be fast to update and easy to triage. They must preserve loose ideas without pretending they are plans.

Each open item should make clear:

- what the idea, risk, question, or next action is
- why it matters now
- what evidence or trigger created it
- what the smallest useful next step is
- whether it should stay in todo, be dropped, or be promoted into another document type

Risk items must include at least a concrete impact and the next mitigation or observation step when that information is available.

## Technical Book Mode

For book-like technical writing, keep `SKILL.md` lightweight and load the reference only when needed.

Read `references/technical-book-writer.md` before writing or rewriting:

- thesis-style chapters, textbook sections, or long-form technical explanations
- derivation-heavy calibration, robotics, state-estimation, optimization, or code-derived math
- formula, Jacobian, residual, coordinate-frame, or implementation-theory bridge explanations
- requests to turn scattered notes into a coherent chapter rather than an experiment record

Do not load that reference for ordinary plan, todo, experiment, roadmap, command, or short know-how updates.

## Post-write Review

After creating or updating any Markdown document, re-read the whole file once as an editor. This is required for all document types, including small updates to an existing file.

Check:

- readability: the opening explains why the document exists, the conclusion answers the opening question, and no paragraph is an orphaned note
- structural consistency: repeated result blocks, scenarios, tools, or datasets use the same headings, table columns, units, and order
- module completeness: the document contains the required background, scope, evidence, interpretation, limitations, and next action for its type
- evidence: claims have data, commands, file paths, logs, references, or explicit assumptions
- metric clarity: tables define units, comparison baseline, success direction, and conditions where values are not comparable
- currentness: stale, superseded, or historical conclusions are marked instead of silently conflicting with the current conclusion
- scanability: long documents have a reading map, result overview, or table of key findings near the top
- actionability: the final section gives a concrete next step, decision, or remaining question

If any checklist item fails, edit the document again and re-read the affected section in context. If the document feels like disconnected notes, reorganize it before finishing. Keep the final document polished enough that another engineer or AI agent can continue from it without asking what the story was.

## Document Templates

Use templates flexibly. Keep only sections that add value.

### Plan Template

```markdown
# 标题

## 背景

## 核心问题

## 目标

## 范围

## 方案

## 执行路径

| 阶段 | 目标 | 产出 | 判断标准 |
|---|---|---|---|

## 风险

## 检查点

## 下一步
```

### Todo Template

```markdown
# 标题

## 背景

## 当前待办

| 状态 | 类型 | 优先级 | 内容 | 来源 | 下一步 |
|---|---|---|---|---|---|
| open | action | P1 |  |  |  |

## 风险与观察点

| 状态 | 风险 | 影响 | 触发条件 | 缓解措施 | 下一步 |
|---|---|---|---|---|---|
| open |  |  |  |  |  |

## 已处理

| 日期 | 原事项 | 结果 | 去向 |
|---|---|---|---|
```

### Experiment Template

```markdown
# 标题

## 结论先行

## 背景

## 对比目标 / 实验问题

## 范围与配置

| 项目 | 内容 | 说明 |
|---|---|---|

## 指标口径

| 指标 | 单位 | 越大/越小越好 | 含义 | 注意事项 |
|---|---|---|---|---|

## 结果总览

| 场景 | 配置 | 关键指标 | 结论 |
|---|---|---|---|

## 分场景结果

### 场景 A

#### 场景含义

#### 结果

| 指标 | 数值 | 对比基线 | 说明 |
|---|---:|---:|---|

#### 读数结论

## 跨场景分析

## 结论

## 边界与未覆盖问题

## 复现入口

## 下一步
```

### Knowhow Template

```markdown
# 标题

## 触发场景

## 现象 / 信号

## 原因 / 判断

## 处理方法

## 验证

## 适用条件

## 陷阱与边界

## 相关命令 / 文件
```

### Roadmap Template

```markdown
# 标题

## 当前状态

## 背景与方向

## 目标状态

## 里程碑

| 阶段 | 目标 | 关键工作 | 判断标准 |
|---|---|---|---|

## 优先级

## 依赖与风险

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

If a concrete command group or document-update pattern is needed, read `references/examples.md`. Do not load that reference for routine updates.

## Final Response After Writing

After creating or updating documentation, report only the useful facts:

- created or updated files
- category chosen
- key command or result if relevant
- any skipped or unresolved item

Keep the final response brief. Do not paste the entire document unless the user asks.
