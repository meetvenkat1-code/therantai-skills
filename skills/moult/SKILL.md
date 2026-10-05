---
name: moult
description: >
  The organ of subtraction in a skill ecosystem that otherwise only knows how to add.
  Audits the Skill Registry against the actual installed skill files and against managed
  memory, surfaces every divergence between the three surfaces — phantoms, orphan installs,
  dead doctrine, never-fired skills — and reconciles them by writing corrected verdicts back
  into the registry. The inverse twin of placement-protocol: placement stamps each skill's
  BIRTH into the registry; moult stamps each DEATH with equal ceremony. Invoke with /moult
  to run a full reconciliation sweep, or /moult --check for a diagnose-only dry run that
  writes nothing. Trigger also on phrases like "audit the registry", "reconcile the skills",
  "what's drifted", "check for phantom skills", "the registry feels stale", "moult the
  ecosystem", "prune dead skills". Do NOT trigger automatically — moult is destructive-capable
  and runs only on intentional invocation.
triggers:
  - /moult
  - /moult --check
  - audit the registry
  - reconcile the skills
  - what has drifted
  - check for phantom skills
  - the registry feels stale
  - moult the ecosystem
  - prune dead skills
scope: global
version: 1.0
date: 2026-06-20
author: meet.venkat1@gmail.com
---

# moult

A system that can only add decays into a mostly-accurate list — the most dangerous kind, trusted without checking. Moult is the organ of forgetting, deprecating, reconciling. Placement-protocol read backwards: placement stamps birth into the registry, moult stamps death.

## When it fires
Never automatically — destructive-capable, only on invocation. `/moult` = full sweep ending in a ratified write. `/moult --check` = diagnose-only dry run, writes nothing. Run when the ecosystem feels stale, a build references a nonexistent skill, or as the subtractive bookend to a heavy-forging season. An ecosystem that runs placement and never moult can only inhale.

## The three surfaces
Drift hides because each surface is internally coherent alone — visible only in the gaps between them.
| Surface | Holds | Can lie about |
|---|---|---|
| REGISTRY | what you declared | a skill never built, or moved-past placement |
| INSTALLED FILES | what actually loads | nothing — a file exists or doesn't |
| MEMORY | what you believe | doctrine the files already abandoned |

**Ground truth: the filesystem.** When surfaces disagree, correct registry and memory *toward* the filesystem, never the reverse — it's the only surface that can't hold an aspiration. (Proven case: registry+memory both claimed intent-lock/plumbline installed — two-against-one consensus, both wrong. Consensus between two aspiration-capable surfaces isn't truth.)

## Divergence categories
**PHANTOM** — registry/memory claims a skill the filesystem lacks (most dangerous). **ORPHAN INSTALL** — a file exists the registry never recorded. **DEAD DOCTRINE** — memory asserts a constraint the files have moved past. **NEVER-FIRED** — recorded, exists, never triggered in available history — not necessarily dead (may be dormant-but-load-bearing), flagged for a verdict. **CONTRADICTION** — two surfaces/entries assert incompatible things about the same skill.

## Verdict set
**KEEP** — benign or dormant-but-load-bearing; reasoning recorded so it's not re-litigated. **REPAIR** — entry wrong, correct toward filesystem, skill stays. **SHED** — phantom/dead-doctrine/confirmed-dead → graveyard, never struck. **UNVERIFIABLE** — filesystem not fully readable this session; no destructive action, flagged for next sweep — moult never sheds on incomplete sight.

## The graveyard (subtraction with memory)
Never hard-deletes (would erase the auditor's own decisions — fatal for a skill whose authority rests on being trustworthy about subtraction). Shedding is move-and-stamp: mark `status: shed`, stamp `shed_date` + `shed_reason` (category + argument), relocate to `## GRAVEYARD`. Living ledger stays clean (phase-map never renders the graveyard) but every cut leaves a readable scar and remains reversible — exhumable if it turns out dormant, not dead.

## The reckoning (how moult speaks its verdicts)
Not item-by-item interrogation (too exhausting → avoided → drift accumulates) nor silent writes (untrustworthy). Instead: (1) full three-surface walk, autonomous; (2) verdict + reasoning per flagged entry; (3) laid before you as one batch; (4) ratify in one gesture — bare "go" ratifies the whole sweep, or strike individual lines; (5) only on ratification: repairs amended, sheds moved to graveyard, phase-map regenerated. All deciding done by moult, all reasoning shown, nothing written until assent — the graveyard is the safety net under a fast ratification.

## Reckoning format (structured table, never prose)
```
MOULT RECKONING — <date>
Surfaces read: REGISTRY ✓ | FILES <✓/partial> | MEMORY ✓

| # | Skill | Divergence | Verdict | Reasoning |
| 1 | intent-lock | PHANTOM | SHED | claimed installed, no file. → graveyard. |
| 2 | typography/Syne | DEAD DOCTRINE | REPAIR | Syne deprecated, amend to Space Grotesk. |
| 3 | rupture | NEVER-FIRED | KEEP | dormant-but-load-bearing. |

RATIFY: "go" to commit all · or strike line numbers to override.
```
`--check` → same table, footer: `DRY RUN — nothing written. Re-run /moult to commit.`

## After the write
Reconciliation IS the registry write. Then: regenerate the phase-map from the corrected registry (never by hand); if any SHED/REPAIR touched a managed-memory constraint, surface the specific edits needing update for ratification (memory changes only by your hand, never silently); report net change (N repaired, N shed, N unverifiable carried forward).

## The pairing
placement-protocol : moult :: inhale : exhale. Run placement when something is born; run moult when the ecosystem feels heavier than its living skills justify. Only-placement accumulates phantoms; moult-without-mercy sheds the dormant — KEEP and UNVERIFIABLE are the mercy, the graveyard is the memory, the filesystem is the truth.
