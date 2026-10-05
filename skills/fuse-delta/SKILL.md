---
name: fuse-delta
description: >
  Use this skill whenever the user wants to merge, compare, or evolve cognitive contracts,
  skill files, UI contracts, living documents, or constraint maps. Triggers include: "fuse
  these contracts", "merge these skills", "what's different between these", "absorb the
  delta", "combine our contracts", "sync our skill files", "one builder has X and I have Y",
  "evolve this contract with new learnings", or any request involving two versions of the
  same document where the goal is to extract resolved friction rather than simply diff text.
  Also triggers for Mode B (self-evolution): "update my contract with these session notes",
  "evolve this skill based on what we learned", "absorb this into the contract".
  IMPORTANT: Use this skill any time the user wants to merge knowledge between two builders,
  contracts, or skill instances — even if they don't use the word "fuse" or "delta".
---

# Fuse Delta

Additive diff merges on living contracts — not a text merger, not version control. Transfers resolved cognitive friction between contract instances: one builder resolves friction, fuse-delta transfers that immunity to the other. The valuable artifact is never the text — it's the friction resolution embedded inside it.

## Modes
**A — Cross-instance fusion:** two contracts in, Fusion Report + Updated Contract out.
**B — Self-evolution:** one contract + new session observations in, Evolution Report + Updated Contract out.
If unclear which, ask.

## Three-pass algorithm (run in order, never skip or merge passes)

**Pass 1 — Intersection.** Constraints present in both = pre-shared immune memory. Discard from merge, log as convergence evidence. No new value from absorbing them.

**Pass 2 — Complementary delta** (primary value-generation). Constraints present in one, absent in the other = friction one builder hit that the other hasn't. Absorb with full provenance:
```
FRICTION — what kept recurring
RESOLUTION — what fixed it
CONSTRAINT — the rule now encoded
SOURCE — which instance originated it
```
Without provenance, rules become decorative.

**Pass 3 — Contradictory fork.** Same territory, different resolutions. Never merge blindly — surface the fork:
```
TERRITORY / RESOLUTION A / RESOLUTION B / ANALYSIS (which is structurally superior, why)
TRADEOFFS / RECOMMENDED / CONFIDENCE (High/Medium/Requires user judgment)
```
Recommend first; ask only when superiority genuinely can't be determined. Prefer resolutions for structural superiority, precision, resilience, or a true synthesis — never for recency, length, or "whose instance this is" alone. State the assumptions under which a recommendation holds.

## Output (always dual)
**Artifact 1 — Fusion Report:** Convergence Map, Absorbed Deltas (with provenance), Resolved Forks, Unresolved Forks (if any), Summary. See `references/report-template.md`.
**Artifact 2 — Updated Contract:** all original constraints unchanged + absorbed deltas woven into appropriate sections (never dumped at the bottom) + resolved forks applied + unresolved forks flagged inline `[FORK: UNRESOLVED]`. Reads as one coherent document, not a patchwork — maintain the target's voice, formatting, section architecture; don't restructure wholesale.

## Execution
1. Identify mode (ask if unclear). 2. Parse both inputs fully before any classification. 3. Run the three passes in order. 4. Generate Fusion Report — name the source contract for every absorbed delta. 5. Generate Updated Contract — integrate into existing structure. 6. Present Fusion Report first, Updated Contract second; surface unresolved forks before the Updated Contract and request decisions.

## Provenance format (inline, in the Updated Contract — see `references/provenance-format.md`)
```
> **[DELTA: absorbed from Contract B]**
> *Friction:* [what kept going wrong]
> *Resolution:* [what fixed it]
```
Strippable for a clean version, but present in the primary output.

## Recursive loop
```
Builder A friction → resolved → becomes contract constraint → fuse-delta extracts
→ Builder B absorbs → avoids the friction → repeats both directions
```
Result: shared immune system across instances.

## Edge cases
Identical contracts, different surface text → Intersection; don't absorb style. One contract a strict subset → all unique constraints are Complementary Deltas, no forks unless shared constraints diverge with functional consequence. No territory analog → absorb as Complementary Delta, don't force a fork. Mode B with no clear friction → say so plainly, don't fabricate. Fork with equal merit → surface both, request judgment, don't default.

## Not
Not a diff tool, version control, formatter, or summarizer. Goal is never a longer document — it's a more friction-resistant one.

## Reference files
`references/report-template.md` (Fusion Report structure), `references/provenance-format.md` (provenance markup) — pull from these, don't reconstruct from memory.
