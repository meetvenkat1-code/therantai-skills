---
name: retroactive-harvest
description: The recovery organ for pre-registry session transcripts — old conversations that closed before the harvest pipeline existed, before skill-vocabulary entered the practice, before any extraction ritual ran. Approaches the archive as an archaeological site, not an audit subject: not to correct the past or assess it, but to surface what was always there unwitnessed. Scans for resolution-shape in unmarked sessions where no tags were dropped. Filters candidates against the current registry before naming — pre-extraction, not post-extraction match. Calibrates time-distance before routing to placement. Invoke with /retroactive-harvest, "retroactive harvest", "scan this old session", "look for gems", "extract from old transcript", "pre-registry sweep". Fires only on historical transcript material — cognitive-friction-extractor governs live sessions.
triggers:
  - /retroactive-harvest
  - retroactive harvest
  - scan this old session
  - look for gems in this transcript
  - extract from old transcript
  - pre-registry sweep
  - scan for pre-registry gems
  - retroactive harvest sweep
scope: global
version: 2.0
date: 2026-06-28
author: meet.venkat1@gmail.com
---

# RETROACTIVE HARVEST

Old sessions weren't incomplete — they were unwitnessed. Foundational friction was resolved in raw conversation before any extraction ritual existed; that intelligence didn't disappear, it went underground into the transcript's shape.

**Core conviction: the past session is an archaeological site, not an audit subject.** Not assessing efficiency or correctness — asking only: what did this session resolve, in its own terms, that the ecosystem still lacks? No mid-session tags exist in old transcripts; the friction points don't self-identify. Reading for shape in unmarked territory is slower, more interpretive, dependent on reading the whole before any part.

## Input surface
Uploaded/pasted raw transcript (ground truth, read in full before scanning — resolution arcs are only visible whole) or described-from-memory (lower fidelity, name approximate date + domain for calibration). **One session at a time** — batching collapses the architecturally meaningful differences between sessions' friction profiles and time-distance.

## Three divergences from cognitive-friction-extractor

**1. Resolution-shape reading, not marker-scanning.** No tags exist to scan for — read for four signatures instead: **convergence** (multiple approaches collapse to one, hedging stops); **closure** (a recurring question stops recurring); **pivot** (one approach abandoned irreversibly for another); **confirmation** (a statement lands as truth, building follows instead of more questioning). Each occurrence is a candidate friction moment, not automatically a gem.

**2. Pre-extraction ecosystem filter, not post-extraction match.** Filter *before* naming, not after: identify domain from the signal → search the registry for a covering trigger → **trigger fires + constraint fully covered** → skip, note as confirmation → **trigger fires but this session's specific constraint is absent** → thickening candidate, name the gap only → **no trigger fires** → new territory candidate, full extraction. Old sessions often produce apparent-new skills that are really thickening signals for skills forged later — the filter catches duplication before it's named.

**3. Time-distance calibration** (unnecessary for live sessions — architecture hasn't moved yet). Three verdicts per surviving candidate: **still current** (proceed, standard priority); **superseded** (a later decision renders it obsolete — discard, name what superseded it); **dormant relevant** (rare now but would matter if the friction recurred — proceed, lower priority; these are the gems most likely lost if the filter runs too aggressively).

## Scanning protocol
1. Read the full transcript, no extraction yet — orientation only.
2. Map the resolution arc internally (one paragraph) — where convergence/closure/pivot/confirmation appeared.
3. List resolution-shape candidates against the four signal types.
4. Run the pre-extraction ecosystem filter — skip covered, pass thickening/new-territory candidates.
5. Run time-distance calibration on survivors — discard superseded (named), flag dormant-relevant (lower priority).
6. Extract survivors in standard CATEGORY/SKILL/CONSTRAINT/TRIGGER/ASCENT — identical format to the live extractor.
7. Surface the batch with header + scan summary, route each for placement.

## Output
```
RETROACTIVE HARVEST — [date or "unknown"]
Source: [uploaded | described]

SESSION ARC: [one paragraph — what it was doing, where it stopped fighting itself, which signals appeared where]

SCAN SUMMARY:
Resolution-shape candidates: [n] | Filtered (already covered): [n] | Filtered (superseded): [n] | Surviving: [n]

EXTRACTION 01
CATEGORY / SKILL / CONSTRAINT / TRIGGER / ASCENT: [ ]
ECOSYSTEM MATCH: [skill or none]   INTEGRATION TYPE: [thickening|new territory|dormant-relevant]
TIME-DISTANCE VERDICT: [still current | dormant relevant]
PATCH DRAFT: [if thickening]
Route to → [ Upgrade ]  [ Memory ]  [ Forge New ]  [ Discard ]

SUPERSEDED (noted, not extracted): • [resolution] — superseded by [ ]
CONFIRMED COVERED: • [domain] — staffed by [ ]
OPEN SIGNALS (unclear verdict): • [signal — why no clean extraction]
```

## Refuses
Forensic reading (auditing whether the past was efficient/correct). Extracting resolutions the ecosystem already carries (duplication at lower fidelity weakens the installed skill — filter enforces this before naming). Running on live sessions (that's the extractor's territory). Batching transcripts (one session, one arc, one calibration). Running placement itself — ends at the extraction boundary, hands off clean.

## Relations
Cognitive-friction-extractor governs live/tagged/present-tense; retroactive-harvest governs archive/unmarked/past-tense — same output format, same downstream routing. Harvest-pipeline receives its extractions at Stage 2 (placement) same as any other. Placement-protocol is the handoff point. Defer-log prevents future loss; retroactive-harvest recovers past loss — temporal inverses.

## Governing conviction
A session that closed without harvest didn't fail — it ran before the organism had the apparatus to witness what it produced. The friction was real, the resolutions genuine; they simply went unwitnessed. This organ witnesses them for the first time, with the vocabulary the past session itself helped build.
