# Technical Book Writer: Execution Guide

Shared reader/logic rules are in [technical-writing.md](technical-writing.md); diagram and interactive-delivery rules are in [interactive-illustrations.md](interactive-illustrations.md). Read the relevant shared guide for substantial work, then use the specialized workflow below.

Read this guide for every book task, including a new book, chapter additions, and revisions. For a formula-heavy knowhow, experiment, or other document, reuse the notation, derivation, and checking sections only; keep its original category and path. Ordinary records do not need a book scaffold.

Execute the steps below in order. For a small revision, inspect the existing outputs of earlier steps and change only what the revision affects. Do not regenerate the whole book merely to add one section.

## 1. Establish the Book Home

1. Resolve the user's target project and existing book directory before creating files. Default to `<docs-root>/books/<topic>/`; an explicit book directory is already the destination.
2. Inspect its README, chapters, notation, figures, evidence links, and export scripts. Reuse established conventions instead of creating a parallel book.
3. For a new book, create only the files needed for the requested scope:

```text
books/<topic>/
├── README.md              # reader, question, reading order, chapter links
├── 00_导读与符号.md        # canonical notation and abbreviations
├── 01_问题与基础模型.md
├── 02_...md
└── figures/               # actual figures used by chapters
```

4. Keep stable chapter filenames. Record substantive revisions inside the book rather than making dated copies of living chapters.
5. Treat the ordered chapters as the maintained manuscript. Combined Markdown/PDF is generated output in the project's existing build/ignored location, not a second editable source. Keep published outputs according to the requested workflow.
6. Link dated experiments and original sources; preserve their historical values and conclusions, marking superseded findings explicitly. A book explains the evidence rather than rewriting it.

**Checkpoint:** identify one reader entry, one notation authority, and the maintained chapter files before drafting. If two files claim to be the current manuscript, resolve their relationship first; do not discard either as cleanup.

## 2. Inventory Questions and Evidence

1. Read the user's requested outcomes and source material. Write the practical question in one sentence: what should the reader explain, calculate, or decide after reading?
2. Record the audience and starting knowledge. For `高中水平`, assume basic algebra, functions, trigonometry, and graphs; introduce unfamiliar matrix, calculus, and probability operations before they are needed.
3. Build a compact working source table: `claim/question | source location/version | theory/code/measurement | assumptions | missing evidence`. Cite a code function, paper section, or experiment record rather than just a repository or website homepage.
4. Distinguish existing findings from tasks not performed. Mark an unmeasured quantity unknown; a planned validation is not a result. Label invented numerical examples as teaching examples.
5. Identify source disagreements before combining them: units, coordinate frames, sample cohorts, algorithm versions, and measurement stages. Resolve from evidence or retain both with their scopes; do not average incompatible definitions.
6. Keep the working table in notes while drafting; publish the source links and unresolved limitations that readers need, not process paperwork for its own sake.

**Checkpoint:** every intended conclusion has a source, a derivation to perform, or an explicit open-question label.

## 3. Build the Chapter Dependency Map

1. List the concepts needed to answer the practical question. Connect `A → B` only when understanding B requires A. Start with observable quantities, then the forward model, derived quantities, uncertainty, interpretation, and evaluation where applicable.
2. Put prerequisites before their consumers. Break a dependency cycle by defining the minimum shared concept earlier; do not make two chapters repeatedly tell readers to read each other first.
3. Group concepts into chapters around one reader question or usable result. Split a chapter when it introduces a separate question with different prerequisites; merge sections that only repeat setup. Do not split by arbitrary word counts or by source-file boundaries.
4. Write a chapter contract before prose:

| Field | Write this concretely |
|---|---|
| Opening question | The problem this chapter will answer |
| Inputs | Earlier chapter/section links, known quantities, assumed reader skills |
| New concepts | Concepts and symbols introduced here, with planned first definitions |
| Argument | The sequence of subquestions or derivation steps |
| Output | A formula, procedure, interpretation, or test the reader can now use |
| Verification | The example, dimensional check, experiment, or counterexample that tests the output |
| Next dependency | Which later question uses this output and why |

5. Put a short reading map and chapter links in README. Put background, prerequisites, scope, conventions, and canonical notation in `00_导读与符号.md`; avoid duplicating a full preface in every chapter.
6. For branching reading paths, label prerequisites explicitly. An optional advanced chapter can be optional only if the main path does not secretly depend on it.

