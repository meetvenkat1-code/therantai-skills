---
name: ui-contract
description: A living constraint map governing the structural, behavioral, and rendering laws of every HTML engine build. Invoke with /ui-contract or by saying "invoke UI Contract" or "update UI Contract". Triggers when building any new engine, modifying an existing engine's layout, or adding new resolved constraints discovered during builds. Apply all constraints before writing any code. Update cumulatively as new friction is resolved — never re-solve a constraint already in this map.
---

# UI CONTRACT — OPERATIONAL SPINE (compressed)

Invoke: `/ui-contract`. Read in full before writing code. Never re-solve a listed constraint.

## PRIORITY ORDER
1. Project system prompt (explicit override only, scoped to named point)
2. UI Contract (default)
3. Memory standing mandates
Conflict → flag, ask. Unnamed implication ≠ override.

## BUILD SEQUENCE (all projects)
```
1. Clarify intent, layout, what-renders-where
2. Invoke UI Contract (+ Model Core, model-config-contract, for any engine that calls an LLM)
3. System prompt first
4. Standalone HTML, all constraints applied
5. Artifact by subtraction — never artifact-first
```
Hybrid/Exploration-Hybrid projects: UI Contract gates fire at steps 1(before)/2(width+visibility)/6(panels+markdown+copy)/9(after: maker's mark check).

## COGNITIVE IDENTITY LAW
Before build closes, one sentence in system prompt: `This engine [verb]s [what] so that [who] can [transformation].` No declaration → build not closed. Not a UI element.

---

## 01 — DUAL-PANEL LAW
- Overlay only, never static sidebar. Closed by default.
- Left = prompt library (`☰`), right = response library (`▤`), both Zone B, flanking the model control (see 07).
- Left slides from left, right from right. Independent backdrop + toggle per panel — never shared.
- Canvas = 100% width always, neither panel compresses it.
- `position:fixed`; closed: `translateX(-100%)` left / `translateX(100%)` right; open: `translateX(0)`; `transition:0.25s ease`.
- Single-panel engines follow same law in full.
- NEVER: `width:240px;flex-shrink:0` nav-in-flex-row. NEVER shared backdrop/toggle across panels.

### 01B — ASYMMETRIC PANEL SPECIFICITY LAW
Any panel with an ID-level positional `transform` override must declare its open-state rule at matching ID-level specificity: `#panelId.open{transform:translateX(0);}` — never inherited from `.panel.open` alone. Class-toggle confirmation (`classList` shows `open`) is NOT sufficient proof of a visible fix. Verify with `getComputedStyle(panel).transform`.

## 02 — MARKDOWN RENDERING
`innerHTML` + parser only, never `textContent`+`pre-wrap`. Convert: `**b**`→strong, `*i*`/`_i_`→em, `***`→strong+em, `#`/`##`/`###`→h1/h2/h3, `-`/`*`→ul>li, `1.`→ol>li, backtick→code, `---`→hr, `\n\n`→paragraph, `\n`→br. Stream incrementally: `innerHTML = renderMarkdown(accumulated)` per chunk, never render-on-completion-only. Escape `&<>` before pattern-matching.

## 03 — OUTPUT WIDTH
80–90% window width. No `max-width` on canvas/output body (includes banning `max-width:62ch`). Padding ≤1.5rem. `width:100%; word-break:break-word`. NEVER centered column with fixed px max-width.

## 04 — UNIVERSAL COPY BUTTON (mandatory, all builds, unrequested)
Top-positioned (header Zone B/C, or above output). Concatenates all stage/response outputs in order, divider: `\n\n— Stage 01: [Name] —\n\n`. Per-card copy buttons additive, never substitute. All buttons call the single canonical `copyToClipboard(text, btn)` — no second implementation anywhere.

## 05 — CANONICAL COPY (sole transport law)
`window.self !== window.top` is a structural constant `true` inside artifacts — NEVER branch copy logic on IS_ARTIFACT. NEVER use `<div>` for selection — `<textarea>` only (survives removal). NEVER "press Ctrl+C" prompt — show `✗ Failed`, revert.

```javascript
function copyToClipboard(text, btn) {
  if (!text || !text.trim()) return;
  var origHTML = btn.innerHTML;
  var ICON_CHECK = '<svg viewBox="0 0 24 24" style="width:11px;height:11px;stroke:currentColor;fill:none;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round"><polyline points="20 6 9 17 4 12"></polyline></svg>';
  function onSuccess() { btn.innerHTML = ICON_CHECK + ' Copied'; btn.classList.add('copied'); setTimeout(function(){ btn.innerHTML=origHTML; btn.classList.remove('copied'); },2000); }
  function onFail() { btn.textContent = '✗ Failed'; setTimeout(function(){ btn.innerHTML=origHTML; },2000); }
  function execCopy() {
    var ta = document.createElement('textarea'); ta.value = text;
    ta.style.cssText = 'position:fixed;left:-9999px;top:-9999px;opacity:0;font-size:12px;pointer-events:none;';
    ta.setAttribute('readonly','');
    document.body.appendChild(ta); ta.focus(); ta.select(); ta.setSelectionRange(0,text.length);
    var ok=false; try{ ok=document.execCommand('copy'); }catch(e){}
    document.body.removeChild(ta); ok ? onSuccess() : onFail();
  }
  if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(text).then(onSuccess).catch(execCopy); }
  else { execCopy(); }
}
```
Button: `<button class="copy-btn" onclick="copyToClipboard(targetText,this)"><svg>...</svg> Copy</button>`
CSS min: `.copy-btn{display:flex;align-items:center;gap:5px;background:none;border:1px solid var(--bg-border);color:var(--text-muted);font-size:.65rem;padding:4px 10px 5px;border-radius:5px;cursor:pointer;transition:all .2s;white-space:nowrap;flex-shrink:0} .copy-btn svg{width:11px;height:11px;stroke:currentColor;fill:none;stroke-width:1.8} .copy-btn:hover{border-color:var(--accent-main);color:var(--accent-main)} .copy-btn.copied{border-color:var(--green);color:var(--green)}`

Universal button: never gate on `lastResults` — reads live DOM as fallback, `innerText` concatenation with dividers. Per-card: direct child of card-header flex row, `innerText`, `copyToClipboard(text,this)`.

BANNED: `contextCopy`/`copyWithFallback`/`artifactCopy`, any IS_ARTIFACT copy branch, `<div>` selection, `showCopyModal()`, `navigator.clipboard` with no execCopy fallback, `Range.selectNodeContents`, gating Copy-All on `lastResults`.

## 06 — SETTINGS GEAR DRAWER
Right-side slide-in, `top:[headerH]; right:0; bottom:0; width:320px`; **400px (max 92%) for catalog drawers, the one width exception** (see 25). `translateX(100%)`closed→`translateX(0)`open, with the ID-level open rule `#gearDrawer.open{transform:translateX(0)}` per 01B. Backdrop closes on click. Key rows are **rendered from `model.json`** (model-config-contract), never literal: values save to `localStorage` at `hek_{keyStorageName}` through the Model Core's `getKey`/`setKey`. Save button → "✓ Saved" → revert 1.5s, auto-close. Native provider row: read-only "No key needed — platform routes natively". Every other row: password input with the config's `keyPlaceholder` plus the config's `keyNote` (OpenRouter's orange "Standalone only"). A "Clear saved keys" control clears the `hek_` slots and any legacy slots.
Section order in an engine with a model picker: model list (lanes or panels), Model catalog, Keys, then **engine-specific settings** (for example Corpus: retrieval keys, index host, chunk count) as one more titled section in the same drawer, never a second drawer. Never full-page settings.

