---
skill: sync
source_file: skills/sync/SKILL.md
source_sha: 4f8441cd92ce5408c75240bcc2335d3ad4f9846b1c6341d46d0c3de354c3adf0
---

# sync (skill behavior, verbatim)

```skill:body
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
```
