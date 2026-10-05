---
name: hybrid-engine-contract
description: >
  Portable architectural contract for building Hybrid HTML Engines from any session or
  project: provider delegation, streaming, palette, engine taxonomy, build constraints,
  banned patterns. Provider and model handling is delegated to model-config-contract (the
  Model Core): providers, chains, keys, defaults and the call layer come from model.json
  plus one pasted block, never from literals in the HTML. Floor: Claude Native inside
  claude.ai; Groq gpt-oss-120b (soft-falls to gpt-oss-20b, hard-falls to the OpenRouter free
  router) standalone; OpenRouter is text-only and standalone-only. Invoke with
  /hybrid-engine, "invoke hybrid engine contract", "load engine contract" or "I want to
  build a hybrid HTML engine". Always pair with /ui-contract (layout, copy, rendering,
  provider dot) and /model-config (provider layer); this skill owns the hybrid law,
  streaming rules, palette, taxonomy and build law.
---

# Hybrid Engine Contract

The portable delta of the **Exploration-Hybrid HTML Engine Architect** project. Everything needed to build a complete, production-grade Hybrid HTML Engine from any session — without being inside the forge project.

**Always invoke alongside UI Contract and the Model Core.** This skill is the delta. UI Contract is the chassis. `model-config-contract` is the provider layer. Together they constitute the full build specification.

```
Invocation: /hybrid-engine  |  "invoke hybrid engine contract"  |  "load engine contract"
Pair with:  /ui-contract     (read UI Contract in full before writing any code)
            /model-config    (Model Core: providers, models, keys, call layer; implied here for every build)
Priority:   This contract > UI Contract > Memory mandates
Providers:  model-config-contract governs all provider and model handling; nothing here restates it
```

---

## WHAT "HYBRID" MEANS — THE NON-NEGOTIABLE CORE

A single `.html` file that:
- Works **inside claude.ai** with zero config — platform proxies `api.anthropic.com` automatically, no Authorization header needed
- Works **in any browser** when opened externally — user supplies key via the settings drawer

One build. Both worlds. Every engine built under this contract is hybrid by definition.

---

## SYSTEM PROMPT AS LIBRARY, NOT CONSTANT

Sourced from Prompt Forge structural DNA (`4c-both-panels-prompt-forge.html`), July 2026. Panel mechanics are owned by UI Contract Constraint 01 (Dual-Panel Law); entry schema by Constraint 20; panel presence/flags by Constraint 22; persistence backend by Constraint 23.

**Old, retired pattern:** `const SYSTEM_PROMPT = \`...\`` — one identity hardcoded into the JS. Changing it means editing code and re-shipping. Never build this way again.

**Current default:** the system prompt lives as a stored, editable library entry — `{ name, triggers, description, body, source, imported }` per UI Contract Constraint 20 — rendered in the left overlay panel when `EnginePanels.library === true`. Even a single-purpose customized engine keeps its one prompt as an editable library entry of one, not a sealed constant.

**Three valid shapes an engine can take under this pattern:**
1. **Single default prompt, still editable** — the simplest case, one library entry, no testing-rig UI needed beyond edit-in-place
2. **Many distinct named prompts** — a testing rig (Prompt Forge itself)
3. **Many versions/registers of one identity** — formal vs. casual, terse vs. expansive, toggleable active/inactive without touching code

**Right panel — response library:** every generated output auto-saves to the right overlay panel per UI Contract Constraint 20, tagged with the producing prompt, timestamped, JSON-exportable. Persistent record sitting behind the live inline output — not a replacement for it.

**Storage:** both panels persist through Constraint 21's abstraction for plain standalone builds, or Constraint 23's folder-connect where a real local folder is available; artifacts always use `window.storage`.

**Upgrade action on any pre-Prompt-Forge engine:** extract its `SYSTEM_PROMPT` constant into a library entry; declare `EnginePanels.library = true` (Constraint 22); add the right-panel response library if absent.

---

## PROVIDERS AND MODELS: DELEGATED TO THE MODEL CORE

Everything about *which* provider, *which* model, *which* key, *which* endpoint and *how* the call is made lives in `model-config-contract` (paste its Model Core block verbatim; edit only its three CONSTANTS). This contract no longer carries `OR_MODEL_MAP`, `GROQ_MODEL_CHAIN`, per-provider `fetch` branches, or its own `readStream`. Those were hardcoded copies of what `model.json` now owns; they are retired.