## 07 — HEADER CONTRACT (Zone A/B/C)
A(left): name + badge (+ `Config: Live / Local Fallback` badge when the engine reads model.json). B(center-right): `☰` + model control + `▤` + `⚙`, where the model control is the provider selector (curated engines) or the lane button (Lanes mode, dot inside; in the matrix variant the provider selector stays and a `Fan out (n)` button sits beside Run); Panel mode has none in the header because per-stage chips own the model. Panels whose `EnginePanels` flag is false are not rendered. C(far-right, mandatory, unrequested):
```
crafted by            [italic, .72rem, muted, no caps]
meet.venkat1@gmail.com [mailto link, plain, .72rem, muted]
```
Stacked flex-column, never inline, never moved off far-right. No footer, ever. NEVER capitalize "crafted by".

## 08 — VISIBILITY CONTRACT
Never `display:none` on event-wired interactive elements (breaks click-handlers on re-show). Use `visibility:hidden;pointer-events:none` / `visibility:visible;pointer-events:all`. Exception: decorative, no-listener elements may use `display:none`.

## 09 — STICKY/SCROLL CONTRACT
Never `position:sticky` inside `overflow:scroll|auto` for elements needing click-through — creates dead zones. Interactive elements in scroll containers: flat-flow, always-in-DOM.

