#!/usr/bin/env python3
"""ingest_and_compile_skills.py: ingestion pipeline for the Compiled Skills track.

Boundary: this tool ONLY reads github-files/skills/ and reads/writes
claude_brain/compiled_skills/, tools/skills_cards.json, and skills_dashboard.html.
It never touches engines/, claude_brain/engines/, index.html, or dashboard_cards.json.

Source of truth is skills/<slug>/SKILL.md. Per-skill freshness is tracked in
claude_brain/compiled_skills/<slug>/.ingest.json ({source_sha}):
  - SKILL.md unchanged since last ingest -> SKIP (triad + dist untouched).
  - SKILL.md changed (or --force)        -> refresh triad, recompile, update dashboard.
  - Hand-edits inside compiled_skills/ triads are overwritten on refresh by design.
  - Removed skills are left alone unless --prune is passed (explicit).

Lifecycle per skill:
  1. Scan     -> skills/*/SKILL.md (lowercase-hyphen slug folders only).
  2. Triad    -> system.md (```skill:body verbatim SKILL.md body, frontmatter stripped),
                 params.json (name/description/resources/chat input/Model Core v2),
                 runner.json (single chat-turn skill execution via callModel).
  3. Compile  -> tools/compile_skill.py -> dist/<slug>-compiled.html (>2KB check).
  4. Dashboard-> upsert tools/skills_cards.json, re-render skills_dashboard.html.

Usage (repo root):
  python tools/ingest_and_compile_skills.py --all
  python tools/ingest_and_compile_skills.py --skill assay
  python tools/ingest_and_compile_skills.py --all --force
  python tools/ingest_and_compile_skills.py --all --prune
  python tools/ingest_and_compile_skills.py --dry-run
  python tools/ingest_and_compile_skills.py --check   (dashboard stale check)
"""
import argparse
import hashlib
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
SOURCE = ROOT / "skills"
REGISTRY = ROOT / "claude_brain" / "compiled_skills"
CARDS = TOOLS / "skills_cards.json"
DASHBOARD = ROOT / "skills_dashboard.html"

# SSOT governance contracts: static architecture, not executable skills.
# Never discovered, ingested, or compiled by this track; artifacts purged on every run.
EXCLUDED_SKILL_SLUGS = frozenset({
    "ui-contract",
    "hybrid-engine-contract",
    "model-config-contract",
    "model-catalog-panel",
})

# Architectural boundary guard: engine-side paths this script must never write
# (enforced in guard(): engines/, claude_brain/engines/, index.html, dashboard_cards.json).

sys.path.insert(0, str(TOOLS))
import compile_skill  # noqa: E402

NAME_RE = re.compile(r"[a-z0-9][a-z0-9-]*")
FRONTMATTER_RE = re.compile(r"---\r?\n(.*?)\r?\n---\r?\n", re.S)


def guard(path: pathlib.Path):
    """Boundary enforcement: engine-side paths are never writable from this track."""
    if path == ROOT / "index.html" or path == TOOLS / "dashboard_cards.json":
        sys.exit(f"refusing to write engine-side file: {path}")
    if ROOT / "engines" in path.parents or ROOT / "claude_brain" / "engines" in path.parents:
        sys.exit(f"refusing to write engine-side path: {path}")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_skill(skill_md: pathlib.Path):
    """Return (name, description, body). Body is markdown after frontmatter, verbatim."""
    raw = skill_md.read_bytes().replace(b"\r\n", b"\n")
    text = raw.decode("utf-8")
    m = FRONTMATTER_RE.match(text)
    meta, body = {}, text
    if m:
        for line in m.group(1).splitlines():
            key, sep, val = line.partition(":")
            if sep and not line.startswith((" ", "\t")):
                meta[key.strip()] = val.strip()
        body = text[m.end():]
    desc = " ".join(meta.get("description", "").split())
    return meta.get("name", skill_md.parent.name), desc, body.strip("\n") + "\n"


