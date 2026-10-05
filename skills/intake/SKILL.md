---
name: intake
description: >
  The threshold gate that fires the moment any external skill, contract, or constraint
  arrives from another builder — before fuse-delta opens, before any merge begins. Not a
  replacement for fuse-delta; its feeder. Resolves three questions in order — material type,
  staffed-or-absent territory, and decomposition of multi-function inputs — and from those
  answers determines HOW the incoming material is processed: Mode A fusion, straight adoption,
  adapt-and-install, or discard. Invoke with /intake, "a friend shared a skill", "I have a new
  skill from someone", "intake this", "what do I do with this incoming skill", or any moment a
  skill arrives from outside your own ecosystem and the question is how to bring it in cleanly.
  Without this gate, the orientation work runs implicitly and slowly inside the session; with
  it, the mode is known in two minutes and fuse-delta arrives already pointed.
triggers:
  - /intake
  - a friend shared a skill
  - I have a new skill from someone
  - intake this
  - what do I do with this incoming skill
  - someone shared this skill
  - bring this skill in
  - new external skill
scope: global
version: 1.0
date: 2026-06-20
author: meet.venkat1@gmail.com
---

# Intake

Cold orientation gate every external skill crosses before anything deeper turns — not a scanner, not fuse-delta. Answers one governing question first: how should this be processed at all? Fuse-delta assumes a comparison surface that may not exist; absent territory has nothing to fuse against, multi-function material can't be fused as one object. Intake is upstream — it points.

## The three questions (in order — each gates the next)

**Q1 — What type of material?** Determines the comparison surface before anything is compared. Types: **skill file** (compares to installed skills, same domain) · **contract variant** (compares to corresponding installed contract) · **session extract** (compares to memory + skills it would thicken) · **loose fragment** (no comparison surface — routes to spinal-column/forging first). Unclear type → name it before proceeding; misclassification poisons everything downstream.

**Q2 — Staffed or absent territory?** Search the installed ecosystem for a trigger that would fire on the same situation. Found → **staffed** → fuse-delta Mode A (three passes, contradiction detection). None → **absent** → no merge at all; collapses to adopt-as-is / adapt-and-install / discard. Most absent-territory skills should be adapted, not adopted raw — a friend's skill carries their lineage/naming/assumptions that rarely transfer whole.

**Q3 — Single or multi-function?** If it spans more than one territory, decompose before comparing — recurse each component through Q1/Q2 separately. Skipping this imports regression: a multi-function skill rarely maps to one installed skill, and installing the whole object because one function is genuinely new drags duplicated functions in with it. **The unit of intake is the function, not the document.** Per function: duplicates an installed organ at equal/lower fidelity → discard; duplicates but adds genuine density → Complementary Delta via fuse-delta; addresses absent territory → extract as candidate, adapt-and-install.

## The verdict (state explicitly, with reasoning, before any work)
```
PATH A — Mode A Fusion: staffed territory, single function, genuine peer → fuse-delta.
PATH B — Adapt and Install: absent territory, no analog → re-author, forge, /place.
PATH C — Decompose First: multi-function → split, each function re-enters intake alone.
PATH D — Discard: duplicates at equal/lower fidelity, no added density → note and decline.
```

## Relations
**Fuse-delta** is one of four paths (A only) — sequential, not overlapping: intake orients, fuse-delta merges. Running fuse-delta without intake is exactly the slow live-orientation problem this gate eliminates. Path A handoff arrives with mode and targets already determined.
**Placement-protocol** brackets the other end of the lifecycle — intake decides whether/how something enters, placement decides where it lands (arc-phase, registry entry). Path B/C outputs still need /place afterward.

## Behavior
Read fully → answer Q1 (name type, resolve ambiguity) → answer Q2 (search for a firing trigger, declare staffed/absent) → answer Q3 (decompose + recurse if multi-function) → state verdict + reasoning in the same response → on assent, execute (hand to fuse-delta / adapt-install / decompose / discard). Meant to take two minutes — its purpose is orientation, not depth; depth belongs to whatever path it routes to.

## Not
Not a merge tool (fuse-delta), not placement (placement-protocol), not a forge (spinal-column/intuition-forge), not an extractor (friction extractor). Owns one decision only — how to process the incoming thing — decided fast, then handed off.
