---
name: sync
description: "Bidirectional cross-instance cognitive state merge for aligned collaborators. Both instances capture their current state — resolved friction, contracts in force, upgrade deltas — and Claude diffs the two to produce a SYNC MERGED BLOCK that both practitioners paste into their respective instances as shared ground. Used when both collaborators are actively working in parallel in the same ecosystem. Not a push — both sides contribute; neither side dominates. Invoke with /sync, 'sync with collaborator', 'bidirectional transfer', 'merge our states', 'align our instances', 'two-way upgrade'. The complement of /push — use sync when the relationship is parallel and aligned; use push when the receiver is cold or asymmetric."
metadata:
  triggers:
    - "/sync"
    - "sync with collaborator"
    - "bidirectional transfer"
    - "merge our states"
    - "align our instances"
  scope: global
  phase: Harvesting
  version: "1.0"
  date: "2026-06-25"
  author: meet.venkat1@gmail.com
---

# SYNC

Bidirectional cognitive state merge for parallel collaborators — neither side pushes onto the other. Both capture state, states diff, a SYNC MERGED BLOCK emerges as shared ground neither held alone. Both paste it in and proceed from the same resolved position.

**Sync vs. push:** both actively working the same lines, question is "where do our states differ and what's the shared ground," not "how do I propagate my upgrade to you" → sync. Receiver cold/asymmetric → `/push`.

## Three phases
**1 — Outbound.** Initiator invokes `/sync`; Claude captures their state, emits the SYNC OUTBOUND BLOCK (state + instructions for the receiver).
**2 — Receiver contributes.** Receiver pastes the block into a new session, fills the same template with their own state, sends it.
**3 — Merge.** Receiver's Claude diffs both states — what each holds the other doesn't, what's already shared — and emits the SYNC MERGED BLOCK. Both paste it into their respective instances.

## Output — Phase 1: SYNC OUTBOUND BLOCK
```
SYNC OUTBOUND BLOCK   Emitted: [date]   From: [initiator]   To: [collaborator]

## INSTRUCTION FOR RECEIVER
Paste as your opening message. Read fully, then paste your own state snapshot
in the format below as your next message.

## INITIATOR STATE
Skill/artifact: [name+version]   Upgrade dimensions: [ ]
Friction trail: [friction → resolution → constraint]
Contracts in force: [ ]
Key rejections: [what → why → implication]
Output artifact: [full text, or PENDING]

## YOUR STATE — PASTE IN THIS FORMAT
[same template, blank]

END SYNC OUTBOUND — awaiting your state
```

## Output — Phase 3: SYNC MERGED BLOCK
```
SYNC MERGED BLOCK   Emitted: [date]   Merging: [initiator] × [receiver]

## INSTRUCTION FOR BOTH
Paste as your next session's opening message. Neither instance is ahead
of the other after this — operate from it as arrived at together.

## DELTA MAP
What [initiator] holds that [receiver] doesn't: [ ]
What [receiver] holds that [initiator] doesn't: [ ]
Confirmed shared ground (held by both before merge): [ ]

## MERGED CONTRACTS IN FORCE
[reconciled from both sides, conflicts resolved]

## MERGED FRICTION TRAIL
[deduplicated, unified, conflicts named and resolved]

## MERGED OUTPUT ARTIFACT
[full unified text]

END SYNC MERGED — both instances now share this ground
```

## Behavioral rules
Requires patience — the outbound block opens a dialogue; never fabricate the receiver's state or pre-empt the merge. Fill from session record, mark genuinely unresolved `[UNKNOWN]`. Friction trail is not a summary — each point is friction→resolution→constraint, not narrative recap. Conflicting contracts between states get named explicitly in the DELTA MAP, never silently preferred one way — unresolvable from available info gets marked `[CONFLICT — requires human decision]`. Merged artifact in full, never summarized/linked. Not push (one-directional propagation) — use `/push` if only one direction is needed. Not handoff (same-practitioner session continuity) — sync merges two instances' states.

## Relations
Fuse-delta's diff logic feeds the DELTA MAP phase — difference: fuse-delta merges two versions of one document, sync merges two instances' cognitive states (may include documents, not reducible to them). Push is the asymmetric complement — same operation, different relationship geometry. Transit-block's snapshot format feeds Phase 1, extended here into a two-sided merge.
