---
skill: core-extractor
source_file: skills/core-extractor/SKILL.md
source_sha: fab88b6cc295d2cc663341e52f2b12c267bf0417719bd02fd92485da9d536475
---

# core-extractor (skill behavior, verbatim)

```skill:body
# CORE EXTRACTOR

Fires when an artifact/engine/code is presented to harvest its cognitive identity — not to summarize, debug, or walk line-by-line. **Principle:** every engine = vessel (HTML/CSS/routing/storage — disposable) + engine (system prompt carrying the cognitive identity — the thing worth keeping).

## Protocol
1. **Locate the spine** — find every system prompt/instruction block/hardcoded directive (`SYSTEM`, `INSTRUCTIONS`, `PLAYBOOK` constants, prompt-building functions). Identify the single cognitive operation it forces.
2. **Separate operation from plumbing** — load-bearing (stance, constraints, output form, forbidden failure mode) stays; plumbing (JSON formatting, API-specific instructions, UI wiring) strips. Preserve structural thinking-logic even when split across calls.
3. **Collapse multi-stage pipelines** — fold sequential AI calls (architect→executor→evaluator→loop) into one self-running instruction; each stage's contribution survives as internal procedure.
4. **Name what's lost** — if collapsing weakens anything (adversarial evaluator → gentler self-check, cross-model → single-instance), name it and add a compensating instruction.
5. **Reforge as portable** — clean standalone prompt: IDENTITY (the single operation) / OPERATING LOOP (staged internally if needed) / OUTPUT CONTRACT / CONSTRAINTS. Self-contained, no reference to original UI/provider/code — paste-ready.
6. **Surface the distillation** — one line: **Engine identity:** [phrase] · **Lost in translation:** [what weakened, or "nothing"].
7. **Route the output** — close with a routing receipt (never omit — a spine with no destination is a vessel without a future):
```
ROUTING RECEIPT
Destination: [SEED | SKILL | REFERENCE]
Reason: [one sentence]
→ SEED — feed into spinal-column as raw material for a new build cycle (wants to become a different engine)
→ SKILL — route to cognitive-friction-extractor as a candidate (reusable, ecosystem lacks it)
→ REFERENCE — archive as a standalone SKILL.md (complete, stable, install globally)
```

## Output
Reforged prompt + distillation line only. No code summary, no UI description, no preamble.

## Relation to distill
Distill climbs toward the regenerative seed (smallest principle that can *regenerate* a system). Core-extractor moves sideways — the operational spine that can *redeploy* a system, shedding vessel, keeping the full operation. Compose: core-extractor → portable spine → distill → regenerative principle.

## Scope
Domain-agnostic, global.
```
