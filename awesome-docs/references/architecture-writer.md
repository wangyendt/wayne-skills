# Architecture Writer: Choose a Depth, Trace Evidence, Draw One View

Load this guide for architecture descriptions and architectural decisions. Apply the destination and naming rules in [../SKILL.md](../SKILL.md) first. The L1–L4 labels below are this skill's writing depths, not an external standard or a maturity ranking.

## 1. Turn the Request into a Writing Contract

Before drafting, extract five fields from the request and existing project documents:

| Field | Record | If missing |
| --- | --- | --- |
| Reader question | One question the page must answer | Infer from the requested change or explanation; ask only if the scope remains materially ambiguous. |
| Subject boundary | One system, runtime unit, component, or mechanism | Locate the named subject in the project before choosing a filename. |
| State | Current implementation, observed deployment, proposal, or historical snapshot | Use current implementation for a request about existing code; do not imply deployment was inspected. |
| Depth | L1, L2, L3, or L4 from the table below | Choose the shallowest depth that answers the question. |
| Evidence scope | Inspected revision, configuration, tests, logs, and their dates when known | Record what was actually inspected; leave unavailable versions or runtime facts unverified. |

Keep this contract as a short scope paragraph in the output, not a separate mandatory planning document. Example: “本页解释当前源码中的报告生成链路，展开到进程内组件；依据提交 X。未核实生产部署拓扑。” Replace X only with a revision actually inspected.

For a broad “write an architecture overview” request with no audience, scope, or depth specified, start with a short L1 boundary and an L2 map. An explicitly high-level overview for a leader can stop at L1. Do not expand every unit to L3 or L4 automatically. For a narrow question, show one sentence or inset locating the subject in its parent, then write only the required depth.

## 2. Select the Depth by the Reader's Question

| Depth | Reader should be able to answer | Entity inside the main view | Default file when no canonical page exists |
| --- | --- | --- | --- |
| L1 — System boundary | Who uses this system, what does it exchange, and what is outside it? | The system as one box, users, external systems | `docs/architecture/system-overview.md` |
| L2 — Runtime structure | What executes or persists independently, and how do those units cooperate? | Processes/services, independently running jobs, stores | The same overview, or `docs/architecture/runtime.md` if it outgrows that page |
| L3 — Component responsibilities | Inside this selected unit, which component does what and owns which state? | Logical components/modules within one named runtime unit | `docs/architecture/<unit>/README.md` or an existing subsystem page |
| L4 — Local mechanism | How does one difficult operation, state transition, or algorithm actually work? | A selected component's steps, states, data structures, invariants | `docs/architecture/<unit>/<mechanism>.md` |

A deployment view and a sequence view are **additional views**, not deeper levels. A class is not a process merely because it has its own file. A process is not a host; several processes may share one host. A database's logical role does not establish its physical installation.

Routing examples:

- “让 leader 看懂这个工具和产线是什么关系” → L1, plus L2 only if operational ownership matters.
- “本地网页、后台和数据同步脚本怎么连接” → L2; add deployment mapping if their locations matter.
- “导出服务里解析、拟合、渲染怎么分工” → L3 within the export unit.
- “重试为什么不会重复写结果” → L4 of the write/retry mechanism; link the broader L3 page.
- “画所有类的关系” → inspect the requested scope, then use a focused L4 class relationship view; do not present an exhaustive class graph as the system overview.

## 3. Build the Evidence Map Before Writing Claims

1. Find the canonical architecture page and its linked ADRs, references, and plans. Note conflicts instead of silently choosing the most polished description.
2. Locate the requested subject in actual entry points, imports/calls, configuration, schemas, tests, and available runtime records. Search by names from the user or code, not a generic inventory of imagined services.
3. Make a compact working table: `entity or relationship | claim | evidence location | evidence scope | uncertainty`.
4. For each planned box, record why it exists and where its boundary is established. For each planned arrow, record producer, consumer, direction, payload/control meaning, and evidence.
5. Trace one representative operation end to end. Follow actual call paths or records across the selected boundary. Stop at external systems unless their internals are part of the request.
6. Resolve material conflicts where evidence permits. Source code establishes an implementation path; a deployment file establishes configuration intent; an observed runtime record establishes behavior for that observation. Keep these scopes distinct.
7. Draft only the claims supported at that scope. Label deductions as deductions and list the observation needed to verify them.

