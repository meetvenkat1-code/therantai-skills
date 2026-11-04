# Engine Forge: Codex + OpenCode backend support

## Why it failed
`forge/loop.sh` called `opencode run --agent <role> --model <model>` for every step. That goes through OpenCode's own provider config, which has no login for your ChatGPT Plus subscription (that works through the Codex CLI). So `OPENCODE_MODEL=openai/gpt-6-luna` gave "Cannot connect to API" on every planner, builder and critic call, and the loop retried.

## What changed
| file | change |
|---|---|
| `forge/agent.sh` (new) | the only place that talks to a model CLI; picks `codex` or `opencode` |
| `forge/loop.sh` | uses `agent.sh`; backend preflight; exit 3 after 3 consecutive builder failures; `agent.sh` added to protected paths |
| `forge/start.sh` | architect call goes through `agent.sh` |
| `forge/testing/fake-codex.sh` (new), `fake-opencode.sh` | test stand-ins (`FAKE_MODE=down` simulates "Cannot connect to API") |
| `forge/selftest.sh` | T10-T14 added; T1-T9 unchanged |
| `BOOTSTRAP.md`, `AGENTS.md` | docs for both backends |

Unchanged: the verifier, the template/reference, the guard, stuck handling, the agent role files.

## Backend choice (default `auto`)
1. `FORGE_BACKEND=codex|opencode` forces one.
2. Otherwise: codex if installed and `codex login status` succeeds; else opencode if installed; else exit 3 with a clear message.
3. If `OPENCODE_MODEL` is set to a non-openai provider (e.g. `opencode/...`) and no codex/forge model is set, opencode wins.

## Codex details
- Command: `codex exec --sandbox workspace-write -c approval_policy=never --skip-git-repo-check --color never -C <repo> [--model M] -` with the prompt on stdin (role instructions from `.opencode/agent/<role>.md` without frontmatter, then the task message).
- Critic: `--sandbox read-only`. Planner, builder, architect: `workspace-write` (unattended, no approval prompts).
- Model names: `openai/gpt-6-luna` becomes `gpt-6-luna` for codex automatically.
- If the verifier's headless Chromium cannot start inside the sandbox: `FORGE_CODEX_SANDBOX=danger-full-access`.
- The loop, not the agent, makes git commits (the workspace-write sandbox may protect `.git`).

## Usage
```bash
codex login
forge/start.sh engine vectorist inputs/vectorist.md                       # auto
FORGE_BACKEND=opencode forge/start.sh engine vectorist inputs/vectorist.md
FORGE_BACKEND=codex CODEX_MODEL=gpt-6-luna forge/start.sh engine vectorist inputs/vectorist.md
```
In the Codex app, drop the `OPENCODE_MODEL` env setting (or leave it: the `openai/` prefix is stripped).

## Not verified here
Real `codex exec` and `opencode run` calls (neither CLI was installed where this was built). Selftest passes 14/14 with fake binaries. First run on your machine: `npm run selftest`, then start the loop and watch for `[forge] backend: codex` and a passing preflight.
