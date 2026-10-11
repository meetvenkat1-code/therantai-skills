---
skill: defer-log
source_file: skills/defer-log/SKILL.md
source_sha: 3689d555405c02ab4a6015b07c0f3e5c882109cff12e71180e618c521539ea13
---

# defer-log (skill behavior, verbatim)

```skill:body
# DEFER-LOG

Insurance-run closing instrument for sessions with no time for a full harvest. `/cognitive-friction-extractor` + `/place` is the full harvest (full reasoning, registry-grade); defer-log is fast, terse, preserved — produces recoverable capture `/place` can act on later at full fidelity, not placements itself. Closes the leak of sessions ending with friction resolved but nothing written.

## Scans for
Resolved friction (no tag required — reads the full record); skill candidates (named procedures, recurring decision rules); thickening signals (implicit skill extensions — new constraint/trigger/edge case); architectural decisions (standing rules, mandate updates, Drive writes decided not executed); open friction (broken, worked around, not resolved — carried forward, not extracted). Mid-session tags anchor the scan but aren't required.

## Entry format
```
SESSION: [date]  TYPE: [skill-candidate|thickening|architectural|open-friction]
ENTRY: [terse, per rules below]  TARGET: [skill being thickened, or null]
STATUS: raw-capture  PLACE-PRIORITY: [high|normal]
```
- **Skill candidate:** one sentence, transferable rule. `Cognitive Patterns: deferred commit log preserves session capture when full harvest isn't possible.`
- **Thickening** (needs most care) — the *full constraint sentence*, ready to install, not a pointer: `[target skill] → thicken: [full constraint, installable as-is].` A pointer-only entry requires reconstruction at replay; a full-constraint entry executes immediately.
- **Architectural:** one sentence — what decided, what surface affected.
- **Open friction:** one sentence — what broke, where it stands. Not yet a skill.

## Priority flagging
Flag 2-3 as `PLACE-PRIORITY: high` when: friction is likely to recur soon if unplaced; it thickens a frequently-firing skill; it's a new candidate staffing an undefended phase (structural gap). Surfaced at log end: *"If a few minutes remain — these are worth placing now."* Person decides; defer-log never forces /place.

## Drive write
Auto-appends (never overwrites) to `therantai-staging-placements.md` (ID: `1daiulTYJbW-TVQuxzAijyvaxHqKOJCiB`), grouped under `## SESSION — [date] · /defer-log`. Confirms file ID, entry count, high-priority count. Fires automatically unless the person says "do not write" after reviewing the rendered log.

## Does NOT
Run /place (no four-questions, no placement verdicts — entries stay raw-capture). Replace the extractor (no CATEGORY/SKILL/CONSTRAINT/TRIGGER/ASCENT, no patch drafts). Write to the skill registry (only /place + sweep does that). Emit ASCENT questions (extractor-only).

## Pipeline position
```
Full harvest:  extractor → /place → staging write → registry merge (sweep)
Light harvest: /defer-log → [auto staging write] → /place later → registry merge (sweep)
```
Not a bypass — an entry point that joins the pipeline at a later stage. A session closed with /defer-log has lost nothing; one closed with neither run has lost everything that resolved.

## Behavior
Scan full session (tags as anchors) → render log by type → flag high-priority → pause for review → auto-write unless stopped → confirm file ID/counts → close (does not open /place or the extractor — separate deliberate gestures).

## Output
```
DEFER-LOG — [date]
────────
SKILL CANDIDATES
  [01] TYPE: skill-candidate  ENTRY: [ ]  STATUS: raw-capture  PLACE-PRIORITY: [ ]
THICKENINGS
  [02] TARGET: [ ]  ENTRY: [full constraint]  STATUS: raw-capture  PLACE-PRIORITY: [ ]
ARCHITECTURAL
  [03] ENTRY: [ ]  STATUS: raw-capture  PLACE-PRIORITY: normal
OPEN FRICTION
  • [ ]
────────
TOTAL: [n] entries · [n] high-priority
IF A FEW MINUTES REMAIN — place these now: ★[ ] ★[ ]
────────
✓ Written — [n] entries appended · File ID: 1daiulTYJbW-TVQuxzAijyvaxHqKOJCiB
```
```
