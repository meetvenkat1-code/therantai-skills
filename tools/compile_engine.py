#!/usr/bin/env python3
"""compile_engine.py: Station 3 compilation pipeline.

Reads a registry entry (system.md + params.json + runner.json) under
claude_brain/engines/<engine>/, merges them into the master HTML chassis,
and writes a compiled standalone projection file.

Usage (repo root):
  python tools/compile_engine.py --engine prompt-generator
  python tools/compile_engine.py --engine prompt-generator --out path/to/out.html
  python tools/compile_engine.py --list

Output default: claude_brain/engines/<engine>/dist/<engine>-compiled.html

Design notes:
- The system template is extracted VERBATIM (first fenced block in system.md).
  Placeholders like ${fragment} / ${coords.a} are preserved for the JS runtime.
  Never run .format()/f-strings over the template itself.
- No legacy scattered fetch: the chassis routes every call through one
  callModel() entry (Model Core v2 shape), trying /api/chat proxy first,
  then direct provider endpoints with BYOK from localStorage.
"""
import argparse
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENGINES = ROOT / "claude_brain" / "engines"


def list_engines():
    return sorted(p.name for p in ENGINES.iterdir() if p.is_dir()) if ENGINES.is_dir() else []


def read_registry(engine: str):
    d = ENGINES / engine
    if not d.is_dir():
        sys.exit(f"unknown engine {engine!r}; --list shows: {list_engines()}")
    system_md = (d / "system.md").read_text(encoding="utf-8")
    params = json.loads((d / "params.json").read_text(encoding="utf-8"))
    runner_path = d / "runner.json"
    runner = json.loads(runner_path.read_text(encoding="utf-8")) if runner_path.is_file() else {}
    return system_md, params, runner


def extract_template(system_md: str) -> str:
    """First fenced code block = verbatim system template."""
    m = re.search(r"```(?:[^\n]*)\n(.*?)```", system_md, re.S)
    if not m:
        sys.exit("system.md has no fenced prompt block to extract")
    return m.group(1).strip("\n")


def extract_templates(system_md: str):
    """Named fenced blocks: ```prompt:<id> (raw text) and ```js:<id> (verbatim JS).

    Station 4 (Wave 2) convention. Wave 1 files use a single untagged fence
    and keep going through extract_template(); this returns {} for them.
    """
    out = {}
    for m in re.finditer(r"```(prompt|js):([A-Za-z0-9_-]+)[^\n]*\n(.*?)```", system_md, re.S):
        out[m.group(2)] = (m.group(1), m.group(3).strip("\n"))
    return out


def js_raw_guard(t: str) -> str:
    """Make verbatim JS safe to inline: only the </script> sequence is dangerous."""
    return t.replace("</script", "<\\/script")


_DEFAULT_PROVIDERS = [
    {"id": "groq", "endpoint": "https://api.groq.com/openai/v1/chat/completions",
     "keyStorageName": "groq", "modelChain": ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]},
    {"id": "or-auto", "endpoint": "https://openrouter.ai/api/v1/chat/completions",
     "keyStorageName": "openrouter", "modelChain": ["openrouter/free"]},
]


def core_block(engine_label, fallback):
    fb = {"native_model": fallback.get("native_model", "claude-sonnet-4-6"),
          "defaultLanes": fallback.get("defaultLanes",
                                       ["groq::openai/gpt-oss-120b", "or-auto::openrouter/free"]),
          "providers": fallback.get("providers", _DEFAULT_PROVIDERS)}
    return (MODEL_CORE_JS.replace("__ENGINE_NAME__", json.dumps(engine_label))
                         .replace("__FALLBACK_JSON__", json.dumps(fb, indent=1)))


def select_options(options, default):
    out = []
    for o in options:
        sel = " selected" if o == default else ""
        out.append('<option value="' + html_escape(o) + '"' + sel + ">" + html_escape(o) + "</option>")
    return "".join(out)


# SSOT governance contracts are architecture, not executable skills — never bundled.
SKILL_EXCLUDED = frozenset({
    "ui-contract",
    "hybrid-engine-contract",
    "model-config-contract",
    "model-catalog-panel",
})

_SKILL_CACHE = None


def load_skill_registry():
    """{slug: SKILL.md body} for all active skills, sorted. Cached per process."""
    global _SKILL_CACHE
    if _SKILL_CACHE is None:
        reg = {}
        src = ROOT / "skills"
        if src.is_dir():
            for d in sorted(p for p in src.iterdir() if p.is_dir() and not p.name.startswith(".")):
                if d.name in SKILL_EXCLUDED:
                    continue
                md = d / "SKILL.md"
                if not md.is_file():
                    continue
                text = md.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
                m = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
                body = text[m.end():] if m else text
                reg[d.name] = body.strip("\n") + "\n"
        _SKILL_CACHE = reg
    return _SKILL_CACHE


def skill_head_inject() -> str:
    """Head <script>: embedded SKILL_REGISTRY + injector dropdown mount + withSkill().

    Bodies are JSON-encoded (never template literals), so ${...} examples in
    skill text stay inert. The dropdown is mounted before the first known
    run control at DOMContentLoaded, so every chassis is covered without edits.
    """
    reg = load_skill_registry()
    payload = json.dumps(reg, ensure_ascii=False).replace("</script", "<\\/script")
    return ("<script>\n/* ---- Embedded skill registry (compile-time, " + str(len(reg))
        + " active skills; SSOT contracts excluded) ---- */\n"
        + "const SKILL_REGISTRY = " + payload + ";\n"
        + "function selectedSkill(){ var el=document.getElementById('skill-injector-dropdown'); return el?el.value:'none'; }\n"
        + "function withSkill(base){ var k=selectedSkill(); if(!k||k==='none'||!SKILL_REGISTRY[k]) return base;\n"
        + "  return base + \"\\n\\n--- INJECTED SKILL PROTOCOL ---\\n\" + SKILL_REGISTRY[k]; }\n"
        + "function mountSkillInjector(){ if(document.getElementById('skill-injector-dropdown')) return;\n"
        + "  var sel=document.createElement('select'); sel.id='skill-injector-dropdown';\n"
        + "  sel.style.cssText='background:#0d0d14;color:#e8e8f0;border:1px solid #26263a;border-radius:6px;padding:.35rem;margin-left:.3rem';\n"
        + "  var base=document.createElement('option'); base.value='none'; base.textContent='Base Engine Only (No Skill)'; sel.appendChild(base);\n"
        + "  Object.keys(SKILL_REGISTRY).sort().forEach(function(k){ var o=document.createElement('option'); o.value=k; o.textContent=k; sel.appendChild(o); });\n"
        + "  var lab=document.createElement('span'); lab.textContent='Skill'; lab.style.cssText='font-size:.72rem;color:#8a8aa3;margin-left:.6rem';\n"
        + "  var wrap=document.createElement('span'); wrap.appendChild(lab); wrap.appendChild(sel);\n"
        + "  var targets=['generateBtn','genBtn','sendBtn','runBtn','map-btn','go-btn','forgeBtn','toStep3'];\n"
        + "  for(var i=0;i<targets.length;i++){ var b=document.getElementById(targets[i]); if(b&&b.parentElement){ b.parentElement.insertBefore(wrap,b); return; } } }\n"
        + "if(document.readyState==='loading'){ document.addEventListener('DOMContentLoaded',mountSkillInjector); } else { mountSkillInjector(); }\n"
        + "</script>")


def inject_skill_track(html: str) -> str:
    """Bundle the active skill registry + injector wiring into compiled engine HTML."""
    marker = "</head>"
    if marker not in html:
        sys.exit("compile: chassis HTML has no </head> for skill-track injection")
    return html.replace(marker, skill_head_inject() + "\n</head>", 1)


def js_escape_template(t: str) -> str:
    """Escape for embedding inside a JS template literal. Keeps ${...} live."""
    return t.replace("\\", "\\\\").replace("`", "\\`").replace("</script", "<\\/script")


def html_escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


MODEL_CORE_JS = """\
/* ---- Model Core v2 (registry runtime, compact) ---- */
var ENGINE_NAME = __ENGINE_NAME__;
var CANONICAL_CONFIG_URL = "https://raw.githubusercontent.com/meetvenkat1-code/therantai-config/refs/heads/main/model.json";
var LOCAL_FALLBACK_CONFIG = __FALLBACK_JSON__;
var liveModelConfig = LOCAL_FALLBACK_CONFIG;
function getKey(name){ try { return localStorage.getItem("hek_" + name) || ""; } catch(e){ return ""; } }
async function fetchModelConfig(){
  try {
    var r = await fetch(CANONICAL_CONFIG_URL + "?v=" + Date.now(), {cache:"no-store"});
    if (r.ok) { var j = await r.json(); if (j && j.providers) { liveModelConfig = j; setBadge("live"); return; } }
  } catch(e){}
  setBadge("fallback");
}
function setBadge(s){ var b = document.getElementById("cfgBadge"); if (b) { b.textContent = "Config: " + s; b.dataset.state = s; } }
function providers(){ return liveModelConfig.providers || []; }
async function readOpenAIStream(resp, onText){
  var reader = resp.body.getReader(), dec = new TextDecoder(), acc = "";
  var buf = "";
  while (true) {
    var chunk = await reader.read(); if (chunk.done) break;
    buf += dec.decode(chunk.value, {stream:true});
    var parts = buf.split("\\n\\n"); buf = parts.pop();
    for (var p of parts) {
      var line = p.trim(); if (!line.startsWith("data:")) continue;
      var data = line.slice(5).trim(); if (data === "[DONE]") continue;
      try {
        var d = JSON.parse(data);
        var t = (d.choices && d.choices[0] && (d.choices[0].delta?.content || d.choices[0].message?.content)) || "";
        if (t) { acc += t; if (onText) onText(acc); }
      } catch(e){}
    }
  }
  return acc;
}
/* callModel: ONE entry. Proxy first, then direct chain-walk. No scattered fetch. */
/* Universal skill injection: registry builds define withSkill(); elsewhere this no-ops. */
async function callModel(opts){
  try { if (typeof withSkill === 'function') { opts = Object.assign({}, opts, {system: withSkill(opts.system)}); } } catch(e){}
  var prov = providers().find(p => p.id === opts.provider) || providers()[0];
  var errors = [];
  // 1) platform proxy (Netlify) when reachable
  try {
    var pr = await fetch("/api/chat", {method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({system: opts.system, user: opts.user, provider: prov.id})});
    if (pr.ok) {
      var pj = await pr.json();
      if (pj && pj.text) { if (opts.onText) opts.onText(pj.text); return {text: pj.text, served: "proxy"}; }
    }
  } catch(e){ errors.push("proxy:" + e.message); }
  // 2) direct BYOK chain
  var chain = [prov].concat(providers().filter(p => p.id !== prov.id && !p.native));
  for (var cand of chain) {
    if (cand.native) continue; // native branch is platform-only; skip standalone
    var key = getKey(cand.keyStorageName || cand.id);
    if (!key) { errors.push(cand.id + ":missing_key"); continue; }
    try {
      var headers = {"Content-Type":"application/json", "Authorization":"Bearer " + key};
      var resp = await fetch(cand.endpoint, {method:"POST", headers,
        body: JSON.stringify({model: (cand.modelChain && cand.modelChain[0]) || "",
          messages:[{role:"system",content:opts.system},{role:"user",content:opts.user}], stream:true})});
      if (!resp.ok) { errors.push(cand.id + ":" + resp.status); continue; }
      var text = await readOpenAIStream(resp, opts.onText);
      if (text) return {text, served: cand.id};
    } catch(e){ errors.push(cand.id + ":" + e.message); }
  }
  throw new Error("all_providers_failed (" + errors.join("; ") + "). Set keys in Settings.");
}
"""