**What does not change (the floor):**
- Inside claude.ai the default is Claude Native (`claude-sonnet-4-6`, no key, no Authorization header, platform proxy).
- Standalone, the default is Groq `openai/gpt-oss-120b`, soft-falling to `openai/gpt-oss-20b` on 429/5xx, hard-falling to the OpenRouter free router `openrouter/free` if Groq itself is dead. These values now live in `model.json` (`modelChain`, `softFallback`, `hardFallback`) and are mirrored in the core's `LOCAL_FALLBACK_CONFIG`.
- **OpenRouter is text-only and standalone-only.** One slug in the floor, `openrouter/free` (the Free Models Router, which picks a live free text model). NEVER `openrouter/auto`: that is the paid Auto Router, the `:free` suffix does not restrict it, and it will bill. No image payloads, no vision logic.
- **Artifact routing:** OpenRouter has no CORS proxy inside claude.ai. A provider flagged `standaloneOnly` in config is blocked at `run()` when `isArtifact` is true, with an inline notice. Claude Native remains the only artifact-safe path. This is data-driven (`standaloneOnly`), never a `startsWith('or-')` string test.

**`callAI` keeps its signature** `(systemPrompt, userMessage, onChunk)`, text-only, and becomes a thin wrapper over the core:

```javascript
/* callAI: unchanged contract, everything underneath is the Model Core */
async function callAI(systemPrompt, userMessage, onChunk) {
  var prev = 0;
  await callModel({ provider: getSelectedProvider(), system: systemPrompt, user: userMessage,
    onText: function (acc) { if (acc.length < prev) prev = 0; onChunk(acc.slice(prev)); prev = acc.length; } });   // core reports accumulated text; onChunk wants deltas
}
function getSelectedProvider() { var s = document.getElementById('providerSelect'); return (s && s.value) || defaultProviderId(); }
function providerBlockedHere(id) { var p = P(id); return !!(p && p.standaloneOnly && isArtifact); }   // run() shows the notice and returns when true
```

Curated mode (this wrapper) walks the provider's chain and fallbacks. An engine that needs content validation, abort, or accumulated text calls `callModel` directly (`validate`, `signal`, `onText`). Engines with a model picker use strict mode via `model-catalog-panel`.

A pipeline engine that wants accumulated partials and the final text back (for example a two-stage generate-then-render engine, tested in the Prompt Generation Engine) defines `callAI` as this variant **instead of** the wrapper above:

```javascript
async function callAI(systemPrompt, userMessage, onPartial) {            // variant: onPartial gets the accumulated text, the promise resolves to the final text
  const r = await callModel({ provider: getSelectedProvider(), system: systemPrompt, user: userMessage, onText: function (acc) { if (onPartial) onPartial(acc); } });
  return r.text;
}
```

---

## STREAMING FINALIZATION: FOUR-LAYER SAFETY PATTERN

**Timing values are owned by UI Contract Constraint 13 (defaults) and by `model.json` (per-provider overrides). This section states the rule; the implementation is `readStream` in the Model Core.**

**Root cause (Anthropic-specific):** Anthropic SSE never emits `[DONE]`. The termination signal is `event: message_stop` as a named event line, which appears BEFORE its `data:` line, so it must be checked before the `data:` filter. A loop that only checks `data === '[DONE]'` hangs indefinitely on the Anthropic provider. The core's `readStream` checks the named event line and the payload `type`.

The four layers, all inside the core: (1) the stream's own terminator (`[DONE]`, `message_stop`, or the reader's `done`); (2) a `done` flag so finalization runs once; (3) an idle timer that resets on every content chunk; (4) a hard ceiling set once before the fetch. Defaults are 3 s idle and 15 s hard; a provider's `idleMs` and `timeoutMs` in `model.json` override them (the OpenRouter route runs 9 s and 45 s because free routes queue). Reasoning deltas count as alive, so thinking models are not cut off while they think.

NEVER write a second `readStream` in an engine. NEVER use a `while(true)` read loop.

---

## MULTI-CALL SEQUENCING ON CLAUDE NATIVE

When an engine fires multiple `callAI()` calls in the same session (parallel card outputs, multi-lens engines, multi-stage pipelines) — **use sequential firing on Claude Native only** (the provider whose config entry has `native: true`).

**Why:** `Promise.all()` causes token budget competition on the claude.ai artifact proxy. All streams compete for a shared per-session budget. Later streams receive less and terminate mid-generation without error — output appears truncated with a "Complete" status. Silent failure that looks like model behavior.

```javascript
// Required pattern for Claude Native multi-call engines
runOne('l1').then(() => runOne('l2')).then(() => runOne('l3')).then(() => {
  // all complete — re-enable UI
});
```

