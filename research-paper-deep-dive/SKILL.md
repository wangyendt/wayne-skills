---
name: research-paper-deep-dive
description: 'Deeply explain, critique, reproduce, or situate an academic paper for a reader entering an unfamiliar field. Use for 读论文, 论文精读, 帮我吃透这篇论文, paper deep dive, method/figure/experiment analysis, author or lab context, related work and GitHub discovery, technical history, reviewer mode, implementation mode, and research opportunities. Turn the paper into a compact, plain-language mental model first; use inspected paper figures and selective generated teaching visuals when they improve understanding; then place exact evidence and technical detail in an optional appendix. Distinguish fact from inference internally and never let audit machinery overwhelm the teaching story.'
---

# Research Paper Deep Dive

Treat the paper as knowledge to install in the reader's mind, not a document to summarize.

The default result must let an unfamiliar reader answer four questions without reopening the paper:

1. What problem made this work necessary?
2. What did the authors do differently?
3. Why should I believe it helped?
4. What idea can I reuse elsewhere?

Accuracy is a backstage constraint. The main explanation must feel like a good advisor at a whiteboard: calm, concrete, and easy to retell.

For a full report, read [references/report-template.md](references/report-template.md) before drafting.

## Optimize for cognitive compression

Use three reader layers. Do not merge them.

### Layer 1 — 30-second understanding

Give three short points:

- **The difficulty:** the real bottleneck in ordinary language;
- **The move:** the paper's key idea, without implementation detail;
- **The consequence:** what became possible, with one important boundary if needed.

This is not an abstract. It is the answer the reader should be able to repeat tomorrow.

### Layer 2 — Five-minute walkthrough

Tell one connected story:

```text
concrete problem -> why obvious approaches fail -> key idea
-> one sample moving through the system -> decisive evidence
-> what to retain and where confidence stops
```

This is the primary deliverable. It should normally use 2,000–3,500 Chinese characters or 900–1,500 English words. Use one running example and, when helpful, one restrained analogy. Prefer causal explanation over lists.

### Layer 3 — Optional technical appendix

Put exact notation, metric protocols, tables, figure locations, implementation parameters, evidence boundaries, history, authors, and reading links here. A reader who stops before this layer must still understand the paper.

When the research lineage materially explains the paper, add a short bridge between Layers 2 and 3: **“这项工作为什么会从这个团队里出现”**. Connect verified author/lab capabilities to the focal work and point to the most relevant papers and official repositories. Keep this bridge readable; do not turn it into six disconnected biographies.

The full document should normally stay around 7,000–11,000 Chinese characters or 2,500–4,000 English words, excluding references. Go longer only when requested or necessary.

## Write in plain language

Follow these rules in the reader-facing explanation:

- Explain the thing before naming the term: “在自己的数据上表现好、换一批数据就掉很多——这叫数据集偏差”。
- Introduce at most one or two new terms in a section.
- Prefer Chinese when writing Chinese. Keep canonical English in parentheses only when useful.
- Keep one main idea per paragraph. Prefer short sentences with explicit subjects.
- Replace labels with mechanisms. Do not say “P3 proves”; say what changed, in which experiment, and what else changed at the same time.
- Translate every equation into one ordinary sentence and explain why it exists.
- Use tables only for genuine comparison. Do not turn the whole report into forms.
- Use a figure only when it removes explanation burden; interpret it immediately.
- Distinguish source visuals from generated teaching visuals in every caption.
- End the teaching layer with a short retelling the reader could say aloud.

Avoid theatrical or adversarial wording unless the user explicitly asks for it. Do not use headings or framing such as “审判”, “审讯”, “革命”, “杀伤力”, “旧世界”, “终极真相”, “legacy”, or “verdict”. Prefer “为什么难”, “作者怎么做”, “证据够不够”, and “哪些地方还不确定”.

Do not expose these in the default teaching layer:

- claim IDs such as P1/E2;
- evidence-class labels;
- commit hashes, code line numbers, or long source manifests;
- reviewer jargon such as confounder, load-bearing claim, validity threat;
- author biography, literature chronology, or implementation inventory before the method is understood.

These may appear in the technical appendix when useful. Claim IDs are internal by default and become reader-facing only in explicit reviewer/audit mode.

## Choose the mode and paper type

Use the smallest mode that satisfies the request.

| Mode | Main output |
| --- | --- |
| `full` | Three-layer explanation plus selective appendix |
| `field-map` | Prerequisite concepts and branching technical map |
| `method` | Intuition, sample trace, formalization, failure modes |
| `reviewer` | Explicit claim-to-evidence audit and missing experiments |
| `implementation` | Reproduction stages, interfaces, diagnostics, missing details |
| `figure-table` | How selected visuals support the argument |

Classify the work before reading deeply:

| Paper type | Emphasize |
| --- | --- |
| Method/model | representation, information flow, objective, ablation |
| Dataset/benchmark | acquisition, annotation, splits, leakage, bias, metrics |
| System | interfaces, scale, latency, reliability, deployment trade-offs |
| Theory | definitions, assumptions, proof idea, counterexample |
| Empirical/clinical | study design, sample, endpoint, statistics, confounding, ethics |
| Survey/position | scope, selection method, taxonomy, omissions, argument |

