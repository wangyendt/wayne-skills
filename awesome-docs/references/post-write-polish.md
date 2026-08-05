# Post-write Plain-Language Pass

Use this pass after `awesome-docs` has finished the document and completed its normal content review. The content pass decides what is true, complete, and actionable. This pass only improves how that settled content reads.

## Activation

Enable the pass by default for Markdown documents.

Skip it when the user says `不需要润色`, `不要润色`, `跳过润色`, `按原流程`, `保持原样`, or gives an equivalent instruction. Skipping means returning to the original `awesome-docs` workflow: generate or update the document, run the Post-write Review in `SKILL.md`, and deliver it. Do not invoke `shuorenhua`, attempt installation, or perform an imitation style pass.

Never send command lines in `常用命令.txt` through prose rewriting. A short Chinese group description may receive a local `minimal + in-place` cleanup, but every command remains byte-for-byte unchanged.

## Workflow

1. Finish the document structure, facts, evidence, conclusions, and next actions.
2. Record protected spans: names and responsibility, dates, numbers and their objects, status and risk strength, metric direction and units, citations, URLs, image paths, commands, code, file paths, logs, table cells, formulas, symbols, coordinate frames, and assumptions.
3. Invoke `$shuorenhua:shuorenhua` on the completed prose using the routing table below.
4. Compare the polished version with the protected spans. Restore any changed fact, relationship, condition, uncertainty, command, formula, link, or asset path.
5. Run the `shuorenhua` fidelity reread first and its residual-style audit second.
6. Deliver one final document. Keep the pre-polish draft only when the user asks for a comparison.

When `bounded` returns a deletion list, do not remove those sentences without user confirmation. Keep unconfirmed sentences in the document and do not append internal editor notes to the delivered Markdown.

If `shuorenhua` is unavailable and installing skills is authorized, follow the current instructions in the official [`shuorenhua` repository](https://github.com/MrGeDiao/shuorenhua). Do not hard-code package-manager commands that may become stale. If installation is unavailable or not authorized, say so once and perform only the existing `awesome-docs` Post-write Review; do not pretend that the dedicated polish ran.

## Routing By Document Type

Treat project documentation as `docs` unless the table names a mixed scene. Never use `aggressive` by default.

| Document | Prose pass | Protected region |
| --- | --- | --- |
| Technical book, thesis chapter, long tutorial | Teaching prose: `standard + bounded`. Use `structural` only when the user asked to reorganize the chapter. | Formulas, derivations, symbol definitions, frames, units, code mappings, citations: `minimal + in-place`. |
| Experiment report or benchmark | Background and interpretation: `standard + bounded` only when template voice is visible. | Setup, commands, commits, metrics, tables, results, limitations: `minimal + in-place`. |
| Know-how | New explanatory prose may use `standard + structural`; a small update to an existing file uses `minimal + in-place`. | Symptoms, causes, procedures, expected outputs, rollback conditions, commands, and paths remain fixed. |
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
