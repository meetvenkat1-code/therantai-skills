#!/usr/bin/env bash
# forge/selftest.sh — proves the toolchain works WITHOUT a model: template sync, regression engine, loop control flow.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
FAILS=0
ok()  { echo "PASS $1"; }
bad() { echo "FAIL $1"; FAILS=$((FAILS+1)); }

# 1. template is in sync with the reference (only meaningful once committed)
if git rev-parse HEAD >/dev/null 2>&1 && git diff --quiet HEAD -- template examples/slot-grammar/prompt.md 2>/dev/null; then
  node forge/split-reference.mjs >/dev/null && git diff --quiet HEAD -- template examples/slot-grammar/prompt.md && ok "T1 template regenerates identically from reference/" || bad "T1 template differs from a fresh split of reference/ (run: npm run split)"
else echo "SKIP T1 (template not committed yet)"; fi

# 2. regression: the reference's own prompt, rebuilt through the pipeline, passes the full verifier
node forge/verify.mjs examples/slot-grammar > /tmp/forge-selftest-regress.log 2>&1 && ok "T2 slot-grammar regression ($(tail -1 /tmp/forge-selftest-regress.log))" || { bad "T2 slot-grammar regression"; grep ^FAIL /tmp/forge-selftest-regress.log; }

# 3. loop control flow with a fake opencode, in a throwaway copy of the repo
W="$(mktemp -d)"; trap 'rm -rf "$W"' EXIT
tar --exclude=node_modules --exclude=.git --exclude=tasks --exclude='out' -cf - . | (cd "$W" && tar xf -)
ln -s "$ROOT/node_modules" "$W/node_modules"; mkdir -p "$W/tasks"
( cd "$W" && git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -q -m base )
export OPENCODE_BIN="$W/forge/testing/fake-opencode.sh" CODEX_BIN="$W/forge/testing/fake-codex.sh" FAKE_SPEC="$W/forge/testing/echo.spec.json" AGENT_TIMEOUT=60
export FORGE_BACKEND=opencode FAKE_CODEX_LOG="$W/codex-argv.log"
chmod +x "$OPENCODE_BIN" "$CODEX_BIN"

cd "$W"
forge/new-engine.sh ta forge/testing/echo.prompt.md >/dev/null
FAKE_MODE=good forge/loop.sh tasks/ta 5 >/tmp/forge-st-a.log 2>&1; rc=$?
[ $rc -eq 0 ] && [ "$(git log --oneline | grep -c 'forge: tasks/ta')" -ge 1 ] && grep -q "DONE" tasks/ta/PROGRESS.md && ok "T3 loop reaches the objective and commits (exit 0)" || { bad "T3 happy path (exit $rc)"; tail -5 /tmp/forge-st-a.log; }

forge/new-engine.sh tb forge/testing/echo.prompt.md >/dev/null
FAKE_MODE=tamper forge/loop.sh tasks/tb 5 >/tmp/forge-st-b.log 2>&1; rc=$?
if git diff --quiet HEAD~0 -- template/core.js 2>/dev/null && ! grep -q "// cheat" template/core.js && grep -q "guard reverted" tasks/tb/PROGRESS.md && [ "$(cat tasks/tb/verify.sh | wc -l)" -gt 1 ]; then ok "T4 guard reverts edits to protected files (core.js, verify.sh)"; else bad "T4 guard"; tail -5 /tmp/forge-st-b.log; fi

forge/new-engine.sh tc forge/testing/echo.prompt.md >/dev/null
FAKE_MODE=idle STUCK_REPLAN=2 STUCK_ABORT=4 forge/loop.sh tasks/tc 10 >/tmp/forge-st-c.log 2>&1; rc=$?
[ $rc -eq 2 ] && [ -f tasks/tc/ESCALATE.md ] && grep -q "critic" tasks/tc/PROGRESS.md && ok "T5 stuck loop invokes the critic, then escalates (exit 2)" || { bad "T5 stuck detection (exit $rc)"; tail -5 /tmp/forge-st-c.log; }

forge/new-engine.sh td forge/testing/echo.prompt.md >/dev/null; touch tasks/td/STOP
FAKE_MODE=good forge/loop.sh tasks/td 5 >/tmp/forge-st-d.log 2>&1; rc=$?
[ $rc -eq 4 ] && ok "T6 STOP file halts the loop (exit 4)" || bad "T6 STOP file (exit $rc)"

forge/new-engine.sh te forge/testing/echo.prompt.md >/dev/null
FAKE_MODE=idle forge/loop.sh tasks/te 2 >/tmp/forge-st-e.log 2>&1; rc=$?
[ $rc -eq 1 ] && ok "T7 iteration budget stops the loop (exit 1)" || bad "T7 budget (exit $rc)"

FAKE_MODE=arch_weak forge/start.sh task "a weak goal" tw >/tmp/forge-st-w.log 2>&1; rc=$?
[ $rc -ne 0 ] && grep -q "REFUSING TO START" /tmp/forge-st-w.log && ok "T8 start.sh refuses an architect verify.sh that already passes" || { bad "T8 weak-verifier guard (exit $rc)"; tail -3 /tmp/forge-st-w.log; }