def chassis_prompt_generator(engine, template, params, runner):
    sliders = params.get("sliders", [])
    default_input = params.get("inputs", [{}])[0].get("default", "")
    fallback = (runner.get("model_core", {}).get("fallback")
                or {"native_model": "claude-sonnet-4-6",
                    "defaultLanes": ["groq::openai/gpt-oss-120b", "or-auto::openrouter/free"]})
    sliders_html = "\n".join(
        '      <div class="axis-block"><div class="axis-head"><span>{label}</span><span id="val{axis}">{dflt}</span></div>\n'
        '      <input type="range" id="slider{axis}" min="{mn}" max="{mx}" value="{dflt}" step="{step}"></div>'.format(
            label=html_escape(s.get("label", s.get("id", ""))), axis=html_escape(s.get("axis", "")),
            dflt=s.get("default", 5), mn=s.get("min", 1), mx=s.get("max", 10), step=s.get("step", 1))
        for s in sliders)
    core = (MODEL_CORE_JS.replace("__ENGINE_NAME__", json.dumps(params.get("provider_config", {}).get("engine_name", engine)))
                          .replace("__FALLBACK_JSON__", json.dumps(
                              {"native_model": fallback.get("native_model"),
                               "defaultLanes": fallback.get("defaultLanes"),
                               "providers": fallback.get("providers", [
                                   {"id": "groq", "endpoint": "https://api.groq.com/openai/v1/chat/completions",
                                    "keyStorageName": "groq", "modelChain": ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]},
                                   {"id": "or-auto", "endpoint": "https://openrouter.ai/api/v1/chat/completions",
                                    "keyStorageName": "openrouter", "modelChain": ["openrouter/free"]}])}, indent=1)))
    js_template = js_escape_template(template)
    return ("<!DOCTYPE html>\n<!-- COMPILED by tools/compile_engine.py from claude_brain/engines/" + engine
        + "/ (system.md + params.json + runner.json). Source: " + html_escape(params.get("source_file", ""))
        + ". DO NOT hand-edit; edit the registry and recompile. -->\n"
        '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
        "<title>" + html_escape(engine) + " (registry build)</title>\n<style>\n"
        ":root{--bg:#0a0a0f;--panel:#12121a;--line:#26263a;--txt:#e8e8f0;--dim:#8a8aa3;--acc:#22c55e}\n"
        "body{background:var(--bg);color:var(--txt);font-family:ui-monospace,Menlo,Consolas,monospace;margin:0}\n"
        ".header{display:flex;justify-content:space-between;align-items:center;padding:.8rem 1.2rem;border-bottom:1px solid var(--line)}\n"
        ".badge{font-size:.65rem;border:1px solid var(--line);border-radius:99px;padding:.15rem .6rem;color:var(--dim)}\n"
        ".canvas{max-width:1080px;margin:0 auto;padding:1.2rem}\n.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1rem;margin-bottom:1rem}\n"
        "textarea{width:100%;min-height:90px;background:#0d0d14;color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:.6rem}\n"
        ".axis-block{margin-top:.7rem}.axis-head{display:flex;justify-content:space-between;font-size:.75rem;color:var(--dim)}\n"
        'input[type=range]{width:100%;accent-color:var(--acc)}\n'
        ".generate-btn{background:var(--acc);color:#04120a;border:0;border-radius:8px;padding:.6rem 1rem;font-weight:700;cursor:pointer;margin-top:.8rem}\n"
        ".cards-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem}\n"
        ".card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1rem}\n"
        ".card-coords{font-size:.7rem;color:var(--dim)}.prose-body{white-space:pre-wrap;font-size:.85rem;margin-top:.6rem}\n"
        ".accordion-body{font-size:.7rem;color:var(--dim);white-space:pre-wrap;max-height:220px;overflow:auto}\n"
        "</style></head>\n<body>\n"
        '<div class="header"><div><b>' + html_escape(engine).upper() + '</b> '
        '<span class="badge">registry build</span> <span class="badge" id="cfgBadge">Config: …</span></div>\n'
        '<div><select id="providerSelect"><option value="groq">Groq</option><option value="or-auto">OR · Free Router</option></select></div></div>\n'
        '<div class="canvas"><div class="panel"><div style="font-size:.7rem;color:var(--dim)">Input anchor</div>\n'
        '<textarea id="inputAnchor">' + html_escape(default_input) + '</textarea>\n' + sliders_html + '\n'
        '<div style="font-size:.7rem;color:var(--dim);margin-top:.6rem">Presets: <span id="pv-current"></span> · opposite <span id="pv-opposite"></span> · centroid <span id="pv-centroid"></span></div>\n'
        '<button class="generate-btn" id="generateBtn">Run Full Pipeline (3 presets × 2 stages)</button></div>\n'
        '<div class="cards-grid" id="cardsGrid"><div style="color:var(--dim)">No output yet.</div></div></div>\n'
        "<script>\n" + core + "\n"
        "/* ---- Registry brain (verbatim system.md template) ---- */\n"
        "function buildStage1Prompt(fragment, coords){\n  return `" + js_template + "`;\n}\n"
        "var STAGE1_SYSTEM = \"You are a precise, obedient prompt-writing assistant.\";\n"
        "function computePresets(a,b,c){ return {current:{a,b,c},opposite:{a:11-a,b:11-b,c:11-c},centroid:{a:5,b:5,c:5}}; }\n"
        "function selProv(){ return document.getElementById('providerSelect').value; }\n"
        "function call(system,user,onPartial){ return callModel({provider:selProv(),system,user,onText:onPartial}).then(r=>r.text); }\n"
        "var PRESETS=[{key:'current',label:'Current Position'},{key:'opposite',label:'Opposite Corner'},{key:'centroid',label:'Neutral Centroid'}];\n"
        "function updatePreview(){ var a=+sliderA.value,b=+sliderB.value,c=+sliderC.value;\n"
        "  valA.textContent=a;valB.textContent=b;valC.textContent=c; var p=computePresets(a,b,c);\n"
        "  document.getElementById('pv-current').textContent='A:'+p.current.a+' B:'+p.current.b+' C:'+p.current.c;\n"
        "  document.getElementById('pv-opposite').textContent='A:'+p.opposite.a+' B:'+p.opposite.b+' C:'+p.opposite.c;\n"
        "  document.getElementById('pv-centroid').textContent='A:5 B:5 C:5'; }\n"
        "['sliderA','sliderB','sliderC'].forEach(id=>document.getElementById(id).addEventListener('input',updatePreview));\n"
        "async function runCard(key,label,coords,fragment,host){\n"
        "  var card=document.createElement('div');card.className='card';\n"
        "  card.innerHTML='<b>'+label+'</b><div class=\"card-coords\">A:'+coords.a+' B:'+coords.b+' C:'+coords.c+'</div><div class=\"prose-body\">Compiling…</div><details><summary>Compiled prompt</summary><div class=\"accordion-body\"></div></details>';\n"
        "  host.appendChild(card);\n"
        "  var compiled=await call(STAGE1_SYSTEM,buildStage1Prompt(fragment,coords),t=>card.querySelector('.accordion-body').textContent=t);\n"
        "  card.querySelector('.accordion-body').textContent=compiled;\n"
        "  card.querySelector('.prose-body').textContent='Rendering…';\n"
        "  var fin=await call(compiled,fragment,t=>card.querySelector('.prose-body').textContent=t);\n"
        "  card.querySelector('.prose-body').textContent=fin;\n"
        "}\n"
        "document.getElementById('generateBtn').addEventListener('click',async()=>{\n"
        "  var frag=document.getElementById('inputAnchor').value.trim(); if(!frag) return;\n"
        "  var p=computePresets(+sliderA.value,+sliderB.value,+sliderC.value);\n"
        "  var grid=document.getElementById('cardsGrid'); grid.innerHTML='';\n"
        "  var btn=document.getElementById('generateBtn'); btn.disabled=true; btn.textContent='Pipeline Running…';\n"
        "  await Promise.allSettled(PRESETS.map((m,i)=>new Promise(r=>setTimeout(r,i*400)).then(()=>runCard(m.key,m.label,p[m.key],frag,grid))));\n"
        "  btn.disabled=false; btn.textContent='Run Full Pipeline (3 presets × 2 stages)';\n"
        "});\n"
        "updatePreview(); fetchModelConfig();\n</script>\n</body></html>\n")


def chassis_easy_english(engine, template, params, runner):
    core = (MODEL_CORE_JS.replace("__ENGINE_NAME__", json.dumps("Easy English"))
                         .replace("__FALLBACK_JSON__", json.dumps(
                             {"native_model": "claude-sonnet-4-6",
                              "defaultLanes": ["groq::openai/gpt-oss-120b", "or-auto::openrouter/free"],
                              "providers": [
                                  {"id": "groq", "endpoint": "https://api.groq.com/openai/v1/chat/completions",
                                   "keyStorageName": "groq", "modelChain": ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]},
                                   {"id": "or-auto", "endpoint": "https://openrouter.ai/api/v1/chat/completions",
                                    "keyStorageName": "openrouter", "modelChain": ["openrouter/free"]}]}, indent=1)))
    js_template = js_escape_template(template)
    return ("<!DOCTYPE html>\n<!-- COMPILED by tools/compile_engine.py from claude_brain/engines/" + engine
        + "/ (system.md + params.json + runner.json). Source: " + html_escape(params.get("source_file", ""))
        + ". DO NOT hand-edit; edit the registry and recompile. -->\n"
        '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
        "<title>" + html_escape(engine) + " (registry build)</title>\n<style>\n"
        ":root{--bg:#0a0a0f;--panel:#12121a;--line:#26263a;--txt:#e8e8f0;--dim:#8a8aa3;--acc:#7c6ef5}\n"
        "body{background:var(--bg);color:var(--txt);font-family:system-ui,sans-serif;margin:0}\n"
        ".header{display:flex;justify-content:space-between;padding:.8rem 1.2rem;border-bottom:1px solid var(--line)}\n"
        ".badge{font-size:.65rem;border:1px solid var(--line);border-radius:99px;padding:.15rem .6rem;color:var(--dim)}\n"
        ".canvas{max-width:760px;margin:0 auto;padding:1.2rem}.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1rem;margin-top:1rem}\n"
        ".row{display:flex;gap:.5rem}input[type=text]{flex:1;background:#0d0d14;color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:.6rem}\n"
        "button{background:var(--acc);color:#fff;border:0;border-radius:8px;padding:.6rem 1rem;cursor:pointer}\n"
        "</style></head>\n<body>\n"
        '<div class="header"><div><b>EASY ENGLISH</b> <span class="badge">registry build</span> <span class="badge" id="cfgBadge">Config: …</span></div>\n'
        '<div><select id="providerSelect"><option value="groq">Groq (gpt-oss-120b)</option><option value="or-auto">OpenRouter (free)</option></select></div></div>\n'
        '<div class="canvas"><div class="row"><input type="text" id="teluguInput" placeholder="Type in Telugu…">'
        '<button id="sendBtn">Translate</button></div><div id="out"></div></div>\n'
        "<script>\n" + core + "\n"
        "/* ---- Registry brain (verbatim DEFAULT_PROMPT.body) ---- */\n"
        "function getActivePromptBody(){ return `" + js_template + "`; }\n"
        "async function runTranslate(){\n"
        "  var inp=document.getElementById('teluguInput').value.trim(); if(!inp) return;\n"
        "  var out=document.getElementById('out'); out.innerHTML='<div class=\"card\">Translating…</div>';\n"
        "  try{\n"
        "    var r=await callModel({provider:document.getElementById('providerSelect').value,system:getActivePromptBody(),user:inp});\n"
        "    var card=JSON.parse(r.text);\n"
        "    out.innerHTML='<div class=\"card\"><h3>'+card.eng+'</h3><p>'+card.pron+'</p><p>'+card.meaning+'</p></div>';\n"
        "  }catch(e){ out.innerHTML='<div class=\"card\">Error: '+String(e.message||e)+'</div>'; }\n"
        "}\n"
        "document.getElementById('sendBtn').addEventListener('click',runTranslate);\n"
        "document.getElementById('teluguInput').addEventListener('keydown',e=>{if(e.key==='Enter')runTranslate();});\n"
        "fetchModelConfig();\n</script>\n</body></html>\n")


