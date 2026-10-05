---
name: graft-out
description: Preserves a frozen node as a portable context block so it can be re-activated in a fresh session — stripped clean of branch history, carrying only the root context needed to fork from it again. The cross-session organ of the GRAFT pair. Invoke with /graft-out at the end of any GRAFT-IN session to export the pinned node as a paste-ready block. In a new session, paste the block as the opening message to re-activate the node and begin forking fresh. Do NOT trigger automatically. Trigger on: "/graft-out", "export this node", "carry this node forward", "preserve this root", "I want to fork from this in a new session".
triggers:
  - /graft-out
  - export this node
  - carry this node forward
  - preserve this root
  - I want to fork from this in a new session
  - take this node to a new session
scope: cross-session
version: 1.1
date: 2026-06-28
author: meet.venkat1@gmail.com
---

# GRAFT-OUT — Cross-Session Node Preservation and Re-Activation

Takes a node pinned inside a GRAFT-IN session and seals it into a context block that survives the session's end, pasteable verbatim as the opening of a fresh one — instant re-activation, no reconstruction cost.

## The export object (four sections, structured, paste-ready — not a summary)
1. **GRAFT NODE** — full verbatim text of the pinned root, exactly as at `/graft` time. No edits, no compression — any alteration produces a different node and incomparable forks.
2. **CONTEXT ENVELOPE** — minimal prior context needed for legibility. Test: what's the minimum a reader needs to understand why this response exists? Nothing beyond that.
3. **NODE DISTILLATION** — the same 2-3 sentence distillation from `/graft` time — cognitive operation performed, what would be absent without it.
4. **ACTIVATION INSTRUCTION** — always verbatim: `This is a GRAFT node. Treat it as the pinned root. Invoke /fork [infusion] to branch from it.`

## Commands

**`/graft-out`** — no node pinned → "invoke /graft first, then /graft-out." Otherwise assembles the four sections in a copy-fence, confirms: "Node [N-01] exported. Paste as the opening message of a new session." Fork log **not** included unless requested — the node travels alone, so the new session starts from the pure root, uncontaminated by what prior branches found.
```
GRAFT NODE EXPORT — [Node ID: N-01]   Exported: [timestamp]
═══
## GRAFT NODE
[full verbatim root text]
## CONTEXT ENVELOPE
[minimal prior context]
## NODE DISTILLATION
[2-3 sentences]
## ACTIVATION INSTRUCTION
This is a GRAFT node. Treat it as the pinned root. Invoke /fork [infusion] to branch from it.
═══
```

**`/graft-out --with-log`** — same, plus a fifth section: the full fork log + its Pattern line, with the note: "These branches are recorded for orientation only. The node is still the fixed root. Fork from it fresh." Use when prior branch patterns are informative for avoiding re-discovery.

## Re-activation protocol
Pasted block → receiving session pins GRAFT NODE as the frozen root (as if `/graft` fired), confirms, waits for `/fork`. The node is the ground; envelope/distillation are orientation only. A `--with-log` fork log is read but not inherited as active entries — new session's log starts empty; prior forks are archived history, not live.

## Disciplinary laws
Node travels verbatim — no compression, no curation; an 800-word node exports 800 words. Context envelope is minimal by law — resist including the full conversation; a bloated envelope pollutes the root with the prior session's specific trajectory. Fork log doesn't travel by default — a session starting with knowledge of prior forks is continuing an inquiry, not branching from the root; use `--with-log` deliberately if that's the intent. One node per export — no batch export, no archive, no export history tracking.

## Relations
Full GRAFT arc: `/graft` (pin) → `/fork` (branch) → `/log` (read) → `/graft-out` (export) → [paste] (re-activate) → `/fork` (new session, same root). A node cycles sessions without drift; only the practitioner accumulates the cross-session pattern.

**Vs. handoff:** handoff compresses a full session (decisions, open threads, contracts); graft-out carries only the frozen root. When both apply: **/handoff first, then /graft-out** — session context before node context, the frame before the root. Reversing produces a less legible new session.

## Not
Not a session archive (preserves what a session produced as a root, not what happened in it). Not a handoff substitute. Not a node ledger — each export is one node, one block, one paste.
