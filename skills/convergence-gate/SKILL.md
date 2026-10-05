---
name: convergence-gate
description: The pre-invocation routing pipeline for the Therantai skill ecosystem. Fires the moment raw input arrives (a fragment dump, a hand-drafted framework, a voice-transcribed thought-structure, a pasted document) and the practitioner does not yet know which skill(s) apply. Reads the input, surfaces every plausible candidate skill, names where two or more genuinely overlap, ranks which candidate is load-bearing versus supportive with structural reasoning, and emits exactly one next invocation plus what is queued behind it. Does not perform the downstream skill's work itself — it only decides which door to open next. Invoke with /gate, "which skill should I use", "route this", "I have a bunch of skills and don't know which one", "what's the next step here", or any moment of standing in front of the full ecosystem with an input and no clear entry point.
triggers:
  - "/gate"
  - "which skill should I use"
  - "route this input"
  - "what's my next step"
  - "I don't know which skill applies"
  - "I have fragments, what do I invoke"
scope: ecosystem-wide, pre-invocation only — fires before any other skill, never after one is already running
version: 1.1
date: 2026-07-11
author: Venkatesh
---

# Convergence Gate

A pipeline, not a taxonomy — order is load-bearing (overlap resolution can't run before candidates are surfaced; ranking can't run before overlaps are named). Decides only which door opens next; never does the downstream skill's own work.

## Stage 0 — Domain classification (before any candidate surfaces)
Coarser prior cut: does the input contain a build target — a North Star, an intended artifact, an engine/tool/document it wants to become?
- **YES → BUILD DOMAIN.** Route only among build-family skills (forge-pipeline, idea-to-engine, spine-pipeline, spinal-column, ossify, core-extractor, render-doc). Intake/fuse-delta/placement-protocol don't fire — nothing is merging into the registry. Skip to Stage 4-equivalent ranking among build candidates only.
- **NO, describes a reusable cognitive OPERATION** (lens, merge rule, routing law, constraint map) meant to sit alongside other skills and fire repeatedly → **REGISTRY DOMAIN.** Intake/fuse-delta/placement-protocol in play. Proceed to Stage 1.
- **Ambiguous/genuinely both** — name the split explicitly, decompose into build-shaped and registry-shaped parts, route each through its own Stage 0 verdict separately. Never let one half's classification leak into the other's.

Density and foreign/external origin are *not* registry-domain signals on their own — a completed spine or dense project-instructions block with a stated purpose is presumptively build domain even arriving as one finished document. The registry signal specifically: *this wants to become a permanent, repeatable tool*, not *a thing I use once, built and rendered*.

## Stage 1 — Intake read
No judgment, no matching yet. Just: what shape is this — bare theme, loaded fragments, completed structure, wounded/failing build, raw material?

## Stage 2 — Candidate surfacing
Cast wide against the registry. Short list (2-4 typical), each with a one-line reason it's plausible. Don't prune yet — a candidate that loses the ranking still belongs on the list; early pruning hides real overlap.

## Stage 3 — Overlap resolution
Where 2+ candidates are plausible, name the overlap explicitly — state what each would do differently with the same input. Skipping this is the most common silent misroute (an identity-testing skill run against a procedure-heavy artifact because "identity spine" vs "operational spine" overlap was never surfaced). If only one candidate survives Stage 2, say so and skip to Stage 5.

## Stage 4 — Dominance ranking
Among overlapping candidates, name which is load-bearing vs. supportive/premature — argue structural superiority (why this one's output is what the others depend on), referencing the shape from Stage 1, not just apparent relevance.

## Stage 5 — Next-step emission
Emit exactly one recommended invocation, plus what's queued behind it if relevant ("assay first, then compress if it holds"). Never a bare menu with no ranked default — fork and recommendation arrive together; bare assent means proceed with what was named.

## Anti-patterns
Skipping Stage 0 and routing a build-domain input to registry-domain skills just because it's dense/externally-voiced. Skipping Stage 3 and jumping straight to a pick. Treating this as unordered taxonomy. Doing the downstream analysis inside the gate. Presenting a bare candidate menu with no default.

## Relations
Distinct from taxonomy-router (single trigger-phrase lookup against a fixed library) and oracle-core's router (task-depth classification for the Oracle Suite specifically). This gate is ecosystem-wide and pipeline-shaped — for the moment before any tool is chosen, when the friction is overlap between plausible skills, not depth-classifying one task.