A teaching-only example of a completed chapter contract:

```text
Chapter: 02_输入变化与输出变化.md
Question: How does a small input change affect the inverse model's output?
Inputs: Chapter 01's inverse relation; fractions and function graphs.
New concept: Local slope, introduced through average slopes.
Argument: Two nearby inputs → output difference → average slope → limit.
Output: A local change formula, with its units and valid domain.
Verification: One numerical step, a smaller-step comparison, and a sign check.
Next dependency: The uncertainty chapter uses this slope after defining variance.
```

The titles and dependency are illustrative, not source-derived project facts. Write a similarly concrete contract for the actual chapter; keep it in drafting notes unless the reader benefits from seeing it.

**Checkpoint:** walk from the first chapter to the final answer using only declared inputs. Repair any concept introduced after its first use.

## 4. Maintain Canonical Notation

For a new book, the sole notation authority is `00_导读与符号.md`. If an existing book already has a dedicated notation file, retain it and link it from the guide; do not create another competing table.

1. Create two tables there: **mathematical symbols** and **abbreviations**. Add entries before using them in chapter prose, formulas, figures, or examples. In the same canonical file, explain notation operators needed by the audience, such as transpose, norm, expectation, and derivative notation; distinguish operators from measured quantities.
2. Use these symbol columns: `symbol | meaning | unit | scalar/vector/matrix shape | domain/constraints | coordinate frame | index/subscript convention | first-definition link | source/code aliases`. Put `not applicable` where a field genuinely does not apply, rather than leaving it ambiguous.
3. Use these abbreviation columns: `abbreviation | full name | plain-language meaning | first-definition link`. Expand the abbreviation on first use in the reading order. If none are used, say so briefly instead of inventing entries or leaving an empty table.
4. Reserve distinct symbols for distinct concepts. Use semantic subscripts where needed; define what subscripts such as `L`, `R`, `i`, `0`, or `*` mean. A reference value, estimated value, and measured value must remain distinguishable.
5. Specify vectors' orientation, matrix dimensions, frame axes, transform direction, handedness, and units before using them. For example, state what coordinates a transform accepts and returns, not merely that it is an “extrinsic matrix.”
6. Map source-specific names to canonical symbols. If a paper and code use different names for the same quantity, explain the equivalence and its conditions; do not silently alternate names between chapters.
7. At each formula, check every symbol against the table. Explain nearby the symbols needed to read that formula, especially new symbols, indices, frames, and changed conditions. Link the global table instead of pasting all of it repeatedly.
8. When renaming a symbol, search all chapters, equations, captions, tables, generated-figure labels, and source-to-code mappings. Update them together, check identifier collisions, and regenerate affected figures. Do not perform a blind text replacement inside code identifiers or quoted source notation.

**Checkpoint:** a reader can look up every symbol and abbreviation without guessing which chapter's definition applies. Local shorthand must map explicitly to the global definition.

## 5. Draft Each Chapter as an Explanation

Use this sequence as reasoning, not as mandatory generic headings:

1. **Real question:** describe the observed situation and the quantity or decision that is missing. Use verified project context, not invented anecdotes or dramatic claims.
2. **First attempt:** show the simplest plausible way to answer it. Work a small case, then state its specific limitation or failed assumption. If there is no meaningful competing attempt, introduce the missing concept directly.
3. **Needed concept:** explain what the new quantity or model adds and why the preceding approach needs it.
4. **Derivation:** follow the procedure below, making the assumptions and every consequential algebraic step visible.
5. **Check and interpretation:** test the result; explain what changes when an input changes, what the result means physically, and where it stops applying.
6. **Next question:** close with the answer promised at the start and the unresolved dependency that motivates the next chapter. Avoid a generic “laying a solid foundation” transition.

Draft one chapter through verification before repeating this cycle for the next. Reuse established symbols and results with links, not another full derivation. If a later chapter reveals a missing prerequisite, add the smallest necessary bridge earlier and re-check the dependent chapters.

## 6. Write LaTeX and Stable Equation References

