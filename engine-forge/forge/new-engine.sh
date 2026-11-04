#!/usr/bin/env bash
# forge/new-engine.sh <slug> <prompt-file> — scaffold tasks/<slug> for the engine builder (no model involved).
set -euo pipefail
cd "$(dirname "$0")/.."
SLUG="${1:?usage: forge/new-engine.sh <slug> <prompt-file>}"; SRC="${2:?usage: forge/new-engine.sh <slug> <prompt-file>}"
[[ "$SLUG" =~ ^[a-z0-9][a-z0-9-]{1,40}$ ]] || { echo "slug must match ^[a-z0-9][a-z0-9-]{1,40}\$"; exit 1; }
[ -f "$SRC" ] || { echo "prompt file not found: $SRC"; exit 1; }
D="tasks/$SLUG"
[ -e "$D" ] && { echo "$D already exists (delete it or pick another slug)"; exit 1; }
mkdir -p "$D/out"
cp "$SRC" "$D/prompt.md"
sed "s/{{SLUG}}/$SLUG/g" forge/templates/engine-objective.md > "$D/OBJECTIVE.md"
cat > "$D/verify.sh" <<VEOF
#!/usr/bin/env bash
# Ground truth for the "$SLUG" engine. Exit 0 = objective achieved.
cd "\$(dirname "\$0")/../.." || exit 1
node forge/build.mjs tasks/$SLUG || exit 1
node forge/verify.mjs tasks/$SLUG
VEOF
chmod +x "$D/verify.sh"
: > "$D/PLAN.md"; printf '# Progress log for %s\n' "$SLUG" > "$D/PROGRESS.md"
git rev-parse HEAD >/dev/null 2>&1 || { git init -q 2>/dev/null; git add -A; git -c user.name=forge -c user.email=forge@local commit -q -m "forge: baseline"; }
git add -A -- "$D"; git diff --cached --quiet || git -c user.name=forge -c user.email=forge@local commit -q -m "forge: scaffold engine task $SLUG"
echo "created $D  (run: forge/loop.sh $D)"