FAKE_MODE=touch forge/start.sh task "make a thing happen" tg 4 >/tmp/forge-st-g.log 2>&1; rc=$?
[ $rc -eq 0 ] && [ -f tasks/tg/done.txt ] && ok "T9 start.sh task: architect writes the contract, loop achieves it (generic goal)" || { bad "T9 generic task (exit $rc)"; tail -5 /tmp/forge-st-g.log; }

# 10. codex backend: same loop, agents run through `codex exec` (role prompt on stdin, sandbox flags, model prefix stripped)
forge/new-engine.sh tx forge/testing/echo.prompt.md >/dev/null
FORGE_BACKEND=codex OPENCODE_MODEL=openai/gpt-6-luna FAKE_MODE=good forge/loop.sh tasks/tx 5 >/tmp/forge-st-x.log 2>&1; rc=$?
if [ $rc -eq 0 ] && grep -q "agent=builder" "$FAKE_CODEX_LOG" && grep "agent=builder" "$FAKE_CODEX_LOG" | grep -q -- "--sandbox workspace-write" \
   && grep "agent=builder" "$FAKE_CODEX_LOG" | grep -q -- "--model gpt-6-luna" && ! grep -q "openai/" "$FAKE_CODEX_LOG" \
   && grep "agent=builder" "$FAKE_CODEX_LOG" | grep -q "role_lines=[1-9]"; then ok "T10 codex backend reaches the objective (workspace-write, model prefix stripped, role prompt delivered)"; else bad "T10 codex backend (exit $rc)"; tail -5 /tmp/forge-st-x.log; cat "$FAKE_CODEX_LOG" 2>/dev/null | tail -3; fi

# 11. codex critic is read-only
forge/new-engine.sh ty forge/testing/echo.prompt.md >/dev/null; : > "$FAKE_CODEX_LOG"
FORGE_BACKEND=codex FAKE_MODE=idle STUCK_REPLAN=2 STUCK_ABORT=4 forge/loop.sh tasks/ty 10 >/tmp/forge-st-y.log 2>&1; rc=$?
[ $rc -eq 2 ] && grep "agent=critic" "$FAKE_CODEX_LOG" | grep -q -- "--sandbox read-only" && ! grep "agent=builder" "$FAKE_CODEX_LOG" | grep -q "read-only" && ok "T11 codex critic runs read-only, builder does not" || { bad "T11 critic sandbox (exit $rc)"; tail -3 /tmp/forge-st-y.log; }

# 12. auto-detect: codex when logged in, opencode when not, error when neither
r1=$(FORGE_BACKEND=auto FAKE_CODEX_LOGIN=ok bash forge/agent.sh --resolve 2>&1)
r2=$(FORGE_BACKEND=auto FAKE_CODEX_LOGIN=no bash forge/agent.sh --resolve 2>&1)
r3=$(FORGE_BACKEND=auto FAKE_CODEX_LOGIN=no OPENCODE_MODEL=opencode/big-pickle bash forge/agent.sh --resolve 2>&1)
r4=$(FORGE_BACKEND=auto FAKE_CODEX_LOGIN=no OPENCODE_BIN=/nonexistent bash forge/agent.sh --resolve 2>&1); rc4=$?
[ "$r1" = codex ] && [ "$r2" = opencode ] && [ "$r3" = opencode ] && [ $rc4 -eq 3 ] && ok "T12 auto-detect (codex if logged in, else opencode, else exit 3)" || bad "T12 auto-detect ($r1 / $r2 / $r3 / rc=$rc4)"

# 13. preflight catches an unreachable backend immediately instead of looping
forge/new-engine.sh tz forge/testing/echo.prompt.md >/dev/null
FAKE_MODE=down forge/loop.sh tasks/tz 5 >/tmp/forge-st-z.log 2>&1; rc=$?
[ $rc -eq 3 ] && grep -q "preflight FAILED" /tmp/forge-st-z.log && ! grep -q "iteration 1" /tmp/forge-st-z.log && ok "T13 preflight stops at once when the backend cannot connect (exit 3)" || { bad "T13 preflight (exit $rc)"; tail -3 /tmp/forge-st-z.log; }

# 14. builder failing repeatedly (after a good preflight) aborts as a backend problem, not a task problem
forge/new-engine.sh tq forge/testing/echo.prompt.md >/dev/null
FAKE_MODE=down FORGE_SKIP_PREFLIGHT=1 AGENT_FAIL_ABORT=2 forge/loop.sh tasks/tq 9 >/tmp/forge-st-q.log 2>&1; rc=$?
[ $rc -eq 3 ] && grep -q "backend keeps failing" /tmp/forge-st-q.log && ok "T14 repeated agent failures abort with exit 3" || { bad "T14 agent-fail abort (exit $rc)"; tail -3 /tmp/forge-st-q.log; }

echo; [ $FAILS -eq 0 ] && echo "SELFTEST: all passed" || echo "SELFTEST: $FAILS failed"
exit $FAILS
