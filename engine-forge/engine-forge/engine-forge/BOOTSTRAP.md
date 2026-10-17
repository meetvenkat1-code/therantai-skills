# Engine Forge: hand-over

A reusable objective loop that runs on **Codex (ChatGPT Plus login) or OpenCode**. You give it a goal; it plans, builds and **verifies by running the thing** until the verifier passes, or a budget/stuck limit stops it.
Built-in task type: **HTML engines** (system prompt in, single-file engine out, cloned from `reference/slot-grammar-script-engine.html`). Any other goal works through the architect.

```
goal ─► OBJECTIVE.md + verify.sh ─► [ planner → builder → verify.sh ] × N ─► done | budget | stuck → ESCALATE.md
                                         ▲ critic (only when stuck) ┘        every iteration is a git commit
```

## 1. Run it yourself (terminal)
```bash
npm run setup          # playwright + chromium (once)
npm run selftest       # must end: SELFTEST: all passed   (no model needed)
forge/start.sh engine vectorist inputs/vectorist.md
```
Watch `tasks/vectorist/PROGRESS.md`. Result: `tasks/vectorist/out/vectorist.html`.

## 2. Or paste this into Codex or OpenCode and let it operate the loop
```
You are setting up and operating the Engine Forge in this repo.
1. Read AGENTS.md and BOOTSTRAP.md. Do NOT set OPENCODE_MODEL; the forge picks the backend itself (codex if logged in, else opencode).
2. Run `npm run setup`, then `npm run selftest`. It must end with "SELFTEST: all passed". If anything fails, fix the environment
   (node >= 18, git, chromium), never the tests, then re-run.
3. Launch the loop in the background so this session is not blocked:
   nohup forge/start.sh engine vectorist inputs/vectorist.md > forge.log 2>&1 &
4. Poll `tail -n 20 forge.log` every few minutes (sleep 120 between polls). Do not edit tasks/vectorist or any protected path while it runs.
5. When it exits, report: exit code, iterations used, tasks/vectorist/.verify.log, and the path tasks/vectorist/out/vectorist.html.
   If the exit code is 2, read tasks/vectorist/ESCALATE.md and tell me exactly what decision you need from me.
```

## 3. Reuse for any task
| want | command |
|---|---|
| another engine from a system prompt | `forge/start.sh engine <slug> <prompt.md>` |
| any goal in plain English | `forge/start.sh task "<goal>" [name]`: the architect writes `OBJECTIVE.md` + `verify.sh` (refuses to start if the verifier already passes), then the loop runs |
| resume / re-run a task | `forge/loop.sh tasks/<name>` |
| stop gracefully | `touch tasks/<name>/STOP` |

Exit codes: `0` achieved, `1` budget used, `2` stuck (read `ESCALATE.md`), `3` setup error, `4` STOP.
Env knobs: `MAX_ITER=20  MAX_SECONDS=5400  AGENT_TIMEOUT=900  STUCK_REPLAN=3  STUCK_ABORT=6  AGENT_FAIL_ABORT=3`. Backend/model knobs are in section 3b.

## 3b. Backends: Codex and OpenCode
All model calls go through `forge/agent.sh`. Nothing else in the repo knows which CLI is used.

| env | meaning |
|---|---|
| `FORGE_BACKEND=auto` (default) | codex if installed **and** `codex login status` succeeds, else opencode if installed, else exit 3 |
| `FORGE_BACKEND=codex` / `opencode` | force one |
| `FORGE_MODEL`, `CODEX_MODEL`, `OPENCODE_MODEL` | model name; unset = that CLI's default. A leading `openai/` is stripped for codex |
| `FORGE_CODEX_SANDBOX` | default `workspace-write`; set `danger-full-access` only if headless Chromium cannot launch inside the sandbox |
| `FORGE_SKIP_PREFLIGHT=1` | skip the one-call backend check at loop start |

Codex has no `--agent` flag, so for codex each role's instructions (`.opencode/agent/<role>.md`, frontmatter removed) are sent on stdin to `codex exec --sandbox workspace-write -c approval_policy=never -`. The critic always runs `--sandbox read-only`. Codex reads `AGENTS.md` natively.
Before iteration 1 the loop sends one tiny call to the chosen backend; if it cannot connect or is not logged in, it exits 3 immediately. If the builder call fails 3 times in a row it also exits 3 (a backend problem, not a task problem).
```bash
codex login                                   # once, with your ChatGPT account
forge/start.sh engine vectorist inputs/vectorist.md              # auto -> codex
FORGE_BACKEND=opencode forge/start.sh engine vectorist inputs/vectorist.md
FORGE_BACKEND=codex CODEX_MODEL=<model> forge/start.sh engine vectorist inputs/vectorist.md
```

## 4. Why it converges and why it can't cheat
- **The verifier is code, not a model.** Engine tasks run the built page in headless Chromium against a mocked model endpoint: exact system prompt sent, streaming render, controls, persistence, error recovery, panels, mobile overflow, console errors.
- **Contract mutation tests.** The planner declares the output rules (headers, last character, fixed replies, forbidden formatting). The verifier breaks a valid sample 8-11 ways and fails if the planner's checker accepts any. It also scans the prompt for rules the contract forgot.
- **Provenance.** Every header and fixed reply in the spec must appear verbatim in the prompt.
- **Frozen core.** Model Core, UI helpers and CSS are byte-checked against the reference. Protected files (verifier, objective, prompt, reference) are auto-reverted if an agent edits them.
- **Stuck handling.** Same failure signature 3× → read-only critic + forced replan; 6× → stop and escalate. Every iteration is committed, so `git log` / `git revert` undo any bad step.

## 5. Status of this package
Tested here (no model): reference split, regression rebuild of the slot-grammar engine (23/23), Vectorist built from a hand-written spec (24/24), a second persona (24/24), adversarial cases (lenient contract, fabricated reply, tampered core, always-true checker, syntax error all caught), loop success/guard/stuck/STOP/budget/generic-task paths (`npm run selftest`).
Backend layer tested with fake `codex`/`opencode` binaries (`npm run selftest`, T10-T14: codex dispatch and flags, read-only critic, auto-detect, preflight, repeated-failure abort).
**Not tested:** real `opencode run` and real `codex exec` calls. Check `codex exec --help` (flags used: `--sandbox`, `-c approval_policy=never`, `--skip-git-repo-check`, `--color never`, `-C`, `--model`, `-` for stdin) and `opencode run --help` against your versions. Everything CLI-specific lives in `forge/agent.sh`. Also untested: how well your MetaMuse model writes the spec; the verifier will tell you.
