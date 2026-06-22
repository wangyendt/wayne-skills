# Awesome Docs Examples

Load this reference only when the main `SKILL.md` instructions are not enough and a concrete pattern would prevent ambiguity.

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
