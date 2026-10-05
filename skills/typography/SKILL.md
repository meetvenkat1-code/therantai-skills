---
name: typography
description: Font pairing rules, descender fixes, and adaptive theme bundles for HTML engine builds. Invoke with /typography or "invoke typography skill" when building engines with custom fonts, selecting a typographic register, or applying the Adaptive Vessel Skin. Covers: Syne descender clipping fix, five theme token bundles (RITUAL/ORACULAR/ANALYTICAL/RUPTURE/SOMATIC), font loading via Google Fonts CSS import, and theme persistence in localStorage.
---

# Typography Skill

A constraint map governing font behavior, typographic register selection, and theme token bundles for HTML engine builds. Invoke before any build involving custom typography or theme selection.

**Invocation:** `/typography` or "invoke typography skill"

When invoked before a build — read this file in full and apply all relevant constraints before writing any CSS.

---

## Syne Font: Descender Clipping Fix

Syne's internal metric tables (`hhea` / `OS/2`) ship with a descent value shallower than its actual glyph depth. The `g`, `y`, `p`, `q`, `j` descenders visibly clip against container edges. This is a documented Syne characteristic — not a CSS error introduced by the build.

**Working fix — apply globally to all Syne-bearing elements:**
```css
[class*="syne"], .engine-name, .tab-label, .badge, h1, h2 {
  line-height: 1.5;
  padding-bottom: 0.18em;
}
```

**Permanent fix — if self-hosting Syne via `@font-face`:**
```css
@font-face {
  font-family: 'Syne';
  src: url('syne.woff2') format('woff2');
  descent-override: 25%;
}
```

`descent-override` corrects the metric at the source — no per-element rules needed. Apply when self-hosting is possible.

**Never:** Apply `overflow: hidden` to containers holding Syne text as a fix — it clips descenders harder, not less.

---

## Font Loading

All fonts load via CSS `@import` in the `<style>` block — never via a CDN `<script>` tag.

```css
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;500&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=EB+Garamond:ital,wght@0,400;1,400&family=Cinzel:wght@400;600&family=Space+Mono:wght@400;700&family=Lora:ital,wght@0,400;1,400&family=DM+Sans:wght@400;500&display=swap');
```

Import only the fonts the active theme requires — not the full list above. Select from the THEME BUNDLES below.

---

## Adaptive Vessel Skin — Five Theme Bundles

Each bundle defines: body font, display font, a tonal palette shift, and spatial rhythm. Select the bundle that matches the engine's cognitive register. Auto-detect from system prompt register; user can override via theme chips in settings drawer. Persist selected theme in `localStorage` under key `hek_theme`.

---

### RITUAL
*Spiritual, contemplative, symbolic, ceremonial*

```css
--font-body:    'Cormorant Garamond', Georgia, serif;
--font-display: 'Syne', sans-serif;
--font-mono:    'Space Mono', monospace;
--line-height:  1.75;
--letter-space: 0.02em;
--palette-shift: hue-rotate(0deg); /* default atmospheric palette */
```

Body: Cormorant Garamond — expansive, unhurried, liturgical weight.
Display: Syne — geometric counterpoint, carries the engine name.
Rhythm: generous line height, slow vertical pacing.

---

### ORACULAR
*Prophetic, archetypal, mythic, aphoristic*

```css
--font-body:    'EB Garamond', Georgia, serif;
--font-display: 'Cinzel', serif;
--font-mono:    'Space Mono', monospace;
--line-height:  1.65;
--letter-space: 0.04em;
--palette-shift: hue-rotate(15deg); /* slight warm shift */
```

Body: EB Garamond — classical authority, dense without heaviness.
Display: Cinzel — roman inscription register, carries weight of pronouncement.
Rhythm: tighter letter-spacing, compressed vertical density.

---

### ANALYTICAL
*Logical, structured, technical, classificatory*

```css
--font-body:    'Inter', system-ui, sans-serif;
--font-display: 'Source Serif 4', Georgia, serif;
--font-mono:    'Space Mono', monospace;
--line-height:  1.6;
--letter-space: 0em;
--palette-shift: hue-rotate(-10deg); /* cooler, bluer shift */
```

