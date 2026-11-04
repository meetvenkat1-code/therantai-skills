#!/usr/bin/env bash
# forge/agent.sh: the ONLY place Engine Forge talks to a model agent. Backend-neutral.
#   forge/agent.sh <agent> <message...>   run one agent (architect|planner|builder|critic) on the chosen backend
#   forge/agent.sh --resolve              print the backend that would be used (codex|opencode), exit 3 if none
#
# Backend selection  FORGE_BACKEND=auto|codex|opencode   (default auto)
#   auto: codex if installed AND logged in (`codex login status`), else opencode if installed.
#         Exception: OPENCODE_MODEL set to a non-openai provider (e.g. opencode/foo) => opencode.
# Model              FORGE_MODEL (either backend) | CODEX_MODEL | OPENCODE_MODEL   (unset = that CLI's default)
#                    A leading "openai/" is stripped for codex, so OPENCODE_MODEL=openai/gpt-5 also works there.
# Codex sandbox      builder/planner/architect: workspace-write (override: FORGE_CODEX_SANDBOX=danger-full-access
#                    if headless Chromium cannot launch inside the sandbox). critic: always read-only.
# Binaries           OPENCODE_BIN=opencode  CODEX_BIN=codex   AGENT_TIMEOUT=900
# Generic backend    FORGE_BACKEND=cmd FORGE_AGENT_CMD='<any agentic CLI>'  (never auto-selected)
#                    Gets role instructions + task on stdin, runs from the repo root, with env:
#                    FORGE_AGENT (role), FORGE_MODEL, FORGE_READONLY (1 for critic, advisory), FORGE_ROOT.
#                    The command must edit files and run bash itself (an agentic CLI, not a plain API call).
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OC_BIN="${OPENCODE_BIN:-opencode}"; CX_BIN="${CODEX_BIN:-codex}"
AGENT_TIMEOUT="${AGENT_TIMEOUT:-900}"

codex_ready()    { command -v "$CX_BIN" >/dev/null 2>&1 && "$CX_BIN" login status >/dev/null 2>&1; }
opencode_ready() { command -v "$OC_BIN" >/dev/null 2>&1; }

pick_backend() {
  case "${FORGE_BACKEND:-auto}" in
    codex)    command -v "$CX_BIN" >/dev/null 2>&1 || { echo "FORGE_BACKEND=codex but '$CX_BIN' is not on PATH (set CODEX_BIN)" >&2; return 3; }; echo codex; return 0;;
    opencode) opencode_ready || { echo "FORGE_BACKEND=opencode but '$OC_BIN' is not on PATH (set OPENCODE_BIN)" >&2; return 3; }; echo opencode; return 0;;
    cmd)      [ -n "${FORGE_AGENT_CMD:-}" ] || { echo "FORGE_BACKEND=cmd needs FORGE_AGENT_CMD" >&2; return 3; }; echo cmd; return 0;;
    auto) ;;
    *) echo "FORGE_BACKEND must be auto, codex, opencode or cmd (got '${FORGE_BACKEND}')" >&2; return 3;;
  esac
  if [ -n "${OPENCODE_MODEL:-}" ] && [ -z "${CODEX_MODEL:-}${FORGE_MODEL:-}" ]; then
    case "$OPENCODE_MODEL" in openai/*) ;; */*) opencode_ready && { echo opencode; return 0; };; esac
  fi
  codex_ready    && { echo codex; return 0; }
  opencode_ready && { echo opencode; return 0; }
  echo "no usable backend: codex is not installed/logged in (run: codex login) and opencode is not installed" >&2
  return 3
}

if [ "${1:-}" = "--resolve" ]; then pick_backend; exit $?; fi

AGENT="${1:?usage: forge/agent.sh <agent> <message...> | --resolve}"; shift
MSG="$*"
BACKEND="${FORGE_BACKEND:-auto}"
[ "$BACKEND" = auto ] && { BACKEND="$(pick_backend)" || exit 3; }

TO="$(command -v timeout || command -v gtimeout || true)"
runit() { if [ -n "$TO" ]; then "$TO" "$AGENT_TIMEOUT" "$@"; else "$@"; fi; }

case "$BACKEND" in
  opencode)
    cmd=("$OC_BIN" run --agent "$AGENT")
    m="${OPENCODE_MODEL:-${FORGE_MODEL:-}}"
    [ -n "$m" ] && cmd+=(--model "$m")
    runit "${cmd[@]}" "$MSG"
    exit $? ;;
  codex)
    f="$ROOT/.opencode/agent/$AGENT.md"
    [ -f "$f" ] || { echo "unknown agent '$AGENT' (no $f)" >&2; exit 3; }
    # role instructions = the agent file without its YAML frontmatter (codex has no --agent flag)
    role="$(awk '/^---[[:space:]]*$/ && n<2 {n++; next} n>=2 {print}' "$f")"
    sandbox="${FORGE_CODEX_SANDBOX:-workspace-write}"
    [ "$AGENT" = critic ] && sandbox="read-only"
    m="${CODEX_MODEL:-${FORGE_MODEL:-${OPENCODE_MODEL:-}}}"; m="${m#openai/}"
    cmd=("$CX_BIN" exec --sandbox "$sandbox" -c approval_policy=never --skip-git-repo-check --color never -C "$ROOT")
    [ -n "$m" ] && cmd+=(--model "$m")
    cmd+=(-)
    printf 'You are acting as the "%s" agent of the Engine Forge. Your role instructions:\n\n%s\n\n---\nTASK MESSAGE:\n%s\n' "$AGENT" "$role" "$MSG" | runit "${cmd[@]}"
    exit $? ;;
  cmd)
    f="$ROOT/.opencode/agent/$AGENT.md"
    [ -f "$f" ] || { echo "unknown agent '$AGENT' (no $f)" >&2; exit 3; }
    role="$(awk '/^---[[:space:]]*$/ && n<2 {n++; next} n>=2 {print}' "$f")"
    export FORGE_AGENT="$AGENT" FORGE_ROOT="$ROOT" FORGE_MODEL="${FORGE_MODEL:-${OPENCODE_MODEL:-}}"
    export FORGE_READONLY=0; [ "$AGENT" = critic ] && export FORGE_READONLY=1
    printf 'You are acting as the "%s" agent of the Engine Forge. Your role instructions:\n\n%s\n\n---\nTASK MESSAGE:\n%s\n' "$AGENT" "$role" "$MSG" \
      | runit bash -c 'cd "$FORGE_ROOT" && '"$FORGE_AGENT_CMD"
    exit $? ;;
esac
