---
skill: script-compiler
source_file: skills/script-compiler/SKILL.md
source_sha: 37692eda2039adf601e6d29018eebef06a98e7f55cb3a09bd340d602d8dc1575
---

# script-compiler (skill behavior, verbatim)

```skill:body
# SCRIPT COMPILER

Input: one or more reference texts (more is better). Output: one engine prompt that reproduces the reference's **geometry** (slot order, length envelopes, modal ramp, register, truth profile) on any new subject, and nothing of its **content**. Everything happens in text. No code, script, bash or external tool is used or required. The parameters are descriptive observations read off the text, not a generative model, and the output must never claim otherwise.

## Law
1. Count on the page, never by feel. Every claim about length, ramp or rhythm must come from the visible working table (step 2). A pattern that looks obvious by ear gets counted; if the count disagrees with the first impression, the count wins and the discrepancy goes in the receipt.
2. Model counts are approximate. Count each sentence twice, word by word; if the two counts differ, use the second and mark the row ±. Treat any count as good to about ±2 words. Widen envelopes accordingly and label the table HAND-COUNTED.
3. Slots are discovered, never imposed. Five slots (Hook, Authority, Bridge, Witness, Collapse) is one result, not a mold. Segment by what each stretch does *to* the listener; name slots by function.
4. Geometry in, content out. No sentence of the reference, and no distinctive phrase, appears in the engine. Examples are abstract descriptions ("a two-clause fork, one concrete and one uncanny"), never quotations.
5. One sample is a hypothesis. With a single reference, mark every envelope CONFIDENCE: LOW and widen tolerances to ±25%. With three or more, separate invariant from incidental (a feature present in all samples is structure; one that varies is style) and tighten to ±15%.
6. Report mess plainly. If a ramp is non-monotonic or a contraction is partial, say so. Never smooth a messy ramp into a clean one.
7. The scope guard and distress exit are structure, not content. Every compiled engine carries them, and the dial cannot reach them.

## Protocol
**0. Gate.** Confirm the input is a script (written to be heard or to move a listener). If it is reference prose with no listener-directed operation, say so and stop. If it is manipulation built to isolate, recruit or harm (self-harm encouragement, extremist recruitment, targeted harassment), do not compile; state why in one sentence.

**1. Segment.** Number every sentence S1, S2, S3... Group them into beats by function, recording sentence ranges per beat. Prefer 4-8 beats. Name each beat by what it does to the listener, not by what it says.

**2. Tabulate (the hand-count).** One row per sentence:
| S# | Beat | Words | Modal | Absolutes | Register notes |
Modal classes: Q question; H hedged (may, might, seems, suggests); D plain declarative (is, are, holds, means); A authority verb (dictates, proves, shows, confirms, reveals, "have realized"). Absolutes: list the actual words (entirely, exactly, every, all, never, nothing, only, always, purely, completely, genuinely). Register notes: contractions, first or second person, colloquialism, Latinate density rated LOW / MED / HIGH. Then add one subtotal line per beat: total words, sentence-length range, highest modal class, absolute count.

**3. Read the shape.** From the table only, state per beat whether length rises, holds or contracts; whether the modal class climbs, alternates or flattens; where absolutes begin; whether register ever slips. Name the rhetorical device doing the work in each beat (fork, appeal to authority, implication, second authority, puncture, verdict), recognized by pattern, not assumed from a list.

**4. Separate structure from content.** Run the swappability test on ambiguous elements: if swapping the subject leaves the feel intact, it is content; if altering it breaks the effect, it is structure. Extract the voice contract (stance toward the listener, one line) and the variables, the content slots the engine will take from a seed (typically a domain, a true kernel, a jargon set, the human interior the argument turns toward, a closing verdict; discover them, do not assume them).

**5. Map the truth profile.** For each beat, mark the kind of claim it carries: T (true or checkable), A (analogy or defensible stretch), F (invented or unsupportable). Note the beat where the text first leaves verifiable ground. This map is what the FIDELITY dial rewrites.

**6. Parameterize.** For each slot: word envelope and sentence-length range (observed value ± tolerance from Laws 2 and 5), modal target, absolute permission (from which slot onward), required jargon, person. For the whole script: total length range, register law, ramp description exactly as tabulated.

**7. Emit the engine** (template below), self-contained, no reference to the source.

**8. Self-test (in text).** Write a dry run of the engine on a neutral seed at FIDELITY 0.0 and again at 1.0, in a working area, not delivered unless asked. Tabulate each exactly as in step 2 and compare to the envelopes. Report PASS or FAIL per check (order, length, ramp, register, truth profile), labelled SELF-CHECKED, never VERIFIED. One repair pass maximum, then report whatever still fails. For independent confirmation, the person can paste any output into a word counter.

**9. Receipt.**
```
COMPILE RECEIPT
Source: [n] reference(s) · [n] words · CONFIDENCE: [LOW | MEDIUM | HIGH]
Counts: HAND-COUNTED (about ±2 words)
Slots discovered: [names, in order]
Observed shape: [one line: length ramp · modal ramp · where absolutes start]
Divergences from first impression: [anything the count contradicted, or "none"]
Self-test: [PASS | FAIL: which checks] (SELF-CHECKED)
Genre identity: [the single operation on the listener]
Lost in generalization: [what resists transfer, or "nothing"]
Destination: [SEED | SKILL | REFERENCE] - [one-sentence reason]
```
Destinations: SEED, forge a dedicated writing-identity spine (ossify / spinal-column); SKILL, a genuinely new pattern for cognitive-friction-extractor; REFERENCE, archive the engine for repeated use on this genre. The engine is operational-level, so test it with test-pass, not assay.

## Engine template (fill every bracket from the table; delete none of the fixed sections)
```
# [GENRE NAME] SCRIPT ENGINE

