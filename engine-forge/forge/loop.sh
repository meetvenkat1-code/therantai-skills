#!/usr/bin/env bash
# forge/loop.sh — generic objective loop. Works for ANY task directory:
#   tasks/<name>/OBJECTIVE.md   fixed contract (human/architect-written, protected)
#   tasks/<name>/verify.sh      ground truth: exit 0 = objective achieved; prints "FAIL <id> <reason>" per failure
# Usage: forge/loop.sh tasks/<name> [max_iterations]
# Exit:  0 achieved | 1 budget exhausted | 2 stuck (see ESCALATE.md) | 3 setup error | 4 STOP file
# Env:   MAX_ITER=20 MAX_SECONDS=5400 AGENT_TIMEOUT=900 STUCK_REPLAN=3 STUCK_ABORT=6
#        OPENCODE_BIN=opencode OPENCODE_MODEL=provider/model (optional; default = your configured model)
set -uo pipefail

TASK=""; MAX=20; MAX_SECONDS=5400; AGENT_TIMEOUT=900; STUCK_REPLAN=3; STUCK_ABORT=6
OC="opencode"; TO=""; VRC=1; NFAIL=0; SIG=""

sha() { if command -v sha1sum >/dev/null 2>&1; then sha1sum; else shasum; fi; }
say()  { printf '[forge %s] %s\n' "$(date +%H:%M:%S)" "$*"; }
note() { printf '%s\n' "$*" >> "$TASK/PROGRESS.md"; }

oc() { # oc <agent> <message...>
  local agent="$1"; shift
  local cmd=("$OC" run --agent "$agent")
  [ -n "${OPENCODE_MODEL:-}" ] && cmd+=(--model "$OPENCODE_MODEL")
  if [ -n "$TO" ]; then "$TO" "$AGENT_TIMEOUT" "${cmd[@]}" "$@"; else "${cmd[@]}" "$@"; fi
}

run_verify() {
  bash "$TASK/verify.sh" > "$TASK/.verify.log" 2>&1; VRC=$?
  NFAIL=$(grep -c '^FAIL' "$TASK/.verify.log" || true)
  if [ "$VRC" -ne 0 ] && [ "$NFAIL" -eq 0 ]; then
    echo "FAIL verify.sh exited $VRC without a FAIL line: $(tail -n 3 "$TASK/.verify.log" | tr '\n' ' ' | cut -c1-200)" >> "$TASK/.verify.log"; NFAIL=1
  fi
  SIG=$(grep '^FAIL' "$TASK/.verify.log" | sort | sha | cut -c1-12)
}

# Protected paths: the builder cannot move the goalposts. Anything it edits here is reverted to the last commit.
guard() {
  local p changed=0
  for p in reference template/core.js template/helpers.js template/style.css template/manifest.json \
           forge/verify.mjs forge/lib forge/loop.sh forge/split-reference.mjs \
           "$TASK/OBJECTIVE.md" "$TASK/verify.sh" "$TASK/prompt.md"; do
    [ -e "$p" ] || continue
    if ! git diff --quiet HEAD -- "$p" 2>/dev/null; then
      git checkout -q HEAD -- "$p" && { say "guard: reverted edits to protected path $p"; note "- guard reverted edits to protected path \`$p\`. Do not edit it; change spec/template/build instead."; changed=1; }
    fi
  done
  return $changed
}

commit() { # commit <iteration>
  git add -A -- . >/dev/null 2>&1
  git diff --cached --quiet || git -c user.name=forge -c user.email=forge@local commit -q -m "forge: $TASK iter $1 ($NFAIL failing)"
}

has_open_tasks() { [ -s "$TASK/PLAN.md" ] && grep -q '^- \[ \]' "$TASK/PLAN.md"; }

