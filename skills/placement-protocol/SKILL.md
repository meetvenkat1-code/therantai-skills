---
name: placement-protocol
description: The deliberate gate every named friction passes through after it is extracted and before it is installed as a skill. Resolves the four structural questions — organizing scheme, arc-phase, trigger condition, staffed-or-orphan verdict — and writes the result to the Skill Registry, the single structured source of truth for the ecosystem. Runs socratic by default (questioning the person through each placement to train structural instinct) with an autonomous escape hatch. The complement of cognitive-friction-extractor — the extractor NAMES the friction, this skill PLACES it. Invoke with /place to smelt a batch of named-but-unplaced frictions, and /map to regenerate the SVG zone projection from the registry on demand.
triggers:
  - /place
  - place these skills
  - place this friction
  - run placement
  - locate this in the architecture
  - where does this skill belong
  - /map
  - regenerate the skill map
  - project the zone map
scope: global
version: 1.0
date: 2026-06-19
author: meet.venkat1@gmail.com
---

# Placement Protocol

A deliberate gate — not a scanner, not a builder. Naming a friction and placing it are two different acts at two different temperatures: cognitive-friction-extractor scans and names (CATEGORY/SKILL/CONSTRAINT/TRIGGER); a named skill with no declared scheme/phase/verdict enters as an orphan on a flat list, and enough orphans recreate the exact "which one now?" disease the whole ecosystem exists to prevent. This gate stops that from forming. The gate and the ledger are one mechanism — placement's final act is the atomic write to the Skill Registry itself; nothing enters without passing through it.

## Two temperatures
Catching friction is hot and fast (extractor's domain, mid-build). Placing is cold and deliberative — structural questions deserving consideration, not reflex. Fusing them would force the slow act to run at the fast one's speed, which is exactly how orphans slip through. So placement runs as its own batch pass: `/place` smelts the whole batch at once, and batch view surfaces what isolated placement hides (two frictions that are really one skill; three crowding one phase while another stands undefended).

## The family above the four questions
Parent dimension: **organizing schemes** — three children, easy to conflate:
- **Pipeline** — dependency order; reorder two stages and it breaks (`spinal-column → intuition-forge`).
- **Lifecycle/phase model** — temporal stage; loose membership, clusters into befores/afters (Opening→Forging→Governing→Compressing→Closing→Harvesting).
- **Taxonomy** — shared essence, no temporality at all.

The right scheme depends on the recurring decision being made of the set, not the set itself — phase wins when the question is "which one now?" Most real practices are lifecycles with embedded pipelines inside individual phases (the engine-build ecosystem is exactly this) — expect this nested form as default.

## The four questions (in order)
1. **Which organizing scheme?** Reordering breaks it → pipeline. Reordering's fine but clusters into befores/afters → lifecycle. No temporality → taxonomy.
2. **Which arc-phase does it staff?** Name the lifecycle phase defended (or fresh phase for a new domain); if inside an embedded pipeline, name both phase and pipeline position.
3. **What's its trigger condition?** The exact situation that wakes it — not a paraphrase of function — specific enough to fire reliably without colliding with a neighbor.
4. **Staffed or orphan?** Thickens an existing skill (name it, prefer this — density over count) or stands alone (name the phase newly defended, check if any phase is now left undefended — an empty phase is an exposed flank and a build target). This is where placement becomes generative, not just filing.

## Registry architecture
Master record separate from its projection (same law as standalone-source-first, artifact-by-projection). Registry is structured (table/YAML, never prose — prose can't be queried or projected):
```yaml
- skill: <name>
  scheme: pipeline | lifecycle | taxonomy
  phase: <arc-phase staffed>
  pipeline_position: <name + position, or null>
  trigger: <condition>
  verdict: staffed | orphan
  thickens: <skill joined, or null>
  defends_phase: <phase newly defended, or null>
```
SVG zone map is a projection *of* the registry, regenerated on demand via `/map` — never maintained by hand, never bound to every write (that would make the cheap act expensive and tempt skipped placements).

## Invocation modes
**Socratic (default)** — walks the four questions as prompts, one friction at a time, with a recommendation + reasoning alongside each (never a bare fork); the person answers. Slower deliberately — trains structural instinct, engineered to make itself progressively less necessary.
**Autonomous (escape hatch)** — "you place it" → resolves all four itself, writes, presents for audit. Use once the instinct is already built.
**Map projection** — `/map` regenerates from current registry state, a separate deliberate act.

## Behavior
1. Gather named-but-unplaced frictions (session or named by the person). 2. Confirm the batch before smelting — placed against each other. 3. Per friction: socratic prompts (waiting each answer) or autonomous resolution + audit. 4. Atomic registry write after each — the write is the final act, no placement without recording. 5. Flag any phase the batch leaves undefended. 6. Next friction only after the current is written. 7. **Placement echo:** after the full batch, ask whether any new placement exposes a gap in a governing skill (ui-contract, typography, prompt-engine-interface-contract) — if yes, generate candidate upgrade text flagged for fuse-delta; if no, state "No governing skill upgrades triggered."

`/map` always regenerates from the current registry, never from memory.

## Output
```
PLACE — [session/date]
BATCH: [n frictions]
FRICTION 01 — [name]
  Q1 SCHEME: [ ] ← recommendation + reasoning
  Q2 PHASE: [ ]   Q3 TRIGGER: [ ]   Q4 VERDICT: [staffed→thickens <skill> | orphan→defends <phase>]
  REGISTRY WRITE: [yaml block]
  ✎ written to registry.
...
UNDEFENDED PHASES (build targets): • [ ]
```
Empty batch → say so plainly; not a failure, means everything already found its home.

## Relationship to the extractor
Load-bearing order: extraction must precede placement. Extractor NAMES (catches the ore); placement PLACES (smelts it, files the metal, writes the registry). The extractor's "Forge New Skill" route is the exact handoff point — a new skill must pass /place before it's considered installed; skipping the gate makes it an orphan by definition.

## Scope
Global, domain-agnostic — applies to any ecosystem where "which one now?" recurs. Building a placement structure for a new domain: name the domain's arc as phases first (never start from tools), sort tools into phases by function, find embedded pipelines, scan for undefended phases, name the bookends (opening axis + closing proof) — a goal with no defined entry/exit leaks at both ends.

## Governing principle
Not filing neatly — keeping the ecosystem inspectable as one coherent architecture instead of a flat list of peers. Every placement locates a skill *and* keeps the registry true, simultaneously — gate and ledger never drift apart. The highest form of placement is the moment the gate reveals a phase nothing yet defends — the protocol telling you what to build next.
