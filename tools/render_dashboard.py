#!/usr/bin/env python3
"""render_dashboard.py: regenerate github-files/index.html from tools/dashboard_cards.json.

Usage (repo root):
  python tools/render_dashboard.py           rewrite index.html from cards json
  python tools/render_dashboard.py --check   fail if index.html is stale

Card schema in dashboard_cards.json:
  {"slug": ..., "title": ..., "kicker": ..., "blurb": ..., "path": ...}
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CARDS = ROOT / "tools" / "dashboard_cards.json"
OUT = ROOT / "index.html"


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def card_html(c) -> str:
    return ('<div class="card"><div class="kicker">' + esc(c["kicker"]) + "</div><h2>" + esc(c["title"])
            + "</h2><p>" + esc(c["blurb"]) + '</p><div class="path">' + esc(c["path"]) + '</div><a href="'
            + esc(c["path"]) + '" target="_blank" rel="noopener">Launch ' + esc(c["title"]) + "</a></div>")


def render(cards) -> str:
    return ("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Engines Platform Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
<style>
:root{--bg:#0a0a0f;--panel:#12121a;--line:#26263a;--txt:#e8e8f0;--dim:#8a8aa3;--acc:#38bdf8}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--txt);font-family:"Space Grotesk",system-ui,sans-serif;margin:0}
.wrap{max-width:1060px;margin:0 auto;padding:2.5rem 1.5rem 4rem}
header h1{font-size:1.9rem;margin:0;letter-spacing:-.01em}
header p{color:var(--dim);font-size:.9rem;margin:.4rem 0 0}
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
.card a{display:inline-block;margin-top:.4rem;background:var(--acc);color:#04121a;font-weight:700;font-size:.8rem;text-decoration:none;border-radius:8px;padding:.55rem 1rem;text-align:center}
footer{margin-top:2.5rem;color:var(--dim);font-size:.72rem}
footer code{font-size:.72rem}
</style>
</head>
<body>
<div class="wrap">
<header>
<h1>AI Engines Platform Dashboard</h1>
<p>Central launchpad for all compiled registry projections. Each card opens its standalone build.</p>
<div class="meta"><span class="badge ok">""" + str(len(cards)) + """ / """ + str(len(cards))
            + """ compiled</span><span class="badge">Model Core v2</span><span class="badge">deterministic builds</span></div>
</header>
<div class="grid">
""" + "\n".join(card_html(c) for c in cards) + """
</div>
<footer>Built from <code>claude_brain/engines/*/dist/</code> registry projections · Rebuild with <code>python tools/compile_engine.py --engine &lt;name&gt;</code></footer>
</div>
</body>
</html>
""")


def load_cards():
    return json.loads(CARDS.read_text(encoding="utf-8"))["cards"]


def main():
    cards = load_cards()
    html = render(cards)
    if "--check" in sys.argv:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != html:
            sys.exit("stale: index.html; run python tools/render_dashboard.py")
        print(f"dashboard current: {len(cards)} cards")
    else:
        OUT.write_text(html, encoding="utf-8")
        print(f"wrote index.html: {len(cards)} cards")


if __name__ == "__main__":
    main()