## 10 — BUILD SEQUENCE GATES
See BUILD SEQUENCE above. Exploration-Hybrid: contract invoked as Step 0 of FORGE IT release.

## 11 — HYBRID COPY RULE
Every engine is hybrid by default. Constraint 05's context-aware pattern present in every copy function regardless of test target.

## 12 — CONTEXT-AWARE PROVIDER DEFAULT
Data-driven (model-config-contract): the default is the usable provider whose config `defaultFor` contains `'artifact'` or `'standalone'`; picker engines seed from `defaultLanes()`.
```javascript
const isArtifact = window.self !== window.top;
function defaultProviderId(){ const ps = usableProviders(), want = isArtifact ? 'artifact' : 'standalone';
  const d = ps.filter(p => (p.defaultFor||[]).includes(want))[0] || ps[0]; return d && d.id; }
document.getElementById('providerSelect').value = defaultProviderId();
```
Artifact→Claude Native (no key, `claude-sonnet-4-6` only — never date-suffixed strings). Standalone→Groq today (key from `hek_groq`); that is config, not HTML. NEVER hardcode `selected` or literal `<option>` rows — JS renders the selector from config post-DOM-load. Banner: artifact+native→none; artifact+`standaloneOnly`→notice, block `run()`; standalone+`requiresKey`+no-key→warn; key stored→none.

## 13 — STREAMING FINALIZATION (four-layer, never rely on chunk.done alone)
```javascript
let done=false, idleTimer=null;
const DEFAULT_IDLE_MS=3000, DEFAULT_TIMEOUT_MS=15000;          // defaults only
const idleMs=cfg.idleMs||DEFAULT_IDLE_MS, timeoutMs=cfg.timeoutMs||DEFAULT_TIMEOUT_MS;   // per-provider override from model.json (OpenRouter 9000/45000)
function finalize(){ if(done)return; done=true; clearTimeout(idleTimer); /* unlock UI */ }
// 1. [DONE] SSE token (primary)
if (data === '[DONE]'){ finalize(); return; }
// 2. chunk.done (clean close)
if (chunk.done){ finalize(); return; }
// 3. idle timer — reset per content chunk (reasoning deltas also reset it)
clearTimeout(idleTimer); idleTimer=setTimeout(finalize, idleMs);
// 4. hard ceiling — set once pre-fetch
setTimeout(finalize, timeoutMs);
```
`done` flag prevents double-finalization. 3000/15000 are the defaults; `idleMs`/`timeoutMs` on a provider in `model.json` override them. This is implemented once, in the Model Core's `readStream` (model-config-contract) — engines never write their own.

## 14 — [retired → typography skill]

## 15 — EXPORT CONTRACT
Hybrid (default, universal): `.txt` via Blob/createObjectURL + canonical copy button. Google Drive write architecturally excluded from hybrid — never wire Drive/Docs API into a hybrid engine, either path.
Standalone-only (explicit): + File System Access API (native picker, read/augment/write-in-place, Chrome/Edge only) + Google Docs API write (user OAuth token).

## 16/17 — [retired → browser-injection skill]

## 18A — SANDWICH LAYOUT LAW
Fixed header (top) + scrolling middle + fixed input bar (bottom). No max-height/truncation on output.
```css
body{margin:0;overflow:hidden}
.header{position:fixed;top:0;left:0;right:0;height:48px;z-index:100}
.output-area{position:fixed;top:48px;bottom:64px;left:0;right:0;overflow-y:auto;padding:1.5rem}
.input-bar{position:fixed;bottom:0;...}
```
Canvas width still 80-90% (Constraint 03) inside the fixed layers. NEVER `position:relative`/document-flow header or input bar. NEVER `min-height:100vh` on scroll container.

