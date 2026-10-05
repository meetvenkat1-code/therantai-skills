---
name: spinal-column
description: "Forges a dense, paste-ready system prompt from raw intuition fragments — the mid-thought residue of a building process, not a clean idea. Fast inward collapse: no expansion, no stations, no scaffolding. One mandatory clarification (what transforms in the person who uses this?) fired only when the fragments don't already carry it. The complement of core-extractor — core-extractor strips a built artifact to its spine; spinal-column forges a spine from fragments that have no artifact yet. Invoke with /spinal-column or phrases like 'forge a spine from this', 'turn this into a system prompt', 'I have fragments, give me a prompt', 'extract the system prompt from this idea', 'compress this into a prompt', 'spinal-column this'. Also triggers when the user drops mid-thought fragments and asks for a system prompt without requesting a full engine build."
metadata:
  triggers:
    - "/spinal-column"
    - "forge a spine from this"
    - "turn this into a system prompt"
    - "I have fragments, give me a prompt"
    - "compress this into a prompt"
    - "spinal-column this"
  scope: global
  version: "1.0"
  date: "2026-06-17"
  author: meet.venkat1@gmail.com
---

# SPINAL COLUMN

Fires on raw intuition fragments — thinking-while-making residue, carrying operational heat but no vessel — presented to forge a system prompt, not build an engine. Collapse inward, never expand. No stations, no architecture/layout/UI questions.

**Principle:** the system prompt is the true engine; everything else (HTML, API, rendering) is vessel. Fragments already contain the identity of what's being made, scattered and implicit. This skill hears it through the noise and compresses to one instruction that could make any capable model *become* the thing. One move, no scaffolding.

## The single gate
Scan fragments for **the transformation** — not what the engine does, what changes in the person who uses it. Visible/implied in fragments → skip, compress directly. Absent → fire the one question: *"What is different about the person after this runs?"* Wait, then compress. No other questions — wanting to ask about architecture/features/layout/interaction is an expansion move; this skill doesn't expand.

## Compression protocol
1. **Hear the identity** — read fragments for what they *are*, not what they describe. Listen for: the single operation (one verb/move, not a feature list); the stance (oracle/mirror/surgeon/companion/adversary/witness — how it relates to the user); the refusal (what it won't do, the failure mode it prevents — often the sharpest identity signal); the transformation (from fragments or the gate answer).
2. **Collapse to spine** — IDENTITY (1-3 sentences: name if present + operation fused with stance) / METHOD (internal cognitive procedure, dense, imperative, no hedging) / OUTPUT CONTRACT (what surfaces, what's suppressed — never explanations where oracles are needed, summaries where images are needed, options where commitments are needed) / CONSTRAINTS (absolute prohibitions, not suggestions) / TRANSFORMATION (dissolved into the other sections as gravity — never its own labeled section, present everywhere, visible nowhere).
3. **Density check** — paste-ready (drops in with zero editing, strip anything referencing a nonexistent UI/provider/format)? Identity-bearing (makes the model *become*, not merely *do* — a task-description read means reforge until a posture shift is felt)? Dense (every sentence load-bearing; removable sentences get removed)?

## Output
System prompt only. No preamble, no "here's your prompt," no fragment summary, no architectural commentary. Lands clean, as if always existing. Exception: if fragments named the engine, surface it as a single header line — never invent a name.

## Relations
Intuition-forge is the full eight-station ceremonial pipeline (expands progressively; use for the full build). Core-extractor is the inverse (strips a *built* artifact to spine; spinal-column forges from *unbuilt* fragments) — both converge on the same portable-spine output. Distill climbs higher still, past the operation to the smallest generative principle — optionally run on a spinal-column output to compress further.
```
FORMLESS INPUT (fragments) → spinal-column ┐
BUILT INPUT (artifact/code) → core-extractor ┘→ PORTABLE SPINE → prompt library / new engine → distill (optional)
```

## Scope
Pure cognitive operation, domain-agnostic. Global.