def chassis_aperture(engine, T, params, runner):
    raw = dict((k, js_raw_guard(T[k][1])) for k in ("shared", "paramblock", "architect", "writer", "editor"))
    fallback = runner.get("model_core", {}).get("fallback", {})
    core = core_block(params.get("provider_config", {}).get("engine_name", engine), fallback)
    tones = select_options(params.get("tone_select", {}).get("options", ["reflective"]),
                           params.get("tone_select", {}).get("default", "reflective"))
    auds = select_options(params.get("audience_select", {}).get("options", ["curious newcomers"]),
                          params.get("audience_select", {}).get("default", "curious newcomers"))
    sc = params.get("slide_count", {})
    return ("<!DOCTYPE html>\n<!-- COMPILED by tools/compile_engine.py from claude_brain/engines/" + engine
        + "/ (system.md + params.json + runner.json). Source: " + html_escape(params.get("source_file", ""))
        + ". DO NOT hand-edit; edit the registry and recompile. -->\n"
        '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
        "<title>" + html_escape(engine) + " (registry build)</title>\n<style>\n"
        ":root{--bg:#0d0c0a;--panel:#161412;--line:#2c2823;--txt:#ece5d8;--dim:#9a917f;--acc:#d4a24e}\n"
        "body{background:var(--bg);color:var(--txt);font-family:Georgia,serif;margin:0}\n"
        ".header{display:flex;justify-content:space-between;align-items:center;padding:.8rem 1.2rem;border-bottom:1px solid var(--line)}\n"
        ".badge{font-size:.65rem;border:1px solid var(--line);border-radius:99px;padding:.15rem .6rem;color:var(--dim)}\n"
        ".canvas{max-width:900px;margin:0 auto;padding:1.2rem}\n.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1rem;margin-bottom:1rem}\n"
        "textarea{width:100%;min-height:70px;background:#0f0e0c;color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:.6rem}\n"
        "select{background:#0f0e0c;color:var(--txt);border:1px solid var(--line);border-radius:6px;padding:.35rem}\n"
        ".row{display:flex;gap:.8rem;align-items:center;margin-top:.7rem;flex-wrap:wrap;font-size:.8rem;color:var(--dim)}\n"
        "input[type=range]{accent-color:var(--acc)}\n"
        ".generate-btn{background:var(--acc);color:#1a1206;border:0;border-radius:8px;padding:.6rem 1.2rem;font-weight:700;cursor:pointer;margin-top:.8rem}\n"
        ".card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1rem;margin-top:.8rem}\n"
        "</style></head>\n<body>\n"
        '<div class="header"><div><b>APERTURE</b> <span class="badge">registry build · 3-stage</span> <span class="badge" id="cfgBadge">Config: …</span></div>\n'
        '<div><select id="providerSelect"><option value="groq">Groq</option><option value="or-auto">OR · Free Router</option></select></div></div>\n'
        '<div class="canvas"><div class="panel">\n'
        '<textarea id="mainInput" placeholder="Brief or topic…"></textarea>\n'
        '<div class="row"><label><input type="radio" name="mode" value="topic" checked> Generate from topic</label>\n'
        '<label><input type="radio" name="mode" value="transform"> Transform content</label>\n'
        '<label><input type="checkbox" id="autoMode" checked> Auto params</label></div>\n'
        '<div class="row"><span>Slides</span><input type="range" id="slideCount" min="' + str(sc.get("min", 3)) + '" max="' + str(sc.get("max", 10)) + '" value="' + str(sc.get("default", 6)) + '">\n'
        '<span>Tone</span><select id="toneSelect">' + tones + '</select>\n'
        '<span>Audience</span><select id="audienceSelect">' + auds + '</select></div>\n'
        '<button class="generate-btn" id="genBtn">Generate carousel</button> <span id="status" style="font-size:.75rem;color:var(--dim)"></span></div>\n'
        '<div id="slides"></div></div>\n'
        "<script>\n" + core + "\n"
        "/* ---- Registry brain js:shared (verbatim) ---- */\n" + raw["shared"] + "\n"
        "/* ---- Registry brain js:paramblock (verbatim) ---- */\n" + raw["paramblock"] + "\n"
        "/* ---- Registry brain js:architect/writer/editor (verbatim) ---- */\n" + raw["architect"] + "\n" + raw["writer"] + "\n" + raw["editor"] + "\n"
        "function $(id){ return document.getElementById(id); }\n"
        "function selProv(){ return $('providerSelect').value; }\n"
        "function call(system,user,onPartial){ return callModel({provider:selProv(),system:system,user:user,onText:onPartial}).then(function(r){return r.text;}); }\n"
        "function params(){ var auto=$('autoMode').checked; return { n: auto?'auto':$('slideCount').value, tone: auto?'auto':$('toneSelect').value, aud: auto?'auto':$('audienceSelect').value }; }\n"
        "function stripFences(t){ return String(t).replace(/```json|```/g,''); }\n"
        "function parsePlan(raw){ try{ var t=stripFences(raw); var p=JSON.parse(t.slice(t.indexOf('{'),t.lastIndexOf('}')+1)); if(p&&p.arc&&p.arc.length>=3&&p.arc.length<=10) return p; }catch(e){} return null; }\n"
        "function parseSlides(raw){ var t=stripFences(raw); try{ var a=JSON.parse(t.slice(t.indexOf('['),t.lastIndexOf(']')+1)); if(Array.isArray(a)&&a.length) return normSlides(a); }catch(e){} return normSlides(salvage(t)); }\n"
        "function salvage(t){ var objs=[],depth=0,start=-1,inStr=false,esc=false;\n"
        "  for(var i=0;i<t.length;i++){ var ch=t[i]; if(inStr){ if(esc) esc=false; else if(ch==='\\\\') esc=true; else if(ch==='\"') inStr=false; }\n"
        "  else if(ch==='\"') inStr=true; else if(ch==='{'){ if(depth===0) start=i; depth++; } else if(ch==='}'){ depth--; if(depth===0&&start>=0){ try{objs.push(JSON.parse(t.slice(start,i+1)));}catch(e){} start=-1; } } }\n"
        "  return objs; }\n"
        "function normSlides(a){ return (a||[]).map(function(s,i,arr){ return {slide:i+1,type:s.type||(i===0?'hook':(i===arr.length-1?'landing':'expansion')),label:'Slide '+(i+1)+' of '+arr.length,headline:s.headline||'',body:s.body||'',cta:s.cta||''}; }).filter(function(s){return s.headline||s.body;}); }\n"
        "function renderSlides(list,tag){ $('slides').innerHTML='<h3>'+tag+' — '+list.length+' slides</h3>'+list.map(function(s){ return '<div class=\"card\"><b>'+s.label+' · '+s.type+'</b><h4>'+s.headline+'</h4><p>'+s.body+'</p>'+(s.cta?'<p><i>'+s.cta+'</i></p>':'')+'</div>'; }).join(''); }\n"
        "async function generate(){ var input=$('mainInput').value.trim(); if(!input) return;\n"
        "  var mode=document.querySelector('input[name=mode]:checked').value;\n"
        "  var msg=(mode==='transform'?'Transform this existing content into a carousel. Preserve its actual argument — do not invent claims it does not make:\\n\\n':'Build a carousel from this topic:\\n\\n')+input;\n"
        "  var btn=$('genBtn'); btn.disabled=true; btn.textContent='Running pipeline…'; $('status').textContent='Architect…';\n"
        "  var plan=null; try{ plan=parsePlan(await call(architectSystem(),msg,function(a){$('status').textContent='Architect… '+a.length;})); }catch(e){}\n"
        "  $('status').textContent='Writer…';\n"
        "  var wuser=plan?msg+'\\n\\nPLAN (from the Architect stage):\\n'+JSON.stringify(plan):msg;\n"
        "  var t1; try{ t1=await call(writerSystem(plan),wuser,function(a){$('status').textContent='Writer… '+a.length;}); }\n"
        "  catch(e){ $('status').textContent='Writer failed: '+e.message; btn.disabled=false; btn.textContent='Generate carousel'; return; }\n"
        "  var draft=parseSlides(t1); if(!draft.length){ $('status').textContent='Writer returned no parseable slides.'; btn.disabled=false; btn.textContent='Generate carousel'; return; }\n"
        "  renderSlides(draft,'Draft'); $('status').textContent='Editor…';\n"
        "  try{ var t2=await call(editorSystem(plan),'SOURCE BRIEF:\\n'+input+'\\n\\nDRAFT SLIDES (JSON):\\n'+JSON.stringify(draft)); var ed=parseSlides(t2);\n"
        "    if(ed.length&&ed.length===draft.length){ renderSlides(ed,'Final'); $('status').textContent='Done — editor accepted ('+ed.length+' slides).'; }\n"
        "    else { $('status').textContent='Done — editor changed slide count, keeping draft.'; } }\n"
        "  catch(e){ $('status').textContent='Done — editor failed, keeping draft.'; }\n"
        "  btn.disabled=false; btn.textContent='Generate carousel'; }\n"
        "$('genBtn').addEventListener('click',generate);\n"
        "fetchModelConfig();\n</script>\n</body></html>\n")


