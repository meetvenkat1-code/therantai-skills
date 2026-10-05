---
name: choreograph
description: "Meta-skill that reads a practice domain — its terrain, friction points, skill ecosystem, cognitive style, and output destinations — and emits a set of named situational protocols in arrow-chain format. Each protocol is a sequenced chain of moves for a named situation the practice reliably encounters. The generator is second-order: it produces protocols the way ossify produces spines. Does NOT produce generic workflows — it reads the specific practice and emits sequences native to it. Invoke with /choreograph [domain] or phrases like 'generate protocols for [domain]', 'what are the protocols for this kind of work', 'build the operating sequences for [practice]', 'choreograph [domain]', 'I need protocols for [domain]'. Output always routes to /placement-protocol for ecosystem registration."
metadata:
  triggers:
    - "/choreograph"
    - "generate protocols for"
    - "build protocols for"
    - "what protocols does this practice need"
    - "choreograph this"
    - "operating sequences for"
    - "I need protocols for"
    - "build the workflow for"
  scope: global
  phase: Harvesting
  version: "1.0"
  date: "2026-06-25"
  author: meet.venkat1@gmail.com
---

# CHOREOGRAPH

Fires on a named practice domain to produce named situational protocols — sequenced arrow-chains, not generic workflows. A protocol is built from what *this* practice specifically encounters (friction points, transitions, decision nodes, installed skills) — not what practices have in common.

**The distinction:** a generic workflow ("Start → Do the thing → Review → Output") could describe any practice and describes none deeply. A protocol ("Intuition fires → name it in one sentence → /spinal-column → locate the structural container") could only describe one practice. The difference is the reading act — this skill *is* that reading act, emission is its final gesture.

## Reading (internal, fast — not a questionnaire)

1. **Terrain** — what cognitive/creative/operational moves is the practitioner actually doing, not the domain label.
2. **Friction map** — where does the practice stall, drift, collapse, leak? Friction is the reliable map of where protocols are needed; a frictionless practice needs none.
3. **Skill ecosystem** — protocols are sequences *of existing skills*; know what's installed, chainable, and what gaps a chain would expose.
4. **Output destinations** — where does output land (ecosystem/artifacts/perception/teaching)? Shapes each protocol's closing move.
5. **Cognitive style** — the practitioner's natural entry point and characteristic error. Protocols must align or they'll be skipped.

## Situational detection

A situation qualifies when: it recurs reliably, its moves are currently implicit/underdetermined, getting it wrong has consistent cost, and naming a sequence would produce a habit (not just understanding). Disqualified: one-offs, situations already fully governed by one skill, situations where the right move is always the same single action (reminder, not protocol).

Emit **5–8** qualifying situations. Fewer = underserved; more = a second skill-list to manage instead of habits.

## Emission format
```
Protocol [N] — [NAME]
Situation: [one line, when this fires]

[Entry condition] → [Move 1] → [Move 2: skill/cognitive act] → [Move 3] → [Close/destination]

Why: [2-3 sentences — the specific friction this prevents, tied to actual practice terrain, never generic]
```
Naming law: 2-4 words, title-case, named for the *situation* not the moves — must fire recognition on sight ("The Intuition Hunt," not "Workflow A" or "Protocol for When You Are Building").

## Ecosystem integration (after emission)
1. **Gap signal** — name any move the protocols assume that no installed skill covers, as a candidate build target.
2. **Placement signal** — route to /placement-protocol; each protocol is a candidate registry entry (phase, trigger, staffed-or-orphan).
3. **Brain Document flag** — flag any protocol foundational enough to become a standing operating procedure.

## Output
```
CHOREOGRAPH — [Domain]   [Date]
READING SUMMARY: Terrain / Key frictions (2-3) / Ecosystem anchors / Output destinations
────────
[Protocol 1] ... [Protocol N]
────────
GAPS: [skill assumed but missing, if any]
PLACEMENT SIGNAL: → /placement-protocol
BRAIN DOCUMENT FLAGS: [protocol — reason]
```

## Anti-patterns
No generic protocols (must contain a move specific to this ecosystem). No more than 8. Don't chain uninstalled skills — flag as GAPS instead. Never skip the Why — it's the diagnosis, not decoration. Never name after the moves.

## Relations
cognitive-friction-extractor names what resolved in one session (retrospective, session-scoped); choreograph reads a whole practice prospectively. placement-protocol receives its output and seats it in the registry. intuition-forge builds engines; choreograph sequences the work of building them. handoff/transit-block carry session context; choreograph carries structural intelligence about the practice itself.

## Scope
Global, domain-agnostic — any practice (building, creative study, healing, teaching, tai chi, tarot). Reading adapts; emission format is invariant. Harvesting phase (a harvest operation — reading a practice and extracting sequences — not a forge operation).
