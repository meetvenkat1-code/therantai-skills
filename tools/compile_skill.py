#!/usr/bin/env python3
"""compile_skill.py: compiler for the Compiled Skills track.

Boundary: this tool ONLY reads/writes claude_brain/compiled_skills/.
It never touches claude_brain/engines/, engines/, index.html, or dashboard_cards.json.
The Model Core v2 runtime is imported from compile_engine (single canonical copy).

Registry triad per skill (written by ingest_and_compile_skills.py):
  claude_brain/compiled_skills/<slug>/system.md      (```skill:body fenced SKILL.md body)
  claude_brain/engines... no — params.json + runner.json alongside system.md.

Usage:
  python tools/compile_skill.py --skill assay
  python tools/compile_skill.py --skill assay --out path/to/out.html
  python tools/compile_skill.py --all
  python tools/compile_skill.py --list
"""
import argparse
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = ROOT / "claude_brain" / "compiled_skills"

sys.path.insert(0, str(ROOT / "tools"))
from compile_engine import MODEL_CORE_JS, core_block, html_escape, js_escape_template  # noqa: E402


def list_skills():
    if not SKILLS.is_dir():
        return []
    return sorted(p.name for p in SKILLS.iterdir() if p.is_dir())


def read_skill(slug: str):
    d = SKILLS / slug
    if not d.is_dir():
        sys.exit(f"unknown skill {slug!r}; --list shows: {list_skills()}")
    system_md = (d / "system.md").read_text(encoding="utf-8")
    params = json.loads((d / "params.json").read_text(encoding="utf-8"))
    runner_path = d / "runner.json"
    runner = json.loads(runner_path.read_text(encoding="utf-8")) if runner_path.is_file() else {}
    return system_md, params, runner


def extract_skill_body(system_md: str) -> str:
    m = re.search(r"```skill:body[^\n]*\n(.*?)```", system_md, re.S)
    if not m:
        sys.exit("system.md has no ```skill:body block to extract")
    return m.group(1).strip("\n")