def chassis_cognitive(engine, T, params, runner):
    raw_lenses = js_raw_guard(T["lenses"][1])
    fallback = runner.get("model_core", {}).get("fallback", {})
    core = core_block("Cognitive Shift Engine", fallback)
    views = params.get("lens_tabs", ["explain", "decode", "apps", "flow", "confuse", "invert",
                                     "steelman", "tension", "socratic", "synthesis", "contrast", "deeper"])
    tabs_html = "".join('<button class="vtab" data-v="' + v + '">' + html_escape(v) + "</button>" for v in views)
    chips_html = "".join('<button class="chip">' + html_escape(c) + "</button>"
                         for c in params.get("preset_chips", []))
    estyles = select_options(params.get("explain_styles", ["Explain Like I'm 10"]),
                             params.get("explain_styles", ["Explain Like I'm 10"])[0])
    dforms = select_options(params.get("decode_forms", ["Auto"]), "Auto")
    return ("<!DOCTYPE html>\n<!-- COMPILED by tools/compile_engine.py from claude_brain/engines/" + engine
        + "/ (system.md + params.json + runner.json). Source: " + html_escape(params.get("source_file", ""))
        + ". DO NOT hand-edit; edit the registry and recompile. -->\n"
        '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
        "<title>" + html_escape(engine) + " (registry build)</title>\n<style>\n"
        ":root{--bg:#0a0a0f;--panel:#12121a;--line:#26263a;--txt:#e8e8f0;--dim:#8a8aa3;--acc:#38bdf8}\n"
        "body{background:var(--bg);color:var(--txt);font-family:system-ui,sans-serif;margin:0}\n"
        ".header{display:flex;gap:.6rem;align-items:center;padding:.8rem 1.2rem;border-bottom:1px solid var(--line);flex-wrap:wrap}\n"
        ".badge{font-size:.65rem;border:1px solid var(--line);border-radius:99px;padding:.15rem .6rem;color:var(--dim)}\n"
        ".canvas{max-width:900px;margin:0 auto;padding:1.2rem}\n"
        "input[type=text]{flex:1;min-width:220px;background:#0d0d14;color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:.6rem}\n"
        "select{background:#0d0d14;color:var(--txt);border:1px solid var(--line);border-radius:6px;padding:.35rem}\n"
        "button{background:#1a1a26;color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:.45rem .8rem;cursor:pointer;margin:.15rem}\n"
        "button.active,button.primary{background:var(--acc);color:#04121a;border-color:var(--acc)}\n"
        ".card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1rem;margin-top:.8rem}\n"
        ".jrow{margin:.3rem 0}.jnest{margin-left:1rem}dl{margin:.3rem 0}dt{font-weight:700;color:var(--acc)}dd{margin:0 0 .4rem 1rem}\n"
        "</style></head>\n<body>\n"
        '<div class="header"><b>COGNITIVE SHIFT</b> <span class="badge">registry build · 12 lenses</span> <span class="badge" id="cfgBadge">Config: …</span>\n'
        '<select id="providerSelect"><option value="groq">Groq</option><option value="or-auto">OR · Free Router</option></select></div>\n'
        '<div class="canvas"><div><input type="text" id="concept-input" placeholder="Enter any concept…"> <button class="primary" id="go-btn">Explore</button></div>\n'
        '<div>' + chips_html + '</div>\n'
        '<div style="margin-top:.5rem"><span style="font-size:.75rem;color:var(--dim)">Challenge:</span>\n'
        '<button class="challenge-pill active" data-level="familiar">familiar</button><button class="challenge-pill" data-level="stretch">stretch</button><button class="challenge-pill" data-level="uncomfortable">uncomfortable</button>\n'
        '<select id="explainStyle">' + estyles + '</select><select id="decodeForm">' + dforms + '</select></div>\n'
        '<div style="margin-top:.5rem">' + tabs_html + '</div>\n'
        '<div id="out"><div class="card">Enter a concept to begin.</div></div></div>\n'
        "<script>\n" + core + "\n"
        "/* ---- Registry brain js:lenses (verbatim, all 12 prompts) ---- */\n" + raw_lenses + "\n"
        "var lastConcept='', lastData=null, activeChallenge='familiar', cache={};\n"
        "function selProv(){ return document.getElementById('providerSelect').value; }\n"
        "function callLens(sys,msg){ return callModel({provider:selProv(),system:sys,user:msg}).then(function(r){return r.text;}); }\n"
        "function ckFor(s){ return lastConcept+'::'+selProv()+'::'+s; }\n"
        "function stripF(t){ return String(t).replace(/```json|```/g,''); }\n"
        "function parseJ(t){ var s=stripF(t); return JSON.parse(s.slice(s.indexOf('{'),s.lastIndexOf('}')+1)); }\n"
        "function esc(t){ return String(t==null?'':t).replace(/&/g,'&amp;').replace(/</g,'&lt;'); }\n"
        "function jsonHtml(v){ if(v===null||v===undefined) return '<i>empty</i>'; if(typeof v!=='object') return esc(v); if(Array.isArray(v)) return '<ul>'+v.map(function(x){return '<li>'+jsonHtml(x)+'</li>';}).join('')+'</ul>'; var h='<dl>'; Object.keys(v).forEach(function(k){ h+='<dt>'+esc(k)+'</dt><dd>'+jsonHtml(v[k])+'</dd>'; }); return h+'</dl>'; }\n"
        "function setChallenge(l){ activeChallenge=l; document.querySelectorAll('.challenge-pill').forEach(function(b){ b.classList.toggle('active',b.dataset.level===l); }); }\n"
        "async function explore(){ var c=document.getElementById('concept-input').value.trim(); if(!c) return; cache={}; lastConcept=c;\n"
        "  var out=document.getElementById('out'); out.innerHTML='<div class=\"card\">Exploring…</div>';\n"
        "  try{ var d=parseJ(await callLens(SYS_MAIN,'Concept: '+c)); d.concept=d.concept||c; lastData=d; renderApps(); switchView('explain'); }\n"
        "  catch(e){ out.innerHTML='<div class=\"card\">Error: '+esc(e.message||e)+'</div>'; } }\n"
        "function renderApps(){ var d=lastData; document.getElementById('out').innerHTML='<h3>'+esc(d.concept)+'</h3><p>'+esc(d.summary)+'</p>'+(d.applications||[]).map(function(a){ return '<div class=\"card\"><b>'+esc(a.name)+' · '+esc(a.domain)+'</b><p>'+esc(a.bridge)+'</p><p><i>'+esc(a.wow)+'</i></p></div>'; }).join(''); }\n"
        "function switchDeeperTab(t){ loadView('deeper',t); }\n"
        "async function loadView(v,sub){ if(!lastData) return; var out=document.getElementById('out');\n"
        "  if(v==='apps'){ renderApps(); return; }\n"
        "  var sys,msg,ck;\n"
        "  if(v==='explain'){ var st=document.getElementById('explainStyle').value; sys=SYS_EXPLAIN; msg='Concept: '+lastData.concept+'\\nSummary: '+lastData.summary+'\\nLens: '+st.toUpperCase(); ck=ckFor('explain::'+st); }\n"
        "  else if(v==='decode'){ var f=document.getElementById('decodeForm').value; sys=SYS_DECODE; msg='Concept: '+lastData.concept+'\\nSummary: '+lastData.summary+(f!=='Auto'?'\\nForce form: '+f:''); ck=ckFor('decode::'+f); }\n"
        "  else if(v==='flow'){ sys=SYS_FLOW; msg='Concept: '+lastData.concept+'\\nSummary: '+lastData.summary+'\\nDomains: '+(lastData.applications||[]).map(function(a){return a.domain;}).join(', '); ck=ckFor('flow'); }\n"
        "  else if(v==='invert'){ sys=getSysInvert(activeChallenge); msg='Concept: '+lastData.concept+'\\nSummary: '+lastData.summary; ck=ckFor('invert::'+activeChallenge); }\n"
        "  else if(v==='steelman'){ sys=getSysSteelman(activeChallenge); msg='Concept: '+lastData.concept+'\\nSummary: '+lastData.summary; ck=ckFor('steelman::'+activeChallenge); }\n"
        "  else if(v==='confuse'){ sys=getSysConfuse(activeChallenge); msg='Concept: '+lastData.concept+'\\nSummary: '+lastData.summary; ck=ckFor('confuse::'+activeChallenge); }\n"
        "  else if(v==='socratic'){ sys=getSysSocratic(activeChallenge); msg='Concept: '+lastData.concept+'\\nSummary: '+lastData.summary; ck=ckFor('socratic::'+activeChallenge); }\n"
        "  else if(v==='tension'){ sys=getSysTension(activeChallenge); msg='Concept: '+lastData.concept+'\\nSummary: '+lastData.summary; ck=ckFor('tension::'+activeChallenge); }\n"
        "  else if(v==='synthesis'){ sys=getSysSynthesis(activeChallenge); msg='Concept: '+lastData.concept+'\\nSummary: '+lastData.summary; ck=ckFor('synthesis::'+activeChallenge); }\n"
        "  else if(v==='contrast'){ sys=getSysContrast(activeChallenge); msg='Concept: '+lastData.concept+'\\nSummary: '+lastData.summary; ck=ckFor('contrast'); }\n"
        "  else if(v==='deeper'){ sys=SYS_DEEPER; msg='Concept: '+lastData.concept+'\\nSummary: '+lastData.summary; ck=ckFor('deeper'); }\n"
        "  else { return; }\n"
        "  if(cache[ck]){ if(v==='deeper'){ paintDeeperTabs(cache[ck],sub||'prereq'); } else { out.innerHTML=jsonHtml(cache[ck]); } return; }\n"
        "  out.innerHTML='<div class=\"card\">Loading '+v+'…</div>';\n"
        "  try{ var d=parseJ(await callLens(sys,msg)); cache[ck]=d; if(v==='deeper'){ paintDeeperTabs(d,sub||'prereq'); } else { out.innerHTML=jsonHtml(d); } }\n"
        "  catch(e){ out.innerHTML='<div class=\"card\">Error: '+esc(e.message||e)+'</div>'; } }\n"
        "function paintDeeperTabs(d,tab){ var el=document.getElementById('out'); var body='';\n"
        "  if(tab==='prereq'){ body=jsonHtml({prerequisites:d.prerequisites,gap_statement:d.gap_statement}); }\n"
        "  else if(tab==='edge'){ body=jsonHtml({edge_works:d.edge_works,edge_breaks:d.edge_breaks,boundary:d.boundary}); }\n"
        "  else { body=jsonHtml({past:d.temporal_past,present:d.temporal_present,future:d.temporal_future}); }\n"
        "  el.innerHTML='<div><button class=\"dtab'+(tab==='prereq'?' active':'')+'\" data-dt=\"prereq\">Prerequisites</button><button class=\"dtab'+(tab==='edge'?' active':'')+'\" data-dt=\"edge\">Edge Cases</button><button class=\"dtab'+(tab==='temporal'?' active':'')+'\" data-dt=\"temporal\">Temporal Zoom</button></div><div>'+body+'</div>';\n"
        "  el.querySelectorAll('.dtab').forEach(function(b){ b.addEventListener('click',function(){ switchDeeperTab(b.dataset.dt); }); }); }\n"
        "function switchView(v){ document.querySelectorAll('.vtab').forEach(function(b){ b.classList.toggle('active',b.dataset.v===v); }); loadView(v); }\n"
        "document.getElementById('go-btn').addEventListener('click',explore);\n"
        "document.querySelectorAll('.chip').forEach(function(c){ c.addEventListener('click',function(){ document.getElementById('concept-input').value=c.textContent; explore(); }); });\n"
        "document.querySelectorAll('.challenge-pill').forEach(function(b){ b.addEventListener('click',function(){ setChallenge(b.dataset.level); }); });\n"
        "document.querySelectorAll('.vtab').forEach(function(b){ b.addEventListener('click',function(){ switchView(b.dataset.v); }); });\n"
        "document.getElementById('explainStyle').addEventListener('change',function(){ if(lastData) loadView('explain'); });\n"
        "document.getElementById('decodeForm').addEventListener('change',function(){ if(lastData) loadView('decode'); });\n"
        "fetchModelConfig();\n</script>\n</body></html>\n")


