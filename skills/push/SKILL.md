---
name: push
description: "One-directional cross-instance cognitive state transfer. Captures the current state of a practitioner's instance — resolved friction, upgrade delta, contracts in force, key rejections — and emits a paste-ready PUSH BLOCK that another Claude instance can absorb cold as the opening message of a new session. Used when the receiver is not deeply aligned or is receiving an upgrade cold. No capture of the receiver's current state — transfer is outbound only. Invoke with /push, 'push this upgrade', 'push to my friend', 'send this upgrade', 'propagate outward', 'one-way transfer', 'upgrade block for collaborator'. The complement of /sync — use push when the relationship is asymmetric or the receiver is cold; use sync when both instances are actively collaborating in parallel."
metadata:
  triggers:
    - "/push"
    - "push this upgrade"
    - "push to my friend"
    - "send this upgrade"
    - "propagate outward"
    - "one-way transfer"
    - "upgrade block for collaborator"
  scope: global
  phase: Harvesting
  version: "1.0"
  date: "2026-06-25"
  author: meet.venkat1@gmail.com
---

# PUSH

One-directional cognitive state transfer — not just the output, the *generative reasoning*: friction traversed, decisions made, alternatives rejected, contracts in force. Receiver's instance absorbs it cold as a new session's opening message and operates from resolved understandings, not a received file.

**Push vs. sync:** receiver not in active parallel collaboration, may be in the same ecosystem but absent for the friction that produced this upgrade → push (outbound only, no receiver-state capture). Both instances actively collaborating in parallel → `/sync` instead.

## What transfers
Current state snapshot · upgrade delta (what changed, superseded version, key dimensions) · friction trail (named points, each with friction→resolution→constraint) · contracts in force (not re-litigated) · key rejections (considered + discarded + why) · output artifact (full, appended).

## Output
```
PUSH BLOCK
Emitted: [date]   From: [identifier/context]

## BRIEFING INSTRUCTION
Paste as the opening message of a new session. You are receiving resolved
understandings, not a file — operate from them as if you arrived at them yourself.

## UPGRADE IDENTITY
Skill/artifact: [name]   Previous: [vX.X]   Current: [vX.X]   Dimensions: [ ]

## FRICTION TRAIL
[point]: [friction → resolution → constraint produced]
...

## CONTRACTS IN FORCE
- [stated as a constraint, not a preference]

## KEY REJECTIONS
- [considered] → rejected because [reason] → [implication]

## OUTPUT ARTIFACT
[full text, appended]

END PUSH BLOCK — absorb and proceed
```

## Behavioral rules
Fill from the session, not imagination — genuinely unresolved fields marked `[UNKNOWN]`, never fabricated. Friction trail is not a summary — each point names friction/resolution/constraint, not narrative recap. Output artifact appended in full, never summarized or linked (`[NO ARTIFACT — conceptual upgrade only]` if none). Not handoff (same-practitioner session continuity — redirect to /transit-block if that's the need). Not sync (no receiver-state capture, no diff/merge — redirect to /sync if bidirectional).

## Relations
Fuse-delta's FRICTION/RESOLUTION/CONSTRAINT structure feeds the friction trail. Transit-block's snapshot logic is the base, adapted for cross-instance rather than same-practitioner continuity. Sync is the bidirectional complement — push when asymmetric/cold, sync when parallel/aligned.
