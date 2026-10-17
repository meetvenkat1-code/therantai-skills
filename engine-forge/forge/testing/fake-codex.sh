#!/usr/bin/env bash
# Stand-in for `codex`, used only by forge/selftest.sh.
#   codex login status   -> exit 0 if FAKE_CODEX_LOGIN=ok (default), else 1
#   codex exec <flags> - -> reads the prompt from stdin, logs argv + role to $FAKE_CODEX_LOG,
#                           then behaves like fake-opencode for the agent named in the prompt.
LOG="${FAKE_CODEX_LOG:-/dev/null}"
case "${1:-}" in
  login) [ "${FAKE_CODEX_LOGIN:-ok}" = ok ] && { echo "Logged in using ChatGPT"; exit 0; } || { echo "Not logged in"; exit 1; };;
  exec)
    shift
    PROMPT="$(cat)"
    A=$(printf '%s' "$PROMPT" | sed -n 's/^You are acting as the "\([a-z]*\)" agent.*/\1/p' | head -1)
    ROLE=$(printf '%s' "$PROMPT" | grep -c "in the Engine Forge loop\|You are the ARCHITECT")
    echo "agent=$A role_lines=$ROLE args=$*" >> "$LOG"
    MSG=$(printf '%s' "$PROMPT" | sed -n '/^TASK MESSAGE:$/,$p' | sed '1d')
    exec "$(dirname "$0")/fake-opencode.sh" run --agent "$A" "$MSG";;
esac
exit 1
