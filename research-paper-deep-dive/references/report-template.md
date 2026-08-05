# Full Deep-Dive Report Template

Use this template for `full` mode. The goal is not to fill every heading. Keep the teaching path short, and move verification detail to the optional appendix.

## Core rule

Write in three reader layers:

1. **30 seconds:** problem, key move, consequence.
2. **Five minutes:** one plain-language story that installs the mental model.
3. **Optional appendix:** exact details for readers who want to verify, implement, or continue researching.

Do the claim audit before writing, but do not expose claim IDs or evidence labels in Layers 1–2. Avoid theatrical headings and reviewer language in the teaching path.

---

# [Paper title]: [a literal question or useful interpretation]

## 30 秒理解

- **难点：** [What was hard, in everyday language?]
- **办法：** [What did the paper change?]
- **意义：** [What became possible, with one boundary if essential?]

## 用五分钟把它讲明白

### 1. 先看一个具体问题

[Start with one concrete input or situation. Explain the desired output and why the input does not contain enough information. Define at most one essential term.]

### 2. 以前的办法为什么不够

[Explain one or two obvious approaches and the exact bottleneck. Do not begin with a long historical timeline.]

### 3. 作者换了一个什么思路

[State the conceptual move before the component names. Use one restrained analogy only when it shortens the explanation.]

### 4. 跟着一个样本走一遍

[Carry the same image/patient/trace/example through acquisition, preparation, training, and use. Make train-time versus deployment-time information explicit.]

```text
[small information-flow diagram when helpful]
```

[Embed one or two inspected paper figures here only if they materially reduce explanation. Preserve identifiers and pages.]

[Optionally embed one generated conceptual image when the paper lacks a clear visual for the core mental model. Caption it: “AI 生成的教学示意图，不是论文原图，也不表示额外实验结果。” Never generate benchmark results, exact undocumented architecture, hardware, or author portraits.]

### 5. 为什么相信它有用

[Ask 1–3 concrete questions and answer each with the most relevant experiment. Explain the metric before the number. State one protocol exception in ordinary language if it changes interpretation.]

### 6. 哪些地方还不能确定

[Use no more than 3–5 concise points. Gather the important boundaries here instead of scattering caveats through the story.]

### 7. 真正值得带走的三个想法

1. **[Principle]:** [Mechanism and transfer value in plain language.]
2. **[Principle]:** [Mechanism and transfer value in plain language.]
3. **[Principle]:** [Mechanism and transfer value in plain language.]

### 你可以这样复述这篇论文

> [Two natural sentences that cover the problem, key move, evidence, and main boundary.]

## 这项工作为什么会从这个团队里出现

[Use 2–4 short paragraphs or a small capability map. Connect publication-time institutions, the first author/senior author, and only the other authors whose verified work explains an essential capability. Place this after the method is understood.]

```text
[lab/author capability] --provides--> [focal paper need]
```

### 最相关的工作与代码

| 工作 / GitHub | 与本文的关系 | 实际包含什么 | 不要误解为 |
| --- | --- | --- | --- |
| | predecessor / focal / follow-up / adjacent tool | | |

Prefer official paper/project repositories and lab organizations. Verify author accounts through first-party profiles. Label third-party repositories and unreleased components explicitly.

---

# 技术附录（需要时再看）

Include only subsections that answer a likely next question. The main story above must remain understandable without them.

## A. 论文与来源

| 字段 | 内容 |
| --- | --- |
| 论文、作者、会议、年份 | |
| 分析版本 | |
| 分析日期 | |
| 论文 / supplement / official artifact | |
| 未获得的材料 | |

State meaningful version differences once.

## B. 必要术语与指标

Use a short glossary. Explain the concept first, then give the canonical term.

For each decisive metric, record:

- direction and unit/range;
- alignment/normalization;
- evaluated subset and aggregation;
- threshold interval when applicable;
- split and any exception;
- what remains unknown.

## C. 方法细节

### 阶段边界

| 阶段 | 输入 | 额外信息 | 操作 | 输出 | 部署时运行？ |
| --- | --- | --- | --- | --- | --- |
| 采集 | | | | | |
| 标注/准备 | | | | | |
| 训练/优化 | | | | | |
| 推理/部署 | | | | | |
| 评测 | | | | | |

### 核心公式

For every included equation:

1. define symbols and units;
2. translate it into one ordinary sentence;
3. explain its pipeline role;
4. name a failure condition.

Do not include equations that do not improve the reader's model.

## D. 关键实验与图表

Use plain claims rather than IDs in default full mode.

| 想回答的问题 | 证据与位置 | 结果 | 可以说明 | 不能说明 |
| --- | --- | --- | --- | --- |
| | | | | |

For selected visuals, record exact PDF/printed page, caption exceptions, missing cells, split substitutions, and unequal sample counts. Do not re-explain a visual already handled in the main story.

## E. 实现或复现

| 主题 | 论文写明 | 官方发布物 | 仍然缺失 | 建议检查 |
| --- | --- | --- | --- | --- |
| | | | | |

For dataset papers, separate:

1. using the released dataset and evaluator;
2. rebuilding the acquisition and label-production pipeline.

Give staged milestones with a deliverable, sanity check, and failure signal. Mark derived compute or memory values as estimates. Do not invent total cost.

## F. 作者、实验室、代码与技术路线

Include this only when it helps explain why the work emerged or where to go next.

- Start with the two or three capability lines that converged in the paper; avoid six independent biographies.
- Verify publication-time role separately from current position.
- Profile the first author, senior/corresponding author, and only other directly relevant contributors.
- Do not infer individual contributions from author order.
- Link the lab GitHub organization, focal repository, direct predecessor/follow-up repositories, and relevant verified author accounts.
- For each repository, state its scope, age/dependencies when relevant, and which paper components remain unreleased.
- Use a branching tree whose edges state inherited capability or unresolved gap.
- State the literature-search cutoff.
- For every recommended paper, explain what question it answers next.

## G. 想继续研究时

For 1–3 opportunities:

```text
缺口：
假设：
第一个能区分真假的实验：
成功信号：
失败信号：
风险：
```

## H. 来源说明

Provide a compact source list or note table. Include exact page/figure/table locations for important numeric claims and first-party links for current facts. Do not publish a claim-ID ledger unless the user requested reviewer/audit mode.

---

## Final editing test

Finish and verify the evidence draft first. Then run the separate `shuorenhua` polish defined in `SKILL.md`; do not mix style rewriting into claim construction.

Delete or rewrite any sentence that fails one of these tests:

- Would an intelligent newcomer understand it on first reading?
- Does the sentence explain a mechanism rather than display vocabulary?
- Is the English term necessary?
- Does the number answer a question the reader already understands?
- Is this detail better placed in the appendix?
- Is the tone calm and literal?
- Can the reader retell the paper after the teaching layer?
- Does each author/repository detail explain the focal paper or a concrete next step?
- Are source figures and AI-generated teaching illustrations unmistakably labeled?
