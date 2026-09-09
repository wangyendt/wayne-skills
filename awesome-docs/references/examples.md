# Awesome Docs Examples

Load this reference when a concrete request would clarify routing or scope. Execute the guide selected in `SKILL.md` before using the example; examples show the operations to perform, not facts or results to copy.

## Common Command Format

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
- Read the actual run logs/configuration; identify the memory metric (for example peak usage versus artifact size), units, baseline, and repeated-run rule. Mark unknown versions or unrun conditions.
- Extract comparable rows, check one value against its source, and reconcile sample counts. Add accuracy only if it was measured and relevant; do not create an empty result column to satisfy a template.
- Write setup and metrics before results, then the supported interpretation and limits; write the short opening answer last. Apply the Experiment workflow checks.

### Example 2: Record Reusable Know-how

User:

```text
这个坑记一下：onnx2tf 会把 groups=dim 的 conv 落成普通 CONV_2D
```

Action:

- Classify as `knowhow/`.
- Create `docs/knowhow/YYYYMMDD_onnx2tf_group_conv_lowering.md`.
- Preserve the user-reported observation with its known scope. Inspect conversion version, graph/operator evidence, and configuration if available before naming a root cause.
- Choose troubleshooting mode: compare expected versus actual operator, distinguish configuration from converter behavior, and give each check an observation and next branch. Do not invent a diagnostic CLI or a verified fix.
- Add a bounded remedy only when supported, then an independent check on the exported model; link any detailed experiment. Keep unverified explanations as hypotheses.

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
- Update the existing same-topic todo, or create `docs/todo/导出链路待办.md` if none exists. Preserve an existing dated filename rather than renaming it.
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
- Create only `roadmap/` and the requested document if missing; leave unrelated categories and `常用命令.txt` uncreated.
- Classify as `roadmap/`.
- Create or update `docs/xiaolei-xiaolei/roadmap/Q2路线图.md`; the period is explicit in the request, and revisions stay in the same file.
- Explain current state, target state, milestone logic, dependencies, priorities, testable completion criteria, risks, and unresolved questions. Link an existing execution plan rather than duplicating its task list.

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

### Example 7: Separate Architecture, Decisions, And Execution

User:

```text
把标定系统现在的模块边界、数据流和接口写成架构文档，另外记录为什么选离线求解，后面要迁移在线求解
```

Action:

- Read `references/architecture-writer.md`; locate entry points, actual module boundaries, interfaces, and state owners. Select L3 for internal component collaboration, with a brief parent context; if independent runtime units are the actual subject, start at L2 instead.
- Keep the living description in `docs/architecture/标定系统.md`. Build a responsibility table and one representative flow from inspected evidence. Stop at that selected level; link exact interface fields to reference rather than listing every helper function.
- Follow the repository's ADR convention for the decision record; otherwise use `docs/architecture/adr/YYYYMMDD_选择离线求解.md`. Retain sequence-based filenames only when that convention already exists. Record status, context, options, decision, consequences, and superseding links when applicable.
- Put the future migration sequence, risks, checkpoints, and acceptance criteria in `docs/plan/YYYYMMDD_在线求解迁移.md`.
- Cross-link these files. Distinguish current behavior from proposed architecture; architecture explains how the system fits together, an ADR explains why a decision was made, and a plan explains how to execute a change.

### Example 8: Build A Book With One Maintained Source

User:

```text
把散落的 IMU 标定推导整理成一本高中数学基础也能顺着读的书，放到 docs/books/imu-calibration
```

Action:

