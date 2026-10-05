---
name: log-this
description: >
  Three-tier friction capture. Tier 1 /log: append one line to friction-log.md. No
  reasoning, no registry touch. Tier 2 /log-sweep: batch-read log, extract, match
  against ecosystem, place (autonomous), write skill-registry.md, clear log. Tier 3
  (auto, inside sweep): write targeted brain-doc delta only if batch is doctrinally
  significant — new phase defended, standing law implied/contradicted, brain-doc-named
  skill's role changed, or 3+ entries thicken one skill. Else no-op. /brain-sync runs
  Tier 3 standalone. /log-sweep --no-sync skips Tier 3 for that run.
triggers:
  - /log
  - log this
  - log that friction
  - /log-sweep
  - sweep the log
  - reconcile the friction log
  - run the sweep
  - /brain-sync
scope: global
phase: Compressing
version: "3.0"
date: 2026-07-04
author: meet.venkat1@gmail.com
supersedes: "log-this v1.0 (single-pass, registry-direct); v2.0 (two-tier, no doctrine sync) — retired: wrong cost tier for routine use, then missing the doctrine-drift closure"
---

# LOG-THIS v3 — THREE-TIER CAPTURE

Placement is batch-shaped (its value comes from seeing several frictions relationally at once) — forcing it to per-friction frequency was v1.0's category error. v3 splits capture from placement into the minimum two-stage shape the cost difference requires, plus a near-free doctrine check riding the expensive tier.

## Tier 1 — LOG (cheap, constant, every time)
`/log`, "log this" → one line appended to `friction-log.md`. No formatting, no matching, no four questions, no registry touch.
```
[date] · [terse description, practitioner's own frame]
```
Completion: `Logged.` — nothing more. Designed to be nearly free since it's the only tier that must fire at friction-frequency.

## Tier 2 — SWEEP (batch, occasional, deliberate)
`/log-sweep`, "sweep the log":
1. Read the full log.
2. Extract batch-wide — press into CATEGORY/SKILL/CONSTRAINT/TRIGGER/ASCENT, reading entries against each other first so duplicates collapse and near-identical frictions merge before formatting.
3. Match against the ecosystem — thicken before proposing new.
4. Place — resolve scheme/phase/trigger/staffed-or-orphan, autonomous by default (batch view already carries the relational advantage Socratic mode surfaces one-at-a-time).
5. Write the resolved batch to `skill-registry.md` in one pass.
6. Clear `friction-log.md`.
```
SWEEP COMPLETE — [n] raw entries → [m] registry writes ([k] merged, [j] thickened, [i] new)
Log cleared.
```
Cadence: occasional, deliberate — whenever the log feels worth reconciling. No fixed schedule; sitting costs nothing.

## Tier 3 — Conditional brain-doc sync (cheap check, rare write)
Runs automatically at the end of every Tier 2 sweep. Asks one question of the batch just written: **is it doctrinally significant?** — yes only if one holds: a new phase got defended (orphan staffed an undefended arc-phase); a standing mandate/law is implied or contradicted; a skill named in the brain doc had its described role changed (not just its constraint list); 3+ entries thicken the same skill (density signal of a shifted role).

None hold (the common case) → no write, no cost beyond the check. One or more hold → write a **short targeted delta** to `therantai-brain.md` — the specific changed section, never a full regeneration.
```
Brain doc: [unchanged | synced — <one-line description>]
```
Override: `/log-sweep --no-sync` skips Tier 3 for that run. `/brain-sync` runs Tier 3's logic standalone against current registry state (e.g. after a moult cut, independent of a recent sweep).

## Family map
Capture family — Tier 1 absorbs defer-log's terse posture as standing rhythm; defer-log remains for architectural decisions and open-unresolved friction Tier 1 isn't scoped for. Placement family — Tier 2 absorbs placement-protocol's batch mode, autonomous by default (full Socratic still reachable on request). Sequencing family — harvest-pipeline's full ceremony now reserved for sessions wanting explicit pause architecture; routine sessions just need Tier 1 during, Tier 2 (+Tier 3) when the log's worth clearing. Doctrine family — brain-doc currency is now a standing property of Tier 2, not a fourth ritual to recall — registry currency and doctrinal currency no longer drift apart by default.

## Lineage
v1.0's instinct to remove per-friction ceremony was right; its error was collapsing a batch-shaped operation to per-friction frequency. v2 split log from sweep. v3 closes v2's remaining gap (registry currency without doctrine currency) as a near-free tail on the already-expensive operation, not a fourth ritual. Each version subtracted a wrong assumption rather than adding complexity — the shape worth preserving.
