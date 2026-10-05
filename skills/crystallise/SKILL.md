---
name: crystallise
description: Captures the cognitive arc of a completed exploratory session — the initial confusion, the friction points dissolved, and the understanding reached — and renders it as a shareable SVG visual. Invoke this skill with /crystallise at the end of any session where a genuine breakthrough, resolution, or framework emerged from back-and-forth dialogue. Trigger on phrases like "make this shareable", "summarise what we figured out", "crystallise this session", "I want to share this with a friend", "turn this into a visual", "what did we actually solve here". Do NOT trigger automatically — this skill requires intentional invocation at a moment of genuine resolution.
---

# Crystallise — Session Arc to Shareable SVG

Transforms a completed session into one shareable SVG readable by a third party with zero context — a transmission artifact, not a session log.

## Reading the arc
Scan the conversation for: **entry state** (earliest message revealing the confusion/mental model that gets corrected), **friction points** (moments a distinction was drawn, a wrong layer identified, a fused concept separated — the pivots), **resolution** (the message where it clicked — "yes exactly," or a forward-looking question from new understanding), **output** (what was built/decided/named). Name each friction point in 3-5 words — distil, never quote verbatim.

## SVG structure (vertical arc, top to bottom)
```
Session title (distilled) + subtitle (what was solved)
        ↓
ENTRY STATE — the initial confusion/wrong layer
        ↓
[Friction 1] [Friction 2] [Friction 3]   (horizontal row, max 4, min 1)
        ↓
RESOLUTION — the understanding that emerged
        ↓
OUTPUT — what was built/decided/named
```

## Visual contract (exact — do not vary)
- ViewBox `0 0 680 H`, H calculated from content + 40px buffer. Background transparent.
- Color by layer: entry `c-coral` · friction `c-amber` · resolution `c-teal` · output `c-purple` · header `c-gray`.
- Arrows: `class="arr" marker-end="url(#arrow)"`. Text: `class="th"` titles, `class="ts"` subtitles.
- Friction row: max 4 nodes — group minor ones and name the group if more.
- Every node clickable via `sendPrompt()` — clicking a friction point asks Claude to expand it.

## Label tone
Engrave-on-stone distilled, never full sentences, never quotes, never the word "understanding" (show it through structure). E.g. entry: "Skills and project instructions fused as one layer." Friction: "Ambient rule vs callable contract." Resolution: "Project instructions govern when. Skills carry what." Output: "Crystallise skill forged."

## Attribution
`meet.venkat1@gmail.com`, small `class="ts"`, bottom-right, muted, no link (shareable artifact, not an engine).

## After rendering
One prose paragraph below the SVG (outside it), 3 sentences max, plain language — the caption a friend reads before the diagram.

## Edge cases
No clear resolution → don't invoke; say the session's still open, ask what would resolve it. Purely technical, no cognitive friction → simpler two-layer arc (entry → output), labeled an execution arc not a discovery arc. Multiple breakthroughs → render the most significant, mention others exist in the caption. Specific audience named → adjust label vocabulary to it, ask if unsure.

## Build sequence
Scan arc → distil labels (before drafting SVG) → calculate layout → render SVG per visual contract → add prose caption.
