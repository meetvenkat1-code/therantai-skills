---
name: intuition-forge
description: "Transforms raw intuition into standalone HTML engines via eight stations: Seed, Intention, Identity, Architecture, Interaction, System Mandate, Stress Test, Artifact."
---

# Intuition Forge

Eight-station pipeline: raw intuition → rendered standalone HTML engine. No station skippable; each feeds the next.

```
Seed → Intention Field → Identity → Architecture → Interaction Schema → System Mandate → Stress Test → Artifact
```

## Core principles
**Hybrid-generative** — Claude generates a first-pass per station, user confirms/edits/reshapes before advancing (approval, edit, or "next"/"go"/"yes"). Corrections regenerate that station's output before moving on.
**Cumulative context** — every confirmed output carries forward; Station 8 has access to everything.
**Backward looping** — user can jump to any prior station by name; revising it invalidates and regenerates everything downstream.
**No premature rendering** — zero code before Station 8; Stations 1-7 are pure conceptual/structural work.
**Station announcements** — name + one-two sentences on what it does, at the start of each.

## Station 1 — Seed
Capture raw intuition unedited. Ask for it messy/fragmented if not already given; don't re-ask if already stated. Produce a **Seed Statement** (2-4 sentences, mirror not interpretation, in the user's own register). Advance on confirm/edit.

## Station 2 — Intention Field
Name the transformation the thing produces — not what it is, what it *does to* someone using it ("before this, the user was ___; after, the user is ___"). Produce **Intention Field Statement** (1-3 sentences) + optional **Shadow Statement** (what it explicitly refuses to be). Advance on confirm/reshape.

## Station 3 — Identity
Naming is an ontological commitment that constrains everything downstream. Produce: **Name** (2-4 distinct candidates, each encoding character not just function), **Essence Statement** ("It is a ___ that ___"), **Temperament** (fast/slow, dense/spacious, generative/analytical, surgical/exploratory, warm/austere). These become architectural constraints, not cosmetics. Advance on name selection + confirm.

## Station 4 — Conceptual Architecture
Internal topology — chambers/modules/layers, their relationships (sequential/parallel/nested/branching), what flows between them, where boundaries sit. Topological, not visual (UI is Station 5). Produce an **Architecture Map** in structured prose, noting which parts are fixed/toggleable/variable. Advance on confirm/reshape.

## Station 5 — Interaction Schema
The surface topology, distinct from Station 4's internal one: entry (single/multi-field/seed+selectors), navigation (tabs/scroll/switchboard/auto-routing), what's seen at each stage, available controls, primary display mode. Produce an **Interaction Schema** naming each interface element + the **primary user action**, made effortless. Key principle: architecture and interaction are deliberately separable — swap one without restructuring the other. Advance on confirm/reshape.

## Station 6 — System Mandate
Compress Architecture + Interaction Schema into the operational core — three components:
1. **System Prompt** — the engine's soul: what it is, how it thinks, what it produces, what it refuses. Dense, precise, complete; encodes Intention as purpose, Identity as voice, Architecture as internal logic, Interaction Schema as user-awareness.
2. **Input Schema** — fields, types, required/optional, constraints.
3. **Output Template** — sections, order, format, length/density/tone rules.

Two mandatory constraints in every System Prompt: a symbolic/oracular final output must never explain or analyze itself — must land as pure image; and transitions between sections must read as deepening, not topic change. Production-ready, copy-pasteable. Advance on confirm/reshape.

## Station 7 — Stress Test
Generate 3-5 test seeds (obvious, edge, adversarial) — user may edit the set. Run the System Prompt against each (Claude roleplays the engine), present outputs for evaluation against: does it honor the Intention? the Architecture? the Output Template? any failure modes? On failure, name which station it traces to (usually 6, sometimes 4) and recommend revisiting — downstream invalidates on re-entry. Advance on satisfactory outputs.

## Station 8 — Artifact Rendering
Single complete runnable HTML file: all CSS/JS inline, Google Fonts via link tags, three-font system (display/body/UI — Syne/Source Serif 4/Inter or as specified), gear-icon config drawer with localStorage keys, multi-provider (Groq default llama-3.3-70b-versatile, OpenAI, Gemini, LMStudio), Station 6's System Prompt embedded as the soul, Station 6's Input/Output Schema driving interface and display, Station 5's Interaction Schema governing nav/layout/controls, mobile-responsive, dark theme default. Identity should be visible in typography/color/spacing/atmosphere — a tool with a point of view, not a generic API wrapper. Deliver the file + a brief human-readable summary (name, intention, core interaction pattern).

## Edge cases
Fully-formed idea, not raw intuition → still run all eight; the value is progressive crystallization, not starting from chaos. Wants React not HTML → Station 8 adapts, upstream unchanged. Wants to skip Station 7 → gently discourage ("untested prompt = looks right, thinks wrong"), proceed if they insist, note the skip. Wants to start at Station 4+ → accept, but ask for compressed upstream context (Seed/Intention/Identity) so downstream coheres.

**Spine-first entry** (arriving with a completed spine from /spinal-column, /ossify, /core-extractor): Stations 1-3 and part of 6 are pre-resolved. Announce "Spine-first mode — Stations 1-3 resolved. Entering at Station 4." Extract: IDENTITY→Station 3, METHOD→Station 2, OUTPUT CONTRACT+CONSTRAINTS→pre-loaded Station 6 material. Open Station 4 immediately (spine names the operation, Station 4 gives it topology). Continue 5→6→7→8 normally; at 6, the spine IS the first System Prompt draft, refined with Architecture/Interaction layered in — thickened, not discarded. Spine identity is immutable — architecture/interaction may add vessel but never contradict its refusals/constraints. Trigger: pasted spine + "build this"/"take this to HTML"/"forge this"/"/intuition-forge from here", detected via IDENTITY/METHOD/OUTPUT CONTRACT/CONSTRAINTS sections.