Infer the reader's background. For an unfamiliar reader, define only the 3–5 concepts needed to follow this paper and mark everything else “later”.

## Research before writing

### Resolve the exact work

1. Confirm title, authors, venue or repository, year, and analyzed version.
2. Inspect the supplied full PDF. Do not infer methods or experiments from an abstract.
3. Use the matching supplement, official project page, and official code when they change interpretation or reproduction.
4. Use first-party author/lab pages and primary papers for people, history, and later work.
5. Search the official paper/project repository, lab organization, and relevant author GitHub accounts. Verify ownership through the project page, paper, author profile, or organization identity; label third-party repositories as third-party.
6. Record the analysis date for current positions, code state, dataset access, and recent frontier claims.
7. State unavailable material once and narrow the claim. Never simulate reading it.

Stop researching when the central mechanism, decisive evidence, and important boundary are supported. Do not collect sources merely to make the report look exhaustive.

### Maintain evidence internally

Before polished prose, keep a private working map for important claims:

| Field | Record |
| --- | --- |
| Claim | one falsifiable statement |
| Type | paper states / external fact / derived / inference / unknown |
| Source | exact version and PDF page, figure, table, equation, or official link |
| Strength | establishes / supports / is consistent with / unresolved |
| Boundary | competing explanation, protocol exception, missing control, or scope limit |

This map prevents hallucination; it is not the structure of the teaching story. In default full mode, publish only compact source notes in the appendix. Show the full audit table only in `reviewer` mode or when the user asks to verify claims.

Use wording that matches support:

- “在这组实验里可以确认……” for a direct controlled result;
- “结果支持……” for bounded evidence;
- “结果与……一致，但还不能排除……” when factors change together;
- “一种合理解释是……” for inference;
- “论文没有给出……” for unknowns.

Treat “更便宜、快速、可扩展、低成本” as evidence-dependent claims. Component timings do not establish total cost.

## Read in four passes

1. **Orient:** title, abstract, introduction, conclusion, headings, figures, tables. Identify the problem, key move, and main evidence.
2. **Reconstruct:** related work, method, appendix, and implementation. Rebuild inputs, outputs, stages, variables, objectives, assumptions, and inherited components.
3. **Check:** connect every important claim to an experiment; inspect captions, footnotes, baselines, splits, ablations, failure cases, and alternative explanations.
4. **Map outward:** research only the predecessors, follow-ups, people, code, and datasets that change understanding or next action.

## Build the explanation

### Start from a concrete difficulty

Define the task as input -> output. Show why information is missing, noisy, expensive, or ambiguous. Explain why one or two obvious solutions are insufficient. Avoid a broad history lecture before the problem is clear.

### State the key move in one sentence

Use this internal scaffold:

```text
Previously:
The bottleneck was:
The paper changes:
Therefore:
```

Rewrite it as natural prose. Do not present this form mechanically unless it improves readability.

### Trace one sample

Choose one image, patient, sensor trace, theorem instance, or request. Follow it through the relevant stages. For papers with several operational systems, keep these boundaries clear:

| Stage | Question |
| --- | --- |
| Acquisition | What raw information is collected? |
| Annotation/preparation | How is supervision produced? |
| Training/optimization | What is learned or solved? |
| Inference/deployment | What information is available at use time? |
| Evaluation | Against what target and protocol is success measured? |

Explain privileged information plainly: expensive sensors or labels may be used while preparing data even if the deployed model never receives them.

### Move from intuition to mathematics

1. Give the smallest intuition.
2. Define only the variables required for the core mechanism.
3. Show the information flow.
4. Include only equations that change understanding.
5. Translate each equation immediately.
6. State assumptions and a realistic failure case.
7. Separate the paper's invention from inherited machinery.

### Explain evidence as answers to questions

Do not lead with a table number. Lead with the question it answers:

- Does the method work outside its own data?
- Which component actually matters?
- Is improvement due to the proposed idea or simply more data/compute?
- Does the label measure the desired physical quantity?

Then name the figure/table, explain how to read it, give the result, and state what it does not show. For a local Markdown report, embed 2–4 legible crops only when they materially help. Preserve the figure/table identifier and source-page location.

Teach metric semantics before using scores: direction, units/range, alignment or normalization, evaluated subset, aggregation, and split. Mark unverified details unknown rather than filling them in.

### Use visuals as teaching tools

Use a visual only when it communicates a relationship faster than prose.

