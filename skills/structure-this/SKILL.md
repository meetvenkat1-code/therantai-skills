---
name: structure-this
description: "Pre-processing gate that captures genuine intent from raw conversational flow before any answering begins. Clusters questions by domain, deduplicates overlaps, types each by the answer-shape it implicitly wants, surfaces the root question the batch is circling, and presents the structured map back for confirmation. Capture is the DNA — default output is recognition-faithful. Blueprint mode (optional) adds dependency-ordering and depth-calibration as a subordinate layer that cannot alter the capture beneath it. Invoke with 'structure this', '/structure-this', 'cluster my questions', 'what did I just ask'. Add 'blueprint mode' for response architecture. Does NOT answer — only structures. Answering begins only after confirmation."
metadata:
  triggers:
    - "structure this"
    - "/structure-this"
    - "cluster my questions"
    - "what did I just ask"
    - "structure this in blueprint mode"
  scope: global
  phase: Opening
  version: "2.1"
  date: "2026-06-25"
  author: meet.venkat1@gmail.com
---

# STRUCTURE THIS

## Three layers
L1 Recognition (always on) — capture floor, everything else builds on frozen capture. L2 Deep Recognition (always on, folded into capture) — hears the answer-shape need inside each question. L3 Response Architecture (toggle, off by default) — organizes the reply, structurally forbidden from altering L1/L2.

## Reading protocol
**L1:** question nuclei (strip circling/repetition/corrections — one nucleus per question); overlap collapse (same question, two angles → sharpest version, marked *merged with Qn*); domain clusters (name the territory, not the questions); implicit surfacing (confusion implying a question, marked *implied*); priority signal (returned-to/flagged, marked ★).

**L2:** type each by answer-shape wanted —
| TYPE | Trigger | Wants |
|---|---|---|
| DEFINITION | "what is X" | crisp definition + parent category |
| MECHANISM | "how does X work" | causal walkthrough |
| PROCEDURE | "how do I do X" | ordered sequence |
| RELATION | "how are X and Y related" | relational map |
| JUDGMENT | "should I / which is better" | reasoned recommendation |
| VALIDATION | "am I understanding this right" | confirm + correct + sharpen |
| PURPOSE | "why does it matter" | function + cost of absence |

Type by intent beneath the phrasing, not grammar alone. Name the single root question the batch is circling, if one exists.

**L3** (blueprint mode only): dependency ordering (answer order ≠ ask order, sequenced for coherence); depth calibration (one-line / paragraph / deep, per question); root-first (answer the root, facets resolve in its light).

## Output — default (L1+L2)
```
STRUCTURE THIS — [date]
ROOT: [circling question, if any]
────────
CLUSTER A — [Domain]
  Q1. [question]                    [TYPE: RELATION]
  Q2. [question] *(merged with Q5)* [TYPE: PURPOSE]
  Q3. [question] ★ *(implied)*      [TYPE: VALIDATION]
CLUSTER B — [Domain]
  Q4. [question]                    [TYPE: DEFINITION]
────────
TOTAL: [n] questions · [n] clusters   COLLAPSED: [n] · IMPLIED: [n]
Confirm or adjust — then say "answer these." (Add "blueprint mode" for answer-ordering.)
```

## Output — blueprint mode (L1+L2+L3)
```
STRUCTURE THIS — blueprint — [date]
ROOT: [circling question]
ANSWER ORDER (dependency-sorted):
  1 ▸ [question]  [TYPE: RELATION]    [depth: paragraph]
  2 ▸ [question]  [TYPE: PURPOSE]     [depth: deep]     ← depends on 1
  3 ▸ [question]  [TYPE: VALIDATION]  [depth: one-line]
  merged: [Qn → Qn — reason]   surfaced: [implied question — source]
Confirm or adjust — then say "answer these."
```

## Behavioral rules
Never answer — gate holds until confirmation. Capture freezes before L3 runs; L3 arranges, never re-reads intent. No clarifying questions before structuring — unresolvable ambiguity gets both readings presented, practitioner picks. One domain = one cluster, no over-splitting. Keep original heat, don't sanitize intent. Collapse aggressively — better merged-then-corrected than split-what-was-one.

## After confirmation
Gate opens on "answer these" or a named subset ("answer Q1, Q3"). Use the structured batch (blueprint mode: approved order + depth). Incorporate any adjustments first.

## Relation to map-my-questions
Structure-this is prospective (fires before scatter happens); map-my-questions is retrospective (recovers the picture after). Same typing/clustering logic, opposite ends of the question arc.
