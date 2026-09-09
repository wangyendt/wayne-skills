# Execution Workflows for Project Records

Read only the section for the current document. Paths, naming, existing-file precedence, and final polishing follow [SKILL.md](../SKILL.md). The examples are writing examples, not results from the current project. [templates.md](templates.md) supplies optional page shapes; perform the workflow before filling a template.

## Navigation

- [Experiment](#experiment-turn-a-question-into-an-auditable-comparison): comparison design, denominators, metrics, and run evidence.
- [Knowhow](#knowhow-choose-explanation-troubleshooting-or-procedure): explanation, diagnostic branches, and operating steps.
- [Reference](#reference-extract-a-contract-instead-of-inventing-one): extract and verify exact contracts.
- [Plan](#plan-expand-an-outcome-into-dependency-ordered-work): implementation order and checkpoints.
- [Roadmap](#roadmap-convert-task-clusters-into-observable-outcomes): outcomes, dependencies, and acceptance.
- [Todo](#todo-preserve-a-small-action-without-expanding-its-scope): minimal update and truthful state transitions.

## Start With the Available Evidence

1. Locate the requested document and its linked source files. Separate user-reported facts, inspected implementation, observed results, assumptions, and proposed work in working notes.
2. Record the source path, revision or date, and applicable scope for each consequential claim. A path alone does not establish that its content was inspected.
3. Choose the workflow below. If the request mixes purposes, update the canonical pages for those purposes and cross-link them; do not duplicate evidence tables.
4. Read available sources before asking for details. Ask only when a missing input changes the intended conclusion or execution path; otherwise mark the gap and write the supported portion.
5. Keep writing and execution separate. Documenting a command does not authorize running it, changing data, committing, or publishing. Run only checks within the user's task and report what actually ran.

Keep this small source-to-claim map in working notes when the document combines several materials. Include it in the deliverable only when it helps audit a complex result:

| Claim to write | Evidence to inspect | If evidence is missing |
| --- | --- | --- |
| “The field defaults to a value” | Default construction and configuration precedence for the applicable version | Mark the default unknown, even if an example supplies a value. |
| “The new method reduces variation” | Comparable data, defined variation statistic, and actual computed outputs | State the hypothesis or planned comparison, not a result. |
| “The migration is complete” | Actual migration output and post-migration invariants | Preserve the current step status and name the missing verification. |

## Experiment: Turn a Question Into an Auditable Comparison

**Inputs:** the question, baseline and alternative, available data and logs, metric code, run configuration, and any prior acceptance criterion. Default output: `experiment/YYYYMMDD_<topic>.md`.

### 1. Establish What Has and Has Not Run

1. Read the user request and available run artifacts. Label the record `planned`, `running`, `completed`, or the project's equivalent based on evidence, not on the presence of a script.
2. For a future experiment, write the hypothesis, comparison, exclusions, metrics, and decision rule before execution. Record their version so later changes can be identified.
3. For historical analysis, record which choices were fixed beforehand and which were selected after seeing the data. Label new hypotheses exploratory; do not describe them as preregistered tests.
4. If modifying a past report, preserve the original setup and results. Add a dated correction or follow-up section with its reason and sources; create a new record for an independent run.

Convert a broad goal into a testable question before writing the setup:

| Vague input | Write this decision before analysis |
| --- | --- |
| “方法 B 更稳定吗？” | Define stability, the same inputs used by A and B, the statistic being compared, and which outcome would change the choice. |
| “新阈值良率多少？” | State the cohort, denominator, pass predicate, exclusions, and whether labels exist to evaluate actual product quality. |
| “工位造成差异吗？” | List station membership, repeated units, time/version differences, and what history can separate from what needs a controlled test. |

### 2. Freeze the Comparison Unit and Denominator

1. Inspect the data schema and identifier columns. Decide whether one observation means a physical unit, an SN, a session, a run, a frame, or a point. Write the choice explicitly.
2. Check uniqueness using that key. If an SN has repeated sessions, decide whether to retain all sessions, select one by a stated rule, or aggregate within SN. Do not silently count repeated sessions as independent machines.
3. For before/after or multi-setting comparisons, identify the pairing key. Verify one usable observation per key and condition after the stated selection rule.
4. For paired comparisons, use the intersection of eligible keys by default; list losses by condition. If an unpaired population view is also useful, show it separately with its own denominator.
5. Write a cohort flow: source rows → eligible rows → usable measurements → paired units. Give exclusion reasons and counts after computing them; do not fill counts from memory.
6. Inspect missingness, invalid values, repeated keys, and grouping by host, station, version, and time when relevant. Explain which distributions could change with the comparison condition.
7. A frozen baseline keeps its original cohort and definition. Do not quietly replace it with a refreshed or paired cohort; label both and show why their counts differ.

For example, “三档配对” means the same selected session has usable near, middle, and far measurements. It does not mean taking every near row and every far row independently because both are available.

### 3. Define Each Metric Before Calculating It

Make one metric table with: name, formula or implementation, input columns, units, aggregation unit, direction, validity conditions, and interpretation limit.

For a threshold replay, define the empirical cumulative proportion as:

\[
\widehat F(t)=\frac{1}{N}\sum_{i=1}^{N}\mathbf 1[m_i\le t].
\]

Here \(t\) is the candidate threshold in the same units as metric \(m_i\); \(i\) indexes eligible observations from 1 through \(N\), the stated positive denominator. The indicator \(\mathbf 1[\cdot]\) is 1 when its condition is true and 0 otherwise, so \(\widehat F(t)\) is a dimensionless proportion. An empty cohort has no estimated pass proportion, not zero percent. Write whether equality passes. This estimates historical threshold pass proportion, not product quality or future yield by itself.

1. Match metric formulas to inspected code. Check sign, absolute values, coordinate frame, units, reference point, and invalid-input handling.
2. For a normalized metric, name the denominator and explain why it is appropriate. Define the handling of a zero or near-zero denominator; never silently discard it.
3. For paired comparisons, compute differences within each pair before their summary. Do not replace paired differences with a comparison of two unrelated averages.
4. Distinguish dispersion of observations, standard error of an estimate, and model-prediction error. Name the quantity and estimation method when writing “standard deviation” or an error bar.
5. If uncertainty is needed, choose a method matching dependence: resample independent units or clusters rather than treating their points or repeated sessions as independent. State its assumptions and sample support.
6. If preprocessing, fitting, or threshold selection uses the data, include those steps in the evaluation design. A selected subset or training residual is not automatically an unbiased estimate of deployment error.
7. Keep formulas proportional to the question. Show intermediate arithmetic for an unfamiliar metric; link a derivation-heavy explanation to knowhow or a book instead of burying the comparison in theory.

### 4. Build the Reproduction Chain, Then Produce Results

1. Record actual source locations or query/filter definitions, acquisition window, code revision, environment, and parameter values. Distinguish unknown versions from known ones.
2. Record input identifiers or a small manifest with hashes when useful. A hash checks identity; preserve the data location or retention note separately.
3. Locate the script that reads those inputs and writes the metrics. If it exists, show its real command, working directory, and output paths. If only a proposed command exists, label it unexecuted.
4. Check a small calculation by hand or against an independent implementation before a large aggregate. For paired data, verify example keys and conditions explicitly.
5. When execution is in scope, capture exit status and inspect produced files. A successful process does not prove correct values; check row counts, units, finite values, and invariants.
6. Generate comparable tables with identical metric columns, units, scenario order, and uncertainty notation. Use a figure for a question a table hides: distribution shape, paired movement, time drift, or spatial pattern.
7. For each figure, write the reading question, cohort, axes and units, denominator, legend, and meaning of bands/markers. Label illustrative or simulated data as such.

### 5. Write the Record and Check the Claim

Write in this order: setup and cohort → metric definitions → results and traceable figures → interpretation → limits → opening summary. For a completed run, the summary states the answer and strongest evidence. For a plan, it states the question and pending evidence instead of a result.

After each result table, add one sentence saying what changed and one saying what the table does not establish. Separate physical reasoning, code behavior, association, and causal evidence.

| Check | If it fails, repair this part |
| --- | --- |
| Every reported value points to a run or reproducible computation | Remove unsupported numbers or label them pending; do not synthesize success output. |
| Cohort counts and denominators reconcile | Correct the selection/join and regenerate affected tables and conclusions. |
| The compared conditions differ only as claimed | Disclose confounders; narrow the conclusion or design a follow-up comparison. |
| Analysis choices were made after looking at results | Label the finding exploratory and separate later validation. |
| A chosen threshold is called an NG criterion | State whether labeled validation supports it; otherwise call it a candidate replay threshold. |

**Deliverable:** an evidence record with the answer or pending status, reproducible scope, comparable results, interpretation boundaries, and actual artifact links. Failed and missing runs remain visible.

## Knowhow: Choose Explanation, Troubleshooting, or Procedure

**Inputs:** the recurring situation, reader's task and level, observed symptoms, verified commands/code, and prior evidence. Default output: an existing canonical note or `knowhow/YYYYMMDD_<topic>.md`, following repository naming.

### 1. Pick the Reader's Entry Point

| Reader needs | Mode | Writing order |
| --- | --- | --- |
| “为什么会这样？” | Explanation | Concrete observation → simple model → assumptions → stepwise reasoning → worked example → when it fails. |
| “现在坏在哪里？” | Troubleshooting | Recognizable symptom → cheap discriminating checks → evidence branches → bounded intervention → independent verification. |
| “怎样重复完成这件事？” | Procedure | Preconditions and inputs → ordered actions → expected outputs → completion check → cleanup/rollback. |

If two modes are needed, lead with the user's immediate need and link a separate explanation. Do not force a short command recipe into a long root-cause essay.

### 2. Extract Evidence Before Naming a Cause

1. Inspect logs, code, configuration, and earlier experiments. For each proposed explanation, write its supporting evidence and the observation that would contradict it.
2. Label claims as **observed**, **derived under stated assumptions**, **supported by a cited test**, or **hypothesis**. These describe support, not a numeric confidence score.
3. Treat “the symptom disappeared after change X” as evidence, not proof of sole causation. List meaningful concurrent changes or alternative explanations.
4. State the versions, hardware, input conditions, and failure signatures where the recipe was checked. Where transfer to another setting is untested, say so.

### 3. Construct the Actual Route

For an explanation, build the argument in this order:

1. State a concrete question and the visible quantities involved: what is held fixed, what changes, and what the reader wants to predict.
2. Give every introduced symbol a plain-language meaning, unit, and role. Reuse existing book notation when linked; do not rename the same quantity for convenience.
3. State the simplest usable model and its assumptions. Explain what each term measures before manipulating it.
4. Change one algebraic expression at a time, naming the rule used, such as substitution, rearrangement, or a local-rate approximation. Insert the needed prerequisite before an unfamiliar operation.
5. Substitute a small, clearly illustrative numerical example and show the arithmetic and units. Check a limiting case, such as zero change, when meaningful.
6. Compare the explanation with available observations and name any disagreement. Distinguish “this model predicts” from “this run measured.”
7. State where the explanation applies and which condition would break it; link inspected implementation after explaining the model.

For sustained derivations, use [technical-book-writer.md](technical-book-writer.md) and its shared notation workflow instead. A short knowhow note can borrow these steps without creating a book directory.

For troubleshooting, make every check discriminate between possible next actions:

| Step | Check or command | Expected evidence | Next branch | Stop / restore condition |
| --- | --- | --- | --- | --- |
| 1 | Inspect the actual configuration file or documented read-only command | Active source/version is identified | Matches intended version → step 2; differs → investigate selection precedence | If the active source is still unknown, stop before changing parameters. |
| 2 | Compare the failing record with a known valid record using the same parser | The relevant field is present and correctly typed | Valid → inspect downstream handling; invalid → check producer | Preserve the failing record; do not overwrite it during diagnosis. |
| 3 | Apply a verified, bounded change only when execution is requested | The original symptom's check passes | Pass → run regression check; fail → revert the recorded change | Restore the saved configuration or snapshot and retain the new logs. |

Replace generic descriptions with actual inspected paths, commands, and fields when available. If the project has no known diagnostic command, name the file or observable to inspect; do not invent a CLI. A placeholder command must be labeled as a proposed example, not a tested procedure.

For an operating procedure:

1. List required inputs and a preflight check that distinguishes “ready” from “missing prerequisite.”
2. Order actions by their dependencies. For each state-changing step, state scope, expected output, and how its effect will be checked.
3. Put the backup or snapshot before the first destructive action, when such an action is in scope. State what it restores and where it is stored; do not imply every action is reversible.
4. Identify a stop condition for failed checks. Avoid chains that keep mutating state after an unexpected result.
5. Verify completion using the user's original symptom or goal plus a regression check, not merely a zero exit code.

### 4. Review by Walking a Reader Through It

Start from a representative symptom and follow only written links, branches, and commands. If a branch needs an unstated fact, add the missing check. If a command's expected output is unknown, mark it unverified and point to the source to inspect. Remove dead-end branches such as “检查配置” with no field or decision named.

**Deliverable:** one reusable explanation or route, its evidence and conditions, and a clear completion/stop rule. Link historical runs rather than copying their logs or presenting a hypothesis as a root cause.

## Reference: Extract a Contract Instead of Inventing One

**Inputs:** the requested version, authoritative schema/specification, implementation, tests, and existing generated documentation. Default paths: `reference/apis/`, `protocols/`, `schemas/`, or `configuration/`.

### Execution

1. Determine what the reader will look up: an endpoint, opcode, field, file layout, or configuration key. Use that exact identifier as a heading or table key.
2. Locate the applicable source definition and version. If a generated schema is authoritative, preserve its native format and generation workflow; link it from explanatory prose.
3. Trace a representative input from declaration through validation and consumption. For configuration, inspect default construction and precedence rather than treating a sample file as proof of a default.
4. Extract exact names, types, requiredness, units, ranges/enums, and missing/null/empty/zero behavior where defined. For wire protocols, also extract framing, byte order, lengths, state, and checksum scope.
5. Record output, error, and side-effect behavior from the implementation, tests, or specification. If sources disagree, show the versioned discrepancy and the unresolved question; do not silently reconcile it by guessing.
6. Build a lookup table, followed by the smallest useful valid and invalid examples. Derive examples from verified tests or contracts; label constructed examples and do not attach invented execution output.
7. Validate syntax/schema offline when possible. If validation requires changing remote or persistent state, document the check and its pending status unless that execution is explicitly in scope.
8. Check every example against the documented field table and version. Update definitions and examples together; preserve separate version boundaries when contracts differ.

Choose the inspection route by the reference type:

| Kind | Trace these sources in order | Smallest useful verification |
| --- | --- | --- |
| API | Routing/signature → input validation → handler → returned response/error | Compare a documented request/response with a matching test or offline schema check. |
| Protocol | Frame encoder → parser → dispatch/state handling → timeout/error path | Check length, byte order, and checksum coverage against a verified frame fixture. |
| Schema | Authoritative declaration → writer → reader → migration rules | Parse a valid fixture and check a specified invalid case without modifying source data. |
| Configuration | Default construction → file/environment/argument overrides → consumer → reload path | Explain which source wins in a known conflicting-input example; mark unchecked reload behavior unknown. |

| Source finding | Write in reference | Do not infer |
| --- | --- | --- |
| Key appears in a sample config, but no default was found | “默认值未核实；示例配置提供该值”，with source path | That the sample value is the runtime default. |
| Test asserts a specific error for one invalid input | That input and tested error, with version/test source | The same error for every malformed input. |
| Parser accepts an optional field but downstream use is unclear | Accepted syntax and unverified semantics separately | A supported end-to-end feature. |

**Deliverable and gate:** the reader can locate one identifier and find its exact supported meaning without reading a tutorial. Mark unsupported defaults, errors, and compatibility behavior as unknown; link a todo for consequential gaps rather than filling them with plausible values.

## Plan: Expand an Outcome Into Dependency-Ordered Work

**Inputs:** the requested outcome, current state, constraints, scope, relevant architecture/ADR/reference, and existing tests. Default output: `plan/YYYYMMDD_<change>.md`.

### Execution

1. Inspect the relevant implementation and docs. Write the current state and the exact desired observable change, then list non-goals.
2. Identify unresolved choices that affect implementation order. Resolve from sources where possible; otherwise make a decision/check step before dependent work.
3. List the necessary changes, then draw their dependency order in working notes. Group related changes into phases; do not list everything as parallel if it shares a migration dependency.
4. For each step, name the actual file/module or resource, action, produced artifact, entry condition, verification, and rollback/recovery. Unknown locations become an explicit discovery step, not a fabricated path.
5. Put compatibility, backup, and migration preflight before changing persistent formats or state. State whether rollback loses new data, requires a restore, or is unsupported.
6. Separate implementation tests, data migration checks, rollout gates, and user acceptance when they prove different things. Explain which failure stops the next phase.
7. Record risks with a triggering observation and a response. Keep unsupported owners or dates unset.
8. Write the summary last: chosen route, main trade-off, required decision, and first executable step. Keep steps `planned` until execution evidence exists.

| Step | Change | Entry condition | Acceptance | Recovery |
| --- | --- | --- | --- | --- |
| Inspect | Locate the schema writer and readers | Repository available | Actual producer/consumer paths recorded | Read-only; no state changed. |
| Extend | Add the optional field in the inspected locations | Missing-field behavior agreed | Existing fixtures still parse; new field round-trips | Revert code change; preserve test fixtures. |
| Migrate | Run the reviewed migration on a copied dataset | Snapshot verified and dry-run accepted | Key counts and defined invariants match | Restore from the verified snapshot if needed. |

This table illustrates step shape, not a ready-to-run migration. Replace it with the actual project's paths, invariants, and supported recovery method.

**Deliverable and gate:** another engineer can start step 1 and tell when to proceed or stop. If a step says only “完善测试” or “确保兼容,” replace it with the fixtures, supported versions, and checks that establish the claim.

## Roadmap: Convert Task Clusters Into Observable Outcomes

**Inputs:** current capability, proposed actions, known commitments, constraints, and dependency evidence. Default output: the existing roadmap or `roadmap/<topic>.md`.

### Execution

1. Read the current roadmap and related todos/plans. Mark what is observed today versus desired; do not reset achieved milestones when reorganizing.
2. Group actions by the capability they enable. Ask for each group: “What will a user be able to do, or what condition will be true, after this work?” Use that answer as the milestone.
3. Replace task counts with acceptance evidence. Name the test, report, user workflow, or operational observation that will demonstrate the outcome.
4. Order milestones by genuine dependencies. Separate a prerequisite from a preferred order; unresolved decisions become explicit gates.
5. Add owner, priority, or target window only from confirmed information. Record whether a date is a commitment or estimate; omit invented quarters and deadlines.
6. Link detailed execution to plans and next actions to todos. Do not copy their checklists into the roadmap.
7. On changes, retain the prior milestone ID and record what changed and why. Mark completion only with actual acceptance evidence; a merged change alone may not establish deployed capability.

| Task cluster | Milestone outcome | Acceptance evidence |
| --- | --- | --- |
| Parse inputs, validate fields, report errors | Inputs are either accepted under a documented contract or rejected with actionable errors | Versioned valid/invalid fixtures and their checked report. |
| Add refresh button, sync script, status UI | A user can refresh the analysis and identify the data snapshot used | An observed end-to-end refresh with source/snapshot identity and failure behavior. |

**Deliverable and gate:** each milestone has an outcome, proof, dependency, and truthful status. If there is no acceptance evidence yet, keep it planned or in progress; recording the roadmap is not delivering its outcomes.

## Todo: Preserve a Small Action Without Expanding Its Scope

**Inputs:** the user's note, existing queue, and any source or resulting work. Default output: the existing same-topic file or `todo/<topic>.md`.

### Execution

1. Search the queue for the same issue or intended action. Compare meaning and source, not only wording.
2. If it exists, update that item. Keep its ID and source/history; add the new evidence or sharpen its next action. If related items are merged, leave a short destination link for IDs already referenced elsewhere.
3. For a new item, identify its type: action, question, idea, risk, or blocker. Write one concrete next step rather than converting every idea into an implementation promise.
4. Use a single bullet for a small unlinked note. Introduce an ID or table only when the queue already uses one or tracking/cross-links require it.
5. For a blocker, name the blocking condition and what would unblock it. For a risk, name the possible impact, observed trigger if known, and next observation or mitigation.
6. Change status only when work or user instruction supports it. Preserve completed/dropped items with evidence or reason and actual date when known.
7. Promote when the work genuinely requires another document. Retain the source item with `promoted` and the destination link; the destination remains planned until its own work is done.

| Note received | Minimal useful edit |
| --- | --- |
| “记一下，需要查重连时间戳” | `- [ ] 检查重连前后时间戳是否连续；下一步：对比同一会话断线前后的相邻记录。` |
| “这事要等新固件” | Mark the existing item blocked; record the needed firmware behavior/version if known and the check that will unblock it. |
| “已经写成迁移方案了” | Mark promoted and link the real plan; do not mark the migration done. |

**Deliverable and gate:** a small, traceable update with a usable next action. Preserve the existing file and history; do not create a dated duplicate, full roadmap, or empty document tree for one note.
