---
name: awesome-docs
description: Use this skill whenever the user asks to record, organize, update, or maintain project documentation, including architecture overviews and decisions, technical books and derivations, API/protocol/configuration references, implementation plans, roadmaps, todos, risks, experiments, know-how, or common commands. Choose paths and naming by document purpose, preserve existing canonical locations, and check links when reorganizing. Defaults to the target project’s docs directory unless the user specifies another location. Covers reader-first technical explanations and interactive HTML documents as well as Markdown, with an opt-out final plain-language polish.
---

# Awesome Docs

Keep project knowledge easy to find, check, and update. Choose the document type and path by what the reader needs, and preserve enough context for another person or agent to continue the work without guessing.

## Standalone Use and Optional Skills

This skill supplies its own writing, illustration and review workflow. Use another skill only when it is listed as available in the current environment and adds value to the task; read its actual provided path, not an assumed sibling directory. If it or its relevant reference is missing, skip that enhancement and continue locally. Do not scan other agents' installations, install/update skills or prompt for installation as part of documentation work. If the user explicitly requested a missing skill, briefly disclose that it was not loaded rather than claiming to have used it.

## Shared Writing and Illustration Guides

For substantial writing or explanation rewrites, read [technical-writing.md](references/technical-writing.md): executable passes for reader questions, evidence and terminology, prerequisite order, findable headings, paragraph reasoning, actionable procedures, comparable reference tables, reproducible calculations and defect-based review. Each pass specifies what to inspect and how to repair a failed check. These rules apply to Markdown, HTML prose and teaching scripts. Small edits use only relevant checks.

When figures or interactive documents are needed, also read [interactive-illustrations.md](references/interactive-illustrations.md): LaTeX in all formulas, retained context with focused highlights, meaningful 3D/2D views, and interaction/delivery checks. Resolve the explanation before choosing effects. Architecture flows normally need 2D; spatial relationships often benefit from 3D. Do not force either on a small text task.

Document type still determines the writing order and depth below. Keep facts, logic, notation and audience fit ahead of presentation polish. The shared guides own these rules; specialized guides add only their domain-specific execution steps.

## Execute the Documentation Task

Use the steps below in order. Keep the working notes in memory or a temporary workspace; do not add a planning dossier to the user's repository for a small edit.

| Step | Action | Output before continuing | If the check fails |
|---|---|---|---|
| 1. Locate | Resolve the user's target, read its instructions, inspect existing docs and relevant changes. | Canonical file/root and edit scope; identify content to preserve. | Resolve a missing project path; do not write into an unrelated checkout. |
| 2. Route | State the reader's question, audience, document type, depth, and whether this is a new document or an update. Load the matching execution guide below. | One sentence such as “Explain this subsystem's internal responsibilities at L3 using verified code.” | Split genuinely different purposes with links, not duplicate content. |
| 3. Gather | Read the relevant code, configuration, source notes, results, or user decisions. Separate observations, assumptions, proposals, and missing evidence. | A small source-to-claim map; enough evidence for the requested scope. | Label the gap and narrow the claim. Ask only when missing input changes the destination or essential task. |
| 4. Design | Follow the guide to order the sections, choose tables/figures, and identify each section's input and output. For books, build the chapter dependencies and symbol ledger first. | An outline in which every section answers a reader question. | Drop empty template headings; add a prerequisite where a section uses an unexplained idea. |
| 5. Write | Draft from evidence in the guide's prescribed order. Apply the relevant shared-writing passes to headings, paragraphs and procedures; explain the reasoning between facts. | The requested document/chapters, with working links and source references. | Repair the specific missing explanation, unsupported claim, or unusable instruction. |
| 6. Verify | Apply the guide's depth/stop checks, then run the final review below. Recalculate worked examples and validate available local links/examples. | Checks actually performed, corrections, and explicitly unverified items. | Return to the step that produced the error; do not turn an unrun check into a success. |
| 7. Deliver | Apply the opt-out plain-language pass to settled prose, inspect the diff, and report paths and meaningful checks. | One maintained source and a short completion note. | Restore altered facts, formulas, statuses, or unrelated edits before delivery. |

For a one-line todo, these steps can mean reading the existing queue, finding the item, adding the line, and re-reading it. They do not require seven visible sections.

## Execution Guide Routing

Read the chosen guide before drafting, not only when the first attempt fails. Read only relevant sections.