**Groq, OpenRouter:** `Promise.all()` is fine — they handle parallel calls independently.

**UI pattern:** Set non-active cards to "Queued" on start. Each transitions Queued → Burning → Complete in sequence.

---

## PROVIDER SELECTOR + CONTEXT-AWARE DEFAULT

Rendered from config, set programmatically on load, never hardcoded in HTML. The markup is an empty control with no `selected` attribute and no literal `<option>` rows:

```html
<select id="providerSelect"></select>
```

```javascript
function renderProviderSelector() {                    // options come from model.json via the core, never from markup
  var sel = document.getElementById('providerSelect'), keep = sel.value; sel.innerHTML = '';
  usableProviders().forEach(function (p) { sel.appendChild(new Option(p.label, p.id)); });
  sel.value = usableProviders().some(function (p) { return p.id === keep; }) ? keep : defaultProviderId();
  updateProviderDot();                                  // dot colour from p.dotColor (UI Contract 18B)
}
function defaultProviderId() {                          // artifact -> defaultFor 'artifact' (Claude); standalone -> defaultFor 'standalone' (Groq)
  var ps = usableProviders(), want = isArtifact ? 'artifact' : 'standalone';
  var d = ps.filter(function (p) { return (p.defaultFor || []).indexOf(want) > -1; })[0] || ps[0];
  return d && d.id;
}
/* boot: render from the floor immediately, then upgrade when the live config lands */
renderProviderSelector(); fetchModelConfig(function (src) { renderProviderSelector(); renderDrawerKeyRows(); setConfigBadge(src); });
```

**Warning banner logic (data-driven):**
- Artifact + native provider: no banner, no key row.
- Artifact + provider with `standaloneOnly`: show that provider's `keyNote` as the artifact notice, block `run()`.
- Standalone + provider with `requiresKey` and no saved key: show the key warning banner.
- Any provider with a saved key: no banner.

**Storage:** keys live at `hek_{keyStorageName}` (Groq `hek_groq`, OpenRouter `hek_openrouter`) through the core's `getKey(name)` / `setKey(name, value)`. The selected provider id is `getSelectedProvider()`.

**Gear drawer key rows** are rendered from `providers[]` (see model-config-contract, DYNAMIC DRAWER KEY ROWS): native providers get a read-only "No key needed — platform routes natively"; the rest get a password input with `keyPlaceholder` and, when present, an inline orange `keyNote`.

**Engines with a model picker** (`model-catalog-panel`) replace this selector with a lane button (Lanes mode) or per-stage model chips (Panel mode). A dropdown beside a picker recreates the two-path conflict, so exactly one control chooses the model; the one exception is the catalog skill's matrix variant (A3d), where an engine that already has a second axis of work keeps its curated Run and provider selector and adds a separate `Fan out (n)` button for lanes.

---

## PALETTE — CSS VARIABLES (always use these names)

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

---

## ATTRIBUTION — ZONE C + FOOTER

Zone C (right side of header) carries the maker's mark on every build without being asked. "crafted by" is lowercase italic, never capitalized (UI Contract Constraint 07):

```html
<div class="zone-c">
  <i>crafted by</i><br>
  <a href="mailto:meet.venkat1@gmail.com">meet.venkat1@gmail.com</a>
</div>
```

```css
.zone-c {
  font-size: 0.72rem;
  color: var(--text-muted);
  text-align: right;
  line-height: 1.3;
}
.zone-c a { color: var(--text-muted); text-decoration: none; }
```

No footer. Zone C only. (UI Contract Constraint 07.)

---

## ENGINE TAXONOMY — AUTO-DETECTION

When input describes an engine without naming a type, match here:

| Engine Type | Detect When Input Mentions | Structure Pattern |
|---|---|---|
| **Cognitive Pipeline** | stages, steps, reorientation, reframe, shift, analysis pipeline | Left panel stage list + right canvas, context injected between stages |
| **Topology Mapper** | map, diagram, visualize, concept graph, structure, topology | SVG canvas, topology override chips, 4 views (Diagram / Structure / Multi / Export) |
| **Lens Interpreter** | lenses, dimensions, portals, perspectives, multi-angle, interpret through | Lens family selector, dimension grid, per-lens output cards |
| **Pattern Library** | patterns, catalog, library, save thinking, recurring, export/import | Pattern cards, save/delete, JSON export/import |
| **Learning Engine** | curriculum, learn, teach, domain, schema, adaptive, levels | Domain input, schema drag-drop, depth selector, module output |
| **Prompt Builder** | system prompt, build prompt, prompt architect, raw intent → prompt | Section-structured output (ROLE/FUNCTION/RULES/OUTPUT), copy button |
| **Text Transformer** | convert, reformat, markdown, rich text, Notion, Google Docs | Mode chips, input → output side by side |
| **Hook Generator** | hook, headline, opening line, tone variants, audience | Tone selector chips, variant counter, copy per variant |
| **Meta-Intent Engine** | intent, before building, what do I want, capture goal | Structured intent form → intent document output |

