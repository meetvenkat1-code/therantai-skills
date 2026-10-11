#!/usr/bin/env python3
"""batch_process.py: incoming-batch lifecycle for standalone HTML engines.

Queue: engines/incoming_batch/*.html (top-level only; archive/ is never scanned).

Lifecycle per queued file:
  1. Scan & detect  -> slugify filename stem.
  2. Triad          -> if claude_brain/engines/<slug>/ has system.md+params.json,
                       keep it untouched (never overwrite human-curated triads).
                       Else auto-triage a DRAFT triad (heuristic brain + params).
  3. Compile        -> tools/compile_engine.py (bespoke WAVE2 chassis or generic
                       fallback); dist/<slug>-compiled.html must exist and be >2KB.
  4. Dashboard      -> upsert card in tools/dashboard_cards.json, re-render index.html.
  5. Archive        -> move source to engines/incoming_batch/archive/ (collision-safe).

Usage (repo root):
  python tools/batch_process.py            process the whole queue
  python tools/batch_process.py --dry-run  print planned actions, change nothing
"""
import argparse
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
INCOMING = ROOT / "engines" / "incoming_batch"
ARCHIVE = INCOMING / "archive"
ENGINES = ROOT / "claude_brain" / "engines"

sys.path.insert(0, str(TOOLS))
import compile_engine  # noqa: E402
import render_dashboard  # noqa: E402

PROMPT_CONST_RE = re.compile(
    r"(?:const|var|let)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"
    r"(`(?:\\.|[^`\\])*`|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\")", re.S)
NAME_HINT = re.compile(r"SYSTEM|PROMPT|SPINE|CONTRACT|TEMPLATE")
ENGINE_NAME_RE = re.compile(r"var\s+ENGINE_NAME\s*=\s*['\"]([^'\"]+)['\"]")
TAG_RE = re.compile(r"<(textarea|input|select|button)\b([^>]*)>", re.I)
ATTR_RE = re.compile(r"""([a-zA-Z-]+)\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))""")
OPTION_RE = re.compile(r"<option\b([^>]*)>(.*?)</option>", re.I | re.S)


def slugify(stem: str) -> str:
    s = stem.strip().lower()
    s = re.sub(r"[^a-z0-9_]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-_")
    return s or "engine"


def js_unescape(inner: str) -> str:
    mp = {"n": "\n", "t": "\t", "r": "\r", "`": "`", "'": "'", '"': '"', "\\": "\\"}
    out, i = [], 0
    while i < len(inner):
        ch = inner[i]
        if ch == "\\" and i + 1 < len(inner):
            out.append(mp.get(inner[i + 1], inner[i + 1]))
            i += 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def triage_prompts(text: str):
    found = []
    for m in PROMPT_CONST_RE.finditer(text):
        name, lit = m.group(1), m.group(2)
        if not NAME_HINT.search(name):
            continue
        raw = js_unescape(lit[1:-1]).strip()
        if len(raw) < 120:
            continue
        bid = re.sub(r"_+", "-", name.lower()).strip("-")
        found.append((bid, name, raw))
        if len(found) >= 12:
            break
    return found


def attr(tag: str, name: str):
    m = re.search(name + r"""\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))""", tag, re.I)
    if not m:
        return None
    return m.group(2) if m.group(2) is not None else (m.group(3) if m.group(3) is not None else m.group(4))


