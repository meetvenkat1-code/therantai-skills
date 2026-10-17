#!/usr/bin/env bash
# forge/start.sh — one entrypoint.
#   forge/start.sh engine <slug> <prompt-file> [max_iter]     build an HTML engine from a system prompt
#   forge/start.sh task "<goal in plain English>" [name] [max_iter]   ANY objective: the architect writes the
#                                                                     contract + verify.sh, then the loop runs
set -euo pipefail
cd "$(dirname "$0")/.."
OC="${OPENCODE_BIN:-opencode}"
case "${1:-}" in
  engine)
    forge/new-engine.sh "${2:?slug}" "${3:?prompt-file}"
    exec forge/loop.sh "tasks/$2" "${4:-}" ;;
  task)
    GOAL="${2:?goal text}"; NAME="${3:-$(echo "$GOAL" | tr 'A-Z' 'a-z' | tr -cs 'a-z0-9' '-' | cut -c1-32 | sed 's/^-//;s/-$//')}"
    D="tasks/$NAME"; [ -e "$D" ] && { echo "$D exists"; exit 1; }
    mkdir -p "$D"; : > "$D/PLAN.md"; printf '# Progress log for %s\n' "$NAME" > "$D/PROGRESS.md"
    OCM=(); [ -n "${OPENCODE_MODEL:-}" ] && OCM=(--model "$OPENCODE_MODEL")
    "$OC" run --agent architect ${OCM[@]+"${OCM[@]}"} "Goal (verbatim from the human): $GOAL

Create $D/OBJECTIVE.md and $D/verify.sh following the rules in AGENTS.md ('Writing an objective'). Do not implement the solution. verify.sh must FAIL right now." 
    [ -f "$D/OBJECTIVE.md" ] && [ -f "$D/verify.sh" ] || { echo "architect did not produce OBJECTIVE.md and verify.sh"; exit 1; }
    chmod +x "$D/verify.sh"
    if bash "$D/verify.sh" >/dev/null 2>&1; then echo "REFUSING TO START: verify.sh already passes before any work, so it cannot measure progress. Tighten it in $D/verify.sh."; exit 1; fi
    git rev-parse HEAD >/dev/null 2>&1 || { git init -q 2>/dev/null; git add -A; git -c user.name=forge -c user.email=forge@local commit -q -m "forge: baseline"; }
    git add -A -- "$D"; git diff --cached --quiet || git -c user.name=forge -c user.email=forge@local commit -q -m "forge: register task $NAME"
    exec forge/loop.sh "$D" "${4:-}" ;;
  *) sed -n '2,6p' "$0"; exit 1 ;;
esac
