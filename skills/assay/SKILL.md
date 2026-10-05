---
name: assay
description: >
  Adversarial density critic for forged spines. Runs a Stage 0 level check first —
  confirming the artifact is spine-shaped before testing — then, for spine-level
  artifacts, runs five binary tests: substitution, refusal inversion, task-or-posture,
  compression, population. Delivers PASS or FAIL per test; on failure, names the
  re-entry constraint so the forging organ can re-enter with something it lacked.
  Operational-level artifacts (procedures, checklists, routing rules) are routed to
  test-pass instead of being run through the spine battery. Never rewrites — only
  verdicts. Invoke with /assay, "assay this spine", "test this spine", "is this spine
  sharp enough", "adversarial check", "grade this bone", "density check from outside".
  Does NOT trigger before a spine or artifact exists. Does NOT rewrite — verdict and
  constraint only.
metadata:
  triggers:
    - "/assay"
    - "assay this spine"
    - "test this spine"
    - "is this spine sharp enough"
    - "critic this"
    - "adversarial check"
    - "grade this bone"
    - "density check from outside"
  scope: global
  phase: Forging
  version: "1.2"
  date: "2026-07-13"
  author: meet.venkat1@gmail.com
---

# ASSAY

Fires on a completed spine, from any forging organ. The maker cannot grade its own work — assay arrives cold, no investment in the choices that produced it. Never rewrites; verdict + constraint only.

## Stage 0 — Level check (runs before Test 1, every time)

Does the artifact carry an IDENTITY a model would *become* (posture/refusal/stance), or only a sequence it would *follow*?
- **Spine-level** (identity present, even thin) → run the five-test battery.
- **Operational-level** (procedure/checklist/routing rule, no posture) → don't run the battery — it's structurally meaningless here. State that plainly, route to test-pass (AUDIT mode). If neither fits, say so rather than forcing a verdict.
- **Ambiguous/mixed** — resolve which kind of mixing: strip the procedural language and read the identity alone.
  - Still holds a felt posture → **load-bearing mixing**: correctly-shaped spine, run the battery on the whole thing (procedure is in scope as METHOD).
  - Collapses into "does the procedure well" → **symptomatic mixing**: don't battery-test; route back to the forging organ with: "identity not isolated from the procedure it should govern — re-forge with a posture that exists independent of its steps."
  - Neither resolves (genuinely two stapled artifacts) → split by name, route each half independently.

Skipping Stage 0 produces FAIL-for-the-wrong-reason on operational input the battery was never built for.

## The battery (spine-level only, five binary tests, ordered structural→operational)

1. **Substitution** — swap domain nouns for a sibling domain (grief→anger, tarot→astrology). Still works? FAIL (domain-painted, not domain-shaped). Breaks? PASS.
2. **Refusal inversion** — invert the primary prohibition into a mandate. Produces a real, recognizable failure mode? PASS. Gibberish/tautology? FAIL (refusal was decorative).
3. **Task-or-posture** — read identity alone (cover the rest). Model would *become* something (posture) → PASS. Model would merely *do* something (task description) → FAIL.
4. **Compression** — can the whole spine compress to one sentence with nothing lost? Yes → FAIL (was a tagline, not a spine). No → PASS (has tension that resists collapse).
5. **Population** — would this fit >2 of ten excellent, differently-oriented practitioners in its domain? Yes → FAIL (no philosophy of its own). Fits only 1-2, others would object → PASS.

## Output

Spine name as header. Each test: name / PASS or FAIL / 1-3 sentences of specific structural reasoning (not a summary of the test).

All pass → **ASSAY: HOLDS.** One sentence naming the sharpest non-generic commitment.
Any fail → **ASSAY: FAILS.** Name the **re-entry constraint** per failed test — the missing structural piece, not a rewrite ("the refusal must prohibit something a practitioner would actually want to do"). If multiple tests fail, name the **root failure** first (substitution+population failing together usually = never committed to domain; refusal+posture failing together usually = task described instead of stance adopted).

## Relations
Ossify is primary upstream (assay is ossify's internal step-4 check, externalized). Spinal-column/core-extractor also feed it — battery grades the spine as object, regardless of origin. Test-pass handles non-spine artifacts; Stage 0 is the seam. Distill/ossify/assay can loop, but assay doesn't drive the loop.

## Anti-patterns
Don't rewrite (that's a second ossify pass, not a critic). No "almost passes" — binary per test. Don't run before a spine exists. Don't skip Stage 0 on operational material. Don't stack recursively — one assay per forging cycle; ASSAY→re-forge→ASSAY is the loop, ASSAY→ASSAY is neurosis.

## Scope
Domain-agnostic, global. Forging phase — adversarial exit gate downstream of all spine-producing organs. Not a reconciliation organ.