1. Use the target renderer's supported LaTeX delimiters, normally `$...$` inline and `$$...$$` for displayed equations. Inspect existing rendering or a preview before choosing renderer-specific macros.
2. Give reusable equations stable semantic anchors, such as the `eq-inverse-rate-example` anchor used below. A same-file reference is `[inverse-rate example](#eq-inverse-rate-example)`; a cross-chapter reference prepends the actual relative chapter path. Check that the target file and anchor both exist. Do not refer only to “the formula above.”
3. Keep anchor names when moving an equation within a chapter. If the project uses equation numbers, update references through its supported cross-reference system; do not rely on auto-renumbering that was never configured.
4. Before each displayed equation, state what it computes and under which assumptions. After it, explain its important terms and result in ordinary language. Definitions may be shared across a contiguous derivation, but newly introduced symbols need explanation before use.
5. Distinguish exact equality, approximation, definition, and proportionality. State a linearization point and small-change assumption whenever replacing a nonlinear function with a local approximation.
6. Keep units out of ambiguous symbol names; put units in the notation table and numerical substitutions. Declare degrees versus radians before angular differentiation, and convert explicitly when outputs use a different unit.
7. Protect formulas during prose polishing. Recheck any edited sentence that defines a sign, domain, assumption, index, or reference frame.

## 7. Execute Each Derivation

For every result the reader is expected to use, perform these steps; omit a step only when it is genuinely inapplicable and the remaining argument still closes.

1. **Set up:** state the known inputs, requested output, assumptions, valid domain, and coordinate/measurement conventions. Look up or add all symbols in the canonical table.
2. **Start small:** draw or describe a scalar/2-D teaching case with values and units. Show what is observed and what must be calculated before introducing compressed general notation.
3. **Show the starting equation:** explain its origin: definition, geometrical relation, physical assumption, or previously derived result. Cite the relevant source where it is not established in the book.
4. **Transform one consequential step at a time:** substitute, distribute, form a common denominator, cancel, or take a limit, saying why the operation is valid. State nonzero divisors. Expand the step that a reader could not reproduce from the previous line; “整理可得” is not that explanation.
5. **Generalize after understanding:** write the component-wise form before vectors/matrices. Map each compact term back to the small example and check multiplication dimensions and frame directions.
6. **Check dimensions:** verify compatible units on additions and both sides of equalities. Derivatives have output-unit/input-unit; Jacobian entries may have different units by column.
7. **Check behavior:** evaluate a simple numerical case, a meaningful boundary/limiting case, and a sign or symmetry expectation. Use finite differences for a derivative/Jacobian, reporting the perturbation size and approximation error.
8. **Explain the result:** identify what the formula predicts, which input controls which behavior, and what it omits. Return to the opening question rather than stopping at the boxed equation.

For residual/Jacobian derivations, define the residual, variable ordering, parameterization, perturbation side, and held-fixed quantities first. For uncertainty propagation, introduce variance and covariance before matrix propagation, and distinguish measurement uncertainty from model mismatch and biased estimation.

## 8. Insert Prerequisite Bridges Where Needed

Place a bridge immediately before the first required use, not only in an appendix. Use a small example and verify that the next calculation can be completed using it.

| Required concept | Bridge to teach first | Reader check |
|---|---|---|
| Derivative | Average change over a small interval, then the limiting local slope | Compute a finite-difference slope and interpret its sign and units |
| Partial derivative | Change one input while explicitly holding the others fixed | Name what moves and what stays fixed |
| Jacobian | Arrange several output/input slopes in a table, then call that table a matrix | Explain one row, one column, and one entry's units |
| Matrix product | Compute a two-component example as weighted sums | Expand the compact product and verify dimensions |
| Rotation/frame transform | Plot two planar axes and transform one point | State input frame, output frame, and check a known orientation |
| Variance/covariance | Compute deviations of a few observations and their paired products | Explain spread versus correlated changes without a matrix first |
| Least squares | Compare candidate fits using squared residuals on a tiny dataset | Identify the minimized quantity and why residual direction matters |

Explain where each simplified example stops applying. An appendix may add advanced proofs, but sending the reader there or telling them to skip material does not replace a prerequisite required by the main argument.

## 9. Worked Teaching Example: An Inverse Relation

The following numbers are invented for teaching, not measured project results. It demonstrates the amount of explanation to write, not a compulsory topic for every book. In a book using it, register these entries in the canonical table before the example.