| Task | Guide to execute | First decision and stopping boundary |
|---|---|---|
| Architecture or ADR | [architecture-writer.md](references/architecture-writer.md) | Choose a depth from the reader's question; stop before unrequested implementation detail. Deployment and sequence/state views are separate from depth. |
| Any book or chapter | [technical-book-writer.md](references/technical-book-writer.md) | Order chapters by prerequisites; settle global notation before formulas. Write connected chapters, not a pasted collection of notes. |
| Experiment, knowhow, reference, plan, roadmap, todo | Matching section of [record-workflows.md](references/record-workflows.md) | Execute its input → extraction → writing → verification steps; a small record stays small. |
| Substantial derivation inside another type | Symbol and derivation sections of [technical-book-writer.md](references/technical-book-writer.md) | Reuse the mathematical procedure without creating an unsolicited book. |
| Reusable command | Common Command Registry below | Preserve the command exactly; record its use without executing side effects merely to document it. |
| Placement or output shape is unclear | [document-types.md](references/document-types.md), [templates.md](references/templates.md), or [examples.md](references/examples.md) | Use these to choose an outline; they supplement, not replace, the execution guide. |

## Documentation Root and Scope

Use the user-specified location first. A path can identify different things:

- Project root: use its existing documentation layout, defaulting to `<project-root>/docs`.
- Documentation root, such as `docs/team-a`: put the requested category beneath it.
- Category or book directory, such as `docs/reference` or `docs/books/camera-geometry`: use it directly; do not append the category again.
- Exact file: update that file rather than inventing a parallel document.

For a path outside the active checkout, resolve that target repository and its instructions before editing. If the user names another project without giving its path, resolve that project from known context or ask for its location; do not silently write into the active checkout. Only when neither a target project nor a path is specified, use the current repository root; outside a repository, use the current working directory. Ask one concise question only if the destination remains materially ambiguous.

Respect existing locations such as `doc/`, `design/`, or an established book directory. The layout below is the default for new content, not a request to migrate old files. Move or rename existing documents only when the user asks to reorganize them.

## Default Directory Layout

```text
<docs-root>/
├── README.md              # navigation, when a collection needs an index
├── architecture/          # system structure and architectural decisions
│   └── adr/               # decision records, when needed
├── books/                 # sustained, chapter-based teaching
│   └── <topic>/
│       ├── README.md      # the book’s single reading entry
│       ├── 00_导读与符号.md  # canonical symbols, abbreviations, and conventions
│       ├── 01_基础模型.md
│       └── figures/
├── reference/             # lookup by API, command, field, or version
│   ├── apis/
│   ├── protocols/
│   ├── schemas/
│   └── configuration/
├── plan/                  # execution design for a defined change
├── roadmap/               # outcomes, milestones, and dependencies
├── todo/                  # living actions, ideas, questions, and risks
├── experiment/            # dated evidence and reproducible results
├── knowhow/               # reusable explanations and operating lessons
└── 常用命令.txt            # only when command capture is requested
```

Create directories and indexes on demand. A one-line todo does not require eight empty directories, a book scaffold, or a command registry. Add topic subdirectories only when they make a growing collection easier to navigate.

## Classification Rules

Classify by the reader’s question and how the content will be maintained, not by keywords alone.

| Reader’s question | Category | What belongs here |
|---|---|---|
| How is the system arranged, and why? | `architecture/` | Boundaries, responsibilities, interfaces, data/deployment flows, constraints, decisions |
| How can I learn this topic from the beginning? | `books/<topic>/` | Connected chapters, notation, derivations, teaching figures, source links |
| What exactly does this command, field, or interface mean? | `reference/` | Versioned facts, API/protocol contracts, schemas, defaults, units, error codes |
| How will we implement this specific change? | `plan/` | Scope, steps, dependencies, migration, validation, rollback |
| Which outcomes come first, and how will we judge progress? | `roadmap/` | Milestones, acceptance evidence, sequencing, priorities, confirmed time horizons |
| What should we investigate or do next? | `todo/` | Small actions, ideas, open questions, risks, blockers |
| What happened in this particular test? | `experiment/` | Setup, data, versions, results, limits, reproduction commands |
| How do I diagnose or handle this recurring situation? | `knowhow/` | Explanations, troubleshooting, procedures, lessons, reuse conditions |

Keep one canonical home for each piece of content. Link related documents rather than copying their tables and conclusions. For example, record a storage decision in an ADR, its rollout steps in a plan, and measured effects in an experiment. A protocol field table belongs in reference; a guide to diagnosing that protocol belongs in knowhow.

After classification, follow the execution guide routing above. The output shapes in [references/document-types.md](references/document-types.md) are examples, not a requirement to fill every heading.

## File Naming

Use names according to the document’s lifecycle. A date prefix is not required on every Markdown file.