Body: Inter — legible at density, zero decorative noise.
Display: Source Serif 4 — authority without ornamentation.
Rhythm: neutral spacing, information-forward layout.

---

### RUPTURE
*Disruptive, deconstructive, raw, fragmented*

```css
--font-body:    'Space Mono', monospace;
--font-display: 'Syne', sans-serif;
--font-mono:    'Space Mono', monospace;
--line-height:  1.5;
--letter-space: -0.01em;
--palette-shift: hue-rotate(30deg); /* warmer, more saturated */
```

Body: Space Mono — mechanical, anti-humanist, resists smooth reading.
Display: Syne — sharp, compressed, cuts.
Rhythm: tight, confrontational spacing.

---

### SOMATIC
*Embodied, somatic, therapeutic, grounded*

```css
--font-body:    'Lora', Georgia, serif;
--font-display: 'DM Sans', system-ui, sans-serif;
--font-mono:    'Space Mono', monospace;
--line-height:  1.8;
--letter-space: 0.01em;
--palette-shift: hue-rotate(-5deg); /* slight warm earth shift */
```

Body: Lora — warm, humanist serif, carries felt sense.
Display: DM Sans — grounded, unpretentious, clear.
Rhythm: widest line height, most breath between lines.

---

## Theme Chip Implementation

Theme selector lives in the settings drawer — five labeled chips.

```html
<div class="theme-chips">
  <button class="chip" data-theme="RITUAL">RITUAL</button>
  <button class="chip" data-theme="ORACULAR">ORACULAR</button>
  <button class="chip" data-theme="ANALYTICAL">ANALYTICAL</button>
  <button class="chip" data-theme="RUPTURE">RUPTURE</button>
  <button class="chip" data-theme="SOMATIC">SOMATIC</button>
</div>
```

```javascript
function applyTheme(name) {
  const themes = {
    RITUAL:     { body: "'Cormorant Garamond', Georgia, serif", display: "'Syne', sans-serif", lh: '1.75' },
    ORACULAR:   { body: "'EB Garamond', Georgia, serif",        display: "'Cinzel', serif",    lh: '1.65' },
    ANALYTICAL: { body: "'Inter', system-ui, sans-serif",       display: "'Source Serif 4', Georgia, serif", lh: '1.6' },
    RUPTURE:    { body: "'Space Mono', monospace",              display: "'Syne', sans-serif", lh: '1.5' },
    SOMATIC:    { body: "'Lora', Georgia, serif",               display: "'DM Sans', system-ui, sans-serif", lh: '1.8' }
  };
  const t = themes[name];
  if (!t) return;
  document.documentElement.style.setProperty('--font-body', t.body);
  document.documentElement.style.setProperty('--font-display', t.display);
  document.documentElement.style.setProperty('--line-height', t.lh);
  localStorage.setItem('hek_theme', name);
  document.querySelectorAll('.chip').forEach(c =>
    c.classList.toggle('active', c.dataset.theme === name)
  );
}

// Load persisted theme on init
const saved = localStorage.getItem('hek_theme') || 'RITUAL';
applyTheme(saved);
```

Active chip: highlighted in `var(--accent-main)`.
Theme persists in `localStorage` under `hek_theme`.

---

## Auto-Detection Heuristic

When a system prompt is handed to VESSEL or any engine with adaptive typography, read its register and pre-select:

| Signal words in system prompt | Auto-select |
|---|---|
| spiritual, contemplative, ritual, sacred, symbolic, tarot, shadow | RITUAL |
| prophetic, archetypal, mythic, oracle, vision, fate | ORACULAR |
| analyze, classify, structure, framework, logical, technical, cognitive | ANALYTICAL |
| disrupt, deconstruct, rupture, fragment, raw, challenge, expose | RUPTURE |
| body, somatic, felt, grounded, embodied, therapeutic, integrate | SOMATIC |

Auto-selection is a suggestion — user override via chips always takes precedence.