| Symbol | Meaning | Unit | Domain |
|---|---|---|---|
| $x$ | Input length | m | $x>0$ |
| $a$ | Fixed positive area parameter | m² | $a>0$ |
| $y$ | Output length, defined by $y=a/x$ | m | $y>0$ |
| $h$ | Small change in input length | m | $h\ne0$ and $x+h>0$ for the difference quotient |
| $s$ | Local slope of output versus input | m/m, dimensionless | Evaluated at the stated positive $x$ |

All five quantities are scalars; no coordinate frame or index applies. Their first definition is this example, and they have no source/code aliases. In a real book, enter those facts in the corresponding global-table columns rather than introducing a second notation authority here.

**Question.** If $a=12\,\mathrm{m}^2$ and $x=3\,\mathrm{m}$, then $y=4\,\mathrm{m}$. How much does $y$ change when $x$ increases a little? The relation $y=a/x$ is the assumed starting model; this example does not establish it as a physical law.

**First calculate an average slope.** After changing the input by $h$, the output is $a/(x+h)$. Output change divided by input change is

$$
\frac{a/(x+h)-a/x}{h}
=\frac{ax-a(x+h)}{h\,x(x+h)}
=\frac{-ah}{h\,x(x+h)}
=-\frac{a}{x(x+h)}.
$$

The first equality gives the two fractions a common denominator. The second expands $a(x+h)=ax+ah$ and cancels $ax$. The third cancels $h$, which is permitted because the average slope uses $h\ne0$. Positive $x$ and $x+h$ keep the other denominators nonzero.

**Make the interval very small.** A derivative is the value this average slope approaches as $h$ approaches zero. We take the limit of the simplified expression, rather than substitute zero into the original division by $h$:

<a id="eq-inverse-rate-example"></a>

$$
s=\frac{\mathrm{d}y}{\mathrm{d}x}
=\lim_{h\to0}\left[-\frac{a}{x(x+h)}\right]
=-\frac{a}{x^2}.
$$

Here $\mathrm{d}y/\mathrm{d}x$ means the local output/input slope, not a new independent quantity. At the stated inputs, $s=-12/3^2=-4/3$. Its unit is $\mathrm{m}^2/\mathrm{m}^2=1$: an input increase of one millimetre gives an output decrease of approximately $1.33$ millimetres near this point.

**Numerical check.** Choose $h=0.03\,\mathrm{m}$. The exact new output is $12/3.03\approx3.960396\,\mathrm{m}$, so its change is approximately $-0.039604\,\mathrm{m}$. The finite-difference slope is approximately $-1.320132$, compared with the derivative $-1.333333$. The local prediction uses $s h=-0.04\,\mathrm{m}$; its error magnitude is approximately $0.000396\,\mathrm{m}$. With the smaller step $h=0.003\,\mathrm{m}$, the average slope is approximately $-1.332001$, closer to the derivative, and the output prediction error is approximately $0.000003996\,\mathrm{m}$. These are approximation errors from finite steps, not observed measurement standard deviations.

**Meaning and limits.** The negative slope agrees with the original inverse relation: increasing positive $x$ decreases $y$. As $x$ grows, the slope's magnitude falls; as $x$ approaches zero from above, it grows without bound, so the same fixed step becomes a poor local approximation. For a meaningful check near zero, keep $|h|$ (the size of the input change, ignoring its sign) small relative to $x$ and remain inside the domain. The next question could be how uncertainty in $x$ changes uncertainty in $y$; that requires defining uncertainty before applying this slope to it.

## 10. Connect Theory, Code, and Evidence

1. State each major claim and its reasoning chain: **claim → premises → derivation or comparison → evidence → supported conclusion → limitation**. A plot without the inference connecting it to the claim is incomplete.
2. For empirical claims, identify data source, sample unit, selection/exclusion, sample count, metric definition/units, comparison baseline, and uncertainty where available. Link the full experiment for details instead of copying its whole log into the chapter.
3. Keep exact mathematical consequences separate from assumptions, approximations, code behavior, measured observations, and hypotheses. A good fit does not prove a mechanism; observational group differences do not by themselves establish causation.
4. Explain possible confounders and alternatives when they affect the conclusion: cohort changes, station offsets, shared calibration, selection, parameter range, or measurement errors. If a claim needs a controlled test that has not run, state that gap.
5. Present the abstract model first, then a mapping table: `canonical quantity/formula | code name and function/path | units/convention | implementation difference`. Cite the inspected version. Label intended behavior separately from verified implementation.
6. Use statistics to test or bound a model, not to replace its explanation. Separate sample variability, measurement uncertainty, estimator uncertainty, and model mismatch; do not label all scatter “noise.”

