---
name: brain-doc-sync
description: The third command in the standing capture/resolve/sync triad. Refreshes therantai-brain.md — the portable narrative wrapper — to reflect the current state of skill-registry.md. Deliberately separate from "sweep" so every registry merge doesn't pay the cost of re-rendering a full narrative document; invoke only when the portable version is actually about to be needed (opening a browser session without MCP, cross-account handoff). Invoke with "sync", /sync, "sync brain doc", "update brain document", "refresh brain doc".
triggers:
  - sync
  - /sync
  - sync brain doc
  - update brain document
  - refresh brain doc
scope: global
version: 1.0
date: 2026-07-04
author: meet.venkat1@gmail.com
brain_doc: E:\Desktop Backups\claude_brain\therantai-brain.md
registry: E:\Desktop Backups\claude_brain\skill-registry.md
---

# BRAIN-DOC-SYNC

## Triad
```
log this  → capture (session-scoped, disk write to friction-log.md)
sweep     → resolve (batch placement, friction-log.md → skill-registry.md)
sync      → transmit (registry → therantai-brain.md) — this skill
```
Sync fires only when the portable narrative version is about to matter: no-MCP session, cross-account handoff, or reading the registry as prose rather than rows.

**Why separate from sweep:** the brain doc is a full narrative rewrite — real token weight. Most sweeps aren't followed by a handoff/browser session. Taxing every merge with a rewrite it usually doesn't need is negative-yield; keep it deliberate.

## Behavior
1. Read `skill-registry.md` in full (registry table, Graveyard, Unplaced, Governing Architecture, Token Registry).
2. Read current `therantai-brain.md`.
3. Rewrite brain-doc sections to match registry's present state — in portable prose, a briefing not a database dump.
4. One-directional: registry → brain doc, never touches registry or friction-log.
5. Confirm: sections rewritten, skills added/removed/shed since last sync, new sync date.

Sync never auto-runs after sweep — say "sweep, then sync" explicitly if both are wanted.

## Output
```
SYNC — [date]
CHANGES SINCE LAST SYNC:
  + [added]  − [shed]  ~ [structural changes]
✓ Synced — [n] sections updated. Current as of [date].
```

*Last of harvest-pipeline's five original stages (extract/place/stage/sweep/sync) to receive an independent home; harvest-pipeline itself was shed via apoptosis 2026-07-04.*
