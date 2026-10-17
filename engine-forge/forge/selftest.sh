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
export OPENCODE_BIN="$W/forge/testing/fake-opencode.sh" FAKE_SPEC="$W/forge/testing/echo.spec.json" AGENT_TIMEOUT=60
chmod +x "$OPENCODE_BIN"

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

echo; [ $FAILS -eq 0 ] && echo "SELFTEST: all passed" || echo "SELFTEST: $FAILS failed"
exit $FAILS
