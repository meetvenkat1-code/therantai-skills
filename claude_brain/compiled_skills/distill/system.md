---
skill: distill
source_file: skills/distill/SKILL.md
source_sha: a870ff9b3ab019d13c2b1fc6dd1b1a2df8e31b40639443618908e31e7c9aea2e
---

# distill (skill behavior, verbatim)

```skill:body
# Distill Skill

Upward traversal of the design hierarchy — not description, summary, or paraphrase. Reverses the generative process: instantiated form → the decisions/assumptions/philosophy that made it inevitable. Output: a **constitutional prompt** — the smallest generative seed that regenerates the system, referencing none of its surface features. Operative question throughout: *"What must they have believed for this architecture to emerge?"*

## Hierarchy (ascend, extracting at each level)
```
Feature/Implementation → Workflow/Module → Architecture → Framework/Pattern Language
→ Transformation Model (what it does to input) → Observer Model (mind it assumes)
→ Identity Assumptions (beliefs about user/world) → Governing Philosophy (deepest "why")
→ Invariant Core (the one principle everything needs) → Constitutional Prompt (OUTPUT)
```

## Protocol
1. **Ingest** — read fully, hold it. What kind of object is this, what transformation does it perform?
2. **Map the hierarchy** — one sentence per level: what it does / how structured / before-after transformation / what mind it assumes / what beliefs it embeds / the deepest conviction beneath those / the one principle whose removal collapses the whole.
3. **Synthesize the constitutional prompt** — states identity (what kind of thing, not its name), governing transformation, observer model, invariant constraint, generative directive (the instruction that lets any competent builder reconstruct it correctly). 150-300 words, short enough to hold in working memory — must generate architecture, not describe it. Write from three simultaneous postures: philosopher extracting a worldview, physicist finding the underlying law, systems theorist finding the generative source. Question is "what must they have believed," not "what did they build."
4. **Deliver** — Hierarchy Traversal (1-3 sentences/level) → Invariant Core (one bold sentence) → Constitutional Prompt (clearly demarcated).

## Register
ANALYTICAL — precise, unhurried, no padding, no performed profundity. Surgery, not poetry. The prompt itself may carry philosophical density only where load-bearing.

## Bundled reference
`references/invocation.md` — second-person invocation form; pull from file (don't reconstruct from memory) when handing this to a fresh model or embedding as a pipeline fragment.

## Anti-patterns
Don't summarize (stays at feature layer). Don't describe the organism — the prompt must read as DNA, not documentation. Don't produce a list of principles — one invariant core, one prompt. Don't let it grow — if it's growing, you're still at the architecture layer.

## Output routing (required)
```
ROUTING RECEIPT
Destination: [SEED | SKILL | REFERENCE]
Reason: [one sentence]
→ SEED — feed back into spinal-column as raw material (wants to become a new engine)
→ SKILL — route to cognitive-friction-extractor (reusable operation, ecosystem lacks it)
→ REFERENCE — archive as standalone SKILL.md (complete, stable, install globally)
```
Never omit — a distillation with no destination is a seed that dissolves.
```