## 18B — PROVIDER DOT STANDARD
Dot lives inside the control that chooses the model — never external chips/pills/button-rows. Colours come from the provider's `dotColor` in `model.json` (today: Groq `#22c55e` 🟢 · Claude `#ef4444` 🔴 · OpenRouter `#f97316` 🟠; `#9090a8` if a provider has none). Lane button: the dot of the first active lane. Panel chip: the dot of that panel's provider.
```javascript
function updateProviderDot(){ const p = P(document.getElementById('providerSelect').value);
  document.getElementById('providerDot').style.background = (p && p.dotColor) || '#9090a8'; }
```
Banner: as in 12. Artifact blocking: `P(id).standaloneOnly && window.self !== window.top` → block `run()`, show the provider's `keyNote` as the notice.
NEVER render the provider list as external chips/button rows. NEVER a `DOT_COLORS` literal or a `startsWith('or-')` test.

## 19 — COGNITIVE IDENTITY LAW
See top. Non-UI, lives in system prompt + session record.

## 20 — LIBRARY ENTRY SCHEMA + IMPORT/EXPORT SYMMETRY
Prompt entry: `{name, triggers, description, body, source, imported}`, key `prompts:{slug}`. `source`: `markdown`|manual. `imported`: ISO timestamp.
Response entry: auto-saves on completion (never opt-in), tagged with source prompt+slug, timestamped, keyed by response id.
Both panels mandatory: `.md` import (prompt panel only), JSON export (`Blob+JSON.stringify(arr,null,2)`), JSON import (merge, never overwrite).
NEVER export-without-import or import-without-export. NEVER untagged response entries.

## 21 — STORAGE ABSTRACTION LAYER
Never scatter raw `localStorage` calls. Route through:
```javascript
function storageSet(key,value){ localStorage.setItem(key,value); return true; }
function storageGet(key){ return localStorage.getItem(key); }
function storageRemove(key){ localStorage.removeItem(key); return true; }
function storageList(prefix){ const keys=[]; for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i); if(k&&k.startsWith(prefix))keys.push(k);} return keys; }
```
Artifacts: `window.storage` (get/set/delete/list, `shared` flag) supersedes `localStorage` — silently fails inside artifact iframe otherwise. Standalone: superseded by Constraint 23 folder-connect when available; this abstraction is the fallback (declined picker / unsupported browser). Provider keys go through the Model Core's `getKey`/`setKey`, which wrap `localStorage` (`hek_{keyStorageName}`); route them through this layer where the engine has one.

## 22 — UNIVERSAL OPTIONAL PANEL ARCHITECTURE
One panel model for every engine — never a named tier. Flags declared once, pre-panel-code:
```javascript
window.EnginePanels = { library:false, importExport:false, settings:true };
```
`importExport` NOT bundled with `library` — export can run standalone against session state; import requires `library:true` or a declared in-memory receiver. "Active" only toggles DOM/CSS/toggle generation — chassis (function names, storage calls, copy law) never varies.
NEVER invent Full/Lite/Session-Only tiers. NEVER generate dead markup for a `false` flag.

## 23 — STANDALONE PERSISTENCE LAYER (FOLDER-CONNECT)
Reuses Constraint 12's `isArtifact` — never a second context check.
```javascript
if (window.EngineState.isArtifact) { /* window.storage */ } else { /* File System Access API, folder-connect */ }
```
Artifact: `window.storage` only (no real folder access, ever — attempts fail silently/throw).
Standalone: `localStorage` write is unconditional and always fires first, regardless of folder-connect state — folder-connect is strictly additive (dual-write), never a replacement. `window.showDirectoryPicker()` adds a file-per-entry `{id,name,content,tags,provider_preference,created,modified}` + root `index.json` manifest (read first) layer on top when authorized, keyed by the same `id` as the `localStorage` record — one entry, two mirrored addresses, never two records. Folder write failure must not roll back or block the `localStorage` write that already succeeded.
NEVER attempt folder access from artifact context. NEVER duplicate the isArtifact check. NEVER let folder-connect state gate whether `localStorage` receives the entry. NEVER mint a new `id` on folder write — reuse the `localStorage`-assigned `id` to prevent duplicate records across reconnect/forget cycles.