main() {
  TASK="${1:?usage: forge/loop.sh tasks/<name> [max_iterations]}"; TASK="${TASK%/}"
  MAX="${2:-${MAX_ITER:-20}}"; MAX_SECONDS="${MAX_SECONDS:-5400}"; AGENT_TIMEOUT="${AGENT_TIMEOUT:-900}"
  STUCK_REPLAN="${STUCK_REPLAN:-3}"; STUCK_ABORT="${STUCK_ABORT:-6}"; OC="${OPENCODE_BIN:-opencode}"
  cd "$(dirname "$0")/.." || exit 3
  TO="$(command -v timeout || command -v gtimeout || true)"

  [ -f "$TASK/OBJECTIVE.md" ] || { say "missing $TASK/OBJECTIVE.md"; exit 3; }
  [ -f "$TASK/verify.sh" ]    || { say "missing $TASK/verify.sh"; exit 3; }
  command -v "$OC" >/dev/null 2>&1 || { say "'$OC' not found on PATH (set OPENCODE_BIN)"; exit 3; }
  git rev-parse --git-dir >/dev/null 2>&1 || git init -q
  git rev-parse HEAD >/dev/null 2>&1 || { git add -A; git -c user.name=forge -c user.email=forge@local commit -q -m "forge: baseline"; }
  git add -A -- "$TASK" >/dev/null 2>&1; git diff --cached --quiet || git -c user.name=forge -c user.email=forge@local commit -q -m "forge: register $TASK"
  touch "$TASK/PLAN.md" "$TASK/PROGRESS.md"

  local start; start=$(date +%s)
  run_verify
  if [ "$VRC" -eq 0 ]; then say "objective already satisfied; nothing to do"; exit 0; fi
  local prev="$SIG" same=1 i
  say "start: $NFAIL failing check(s); budget $MAX iterations / ${MAX_SECONDS}s"

  for ((i=1; i<=MAX; i++)); do
    [ -f "$TASK/STOP" ] && { say "STOP file present; halting"; exit 4; }
    if [ $(( $(date +%s) - start )) -ge "$MAX_SECONDS" ]; then say "time budget exhausted"; exit 1; fi

    note ""; note "## iteration $i ($(date +%H:%M)) - $NFAIL failing"
    grep '^FAIL' "$TASK/.verify.log" | head -n 25 | sed 's/^/- /' >> "$TASK/PROGRESS.md"

    local replan=""
    if [ "$same" -ge "$STUCK_REPLAN" ]; then
      say "stuck: same failures x$same -> critic + replan"
      note "### critic (iteration $i)"
      oc critic "Task directory: $TASK. The same failures have repeated $same times. Read AGENTS.md, $TASK/OBJECTIVE.md, $TASK/PROGRESS.md and $TASK/.verify.log. Reply with at most 15 lines: the most likely root cause, what has already been tried (from PROGRESS.md), and one concretely different approach." >> "$TASK/PROGRESS.md" 2>/dev/null || say "critic failed (continuing)"
      replan="REPLAN: the same failures repeated $same times. Read the critic note at the end of PROGRESS.md. Choose a different approach and do not repeat what PROGRESS.md records as failed."
    fi
    if ! has_open_tasks || [ -n "$replan" ]; then
      say "iteration $i: planner"
      oc planner "You are inside the Engine Forge loop. Task directory: $TASK. Read AGENTS.md, $TASK/OBJECTIVE.md, $TASK/PROGRESS.md and $TASK/.verify.log. Write $TASK/PLAN.md: an ordered checklist of small tasks ('- [ ] ...'), each finishable in one builder session; keep finished items as '- [x]'. Edit nothing else. $replan" || say "planner exited non-zero (continuing)"
      guard || true
    fi

    say "iteration $i: builder"
    oc builder "You are inside the Engine Forge loop. Task directory: $TASK. Read AGENTS.md, $TASK/OBJECTIVE.md, $TASK/PLAN.md, $TASK/PROGRESS.md and $TASK/.verify.log. Do exactly the first unchecked task in PLAN.md. Then run 'bash $TASK/verify.sh', mark the task '- [x]', and append 2-5 lines to $TASK/PROGRESS.md (what you changed, what you learned). Do not declare the objective complete: only verify.sh decides. Never edit protected paths listed in AGENTS.md." || say "builder exited non-zero (continuing)"
    guard || true

    run_verify
    commit "$i"
    if [ "$VRC" -eq 0 ]; then
      note ""; note "## DONE at iteration $i - verify.sh passes"
      commit "$i"
      say "OBJECTIVE ACHIEVED at iteration $i"; exit 0
    fi
    if [ "$SIG" = "$prev" ]; then same=$((same+1)); else same=1; prev="$SIG"; fi
    say "iteration $i: $NFAIL failing (same signature x$same)"
    if [ "$same" -ge "$STUCK_ABORT" ]; then
      { echo "# Escalation: $TASK"; echo; echo "The same $NFAIL failure(s) repeated $same times. A human decision is needed."; echo; echo '## Current failures'; grep '^FAIL' "$TASK/.verify.log"; echo; echo 'See PROGRESS.md for what was tried.'; } > "$TASK/ESCALATE.md"
      commit "$i"; say "stuck: wrote $TASK/ESCALATE.md"; exit 2
    fi
  done
  say "iteration budget exhausted ($MAX); $NFAIL still failing"; exit 1
}
main "$@"
exit $?
