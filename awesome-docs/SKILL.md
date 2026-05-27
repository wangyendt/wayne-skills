---
name: awesome-docs
description: Use this skill whenever the user asks to record, save, organize, update, or maintain project documentation, including plan documents, todo documents, temporary ideas, project risks, next actions, experiment notes, know-how, roadmap items, decision records, summaries, story-telling documentation polish, or common command registries. Also use it when the user asks to save a generated shell command, append to 常用命令, or create a reusable AI/human project documentation interface. Defaults to <project-root>/docs unless the user specifies another documentation path.
---

# Awesome Docs

This skill treats project documentation as an interface between human understanding and automated AI execution. The goal is not to produce verbose reports; the goal is to preserve project state in a form that a human can read quickly and a future AI agent can act on without guessing.

## Core Contract

When the user asks to record project knowledge:

1. Resolve the documentation root.
2. Classify the content.
3. Create or update the right document.
4. Write in a concise, factual, readable style with a clear story line.
5. Re-read the full document after writing and tighten the logic, headings, transitions, and conclusions.
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

Experiment documents must be organized and self-contained. Every experiment needs enough background for a future reader to understand why the run existed before reading the numbers.

Always make clear:

- the project context or regression that triggered the experiment
- the question or hypothesis being tested
- what changed and what stayed fixed
- the dataset, model, environment, commands, and key parameters
- which metrics decide success or failure
- what the results prove, what they do not prove, and the next experiment if any

### Know-how

Know-how documents should be easy to reuse under pressure. Start with the practical situation, then explain the symptom, root cause, procedure, verification method, and boundary conditions.

The reader should leave knowing when to apply the recipe, when not to apply it, and which command or file confirms the fix.

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

## Post-write Review

After creating or updating any Markdown document, re-read the whole file once as an editor.

Check:

- the opening explains why the document exists
- each section follows logically from the previous section
- claims have evidence, commands, files, or explicit assumptions
- experiment conclusions are tied to the stated question
- know-how, plan, todo, and roadmap documents are easy to scan
- duplicated or stale statements were removed or reconciled
- the final section gives a concrete next step, decision, or remaining question

If the document feels like disconnected notes, reorganize it before finishing. Keep the final document polished enough that another engineer or AI agent can continue from it without asking what the story was.

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

## 背景

## 实验问题

## 假设

## 配置

| 项目 | 内容 | 说明 |
|---|---|---|

## 命令

## 结果

| 指标 | 数值 | 对比基线 | 说明 |
|---|---:|---:|---|

## 分析

## 结论

## 未覆盖问题

## 下一步
```

### Knowhow Template

```markdown
# 标题

## 场景

## 现象

## 原因

## 方法

## 验证

## 适用条件

## 注意事项
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
- Explain the experiment background, question, fixed variables, model files, commands, memory table, accuracy table, analysis, conclusion, and next step.
- Re-read the document and make sure the conclusion answers the experiment question.

### Example 2: Record Reusable Know-how

User:

```text
这个坑记一下：onnx2tf 会把 groups=dim 的 conv 落成普通 CONV_2D
```

Action:

- Classify as `knowhow/`.
- Create `docs/knowhow/YYYYMMDD_onnx2tf_group_conv_lowering.md`.
- Explain the scenario, symptom, cause, diagnosis command, fix, verification, reuse condition, and caveats.

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

### Example 4: Record A Todo List

User:

```text
这个先记一下：导出链路后面要检查量化日志，另外 TFLite 体积可能有风险
```

Action:

- Classify as `todo/`.
- Create or update `docs/todo/YYYYMMDD_导出链路待办.md`.
- Add the log check as an `action` item with a concrete next step.
- Add the TFLite size concern as a `risk` item with impact, trigger, mitigation, and next observation step when known.
- Keep unresolved items near the top and preserve completed items in `已处理`.

### Example 5: Use A Custom Documentation Root

User:

```text
文档路径用 docs/xiaolei-xiaolei，记录一个 Q2 路线图
```

Action:

- Use `docs/xiaolei-xiaolei` as the root.
- Ensure `plan/ todo/ experiment/ knowhow/ roadmap/ 常用命令.txt` exist under it.
- Classify as `roadmap/`.
- Create `docs/xiaolei-xiaolei/roadmap/YYYYMMDD_Q2路线图.md`.
- Explain current state, target state, milestone logic, testable completion criteria, risks, and unresolved questions.

### Example 6: Update An Existing Document

User:

```text
更新 docs/experiment/20260401_端侧评测.md，加上今天的新结果
```

Action:

- Update the specified existing file.
- Add a dated subsection or extend the existing table.
- Preserve old conclusions unless the new result invalidates them; if so, write the replacement conclusion clearly.
- Re-read the full document after the update so the new result fits the existing narrative.

## Final Response After Writing

After creating or updating documentation, report only the useful facts:

- created or updated files
- category chosen
- key command or result if relevant
- any skipped or unresolved item

Keep the final response brief. Do not paste the entire document unless the user asks.
