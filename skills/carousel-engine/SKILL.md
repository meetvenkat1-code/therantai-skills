---
name: carousel-engine
description: Build an Instagram carousel engine as a single HTML file with full slide generation, preview/storyboard views, copy controls, and ZIP export of individual PNG slides + storyboard overview + carousel-copy.txt. Use this skill whenever the user wants to build, modify, or extend a carousel engine — including new themes, new hook styles, image support, or brand variants. Trigger on any mention of "carousel", "Instagram slides", "slide deck generator", "content carousel", or requests to generate multi-slide social content. The structural contract (views, export, copy, API routing) must remain identical across all builds; only content, colour palette, and AI prompt vary.
---

# Carousel Engine — Structural Skill

A single `.html` file that:
- Takes a topic or existing content as input
- Calls an AI API to generate structured slide JSON
- Renders slides in two views: **Preview** (one slide at a time) and **Storyboard** (all slides as a grid)
- Exports everything as a ZIP containing individual PNGs + storyboard overview + plain-text copy file
- Works inside claude.ai natively (no API key needed) and in any browser with an external provider key

---

## Fixed Structural Contract

These elements are **non-negotiable** across every carousel engine build. Do not remove, reorder, or redesign them.

### 1. Header — Three Zones

```
┌─────────────────────────────────────────────────────────┐
│  [Zone A]              [Zone B]              [Zone C]    │
│  ● Engine Name         Provider + ⚙          attribution│
└─────────────────────────────────────────────────────────┘
```

- Zone A: pip dot (7px, accent-main glow) + engine name (EB Garamond italic)
- Zone B: provider `<select>` defaulting to `claude` + gear button (⚙)
- Zone C: attribution email `meet.venkat1@gmail.com` as clickable mailto, right-aligned, muted

### 2. Input Panel (below header, fixed height)

- Mode tabs: **✦ Generate from topic** | **⇄ Transform content**
- Textarea (mainInput) + Generate button
- Controls row: Auto toggle (on by default) + manual controls (hidden when Auto on)
  - Manual controls: Slides (range 3–10), Tone (select), Audience (select)
  - Each manual control has an "Auto" badge that re-enables auto for that field

### 3. Output Section (scrollable, flex:1, min-height:0)

Three sub-components always present once slides are generated:

**A. View Toggle Bar**
```
[▶ Preview]  [⊞ Storyboard]          [Copy All]  [⬇ Download ZIP]
```
- Left: view tabs
- Right: Copy All (accent border) + Download ZIP (green border) — always visible together

**B. Preview View**
- Single slide card (max-width 420px, centred, aspect-ratio 4/5)
- Gradient background per slide index
- Coloured accent bar at top of card
- Slide content: label (Inter, uppercase, muted) → headline (EB Garamond bold) → body (EB Garamond) → CTA
- Navigation: ← dot indicators → below card
- Slide counter below nav (e.g. "3 / 6")
- **No per-slide copy button** on the card itself

**C. Storyboard View**
- CSS grid: `repeat(auto-fill, minmax(220px, 1fr))`, gap 1rem
- Each card: same gradient + accent styling as preview, scaled down
- Cards animate in (opacity 0→1, translateY 8px→0)
- Click any card → switches to Preview view at that index
- **No per-card copy button**

### 4. Copy Controls

| Control | Location | Behaviour |
|---|---|---|
| Copy All | Toolbar, right side | Copies all slides as formatted text |
| Per-slide copy | **REMOVED** | Not present anywhere |

Copy All format:
```
[Slide Label]\n\nHeadline\n\nBody\n\nCTA\n\n---\n\n
```

### 5. ZIP Export

**One button. One download. Everything inside.**

Contents of every ZIP:
```
carousel-{topic-slug}.zip
  ├── slide-01-{headline-slug}.png     1080×1350px  Instagram 4:5
  ├── slide-02-{headline-slug}.png     1080×1350px
  ├── ...
  ├── storyboard-overview.png          Full grid capture
  └── carousel-copy.txt                All slide text, sequential
```

**carousel-copy.txt format:**
```
CAROUSEL: {topic}
Generated: {date}
Slides: {n}
────────────────────────────────────────────────

SLIDE 1 — HOOK
{label}

{headline}

{body}

↳ {cta}

────────────────────────────────────────────────
```

**ZIP progress overlay** (full-screen, backdrop blur):
- Title: "Building your ZIP…"
- Progress bar (green → teal gradient)
- Step label: "Rendering slide 2 of 6… / Capturing storyboard… / Writing carousel-copy.txt… / Packing ZIP…"
- Closes automatically, shows "✓ N slides + storyboard + copy.txt" on completion

---

## Slide Data Structure (AI output)

The AI returns a JSON array. Each object:

```json
{
  "slide": 1,
  "type": "hook" | "expansion" | "landing",
  "label": "Slide 1 of 6",
  "headline": "Max 12 words — punchy and direct",
  "body": "2–4 sentences of prose. No bullets.",
  "cta": "Only on landing slide — empty string otherwise"
}
```

### Slide Progression Rules

| Position | Type | Purpose |
|---|---|---|
| Slide 1 | hook | One arresting line that stops the scroll |
| Slides 2…N-1 | expansion | Each deepens ONE distinct dimension — not a list |
| Slide N | landing | CTA, reframe, or resonant echo of the hook |

---

## Visual Identity — Fixed Palette

```css
:root {
  --bg-void:        #0a0a0f;
  --bg-surface:     #12121a;
  --bg-elevated:    #1a1a28;
  --bg-border:      #2a2a3d;
  --text-primary:   #e8e8f0;
  --text-secondary: #9090a8;
  --text-muted:     #505068;
  --accent-main:    #7c6ef5;
  --accent-glow:    rgba(124,110,245,0.15);
  --amber:          #f5a623;
  --green:          #4caf82;
  --coral:          #f56565;
  --teal:           #38bdf8;
  --orange-warn:    #f97316;
}
```

### Slide Colour Sequence (10 colours, cycles)

```javascript
const SLIDE_COLORS = [
  '#7c6ef5','#38bdf8','#f5a623','#4caf82',
  '#f56565','#e879f9','#fb923c','#a3e635',
  '#f472b6','#34d399'
];
```

### Slide Gradient Backgrounds (10 themes, cycles)

```css
.grad-0 { background: linear-gradient(145deg, #1a1028 0%, #0d0820 100%); }
.grad-1 { background: linear-gradient(145deg, #0a1628 0%, #071020 100%); }
.grad-2 { background: linear-gradient(145deg, #1a1200 0%, #120d00 100%); }
.grad-3 { background: linear-gradient(145deg, #001a12 0%, #00100a 100%); }
.grad-4 { background: linear-gradient(145deg, #1a0808 0%, #120505 100%); }
.grad-5 { background: linear-gradient(145deg, #1a0a1a 0%, #120812 100%); }
.grad-6 { background: linear-gradient(145deg, #1a0e00 0%, #120900 100%); }
.grad-7 { background: linear-gradient(145deg, #101a00 0%, #0a1200 100%); }
.grad-8 { background: linear-gradient(145deg, #1a0010 0%, #12000a 100%); }
.grad-9 { background: linear-gradient(145deg, #001a1a 0%, #001212 100%); }
```

### Slide Gradient Pairs (for offscreen PNG render)

```javascript
const GRAD_PAIRS = [
  ['#1a1028','#0d0820'],['#0a1628','#071020'],['#1a1200','#120d00'],
  ['#001a12','#00100a'],['#1a0808','#120505'],['#1a0a1a','#120812'],
  ['#1a0e00','#120900'],['#101a00','#0a1200'],['#1a0010','#12000a'],
  ['#001a1a','#001212']
];
```

---

## Typography Pairing

| Element | Font | Size | Weight | Style |
|---|---|---|---|---|
| Engine name (header) | EB Garamond | 1.05rem | 400 | italic |
| Slide headline (preview) | EB Garamond | 1.65rem | 600 | normal |
| Slide body (preview) | EB Garamond | 1rem | 400 | normal |
| Slide label | Inter | 0.6rem | 400 | uppercase |
| Slide CTA | Inter | 0.72rem | 400 | uppercase |
| Storyboard headline | EB Garamond | 1.05rem | 600 | normal |
| Storyboard body | EB Garamond | 0.82rem | 400 | normal |
| Controls, tabs, buttons | Inter | 0.68–0.78rem | 400–500 | normal |

---

## API Routing (5-provider hybrid)

```javascript
async function callAI(systemPrompt, userMessage, onChunk) {
  const provider = getSelectedProvider();

  if (provider === 'claude') {
    // NO Authorization header — platform proxies automatically
    const res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01',
        'anthropic-dangerous-direct-browser-access': 'true'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-6',
        max_tokens: 4000,
        stream: true,
        system: systemPrompt,
        messages: [{ role: 'user', content: userMessage }]
      })
    });
    await readStream(res, 'anthropic', onChunk);

  } else if (provider === 'groq') { /* Bearer hek_groq, llama-3.3-70b-versatile */ }
  else if (provider === 'openai') { /* Bearer hek_openai, gpt-4o */ }
  else if (provider === 'gemini') { /* key param hek_gemini, gemini-1.5-pro */ }
  else if (provider === 'lmstudio') { /* hek_lmstudio as base URL */ }
}
```

Storage prefix for all keys: `hek_{provider}`

---

## Offscreen PNG Render Architecture

