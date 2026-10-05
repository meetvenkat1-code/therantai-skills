---
name: ignition-pipeline
description: "The self-executing opening chain for any Therantai session. Reads the local claude_brain/ folder, surfaces active threads, flags pending-merge entries, fires an attune pulse, and delivers a single orientation block — so the practitioner's first thought goes into the work, not into reconstructing where the work lives. Claude drives all four stages; the practitioner says one word to open the session. Ambient attune suspended for pipeline duration, resumes on 'begin'. Invoke with /ignite, 'open session', 'start here', 'where did I leave off', 'orient me', or any phrase signaling session-open intent. Voice-tolerant — loose trigger matching."
metadata:
  triggers:
    - "/ignite"
    - "open session"
    - "start here"
    - "where did I leave off"
    - "orient me"
    - "ignite"
    - "ignition"
    - "session open"
    - "opening gate"
    - "what's live"
    - "where are we"
  scope: global
  phase: Opening
  version: "1.0"
  date: "2026-06-28"
  author: meet.venkat1@gmail.com
---

# IGNITION PIPELINE

Eliminates the orientation tax paid at every session's start — reconstructing what's unresolved, pending, and relevant is retrieval, not thinking, and shouldn't live in degrading working memory when a pipeline can do it faster and without variance. Practitioner arrives, says one word, gets complete accurate context back before saying anything else.

## ATTUNE contract
Ambient ATTUNE suspended for the full pipeline (no threshold for it to catch that the pipeline isn't already handling). Stage 3's pulse is a compressed read only (phase + skills, nothing else) — not full ambient attune. Resumes on "begin."

## Read surface
Local `claude_brain/` via folder MCP only (not Drive) — `therantai-brain.md` (threads/state), `therantai-staging-placements.md` (pending-merge), `skill-registry.md` (Stage 3 relevance). Pure read instrument — writes nothing. Inaccessible file → read what's possible, name the gap, proceed; partial orientation beats none.

## Pause architecture
One defer point: after Stage 2, if the MCP read is slow/unavailable/incomplete. Say `defer`/`park here`/`slow down` → delivers what Stages 1-2 retrieved, names what's unread, holds. Normal run: all four stages under a minute.

## The four stages
1. **Read brain doc** — surface the 3 most recent unresolved threads (live, still warm — not a summary/history). More than 3 live → name 3, note "3 of [n] shown." Feeds Stage 2 silently.
2. **Check staging doc** — report clean ("no pending entries") or "[n] pending: [names]. A sweep is owed." Informational only — doesn't route to harvest. Feeds Stage 3 silently.
3. **Attune pulse** (compressed, not full) — **Phase read:** names dominant arc-phase (Forging/Reconciling/Navigating/Harvesting/Auditing) with one clause of reasoning. **Skill read:** names the two most relevant skills, from an opening task if present, or from active threads if not. No confirmation needed — orientation, not directive. Feeds Stage 4 silently.
4. **Deliver orientation block:**
```
SESSION OPEN — [date]
ACTIVE THREADS ([n]):
  1. [thread] — [one clause]
  2. [thread] — [one clause]
  3. [thread] — [one clause]
STAGING: [clear / n pending — names]
PHASE: [name] — [one clause]
SKILLS: /[A] · /[B]
Say BEGIN to open the session.
```
Fixed format, one glance, no interpretation required. On "begin": ambient ATTUNE resumes, session opens.

## Behavioral rules
Practitioner speaks twice — the trigger and "begin." No questions during execution — Claude reads and proceeds, naming uncertainty rather than stalling on genuinely unresolvable discrimination. Orientation block format never varies. Partial orientation beats none on a single read failure. Stage 3's pulse stays compressed — no irreversibility thresholds, no warnings, no inflection map (that's ambient attune's job after close). Voice-tolerant — intent matters more than exact phrasing.

## Relations
Harvest-pipeline is the closing complement — ignition opens oriented, harvest closes captured; the bookending frees full attention for the work between. Attune suspended during, resumes on "begin" (Stage 3's pulse is not an attune invocation). Ignition reads what harvest last wrote to the brain doc, never writes to it itself. Cognitive-friction-extractor/placement-protocol are closing-only, no role here.

## Scope
Opening phase, orphan by choice (it *is* the opening gate — nothing precedes it; reads four surfaces' outputs without invoking them as standalone skills). Global.