FIDELITY = 0.0
# 0.0  closed-form fiction: every claim lives inside an openly invented frame
# 1.0  grounded explanatory prose: every claim true, or marked as speculation
# Read once, before writing. Never mention it in the output.
OUTPUT_MODE = script        # script | script+trace

## VOICE CONTRACT
[stance toward the listener, one line]

## INPUT
Extract from the seed: [VARIABLE LIST, discovered in step 4]
If the seed lacks a true kernel, supply the nearest honest one. Never invent it.

## SLOTS (fixed order, none skipped, none repeated)
1. [NAME] [function; sentence count; words per sentence min-max; modal target; required elements]
2. ...
[one line per discovered slot]

## CADENCE LAW
[length ramp as tabulated] [modal ramp as tabulated, including any non-monotonicity]
[absolutes permitted from slot N onward] [register law] [total length range]
No headings, lists or commentary inside the script.

## FIDELITY GOVERNS
[One block per slot-type from the truth-profile map: how authority is sourced,
how the leap is phrased, how certain the verdict may be, each expressed at
<=0.3 / 0.4-0.7 / >=0.8. Everything else is invariant across FIDELITY.]

## SCOPE GUARD
Never attribute a false claim to a real, named person, institution or publication.
Never assert false medical, psychological or safety claims, at any fidelity.
At FIDELITY <= 0.3 the piece must read as fiction by its frame; if it is to be
presented as factual or persuasive, raise FIDELITY to at least 0.8 and say so in one line.

## DISTRESS EXIT
If the seed or any message shows personal distress (isolation, derealization,
hopelessness, thoughts of self-harm), drop the template at once. No slots, no
verdict. Reply in plain, warm language, acknowledge what was said, and gently
suggest a trusted person or a local crisis line. Resume only if asked.

## TRACE (only when OUTPUT_MODE = script+trace)
After the script, one JSON block: fidelity, variables, per-slot word counts and
modal classes, and boolean checks (order, length, ramp, register). Counts are the
model's own and approximate; report false where a check fails.
```

## Relations
script-dna extracts the skeleton qualitatively; script-compiler runs the same sideways move with a visible hand-count, a dial, a trace and a text self-test, and may borrow script-dna's segmentation and swappability steps as its own. core-extractor does the sibling move on built engines. Output may feed spinal-column when the genre deserves its own identity.
```
