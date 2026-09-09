# Placement and Output Shapes

Use this reference after choosing a document type. It shows where the output goes and how to arrange it; the linked execution guides explain how to collect evidence and write it. Examples are illustrative, not facts about the current project.

## Before Creating a File

1. Resolve the user's target and existing canonical file using [SKILL.md](../SKILL.md).
2. Classify by the reader's question in the table below.
3. Load the linked workflow, choose its scope/depth, and collect the required inputs.
4. Reuse an existing page or choose the smallest useful outline below. Create only needed directories.
5. Check links relative to the containing file and preserve the native format of authoritative data.

| Type | Default path | Execution guide |
|---|---|---|
| Architecture | `docs/architecture/system-overview.md`, `<subsystem>.md` | [Architecture writer](architecture-writer.md) |
| Decision record | `docs/architecture/adr/YYYYMMDD_<decision>.md` | [Architecture writer](architecture-writer.md); preserve existing numbered ADR convention |
| Book | `docs/books/<topic>/README.md` and numbered chapters | [Technical book writer](technical-book-writer.md) |
| Reference | `docs/reference/<kind>/<topic>.md` or native CSV/JSON/YAML | [Record workflows](record-workflows.md) — Reference |
| Plan | `docs/plan/YYYYMMDD_<change>.md` | [Record workflows](record-workflows.md) — Plan |
| Roadmap | `docs/roadmap/<topic>.md` | [Record workflows](record-workflows.md) — Roadmap |
| Todo | `docs/todo/<topic>.md` | [Record workflows](record-workflows.md) — Todo |
| Experiment | `docs/experiment/YYYYMMDD_<question>.md` | [Record workflows](record-workflows.md) — Experiment |
| Knowhow | `docs/knowhow/YYYYMMDD_<topic>.md` or existing canonical guide | [Record workflows](record-workflows.md) — Knowhow |

Stable living pages do not need a new date-prefixed copy for each revision. Preserve an existing dated todo or guide filename. A new experimental run is historical evidence; do not rewrite it as if it had used today's method.

## Architecture Shape

First select a granularity with [architecture-writer.md](architecture-writer.md). This skeleton is not a reason to include every level in one page.

```markdown
# <System or subsystem>: <reader's question>

Scope/depth: <selected boundary and level>; excluded: <deeper detail>.
State: <verified current / proposed / historical>; sources: <actual files and version>.

## Boundary and responsibilities
<Table or diagram at the selected level, with named inputs, outputs, and state owners.>

## A representative flow
<One path through the boundary; arrows explain the actual interaction.>

## Constraints and failure boundaries
<What evidence establishes each constraint; what is still unknown.>

## Related views and decisions
<Parent/deeper view, exact interface reference, ADR, or implementation plan as needed.>
```

Deployment and runtime sequence are separate views of the same selected scope. Do not equate a source directory with a process or machine. Accepted decisions stay target-state descriptions until implementation is verified.

## Book Shape

```text
docs/books/<topic>/
├── README.md                 # one entry and chapter dependency/reading map
├── 00_导读与符号.md            # canonical symbols, abbreviations, conventions
├── 01_<first-question>.md
├── 02_<dependent-question>.md
└── figures/                  # only when figures exist
```

Use the existing global notation file if present; do not add another canonical table. The writing workflow creates the chapter map and ledger before formulas. Each chapter follows its own question through background, simple model, derivation/evidence, worked check, limits, and a handoff to the next question. LaTeX examples and the per-formula explanation procedure are in [technical-book-writer.md](technical-book-writer.md).

A one-chapter request updates that chapter and affected notation/navigation; it does not create empty future chapters. Keep dated experimental evidence at its canonical location and link it. Generate combined Markdown/PDF outside the maintained manuscript.

## Reference Shape

Choose `apis/`, `protocols/`, `schemas/`, or `configuration/` only as needed. Start from code, schema, or a versioned contract, not a plausible list of fields.

```markdown
# <Interface / protocol / schema / configuration>

Applicable version and source: <actual evidence>; unverified fields: <explicit gaps>.

## Definitions
| Name | Meaning | Type / unit | Valid values | Default / missing behavior | Evidence |
|---|---|---|---|---|---|
| <exact identifier> | <source-backed meaning> | <actual definition> | <actual constraint> | <known value or unknown> | <source> |

## Examples and failure behavior
<Minimal valid example and relevant invalid example; distinguish specified, inspected, and executed behavior.>

## Compatibility
<Only real supported differences, precedence, or deprecation information.>
```

Add kind-specific fields through the workflow: protocol byte order/checksum scope, API side effects, schema missing-value meanings, configuration precedence/reload behavior. Keep machine-readable definitions native and link them rather than copying an entire maintained schema.

## Roadmap Shape

Group source actions into outcomes before creating this table. A stage name such as “testing” is incomplete until the reader can observe its result.

```markdown
# <Topic> Roadmap

Current gap and target outcome: <evidence or confirmed user direction>.
Scope exclusions: <what this roadmap does not promise>.

| Milestone | Observable outcome | Acceptance evidence | Dependency | Status |
|---|---|---|---|---|
| <stable name / ID> | <result, not task list> | <test/report/decision> | <what must exist first> | <actual status> |

## Decisions that could change the order
<Unresolved dependencies/risks, linked investigation or plan, and reason for any changed direction.>
```

Use a named quarter or owner only if supplied or verified. Details of file changes, commands, and rollback belong in a linked plan. Completion needs evidence, not an elapsed date.

## Todo Shape

For one small item, use the existing checklist style:

```markdown
- [ ] 核对导出 CSV 的单位；先对照表头和字段定义。来源：本次用户要求。
```

For tracked items, reuse the project's IDs/statuses and only add useful columns:

```markdown
| ID | Status | Item | Source | Next action / unblock condition |
|---|---|---|---|---|
| <existing or new stable ID> | <open/doing/blocked> | <one action/question/risk> | <actual source> | <inspectable next step> |
```

Preserve completed/dropped history and reasons. `promoted` needs a destination link and means another document takes over the work, not that implementation is complete. Do not create a roadmap or plan for every single todo.

## Split Purposes Without Duplicating Content

| Material | Route |
|---|---|
| Current module boundaries plus a proposed split | Current architecture plus linked target view/plan; keep their state labels distinct. |
| Why a transport was selected and how to migrate | ADR for rationale; plan for execution; reference for the exact protocol. |
| Serial field definitions and packet-loss diagnosis | Reference for fields; knowhow for evidence-driven diagnosis branches. |
| Several experiments turned into a tutorial | Book for the dependency-ordered explanation; link dated experiments as evidence. |
| Tasks spanning a confirmed quarter | Roadmap for outcomes; todo for next actions; do not infer an unprovided deadline. |
| A todo becomes a next-version goal | Link the promoted item to its roadmap/plan without labeling it done. |
| A field dictionary for a program | Native CSV/JSON reference, with only the explanatory prose needed to use it. |
