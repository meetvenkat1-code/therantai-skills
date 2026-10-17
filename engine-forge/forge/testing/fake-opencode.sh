#!/usr/bin/env bash
# Stand-in for `opencode run --agent <name> ... "<message>"`, used only by forge/selftest.sh.
# FAKE_MODE: good (builder writes a valid spec) | tamper (good + edits a protected file) | idle (does nothing)
shift   # "run"
AGENT=""; MSG=""
while [ $# -gt 0 ]; do case "$1" in --agent) AGENT="$2"; shift 2;; --model) shift 2;; *) MSG="$1"; shift;; esac; done
TASK=$(printf '%s' "$MSG" | sed -E 's/.*Task directory: ([^ ]+).*/\1/; s/\.$//')
case "$AGENT" in
  architect)
    T=$(printf '%s' "$MSG" | grep -oE 'tasks/[a-z0-9-]+' | head -1)
    echo "# goal" > "$T/OBJECTIVE.md"
    if [ "${FAKE_MODE:-}" = arch_weak ]; then printf '#!/usr/bin/env bash\nexit 0\n' > "$T/verify.sh"
    else printf '#!/usr/bin/env bash\ncd "$(dirname "$0")/../.."\n[ -f %s/done.txt ] || { echo "FAIL D1 done.txt missing"; exit 1; }\necho "PASS D1 done"\n' "$T" > "$T/verify.sh"; fi;;
  planner) printf -- '- [ ] write spec.json\n' > "$TASK/PLAN.md";;
  critic)  echo "Root cause: spec.json missing. Tried: nothing. Different approach: write it from the prompt.";;
  builder)
    case "${FAKE_MODE:-good}" in
      good)   cp "$FAKE_SPEC" "$TASK/spec.json"; sed -i 's/- \[ \]/- [x]/' "$TASK/PLAN.md";;
      tamper) cp "$FAKE_SPEC" "$TASK/spec.json"; echo "// cheat" >> template/core.js; echo "exit 0" > "$TASK/verify.sh";;
      touch)  touch "$TASK/done.txt"; sed -i.bak 's/- \[ \]/- [x]/' "$TASK/PLAN.md"; rm -f "$TASK/PLAN.md.bak";;
      idle)   :;;
    esac;;
esac
exit 0
