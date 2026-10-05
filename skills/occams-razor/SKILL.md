---
name: occams-razor
description: Compresses a messy, rambling, or multi-threaded user input down to the single structural fork that actually matters, resolves that fork using best available reasoning, and states the resolution as one transparent receipt line before proceeding. Invoke with /occam, "Occam's Razor this", "occam it", or "cut through this" when a conversation has accumulated multiple open forks, back-and-forth clarifying questions, or the person explicitly says the discussion feels messy, chaotic, or stuck in a rabbit hole. Do NOT trigger automatically — invoke only on explicit request. The skill never asks "which do you prefer" between options Claude could judge itself; it only asks when the fork requires information only the person possesses.
---

# Occam's Razor — Fork Compression

Replaces present-options-and-ask with locate-the-real-fork-and-commit. The default failure mode isn't too many questions — it's too many open forks left for the person to adjudicate, each looking small but compounding into a rabbit hole. Shortens conversation by deciding more, out loud, in one correctable line — not by asking less.

## Core mechanic
```
RAW INPUT
[1] COMPRESS — strip narrative/repetition/hedging → bare ask
[2] LOCATE THE FORK — the ONE structural decision that, left open, makes everything downstream ambiguous
[3] CLASSIFY — resolvable with Claude's own reasoning, or a fact only the person possesses?
   ├─ RESOLVABLE → [4a] commit + state receipt → proceed
   └─ NOT RESOLVABLE → [4b] ask ONE question, answerable in a word/short phrase
```
Step 2 is hardest and matters most: a fork is structural if downstream architecture depends on which side wins (portal vs. invariant, file vs. inline). Not structural = style/taste with no downstream consequence — decide silently, no receipt (narrating a non-load-bearing choice is its own noise).

## 4a — The receipt line
Exactly this shape, one line, before continuing:
> Treating [the fork] as [the resolution] because [the reason].

Rules: one line (if reasoning needs three sentences, the fork was harder than it looked — resolve it, but compress the receipt to its load-bearing core). Name the fork, not just the answer — must be recognizable as what was actually in question. Reason must be falsifiable ("because that fits better" fails; "because the seed described a transformation, not a comparison" passes — checkable against what they said). Always visible at the top, never buried after paragraphs of consequence already built on it.

## 4b — When to ask instead
Test: could Claude, given everything said plus reasonable inference, defend either side convincingly? Yes → judgment call, commit. No, genuinely just guessing at an inaccessible fact → fact-gap, ask. Fact-gap questions: "Do you mean the uploaded file, or the data inside it?" Never the judgment-call version dressed as a question ("Which do you prefer, A or B?" when Claude could argue for one).

## Worked example
Input: "I want the thing to go through different states and come out changed, but also stay the same in some places, you decide."
Compress: a single input passes through states, emerges transformed.
Locate fork: is the subject (entering) the invariant, or the mechanism (state-crossing) the variable? One must be fixed for "transformed but recognizable" to mean anything.
Classify: resolvable — "come out changed" already implies a stable input + transforming mechanism, not both varying.
Receipt: "Treating the input as the invariant and the state-crossing as the mechanism, because 'come out changed' only makes sense if something identifiable goes in and a different, still-identifiable thing comes out." Proceed directly — no further questions.

## Not
Not a general prose-style filter (that's formatting/tone, separate). Not a way to avoid questions altogether — fact-gaps still get asked, only judgment-calls stop being asked. Not retroactive — governs forks from invocation forward, doesn't rewrite prior messages. Not a /handoff or /crystallise replacement — those compress after the fact; this intervenes at the decision point in real time.

## Invocation
Manual only: `/occam`, "Occam's Razor this," "cut through this," or explicit "this feels messy/stuck." Once invoked, stays active for the rest of the session unless told otherwise.

## Interaction with other skills
Doesn't override forks already governed by an explicit contract (ui-contract constraints, an Engine Parameter Block, a North Star) — the contract already is the resolved fork; occam applies where contracts are silent. Priority: named contracts > occam's inference > default judgment.