If an entry point, state owner, or connection is not established, omit the invented box/arrow and write the specific gap. Continue with the supported portion when useful. If that gap determines the entire topology, stop topology expansion and ask for the missing repository/configuration or record a narrow unresolved boundary. Do not turn “a cache would be useful” into “the service uses Redis.”

The working table can remain internal. Preserve enough source links beside claims or in a short evidence section for the reader to repeat the inspection. Do not copy entire source files into the architecture page.

## 4. L1 — Write the System Boundary

**Input:** the writing contract, user/consumer evidence, externally visible inputs and outputs, existing product or interface descriptions.

### Execute

1. Write one sentence naming the system and its useful result, using project terminology.
2. Identify users and external systems that directly exchange something with it. Separate a human role from a software actor.
3. For every exchange, name the direction and the thing exchanged: a request, a file, an event, or a result. Avoid arrows labelled only “connects.”
4. Draw the system as one box. Place external actors outside its boundary. Keep internal modules out of this view.
5. Add an exchange table: `external actor | input to system | output from system | relevant constraint | source`.
6. Explain one normal user journey in three to six steps using the same actor and system names as the diagram.
7. State exclusions explicitly, then link to the L2 page if a reader needs internal cooperation details.

**Output:** a scope paragraph, one boundary diagram when useful, an exchange table, a short journey, and source links. A small system can combine the table and journey rather than repeat them.

**Stop at:** the external contract. No classes, worker threads, SQL tables, or internal function calls. Expand to L2 only when the reader asks who executes/stores something or which internal boundary affects the answer.

**Accept / return:** a reader can name the system's purpose, input, output, users, and exclusions without reading code. If they must infer an arrow's direction or whether a box belongs inside the system, revise the view before continuing.

## 5. L2 — Write Runtime Cooperation

**Input:** L1 scope plus entry points, service/job startup definitions, inter-process interfaces, persistence definitions, and available runtime observations.

### Execute

1. List units that run independently or persist data independently. Confirm each executable boundary from a startup path or runtime/configuration evidence. Do not promote every package into a service.
2. Assign each unit one primary responsibility and state whether it is a long-running process, invoked job, or store.
3. Build a unit table: `unit | kind | responsibility | input/output interface | state owned | source`.
4. Draw only these units and relevant external actors. Label arrows with interaction type and content, for example “HTTP: submit report request” or “file: read session JSON,” only when supported.
5. Trace the representative operation across units. Name the writer and reader for each persisted artifact; distinguish authoritative state from copies or caches when established.
6. Add failure boundaries relevant to the reader's question: what remains available if a unit stops, where an error is returned, and whether a retry exists. Mark unverified behavior rather than promising fault tolerance.
7. Link detailed interface definitions to reference. Add a deployment overlay only if host/device/network placement is needed and evidenced.

**Output:** a runtime map, unit responsibility table, one cross-unit flow, and relevant failure/uncertainty notes. Reuse the L1 paragraph or link rather than redraw unrelated context.

**Stop at:** independently executing/persisting units and their contracts. Keep internal parser classes and mathematical routines out. Expand one selected unit to L3 when its responsibility is too broad to explain ownership or a change boundary.

**Accept / return:** every unit has a supported runtime/store identity, and every arrow names an exchange. If a box is merely a source folder, move it to L3. If “runs on server A” is inferred from a URL alone, remove the placement claim until verified.

## 6. L3 — Write Responsibilities Inside One Unit

**Input:** one selected L2 parent, its entry points, call/import relationships, data structures, interfaces, and relevant tests.

### Execute

