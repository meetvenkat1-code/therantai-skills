---
name: custom-gpt-package
description: "Converts a design idea, spine, or existing system prompt into a complete, copy-paste-ready ChatGPT Custom GPT package — Name, Description, Instructions (with a mandatory anti-drift block), Conversation Starters, and a Capabilities table. Takes a single input in one pass; does not interview unless the source material is genuinely missing something required to write the Instructions field. Invoke with /custom-gpt-package, 'build a custom GPT package', 'turn this into a custom GPT', 'package this for ChatGPT', 'custom GPT from this spine', or any request to render an existing prompt/idea/engine into ChatGPT's Custom GPT builder format."
metadata:
  triggers:
    - "/custom-gpt-package"
    - "build a custom GPT package"
    - "turn this into a custom GPT"
    - "package this for ChatGPT"
    - "custom GPT from this spine"
    - "make a custom GPT out of this"
    - "render this for the GPT builder"
  scope: global
  version: "1.0"
  date: "2026-07-02"
  author: meet.venkat1@gmail.com
---

# CUSTOM GPT PACKAGE

Fires when a design idea/spine/system prompt needs deploying as a ChatGPT Custom GPT — renders it into the five fields the builder requires, plus the anti-drift scaffolding ChatGPT specifically needs. Don't interview first — take reasonable defaults for missing details and note the assumption inline; ask only when there's no reasonable inference (no tone signal at all, no way to infer output caps).

**Why:** ChatGPT Custom GPTs drift in ways single-session engines don't — hedging, self-narration, unsolicited extras, format discipline relaxing by turn 30. A system prompt that works as an HTML engine's `system` param isn't drift-resistant in a long ChatGPT thread on its own. The anti-drift block is this skill's entire value-add — mandatory, every package.

## Output — five sections, always this order

1. **NAME** — short, matches actual function, not generic branding.
2. **DESCRIPTION** — one sentence: what it does, and what it explicitly does NOT do.
3. **INSTRUCTIONS**:
   - IDENTITY — role/function, one paragraph, does/doesn't.
   - INPUT HANDLING — valid input, min/max bounds, behavior at edges. Soft complexity ceilings carry forward as warned-not-blocked, not hard stops.
   - MODE SELECTION (only if source defines multiple modes) — default stated, switch-trigger language, rule for mid-thread mode-switch requests on already-discussed input.
   - TONE — derived from source's own voice, never generic "helpful assistant."
   - OUTPUT RULES — hard format caps pulled from source; if unspecified, infer from apparent purpose and state the assumption.
   - **ANTI-DRIFT BLOCK** (mandatory, numbered, framed as "does not relax as conversation lengthens"): no narrating reasoning; no unsolicited extras/follow-ups; no restating own instructions to the user; no exceeding format caps "to be more helpful"; no apologizing/padding refusals; no drifting into commentary outside the one job; one-sentence decline pattern for pushback requesting format abandonment; plain-prose lock (no headers/bullets/bold in actual output) unless source format requires structure.
4. **CONVERSATION STARTERS** — 3-4, concrete, from the actual domain, never placeholders.
5. **CAPABILITIES TABLE** — Web Browsing / Canvas / Image Generation / Code Interpreter / Actions, all default **Off**. Enable only if core function genuinely requires it (e.g. live-data fetch needs Browsing), stating which and why in one line — every enabled capability is a door the model can wander through instead of staying in its lane.

## Delivery
Whole package, one copy-paste-ready block, section headers intact, ready for the Configure tab. No preamble, no summary.

## Relations
Core-extractor/spinal-column produce the platform-agnostic spine. This skill is the downstream render — wraps that spine (or idea, or existing prompt) in the five-field structure + anti-drift hardening. Run core-extractor/spinal-column first if no spine exists; this skill once one does.
```
SPINE/IDEA/PROMPT → custom-gpt-package → NAME·DESCRIPTION·INSTRUCTIONS(anti-drift)·STARTERS·CAPABILITIES → paste into ChatGPT Configure
```

## Scope
Platform-specific (ChatGPT), domain-agnostic otherwise. Global.
