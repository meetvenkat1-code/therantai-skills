---
name: cognitive-friction-extractor
description: Scans any build session for resolved friction points and extracts them as named, categorized skills in CATEGORY / SKILL / CONSTRAINT / TRIGGER / ASCENT format. Runs both arms of the recursive-learning flywheel in a single gesture — the compression arm captures and thickens what resolved, and the ascent arm emits the sharper successor question each resolution now makes askable. Each extraction is matched against the existing skill ecosystem before any new skill is proposed — the default move is to thicken an installed skill, not to proliferate a new one. Invoke with "extract skills" at any point in a session — mid-session to capture live resolution, or end-of-session for a full retrospective sweep. Also triggers on "extract skills from what I just described" for cross-session recall. Each extracted skill is automatically categorized, matched against existing skills, given its successor question, and offered for routing — upgrade, memory, new file, or discard.
triggers:
  - extract skills
  - extract skills from what I just described
  - scan this session for friction
  - what did we solve
  - capture what resolved
scope: global
version: 1.5
date: 2026-06-28
author: meet.venkat1@gmail.com
---

# Cognitive Friction Extractor

Retrospective scanner: pauses after friction resolves, presses the resolution into a named, reusable constraint before it dissolves — so the next session doesn't re-discover the same wall. Two arms, one gesture: **compression** (capture + fold back into existing skills, so carrying what you know gets cheaper) and **ascent** (emit the sharper question the resolution now makes askable). Capture without provocation is half a loop — this skill doesn't permit the half.

## Invocation modes
- **Mid-session** — extract the instant a wall clears, while the fix is warm. Trigger: "extract skills."
- **Mid-session tag anchoring** — drop a terse inline tag at resolution instead of stopping to format ("tag: streaming finalization — three-layer safety solved"). End-of-session extraction reads these as heat anchors, prioritizing them, filling gaps around them.
- **End-of-session sweep** — scan the full conversation for every point of resistance (misunderstood requirements, tool failures, bugs, pivots, mistaken assumptions) and extract what resolved.
- **Cross-session recall** — apply the same methodology to friction described from a past, unextracted session. Trigger: "extract skills from what I just described."

## Extraction format
`CATEGORY / SKILL / CONSTRAINT / TRIGGER / ASCENT`

- **CATEGORY** (fixed taxonomy): Rendering (layout/overflow/font/z-index) · API (streaming/routing/parsing/CORS/auth) · Build Sequence (pipeline order, gates missed) · UI Contract (zone/copy/panel/sandwich violations) · Prompting (instruction drift, trigger collisions) · Memory (managed-edit conflicts, path errors) · Tool Behavior (platform constraints: clipboard, FileSystem API, Drive MCP) · Cognitive Patterns (skipped clarification, hardened assumptions).
- **SKILL** — the resolution as a capability, not the failure: "Streaming finalization three-layer safety," not "streaming broke."
- **CONSTRAINT** — 1-3 sentences, specific enough to apply without re-deriving.
- **TRIGGER** — the situation that makes this rule relevant.
- **ASCENT** — non-optional. The sharper, previously-unaskable question this resolution unlocks — the nutrient for the next cycle. Write it as a real question in the person's own line of inquiry.

## Existing-skill matching (compounding phase, runs before any new skill is proposed)
Default: most learning strengthens an existing capability; new-skill creation is the exception. For each friction point: search installed skills → find closest domain → classify as new constraint / edge case / trigger refinement / workflow improvement / clarification / failure-mode rule → propose integration where a home exists → create new only if none does. Filing a learning as a new skill when a home existed is fragmentation, not extraction.

## Drafting the patch
When routed as an upgrade, draft the literal insertion text in the target skill's own register, naming the landing section — not an instruction to go write it, the update itself, provisional pending approval. Bound by one honesty rule: the patch is only as trustworthy as its match — strong match → offered ready-to-apply; loose/ambiguous match → offered as a candidate with the ambiguity named, not buried under polish. No patch for Memory/New/Discard routes.

## Routing priority
1. Upgrade Existing Skill (default/preferred) 2. Add to Memory (standing behavioral instruction) 3. Forge New Skill File (no existing home) 4. Discard (too session-specific). Routed one skill at a time, not batch.

## Behavior
1. Scan conversation (or described friction). 2. Identify every resolved friction point (tags as heat anchors first). 3. Filter — unresolved issues are noted, not extracted. 4. Assign CATEGORY. 5. Generate SKILL/CONSTRAINT/TRIGGER. 6. Emit ASCENT (always). 7. Match against ecosystem, classify integration type. 8. Draft the patch (upgrade route only). 9. Determine route. 10. Present each in sequence with match, patch, ascent, and routing options.

## Output
```
EXTRACT — [session/date]
────────
SKILL 01
CATEGORY: [ ]   SKILL: [ ]   CONSTRAINT: [ ]   TRIGGER: [ ]   ASCENT: [ ]
EXISTING SKILL MATCH: [name or none]
INTEGRATION TYPE: [new constraint/refinement/edge case/trigger update/workflow improvement/failure-mode prevention]
PATCH DRAFT: [literal insertion text, if upgrade route]
Route to → [ Upgrade ]  [ Memory ]  [ Forge New ]  [ Discard ]
────────
SKILL 02 ...
```
No resolved friction → say so; an empty extraction means the session ran clean.

## Open Friction Log
Unresolved friction, listed separately, not converted to skills:
```
OPEN FRICTION — not yet resolved
• [what failed, where it stands]
```

## Ascent Log
Every ASCENT question from the session, gathered at close:
```
ASCENT — questions this session made askable
• [successor question, traced to its resolution]
```
Open Friction = debt carried forward. Ascent = the door carried forward. A session may legitimately close with an empty Open Friction Log; one that closes with an empty Ascent Log learned nothing that sharpened the next question — worth noticing.

## Scope
Global — applies to HTML builds, skill forges, prompt sessions, philosophical inquiry alike. Any session where something was figured out qualifies, if the resolution is nameable and portable.

## Relationship to Session Ritual
Operational implementation of the memory-encoded Session Ritual ("extract constraint hits and working patterns before closing"). Same law, two resolutions — reminder and execution.