1. Name the parent unit at the top. Write which of its operations this page covers; avoid expanding all siblings.
2. Follow the representative operation through that unit. Group code by cohesive responsibility, not mechanically by file count.
3. For each component, identify what it accepts, what it returns or changes, what state it owns, and what it explicitly leaves to another component.
4. Build a responsibility table: `component | responsibility / non-responsibility | inputs → outputs | state / side effects | implementation locations`.
5. Draw components inside the parent boundary. Mark arrows as calls, events, or shared-state access according to evidence. Keep external dependencies outside the parent.
6. Explain the operation in numbered steps, naming validation, transformation, state mutation, and error propagation where they occur.
7. Record a consequential boundary rule, such as which layer may write results, only if code/tests or a documented decision supports it. If practice violates the intended rule, describe both rather than hiding the conflict.
8. Link each tricky mechanism to L4 only when the reader needs its internal logic. Link exact signatures and field tables to reference instead of duplicating them.

**Output:** one parent-scoped component diagram when useful, a responsibility table, one execution narrative, and implementation/evidence links.

**Stop at:** contracts and ownership between components. Do not enumerate every helper or method. Expand to L4 when an invariant, numerical step, lifecycle, concurrency rule, or failure mechanism remains unexplained by the component boundary.

**Accept / return:** the reader can identify which component to inspect for each step and which component owns each mutation. If two components have indistinguishable responsibilities, inspect the actual split or combine the prose; do not invent a clean separation absent from code.

## 7. L4 — Explain One Local Mechanism

**Input:** a named L3 component, the exact operation under discussion, implementation branches, relevant data structures, and tests or reproducible traces.

### Execute

1. State the triggering condition, initial state, inputs, expected outputs, and why this mechanism deserves detail.
2. Choose the smallest useful representation: numbered algorithm for transformations, state table for lifecycle, sequence for interaction, or a small class/data relationship view for ownership.
3. Trace one concrete supported input through every decision that changes the result. Explain variables and state before using them. Use pseudocode only when it clarifies the implementation rather than becoming a second source of code truth.
4. Write the invariant or correctness condition in plain language, then a formula if needed. Link the condition to the branch, check, or test that enforces it; label an untested expectation accordingly.
5. Trace one relevant failure or boundary case, including state left behind and recovery behavior only where implemented or explicitly proposed.
6. If formulas drive the mechanism, define symbols and units, show the necessary intermediate steps, and link a longer derivation to a book or know-how page. Do not hide a mathematical assumption behind an architecture label.
7. Provide exact source/test locations and the inspection version. Include a reproduction command only if its inputs and expected observation are known; do not claim an unrun test passed.

**Output:** a focused mechanism explanation, an algorithm/state/interaction view, one normal trace, one relevant edge trace, and verification evidence or an explicit verification gap.

**Stop at:** what proves or explains this mechanism. Avoid full-file listings, unrelated helpers, and complete API catalogs. Detailed rollout work belongs in a plan; general teaching beyond this mechanism belongs in books or know-how.

**Accept / return:** a reader can follow the input to the output and identify where the invariant could fail. If a key branch is skipped with “the framework handles it,” inspect that behavior or narrow the claim. If the explanation is just a class list, replace it with the operation trace.

## 8. Add Only the Views Needed to Answer the Question

### Deployment view

1. Start with known L2 units; do not invent new logical components while drawing hosts.
2. Inspect actual configuration or runtime evidence for unit → process/container → host/device mapping.
3. Draw labelled containment and network boundaries; state whether the view is configured, observed, or proposed.
4. Record replicas, storage attachment, ports, and trust/failure boundaries only when relevant and evidenced.
5. Verify that logical component names match the main page and that “remote,” “local,” or “production” has an explicit frame of reference.

A missing deployment map does not invalidate a source-backed logical architecture page. State that deployment placement is outside verified scope rather than guessing where components run.

### Sequence or state view

1. Select one scenario and give its precondition.
2. Reuse entities from the selected depth; do not mix a host, a method, and a whole subsystem as interchangeable peers.
3. Label each arrow with operation/data and distinguish a call, response, or asynchronous event where supported.
4. Show one relevant alternative/error branch if it changes the explanation.
5. Finish with the resulting state and its owner. For a state table, include `state | event / guard | action | next state`.

### Diagram checks