def triage_inputs(text: str):
    inputs, selects, actions = [], [], []
    for m in TAG_RE.finditer(text):
        tag, attrs = m.group(1).lower(), m.group(2)
        iid = attr(attrs, "id")
        if not iid:
            continue
        if tag == "textarea":
            inputs.append({"id": iid, "kind": "textarea", "label": iid,
                           "placeholder": attr(attrs, "placeholder") or ""})
        elif tag == "input":
            t = (attr(attrs, "type") or "text").lower()
            if t in ("text", "search"):
                inputs.append({"id": iid, "kind": "text", "label": iid,
                               "placeholder": attr(attrs, "placeholder") or "",
                               "default": attr(attrs, "value") or ""})
            elif t in ("number", "range"):
                entry = {"id": iid, "kind": "number", "label": iid,
                         "default": attr(attrs, "value") or ""}
                mn, mx = attr(attrs, "min"), attr(attrs, "max")
                if mn is not None:
                    entry["min"] = mn
                if mx is not None:
                    entry["max"] = mx
                inputs.append(entry)
            elif t in ("button", "submit"):
                actions.append({"id": iid, "kind": "button",
                                "label": attr(attrs, "value") or iid})
        elif tag == "select":
            sel = {"id": iid, "label": iid, "options": []}
            # re-scan only this select's inner html
            close = text.find("</select", m.end())
            inner = text[m.end():close if close != -1 else m.end()]
            for om in OPTION_RE.finditer(inner):
                val = attr(om.group(1), "value")
                label = re.sub(r"\s+", " ", om.group(2)).strip()
                sel["options"].append(val if val is not None else label)
                if re.search(r"\bselected\b", om.group(1), re.I) and "default" not in sel:
                    sel["default"] = sel["options"][-1]
            if sel["options"]:
                if "default" not in sel:
                    sel["default"] = sel["options"][0]
                selects.append(sel)
        elif tag == "button":
            inner = text[m.end():m.end() + 120].split("<", 1)[0].strip()
            actions.append({"id": iid, "kind": "button", "label": inner or iid})
    # de-dupe by id, keep order
    def dedupe(lst):
        seen, out = set(), []
        for e in lst:
            if e["id"] not in seen:
                seen.add(e["id"])
                out.append(e)
        return out
    return dedupe(inputs), dedupe(selects), dedupe(actions)


def write_triad(slug: str, src_name: str, text: str, dry: bool):
    d = ENGINES / slug
    prompts = triage_prompts(text)
    inputs, selects, actions = triage_inputs(text)
    m = ENGINE_NAME_RE.search(text)
    engine_name = m.group(1) if m else slug.replace("-", " ").replace("_", " ").title()
    if not inputs:
        inputs = [{"id": "input1", "kind": "textarea", "label": "Input", "placeholder": "Paste input…"}]
    if not actions:
        actions = [{"id": "runBtn", "kind": "button", "label": "Run"}]
    if prompts:
        blocks = "".join("```prompt:" + bid + "\n" + raw + "\n```\n\n" for bid, _, raw in prompts)
        extracted_from = "auto-triage consts: " + ", ".join(n for _, n, _ in prompts)
    else:
        blocks = ("```prompt:default\nREVIEW REQUIRED: no system-prompt constant detected "
                  "by auto-triage. Paste the engine's system prompt here, then recompile.\n```\n")
        extracted_from = "auto-triage: no const *SYSTEM/*PROMPT block found"
    system_md = ("---\nengine: " + slug + "\nsource_file: engines/incoming_batch/" + src_name
                 + "\nextracted_from: " + extracted_from + "\narchetype: Unclassified (auto-draft)\n"
                 + "review_required: true\n---\n\n# " + engine_name + " (auto-triaged draft)\n\n"
                 + "> DRAFT — heuristic extraction. Verify prompts, then set review_required: false "
                   "in params.json and recompile.\n\n" + blocks)
    params = {"engine": slug, "source_file": "engines/incoming_batch/" + src_name,
              "archetype": "Unclassified (auto-draft)", "review_required": True,
              "provider_config": {"engine_name": engine_name, "model_core": "v2"},
              "inputs": inputs, "selects": selects, "actions": actions}
    runner = {"engine": slug, "version": "0.1.0-draft",
              "source_file": "engines/incoming_batch/" + src_name,
              "review_required": True,
              "model_core": {"contract": "model-config-contract v2",
                             "canonical_config_url": "https://raw.githubusercontent.com/meetvenkat1-code/therantai-config/refs/heads/main/model.json"},
              "execution": {"topology": "single-step projection (auto-draft)",
                            "steps": [{"id": "run", "call": {"system_from": "prompt:default",
                                                             "user_recipe": "joined non-empty inputs"}}]},
              "api_routing": {"call_entry": "callModel({provider, system, user, onText})",
                              "mode": "curated chain-walk",
                              "proxy": {"attempt_order": ["/api/chat (if deployed)",
                                                          "direct provider endpoints (standalone BYOK)"]}}}
    if dry:
        print(f"  would write triad: {len(prompts)} prompt blocks, "
              f"{len(inputs)} inputs, {len(selects)} selects, {len(actions)} actions")
        return engine_name, len(prompts)
    d.mkdir(parents=True, exist_ok=True)
    (d / "system.md").write_text(system_md, encoding="utf-8")
    (d / "params.json").write_text(json.dumps(params, indent=2) + "\n", encoding="utf-8")
    (d / "runner.json").write_text(json.dumps(runner, indent=2) + "\n", encoding="utf-8")
    print(f"  triad written: {len(prompts)} prompt blocks, {len(inputs)} inputs, "
          f"{len(selects)} selects, {len(actions)} actions")
    return engine_name, len(prompts)