1. Prefer inspected figures and tables from the focal paper for architecture, apparatus, examples, and results.
2. Crop legibly, preserve the figure/table number and page, and explain what the reader should notice.
3. Use image generation only for a conceptual illustration the paper does not already provide well, such as a train-versus-deployment boundary, an ambiguity, or a memorable analogy.
4. Label every generated asset **“AI 生成的教学示意图，不是论文原图，也不表示额外实验结果”**.
5. Do not use generated images to depict numeric results, exact architectures, author likenesses, laboratory history, benchmark rankings, or undocumented hardware.
6. Keep generated diagrams sparse and verify countable constraints, direction of arrows, labels, and scientific meaning before embedding them.
7. In a default full report, use 2–4 source visuals and at most 1–2 generated teaching visuals. Omit image generation when the paper already explains the idea clearly.

### End with bounded takeaways

State in plain language:

- what the paper demonstrates in its own setting;
- what looks promising but was not isolated;
- what remains unknown;
- three reusable ideas;
- one sentence the reader can repeat.

Concentrate uncertainty in one short “哪里不能信太满” section. Do not interrupt every paragraph with disclaimers. Never strengthen the final summary beyond the appendix evidence.

## Adapt the optional appendix

Include only sections that answer a likely next question.

### Figures and experiments

For each selected visual, record its exact location, reading method, conclusion, caption exception, and limitation. For a dataset paper, distinguish time instants, views, subjects/scenes, and augmented files. Check whether every “test” column truly uses a held-out test split.

### Reusable principles

Extract 3–5 decisions, not renamed components. For each, state the conclusion, why it works, prerequisites, failure boundary, and a transfer example.

### Reviewer mode

Only in explicit reviewer mode, publish the detailed claim map. Give the strongest sympathetic reading and strongest alternative explanation. Identify hidden assumptions, unfair comparisons, missing controls, shifted-domain failures, and the single most discriminating missing experiment. Say “our assessment” unless actual public reviews were inspected.

### Implementation mode

Separate:

| Topic | Paper says | Official artifact does | Still unknown | Recommended check |
| --- | --- | --- | --- | --- |

For dataset papers, distinguish using the released benchmark from rebuilding its data-production pipeline. Turn the latter into stages with inputs/outputs, coordinates, initialization, objectives/weights, optimizer, acceptance rules, human work, released artifacts, and missing fields. Never invent runtime or hardware cost. Pair every engineering risk with a diagnostic.

### People and technical lineage

Include authors and labs when their prior capability explains why the paper was possible. Place this after the reader understands the method, not before the problem statement.

Organize the section around capability lines rather than author order:

- identify the publication-time institutions and collaboration boundary;
- profile the first author, senior/corresponding author, and only the other authors whose verified prior work explains an essential capability;
- connect 2–5 earlier or later works to the focal paper with an explicit relationship;
- link the official lab GitHub organization, focal-paper repository, direct predecessor/follow-up repositories, and relevant author accounts;
- state what each repository actually contains and what remains unreleased.

Separate publication-time facts, current facts checked on the analysis date, plausible lineage, and unknown individual contribution. Do not infer module ownership from author order. A missing or stale profile must be labeled unresolved rather than replaced with a guessed biography.

Build a branching technical map. Label edges by the capability inherited or gap addressed; chronology alone does not prove influence. For current field maps, search through the analysis year or state the cutoff.

### Research opportunities

Recommend a selective path, not a bibliography dump. For each opportunity, give the gap, hypothesis, first discriminating experiment, success signal, failure signal, and risk.

## Full-mode output contract

A default full report normally contains:

1. Title and 30-second understanding;
2. Five-minute plain-language walkthrough;
3. One running sample, 2–4 useful source visuals when available, and at most 1–2 clearly labeled generated teaching visuals;
4. One concise “why believe it” section;
5. One concise “where confidence stops” section;
6. Three reusable ideas and a one-sentence retelling;
7. A compact author/lab capability bridge with related work and official repositories when sourceable;
8. Optional technical appendix with paper identity/sources, exact method and metrics, selected experiments, implementation, extended lineage, and next reading.

Do not force six full biographies, reviewer audit, research opportunities, every equation, or every table into the default report. Include only the people and projects that explain the paper's origin or enable the reader's next step.

## Quality gate

Before delivery, verify:

- A newcomer can state the problem and key move after the first screen.
- The five-minute walkthrough works without reading the appendix.
- The explanation begins with ordinary language, then introduces terms.
- The main layer uses no claim IDs, evidence taxonomy, reviewer jargon, commit hashes, or code line numbers.
- No theatrical/adversarial headings or exaggerated verbs appear.
- Each paragraph advances one idea; jargon and English are sparse.
- One concrete sample connects the problem, mechanism, and outcome.
- Source figures and generated illustrations are visibly distinguished; generated images do not invent evidence or undocumented system detail.
- The decisive experiment answers an explicit question.
- Important metric, split, caption, and protocol exceptions are accurate.
- Acquisition, annotation, training, inference, and evaluation are not conflated.
- Strong verbs, cost claims, and causal claims match the evidence.
- Limitations appear once, without dominating the story.
- Technical details and source locations are available but optional.
- The author/lab section explains capabilities and relationships, not merely credentials; official GitHub links state their scope and missing pieces.
- The final sentence is memorable and no stronger than the evidence.
- Repeated conclusions have one canonical home.
