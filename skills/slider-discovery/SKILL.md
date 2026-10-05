---
name: slider-discovery
description: "Discovers load-bearing slider dimensions native to a specific artifact or HTML engine — a judgment organ that first decides if a slider is structurally warranted, then surfaces only the 1-3 dimensions carrying real weight for that artifact's execution logic and output range. Two modes: manual (/slider) and ambient (watches builds under ui-contract/hybrid-engine-contract, speaks unprompted when a slider-shaped decision is live). Subordinate-but-invocable to both contracts. Default output is compressed; --full or 'full taxonomy' unlocks the four-category sweep (Intensity, Frequency, Tonality, Structural Depth). Invoke with /slider, 'slider this', 'discover sliders for this', 'what sliders does this need'. Never generates parameter values or numbers — only the dimension, its core tension, and its functional impact."
metadata:
  triggers:
    - "/slider"
    - "slider this"
    - "discover sliders for this"
    - "find the load-bearing sliders"
    - "does this need a slider"
    - "/slider --full"
    - "full taxonomy"
  scope: cross-phase
  phase: Build
  version: "1.0"
  date: "2026-07-22"
  author: meet.venkat1@gmail.com
---

# SLIDER DISCOVERY

Answers what other contracts don't ask on their own: does this artifact have a hidden axis of variance deserving a control surface, and which one actually matters? Not a generation template — doesn't assume every engine needs a slider, doesn't default to the full four-category taxonomy (padding wearing thoroughness' costume). Judgment first, density second, exhaustiveness only on request.

## Stage 0 — Necessity gate (non-skippable, both modes)
Three tests, read against the artifact's actual execution logic:
1. Does the output genuinely vary along an axis a user would want to move? Fixed-function (one input/output shape, no tonal/intensity range) → fails.
2. Is the variance continuous, not categorical? 3-4 discrete mutually-exclusive modes → toggle/dropdown, not a slider.
3. Would moving it change the output's *character*, not just a cosmetic setting? Font-size/padding nudges → UI Contract's territory, not load-bearing.

Any test fails → **"No slider warranted"** + one-sentence reason — a legitimate, complete output. Never manufacture a slider to justify invocation. Pass → proceed.

## Stage 1 — Domain variable analysis (internal, not narrated in compressed mode)
Read the artifact's actual execution logic — what fluctuates within *this* build, what's the difference-maker between its most restrained and most extreme output.

## Stage 2 — Four-family lens (diagnostic; full detail only in `--full`)
Intensity & Amplitude (volume/strength/concentration) · Frequency & Pulse (rate/repetition/cadence) · Tonality & Modulation (voice/emotional posture/register) · Structural & Abstraction Depth (systemic complexity/density). Most artifacts have real variance in one or two families, none in the rest — naming all four regardless of fit is exactly the padding this skill refuses.

## Stage 3 — Load-bearing selection
Keep only: if this slider didn't exist, would the output range be meaningfully smaller? Typically 1-3 dimensions survive. Discard stylistic-flourish-only candidates.

## Output — compressed (default)
```
SLIDER DISCOVERY — [artifact]
VERDICT: [warranted / not warranted — one clause]
[per load-bearing dimension:]
DIMENSION: [name]
CORE TENSION: [left] ←→ [right]
FUNCTIONAL IMPACT: [1-2 sentences — what changes in behavior/output]
```
No parameter values/ranges/numbers. Stop there — don't append the full taxonomy "for completeness."

## Output — full taxonomy (`--full` only)
All four categories, every discovered dimension per category, marginal-fit families explicitly marked rather than silently dropped — for early-build possibility-space work, not everyday use.

## Ambient mode
**Standing rule:** mandatory the moment a trigger fires, during any session where ui-contract/hybrid-engine-contract is active or a new HTML engine is being built/modified — continuous background test, not a one-time check. Deliberately lower threshold than ATTUNE's irreversibility bar: a wrong suggestion costs one dismissal line; a missed slider costs a rebuild once fixed-behavior assumptions are baked in.

**Triggers (any one sufficient):** a continuous-variance concept described in prose without the word "slider" yet (the most common failure — fire before code is written); an existing slider-bearing engine pattern (e.g. Fragment Forge) being extended, not yet re-discovered; the system prompt's tonal/behavioral *range* being defined (spinal-column/ossify work articulating a range rather than fixed stance); a UI/Hybrid contract control surface being added over something continuous; the practitioner directly asking or expressing uncertainty.

**Format:** one line — *"/slider check — [artifact/feature] just described a range along [dimension]. Worth running the necessity gate before this locks as fixed?"* Not the full output unprompted. Assent or continued description = invocation, run Stage 0 onward. Already moving to define it themselves → stay silent. Fire at first mention, not at review — late recognition means bolted-on, not architected-in.

**Re-surfacing (differs from ATTUNE's permanent silence):** a wave-off suppresses that dimension for the current build only until it resurfaces with genuine new weight — a different context, a system-prompt draft actually writing the range in, or an independent second description (not a rephrase in the same breath). Resurfacing says so plainly: *"/slider check — [dimension] again, this time in [new context]. Still worth a look, or staying fixed deliberately?"* A second explicit wave-off on the same dimension in the same build = standing decision, not raised again there (other dimensions remain fair game).

## Relations
Ui-contract owns the slider component's rendering law; this skill hands it *which* dimension. Hybrid-engine-contract owns provider routing; this skill names the dimension and its routing implication, doesn't design routing. Spinal-column/ossify are the natural upstream call when their output describes a range rather than a fixed stance. Typography governs visual-register variance — a different axis, relevant only if the discovered dimension is explicitly aesthetic.

## Scope
Cross-phase, Build-weighted. Subordinate-but-invocable inside both contracts (never a mandatory gate in either's sequence); standalone invocation always available.
