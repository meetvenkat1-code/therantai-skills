# Engine Forge: rules for every agent

This repo runs an **objective loop**: `forge/loop.sh tasks/<name>` repeats *plan, build, verify* until `tasks/<name>/verify.sh` exits 0, or a budget/stuck limit stops it.
Only `verify.sh` decides whether the objective is achieved. Never claim completion yourself.

## Layout
- `tasks/<name>/OBJECTIVE.md` the fixed contract. `verify.sh` the ground truth. `PLAN.md` / `PROGRESS.md` your shared state. `.verify.log` the latest verify output.
- `reference/` the reference engine. `template/` the frozen template derived from it. `forge/` the tooling (build, verify, loop).
- Engine tasks only: `tasks/<name>/prompt.md` (the system prompt, input), `spec.json` (your main output), `out/<slug>.html` (built, never hand-edited).

## Protocol
1. Start every session by reading: this file, the task's `OBJECTIVE.md`, `PLAN.md`, `PROGRESS.md`, `.verify.log`. You have no memory beyond these files.
2. Do ONE small task per builder session. Run `bash tasks/<name>/verify.sh` before you finish and read the output.
3. verify.sh prints one line per check: `PASS <id> ...` or `FAIL <id> <reason>`. Fix the **reason**, never the check.
4. Record what you changed and what you learned in `PROGRESS.md` (2-5 lines). Mark finished plan items `- [x]`.
5. No network except package installs. Never `git push`. Never read or print secrets.

## Protected paths (the loop reverts any edit to these)
`reference/`, `template/core.js`, `template/helpers.js`, `template/style.css`, `template/manifest.json`, `forge/verify.mjs`, `forge/lib/`, `forge/loop.sh`, `forge/split-reference.mjs`, and per task: `OBJECTIVE.md`, `verify.sh`, `prompt.md`.
Weakening a test, editing the verifier, or hand-patching `out/*.html` to make a check pass is cheating and is undone automatically. If a check seems wrong, say so in PROGRESS.md and keep working on everything else.

## You may edit
`tasks/<name>/spec.json`, `PLAN.md`, `PROGRESS.md`; and, only when the spec genuinely cannot express what the prompt needs, `template/shell.html`, `template/engine.pre.js`, `template/engine.post.js`, `forge/build.mjs`, `forge/templates/`. Keep such changes generic (other engines must still build) and run `npm run selftest` after.

## Writing an objective (architect only)
An objective is only as good as its verify.sh. Rules:
- Measurable acceptance criteria, each one a check that can fail. No "looks good", no model self-grading.
- `verify.sh` is deterministic, offline, fast (< 2 min), exits non-zero on any failure, prints `FAIL <id> <specific reason>` per failure and `PASS <id> ...` otherwise.
- It must FAIL on an empty project. Cover behaviour (run it), not just file existence.
- OBJECTIVE.md states: goal, constraints, what may and may not be edited, acceptance criteria, how to run verify.sh.
- Do not implement the solution.
