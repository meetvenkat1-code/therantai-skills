---
name: registry-delta-exporter
description: >
  Extracts and formats only the new or meaningfully changed entries from the 
  skill registry since the last export. Produces a clean, structured delta 
  optimized for transfer to another instance (such as Claude) where it can be 
  intelligently merged. Supports the principle of thickening over duplication 
  by surfacing additive changes rather than full registry dumps. Works best 
  after a sweep has been performed. Invoke with "export delta", "show registry 
  delta", "give me the delta", or similar phrases.
metadata:
  triggers:
    - export delta
    - show registry delta
    - give me the delta
    - export new changes
    - export registry changes
    - show what changed in registry
  scope: global
  phase: Harvesting
  version: "1.0"
  date: "2026-06-29"
  author: meet.venkat1@gmail.com
---

# Registry Delta Exporter

A synchronization/transfer tool, not an extraction tool — operates on the registry *after* work is placed and swept, not on raw session friction. Solves: moving only what's new between platforms (e.g. Grok and Claude) without noise or duplication — Thicken-before-Proliferate applied cross-platform, so the receiving side merges intelligently instead of blindly replacing.

## Behavior
1. **Establish reference point** — last export state, via stored marker or explicit input ("since yesterday").
2. **Compare and filter** — scan `skill-registry.md` for entries newly added or significantly changed (new constraints/triggers/notes/structural updates) since the reference point.
3. **Format the delta** — clean, structured, copy-paste ready.
4. **Add context** — header with date, source platform, one-line summary, notes for the receiver.
5. **Respect boundaries** — exclude minor formatting changes or non-functional edits. Signal, not noise.

## Output
```markdown
## Registry Delta Export
**Date:** [YYYY-MM-DD]  **Source:** [Grok/Claude]  **Summary:** [one line]

### New Entries:
- [entry]

### Thickened / Updated Entries:
- [entry — what changed]

### Notes for Receiving Side:
- Merge intelligently; prefer thickening over replacement.
```
Optimized for the receiving instance to process through `intake` or `placement-protocol`.

## Relations
Harvest-pipeline — run sweep first; this exports from the registry, not staging. Cognitive-friction-extractor — different layer (raw session friction vs. already-processed registry state). Placement-protocol/intake — receiving-side integration points for incoming deltas. Moult — complementary (this moves changes forward, moult cleans up redundancy over time).

## Anti-patterns
Don't export the full registry for a small delta. Don't include non-functional formatting changes. Don't run on unstaged work — sweep first. Don't treat as an extractor replacement. Don't make output verbose — clean transfer, not documentation.

## Scope
Meta-skill, Harvesting phase — supports healthy cross-platform ecosystem evolution, not new domain capability. Global, domain-agnostic.