## 23B — FOLDER-CONNECT ROBUSTNESS (extends 23)
- Persist dirHandle in IndexedDB (idbKeyval) so connection survives reload — localStorage cannot hold a FileSystemDirectoryHandle.
- Re-verify on load: queryPermission→requestPermission; distinct "Reconnect required" state ≠ "Not connected".
- Tag every disk record {engine: ENGINE_ID, schemaVersion}. Skip foreign-engine-tagged records on sync.
- Untagged file → claim ONLY if it structurally matches this engine's own record shape (e.g. prompt: body+triggers[]+name; response: promptSlug+input+output). Filename match alone is insufficient — shape-check is the gate. Absence of tag ≠ ownership.
- Reconcile same-slug/id duplicates: newest mtime wins, delete stale, rename survivor to canonical filename.
- Deletion in-session must remove matching disk file(s) — no resurrection on resync.
- index.json is fast-path cache only — folder scan is source of truth on manifest/disk conflict.
- Backfill-on-connect: on EVERY dirHandle null→set transition (explicit connect AND auto-reconnect-on-load), snapshot local library BEFORE syncFromDisk, diff against disk-confirmed slugs/ids after sync, push any browser-only entries to disk via the same saveRecordToDisk path. Batch writes (5/batch) + yield (requestIdleCallback/setTimeout(0)) between batches — never freeze UI on large pre-existing libraries.
NEVER: assume reload-safety without handle persistence. NEVER trust a saved handle without re-verifying permission. NEVER share a folder across engines without tagging. NEVER claim an untagged file without a structural shape match. NEVER leave duplicate files from a rename/edit unresolved. NEVER let an in-session delete skip the disk file. NEVER treat connect as backup-complete without pushing pre-existing local-only history out on the same action.

## 25 — MODEL DELEGATION (MODEL CORE)
Provider list, model slugs, endpoints, key slots, default lanes, the call layer and stream timing are owned by `model-config-contract` (data: `model.json`; runtime: the Model Core block). The HTML carries none of them as literals. An engine that needs a model picker adds `model-catalog-panel` (Lanes or Panel mode), which consumes the Core API and owns the picker surface: the header lane button or per-stage chips, the catalog, and the 400px drawer. Exactly one control chooses the model in an engine — never a provider dropdown beside a picker; the one exception is the catalog skill's matrix variant (A3d), where an engine that already has a second axis of work keeps its curated Run and provider selector and adds a separate `Fan out (n)` button for lanes.
NEVER: literal `<option>` provider rows · `DOT_COLORS` · `OR_MODEL_MAP` · an engine-local `readStream` or per-provider `callAI` branch · a second key store.

---

## LIVING CONSTRAINT LOG
01 Dual-Panel Law (+01B specificity law) · 02 Markdown rendering · 03 Output width · 04 Universal copy button · 05 Canonical copy (sole transport) · 06 Gear drawer · 07 Header Zone A/B/C + maker's mark · 08 Visibility contract · 09 Sticky/scroll contract · 10 Build sequence gates · 11 Hybrid copy rule · 12 Context-aware provider default (config-driven) · 13 Streaming four-layer safety (defaults; per-provider override) · 14 retired · 15 Export contract · 16-17 retired · 18A Sandwich layout · 18B Provider dot standard (config dotColor) · 19 Cognitive Identity Law · 20 Library schema + import/export symmetry · 21 Storage abstraction · 22 Universal Optional Panel Architecture · 23 Standalone persistence (folder-connect — unconditional localStorage + additive mirror) · 23B Folder-connect robustness (reload persistence, permission re-verify, engine-tagging + untagged shape guard, drift reconciliation, delete propagation, backfill-on-connect) · 24 Asymmetric Panel Specificity Law (see 01B) · 25 Model delegation (Model Core)

**Revision 2026-10-03:** 01, 06, 07, 12, 13, 18B, 21 patched and 25 added to align with model-config-contract (Model Core) and model.json; no constraint renumbered.

**Update protocol:** read in full → add/modify/remove → confirm before/after → new constraints get next sequential number, never renumber existing → emit updated file for reinstall.