Each slide is painted into a hidden `#renderStage` div at **1080×1350px** (Instagram 4:5 spec), captured via `html2canvas`, then added to the JSZip as a PNG blob.

```css
#renderStage {
  position: fixed;
  left: -9999px;
  width: 1080px;
  height: 1350px;
  overflow: hidden;
  pointer-events: none;
  z-index: -999;
}
```

Render card anatomy at 1080×1350:
- 7px accent colour bar across the top
- Soft colour glow circle (bottom-right, `filter: blur(80px)`, opacity 0.08)
- Slide counter (top-right, colour-tinted, opacity 0.32)
- Content zone (bottom-aligned, padding 92px 90px 88px):
  - Label: Inter 24px uppercase
  - Headline: Georgia 88px bold (system serif — Google Fonts unavailable in canvas)
  - Body: Georgia 44px
  - CTA: Inter 30px uppercase (landing slide only)

> **Note:** PNG renders use `Georgia` (system serif) not EB Garamond, because
> html2canvas cannot load cross-origin web fonts at capture time.

Required CDN libraries (include in `<head>`):
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
```

---

## Empty State

Shown before first generation:
- Large faded icon (opacity 0.1)
- EB Garamond italic heading — one evocative sentence about what the engine does
- Short sub-text (Inter, muted)
- 4–6 example pills (clickable, fill textarea on click)

---

## Scroll Architecture (critical — do not change)

```css
body {
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.shell {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.output-section {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;   /* NON-NEGOTIABLE — removes flex minimum sizing floor */
}
```

---

## Attribution Contract

Every build must carry `meet.venkat1@gmail.com` as a clickable `mailto:` link:
- Header Zone C: right-aligned, muted text
- Footer: centered or right-aligned

This is automatic — never skip it, never ask.

---

## Build Order

Always follow this sequence:

1. HTML skeleton + all section divs
2. Full `<style>` block — palette variables, all component CSS
3. `callAI()` + `readStream()` — 5-provider routing
4. `getKey()` / `storeKey()` / `saveKey()` — gear drawer wiring
5. Provider selector (default: claude) + warning banner logic
6. `buildSystemPrompt()` — slide generation prompt
7. `generate()` — input validation, API call, JSON parse, renderCarousel()
8. `renderCarousel()` → `buildStoryboard()` + `renderPreviewSlide()` + `buildDots()`
9. `attachCopy()` + Copy All wiring (no per-slide copy)
10. ZIP system: `buildRenderSlide()` + `captureStoryboard()` + `downloadZip()`
11. Navigation wiring (prev/next buttons, keyboard arrows, dot indicators)
12. Provider/gear/Auto toggle event wiring
13. Error handling on every API call

---

## What Can Vary Between Builds

| Element | Can change freely |
|---|---|
| Engine name in header | Yes |
| Colour palette | Yes — swap CSS variables |
| Slide colour sequence | Yes |
| Gradient themes | Yes |
| Empty state heading + pills | Yes |
| System prompt / hook strategy | Yes |
| Slide count range | Yes |
| Tone/audience options | Yes |
| Image support on slides | Yes |
| Attribution email (Zone C) | Yes |

| Element | Must NOT change |
|---|---|
| Two-view structure (Preview + Storyboard) | Fixed |
| View toggle bar position + button order | Fixed |
| Copy All in toolbar | Fixed |
| Download ZIP in toolbar | Fixed |
| ZIP contents (PNGs + storyboard + copy.txt) | Fixed |
| No per-slide copy buttons | Fixed |
| Offscreen render at 1080×1350 | Fixed |
| 5-provider routing | Fixed |
| hek_ storage prefix | Fixed |
| Auto toggle + manual controls pattern | Fixed |
| Scroll architecture (min-height: 0) | Fixed |

---

## How to Request a New Carousel Engine

Template:
```
Build a carousel engine with this theme: [THEME NAME]

Topic domain: [e.g. fitness / startup / philosophy / personal finance]
Hook style: [e.g. contrarian / question-led / statistic-led / story-led]
Tone range: [e.g. bold + reflective / educational + warm]
Palette variation: [e.g. keep default / warmer ambers / cooler blues]
Example pills: [list 4–6 topic examples for the empty state]
```

Or simply: **"Build a [THEME] carousel engine"** — the structural contract applies automatically.

---

## Known Constraints

- `html2canvas` cannot render cross-origin web fonts → PNG slides use Georgia (system serif)
- Sequential browser downloads blocked after first file → ZIP solves this entirely
- Storyboard capture requires the grid to be built even when not visible → `buildStoryboard()` always called on generation
- JSZip uses `STORE` compression for PNGs → ZIP file size ≈ sum of individual PNG sizes

---

*Skill version: 1.0 — Carousel Engine as built June 2026*
