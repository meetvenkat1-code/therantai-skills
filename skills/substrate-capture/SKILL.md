---
name: substrate-capture
description: Catches the failure where a correct realization mid-build ("this needs to live outside X") opens an unbounded engineering tail that quietly replaces the original intuition as the thing being optimized. Unlike scope creep, the drift is straight underneath the goal, not away from it, so every step still feels justified. Pre-build: self-trigger a Ceiling Line the moment such a realization surfaces, before infra work begins. Live: self-trigger an interrupt, mid-sentence if needed, once several consecutive decisions test against "does the substrate work" rather than the Ceiling Line. Manual triggers: "ceiling check", "is this substrate capture". Prospective, unlike recursion-ledger which is retrospective — logs there only after a capture event resolves.
triggers:
  - ceiling check
  - is this substrate capture
scope: global
version: 1.0
date: 2026-07-11
author: meet.venkat1@gmail.com
---

# Substrate Capture

One failure mode, not general scope discipline: a correct mid-build realization ("this can't be X, it needs to actually be Y") carries an unbounded tail, and nothing marks the boundary between implementing the realization and perfecting its tail. Every step feels like progress because it's adjacent and necessary-seeming — the swap from "building the idea" to "building the substrate" is invisible from inside the momentum. Unlike ordinary scope creep (drifts toward something unrelated, usually *feels* like drift), this drifts straight underneath the goal and feels like diligence the whole time.

```
INTUITION → build proceeds → REALIZATION SURFACES ("needs real infra")
                                     │ ◄── CEILING LINE written here (pre-build)
                              implementing it → tail opens
                                     │ ◄── LIVE TRIPWIRE checks here (continuous)
                              tested against Ceiling Line, or against "does substrate work"?
                                     │
                              DONE, or CAPTURED
```

## Mechanism 1 — Ceiling Line (pre-build)
**Trigger:** grammar "this can't just be X, it needs to actually be Y." **Action:** before writing any code for Y, write one line:
```
CEILING LINE
Realization:  [the "needs to actually be Y" insight, one clause]
Debt owed:    [what Y needs to DO — not BE — for the intuition to keep working]
Smallest Y:   [minimum version paying that debt — concrete enough that "more" is visibly extra]
Not-yet list: [things Y could grow into, explicitly deferred — naming drains the pull]
```
Not a plan for building Y — a ceiling on Y. "Smallest Y" is what every later decision is checked against, not the open-ended realization itself. Don't skip because the realization seems small — small-seeming ones have the longest unnoticed tails.

## Mechanism 2 — Live Tripwire (during execution)
**Trigger:** look at the last 3-5 decisions — tested against Smallest Y, or against "does the substrate work better"? Mostly the latter → fires, regardless of how reasonable each felt or whether real progress is happening (capture produces real progress — that's what makes it capture, not a stall). **Action:** interrupt immediately, mid-sentence if needed: *"This looks like substrate capture — testing against the infrastructure, not the Ceiling Line. Here's Smallest Y again: [restate]. Keep going past it, or stop here?"* Then stop and let the user decide — don't silently scope back down; a legitimately-moved ceiling is a valid outcome, not a failure of the check. No Ceiling Line was written → reconstruct one on the spot, retroactively, note it's late (still better than none).

## After resolution
A resolved capture event (ceiling held, or deliberately moved) is exactly recursion-ledger's shape of friction. Log there, standard format:
```
[date] substrate-capture: assumed <Y was the goal> → <Y was a delivery mechanism for Z, capped/moved> | session: <topic>
```
No persistent log of its own — live discipline, not archive; only resolved events are worth recursion-ledger's ink.

## Relations
Recursion-ledger: retrospective sibling (flags friction *after* a break); substrate-capture is prospective (marks the boundary *before* the tail opens). Compose at one point only — resolved capture is loggable friction. Idea-to-engine's North Star is the closest relative to a Ceiling Line but not the same: North Star extracted once at Stage 1, carried through a whole engine build; Ceiling Line is narrower, can fire any number of times, anywhere, not just engine builds — if a North Star already exists, check "Debt owed" against it directly. Ui-contract is unrelated (layout/behavior vs. this process failure). Priority: named contracts/mandates > an active Ceiling Line > default judgment.