No match → default to **Cognitive Pipeline**.

---

## NODE COLOR SEMANTICS (SVG engines)

| Node type | Hex | Variable |
|---|---|---|
| Root / Central | `#7c6ef5` | `--accent-main` |
| Cause / Input | `#f5a623` | `--amber` |
| Effect / Output | `#4caf82` | `--green` |
| Terminal / End | `#f56565` | `--coral` |
| Connector | `#38bdf8` | `--teal` |
| Neutral | `#9090a8` | `--text-secondary` |

---

## BUILD CONSTRAINTS — ALWAYS ENFORCED

- Single `.html` file — all CSS and JS inlined
- No CDN dependencies, no frameworks, no external scripts
- No `<form>` tags — use `<div>` with `addEventListener`
- No `max-width: 62ch` or any fixed-width constraint on output text
- Streaming SSE on every API call — never non-streaming
- Keys at `hek_{keyStorageName}` (Groq `hek_groq`, OpenRouter `hek_openrouter`), read and written only through the Model Core's `getKey`/`setKey`
- No provider list, model slug, endpoint, key slot, default or stream timing literal in the HTML: all of it comes from `model.json` through the Model Core
- Attribution email in Zone C: `meet.venkat1@gmail.com`
- File size target: under 200KB unminified
- Every engine is hybrid by definition
- Multi-call engines on Claude Native use sequential firing — never `Promise.all()`
- All copy buttons use canonical `copyToClipboard(text, btn)` function (UI Contract Constraint 05)
- All AI output rendered via `innerHTML` with markdown parser — never `textContent`
- Providers flagged `standaloneOnly` (OpenRouter) are always blocked at `run()` in artifact context
- `callAI()` signature is `(systemPrompt, userMessage, onChunk)` — text-only, no vision params

---

## BANNED PATTERNS — NEVER USE

- `max-width: 62ch` on output text (extends to all fixed-width content constraints)
- `<form>` tags anywhere
- Non-streaming API calls
- CDN imports or external framework scripts
- `display:none` on event-wired elements — use `visibility:hidden` + `pointer-events:none`
- `position:sticky` inside `overflow:scroll` on interactive elements
- Raw `navigator.clipboard` calls without canonical `copyToClipboard(text, btn)`
- `Range.selectNodeContents` on hidden divs (retired pattern)
- Copy All gated on `lastResults` flag (silently fails mid-stream)
- `while(true)` readStream loop (hangs on Anthropic SSE — use the three-layer pattern above)
- `Promise.all()` for multi-call on Claude Native (token budget competition)
- `selected` attribute or any literal `<option>` rows in the provider selector (rendered from config)
- `Authorization` header in Claude Native fetch call
- Calling a `standaloneOnly` provider (OpenRouter) inside artifact context without blocking: no CORS proxy, the call fails silently
- Hardcoding any provider, model slug, endpoint, key slot or stream timing in the HTML. `OR_MODEL_MAP`, `GROQ_MODEL_CHAIN`, literal per-provider `fetch` branches and an engine-local `readStream` are retired; they come from `model.json` via the Model Core
- `openrouter/auto` anywhere (paid router)

---

## BUILD ORDER — ALWAYS FOLLOW THIS SEQUENCE

```
BEFORE step 1 — Invoke UI Contract: read /mnt/skills/user/ui-contract/SKILL.md in full.
BEFORE step 1 — Invoke the Model Core: read /mnt/skills/user/model-config-contract/SKILL.md in full.
BEFORE step 1 — Clarify intent, layout, what-renders-where if anything is ambiguous.
```

1. HTML skeleton + all section divs
2. CSS — full inline `<style>` block using palette variables
   ↳ Apply UI Contract Constraint 03 (output width) and Constraint 08 (visibility)
3. Paste the Model Core block (model-config-contract), set its three CONSTANTS, add the thin `callAI` wrapper
   ↳ Apply multi-call sequencing rule if engine fires multiple parallel calls