def chassis_flywheel(engine, T, params, runner):
    spine = js_escape_template(T["spine"][1])
    fan = js_escape_template(T["fan"][1])
    ramify = js_escape_template(T["ramify"][1])
    flywheel = js_escape_template(T["flywheel"][1])
    fallback = runner.get("model_core", {}).get("fallback", {})
    core = core_block("Fan / Ramify / Flywheel", fallback)
    chips = "".join('<button class="chip">' + html_escape(c) + "</button>"
                    for c in params.get("example_chips", []))
    return ("<!DOCTYPE html>\n<!-- COMPILED by tools/compile_engine.py from claude_brain/engines/" + engine
        + "/ (system.md + params.json + runner.json). Source: " + html_escape(params.get("source_file", ""))
        + ". DO NOT hand-edit; edit the registry and recompile. -->\n"
        '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
        "<title>" + html_escape(engine) + " (registry build)</title>\n<style>\n"
        ":root{--bg:#0f0e0c;--panel:#171512;--line:#2c2823;--txt:#ece5d8;--dim:#9a917f;--acc:#c9a86a}\n"
        "body{background:var(--bg);color:var(--txt);font-family:Georgia,serif;margin:0}\n"
        ".header{display:flex;justify-content:space-between;align-items:center;padding:.8rem 1.2rem;border-bottom:1px solid var(--line)}\n"
        ".badge{font-size:.65rem;border:1px solid var(--line);border-radius:99px;padding:.15rem .6rem;color:var(--dim)}\n"
        ".canvas{max-width:900px;margin:0 auto;padding:1.2rem}\n.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1rem;margin-bottom:1rem}\n"
        "textarea{width:100%;min-height:70px;background:#0d0c0a;color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:.6rem}\n"
        "select{background:#0d0c0a;color:var(--txt);border:1px solid var(--line);border-radius:6px;padding:.35rem}\n"
        "button{background:#221e18;color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:.5rem .9rem;cursor:pointer;margin:.15rem}\n"
        ".generate-btn{background:var(--acc);color:#1a1206;font-weight:700;margin-top:.7rem}\n"
        ".card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1rem;margin-top:.8rem}\n"
        ".prose{white-space:pre-wrap}\n"
        "</style></head>\n<body>\n"
        '<div class="header"><div><b>FAN / RAMIFY / FLYWHEEL</b> <span class="badge">registry build · 3 portals</span> <span class="badge" id="cfgBadge">Config: …</span></div>\n'
        '<div><select id="providerSelect"><option value="groq">Groq</option><option value="or-auto">OR · Free Router</option></select></div></div>\n'
        '<div class="canvas"><div class="panel"><textarea id="fragmentInput" placeholder="Drop the intuition or idea fragment…"></textarea>\n'
        '<div>' + chips + '</div>\n'
        '<button class="generate-btn" id="runBtn">Run Axes</button></div>\n'
        '<div id="axes"></div></div>\n'
        "<script>\n" + core + "\n"
        "/* ---- Registry brain prompt:spine/fan/ramify/flywheel (verbatim) ---- */\n"
        "const SPINE = `" + spine + "`;\n"
        "const FAN_SYSTEM = SPINE + `" + fan + "`;\n"
        "const RAMIFY_SYSTEM = SPINE + `" + ramify + "`;\n"
        "const FLYWHEEL_SYSTEM = SPINE + `" + flywheel + "`;\n"
        "var AXES=[{key:'fan',label:'Fan'},{key:'ramify',label:'Ramify'},{key:'flywheel',label:'Flywheel'}];\n"
        "function sysFor(k){ return k==='fan'?FAN_SYSTEM:(k==='ramify'?RAMIFY_SYSTEM:FLYWHEEL_SYSTEM); }\n"
        "async function runEngine(){ var frag=document.getElementById('fragmentInput').value.trim(); if(!frag) return;\n"
        "  var host=document.getElementById('axes'); host.innerHTML=''; var btn=document.getElementById('runBtn'); btn.disabled=true; btn.textContent='Turning…';\n"
        '  var um="Fragment: \\""+frag+"\\"\\n\\nRun your axis on this fragment.";\n'
        "  await Promise.all(AXES.map(async function(a){ var card=document.createElement('div'); card.className='card'; card.innerHTML='<b>'+a.label+'</b><div class=\"prose\">Turning…</div>'; host.appendChild(card);\n"
        "    var body=card.querySelector('.prose');\n"
        "    try{ var r=await callModel({provider:document.getElementById('providerSelect').value,system:sysFor(a.key),user:um,onText:function(acc){body.textContent=acc;}}); body.textContent=r.text; }\n"
        "    catch(e){ body.textContent='Error: '+e.message; } }));\n"
        "  btn.disabled=false; btn.textContent='Run Axes'; }\n"
        "document.getElementById('runBtn').addEventListener('click',runEngine);\n"
        "document.querySelectorAll('.chip').forEach(function(c){ c.addEventListener('click',function(){ document.getElementById('fragmentInput').value=c.textContent; runEngine(); }); });\n"
        "fetchModelConfig();\n</script>\n</body></html>\n")


def chassis_scenario(engine, T, params, runner):
    blocks = dict((k, js_raw_guard(T[k][1])) for k in ("decomposition", "lane-system-decomposition",
                                                      "intensity", "contract", "suggest", "lane-system-branching"))
    fallback = runner.get("model_core", {}).get("fallback", {})
    core = core_block("Scenario Forge", fallback)
    inten = params.get("intensity", {})
    ratio = params.get("ratio", {})
    roles = "".join("<option>" + html_escape(o) + "</option>"
                    for o in params.get("user_role", {}).get("options", ["Primary protagonist"]))
    pacing = params.get("pacing", {}).get("options", ["slow-burn", "moderate", "rapid"])
    pacing_html = "".join('<button data-val="' + p + '"' + (" class=\"selected\"" if p == "moderate" else "") + ">" + p + "</button>"
                          for p in pacing)
    return ("<!DOCTYPE html>\n<!-- COMPILED by tools/compile_engine.py from claude_brain/engines/" + engine
        + "/ (system.md + params.json + runner.json). Source: " + html_escape(params.get("source_file", ""))
        + ". DO NOT hand-edit; edit the registry and recompile. -->\n"
        '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
        "<title>" + html_escape(engine) + " (registry build)</title>\n<style>\n"
        ":root{--bg:#0a0a0f;--panel:#12121a;--line:#26263a;--txt:#e8e8f0;--dim:#8a8aa3;--acc:#7c6ef5}\n"
        "body{background:var(--bg);color:var(--txt);font-family:system-ui,sans-serif;margin:0}\n"
        ".header{display:flex;justify-content:space-between;align-items:center;padding:.8rem 1.2rem;border-bottom:1px solid var(--line)}\n"
        ".badge{font-size:.65rem;border:1px solid var(--line);border-radius:99px;padding:.15rem .6rem;color:var(--dim)}\n"
        ".canvas{max-width:860px;margin:0 auto;padding:1.2rem}\n.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1rem;margin-bottom:1rem;display:none}\n.panel.active{display:block}\n"
        ".stepper{display:flex;gap:.5rem;margin-bottom:1rem;font-size:.8rem}.step{padding:.3rem .7rem;border:1px solid var(--line);border-radius:99px;color:var(--dim)}.step.active{color:var(--acc);border-color:var(--acc)}.step.locked{opacity:.4}\n"
        "textarea{width:100%;min-height:56px;background:#0d0d14;color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:.6rem}\n"
        "select{background:#0d0d14;color:var(--txt);border:1px solid var(--line);border-radius:6px;padding:.35rem}\n"
        "button{background:#1a1a26;color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:.5rem 1rem;cursor:pointer;margin:.2rem}\n"
        "button.primary{background:var(--acc);color:#fff;border-color:var(--acc)}button.selected{border-color:var(--acc);color:var(--acc)}\n"
        ".card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1rem;margin-top:.8rem;cursor:default}\n"
        ".scard,.branch{cursor:pointer}.val{color:var(--acc)}\n"
        "</style></head>\n<body>\n"
        '<div class="header"><div><b>SCENARIO FORGE</b> <span class="badge">registry build · 3-step wizard</span> <span class="badge" id="cfgBadge">Config: …</span></div>\n'
        '<div><select id="providerSelect"><option value="groq">Groq</option><option value="or-auto">OR · Free Router</option></select></div></div>\n'
        '<div class="canvas"><div class="stepper"><div class="step active" data-step="1">01 Decompose</div><div class="step locked" data-step="2">02 Tune</div><div class="step locked" data-step="3">03 Play scene</div></div>\n'
        '<div class="panel active" id="panel-1"><textarea id="topicInput" placeholder="e.g. Sci-fi education system…"></textarea><br>\n'
        '<button class="primary" id="generateBtn">Generate scenarios</button><div id="scenarioList"></div></div>\n'
        '<div class="panel" id="panel-2"><div>Intensity <input type="range" id="intensity" min="' + str(inten.get("min", 1)) + '" max="' + str(inten.get("max", 5)) + '" value="' + str(inten.get("default", 3)) + '"> <span class="val" id="intensityVal">3</span><div id="intensityDesc" style="font-size:.75rem;color:var(--dim)"></div></div>\n'
        '<div id="pacingGroup" style="margin-top:.6rem">Pacing ' + pacing_html + '</div>\n'
        '<div style="margin-top:.6rem">Ratio <input type="range" id="ratio" min="' + str(ratio.get("min", 0)) + '" max="' + str(ratio.get("max", 4)) + '" value="' + str(ratio.get("default", 2)) + '"> <span class="val" id="ratioVal">Balanced</span></div>\n'
        '<div style="margin-top:.6rem">Role <select id="userRole">' + roles + '</select></div>\n'
        '<div style="margin-top:.6rem"><textarea id="extraNotes" placeholder="A detail, a constraint, a desired opening beat…"></textarea></div>\n'
        '<button class="primary" id="toStep3">Compile &amp; enter scene</button></div>\n'
        '<div class="panel" id="panel-3"><div id="contractSummary"></div><div id="chatStream"></div>\n'
        '<div style="margin-top:.6rem"><button id="suggestBtn">Suggest directions</button><div id="branchCards"></div></div>\n'
        '<div style="margin-top:.6rem"><textarea id="chatInput" rows="2" placeholder="[pause] to break frame · type to continue…"></textarea><br><button class="primary" id="sendBtn">Send</button></div></div>\n'
        '</div>\n'
        "<script>\n" + core + "\n"
        "/* ---- Registry brain (verbatim js blocks) ---- */\n" + blocks["decomposition"] + "\n" + blocks["lane-system-decomposition"] + "\n" + blocks["intensity"] + "\n" + blocks["contract"] + "\n" + blocks["suggest"] + "\n" + blocks["lane-system-branching"] + "\n"
        "var state={topic:'',selectedScenario:null,intensity:3,pacing:'moderate',ratio:2,userRole:'',notes:'',chatHistory:[],compiledContract:''};\n"
        "var RATIOLABELS=" + json.dumps(ratio.get("labels", ["Balanced"])) + ";\n"
        "function $(id){return document.getElementById(id);}\n"
        "function selProv(){return $('providerSelect').value;}\n"
        "function goTo(n){ [1,2,3].forEach(function(i){ $('panel-'+i).classList.toggle('active',i===n); document.querySelector('.step[data-step=\"'+i+'\"]').classList.toggle('active',i===n); }); }\n"
        "function unlockStep(n){ document.querySelector('.step[data-step=\"'+n+'\"]').classList.remove('locked'); }\n"
        "function parseScenarios(raw){ return String(raw).split(/---+/).map(function(b){ function g(k){ var m=b.match(new RegExp(k+':\\\\s*(.+)')); return m?m[1].trim():''; } return {title:g('TITLE'),genre:g('GENRE'),setting:g('SETTING'),conflict:g('CORE_CONFLICT'),tone:g('TONE')}; }).filter(function(s){return s.title&&s.setting;}).slice(0,4); }\n"
        "async function runDecomposition(){ var topic=$('topicInput').value.trim(); if(!topic) return; state.topic=topic;\n"
        "  $('scenarioList').innerHTML='Scanning…';\n"
        "  try{ var r=await callModel({provider:selProv(),system:LANE_SYSTEM_DECOMPOSITION,user:buildDecompositionPrompt(topic)});\n"
        "    var list=parseScenarios(r.text); if(!list.length){ $('scenarioList').textContent='No scenarios parsed.'; return; }\n"
        "    window._scen=list; $('scenarioList').innerHTML=list.map(function(s,i){ return '<div class=\"card scard\" data-i=\"'+i+'\"><b>'+s.title+'</b><p>'+s.genre+' · '+s.tone+'</p><p>'+s.setting+'</p><p><i>'+s.conflict+'</i></p></div>'; }).join('');\n"
        "    document.querySelectorAll('.scard').forEach(function(c){ c.addEventListener('click',function(){ selectScenario(window._scen[+c.dataset.i]); }); }); }\n"
        "  catch(e){ $('scenarioList').textContent='Error: '+e.message; } }\n"
        "function selectScenario(s){ state.selectedScenario=s; state.userRole=$('userRole').value; unlockStep(2); goTo(2); }\n"
        "function compileAndEnter(){ var s=state.selectedScenario; if(!s) return; state.notes=$('extraNotes').value.trim();\n"
        "  state.compiledContract=buildContractText(s,state.userRole,state.intensity,state.pacing,state.ratio,state.notes);\n"
        "  $('contractSummary').innerHTML='<b>'+s.title+'</b> · '+s.genre+' · intensity '+state.intensity+'/5 · '+state.pacing+'<br>Playing: '+state.userRole;\n"
        "  state.chatHistory=[]; $('chatStream').innerHTML='<div class=\"card\">Scene compiled. Send a message to begin.</div>'; unlockStep(3); goTo(3); }\n"
        "function appendLine(who,text){ var d=document.createElement('div'); d.className='card'; d.textContent=who+': '+text; $('chatStream').appendChild(d); return d; }\n"
        "async function sendChat(){ var inp=$('chatInput').value.trim(); if(!inp||!state.compiledContract) return; $('chatInput').value='';\n"
        "  appendLine('You',inp); state.chatHistory.push({role:'user',content:inp});\n"
        "  var ctx=state.chatHistory.slice(-10).map(function(t){return t.role+(t.lane?' ['+t.lane+']':'')+': '+t.content;}).join('\\n');\n"
        "  var msg=ctx?ctx+'\\nuser: '+inp:inp;\n"
        "  var host=appendLine('Scene','…');\n"
        "  try{ var r=await callModel({provider:selProv(),system:state.compiledContract,user:msg,onText:function(a){host.textContent=a;}});\n"
        "    host.textContent=r.text; state.chatHistory.push({role:'assistant',content:r.text}); }\n"
        "  catch(e){ host.textContent='Error: '+e.message; } }\n"
        "async function suggest(){ if(!state.selectedScenario) return; $('branchCards').innerHTML='Thinking…';\n"
        "  try{ var r=await callModel({provider:selProv(),system:LANE_SYSTEM_BRANCHING,user:buildSuggestPrompt()});\n"
        "    var branches=String(r.text).split(/---+/).map(function(b){ function g(k){var m=b.match(new RegExp(k+':\\\\s*(.+)'));return m?m[1].trim():'';} return {label:g('LABEL'),implication:g('IMPLICATION')}; }).filter(function(x){return x.label;});\n"
        "    window._br=branches; $('branchCards').innerHTML=branches.map(function(b,i){return '<div class=\"card branch\" data-i=\"'+i+'\"><b>'+b.label+'</b><p>'+b.implication+'</p></div>';}).join('');\n"
        "    document.querySelectorAll('.branch').forEach(function(c){ c.addEventListener('click',function(){ $('chatInput').value=window._br[+c.dataset.i].label; }); }); }\n"
        "  catch(e){ $('branchCards').textContent='Error: '+e.message; } }\n"
        "document.getElementById('generateBtn').addEventListener('click',runDecomposition);\n"
        "document.getElementById('intensity').addEventListener('input',function(e){ state.intensity=+e.target.value; $('intensityVal').textContent=state.intensity; $('intensityDesc').textContent=INTENSITY_DESC[state.intensity]; });\n"
        "document.getElementById('ratio').addEventListener('input',function(e){ state.ratio=+e.target.value; $('ratioVal').textContent=RATIOLABELS[state.ratio]; });\n"
        "document.querySelectorAll('#pacingGroup button').forEach(function(b){ b.addEventListener('click',function(){ document.querySelectorAll('#pacingGroup button').forEach(function(x){x.classList.remove('selected');}); b.classList.add('selected'); state.pacing=b.dataset.val; }); });\n"
        "document.getElementById('userRole').addEventListener('change',function(e){ state.userRole=e.target.value; });\n"
        "document.getElementById('toStep3').addEventListener('click',compileAndEnter);\n"
        "document.getElementById('sendBtn').addEventListener('click',sendChat);\n"
        "document.getElementById('suggestBtn').addEventListener('click',suggest);\n"
        "state.userRole=$('userRole').value; $('intensityDesc').textContent=INTENSITY_DESC[3]; $('ratioVal').textContent=RATIOLABELS[2]; goTo(1); fetchModelConfig();\n</script>\n</body></html>\n")


