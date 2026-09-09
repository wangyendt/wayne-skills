# Plan, Experiment, and Knowhow Output Templates

Execute the matching section of [record-workflows.md](record-workflows.md) first. These are output shapes, not the writing algorithm. Fill from actual sources, omit unused sections, and preserve the structure for small updates. Other types are in [document-types.md](document-types.md); paths follow [SKILL.md](../SKILL.md).

## Plan

```markdown
# <Change> Implementation Plan

## Background and scope
<Observed gap, intended result, constraints, exclusions, and evidence.>

## Approach and dependencies
<Selected approach, why it fits, unresolved decisions, and what must precede what.>

## Execution
| Step | Preconditions | Change / operation | Output | Verification and expected result | Failure response / rollback |
|---|---|---|---|---|---|
| <step> | <required state> | <specific action> | <inspectable artifact> | <actual check> | <stop / restore / branch> |

## Acceptance and rollout
<End-to-end check, rollout gate, backup/migration rules if applicable, and known risks.>

## Next action
<First currently executable step; unknown owners/dates remain unknown.>
```

## Experiment

```markdown
# <Question>: <dated experiment>

## Result and scope
<Answer supported by these runs, or “not run / evidence incomplete”; no invented outcome.>

## Question and comparison design
<Trigger, hypothesis, alternatives, changed variables, fixed variables.>

## Inputs and reproduction
<Data/source versions, software/config, exact filters, raw → analyzed count, commands, artifact paths.>

## Units of analysis and metrics
<Independent unit, repeated sessions, aggregation order, pairing keys, inclusion/exclusion rules.>
| Metric | Definition / numerator / denominator | Unit and preferred direction | Known limits |
|---|---|---|---|
| <metric> | <recomputable definition> | <unit/direction> | <when comparisons fail> |

## Results
| Group / scenario | Eligible units | Value | Comparison baseline | Variation / uncertainty | Evidence |
|---|---|---|---|---|---|
| <actual group> | <actual N> | <measured value> | <matched or unmatched> | <what was estimated, or not estimated> | <source> |

## Interpretation
<For each conclusion: observation → reasoning → allowed claim → competing explanation/limit.>

## Next discriminating check
<What new observation would resolve the remaining ambiguity; not another unbounded task list.>
```

Do not estimate repeated-run uncertainty from one run or hide failed runs in a success-only denominator. Preserve earlier conditions and results when adding a dated update; mark superseded interpretations without erasing evidence.

## Knowhow

Choose **explanation**, **diagnosis**, or **operation** before using this shape. A short conceptual note does not need a fake incident or rollback section.

```markdown
# <Situation or question>

## When to use this
<Symptom/question, applicable versions/conditions, and when this procedure does not apply.>

## What is known
<Observed facts, supported explanation, competing hypotheses, source links.>

## Reasoning or checks
<For explanations: premise → intermediate reasoning → conclusion → worked check.>
<For diagnosis/operation: fill branches below using inspected commands/files.>
| Check / action | Expected observation | If it matches | If it does not match | Stop / undo condition |
|---|---|---|---|---|
| <concrete read/action> | <observable value/state> | <next step> | <other branch> | <avoid damage or unsupported inference> |

## Verify and reuse
<Independent end-to-end check, expected result, applicability limits, and remaining uncertainty.>

## Related definitions and evidence
<Reference for exact fields, experiment for run-specific results; do not duplicate either.>
```