Use the project's existing diagram format. Keep editable source with generated assets when practical. Each figure needs a scope/title, boundary labels, arrow meanings, and a short explanation of the important path. Keep one abstraction depth per main view; use a clearly labelled inset or link for a zoom. Verify rendered labels and links if a renderer is available; otherwise state that rendering was not checked.

## 9. Same Fictional System at Four Depths

This example is invented to demonstrate writing, not a description to copy into a real project. Assume a small “采集报告工具” has a browser, one report process, and a local result directory. Inside the report process, a reader loads CSV, an evaluator computes metrics, and a writer saves the report.

| Depth | What the page says or draws | What it deliberately leaves out |
| --- | --- | --- |
| L1 | “操作员提交一次采集记录，工具返回可查看的报告。” Draw operator → report tool → operator; identify the incoming CSV file. | Browser/server split; parsing helpers. |
| L2 | Browser sends a report request to the report process; the process reads the input file and writes the result directory; the browser displays the response. Identify the directory as file storage, not a database service. | Reader/evaluator/writer internals; which physical computer hosts the process unless separately verified. |
| L3 | Inside the report process: reader owns parsing/validation, evaluator maps validated rows to metrics, writer owns output creation. List each component's concrete input/output and the error handoff. | How one invalid row is recognized internally. |
| L4 | Trace reader validation for a selected CSV row: obtain the expected schema, check required cells, parse values, return a valid record or a specified error; show one accepted row and one rejected row. | Report publishing or other unrelated workflows. |

To write this for an actual repository, replace every assumed entity and behavior with inspected evidence. If evaluation and writing are not separate components in that code, document the actual combined responsibility rather than preserving this example's tidy split.

The cross-level links should form a zoom path, not four competing summaries: overview → selected runtime unit → selected component mechanism. Keep deployment as a separate named view of the same runtime units.

## 10. Route Decisions and Future Work Without Rewriting Reality

| Material found during inspection | Action | Canonical output |
| --- | --- | --- |
| Confirmed implementation structure | Describe it with inspected revision and limits | Living architecture page |
| Observed runtime placement | Add an observation-scoped deployment view | Architecture page or linked deployment page |
| Possible redesign | Label its assumptions, proposed boundaries, and unresolved choices | Clearly marked proposal section/page; ADR if a durable decision is needed |
| Confirmed architectural choice | Record context, alternatives and evidence, decision, status, consequences | `docs/architecture/adr/YYYYMMDD_<decision>.md`, preserving any existing ID convention |
| Accepted design not yet implemented | Keep current state and target state separate | ADR/target view plus linked plan |
| Migration or rollout steps | Extract sequencing, validation, and rollback | `docs/plan/YYYYMMDD_<change>.md` |
| Historical performance result | Link the dated run and its conditions | Experiment record; do not promote it into a universal architectural guarantee |

When writing an ADR, first locate the actual decision and its status. Then reconstruct only alternatives and rationale supported by notes, code history, measurements, or user input. Mark newly suggested alternatives as new analysis, not options the team previously considered. An ADR may record “rationale not preserved”; do not invent a persuasive history.

## 11. Final Acceptance and Revision Loop

1. **Scope check:** read the question and the first paragraph together. If they differ, narrow the page or explicitly agree a broader scope before expanding it.
2. **Depth check:** assign every box/section to its depth. Move accidental internals into a linked zoom or remove them if unnecessary.
3. **Evidence check:** select every component, ownership claim, and important arrow; locate its evidence. Replace unsupported certainty with a precise gap, or return to inspection.
4. **State check:** search for future-tense intent presented as present-tense behavior. Separate current, observed, proposed, accepted, and retired states.
5. **Trace check:** walk the representative operation using only the page. Fix missing inputs, unexplained transitions, and ambiguous state ownership.
6. **Boundary check:** ensure module, runtime unit, container, host, and external system are not treated as synonyms.
7. **Maintenance check:** verify canonical paths, parent/child links, source references, diagram assets, and relevant ADR/plan links. Update affected existing views instead of leaving contradictory copies.
8. **Reader check:** confirm the requested question is answered at the chosen depth. Remove detail that does not help answer it. Deliver the edited files, chosen depth, and remaining evidence gaps; do not claim live deployment verification from a source-only review.