def chassis_dimensions(engine, T, params, runner):
    tax = js_raw_guard(T["taxonomy"][1])
    mapping = js_raw_guard(T["mapping"][1])
    expansion = js_raw_guard(T["expansion"][1])
    fallback = runner.get("model_core", {}).get("fallback", {})
    core = core_block("Dimensions", fallback)
    lanes = fallback.get("defaultLanes", ["groq::openai/gpt-oss-120b", "or-auto::openrouter/free"])
    lane_checks = "".join(
        '<label><input type="checkbox" class="lanebox" data-lane="' + html_escape(l) + '" checked> '
        + html_escape(l) + "</label>" for l in lanes)
    ph = params.get("inputs", [{}])[0].get("placeholder", "Paste a thinking fragment…")
    return ("<!DOCTYPE html>\n<!-- COMPILED by tools/compile_engine.py from claude_brain/engines/" + engine
        + "/ (system.md + params.json + runner.json). Source: " + html_escape(params.get("source_file", ""))
        + ". DO NOT hand-edit; edit the registry and recompile. -->\n"
        '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
        "<title>" + html_escape(engine) + " (registry build)</title>\n<style>\n"
        ":root{--bg:#0a0a0f;--panel:#12121a;--line:#26263a;--txt:#e8e8f0;--dim:#8a8aa3;--acc:#6366f1}\n"
        "body{background:var(--bg);color:var(--txt);font-family:system-ui,sans-serif;margin:0}\n"
        ".header{display:flex;justify-content:space-between;align-items:center;padding:.8rem 1.2rem;border-bottom:1px solid var(--line)}\n"
        ".badge{font-size:.65rem;border:1px solid var(--line);border-radius:99px;padding:.15rem .6rem;color:var(--dim)}\n"
        ".canvas{max-width:960px;margin:0 auto;padding:1.2rem}\n.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1rem;margin-bottom:1rem}\n"
        "textarea{width:100%;min-height:70px;background:#0d0d14;color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:.6rem}\n"
        ".row{display:flex;gap:.8rem;align-items:center;margin-top:.7rem;flex-wrap:wrap;font-size:.8rem;color:var(--dim)}\n"
        "button{background:var(--acc);color:#fff;border:0;border-radius:8px;padding:.55rem 1.1rem;font-weight:700;cursor:pointer}\n"
        "button.plain{background:#1a1a26;color:var(--txt);border:1px solid var(--line);font-weight:400;padding:.3rem .7rem;margin:.15rem}\n"
        ".card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1rem;margin-top:.8rem}\n"
        ".card.error{border-color:#f43f5e}.match{border-top:1px solid var(--line);padding:.6rem 0}\n"
        ".str{font-size:.65rem;border:1px solid var(--line);border-radius:99px;padding:.1rem .5rem}\n"
        ".str-high{color:#22c55e;border-color:#22c55e}.str-medium{color:#f59e0b;border-color:#f59e0b}.str-low{color:var(--dim)}\n"
        ".xout{white-space:pre-wrap;font-size:.85rem;margin-top:.4rem}\n"
        "</style></head>\n<body>\n"
        '<div class="header"><div><b>DIMENSIONS</b> <span class="badge">registry build · multi-lane mapping</span> <span class="badge" id="cfgBadge">Config: …</span></div></div>\n'
        '<div class="canvas"><div class="panel"><textarea id="map-input" placeholder="' + html_escape(ph) + '"></textarea>\n'
        '<div class="row">' + lane_checks + '</div>\n'
        '<div class="row"><button id="map-btn">Map This</button><span id="map-error" style="color:#f43f5e"></span></div></div>\n'
        '<div id="map-results"></div></div>\n'
        "<script>\n" + core + "\n"
        "/* ---- Registry brain js:taxonomy (verbatim, 6 dims + 23 taxonomy entries) ---- */\n" + tax + "\n"
        "/* ---- Registry brain js:mapping (verbatim) ---- */\n" + mapping + "\n"
        "/* ---- Registry brain js:expansion (verbatim: expand + apply + callLaneStrict) ---- */\n" + expansion + "\n"
        "function $(id){ return document.getElementById(id); }\n"
        "function tickedLanes(){ return Array.prototype.slice.call(document.querySelectorAll('.lanebox')).filter(function(b){return b.checked;}).map(function(b){ var p=b.dataset.lane.split('::'); return {key:b.dataset.lane,pid:p[0],m:p.slice(1).join('::'),label:b.dataset.lane}; }); }\n"
        "function strengthRank(s){ return s==='high'?0:(s==='medium'?1:2); }\n"
        "function parseMatches(raw){ var t=String(raw).replace(/```json|```/g,''); var o=JSON.parse(t.slice(t.indexOf('{'),t.lastIndexOf('}')+1)); return (o.matches||[]).filter(function(m){ return m&&taxonomy[m.index]; }).sort(function(a,b){ return strengthRank(a.strength)-strengthRank(b.strength); }); }\n"
        "async function runMapping(){ var frag=$('map-input').value.trim(); if(!frag) return;\n"
        "  var lanes=tickedLanes(); if(!lanes.length){ $('map-error').textContent='Tick at least one model lane.'; return; } $('map-error').textContent='';\n"
        "  var built=buildMappingPrompt(frag); var host=$('map-results'); host.innerHTML='';\n"
        "  var btn=$('map-btn'); btn.disabled=true; btn.textContent='Mapping…';\n"
        "  await Promise.all(lanes.map(function(l,i){ return new Promise(function(r){setTimeout(r,i*220);}).then(function(){ return runLaneMapping(l,frag,built.system,built.user,host); }); }));\n"
        "  btn.disabled=false; btn.textContent='Map This'; }\n"
        "async function runLaneMapping(l,frag,system,user,host){ var card=document.createElement('div'); card.className='card'; card.innerHTML='<b>'+l.label+'</b><div class=\"lane-status\">Mapping…</div><div class=\"matches\"></div>'; host.appendChild(card);\n"
        "  var st=card.querySelector('.lane-status'), box=card.querySelector('.matches');\n"
        "  try{ var r=await callLaneStrict(l,system,user);\n"
        "    st.textContent='Complete'+((r.served&&r.served!==l.m)?' → served: '+r.served:'');\n"
        "    var matches=parseMatches(r.text);\n"
        "    box.innerHTML=matches.map(function(m){ var t=taxonomy[m.index]; var dim=dimensions.find(function(d){return d.id===t.dim;});\n"
        "      return '<div class=\"match\"><b>'+t.name+'</b> <span class=\"str str-'+m.strength+'\">'+m.strength+'</span> <span style=\"color:var(--dim)\">'+(dim?dim.name:'Dim '+t.dim)+'</span><p>'+m.reason+'</p><button class=\"plain\" data-lane=\"'+l.key+'\" data-mi=\"'+m.index+'\" data-kind=\"expand\">Expand</button> <button class=\"plain\" data-lane=\"'+l.key+'\" data-mi=\"'+m.index+'\" data-kind=\"apply\">Apply</button><div class=\"xout\"></div></div>'; }).join('');\n"
        "    box.querySelectorAll('button').forEach(function(b){ b.addEventListener('click',function(){ expandApply(b,frag); }); }); }\n"
        "  catch(e){ card.classList.add('error'); st.textContent='Error'; box.textContent=String(e.message||e); } }\n"
        "async function expandApply(btn,frag){ var wrap=btn.parentElement; var out=wrap.querySelector('.xout'); out.textContent='…';\n"
        "  var t=taxonomy[+btn.dataset.mi]; var lp=btn.dataset.lane.split('::'); var lane={key:btn.dataset.lane,pid:lp[0],m:lp.slice(1).join('::')};\n"
        "  try{ var reason=wrap.querySelector('p').textContent;\n"
        "    var p=(btn.dataset.kind==='expand'?buildExpansionPrompt(frag,t,reason):buildApplicationPrompt(frag,t,reason));\n"
        "    var r=await callLaneStrict(lane,p.system,p.user); out.textContent=r.text; }\n"
        "  catch(e){ out.textContent='Error: '+e.message; } }\n"
        "$('map-btn').addEventListener('click',runMapping);\n"
        "fetchModelConfig();\n</script>\n</body></html>\n")