- Read `references/technical-book-writer.md`. Use `docs/books/imu-calibration/README.md` as the book's single navigation entry, with reader prerequisites, reading order, chapter links, and source links.
- Keep chapters in the same topic directory, for example `00_导读与符号.md`, `01_测量模型.md`, and `02_参数估计.md`; put figures in its `figures/` directory. Do not require a date prefix or create a new dated copy on each update.
- Inventory source conclusions and disagreements. Build chapter dependencies and a question/input/output contract for each chapter before writing prose.
- Make `00_导读与符号.md` the sole notation authority unless one already exists. Record symbols, units, dimensions, domains, frames, index meanings, abbreviation expansions, first definitions, and source aliases. Resolve conflicting symbols before combining notes.
- For each formula, look up the symbols, explain the starting relation and assumptions, show substitutions or algebra with the reason for each transition, and verify a hand-computable example. Use LaTeX with stable references; keep nearby explanations consistent with the global table.
- Introduce a required advanced operation through a small example before using the compact notation. Close a chapter with its concrete answer and the next unresolved question, then check that the next chapter starts from that output. Review numerical values, dimensions, boundary behavior, and affected figure labels.
- Preserve dated experiment notes as evidence and link original literature and existing topic material instead of maintaining duplicate copies. Extract a coherent chapter, not a chronological dump of source notes.
- Treat any generated combined Markdown/PDF as an output, not another editable book source. Use a temporary build location and verify its relative assets and export result.

### Example 9: Maintain A Protocol And CSV Reference

User:

```text
把采集协议和结果 CSV 的字段、单位、取值范围、兼容版本整理成以后查得到的规范
```

Action:

- Reuse existing canonical specifications, or create `docs/reference/protocols/采集协议.md` and `docs/reference/schemas/结果CSV.md` with stable paths rather than daily copies. Keep authoritative CSV definitions in their native format and link them; do not replace them with a manually maintained Markdown copy.
- Describe protocol framing, encoding, field types, byte order, units, allowed values, errors, and compatibility as applicable. For CSV, specify headers/order, delimiter/encoding, types, units, missing-value rules, valid ranges, and a minimal example.
- State the applicable protocol/schema/software versions, source of truth, and update date. Separate observed implementation behavior from required contract behavior; mark unknowns instead of guessing field definitions.
- Use versioned paths only when distinct supported contracts must coexist; provide a compatibility table and a clear current-version entry. Link the reference from related architecture, code, or book material instead of copying the specification into each document.

### Example 10: Promote A Todo Through Roadmap To Plan

User:

```text
待办里的在线标定已经确定要做：先做离线回放，再影子验证，最后在线启用；把路线和第一阶段实施方案补出来
```

Action:

- Update the existing `docs/todo/YYYYMMDD_在线标定待办.md`; preserve its original filename and source evidence. Mark the promoted item as `promoted` and link to its destination.
- Create or update `docs/roadmap/在线标定路线图.md` for target state, phase order and reasons, dependencies, priorities, stage acceptance evidence, and unresolved decisions.
- Put the first stage's concrete tasks, deliverables, risks, verification, and checkpoints in `docs/plan/YYYYMMDD_离线回放实施.md`.
- Link todo → roadmap → plan and back: use links such as `../roadmap/在线标定路线图.md` from the todo and `../todo/YYYYMMDD_在线标定待办.md` from the roadmap, resolving each from its containing file. In real files, substitute the actual filenames and dates, not the literal placeholders; keep the existing dated todo at its original path.
- Keep tactical follow-ups in the living todo; do not maintain three copies of one task list. Promotion can go directly to a plan when no roadmap is needed.

### Example 11: Move A Book And Repair Its Consumers

User:

```text
把 docs/books/imu/ 搬到 docs/books/imu-calibration/，阅读入口和导出也一起改好
```

Action:

- Inspect the book, incoming links, figure paths, navigation, and the scripts/configuration that build or export it before moving anything.
- Move the maintained source to the requested directory. Repair chapter/internal links, repository README/index backlinks, cross-document links, and image references relative to their new locations.
- Update build/export inputs, asset/search paths, and output destinations, including document-generating tools that might recreate the old directory. Keep old dated evidence at its original location unless its move was requested.
- Search for stale path references, check local links and assets, and run the relevant build/export verification when available. Report what was checked and any remaining dependency; historical mentions can remain when clearly labeled.
- Preserve one maintained book source, not two editable copies. Do not delete unrelated caches or outputs as part of link repair.

### Example 12: Keep A Small Documentation Task Small

User:

```text
只在现有待办加一条：下周核对 CSV 的单位
```

Action:

- Update the matching living todo with the source, concrete next step, and known context; re-read the whole document.
- Do not create empty category folders, a roadmap, or a full plan for this one item.
- Do not turn a documentation edit into a commit, push, release, deployment, cache cleanup, or unrelated repository reorganization without a separate request.
