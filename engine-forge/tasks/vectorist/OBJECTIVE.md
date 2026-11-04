# OBJECTIVE: the "vectorist" engine

Deliver `tasks/vectorist/out/vectorist.html`: a single-file HTML engine that wraps the system prompt in
`tasks/vectorist/prompt.md`, built by `node forge/build.mjs tasks/vectorist` from the frozen template in `template/`
(Model Core, UI helpers and CSS come from the reference engine and must stay byte-identical).

## Your work: `tasks/vectorist/spec.json`
1. Read `prompt.md` completely. Read `forge/SPEC.md` (field reference) and `examples/slot-grammar/spec.json` (worked example).
2. Write `spec.json`. Derive every label from the prompt's identity and purpose. Capture **every machine-checkable output rule the prompt states** in `contract`:
   required section headers (verbatim), the required last character, forbidden formatting, and every fixed reply the prompt mandates (verbatim, character for character).
3. If the prompt has parameter lines like `KEY = value`, declare one control per line.
4. Write at least one realistic `tests` sample with `valid: true` that obeys every rule in the prompt. Write it yourself; it must read like a real output of this persona.
5. Run `bash tasks/vectorist/verify.sh`. Fix each `FAIL` line at its cause. Repeat.

## Acceptance
`bash tasks/vectorist/verify.sh` exits 0. It checks: spec schema and provenance (contract strings must appear in the prompt), Model Core/helpers/CSS byte-identical to the reference,
script compiles, every referenced DOM id exists, DEFAULT_PROMPT byte-identical to prompt.md, then in headless Chromium with a mocked model: labels, prompt library, controls,
exact system prompt sent, streaming render, response save and persistence, empty input behaviour, provider error recovery, panels, no mobile overflow, no console errors,
and a contract checker that accepts your valid sample and rejects every automatically mutated broken output.

## Constraints
- Do not edit protected paths (see AGENTS.md). Do not hand-edit `out/*.html`.
- Judgement items the verifier cannot check, so do them with care: labels fit the persona's voice and fit their UI slot (buttons are short); `emptyInputReply` is set only when the prompt dictates a fixed reply for empty input.