def chassis_vectorforge(engine, T, params, runner):
    stages = js_raw_guard(T["stages"][1])
    builders = js_raw_guard(T["builders"][1])
    fallback = runner.get("model_core", {}).get("fallback", {})
    core = core_block("Vector Forge", fallback)
    ocfg = params.get("optimizer_config", {})
    maxiter = ocfg.get("maxiter", {})
    thresh = ocfg.get("threshold", {})
    defs = ("[{slug:'diverge',name:'Diverge'},{slug:'crystallize',name:'Crystallize'},"
            "{slug:'architect',name:'Architect'},{slug:'fidelity',name:'Path-Fidelity'},"
            "{slug:'revise',name:'Revise'},{slug:'confirm',name:'Confirm Probe'}]")
    return ("<!DOCTYPE html>\n<!-- COMPILED by tools/compile_engine.py from claude_brain/engines/" + engine
        + "/ (system.md + params.json + runner.json). Source: " + html_escape(params.get("source_file", ""))
        + ". DO NOT hand-edit; edit the registry and recompile. -->\n"
        '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
        "<title>" + html_escape(engine) + " (registry build)</title>\n<style>\n"
        ":root{--bg:#0a0a0f;--panel:#12121a;--line:#26263a;--txt:#e8e8f0;--dim:#8a8aa3;--acc:#a855f7}\n"
        "body{background:var(--bg);color:var(--txt);font-family:system-ui,sans-serif;margin:0}\n"
        ".header{display:flex;justify-content:space-between;align-items:center;padding:.8rem 1.2rem;border-bottom:1px solid var(--line)}\n"
        ".badge{font-size:.65rem;border:1px solid var(--line);border-radius:99px;padding:.15rem .6rem;color:var(--dim)}\n"
        ".canvas{max-width:960px;margin:0 auto;padding:1.2rem}\n.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1rem;margin-bottom:1rem}\n"
        "textarea{width:100%;min-height:70px;background:#0d0d14;color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:.6rem}\n"
        "input[type=text],input[type=number]{background:#0d0d14;color:var(--txt);border:1px solid var(--line);border-radius:6px;padding:.4rem .6rem}\n"
        "select{background:#0d0d14;color:var(--txt);border:1px solid var(--line);border-radius:6px;padding:.35rem}\n"
        ".row{display:flex;gap:.8rem;align-items:center;margin-top:.7rem;flex-wrap:wrap;font-size:.8rem;color:var(--dim)}\n"
        "button{background:var(--acc);color:#fff;border:0;border-radius:8px;padding:.55rem 1.1rem;font-weight:700;cursor:pointer}\n"
        "button.plain{background:#1a1a26;color:var(--txt);border:1px solid var(--line);font-weight:400;padding:.3rem .7rem;margin:.15rem}\n"
        ".card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1rem;margin-top:.8rem}\n"
        ".vec{border-top:1px solid var(--line);padding:.6rem 0}.prose{white-space:pre-wrap;font-size:.88rem}\n"
        "details{margin-top:.6rem}summary{cursor:pointer;color:var(--acc);font-size:.8rem}details textarea{width:100%;min-height:120px;margin-top:.4rem}\n"
        "</style></head>\n<body>\n"
        '<div class="header"><div><b>VECTOR FORGE</b> <span class="badge">registry build · fan + optimizer</span> <span class="badge" id="cfgBadge">Config: …</span></div>\n'
        '<div><select id="providerSelect"><option value="groq">Groq</option><option value="or-auto">OR · Free Router</option><option value="claude">Claude · Native</option></select></div></div>\n'
        '<div class="canvas"><div class="panel"><textarea id="seed-input" placeholder="The thing you are reaching for but cannot quite say yet…"></textarea>\n'
        '<div class="row"><input type="text" id="hint-input" placeholder="Optional success hint…" style="flex:1">\n'
        '<label><input type="checkbox" id="mode-switch" checked> Explorer</label>\n'
        '<span>maxIter</span><input type="number" id="cfg-maxiter" min="' + str(maxiter.get("min", 1)) + '" max="' + str(maxiter.get("max", 8)) + '" value="' + str(maxiter.get("default", 4)) + '">\n'
        '<span>threshold</span><input type="number" id="cfg-threshold" min="' + str(thresh.get("min", 1)) + '" max="' + str(thresh.get("max", 10)) + '" value="' + str(thresh.get("default", 8)) + '"></div>\n'
        '<div class="row"><button id="forgeBtn">Throw the fan</button><span id="pathLine"></span></div>\n'
        '<div id="fanGrid"></div><div id="loopLog"></div><div id="forged"></div></div>\n'
        '<div class="panel"><b>Prompt library</b> <span style="font-size:.72rem;color:var(--dim)">stage overrides persist to localStorage</span><div id="libEditors"></div></div>\n'
        '<div class="panel"><b>Responses</b><div id="respList"></div></div></div>\n'
        "<script>\n" + core + "\n"
        "/* ---- Registry brain js:stages (verbatim, 6 stage prompts + registry) ---- */\n" + stages + "\n"
        "/* ---- Registry brain js:builders (verbatim; uses SEED/HINT/activeVectors below) ---- */\n" + builders + "\n"
        "var SEED='', HINT=''; var VF_PATH=[], VF_FAN=null, VF_CRYST=null;\n"
        "function activeVectors(){ return VF_PATH; }\n"
        "function $(id){ return document.getElementById(id); }\n"
        "function selProv(){ return $('providerSelect').value; }\n"
        "function vfCall(slug,user,onChunk){ return callModel({provider:selProv(),system:activeStagePrompt(slug),user:user,onText:onChunk}).then(function(r){return r.text;}); }\n"
        "function stripF(t){ return String(t).replace(/```json|```/g,''); }\n"
        "function parseJ(t){ var s=stripF(t); return JSON.parse(s.slice(s.indexOf('{'),s.lastIndexOf('}')+1)); }\n"
        "function esc(t){ return String(t==null?'':t).replace(/&/g,'&amp;').replace(/</g,'&lt;'); }\n"
        "function log(m){ var d=document.createElement('div'); d.className='card'; d.textContent=m; $('loopLog').appendChild(d); }\n"
        "function renderPath(){ $('pathLine').textContent=VF_PATH.length?('Path: '+VF_PATH.map(function(v){return v.label;}).join(' → ')):'No recognitions yet.'; }\n"
        "async function startForge(){ SEED=$('seed-input').value.trim(); if(!SEED) return; HINT=$('hint-input').value.trim(); VF_PATH=[]; VF_CRYST=null; renderPath(); $('fanGrid').innerHTML=''; $('loopLog').innerHTML=''; $('forged').innerHTML='';\n"
        "  var btn=$('forgeBtn'); btn.disabled=true; await fan(null); btn.disabled=false; }\n"
        "async function fan(scope){ var host=$('fanGrid'); host.innerHTML='<div class=\"card\">Throwing vectors…</div>';\n"
        "  try{ var f=parseJ(await vfCall('diverge',divergeContent(scope))); VF_FAN=f; renderFan(f); }\n"
        "  catch(e){ host.innerHTML='<div class=\"card\">Error: '+esc(e.message||e)+'</div>'; } }\n"
        "function renderFan(f){ var host=$('fanGrid'); if(f.floor_reached||!(f.vectors||[]).length){ host.innerHTML='<div class=\"card\">Floor reached — no further forks. Forge from the current path.</div>'; return; }\n"
        "  host.innerHTML='<div class=\"card\"><b>'+esc(f.anchored_position||'')+'</b></div>'+(f.vectors||[]).map(function(v,i){ return '<div class=\"card vec\"><b>'+esc(v.label)+'</b> <span style=\"color:var(--dim)\">depth '+v.resonance_depth+(v.can_subdivide?'':' · atomic')+'</span><p>'+esc(v.direction)+'</p><p style=\"font-size:.75rem;color:var(--dim)\">'+esc(v.traces_via||'')+'</p><button class=\"plain\" data-i=\"'+i+'\" data-k=\"descend\">Descend</button> <button class=\"plain\" data-i=\"'+i+'\" data-k=\"forge\">Forge from here</button></div>'; }).join('');\n"
        "  host.querySelectorAll('button').forEach(function(b){ b.addEventListener('click',function(){ var v=(VF_FAN.vectors||[])[+b.dataset.i]; if(!v) return; VF_PATH.push({label:v.label,direction:v.direction}); renderPath(); if(b.dataset.k==='descend'){ fan(v); } else { runOptimizer(); } }); }); }\n"
        "async function runOptimizer(){ var maxIter=+$('cfg-maxiter').value||4, threshold=+$('cfg-threshold').value||8;\n"
        "  log('Crystallizing path…');\n"
        "  try{ VF_CRYST=parseJ(await vfCall('crystallize',pathText()+'\\n\\nCrystallize what this path actually changed — the operative stance, the specific reorientations, what must change in the cognition, and what must be refused.')); }\n"
        "  catch(e){ log('Crystallize failed: '+e.message); return; }\n"
        "  log('Operative stance: '+(VF_CRYST.operative_stance||'(none)'));\n"
        "  var best='', bestScore=-1, lastEval=null;\n"
        "  for(var it=1; it<=maxIter; it++){\n"
        "    log('Architect iteration '+it+'…');\n"
        "    var stream=document.createElement('div'); stream.className='card prose'; stream.textContent='Forging…'; $('loopLog').appendChild(stream);\n"
        "    var user=(it===1)?(pathText()+'\\n\\n'+crystalText(VF_CRYST)+'\\n\\nForge the dense system prompt that inhabits this crystallized dimension.')\n"
        "      :(pathText()+'\\n\\n'+crystalText(VF_CRYST)+'\\n\\nPrevious prompt:\\n---\\n'+best+'\\n---\\n\\nEvaluator axis scores: '+JSON.stringify(lastEval.axis_scores)+'\\nWeaknesses: '+(lastEval.weaknesses||[]).join('; ')+'\\nRevision guidance: '+(lastEval.revision_guidance||'')+'\\n\\nRewrite to fix every weakness while inhabiting the crystallized operative stance.');\n"
        "    var prompt=await vfCall(it===1?'architect':'revise',user,function(a){stream.textContent=a;});\n"
        "    stream.textContent=prompt;\n"
        "    var ev=parseJ(await vfCall('fidelity',pathText()+'\\n\\n'+crystalText(VF_CRYST)+'\\n\\nForged prompt to judge:\\n---\\n'+prompt+'\\n---\\nThreshold for pass: '+threshold+'/10.'));\n"
        "    log('Fidelity: '+ev.score+'/10 — '+ev.verdict);\n"
        "    if(ev.score>bestScore){ bestScore=ev.score; best=prompt; }\n"
        "    lastEval=ev; if(ev.score>=threshold&&ev.verdict!=='fail'){ log('Converged at iteration '+it+'.'); break; }\n"
        "  }\n"
        "  var term=VF_PATH.length?VF_PATH[VF_PATH.length-1]:{label:'seed',direction:SEED};\n"
        "  log('Confirmation probe (off-loop)…');\n"
        "  var probe=parseJ(await vfCall('confirm','Forged prompt:\\n---\\n'+best+'\\n---\\n\\nTerminal vector: \"'+term.label+': '+term.direction+'\"\\n\\nCrystallized operative stance: \"'+((VF_CRYST&&VF_CRYST.operative_stance)||'')+'\"\\n\\nExecute briefly, then judge both terminal vector continuity and operative stance continuity.'));\n"
        "  renderForged(best,bestScore,probe); saveResponse(best,bestScore,probe); }\n"
        "function renderForged(prompt,score,probe){ $('forged').innerHTML='<div class=\"card\"><b>The dense prompt · '+score+'/10</b><div class=\"prose\">'+esc(prompt)+'</div><p style=\"font-size:.8rem\">Probe: '+esc(probe.sample||'')+' — '+(probe.continuous?'continuous':'drift')+' / '+(probe.stance_continuous?'stance holds':'stance drifts')+'. '+esc(probe.note||'')+'</p><button class=\"plain\" id=\"copyForged\">Copy prompt</button></div>';\n"
        "  document.getElementById('copyForged').addEventListener('click',function(){ try{ navigator.clipboard.writeText(prompt); }catch(e){} }); }\n"
        "function saveResponse(prompt,score,probe){ var entry={id:'r_'+Date.now(),seed:SEED,hint:HINT,score:score,output:prompt,crystallization:VF_CRYST,confirm:probe,trace:VF_PATH.slice(),timestamp:new Date().toISOString()};\n"
        "  var lib=[]; try{ lib=JSON.parse(localStorage.getItem('responses:vector-forge')||'[]'); }catch(e){ lib=[]; }\n"
        "  lib.unshift(entry); try{ localStorage.setItem('responses:vector-forge',JSON.stringify(lib)); }catch(e){}\n"
        "  renderResponses(); }\n"
        "function renderResponses(){ var lib=[]; try{ lib=JSON.parse(localStorage.getItem('responses:vector-forge')||'[]'); }catch(e){ lib=[]; }\n"
        "  $('respList').innerHTML=lib.length?lib.slice(0,12).map(function(e){ return '<div class=\"card\"><b>'+esc(e.seed||'').slice(0,80)+'</b> <span style=\"color:var(--dim)\">'+e.score+'/10 · '+esc(e.timestamp||'')+'</span></div>'; }).join(''):'<div style=\"color:var(--dim);font-size:.8rem\">No saved forges yet.</div>'; }\n"
        "function renderLib(){ var defs="+defs+";\n"
        "  $('libEditors').innerHTML=defs.map(function(d){ return '<details><summary>'+d.name+'</summary><textarea id=\"lib-'+d.slug+'\">'+esc(activeStagePrompt(d.slug))+'</textarea><br><button class=\"plain\" data-s=\"'+d.slug+'\" data-k=\"save\">Save override</button> <button class=\"plain\" data-s=\"'+d.slug+'\" data-k=\"reset\">Reset</button></details>'; }).join('');\n"
        "  document.querySelectorAll('#libEditors button').forEach(function(b){ b.addEventListener('click',function(){\n"
        "    if(b.dataset.k==='save'){ PROMPT_OVERRIDES[b.dataset.s]=document.getElementById('lib-'+b.dataset.s).value; }\n"
        "    else { delete PROMPT_OVERRIDES[b.dataset.s]; document.getElementById('lib-'+b.dataset.s).value=activeStagePrompt(b.dataset.s); }\n"
        "    try{ localStorage.setItem('prompts:vector-forge',JSON.stringify(PROMPT_OVERRIDES)); }catch(e){} }); }); }\n"
        "document.getElementById('forgeBtn').addEventListener('click',startForge);\n"
        "try{ Object.assign(PROMPT_OVERRIDES,JSON.parse(localStorage.getItem('prompts:vector-forge')||'{}')); }catch(e){}\n"
        "renderLib(); renderResponses(); renderPath(); fetchModelConfig();\n</script>\n</body></html>\n")


