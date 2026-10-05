---
name: transit-block
description: Universal session capture skill — scans the current session, fills what it can, and emits a paste-ready context block that carries resolved understanding, decisions, rejections, pending threads, and contracts to any destination. Works from any project, any general chat, any tool. Destination-agnostic. Invoke with /transit-block, "capture this session", "universal handoff", "carry this forward", "I need to transfer context", "session capture", "close and transit". Does NOT trigger automatically — invoke only when ready to close or transit a session. On invocation, Claude reads the session first, fills every field it can from the conversation record, marks genuinely unresolved fields as [UNKNOWN] — never fabricates. Emits a pre-filled block, not a blank template. Distinct from /handoff (which compresses within the ecosystem) — transit-block is the outbound capture ritual for cross-boundary travel.
---

# transit-block — Universal Session Capture

Universal outbound ritual: reads the full session, fills what it can, emits one paste-ready block — a machine-readable seed a receiving session *starts from*, not a summary it reconstructs from.

**Distinct from `/handoff`:** handoff compresses within the ecosystem for session-to-session continuity; transit-block is destination-agnostic, built for cross-boundary travel including outside the ecosystem entirely.

## Execution
1. **Scan** the full conversation for: what was settled and why (RESOLVED), decisions that must hold (DECIDED), what was considered and cut (REJECTED), what remains open (PENDING), constraints/agreements established (CONTRACTS), the single most important thing (THE ONE THING), any spine forged/referenced (PORTABLE SPINE), source and destination context.
2. **Fill honestly** — every extractable field; genuinely unresolved → `[UNKNOWN]`, never fabricated. THE ONE THING must compress to one sentence — if it won't compress, it isn't found yet. PORTABLE SPINE pastes verbatim, or `NONE`. Omit empty sections except THE ONE THING (always present).
3. **Emit** — single markdown fence, no preamble/postamble, followed by one plain line below it.

## Output
```
## TRANSIT-BLOCK
Session: [one-line identity]   Date: [date]
Source: [project/chat/tool]   Destination: [inferred, or OPEN]

### RESOLVED
- [resolution] — because [reason]

### DECIDED
- [decision that must not be re-litigated]

### REJECTED
- [alternative] — killed by [reasoning]

### PENDING
- [open thread the receiving session must handle first]

### CONTRACTS
- [standing rule that must persist]

### THE ONE THING
[single sentence — the minimum viable transfer unit]

### PORTABLE SPINE
[verbatim, or NONE]
```

## Filling rules
Session/Date/Source/Destination: one line each, infer or OPEN. RESOLVED: only genuinely settled, max 5. DECIDED: choices not to be re-opened, max 5. REJECTED: explicitly cut only, with the killing reason, max 4. PENDING: must-address-first items, max 3. CONTRACTS: carry-forward rules, max 4. THE ONE THING: always present, one sentence. PORTABLE SPINE: direct paste, never paraphrased.

## Compression rules
Outcomes only, no back-and-forth. No code/SVG/heavy formatting inside the block. Bullets under 20 words. Total under 400 words. Pasteable as-is, no editing needed.

## After rendering
One line below the fence: "Paste this block as your first message in the receiving session." Nothing else.

## Edge cases
No resolutions yet → say the session hasn't settled enough to transit cleanly; suggest continuing, or `/crystallise` for the open arc instead. Multiple unrelated threads → one block per thread, labeled, person chooses. Destination is the Exploration-Hybrid Engine Architect project → stack `/forge-transit` directly below, separated by a horizontal rule (transit-block first, forge-transit second). Destination unknown → leave OPEN.
