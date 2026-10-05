---
name: forge-transit
description: Engine-specific session capture skill for transit into the Exploration-Hybrid HTML Engine Architect project. On invocation, scans the session for engine-building signals, fills ENGINE DIMENSIONS from the conversation record using exact QUICK REFERENCE vocabulary, marks unresolved fields as [UNKNOWN] — never fabricates. Emits a pre-filled block, not a blank template. Invoke with /forge-transit, "engine handoff", "capture for the forge", "transit to forge", "I'm bringing this to the engine project", "forge context capture". Invoke at the end of any external session where an engine was being designed, explored, or architecturally specified. Stacks with /transit-block — transit-block first, forge-transit second. The receiving project reads transit-block for session architecture, forge-transit for engine dimensions, then asks only what the combined block leaves unresolved before FORGE IT.
---

# forge-transit — Engine Context Capture for the Forge

Engine-specific outbound ritual. Reads first, then fills every ENGINE DIMENSIONS field extractable from the session, in the exact project vocabulary — never fabricates, marks the rest `[UNKNOWN]`. Stacks with `/transit-block`, never replaces it: **transit-block first, forge-transit second**.

**Trigger:** `/forge-transit`, "engine handoff", "capture for the forge", "transit to forge", "I'm bringing this to the engine project", "close and bring to forge."

## Protocol
1. **Scan for engine signals** — Zone A/B/C references, UI Contract constraint numbers, taxonomy terms, hek_ keys/provider discussion, FORGE IT/EXPLORATION mentions, I/O shape or canvas decisions, a forged spine. No signals → don't emit; tell the person forge-transit isn't needed here.
2. **Fill honestly** — exact QUICK REFERENCE field vocabulary, no paraphrasing. Unresolved → `[UNKNOWN]`. Cognitive identity declaration unresolved → `[UNKNOWN]` (hard gate, UI Contract Constraint 19). Portable spine: paste verbatim if forged; `SEE TRANSIT-BLOCK` if transit-block already carries it; `NONE` if not forged.
3. **Emit** — single markdown code fence, stacked below transit-block's output, separated by a horizontal rule.

## Output format
```
## FORGE-TRANSIT
Session: [one-line engine session identity]   Date: [date]   Source: [project/general chat]
Destination: Exploration-Hybrid HTML Engine Architect

### ENGINE DIMENSIONS
Engine name (Zone A): [name or UNKNOWN]
Engine type from taxonomy: [Cognitive Pipeline / Topology Mapper / Lens Interpreter / Pattern Library / Learning Engine / Prompt Builder / Text Transformer / Hook Generator / Meta-Intent Engine — or UNKNOWN]
Cognitive identity declaration: [This engine Xs Y so that Z can T — or UNKNOWN]
Input shape: [specific — or UNKNOWN]
Output shape: [specific — or UNKNOWN]
Pipeline shape: [Single-shot / Multi-stage sequential — or UNKNOWN]
Provider default deviation: [STANDARD — or named deviation + reason]
hek_ storage needs beyond provider keys: [list — or NONE]
UI Contract conflict flags: [constraint numbers + conflicts — or NONE FLAGGED]
Banned list violations to flag: [named — or NONE]

### WHAT EXPLORATION MUST RESOLVE BEFORE FORGE IT
- [open question, or NONE]

### PORTABLE SPINE
[verbatim — or SEE TRANSIT-BLOCK — or NONE]
```

## Field definitions
Engine name = Zone A public identity. Engine type = exact taxonomy match (nine types); UNKNOWN triggers taxonomy matching downstream. Cognitive identity = `This engine [verb]s [what] so that [who] can [transformation]` — hard gate, must resolve before FORGE IT. Input/output shape = specific description of Zone B input / canvas render, not generic. Pipeline shape = single-shot vs. multi-stage. Provider deviation = STANDARD unless engine deviates from context-aware default (artifact→Claude Native / standalone→Groq). hek_ needs = localStorage keys beyond standard provider keys. UI Contract flags = specific constraint numbers at risk. Banned-list flags = `62ch constraints`, fixed-width containers, `<form>` tags, non-streaming calls, CDN imports, `display:none` on event-wired elements, sticky-inside-scroll on interactive elements, raw clipboard calls.

## Stacking order
```
## TRANSIT-BLOCK
[universal session context]
---
## FORGE-TRANSIT
[engine dimensions]
```
Paste both as one opening message; receiving session reads universal context first, engine dimensions second.

## Receiving session behavior
Read both blocks → state what's already resolved (never re-ask) → ask only UNKNOWN fields, one at a time → FORGE IT releases normally once resolved.

## Edge cases
No engine signals → don't emit, use transit-block alone. Spine not forged → `NONE`; receiving session runs /spinal-column or /ossify first. Cognitive identity undeclared → `UNKNOWN`, hard gate. Multiple engine concepts → one block per concept, labeled, person chooses which to bring first. Engine type unclear → `UNKNOWN`, taxonomy matching runs downstream.