def scan_skills():
    found = []
    if not SOURCE.is_dir():
        sys.exit("skills/ directory not found")
    for d in sorted(p for p in SOURCE.iterdir() if p.is_dir() and not p.name.startswith(".")):
        if d.name in EXCLUDED_SKILL_SLUGS:
            print(f"skip {d.name} (SSOT governance contract, excluded)")
            continue
        if not NAME_RE.fullmatch(d.name):
            print(f"skip {d.name} (folder name must be lowercase-hyphen)")
            continue
        md = d / "SKILL.md"
        if not md.is_file():
            print(f"skip {d.name} (SKILL.md missing)")
            continue
        found.append(d.name)
    return found


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def write_triad(slug: str, name: str, desc: str, body: str, source_sha: str,
                resources: list, dry: bool):
    d = REGISTRY / slug
    system_md = ("---\nskill: " + slug + "\nsource_file: skills/" + slug + "/SKILL.md\n"
                 + "source_sha: " + source_sha + "\n---\n\n# " + name + " (skill behavior, verbatim)\n\n"
                 + "```skill:body\n" + body.rstrip("\n") + "\n```\n")
    params = {"skill": slug, "skill_name": name, "description": desc,
              "source_file": "skills/" + slug + "/SKILL.md", "source_sha": source_sha,
              "resources": resources,
              "provider_config": {"model_core": "v2"},
              "inputs": [{"id": "chatInput", "kind": "textarea", "label": "Invoke the skill"}]}
    runner = {"skill": slug, "version": "1.0.0",
              "execution": {"topology": "single chat-turn skill execution with transcript",
                            "steps": [{"id": "send",
                                       "call": {"system_from": "skill:body",
                                                "user_recipe": "last-12-turn transcript"}}]},
              "api_routing": {"call_entry": "callModel({provider, system, user, onText})",
                              "mode": "curated chain-walk",
                              "proxy": {"attempt_order": ["/api/chat (if deployed)",
                                                          "direct provider endpoints (standalone BYOK)"]}},
              "model_core": {"contract": "model-config-contract v2",
                             "canonical_config_url": "https://raw.githubusercontent.com/meetvenkat1-code/therantai-config/refs/heads/main/model.json"}}
    if dry:
        print(f"  would write triad ({len(body)} body chars, {len(resources)} resources)")
        return
    guard(d / "system.md")
    d.mkdir(parents=True, exist_ok=True)
    (d / "system.md").write_text(system_md, encoding="utf-8")
    (d / "params.json").write_text(json.dumps(params, indent=2) + "\n", encoding="utf-8")
    (d / "runner.json").write_text(json.dumps(runner, indent=2) + "\n", encoding="utf-8")
    (d / ".ingest.json").write_text(json.dumps({"source_sha": source_sha}, indent=2) + "\n",
                                    encoding="utf-8")
    print(f"  triad written ({len(body)} body chars)")