| Kind | Default pattern / example | Maintenance rule |
|---|---|---|
| Experiment or dated technical note | `experiment/YYYYMMDD_主题.md`, `knowhow/YYYYMMDD_主题.md` | Preserve the original run or observation date; new experiments get new records |
| Change-specific implementation plan | `plan/YYYYMMDD_迁移方案.md` | Keep the same file while the plan develops; record revision dates inside |
| Current architecture description | `architecture/system-overview.md` or `<subsystem>/README.md` | Stable path; state the implementation version and review date |
| Architectural decision record | `architecture/adr/YYYYMMDD_决策.md` | Follow an existing sequence such as `0007_决策.md` if present; link superseding decisions |
| Book | `books/<topic>/README.md`, `00_导读与符号.md`, `01_主题.md` | Stable directory and chapter names; dates belong in revision notes, not each new filename |
| API / protocol / schema reference | `reference/protocols/tcp_commands.csv`, `reference/apis/device-api.md` | Stable searchable names; preserve native CSV/JSON/YAML formats |
| Roadmap | `roadmap/product-roadmap.md` | Update the same document; use a named period only when the scope is actually period-bound |
| Todo | `todo/<topic>.md` or `todo/backlog.md` | Update stable items; an existing dated todo keeps its original filename |
| Directory index | `README.md` | Navigation and scope, not a second copy of every document |

Use the user’s date when supplied; otherwise use the environment date for new dated records. Preserve existing naming conventions unless a rename is requested. Write titles in the project’s language; directory names above are defaults, not a reason to translate established paths.

## New Document vs Existing Document

Search for an existing same-topic document before creating one. Update an explicit target or a living architecture page, reference, chapter, roadmap, plan, or todo in place. Keep changes local unless the user asks for a broader rewrite.

Create a new file for a new topic, independently reproducible experiment, or superseding decision. A decision change gets a new ADR and a link from the old one; the current-state architecture overview changes when implementation or deployment is verified. Until then, label the accepted but unimplemented design as a target state. Do not silently rewrite historical results or present proposed architecture as deployed.

For a new incompatible interface version, document the versions side by side if both remain relevant. Avoid date-stamped copies of a reference page that leave readers guessing which one applies.

## Todo and Roadmap Maintenance

A roadmap describes outcomes; a plan describes execution; a todo holds the next concrete action. A long list of tasks does not become a roadmap merely because it has dates.

- Use stable item IDs when items will be linked, such as `T-014` or an existing issue ID.
- For todos, record type, status, source, content, and next action. Add priority, owner, deadline, or blocker only when known; mark unknowns explicitly rather than inventing assignments or commitments.
- Suggested statuses are `open`, `doing`, `blocked`, `done`, `dropped`, and `promoted`; respect an existing project vocabulary. A blocked item names the blocker and the condition that would unblock it.
- For risks, record impact, trigger or evidence, mitigation, and the next observation. A suspected risk stays a suspicion until evidence supports it.
- For roadmap milestones, record the outcome, acceptance evidence, dependencies, status, and any confirmed target window. Distinguish a target from a promise.
- Keep active items near the top. Preserve completed or dropped items with dates and reasons; do not delete their history as cleanup.
- On promotion, link the todo to its destination plan, roadmap, experiment, architecture decision, or knowhow page, and link back when useful. `promoted` means moved into another document, not implemented or verified.

## Writing Style

Use the shared [technical-writing guide](references/technical-writing.md) rather than a phrase blacklist. Explain objects, actions, conditions and outcomes directly; protect established terminology, exact commands, quantities and uncertainty. Keep reasoning in connected prose, execution in ordered steps, and lookup facts in tables as appropriate. Natural wording must not hide missing premises or replace evidence.

## Convert Writing Goals into Operations

When a request says “clear,” “rigorous,” or “beginner-friendly,” translate it into work before drafting:

| Requested quality | Operation | Observable check |
|---|---|---|
| Appropriate architecture depth | Pick the scope and level; inspect evidence at that boundary; show one representative flow. | A reader can identify responsibilities and interfaces without digging into lower-level functions. |
| A coherent book | Draw a chapter dependency list; give each chapter an incoming question and an output used by the next. | No required concept first appears after its use; chapter transitions say what remains unresolved. |
| Consistent math | Build one global symbol/abbreviation ledger; register notation before writing LaTeX; check each equation against it. | No symbol silently changes meaning, units, frame, index, or shape across chapters. |
| High-school accessibility | Start from a hand-computable example; teach each unfamiliar operation; show the rule for each algebraic transition. | The worked example can be reproduced without knowing the final answer or skipping a required advanced concept. |
| An argued conclusion | Pair a claim with its source, explain why the evidence supports it, and state the remaining competing explanation. | An observed association is not labeled causal; assumptions and missing measurements remain visible. |
| Reusable knowhow | Turn advice into checks with expected observations and next branches; distinguish symptom from confirmed cause. | A reader knows what to inspect, when to stop, and how to verify or undo an action. |
| Reproducible experiment | Define the comparison unit, filters, denominator, metric, and data/code version before computing summaries; mark retrospective choices in historical analysis. | Another reader can recover the numerator/denominator and distinguish paired samples from unmatched populations. |
| An actionable plan | Specify each step's precondition, operation, output, pass criterion, and failure response. | “Test it” is replaced by an actual test and an observable expected result. |

