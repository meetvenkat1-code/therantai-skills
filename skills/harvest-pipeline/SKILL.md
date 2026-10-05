---
name: harvest-pipeline
description: "The self-executing closing chain for any Therantai session. Encodes the five-stage harvest sequence — extract, place, stage, sweep, sync — as a sequential pipeline with handoff prompts baked in, so the practitioner never navigates or recalls what comes next. Claude drives the chain; the practitioner only confirms each advance. Built-in pause architecture: at any stage the practitioner says 'defer' or 'park here' to freeze the chain at that point, log what completed, and hold the remaining stages as a named continuation resumable in the same or future session. The staging doc is a legitimate stopping point, not an incomplete run. Invoke with /harvest, 'close session', 'run harvest', 'end of session', 'harvest this session'. Light close: /harvest --light skips to staging only and defers the sweep and brain sync explicitly. After harvest completes, run /handoff if carrying forward to a new session — never before."
metadata:
  triggers:
    - "/harvest"
    - "/harvest --light"
    - "close session"
    - "run harvest"
    - "end of session"
    - "harvest this session"
    - "run the closing chain"
    - "session close"
    - "resume harvest"
  scope: global
  phase: Closing
  version: "1.1"
  date: "2026-06-28"
  author: meet.venkat1@gmail.com
---

# HARVEST PIPELINE

Ensures the session's resolved intelligence doesn't die in the practitioner's memory — the least reliable surface in the ecosystem, degrading silently (skills named but never placed, stale staging docs, diverging registries, frozen brain docs). Closing sequence knowledge belongs to the ecosystem, not the practitioner; the practitioner's job is to confirm and defer, nothing more. Discipline applied to sequence-memory is inconsistent; a pipeline is the same result every time.

## Read/write surface — local only
All reads/writes route through `claude_brain/` via Claude Desktop's local folder MCP — never Google Drive, no file ID minting, no Drive fallback. Canonical paths: `claude_brain/therantai-staging-placements.md` (staging), `claude_brain/skill-registry.md` (registry), `claude_brain/therantai-brain.md` (brain doc). All writes overwrite in place. If `claude_brain/` is inaccessible: name the gap, deliver in-session text, hold — never silently fall back to Drive.

## Pause architecture (first-class, not an edge case)
Three clean stations — `defer`/`park here`/`stop after this`:
- **After extraction** — nothing written yet. Resume → placement.
- **After staging** (most common stop) — written to staging doc as pending-merge; this is the buffer working correctly, not a broken run. Resume → sweep.
- **After registry sweep** — merged, staging cleared, only brain sync remains. Resume → sync.

**Light close** (`/harvest --light`) — runs extraction + staging only, explicitly defers sweep + sync. Not a shortcut — the correct invocation for minor sessions.

## The five stages

1. **Extract** (`/cognitive-friction-extractor`) — scan for resolved friction, press into CATEGORY/SKILL/CONSTRAINT/TRIGGER/ASCENT, thicken existing skills before proposing new. Handoff: "[n] friction(s) named. Say **place** or **defer**."
2. **Place** (`/placement-protocol`) — four structural questions per friction (scheme/arc-phase/trigger/staffed-or-orphan); autonomous mode by default inside the pipeline, no socratic questioning unless explicitly requested. Handoff: "[n] placed. Say **stage** or **defer**."
3. **Stage** — write placed skills to the staging doc as pending-merge entries (name, arc-phase, verdict, trigger, forging status). Read the doc first — append, don't overwrite, if pending entries exist. Handoff: "[n] staged. Say **sweep** or **defer** (clean — staging holds state across sessions)."
4. **Sweep** — absorb all pending-merge entries into the registry, then **overwrite staging doc to empty immediately** (mandatory — the recurring leak is absorption without clearing). Handoff: "Registry updated, staging cleared. Say **sync** or **defer**."
5. **Sync** — read and update `therantai-brain.md` to reflect the new registry state (phase map, candidate→living transitions). Closing: "Harvest complete. [n] extracted→placed→staged→registered→reflected. If carrying forward, run /handoff now."

## Resumption protocol
On `resume harvest`: ask where they parked, or infer from the staging doc / registry timestamp if MCP is accessible. Name remaining stages, confirm with "go," resume from that station — completed stages never re-run.

## Behavioral rules
Claude drives, practitioner confirms with one word (`place`/`stage`/`sweep`/`sync`/`go`) — no stage-naming burden on the practitioner. Every station is a clean, complete stopping point. Placement runs autonomously inside the pipeline (socratic mode is for standalone /placement-protocol). Staging-doc overwrite after sweep is mandatory and non-negotiable — flag explicitly and don't close if it fails. Local MCP is the sole write surface — ignore any Drive file ID reference from prior context. Handoff always follows harvest, never precedes it (an early handoff carries an incomplete picture). Light close is a first-class invocation, not a lesser one.

## Relations
Cognitive-friction-extractor (Stage 1) and placement-protocol (Stage 2) remain standalone-invokable — same organs, different operating mode inside the pipeline (autonomous vs. socratic). Attune may surface /harvest as the invocation when the threshold crosses; harvest executes the chain. Handoff runs after harvest closes, never instead of or before. Ignition-pipeline reads what harvest writes to the brain doc — harvest writes, ignition reads.

## Scope
Closing phase, staffed (sequences 4 existing skills + brain sync). v1.1 delta: Drive fully excised, all surfaces migrated to local `claude_brain/`, handoff-after-harvest law encoded. Global.