**Checkpoint:** trace each conclusion backward to its premises and evidence. Weaken or mark claims whose supporting chain is incomplete; never manufacture observations to finish a narrative.

## 11. Choose and Validate Teaching Figures

1. Write the question a figure must answer before drawing it. Choose a diagram for geometry/frames, an input–output curve for response, a derivative curve for sensitivity, a residual plot for mismatch, or a distribution for sample spread.
2. Define axes, units, parameter values, fixed versus varied quantities, coordinate frames, and ranges in the caption or adjoining text. Mark teaching/simulation data separately from measurements.
3. Keep comparable panels on compatible scales, or state the changed scale visibly. For 3-D geometry show axes, viewpoint, scale/aspect, and reference objects; add a 2-D projection when perspective hides the relevant deviation.
4. Tie at least one plotted value to a worked numerical substitution in the text. Check that signs, units, domains, labels, and limiting behavior agree with the formula and global notation.
5. Save editable diagram sources or figure-generation code when practical; follow repository conventions for rendered assets and large data. Link figures from the chapter and record the regeneration command when it is needed to maintain them.
6. Preview actual rendering: equations render, symbols survive font/export changes, captions are legible, and images are not unresolved LFS pointers. If a renderer is unavailable, report which rendering check remains unperformed.

## 12. Review, Repair, and Maintain

Review one finished chapter, then the reading order across chapters. Use failures to choose a concrete repair, not merely to add another disclaimer.

For the beginner-reading check, temporarily ignore your own background knowledge. At each derivation, list the operations needed to reproduce it and locate where each was taught or declared as a prerequisite. Rework the numerical example from the preceding lines, not from the final answer. If an independent reviewer is available, ask them to flag the first unexplained operation and to reconstruct one derivation using only the book's declared prerequisites. Repair the flagged step and repeat. This checks teaching gaps; an AI review alone does not establish that real high-school readers understood the book.

| Failure found | Repair before delivery |
|---|---|
| A chapter uses an undeclared input or advanced concept | Add the missing prerequisite/bridge before use; update the dependency map |
| A symbol, abbreviation, unit, or frame is missing/ambiguous | Update the canonical table, nearby explanation, and every affected occurrence |
| A derivation jumps from setup to final expression | Expand the exact skipped substitution/algebra/limit; add a small worked calculation |
| A formula fails dimensions, signs, boundaries, or numerical checks | Revisit assumptions and algebra; correct the formula and downstream figures/results |
| A chapter is a chronological source dump | Regroup around its opening question; link dated evidence instead of erasing it |
| A conclusion exceeds data or relies on unexplained correlation | Narrow the claim, expose alternative explanations, and identify the missing test |
| The same result is independently maintained twice | Choose the established canonical home; replace duplicate exposition with scoped links |
| A chapter ends without its promised answer | Add the actual result, validity limits, and the next dependency, not a generic summary |
| A moved chapter or renamed symbol leaves stale consumers | Fix incoming/outgoing links, captions, producer scripts, and export configuration; rerun affected checks |

For a new chapter, first update its contract and prerequisites, then reserve notation, derive and verify, add figures, and update README and cross-links. Preserve stable anchors and established chapter filenames where possible; avoid renumbering all chapters for one addition unless the ordering convention requires it.

When reorganizing a book, inspect the user's actual new location before moving anything. Record old-to-new paths and check collisions. Repair chapter/image links, repository backlinks, build inputs, export commands, and producer output paths so regeneration does not recreate the old directory. Keep raw data and historical evidence; a hash manifest identifies a file but is not its backup.

Finish with technical checks before the configured plain-language pass. Protect equations, notation, assumptions, units, source names, code identifiers, and evidence strength during polishing. Re-read transitions after edits so no symbol appears before its definition. Report the delivered files and any unresolved source/rendering checks; do not imply a commit, installation, or publication occurred unless requested and performed.
