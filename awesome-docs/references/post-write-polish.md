# Post-write Plain-Language Pass

Use this pass after `awesome-docs` has finished the document and completed its normal content review. The content pass decides what is true, complete, and actionable. This pass only improves how that settled content reads.

## Activation

Enable the pass by default for document prose, including Markdown and visible HTML text. For HTML, edit only prose text nodes; preserve tags, IDs, classes, attributes, embedded scripts/styles, math markup, control labels that code depends on, and asset paths.

Skip it when the user says `不需要润色`, `不要润色`, `跳过润色`, `按原流程`, `保持原样`, or gives an equivalent instruction. Skipping means returning to the original `awesome-docs` workflow: generate or update the document, run the Post-write Review in `SKILL.md`, and deliver it. Do not invoke `shuorenhua`, attempt installation, or perform an imitation style pass.

Never send command lines in `常用命令.txt` through prose rewriting. A short Chinese group description may receive a local `minimal + in-place` cleanup, but every command remains byte-for-byte unchanged.

## Workflow

1. Finish structure, facts, evidence, conclusions and next actions before language editing.
2. Protect names and responsibility, quantities, conditions, uncertainty, commands, code, paths, formulas, coordinate frames, citations and machine-readable fields. Preserve HTML structure and behavior as above.
3. Perform a local plain-language pass: state actors and actions directly; remove empty previews, redundant wording and literal-translation phrasing only where meaning is preserved. Keep necessary transitions and established terms. Do not mechanically ban sentence patterns or invent missing reasoning.
4. If `shuorenhua` is available in the current environment and a dedicated polish would help, read its actual skill path and use the document-type scope below. Skip this optional enhancement when absent; do not search other agents' directories or start an installation/update prompt or workflow.
5. Compare edits with the protected facts and surrounding paragraphs. Restore changed conditions, responsibility, quantities or uncertainty; check residual awkwardness without forcing further edits. Follow `shuorenhua`'s fidelity review too when it was actually used.
6. Deliver one final document. Keep the pre-polish draft only when the user requests a comparison. Mention an unavailable named skill only when the user explicitly requested it; ordinary optional skips need no installation notice.

When `bounded` produces a deletion list, keep unconfirmed sentences; do not append internal editor notes to the delivered document. Do not claim that a dedicated skill ran when only the local review was performed.

## Routing By Document Type

Use this table to preserve editing scope in the local pass and, when available, to choose `shuorenhua` settings. External scene packs are optional and read only when that skill is available.

For local review, `minimal + in-place` means sentence-level edits without changing structure; `bounded` preserves sentences and paragraph order; `structural` permits reorganization only within the authorized scope. These scopes need no external skill. Treat project documentation as `docs` when selecting optional `shuorenhua` settings; never use `aggressive` by default.

| Document | Prose pass | Protected region |
| --- | --- | --- |
| Technical book, thesis chapter, long tutorial | Teaching prose: `standard + bounded`. Use `structural` only when the user asked to reorganize the chapter. | Formulas, derivations, symbol definitions, frames, units, code mappings, citations: `minimal + in-place`. |
| Experiment report or benchmark | Background and interpretation: `standard + bounded` only when template voice is visible. | Setup, commands, commits, metrics, tables, results, limitations: `minimal + in-place`. |
| Know-how | New explanatory prose may use `standard + structural`; a small update to an existing file uses `minimal + in-place`. | Symptoms, causes, procedures, expected outputs, rollback conditions, commands, and paths remain fixed. |
| Architecture overview or ADR | Current-system explanation: `docs + minimal + in-place`; use broader scope only when reorganization is requested. | Component boundaries, deployment state, data flow, decision status, dates, trade-offs, constraints, supersession links, and diagram/source paths remain fixed. |
| API / protocol / schema / configuration reference | Usually `minimal + in-place`; follow the API-reference Scene Pack where relevant. | Exact identifiers, bytes, types, units, ranges, defaults, required/optional status, versions, examples, error codes, and unknown-value markers remain fixed. Do not prose-rewrite CSV/JSON/YAML source data. |
| Plan or roadmap | Choose `docs` or `status` from the primary use, then use `standard + bounded` for long prose and `minimal + in-place` for small updates. | Scope, owners, dates, dependencies, milestones, risks, decisions, and completion criteria remain fixed. |
| README or public-facing project guide | Introductory and explanatory prose: `standard`; follow the `shuorenhua` README Scene Pack. | Installation commands, API names, compatibility claims, examples, links, and paths use `minimal + in-place`. |
| Todo | Usually skip the separate full-document pass. Remove only obvious Tier 1 filler around an item. | Status, priority, source, owner, trigger, risk, and next action remain fixed. |
| `常用命令.txt` | No prose pass on commands. | Preserve every command exactly, including quoting, spacing, redirection, variables, and line count. |
| Other technical Markdown | Default to `docs + minimal + in-place`; raise a clearly narrative section to `standard` only when needed. | Preserve all searchable terms, procedures, conditions, examples, and evidence. |

## Technical Book Boundary

Polish teaching prose and technical notation separately. A smoother paragraph must not change derivation order or hide an assumption. After the pass, recheck the symbol ledger and confirm:

- every symbol is defined before use;
- transform directions, perturbation sides, signs, multiplication order, timestamps, and units are unchanged;
- equations and code identifiers are exact;
- prose still distinguishes theory, implementation, and experimental evidence;
- limitations and uncertainty have not been softened.

## Existing Documents

When updating an existing document, polish only the changed region plus the minimum surrounding context needed for a natural transition. Do not use this pass as permission to rewrite unrelated sections. Preserve the existing structure unless the user explicitly requests a cleanup or full rewrite.
