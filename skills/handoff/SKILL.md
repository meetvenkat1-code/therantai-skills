---
name: handoff
description: Compresses the current session into a minimal markdown context block designed to be pasted as the opening message of a new chat session, preserving resolved understandings, active decisions, pending threads, and established contracts — without SVG overhead or full conversation replay. Invoke with /handoff when a session is long, token-heavy, or complete enough to continue in a new chat. Trigger on phrases like "compress this session", "transfer context", "continue in new chat", "handoff", "carry this forward", "I want to start a new session from here", "too many tokens". Do NOT trigger automatically — invoke only when the person is ready to move to a new session.
---

# Handoff — Session Context Compression

One tight markdown block, under 300 words, that a new session opens directly from resolved understanding — not the exploratory arc. Transfer companion to `/crystallise` (that shares outward; this carries forward).

## Extract
1. **Session topic** — one line.
2. **Resolved understandings** — 2-4 bullets, max, each the resolution not the journey.
3. **Active build decisions** — artifacts built/decided, with status (forged/installed/pending).
4. **Established contracts** — standing rules locked in this session that persist forward.
5. **Session ritual context** — if part of a named pipeline (Ignition/Forge/Harvest/Audit), which stage was active at close and what's next; if harvest was partial, which stages completed.
6. **Pending threads** — 1-3 items max, omit section if none.
7. **Suggested opening prompt** — one sentence to open the new session with.

## Output
```
## Handoff — [Session Topic]
[Date · Time]

### Resolved
- [ ]

### Built this session
- [artifact] — [status]

### Contracts in force
- [ ]

### Pipeline context
- [pipeline] — [stage at close] → next: [stage]

### Pending
- [ ]

### Open with
"[suggested opening prompt]"
```

## Compression rules
No back-and-forth, only outcomes. No friction narrative (that's /crystallise). No code/SVG/heavy formatting inside the block. Every bullet under 15 words — if a resolution needs more, it's not distilled yet. Total under 300 words. Omit empty sections.

## Not
Not a readable session summary — a machine-readable seed. Not a /crystallise replacement. Not a memory substitute — memory handles persistent facts, handoff handles session-specific decisions/pending work.

## After rendering
One plain-prose line below the block: "Paste this block as your first message in the new session." Nothing else.

## Edge cases
Still mid-exploration, no resolution → say it can't hand off cleanly yet; suggest continuing or /crystallise for the open arc. Multiple unrelated threads → one block per thread, labeled, person picks. Handoff to a specific project/engine → add a one-line preamble naming it to the opening prompt.