def chassis_skill(slug, body, params, runner):
    """Generic chat/execution chassis: transcript + skill-constant system + single callModel entry."""
    sys_text = js_escape_template(body)
    label = params.get("skill_name", slug)
    desc = params.get("description", "")
    fallback = runner.get("model_core", {}).get("fallback", {})
    core = core_block(label, fallback)
    return ("<!DOCTYPE html>\n<!-- COMPILED by tools/compile_skill.py from claude_brain/compiled_skills/"
        + slug + "/. Source: " + html_escape(params.get("source_file", ""))
        + ". DO NOT hand-edit; edit skills/ source and re-ingest. -->\n"
        '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
        "<title>" + html_escape(label) + " (skill build)</title>\n<style>\n"
        ":root{--bg:#0a0a0f;--panel:#12121a;--line:#26263a;--txt:#e8e8f0;--dim:#8a8aa3;--acc:#22c55e}\n"
        "body{background:var(--bg);color:var(--txt);font-family:system-ui,sans-serif;margin:0}\n"
        ".header{display:flex;justify-content:space-between;align-items:center;padding:.8rem 1.2rem;border-bottom:1px solid var(--line)}\n"
        ".badge{font-size:.65rem;border:1px solid var(--line);border-radius:99px;padding:.15rem .6rem;color:var(--dim)}\n"
        ".canvas{max-width:800px;margin:0 auto;padding:1.2rem}\n.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1rem;margin-bottom:1rem}\n"
        ".desc{font-size:.8rem;color:var(--dim);margin:.4rem 0 0}\n"
        ".bubble{border:1px solid var(--line);border-radius:10px;padding:.7rem 1rem;margin-top:.6rem;white-space:pre-wrap;font-size:.88rem}\n"
        ".bubble.user{border-color:var(--acc)}.who{font-size:.65rem;color:var(--dim);letter-spacing:.1em;text-transform:uppercase}\n"
        "textarea{width:100%;min-height:70px;background:#0d0d14;color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:.6rem}\n"
        "input[type=password]{background:#0d0d14;color:var(--txt);border:1px solid var(--line);border-radius:6px;padding:.4rem .6rem;width:210px}\n"
        "select{background:#0d0d14;color:var(--txt);border:1px solid var(--line);border-radius:6px;padding:.35rem}\n"
        "button{background:var(--acc);color:#04120a;border:0;border-radius:8px;padding:.55rem 1.1rem;font-weight:700;cursor:pointer;margin-top:.6rem}\n"
        "button.plain{background:#1a1a26;color:var(--txt);border:1px solid var(--line);font-weight:400}\n"
        ".keyrow{display:flex;gap:.5rem;align-items:center;flex-wrap:wrap;font-size:.72rem;color:var(--dim);margin-top:.6rem}\n"
        "</style></head>\n<body>\n"
        '<div class="header"><div><b>' + html_escape(label.upper()) + '</b> <span class="badge">skill build</span> <span class="badge" id="cfgBadge">Config: …</span></div>\n'
        '<div><select id="providerSelect"><option value="groq">Groq</option><option value="or-auto">OR · Free Router</option><option value="claude">Claude · Native</option></select></div></div>\n'
        '<div class="canvas"><div class="panel"><p class="desc">' + html_escape(desc) + '</p>\n'
        '<div class="keyrow">Keys (this browser only): <input type="password" id="key-groq" placeholder="gsk_…"> <input type="password" id="key-openrouter" placeholder="sk-or-…"> <button class="plain" id="saveKeys">Save</button></div></div>\n'
        '<div id="stream"></div>\n'
        '<div class="panel"><textarea id="chatInput" placeholder="Invoke the skill… (Enter to send, Shift+Enter for newline)"></textarea><br>\n'
        '<button id="sendBtn">Send</button> <button class="plain" id="clearBtn">Clear transcript</button></div></div>\n'
        "<script>\n" + core + "\n"
        "/* ---- Skill behavior (verbatim SKILL.md body) ---- */\n"
        "function getSkillText(){ return `" + sys_text + "`; }\n"
        "var transcript=[];\n"
        "function bubble(who,text,cls){ var d=document.createElement('div'); d.className='bubble '+(cls||''); d.innerHTML='<div class=\"who\">'+who+'</div>'; var b=document.createElement('div'); b.textContent=text; d.appendChild(b); document.getElementById('stream').appendChild(d); d.scrollIntoView(false); return b; }\n"
        "function buildUser(){ return transcript.slice(-12).map(function(t){ return t.role+': '+t.content; }).join('\\n\\n'); }\n"
        "async function send(){ var inp=document.getElementById('chatInput').value.trim(); if(!inp) return; document.getElementById('chatInput').value='';\n"
        "  transcript.push({role:'user',content:inp}); bubble('you',inp,'user');\n"
        "  var body=bubble('skill','…');\n"
        "  try{ var r=await callModel({provider:document.getElementById('providerSelect').value,system:getSkillText(),user:buildUser(),onText:function(a){body.textContent=a;}});\n"
        "    body.textContent=r.text; transcript.push({role:'assistant',content:r.text}); }\n"
        "  catch(e){ body.textContent='Error: '+e.message; } }\n"
        "document.getElementById('sendBtn').addEventListener('click',send);\n"
        "document.getElementById('chatInput').addEventListener('keydown',function(e){ if(e.key==='Enter'&&!e.shiftKey){ e.preventDefault(); send(); } });\n"
        "document.getElementById('clearBtn').addEventListener('click',function(){ transcript=[]; document.getElementById('stream').innerHTML=''; });\n"
        "document.getElementById('saveKeys').addEventListener('click',function(){ try{ localStorage.setItem('hek_groq',document.getElementById('key-groq').value); localStorage.setItem('hek_openrouter',document.getElementById('key-openrouter').value); }catch(e){} });\n"
        "try{ document.getElementById('key-groq').value=localStorage.getItem('hek_groq')||''; document.getElementById('key-openrouter').value=localStorage.getItem('hek_openrouter')||''; }catch(e){}\n"
        "fetchModelConfig();\n</script>\n</body></html>\n")


def compile_skill(slug: str, out: pathlib.Path):
    system_md, params, runner = read_skill(slug)
    html = chassis_skill(slug, extract_skill_body(system_md), params, runner)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    sha = hashlib.sha256(html.encode("utf-8")).hexdigest()[:12]
    print(f"compiled skill {slug} -> {out} ({len(html)} bytes, sha {sha})")
    return out


def batch_compile_skills():
    ok, fail = [], []
    for name in list_skills():
        d = SKILLS / name
        if not (d / "system.md").is_file() or not (d / "params.json").is_file():
            print(f"skip {name} (incomplete triad)")
            continue
        try:
            compile_skill(name, d / "dist" / (name + "-compiled.html"))
            ok.append(name)
        except SystemExit as e:
            print(f"FAIL {name}: {e}")
            fail.append(name)
        except Exception as e:  # noqa: BLE001 - batch must report, not crash
            print(f"FAIL {name}: {e}")
            fail.append(name)
    print(f"skill batch: {len(ok)} ok, {len(fail)} fail")
    return ok, fail


def main():
    ap = argparse.ArgumentParser(description="Compile registered skill -> standalone HTML")
    ap.add_argument("--skill", help="skill folder under claude_brain/compiled_skills/")
    ap.add_argument("--out", help="output HTML path (default: <skill>/dist/<skill>-compiled.html)")
    ap.add_argument("--all", action="store_true", help="batch-compile every registered skill")
    ap.add_argument("--list", action="store_true", help="list registered skills")
    args = ap.parse_args()
    if args.all:
        _, fail = batch_compile_skills()
        sys.exit(1 if fail else 0)
    if args.list or not args.skill:
        print("skills: " + ", ".join(list_skills()))
        if not args.skill:
            return
    out = pathlib.Path(args.out) if args.out else SKILLS / args.skill / "dist" / f"{args.skill}-compiled.html"
    compile_skill(args.skill, out)


if __name__ == "__main__":
    main()