def archive_source(src: pathlib.Path, dry: bool):
    dest = ARCHIVE / src.name
    n = 1
    while dest.exists():
        dest = ARCHIVE / (src.stem + f"-{n}" + src.suffix)
        n += 1
    if dry:
        print(f"  would archive -> {dest.relative_to(ROOT)}")
        return dest
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest))
    print(f"  archived -> {dest.relative_to(ROOT)}")
    return dest


def upsert_dashboard_card(slug: str, title: str, archetype: str, n_prompts: int, dry: bool):
    cards = render_dashboard.load_cards()
    path = f"claude_brain/engines/{slug}/dist/{slug}-compiled.html"
    kicker = archetype if archetype != "Unclassified (auto-draft)" else "Auto-draft"
    blurb = (f"Auto-onboarded from incoming batch ({n_prompts} prompt blocks). "
             "Triad under review — verify system.md, then recompile.")
    entry = {"slug": slug, "title": title, "kicker": kicker, "blurb": blurb, "path": path}
    for i, c in enumerate(cards):
        if c.get("slug") == slug:
            cards[i] = entry
            break
    else:
        cards.append(entry)
    if dry:
        print(f"  would upsert dashboard card: {slug}")
        return
    render_dashboard.CARDS.write_text(json.dumps({"cards": cards}, indent=2) + "\n", encoding="utf-8")
    render_dashboard.main()
    print(f"  dashboard updated ({len(cards)} cards)")


def process_one(src: pathlib.Path, dry: bool):
    print(f"[{src.name}]")
    slug = slugify(src.stem)
    print(f"  slug: {slug}")
    reg = ENGINES / slug
    if (reg / "system.md").is_file() and (reg / "params.json").is_file():
        print("  triad exists — keeping human-curated files untouched")
        title = slug
        try:
            p = json.loads((reg / "params.json").read_text(encoding="utf-8"))
            title = p.get("provider_config", {}).get("engine_name", slug)
        except Exception:  # noqa: BLE001 - fall back to slug
            pass
    else:
        text = src.read_text(encoding="utf-8", errors="replace")
        title, _ = write_triad(slug, src.name, text, dry)
    dist = reg / "dist" / (slug + "-compiled.html")
    if dry:
        print(f"  would compile -> {dist.relative_to(ROOT)}")
        archive_source(src, dry=True)
        return True
    try:
        compile_engine.compile_engine(slug, dist)
    except SystemExit as e:
        print(f"  COMPILE FAILED: {e} — source left in queue")
        return False
    if not dist.is_file() or dist.stat().st_size < 2048:
        print("  COMPILE FAILED: dist missing/too small — source left in queue")
        return False
    print(f"  compiled ok ({dist.stat().st_size} bytes)")
    upsert_dashboard_card(slug, title, "Unclassified (auto-draft)", 0, dry)
    archive_source(src, dry)
    return True


def main():
    ap = argparse.ArgumentParser(description="Process engines/incoming_batch/ lifecycle queue")
    ap.add_argument("--dry-run", action="store_true", help="print actions without changing anything")
    args = ap.parse_args()
    INCOMING.mkdir(parents=True, exist_ok=True)
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    queue = sorted(p for p in INCOMING.glob("*.html") if p.is_file())
    if not queue:
        print("queue empty: nothing in engines/incoming_batch/")
        return
    ok, fail = 0, 0
    for src in queue:
        try:
            if process_one(src, args.dry_run):
                ok += 1
            else:
                fail += 1
        except Exception as e:  # noqa: BLE001 - batch must report, not crash
            print(f"  ERROR: {e} — source left in queue")
            fail += 1
    print(f"batch: {ok} processed, {fail} failed")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
