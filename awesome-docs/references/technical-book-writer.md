# Technical Book Writer Reference

Load this reference only when the user asks for book-like technical documentation, thesis-style chapters, long-form derivations, formula/Jacobian explanations, or a coherent chapter distilled from scattered notes. Do not load it for ordinary experiment, todo, plan, roadmap, command, or short know-how updates.

## Purpose

Write rigorous technical material that teaches a reader the concept in dependency order. The output should read like a chapter, not a chronological experiment log, a patch note, or a loose answer dump.

## Core Workflow

1. Identify the reader path: what the reader already knows, what problem motivates the chapter, and what conceptual steps must be learned in order.
2. Define a chapter spine before drafting: each section should have a local question, required prerequisites, introduced symbols, and a clear output.
3. Maintain a symbol ledger for frames, transforms, residuals, Jacobians, timestamps, noise terms, and units. Do not use a symbol before defining it.
4. Derive before presenting final formulas. Show why a term appears, what frame it lives in, and which convention fixes its sign or multiplication order.
5. Separate theory, implementation, and experimental evidence. Code details should explain how the theory is realized, not replace the theory.
6. Reconnect every section to the previous and next section after edits so the final chapter reads as one argument.

## Chapter Shape

Prefer this structure unless the user asks for a different one:

- Background and motivating problem.
- Reader prerequisites and notation.
- Conceptual model or system setup.
- Mathematical derivation in dependency order.
- Implementation mapping: data structures, functions, files, and where conventions enter code.
- Practical interpretation: failure modes, diagnostics, limitations, and what the formulas mean in real runs.
- Summary of conclusions and remaining questions.

## Formula And Frame Discipline

- Define each coordinate frame and transform direction explicitly.
- State whether rotations map world-to-body, body-to-world, camera-to-IMU, or IMU-to-camera.
- For residuals and Jacobians, specify the residual definition first, then perturbation side, parameterization, and units.
- Track timestamps, time offsets, interpolation assumptions, and exposure/rolling-shutter assumptions when relevant.
- If a sign, inverse, or multiplication order comes from code, cite the function or file and explain the convention.

## Source-Code Bridge

When deriving from code, first explain the abstract model, then map it to implementation names. Use file paths and function names as evidence, but avoid turning the chapter into a line-by-line code tour.

For calibration, VIO, robotics, or optimization topics, include the meaning of each optimized state, residual, covariance/noise model, and observability limitation when it affects the conclusion.

## Review Checklist

Before finishing, re-read the chapter and check:

- the opening states why the chapter exists and what the reader will understand by the end
- every section has a clear input, output, and reason to be in this order
- all symbols, frames, units, and conventions are defined before use
- derivations explain assumptions and intermediate steps instead of jumping to formulas
- theory, implementation, and experimental evidence are clearly separated
- implementation references support the explanation without becoming the structure
- final conclusions answer the motivating problem and name remaining limitations