def render_dashboard(cards) -> str:
    def card(c):
        return ('<div class="card"><div class="kicker">Skill</div><h2>' + esc(c["title"])
                + "</h2><p>" + esc(c["blurb"]) + '</p><div class="path">' + esc(c["path"])
                + '</div><a href="' + esc(c["path"]) + '" target="_blank" rel="noopener">Launch '
                + esc(c["title"]) + "</a></div>")
    return ("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Compiled Skills Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#0a0a0f;--panel:#12121a;--line:#26263a;--txt:#e8e8f0;--dim:#8a8aa3;--acc:#22c55e}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--txt);font-family:"Space Grotesk",system-ui,sans-serif;margin:0}
.wrap{max-width:1060px;margin:0 auto;padding:2.5rem 1.5rem 4rem}
header h1{font-size:1.9rem;margin:0;letter-spacing:-.01em}
header p{color:var(--dim);font-size:.9rem;margin:.4rem 0 0}
header p a{color:var(--acc)}
.meta{display:flex;gap:.5rem;margin-top:1rem;flex-wrap:wrap}
.badge{font-size:.68rem;border:1px solid var(--line);border-radius:99px;padding:.15rem .6rem;color:var(--dim)}
.badge.ok{color:#22c55e;border-color:#22c55e}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1rem;margin-top:2rem}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:1.2rem;display:flex;flex-direction:column;gap:.5rem}
.card:hover{border-color:var(--acc)}
.card .kicker{font-size:.65rem;letter-spacing:.12em;text-transform:uppercase;color:var(--acc)}
.card h2{font-size:1.05rem;margin:0}
.card p{font-size:.82rem;color:var(--dim);margin:0;flex:1}
.card .path{font-size:.65rem;color:var(--dim);font-family:ui-monospace,Menlo,Consolas,monospace;word-break:break-all}
.card a{display:inline-block;margin-top:.4rem;background:var(--acc);color:#04120a;font-weight:700;font-size:.8rem;text-decoration:none;border-radius:8px;padding:.55rem 1rem;text-align:center}
footer{margin-top:2.5rem;color:var(--dim);font-size:.72rem}
footer code{font-size:.72rem}
</style>
</head>
<body>
<div class="wrap">
<header>
<h1>Compiled Skills Dashboard</h1>
<p>Skill execution track — chat chassis over verbatim skill behavior. Separate from the <a href="index.html">Core Engines dashboard</a>.</p>
<div class="meta"><span class="badge ok">""" + str(len(cards)) + """ / """ + str(len(cards))
            + """ compiled</span><span class="badge">Model Core v2</span><span class="badge">skill track</span></div>
</header>
<div class="grid">
""" + "\n".join(card(c) for c in cards) + """
</div>
<footer>Built from <code>claude_brain/compiled_skills/*/dist/</code> skill projections · Rebuild with <code>python tools/ingest_and_compile_skills.py --all</code> · Engine track lives in <code>index.html</code></footer>
</div>
</body>
</html>
""")


def load_cards():
    if not CARDS.is_file():
        return []
    return json.loads(CARDS.read_text(encoding="utf-8"))["cards"]


def build_card(slug: str, title: str, desc: str):
    blurb = desc if len(desc) <= 180 else desc[:177] + "..."
    return {"slug": slug, "title": title, "blurb": blurb,
            "path": f"claude_brain/compiled_skills/{slug}/dist/{slug}-compiled.html"}


def write_dashboard(cards, dry: bool):
    """Single batched write of the manifest + dashboard (called at most once per run)."""
    if dry:
        print(f"  would write skills dashboard once ({len(cards)} cards)")
        return
    guard(CARDS)
    guard(DASHBOARD)
    CARDS.write_text(json.dumps({"cards": cards}, indent=2) + "\n", encoding="utf-8")
    DASHBOARD.write_text(render_dashboard(cards), encoding="utf-8")
    print(f"skills dashboard written once ({len(cards)} cards)")


def purge_excluded(dry: bool):
    """Remove registry artifacts for excluded SSOT contracts. Returns removed slugs."""
    removed = []
    for slug in sorted(EXCLUDED_SKILL_SLUGS):
        if (REGISTRY / slug).is_dir():
            if not dry:
                guard(REGISTRY / slug / "system.md")
                shutil.rmtree(REGISTRY / slug)
            removed.append(slug)
            print(f"purged excluded contract artifacts: {slug}")
    return removed


def ingest_one(slug: str, force: bool, dry: bool):
    print(f"[{slug}]")
    md = SOURCE / slug / "SKILL.md"
    raw = md.read_bytes().replace(b"\r\n", b"\n")
    source_sha = sha_bytes(raw)
    name, desc, body = parse_skill(md)
    if name != slug:
        print(f"  WARN frontmatter name {name!r} != folder {slug!r}; using folder slug")
    resources = sorted(str(p.relative_to(SOURCE / slug)).replace("\\", "/")
                       for p in (SOURCE / slug).rglob("*")
                       if p.is_file() and p.name != "SKILL.md" and ".git" not in p.parts)
    reg = REGISTRY / slug
    ingest = {}
    if (reg / ".ingest.json").is_file():
        try:
            ingest = json.loads((reg / ".ingest.json").read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 - corrupt stamp means re-ingest
            ingest = {}
    if not force and ingest.get("source_sha") == source_sha and (reg / "dist" / (slug + "-compiled.html")).is_file():
        print("  SKIP-current (SKILL.md unchanged, dist present)")
        return "skip", None
    write_triad(slug, name or slug, desc, body, source_sha, resources, dry)
    dist = reg / "dist" / (slug + "-compiled.html")
    if dry:
        print(f"  would compile -> {dist.relative_to(ROOT)}")
        return "dry", None
    try:
        compile_skill.compile_skill(slug, dist)
    except SystemExit as e:
        print(f"  COMPILE FAILED: {e}")
        return "fail", None
    if not dist.is_file() or dist.stat().st_size < 2048:
        print("  COMPILE FAILED: dist missing/too small")
        return "fail", None
    print(f"  compiled ok ({dist.stat().st_size} bytes)")
    return "ok", {"slug": slug, "title": name or slug, "desc": desc}


def main():
    ap = argparse.ArgumentParser(description="Ingest skills/ into the Compiled Skills track")
    ap.add_argument("--skill", help="single skill slug to ingest")
    ap.add_argument("--all", action="store_true", help="ingest every skill in skills/")
    ap.add_argument("--force", action="store_true", help="rebuild even when unchanged")
    ap.add_argument("--prune", action="store_true", help="remove registry entries for deleted skills")
    ap.add_argument("--dry-run", action="store_true", help="print actions without changing anything")
    ap.add_argument("--check", action="store_true", help="fail if skills_dashboard.html is stale")
    args = ap.parse_args()
    if args.check:
        cards = load_cards()
        if not DASHBOARD.is_file() or DASHBOARD.read_text(encoding="utf-8") != render_dashboard(cards):
            sys.exit("stale: skills_dashboard.html; run python tools/ingest_and_compile_skills.py --all")
        print(f"skills dashboard current: {len(cards)} cards")
        return
    slugs = [args.skill] if args.skill else (scan_skills() if args.all or args.dry_run else [])
    if not slugs:
        print("specify --skill <slug> or --all (add --dry-run to preview)")
        return
    if args.skill and args.skill in EXCLUDED_SKILL_SLUGS:
        sys.exit(f"refusing: {args.skill} is an SSOT governance contract, excluded from the skill track")
    removed = purge_excluded(args.dry_run)
    pruned = []
    if args.prune and not args.dry_run:
        live = set(slugs)
        for d in REGISTRY.iterdir() if REGISTRY.is_dir() else []:
            if d.is_dir() and d.name not in live:
                guard(d / "system.md")
                shutil.rmtree(d)
                pruned.append(d.name)
                print(f"pruned {d.name}")
    counts = {"ok": 0, "skip": 0, "fail": 0, "dry": 0}
    fresh = {}
    for slug in slugs:
        try:
            status, info = ingest_one(slug, args.force, args.dry_run)
            counts[status] += 1
            if status == "ok" and info:
                fresh[info["slug"]] = info
        except Exception as e:  # noqa: BLE001 - batch must report, not crash
            print(f"  ERROR: {e}")
            counts["fail"] += 1
    if (fresh or removed or pruned) and not args.dry_run:
        cards = load_cards()
        for slug, info in fresh.items():
            entry = build_card(slug, info["title"], info["desc"])
            for i, c in enumerate(cards):
                if c.get("slug") == slug:
                    cards[i] = entry
                    break
            else:
                cards.append(entry)
        doomed = set(removed) | set(pruned) | set(EXCLUDED_SKILL_SLUGS)
        cards = [c for c in cards if c.get("slug") not in doomed]
        write_dashboard(cards, dry=False)
    elif args.dry_run and (fresh or removed or pruned):
        print(f"  dashboard would be written once at end (updates pending)")
    print(f"skills batch: {counts['ok']} ok, {counts['skip']} skip, "
          f"{counts['fail']} fail, {counts['dry']} dry")
    sys.exit(1 if counts["fail"] else 0)


if __name__ == "__main__":
    main()