Use the detailed guide for the actual writing sequence. Do not paste this table into every deliverable.

## Post-write Review

After creating or updating a document (including HTML prose), re-read the whole file once as an editor. This is required for all document types, including small updates to an existing file.

Run these checks, correcting failures rather than merely saying the document is clear:

1. **Follow the reader path.** Re-read the opening and then each section in order. Move a definition or add a prerequisite bridge wherever a section needs an unexplained term. For lookup pages and todos, test finding a field or next action rather than imposing a narrative ending.
2. **Trace claims backwards.** For each consequential conclusion, locate its evidence, version, and assumptions. Mark unsupported portions as unknown or proposed, and separate historical results from current behavior.
3. **Check technical consistency.** Recalculate worked examples; compare symbols/units against the ledger; inspect signs, frames, domains, formula references, and approximations. For tables, recompute key counts or totals and verify common comparison units. Report checks not run.
4. **Walk an action forwards.** On procedural pages, follow a representative success and failure branch on paper. Add an expected observation, stop condition, or rollback where the reader would have to guess. Actually run commands only within the user's task authorization.
5. **Check the chosen depth.** Use the guide's stop criteria. Remove irrelevant lower-level detail by linking its canonical source; add missing boundaries or section outputs. Preserve relevant evidence rather than trimming to an arbitrary word count.
6. **Validate artifacts.** Resolve local links and images from the containing file; inspect native-format examples with an available parser; render math/figures in the project's existing preview/export path when available. If no renderer exists, inspect source and report that rendering was not verified.
7. **Review the diff.** Confirm status/versions and navigation changed together, historical evidence remains intact, and no unrequested move, deletion, publication, or application-code edit slipped in.

Re-read the corrected section with its preceding and following sections. Finish only when applicable checks pass or the remaining uncertainty is explicitly documented.

## Final Plain-Language Pass

Run this after the post-write content review, not while collecting facts or building the document structure. Read [references/post-write-polish.md](references/post-write-polish.md) for the local plain-language review. Use `shuorenhua` as an optional enhancement when available and useful; its absence does not skip the local review.

Skip this pass when the user says `不需要润色`, `不要润色`, `跳过润色`, `按原流程`, `保持原样`, or gives an equivalent instruction. In that case, finish with the existing Post-write Review above and do not invoke `shuorenhua`, install it, or apply a substitute style pass.

The two passes are internal. Deliver only the final document unless the user explicitly asks to compare the pre-polish and polished versions.

## Paths, Assets, and Moves

When the user requests a move, preserve content and evidence while updating the paths around it. If the user already moved the files, inspect the actual new location and repair references there; do not repeat the move:

1. Record the old-to-new directory mapping. Check for destination collisions before moving files.
2. Update links inside moved documents, links pointing to them, README indexes, image paths, and references in scripts, build defaults, export commands, and deployment configuration where applicable.
3. Check paths from each document’s directory, not only from the repository root. A rename can change both inbound and outbound relative paths.
4. Run available link/build checks and regenerate only the affected derived outputs. Check embedded images are real files rather than unresolved LFS pointers.
5. Keep one editable source. Put combined-book exports, rendered previews, caches, and large intermediate datasets in the project’s existing generated/ignored location, not beside the book as a second maintained manuscript.

Follow repository asset rules, including existing LFS policies. Keep small provenance manifests where useful; a hash identifies a file but does not back it up. Do not delete raw data or historical evidence just because it is not committed. Documentation maintenance alone does not authorize committing, pushing, deploying, installing tools, or publishing data.

## Document Templates

Use templates only after executing the relevant guide. [references/templates.md](references/templates.md) contains plan, experiment, and knowhow output shapes; [references/document-types.md](references/document-types.md) covers the other categories. Fill them from actual evidence and decisions, not from plausible boilerplate. Omit unused headings.

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

If a concrete command group or document-update pattern is needed, read [references/examples.md](references/examples.md). Do not load that reference for routine updates.

## Final Response After Writing

After creating or updating documentation, report only the useful facts:

- created or updated files
- category chosen
- key command or result if relevant
- any skipped or unresolved item

Keep the final response brief. Do not paste the entire document unless the user asks.