4. Gear drawer (UI Contract Constraint 06) with key rows rendered from config; keys via the core's `getKey`/`setKey`
5. Provider selector rendered from config, context-aware default, warning banner logic (or the picker control, if `model-catalog-panel` is in use)
6. Engine-specific pipeline/logic (the functional core)
   ↳ Apply UI Contract Constraint 01 (dual-panel layout) and Constraint 02 (markdown rendering)
   ↳ Declare `window.EnginePanels` (UI Contract Constraint 22) — library/importExport/settings flags, decided at Step 3 clarify-before-building, not invented mid-build
   ↳ If `EnginePanels.library === true`: wire panel per Constraint 01, entry schema per Constraint 20, persistence per Constraint 23
   ↳ Wire all copy buttons through UI Contract Constraint 05 (three-path triad)
7. SVG rendering (if topology/graph engine)
8. Secondary views / tabs (if multi-view engine)
9. Error handling — every API call wrapped in try/catch, errors shown in output area
   ↳ Confirm Zone C maker's mark present (UI Contract Constraint 07)

---

## QUICK REFERENCE

```
CONTRACT         : hybrid-engine-contract (delta) + ui-contract (chassis) + model-config-contract (Model Core)
PRIORITY         : This contract > UI Contract > Memory mandates; provider/model handling is the Model Core's
HYBRID LAW       : One .html file. Works inside claude.ai AND as standalone.
PROVIDER DEFAULT : Artifact → Claude (claude-sonnet-4-6) | Standalone → Groq gpt-oss-120b (defaultFor, from model.json)
PROVIDERS        : from model.json via the Model Core (Claude Native, Groq, OR Free Router today) — never literals in HTML
FLOOR            : defaultLanes = groq::openai/gpt-oss-120b + or-auto::openrouter/free; mirrored in LOCAL_FALLBACK_CONFIG
GROQ CHAIN       : in model.json: gpt-oss-120b → gpt-oss-20b (soft, 429/5xx) → hardFallback or-auto (dead/404).
                   Dropdown label never changes; fallback is silent. llama-3.3-70b-versatile RETIRED (Groq shutdown Aug 2026).
                   Chain edits are model.json edits, last verified 2026-10-03 — never HTML edits.
STORAGE PREFIX   : hek_{keyStorageName} via the core's getKey/setKey — Groq hek_groq, OpenRouter hek_openrouter
OR RULES         : text-only | standalone-only (standaloneOnly flag) | openrouter/free only | NEVER openrouter/auto (bills)
OR DOT COLOR     : #f97316 (config dotColor)
callAI SIGNATURE : (systemPrompt, userMessage, onChunk) — thin wrapper over callModel, text-only
STREAM FORMAT    : SSE — anthropic delta | openai choices delta (Groq + OR); parsed by the core's readStream
STREAM SAFETY    : Four-layer: message_stop/[DONE] | done flag | idle timer | hard ceiling
                   Defaults 3s/15s (UI Contract C13); per-provider idleMs/timeoutMs in model.json override (OR 9s/45s)
MULTI-CALL       : Sequential on Claude Native (native:true) — never Promise.all()
PALETTE ROOT     : --bg-void #0a0a0f | --accent-main #7c6ef5 | --orange-warn #f97316
HEADER           : Zone A name + config badge | Zone B ☰ + model control + ▤ + ⚙ | Zone C "crafted by" (lowercase italic) + meet.venkat1@gmail.com
ATTRIBUTION      : Zone C only — no footer
PANELS           : window.EnginePanels{library,importExport,settings} — one model, no named tiers (UI Contract C22)
                   importExport independent of library; export always available, import needs library or a receiver
                   Entry schema (prompt + response) per UI Contract C20
PERSISTENCE      : Artifact → window.storage | Standalone → File System Access folder-connect, 1 JSON/entry + index.json (+ UI Contract 23B robustness sub-laws)
                   Backend inherits isArtifact — never a second context check (UI Contract C23)
BANNED           : 62ch, fixed-width containers, <form>, non-streaming, CDN, display:none
                   on wired elements, sticky inside scroll, raw clipboard, while(true) stream,
                   Promise.all() on Claude Native, hardcoded selected/literal provider options, Auth header on Claude,
                   standaloneOnly provider called in artifact context without blocking, any provider/slug/endpoint/timing literal in HTML,
                   OR_MODEL_MAP / GROQ_MODEL_CHAIN / engine-local readStream (retired), imageData/imageMime in OR arm,
                   openrouter/auto (paid router — will bill), isVisionModel usage (retired)
OUTPUT           : .html file + one paragraph summary
CONFLICT         : Unnamed implications ≠ overrides — flag and ask before building
```
