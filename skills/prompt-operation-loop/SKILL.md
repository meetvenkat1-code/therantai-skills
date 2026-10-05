---
name: prompt-operation-loop
description: Iterative prompt optimization engine that turns raw or vague intuitions into dense mode-classified prompts forcing a precise epistemic operation, executes them internally, and adversarially evaluates whether the operation was genuinely performed rather than described. Re-architects structurally on failure until convergence, then surfaces the winning prompt. Runs in two output modes — default (response + winning prompt) and --prompt-only (winning prompt is the deliverable, responses run internally as the test harness). Activation phrases include auto-loop this, run the prompt loop on, epistemic loop this, prompt-to-operation this, optimize this intuition, dense prompt and execute, adversarial prompt evaluator this, turn this into forced cognitive operation, generate the winning prompt, winning prompt only, prompt operation loop, /prompt-loop, /prompt-loop --prompt-only.
---

Self-contained prompt optimization engine. Takes raw/vague intuitions, forges one dense mode-classified prompt forcing a precise epistemic operation, executes it internally without meta-commentary, adversarially evaluates whether the operation was genuinely performed — not described, hedged, summarized — and structurally re-architects on failure until convergence or max iterations. A prompt earns "winning" only by surviving evaluation against real generated output — never handed over unexecuted.

## Invocation modes
**default** — final response + winning prompt + per-iteration scores + convergence verdict.
**`--prompt-only`** ("generate the winning prompt") — loop runs fully internally, every response suppressed as test-harness output, only the winning dense prompt + a compact receipt emitted.

## Operating loop (internal, max 3 iterations)

**ARCHITECT** — read the input as pointing toward the actual cognitive need, not its literal words. Resolve: `reconstructed_intent` (1-2 sentences, what the person must walk away with); `cognitive_mode` (REFRAME/ANALYTICAL/GENERATIVE/EXPLORATORY/DIAGNOSTIC/SYNTHESIS/CRITICAL); `detected_escape_hatch` (the likeliest default failure — usually describing instead of performing); `dense_prompt` (4-10 sentences: precise subject, exact operation, prescribed form/length/prohibitions, closes the escape hatch; wire in any supplied success criterion as a verifiable pass condition).

**EXECUTOR** — execute the dense prompt exactly under its Mode Playbook. First substantive word, no preamble, no self-narration. Full commitment, never describes or comments on the operation itself.

**EVALUATOR** — hostile external reviewer, score 1-10 on: (1) was the operation actually executed, not described/hedged/summarized; (2) was the escape hatch used; (3) exact prescribed form; (4) specific to this input vs. generic; (5) verifiably satisfies any given success criterion. Threshold ≥7; name the escape hatch explicitly if used.

**RE-ARCHITECT/LOOP DECISION** — ≥7 or iterations exhausted → stop, winning prompt = highest-scoring iteration. <7 with iterations left → re-architect *structurally* (never lexical patching), matched to the failure: described-not-analyzed → specify a load-bearing scaffold with named criteria; hedged → open with the position stated, task defending it; generic → embed specific input elements verbatim; escape hatch used → forbid it explicitly next pass; already failed once → escalate to a different mode + output form. Return to ARCHITECT.

## Mode playbooks
**REFRAME** — relocate perspective, don't report on the topic: name the current default frame and why it forecloses, introduce a genuinely different frame with its own logic, demonstrate it on the material. One frame, full commitment — never announce the reframe, never split weight across multiple frames.
**ANALYTICAL** — build a load-bearing scaffold before filling it (not a table of contents). Name criteria, apply consistently. No "it is important to note," no "key takeaways" close. Must withstand "why" at every step.
**GENERATIVE** — original production, not description of what exists. Give the thing itself; specificity over quantity.
**EXPLORATORY** — move through shapeless territory without imposing shape prematurely. Stay in motion, end on an opening not a conclusion. Premature closure is the failure mode.
**DIAGNOSTIC** — name the load-bearing fault, not the symptom. Test it: what else would this cause predict? No predictions = description, not diagnosis.
**SYNTHESIS** — fuse disparate inputs into something more than their sum — the unified thing, not a list of relations. Seam invisible; where tension exists, decide, don't split the difference.
**CRITICAL** — a genuine argument, not a balanced account. Take a position, use the strongest evidence, address the best counterargument directly. Failed if it reads as "fair." End on the sharpest formulation.

## Output
**default:** WINNING PROMPT (labeled) + final response + per-iteration scores with failure reasons + convergence verdict. Internal reasoning suppressed.
**`--prompt-only`:** the winning prompt alone, paste-ready, plus `mode: <mode> · score <X>/<threshold> · iterations <n> · escape hatch closed: <hatch> · <converged|best-available>`. Responses suppressed entirely; attach as collapsed evidence only if explicitly asked.

## Constraints
Executor never describes, only performs. Evaluator judges operation-performed, not topic-addressed. Re-architecture is always structurally different, never reworded. A used escape hatch is forbidden explicitly next pass. Topic addressed without the operation executed = failure regardless of quality. `--prompt-only` still runs the loop fully internally — never surfaces "winning" without real-output evaluation.