def chassis_generic(engine, T, params, runner):
    """Fallback projection for auto-onboarded engines: params-driven form + single callModel run.

    Used by the incoming-batch pipeline for engines with no bespoke chassis yet.
    Requires one prompt:* block in system.md (auto-triage always emits prompt:default).
    """
    pick = T.get("default")
    if pick is None:
        for k in sorted(T):
            if T[k][0] == "prompt":
                pick = T[k]
                break
    if pick is None or pick[0] != "prompt":
        sys.exit(engine + ": generic chassis needs a prompt:* block in system.md")
    sys_text = js_escape_template(pick[1])
    label = params.get("provider_config", {}).get("engine_name", engine)
    fallback = runner.get("model_core", {}).get("fallback", {})
    core = core_block(label, fallback)
    draft = params.get("review_required", False)
    fields = []
    for inp in params.get("inputs", []):
        iid, kind = inp.get("id", "input1"), inp.get("kind", "text")
        lab, ph = html_escape(inp.get("label", iid)), html_escape(inp.get("placeholder", ""))
        dflt = html_escape(str(inp.get("default", "")))
        if kind == "textarea":
            fields.append('<div><div class="flabel">' + lab + '</div><textarea id="' + html_escape(iid)
                          + '" placeholder="' + ph + '">' + dflt + "</textarea></div>")
        elif kind in ("number", "range"):
            extra = ""
            if inp.get("min") is not None:
                extra += ' min="' + html_escape(str(inp.get("min"))) + '"'
            if inp.get("max") is not None:
                extra += ' max="' + html_escape(str(inp.get("max"))) + '"'
            fields.append('<div><div class="flabel">' + lab + '</div><input type="number" id="'
                          + html_escape(iid) + '" value="' + dflt + '" placeholder="' + ph + '"' + extra + "></div>")
        else:
            fields.append('<div><div class="flabel">' + lab + '</div><input type="text" id="'
                          + html_escape(iid) + '" value="' + dflt + '" placeholder="' + ph + '"></div>')
    for sel in params.get("selects", []):
        sid = sel.get("id", "select1")
        opts = "".join('<option value="' + html_escape(o) + '"'
                       + (" selected" if o == sel.get("default") else "") + ">" + html_escape(o) + "</option>"
                       for o in sel.get("options", []))
        fields.append('<div><div class="flabel">' + html_escape(sel.get("label", sid)) + '</div><select id="'
                      + html_escape(sid) + '">' + opts + "</select></div>")
    run_label = (params.get("actions") or [{}])[0].get("label", "Run")
    ids = [i.get("id", "input1") for i in params.get("inputs", [])]
    return ("<!DOCTYPE html>\n<!-- COMPILED by tools/compile_engine.py (generic chassis) from claude_brain/engines/"
        + engine + "/. Source: " + html_escape(params.get("source_file", ""))
        + ". DO NOT hand-edit; edit the registry and recompile. -->\n"
        '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
        "<title>" + html_escape(label) + " (registry build)</title>\n<style>\n"
        ":root{--bg:#0a0a0f;--panel:#12121a;--line:#26263a;--txt:#e8e8f0;--dim:#8a8aa3;--acc:#a855f7}\n"
        "body{background:var(--bg);color:var(--txt);font-family:system-ui,sans-serif;margin:0}\n"
        ".header{display:flex;justify-content:space-between;align-items:center;padding:.8rem 1.2rem;border-bottom:1px solid var(--line)}\n"
        ".badge{font-size:.65rem;border:1px solid var(--line);border-radius:99px;padding:.15rem .6rem;color:var(--dim)}\n"
        ".canvas{max-width:760px;margin:0 auto;padding:1.2rem}\n.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1rem;margin-bottom:1rem}\n"
        ".flabel{font-size:.72rem;color:var(--dim);margin:.6rem 0 .25rem}\n"
        "textarea{width:100%;min-height:80px;background:#0d0d14;color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:.6rem}\n"
        "input[type=text],input[type=number]{width:100%;background:#0d0d14;color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:.6rem}\n"
        "select{background:#0d0d14;color:var(--txt);border:1px solid var(--line);border-radius:6px;padding:.4rem}\n"
        "button{background:var(--acc);color:#fff;border:0;border-radius:8px;padding:.6rem 1.2rem;font-weight:700;cursor:pointer;margin-top:.8rem}\n"
        ".card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1rem;margin-top:.8rem;white-space:pre-wrap}\n"
        "</style></head>\n<body>\n"
        '<div class="header"><div><b>' + html_escape(label.upper()) + '</b> '
        + ('<span class="badge">draft build · review required</span> ' if draft else '<span class="badge">registry build</span> ')
        + '<span class="badge" id="cfgBadge">Config: …</span></div>\n'
        '<div><select id="providerSelect"><option value="groq">Groq</option><option value="or-auto">OR · Free Router</option></select></div></div>\n'
        '<div class="canvas"><div class="panel">' + "".join(fields) + '\n'
        '<button id="runBtn">' + html_escape(run_label) + '</button></div>\n'
        '<div id="out"><div class="card">Output appears here.</div></div></div>\n'
        "<script>\n" + core + "\n"
        "/* ---- Registry brain (auto-triaged prompt block) ---- */\n"
        "function getSystemText(){ return `" + sys_text + "`; }\n"
        "var INPUT_IDS=" + json.dumps(ids) + ";\n"
        "function getUser(){ return INPUT_IDS.map(function(id){ var el=document.getElementById(id); return el?el.value:''; }).filter(function(v){return v;}).join('\\n\\n'); }\n"
        "async function runGeneric(){ var u=getUser(); if(!u) return; var out=document.getElementById('out'); out.textContent='Running…';\n"
        "  try{ var r=await callModel({provider:document.getElementById('providerSelect').value,system:getSystemText(),user:u,onText:function(a){out.textContent=a;}}); out.textContent=r.text; }\n"
        "  catch(e){ out.textContent='Error: '+e.message; } }\n"
        "document.getElementById('runBtn').addEventListener('click',runGeneric);\n"
        "fetchModelConfig();\n</script>\n</body></html>\n")


def batch_compile_all():
    """Compile every registry engine with a complete triad. Returns (ok, fail) name lists."""
    ok, fail = [], []
    for name in list_engines():
        d = ENGINES / name
        if not (d / "system.md").is_file() or not (d / "params.json").is_file():
            print(f"skip {name} (incomplete triad)")
            continue
        try:
            compile_engine(name, d / "dist" / (name + "-compiled.html"))
            ok.append(name)
        except SystemExit as e:
            print(f"FAIL {name}: {e}")
            fail.append(name)
        except Exception as e:  # noqa: BLE001 - batch must report, not crash
            print(f"FAIL {name}: {e}")
            fail.append(name)
    print(f"batch: {len(ok)} ok, {len(fail)} fail")
    return ok, fail


WAVE2 = {
    "aperture-carousel": (chassis_aperture, ("shared", "paramblock", "architect", "writer", "editor")),
    "cognitive-shift-v7": (chassis_cognitive, ("lenses",)),
    "fan_ramify_flywheel": (chassis_flywheel, ("spine", "fan", "ramify", "flywheel")),
    "scenario-forge": (chassis_scenario, ("decomposition", "lane-system-decomposition", "intensity",
                                          "contract", "suggest", "lane-system-branching")),
    "dimensions": (chassis_dimensions, ("taxonomy", "mapping", "expansion")),
    "vectorforge-v3": (chassis_vectorforge, ("stages", "builders")),
}


def compile_engine(engine: str, out: pathlib.Path):
    system_md, params, runner = read_registry(engine)
    if engine in WAVE2:
        fn, required = WAVE2[engine]
        templates = extract_templates(system_md)
        missing = [k for k in required if k not in templates]
        if missing:
            sys.exit(f"{engine}: system.md missing blocks: {missing}")
        html = fn(engine, templates, params, runner)
    elif engine == "prompt-generator":
        html = chassis_prompt_generator(engine, extract_template(system_md), params, runner)
    elif engine == "easy-english":
        html = chassis_easy_english(engine, extract_template(system_md), params, runner)
    else:
        # Batch-pipeline fallback: any complete triad builds via the generic chassis.
        templates = extract_templates(system_md)
        html = chassis_generic(engine, templates, params, runner)
    html = inject_skill_track(html)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    sha = hashlib.sha256(html.encode("utf-8")).hexdigest()[:12]
    print(f"compiled {engine} -> {out} ({len(html)} bytes, sha {sha})")
    return out


def main():
    ap = argparse.ArgumentParser(description="Compile registry engine -> standalone HTML")
    ap.add_argument("--engine", help="engine folder under claude_brain/engines/")
    ap.add_argument("--out", help="output HTML path (default: <engine>/dist/<engine>-compiled.html)")
    ap.add_argument("--list", action="store_true", help="list available engines")
    ap.add_argument("--all", action="store_true", help="batch-compile every registry engine")
    args = ap.parse_args()
    if args.all:
        _, fail = batch_compile_all()
        sys.exit(1 if fail else 0)
    if args.list or not args.engine:
        print("engines: " + ", ".join(list_engines()))
        if not args.engine:
            return
    out = pathlib.Path(args.out) if args.out else ENGINES / args.engine / "dist" / f"{args.engine}-compiled.html"
    compile_engine(args.engine, out)


if __name__ == "__main__":
    main()
