# Interactive Illustrations: Show the Relationship Being Explained

Read when a document or teaching script needs diagrams, formulas, animations or an interactive HTML delivery. Content organization follows [technical-writing.md](technical-writing.md). Do not generate a website or video merely because a document contains a formula.

## Choose a View for the Question

| What is hard to understand? | Prefer | Show explicitly |
|---|---|---|
| Spatial position, orientation, rays or planes | Rotatable 3D, with a useful default camera | Original frame, object locations, relevant axes and reference planes |
| Projection or coordinate conversion | Linked 3D and 2D views | Same selected point, direction, sign and numerical value in both |
| Sequence, runtime cooperation, state ownership | 2D flow, sequence diagram or state table | Actor boundaries, meaningful arrows, conditions and result owner |
| Change over time or a staged calculation | Stepped animation, with replay / pause / direct step selection | Current input, operation, output and which quantities stay fixed |
| Comparison, distributions or lookup | Plot or table | Units, denominator, aggregation and shared comparison scale |

Do not make a software dependency graph 3D for decoration. For true spatial problems, prefer interactive 3D over a perspective picture that hides the relationship. Explain non-uniform drawing scales; the screen's projected angle must not be presented as a measured spatial angle.

## Define the Picture Before Drawing

For each figure, record its reader question, known inputs, example vs measured data, object/frame identities, current focus and invariant quantities. Keep one source of truth for numbers; derive labels and geometry from it, rounding only for display.

For metrics, show the path when applicable: source data → coordinate representation → selected sample set → per-sample calculation → aggregation → interpretation. Add threshold/compensation/retest only when the subject actually has them. Define absolute value, mean, maximum, standard deviation or quantile before combining them; show the computation order when it changes the answer.

## Preserve Context, Control Emphasis

- Give the origin, positive axes, reference object, relevant units and observer viewpoint. The viewer's rendering camera is distinct from a camera/object inside the lesson.
- Label physical objects, calibrated/virtual models, and auxiliary constructions separately. An auxiliary frame translated to a centroid keeps the original axis directions unless a rotation is explicitly part of the calculation.
- Background objects should normally remain faintly visible if omitting them changes the apparent system. Omit their irrelevant rays/axes/edges to reduce clutter; do not delete a participating component just because it is not the current reference.
- Highlight the selected point, its source/target, connecting ray, foot of projection, angle arc, normal or residual as the explanation reaches them. Dim other measurements. Keep a clear legend; color is reinforced by labels or line style.
- Define angle zero, sign and unit, the plane being projected onto, and vector degeneracies. A total angle may need an azimuth or another constraint to determine component angles; projection angles are not automatically Euler angles.
- Give architecture boxes one abstraction depth per view. Separate host/process containment, internal component calls, file state and external services. Keep external participants visible without inventing their internals.

## Render All Math Consistently

Use LaTeX for formulas, substitutions, fractions, hats, subscripts, vectors, matrices and units wherever they appear, including SVG/canvas labels and animated values. Use a real math renderer; ordinary text approximations such as `nXZ` are not equivalent mathematical typography.

A build-time SVG representation is suitable for standalone HTML; dynamic values may compose math-rendered glyphs with tested spacing/baselines. A runtime renderer is also valid when its dependencies and performance fit the delivery. Do not assume a CDN is available for an offline artifact. Keep Chinese explanatory labels separate and readable. Preserve text alternatives for math and diagram meaning.

Check long formulas, negative values, exponents, rotation/zoom, unit spacing, baseline alignment and label collisions in the final rendered view. If the requested medium lacks a renderer, preserve correct LaTeX source and disclose the rendering limit; do not claim the result was visually verified.

## Interaction Is Part of the Explanation

- View rotation/zoom must not change measurements or selected features. Parameter controls may change model values, with a clear distinction in labels.
- Use steps to expose a causal sequence, not to imply timing guarantees or real hardware actions. Label simulated progress; distinguish predicted changes from new measurements.
- Provide useful defaults, reset, pause and keyboard-operable controls. Do not autoplay merely to decorate the page; respect reduced motion. Keep a static readable explanation for print and disabled scripting where feasible.
- For 3D/2D pairs, share selected IDs, values, colors and conventions. For flows, highlight both the actors and the relevant exchange; keep the remaining topology visible.
- Never let an animation suggest successful measurement, archive completion or a retry that the underlying source does not establish.

## HTML Delivery Checks

1. Navigation: direct anchors, link clicks, manual scroll, back/forward and resize select the current chapter deterministically. Layout changes during animation must not leave a previous chapter selected.
2. Figures: labels remain legible, important objects are visible at the default view, and the chosen point/line/plane stays highlighted during interaction.
3. Numerical invariants: test unit conversion, sign, aggregation order, rounding, limiting cases and view-independent values as relevant.
4. Accessibility/layout: keyboard focus, control labels, narrow screens, zoom, print and reduced motion. Report which checks actually ran.
5. Reproduction: keep editable sources and build/check instructions; avoid machine-specific paths in generated assets. Offline HTML must not require a development server, remote font or remote library to read its essential content.
6. Delivery truthfulness: a successful HTML preview is not proof a video was rendered. When a video is requested and `technical-explainer-video` is available, it can optionally guide encoding, audio and subtitle checks. Do not require or install it for document delivery; report only the artifacts and checks actually completed.

Use the existing project renderer where practical; do not impose a particular framework. Keep business examples, raw data, generated media and production code in the user's project, not in this skill.
