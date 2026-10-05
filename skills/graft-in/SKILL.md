---
name: graft-in
description: Pins the immediate prior response as a frozen root-node inside the current session and opens a sequential branching log from it. Each invocation of /fork runs one new branch from the same pinned root — a different infusion, a different continuation — without moving the root. Multiple forks accumulate against the same fixed ground. The in-session organ of the GRAFT pair. Invoke with /graft to pin a node, /fork to run a new branch from it, /log to read the accumulated branch-log, /root to recall the pinned node verbatim. Do NOT trigger automatically — GRAFT is always a deliberate act. Trigger on: "pin this", "branch from here", "fork from this point", "I want to try a different direction from this response", "graft this", "/graft", "/fork".
triggers:
  - /graft
  - /fork
  - /log
  - /root
  - pin this node
  - branch from here
  - fork from this point
  - I want to try a different direction from this response
scope: session-local
version: 1.1
date: 2026-06-28
author: meet.venkat1@gmail.com
---

# GRAFT-IN — In-Session Node Pinning and Sequential Branching Log

Holds a root response fixed while branches accumulate against it — bringing ChatGPT's per-response fork gesture inside one thread, but legible: branches sit side by side in a durable log instead of isolated.

## When NOT to invoke
**/fan territory** — stuck/entangled/frame-exhausted, not arrival. Graft fires on an already-resolved response worth varying; pinning a jammed one produces branches of the jam, not variations of a generative ground.
**/ramify territory** — need a fan of divergent successor *questions* from friction, not controlled counterfactuals on a fixed root. Graft = compare continuations; ramify = generate directions.
**No node yet** — /graft can't fire without a prior response. If invoked too early: "Nothing to pin yet — /graft pins the immediately prior response."

## The three objects
**Node** — the frozen root, pinned once at `/graft`, never updates; conversation happens around it, never in it.
**Infusion** — the one variable injected per branch (one constraint/reframe/context fragment/question angle). One infusion per branch is what makes a fork readable — two makes attribution ambiguous.
**Fork** — one branch run under one infusion. Forks accumulate in the log, addressable by number; they never replace each other.

## Commands

**`/graft`** — pins the immediately preceding response. Compresses to a titled snapshot (Node ID, timestamp, 2-3 sentence distillation of its generative ground, not its conclusions), declares it open, then waits.
```
NODE PINNED — [Node ID: N-01]
Root: [2-3 sentence distillation]
Pinned at: [timestamp/position]
Status: OPEN — awaiting first fork
Invoke /fork [infusion] to branch from this root.
```
One node per session — re-invoking with a node already pinned prompts: replace (closes current log, opens new) or continue branching from existing root. Never silently overwrites.

**`/fork [infusion]`** — runs one branch from the pinned node under the stated infusion. No node pinned → "invoke /graft first." No infusion given → ask for one. Generates the continuation as if the node had been seeded with that infusion, appends to the log with a fork number, then a one-sentence diff note (most visible shift vs. previous fork or raw node).
```
FORK [F-01] from Node [N-01]
Infusion: [verbatim]
[Branch response, full]
Δ Shift from [previous]: [one sentence]
```
Two+ infusions in one call → name them explicitly, flag attributional ambiguity, proceed only on confirmation, mark the entry `infusion-compound: true`.

**`/log`** — full accumulated branch log for the pinned node:
```
GRAFT LOG — Node [N-01]
Root: [distillation]
  F-01 | Infusion: [ ] | Δ: [ ]
  F-02 | Infusion: [ ] | Δ: [ ]
Pattern so far: [1-2 sentences — which dimensions are sensitive to infusion, what stayed stable]
```
The Pattern line is the highest-value output — meta-knowledge across forks, not per-fork change.

**`/root`** — recalls the pinned node verbatim (full text, not distillation). Use to re-read before forking or to re-ground after drift.

## Disciplinary laws
One infusion per fork — the discipline is the instrument. The node never drifts — fixed regardless of what forks or subsequent conversation produce. Forks never invalidate each other — comparative log, not revision history. Graft-in never fires ramify — different object (root vs. friction), different output (log vs. fan).

## Relation to GRAFT-OUT
Graft-in is session-local — the log dissolves at session end unless exported. Graft-out is the cross-session organ, preserving a frozen node as a portable block for a fresh session. Export via `/graft-out` or "export this node" — the node exports clean, the fork log only with `/graft-out --with-log`.

## Not
Not a revision tool (varying, not correcting). Not a ramify replacement (pre-resolution divergence vs. post-resolution counterfactual). Not an undo (node and main thread coexist; pinning doesn't rewind).
