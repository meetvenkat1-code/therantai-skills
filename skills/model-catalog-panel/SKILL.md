---
name: model-catalog-panel
description: "Optional model-picker layer for Hybrid HTML Engines, built on the Model Core (model- config-contract v2). Lanes mode: pin models as exact parallel lanes, one input through many models side by side. Panel mode: each panel, stage or role owns one model, chosen from the config defaults plus a per-panel Recent history, with a reassign popover per panel. Both modes consume the Core API (config, keys, hardened callModel) and never re- implement it. Defaults are the config's defaultLanes; everything else arrives through a live /models catalog (tiers, search, /regex/; tags, Synth Picks and price sort as opt-in modules). Exactly one control chooses the model. Invoke with /catalog lanes or /catalog panel (/catalog fanout aliases lanes), or say \"add live model catalog\", \"pin models as lanes\", \"per-panel model picker\". A bare /catalog asks one gate question. Skip for engines that only need the default models.\n"
---

# Model Catalog Panel v3.2

`model-config-contract` (the **Model Core**) answers "which providers exist, what are the default models, where do keys live, and how is a call made". This skill is the **optional layer above it**: it answers "which models does each provider offer *right now*, and how does the user put them to work". How they put them to work is the **mode**. An engine that only needs the default models (Groq `gpt-oss-120b` and the OpenRouter free router) does not invoke this skill at all.

```
Invocation : /catalog lanes | /catalog panel | /catalog fanout (alias of lanes) | "invoke model catalog panel"
Requires   : /hybrid-engine + /ui-contract + /model-config (Model Core v2)
Priority   : model-config-contract owns provider identity, config, keys and the call layer.
             This file owns only the picker surface and the lane / panel state.
             (v2.0 said this file wins for standalone engines; that clause is retired, because those rules now live in the core.)
```

## SKILL METADATA

Kept in the body rather than the front matter, so the upload validator sees only `name` and `description`.

```yaml
scope: add-on
invokable: true
triggers: ["/catalog", "/catalog lanes", "/catalog fanout", "/catalog panel", "invoke model catalog panel", "add live model catalog", "pin models as lanes", "fan-out lanes", "per-panel model picker", "each stage has its own model"]
requires: [hybrid-engine-contract, ui-contract, model-config-contract]
phase: Build
version: "3.2"
reference_builds:
  - "osho-refraction-standalone.html (Lanes, single path, left system-prompt panel, right drawer with Corpus)"
  - "sequential-pipeline.html (Panel)"
  - "capsule-relay-loop-engine-v2.html (Panel, after retrofit onto the Model Core)"
  - "prompt-generator-engine-v2.html (Lanes, matrix variant: 3 presets x lanes, curated Run kept)"
lineage: "Triangulator live-fetch gear drawer -> Capsule Tree v7 (v1.0) -> Sequential Pipeline (v2.0, standalone-first, two modes) -> Osho Refraction Engine (v3.0, selection layer on the Model Core, single-path Lanes) -> Prompt Generation Engine (v3.1, matrix variant, reference code from a tested retrofit) -> v3.2 (catalog GET hardening: minimal headers, instant tab switch, in-flight guard; Panel plumbing completed)"
```

## WHAT CHANGED IN v3 (the delta from v2.0)

1. **Selection only.** The config layer, key store and call layer are gone from this file; the engine consumes the Core API (`usableProviders`, `defaultLanes`, `getKey`, `headersFor`, `callModel`, `resolveModelId`).
2. **Single path is the default form of Lanes.** One Run button runs the ticked lanes; a lane button in the header replaces the provider dropdown; any pre-existing block of provider / endpoint / model fields is deleted. The two-button matrix survives only for engines that already have a second axis of work (A3d).
3. **Defaults are `defaultLanes()`** (two entries today), not the whole `modelChain`. Chain entries beyond the defaults, such as Groq's `gpt-oss-20b`, serve as the core's fallback, and reach a user only through the catalog.
4. **Extras are opt-in modules.** Content tags, Synth Picks and price sort are off unless the brief asks for them.
5. **Lane keys are `providerId::modelId`.** v2 used `provider|model` and `pin|provider|model`; migrate them at boot.
6. **Panel mode's 429 countdown wraps the core's `callModel`** using the `status` and `retryAfter` it puts on errors. There is no second stream reader.
7. **Alias resolution is the core's `resolveModelId`** over `model_aliases` in `model.json`.

## WHAT CHANGED IN v3.1 (from retrofitting the Prompt Generation Engine)

The v3.0 skill described the Lanes drawer and the matrix run in prose only, so the first retrofit had to rewrite them. v3.1 adds, all copy-paste and tested in that retrofit:

1. **Engine plumbing** (`$`, `lsGet`/`lsSet`, `S`, `save`, `toast`, `MAX_LANES`, `MAX_CELLS`) that the other blocks assume, in Section 1a.
2. **Lanes drawer reference code** (catalog fetch, tiers, search, pin rows, lane rows, key rows, `renderConfigUI`) in A5.
3. **The `renderConfigUI` hook is now defined**, with `afterConfigUI` for engines that keep a provider selector.
4. **Matrix dispatch** (`fanOut`, `laneCaller`) in A3d, with the five hooks an engine supplies.

## WHAT CHANGED IN v3.2 (catalog GET hardening, from an external audit that was itself audited)

An outside review reported that the catalog fetch can fail in the browser on OpenRouter once a key is saved. The diagnosis was half right: `headersFor()` builds headers meant for `POST /chat/completions`, and on a cross-origin `GET /models` every non-simple header (attribution headers, `Content-Type`, `Authorization`) forces a CORS `OPTIONS` preflight. Three of the review's patches were vetted; one was adopted as written, one was adopted in a corrected form, one was rejected.

1. **`catalogHeaders(cfg, key)`** (Section 2). A catalog read is a GET of public data and sends the least that works: nothing at all for OpenRouter (its `/models` is public, so even a saved key is not sent), and only the auth header for a keyed provider such as Groq. This replaces the review's "delete `HTTP-Referer` and `X-Title`" patch, which left `Authorization` and `Content-Type` in place, used names (`P()`, `.endpoint`) that do not exist in this skill, and dropped the 401/403 key message and the empty-catalog guard.
2. **Provider tabs switch instantly.** In both modes the click handler renders the new tab first and fetches second, so a failed fetch no longer leaves the old tab showing with the error under the wrong provider (B3 `makePicker`, A5 `renderCatalog`).
3. **In-flight guard** (`inflight[pid]`). Instant tabs make rapid clicks easy; two concurrent fetches of one provider are now impossible.
4. **Panel plumbing made complete.** Panel mode's code used `h()`, `HISTORY_CAP`, `normaliseModels` and `rebuildSelects` that nothing defined, and called `$("#id")` while the Lanes code called `$("id")`, so the two modes could not share one plumbing block. The `$` in Section 1a now accepts both forms, `h` is defined there, and the Panel block under B1 defines the rest and states the shapes of the three engine-owned names (`state`, `ui`, `STAGES`).
5. **Rejected: a boot-time auto-fetch loop in `renderConfigUI`.** It contradicts the banned pattern "never auto-refetch the catalog on load", would fire again when the live config swaps in, and assumed a `#drawerPicker .cat-status` node that Lanes engines do not have. Auto-fetch already happens in `makePicker.show()`, which passes the real status element, so its errors are visible.

## THE LAYER RULE

This skill consumes the Core API. It must not re-implement a config loader, key store, request builder, stream reader or call layer. If the engine needs behaviour the core lacks, the fix is a core change (model-config-contract), never a local copy.

---

## MODE GATE (run before anything else)

The skill cannot see the engine. It reads the invocation and the build brief. Decide the mode from these signals, and never guess.

| The brief says | Mode |
|---|---|
| one input runs through many models side by side; compare models; lanes; fan-out; triangulate; results as parallel columns per model | **A. Lanes** |
| each panel / stage / role / agent owns its own model; pipeline; sequential roles; per-panel model; every panel has a model dropdown | **B. Panel** |
| the engine only needs one answer from the default models | **No picker.** Stay on the Model Core; build nothing from this skill. |
| none of these clearly, or more than one | Ask exactly one question: "Does one input run through many models at once (lanes), does each panel own its own model (panel), or do you just want the default models (no picker)?" Build nothing until answered. |

An engine that genuinely needs both surfaces builds Sections 1 to 3 (the shared layer) once and mounts Mode A for its lane run and Mode B for its per-role runs. This is rare; state it in the build plan when it happens.

| | Mode A: Lanes | Mode B: Panel |
|---|---|---|
| Picking a model means | tick a lane (pin = exact extra lane) | fill that panel's slot |
| Persisted selection | `lanes[]` + `customLanes[]` + `lanesTouched` | `models[]` (one per panel) + `history[][]` (Recent, 5 per panel) + `caps[]` |
| Defaults | `defaultLanes()` listed; only the first ticked until the user touches the list | `defaultLanes()` as the "from config" group; empty slots normalize to the first |
| Concurrency | all lanes in parallel, 220 ms stagger, max 12 | the engine decides (the pipeline reference runs panels strictly in order) |
| Failover | never across lanes (strict mode) | none; a failed panel stops and is re-run by the user |
| Rate limit (429) | the core retries once (1800 ms), then the lane errors | visible countdown, honors the provider's own wait, up to 3 retries |
| Picker surface | header lane button + gear drawer: Lanes, Model catalog, Keys, engine settings | popover on every panel + drawer catalog with 1..N / all buttons |
| Call | `callModel({ provider, model, ... })` per lane | `streamChat` wrapper over strict `callModel` (B5) |

---

## 1. STANDALONE-FIRST DOCTRINE (applies to both modes)

These rules exist because the engines are run standalone, from a file or a host, not inside claude.ai artifacts. Most are now enforced by the Model Core; they are listed so the picker never contradicts them.

1. **Native entries are skipped, never routed.** The shared `model.json` carries one `native: true` entry (Claude). `usableProviders()` leaves it out of a standalone engine, so it appears in no dropdown, lane roster, default, key row or catalog button, and no Anthropic-native request branch is built in the picker.
2. **Defaults are the config's `defaultLanes()`.** Today that is Groq `gpt-oss-120b` and the OpenRouter free router. Nothing in the HTML names a provider or a model. The default ticked or selected model is the first entry.
3. **Config fetch, validation, fallback and the badge belong to the core** (`fetchModelConfig`, `isValidConfig`, `LOCAL_FALLBACK_CONFIG`). The engine renders from the floor first, then upgrades. Header badge: `Config: Live` (success) or `Config: Local Fallback`.
4. **Keys** go through the core's `getKey(name)` / `setKey(name, value)` at `hek_{keyStorageName}`, entered in rows rendered from `providers[]` (`keyLabel`, `keyPlaceholder`, `keyNote`). Engines that stored keys under their own names declare `LEGACY_KEY_SLOTS`. A key goes only to its own provider's endpoints.
5. **`standaloneOnly` is enforced by `callModel`** (it refuses inside claude.ai); the picker shows the provider's `keyNote`.
6. **Trimming and defaults are `model.json` edits, not HTML edits.** A model the account cannot call (404) is removed from the chain in the repo; the default pair is `defaultLanes`; retired slugs are `model_aliases`. Do not hard-code exclusions in the engine.
7. **Id renames migrate once.** If an engine previously stored `openrouter::` ids, rewrite them to the config id (`or-auto::`) at boot; convert v2 lane keys (`provider|model`, `pin|provider|model`) to `providerId::modelId`; move any `state.keys` into `hek_*`.
8. **Single path.** Exactly one control chooses the model. A pre-existing block of provider / endpoint / model fields, or a provider dropdown beside the picker, is deleted in the retrofit, never left alongside it: two paths disagree, and the stale one fails with a model id the catalog never offered. The one exception is the matrix variant (A3d): an engine with a second axis of work keeps its curated Run and provider selector, and the lanes drive only the separate `Fan out (n)` button; the two never share a model field.

### 1a. Glue: Model Core to picker (the only config code a picker engine owns)

```javascript
/* ───────── Glue: Model Core -> picker ───────── */
const CAT_KEY = "myengine.v1:catalog";                       // dedicated cache key, one per engine
const PROVIDERS = {}; let DEFAULT_MODELS = [], configSource = "fallback", uiReady = false;
const keyOf = cfg => getKey(cfg.keyStorageName || cfg.id);    // the core's getKey takes the storage name
const isDefault = v => DEFAULT_MODELS.some(d => d[0] === v);
function applyConfigToPicker(src) {
  configSource = src; Object.keys(PROVIDERS).forEach(k => delete PROVIDERS[k]);
  usableProviders().filter(p => !p.native).forEach(p => { PROVIDERS[p.id] = { id: p.id, label: p.label, url: p.endpoint, cfg: p }; });
  DEFAULT_MODELS = defaultLanes().map(k => { const s = splitKey(k); return [k, PROVIDERS[s.provider].label + " · " + s.model, s.provider]; });
  if (uiReady) renderConfigUI();
}
const defaultModel = () => DEFAULT_MODELS.length ? DEFAULT_MODELS[0][0] : "";
/* boot: the core already holds the floor, so the first paint works with no network; then the live file swaps in */
applyConfigToPicker("fallback");
/* ... build the UI, set uiReady = true, renderConfigUI() ... */
fetchModelConfig(src => applyConfigToPicker(src));
```

`DEFAULT_MODELS` entries are `[providerId::model, label, providerId]`. `applyConfigToPicker` re-renders only after first paint (`uiReady`), so the floor applies instantly and the live config swaps in without a flash of nothing.

**Engine plumbing (both modes).** The Lanes blocks (A1 to A5) and the Panel blocks (B2 to B6) assume these helpers; Panel mode additionally needs the names listed under B1. If the engine already has its own `$`, state object or toast, reuse it; otherwise paste this. The engine's markup needs `<div id="toast"></div>` (fixed, centred, `opacity:0`, `.show{opacity:1}`).

```javascript
/* ───────── Engine plumbing the Lanes blocks assume ───────── */
const $ = id => document.getElementById(String(id).replace(/^#/, ""));   // accepts "id" (Lanes code) and "#id" (Panel code)
const h = (tag, cls, txt) => { const e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; };   // element builder the Panel pickers use
const lsGet = (k, d) => { try { const v = JSON.parse(localStorage.getItem(k)); return v == null ? d : v; } catch (e) { return d; } };
const lsSet = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} };
const MAX_LANES = 12, MAX_CELLS = 12, SETTINGS_KEY = "myengine.v1:settings";
const S = { settings: Object.assign({ lanes: [], customLanes: [], lanesTouched: false }, lsGet(SETTINGS_KEY, {})) };
const save = () => lsSet(SETTINGS_KEY, S.settings);
function toast(m) { const t = $("toast"); t.textContent = m; t.classList.add("show"); clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.remove("show"), 3500); }
```

---

## 2. CATALOG FETCH AND FILTERS (shared)

Which providers are fetchable is decided by config: any non-native provider whose chat `endpoint` ends in `/chat/completions`. A provider added to `model.json` tomorrow gets a Fetch button with zero HTML edits. The models URL is the endpoint with `/chat/completions` replaced by `/models`. **The catalog request does not use `headersFor` as is.** `headersFor` builds the headers a chat POST needs; on a cross-origin `GET /models` they only add a CORS preflight that a provider's edge cache may fail. The request goes through `catalogHeaders` below. Paste this block once, before `fetchCatalog`, in either mode.

```javascript
/* ───────── Catalog GET helpers (shared by Lanes and Panel) ───────── */
/* A catalog read is a GET of public data. Attribution headers belong to POST /chat/completions only; on a GET they,
   and Content-Type, widen the CORS preflight. Send the least that works. */
const catalogHeaders = (cfg, k) => {
  if (!k || /openrouter\.ai/.test(cfg.endpoint)) return {};     // OpenRouter's /models is public: no key, no headers, no preflight
  const h = headersFor(cfg, k), o = {};
  Object.keys(h).forEach(n => { if (/^(authorization|x-api-key)$/i.test(n)) o[n] = h[n]; });   // keyed providers (Groq): auth header only
  return o;
};
const inflight = {};                                             // one catalog fetch per provider at a time
```

**Base set (always built):**
- The response is `{ data: [...] }` for both OpenRouter and Groq. A provider that deviates is out of scope until a format map exists.
- **Auto-fetch rule, keyed on the endpoint, not the name:** when a picker opens for a provider with no cached catalog, auto-fetch only if its endpoint is public (OpenRouter's `/models` needs no key) or a key is already saved. Groq's catalog waits for its key; the no-key 401/403 message must say so.
- Cache at a dedicated key (`CAT_KEY`), loaded at boot, refreshed only by the user (Fetch or refetch). Exclude it from state export.
- Catalog data is untrusted text: render ids, names, descriptions with `textContent` / `title`, never `innerHTML`.
- Tiers: `free` (price 0 or `:free`), `cheap` (< $0.50/M in), `medium` (< $3), `premium`, `n/a` (no price, e.g. Groq). Rows sort by tier then natural id order.
- Search matches id, name and description; `/regex/flags` is supported.
- Row anatomy: model id on its own line (wraps), then a meta line: blue `ctx` tag, orange `$x/M in` or green `FREE`. Cap 150 rows (30 in a popover until the user types), with a "Showing n of m" footer.

**Optional modules (off unless the brief asks; each is independent):**
- `+tags` **Content tags** (Uncensored, Roleplay, Unfiltered Prose) from three sources in order: a curated id list, a creator-namespace map, then a regex fallback. Heuristic matches render with a dashed border and a trailing `?`. Tags are hints, never ratings; the chip tooltip says so. Tag chips combine as OR; search also matches tag labels.
- `+synth` **Synth Picks**, a tab over a curated substring list (`SYNTH_PICKS`). Advisory only; edit as the catalog rotates.
- `+price` **Price sort** cycling tier order, then low to high, then high to low; free and unpriced models stay pinned to the top in both price directions.

The reference code in B3 includes all three modules. Omit the tabs, chips and functions of any module that is not enabled; a lean build (the Osho reference) ships the base set only.

---

## 3. CALL LAYER: OWNED BY THE MODEL CORE

This skill has no call layer of its own. Every model call goes through the core's `callModel`, in **strict mode** (`callModel({ provider, model, ... })`: exactly the chosen model, never a substitute). The hardening catalog models need is already in it:

| Rule | Where it lives |
|---|---|
| System-role fold (a 400 mentioning system, developer or instruction retries once with the system text in the user turn) | `callModel` |
| 404: "model not found, refresh the catalog"; never silently swaps models | `callModel` |
| Fatal statuses 401, 402, 403, 413 stop the call; a wrong key never reads as "all routes failed" | `callModel` |
| Served tag: the `model` on stream chunks is reported to `onText(acc, served)`; show `served: X` when it differs from the requested slug (how `openrouter/free` reveals its routing) | `callModel` + the lane / panel header |
| Reasoning liveness: reasoning deltas count as alive for idle timing | `readStream` |
| Empty reply is an error, with a specific hint when `finish_reason` is `length` | `callModel` |
| Output cap: optional `maxTokens` per call (Mode B's `caps[]`) | `callModel` option |
| 429: one retry after 1800 ms, then an error carrying `status` and `retryAfter` | `callModel`; Mode B adds a countdown on top (B5) |
| Abort | `callModel` option `signal` |

---

## MODE B. PANEL (per-panel model, reference: sequential-pipeline.html)

### B1. What each panel holds

- `models[i]`: the panel's selected model as `providerId::slug`. Empty or unknown ids are normalized to the config default at boot and whenever the config changes (`normaliseModels`).
- `history[i]`: that panel's Recent list, most recent first, no duplicates, `HISTORY_CAP = 5`. Config defaults are never added to history. Existing selections seed the lists on first run.
- `caps[i]`: the panel's max output tokens (0 means no cap).

**Panel plumbing.** The Section 1a helpers (`$`, `h`, `save`, `toast`) plus the block below. `state`, `ui` and `STAGES` are the engine's own, in these shapes: `STAGES = [{ name }, ...]` (one per panel); `state = { models: [], history: [[], ...], caps: [] }`, each array one entry per panel and persisted through `save`; `ui[i] = { sel, pop, picker }`, where `sel` is the panel's `<select>`, `pop` its popover element and `picker` is filled lazily by `togglePop`. `STAGES.length` sets the panel count everywhere: `assign` and the drawer picker's `1..N` / `all` buttons read it instead of assuming four panels.

```javascript
const HISTORY_CAP = 5;
const rebuildSelects = () => ui.forEach((_, i) => buildSelect(i));      // B2
function normaliseModels() {                                            // empty or unknown ids fall back to the config default; call at boot and whenever the config changes
  state.models = state.models.map(v => (v && v.indexOf("::") > 0 && PROVIDERS[splitKey(v).provider]) ? v : defaultModel());
}
```

### B2. The dropdown (no Custom entry)

Groups, in order: one **"{Provider} · from config"** group per provider holding that provider's `defaultLanes()` entries (the floor, two models today); **"Recent on this panel"**; **"More"** containing only "Clear recent list" (shown only when history exists). A chain entry that is not a default (for example Groq's `gpt-oss-20b`) is the core's fallback, not a dropdown row. Anything the catalog can offer arrives through the popover, so there is deliberately no free-text "Custom…" option. Assigning from the catalog also records into history; picking from Recent moves it to the front.

```javascript
const pushHistory = (i, val) => { if (!val || isDefault(val)) return; state.history[i] = [val].concat(state.history[i].filter(x => x !== val)).slice(0, HISTORY_CAP); };
const labelOf = v => { const d = DEFAULT_MODELS.find(x => x[0] === v); if (d) return d[1]; const [pid, ...r] = v.split("::"); return (PROVIDERS[pid] ? PROVIDERS[pid].label : pid) + " · " + r.join("::"); };
function buildSelect(i) {
  const sel = ui[i].sel, cur = state.models[i], grp = l => { const g = document.createElement("optgroup"); g.label = l; sel.appendChild(g); return g; };
  sel.innerHTML = "";
  Object.values(PROVIDERS).forEach(p => { const items = DEFAULT_MODELS.filter(d => d[2] === p.id); if (!items.length) return;
    const g = grp(p.label + " · from config"); items.forEach(([v]) => g.appendChild(new Option(v.split("::").slice(1).join("::"), v))); });
  const rec = state.history[i].filter(v => PROVIDERS[v.split("::")[0]]); if (cur && !isDefault(cur) && !rec.includes(cur)) rec.unshift(cur);
  if (rec.length) { const g2 = grp("Recent on this panel"); rec.forEach(v => g2.appendChild(new Option(labelOf(v), v))); }
  if (state.history[i].length) { const g3 = grp("More"); g3.appendChild(new Option("Clear recent list", "__clear")); }
  sel.value = cur;
}
```

### B3. Pickers (one reusable component, two mounts)

*The reference code below includes every optional module of Section 2 (tags, Synth Picks, price sort); drop the ones the brief did not ask for.* `makePicker(root, { title, cap, onRow })` renders: title `{title} · {Provider} live (n)`, provider buttons (Fetch / count / refetch), tabs **Full list** and **★ Synth Picks**, search, tier chips, tag chips, the price-sort chip, then rows. The mount decides what a row does:

- **Per-panel popover** (`Live models ▾` button in each panel header): opens on that panel's current provider, auto-fetches per the Section 2 rule, row click assigns that panel and closes the popover; the current model's row carries an accent bar. One popover open at a time; outside click closes it; clicks inside the popover must `stopPropagation` so chip re-renders do not close it.
- **Drawer picker**: rows carry `1..N` buttons to assign one panel and `all` to assign every panel.

```javascript
/* ───────── Live model catalog + reusable picker (drawer + one popover per stage) ───────── */
let catalog = {}; try { catalog = JSON.parse(localStorage.getItem(CAT_KEY)) || {}; } catch (e) {}
if (catalog.openrouter && !catalog["or-auto"]) { catalog["or-auto"] = catalog.openrouter; delete catalog.openrouter; }
const pickers = [], refreshPickers = () => pickers.forEach(p => p.render());
const modelsUrl = pid => PROVIDERS[pid].url.replace(/\/chat\/completions$/, "/models");
function slimModel(m) {
  if (!m || !m.id) return null;
  if (/whisper|tts|orpheus|embed|guard|moderation|playai/i.test(m.id)) return null;
  const o = m.architecture && m.architecture.output_modalities; if (o && o.indexOf("text") < 0) return null;
  let pIn = null; if (m.pricing && m.pricing.prompt != null) { pIn = parseFloat(m.pricing.prompt) * 1e6; if (isNaN(pIn) || pIn < 0) pIn = null; }
  if (pIn === null && /:free$/.test(m.id)) pIn = 0;
  return { id: m.id, name: m.name || "", ctx: m.context_length || m.context_window || 0, pIn, desc: String(m.description || m.owned_by || "").slice(0, 240) };
}
const tierOf = m => m.pIn === null ? "n/a" : m.pIn === 0 ? "free" : m.pIn < 0.5 ? "cheap" : m.pIn < 3 ? "medium" : "premium";
const TIER_ORDER = { free: 0, cheap: 1, medium: 2, premium: 3, "n/a": 4 };
/* Curated long-context synthesizer shortlist — advisory only, edit as the catalog rotates. */
const SYNTH_PICKS = ["deepseek-v4", "gemini-2.5-flash", "llama-4-maverick", "qwen3-max", "gpt-oss-120b", "gemini-2.5-pro", "gemini-3", "claude-haiku", "gpt-5-mini", "claude-sonnet", "claude-opus", "gpt-5", "grok-4"];
const isPick = id => { id = id.toLowerCase(); return SYNTH_PICKS.some(f => id.includes(f)); };
/* Content tags: curated id list → creator namespace → regex fallback (heuristic, shown dashed with "?"). Hints, not ratings. */
const CONTENT_TAGS = {
  uncensored: { label: "Uncensored", color: "#f472b6", title: "Creator describes removing/loosening safety alignment — not an authoritative rating",
    ids: ["cognitivecomputations/dolphin-mistral-24b-venice-edition", "cognitivecomputations/dolphin-mistral-24b-venice-edition:free", "cognitivecomputations/dolphin3.0-mistral-24b", "cognitivecomputations/dolphin3.0-r1-mistral-24b", "anthracite-org/magnum-v4-72b", "thedrummer/cydonia-24b-v4.1", "neversleep/noromaid-20b", "neversleep/llama-3-lumimaid-70b", "neversleep/llama-3-lumimaid-8b", "neversleep/llama-3.1-lumimaid-70b", "neversleep/llama-3.1-lumimaid-8b"],
    pattern: /(uncensored|unaligned|abliterated|venice|dolphin|no-guardrails)/i },
  roleplay: { label: "Roleplay", color: "#a78bfa", title: "Fine-tuned for character cards, persona consistency and multi-turn narrative — not an authoritative rating",
    ids: ["sao10k/l3.3-euryale-70b", "sao10k/l3.1-euryale-70b", "sao10k/l3-euryale-70b", "sao10k/l3-lunaris-8b", "sao10k/l3-stheno-8b", "gryphe/mythomax-l2-13b", "neversleep/noromaid-20b", "neversleep/llama-3-lumimaid-70b", "neversleep/llama-3-lumimaid-8b", "neversleep/llama-3.1-lumimaid-70b", "neversleep/llama-3.1-lumimaid-8b", "thedrummer/cydonia-24b-v4.1", "thedrummer/valkyrie-49b-v1"],
    pattern: /(roleplay|\bRP\b|eroleplay|\bERP\b|character-card|persona|stheno|euryale|mythomax|lumimaid|noromaid)/i },
  unfilteredProse: { label: "Unfiltered Prose", color: "#fb923c", title: "Tuned for raw creative-writing fluency, without roleplay/persona machinery — not an authoritative rating",
    ids: ["thedrummer/unslopnemo-12b", "thedrummer/rocinante-12b", "thedrummer/skyfall-36b-v2"],
    pattern: /(unslop|prose|creative-writing|skyfall|rocinante)/i }
};
const TAG_KEYS = Object.keys(CONTENT_TAGS); TAG_KEYS.forEach(k => CONTENT_TAGS[k].idSet = new Set(CONTENT_TAGS[k].ids));
const NS_TAGS = { neversleep: ["uncensored", "roleplay"], sao10k: ["roleplay"], cognitivecomputations: ["uncensored"], thedrummer: ["unfilteredProse", "roleplay"], gryphe: ["roleplay"] };
function contentTags(m) {
  const ns = m.id.includes("/") ? m.id.slice(0, m.id.indexOf("/")) : "", hay = [m.id, m.name, m.desc].join(" "), conf = {};
  TAG_KEYS.forEach(k => { const t = CONTENT_TAGS[k];
    if (t.idSet.has(m.id)) conf[k] = "curated"; else if (NS_TAGS[ns] && NS_TAGS[ns].includes(k)) conf[k] = "namespace"; else if (t.pattern.test(hay)) conf[k] = "heuristic"; });
  return { tags: Object.keys(conf), conf };
}
function modelMatch(m, q) {
  if (!q) return true; const hay = [m.id, m.name, m.desc, contentTags(m).tags.map(k => CONTENT_TAGS[k].label).join(" ")], rx = /^\/(.+)\/([a-z]*)$/i.exec(q.trim());
  if (rx) { let re; try { re = new RegExp(rx[1], rx[2]); } catch (e) { return false; } return hay.some(x => re.test(x)); }
  q = q.toLowerCase(); return hay.some(x => x.toLowerCase().includes(q));
}
const sortModels = (ms, mode) => ms.slice().sort((a, b) => {
  if (mode === "tier") return TIER_ORDER[tierOf(a)] - TIER_ORDER[tierOf(b)] || a.id.localeCompare(b.id, undefined, { numeric: true });
  const fa = !a.pIn, fb = !b.pIn; if (fa !== fb) return fa ? -1 : 1;     // free / unpriced pinned to the top either direction
  if (a.pIn !== b.pIn) return mode === "desc" ? b.pIn - a.pIn : a.pIn - b.pIn;
  return a.id.localeCompare(b.id);
});
async function fetchCatalog(pid, st) {
  if (inflight[pid]) return; inflight[pid] = true;               // catalogHeaders + inflight: see Section 2
  const k = keyOf(PROVIDERS[pid].cfg); st.textContent = "Fetching " + PROVIDERS[pid].label + " models…";
  try {
    const res = await fetch(modelsUrl(pid), { headers: catalogHeaders(PROVIDERS[pid].cfg, k) });
    if (!res.ok) { let d = String(res.status); try { const b = await res.json(); if (b.error && b.error.message) d = b.error.message; } catch (e) {}
      throw new Error((res.status === 401 || res.status === 403) && !k ? "this provider needs a key — save one in ⚙ first" : d); }
    const j = await res.json(), arr = (j.data || []).map(slimModel).filter(Boolean);
    if (!arr.length) throw new Error("no chat models returned");
    catalog[pid] = { ts: Date.now(), models: arr };
    try { localStorage.setItem(CAT_KEY, JSON.stringify(catalog)); } catch (e) {}
    refreshPickers();
  } catch (e) { st.textContent = PROVIDERS[pid].label + " catalog failed — " + String(e.message || e); }
  finally { delete inflight[pid]; }
}
function assign(k, val) {
  const ks = k === "all" ? STAGES.map((_, i) => i) : [k]; ks.forEach(x => state.models[x] = val);
  ks.forEach(x => pushHistory(x, val));
  save(); rebuildSelects(); refreshPickers();
  toast((k === "all" ? "All stages" : STAGES[k].name) + " → " + labelOf(val));
}
/* makePicker(root, {title, cap, onRow(actionsEl, model, pid, rowEl)}) — Full list / ★ Synth Picks, search, tier + content-tag chips, price sort */
function makePicker(root, o) {
  const s = { pid: PROVIDERS["or-auto"] ? "or-auto" : Object.keys(PROVIDERS)[0], tab: "full", tier: "all", tags: new Set(), sort: "tier", q: "" };
  const title = h("div", "pk-title"), provs = h("div", "pk-row"), tabs = h("div", "pk-row"), search = h("input", "pk-search"),
    chips = h("div", "pk-chips"), status = h("div", "cat-status"), rows = h("div", "pk-rows");
  search.placeholder = "Search or /regex/ — id, name, tag, description…";
  root.append(title, provs, tabs, search, chips, status, rows);
  root.addEventListener("click", e => e.stopPropagation());
  search.oninput = () => { s.q = search.value; list(); };
  const chip = (txt, on, fn, color, tip) => { const b = h("button", "tchip" + (on ? " active" : ""), txt); if (color && on) { b.style.borderColor = color; b.style.color = color; } if (tip) b.title = tip; b.onclick = fn; return b; };
  function head() {
    if (!PROVIDERS[s.pid]) s.pid = Object.keys(PROVIDERS)[0];
    const c = catalog[s.pid]; title.textContent = `${o.title} · ${PROVIDERS[s.pid].label} live` + (c ? ` (${c.models.length})` : "");
    provs.innerHTML = ""; tabs.innerHTML = ""; chips.innerHTML = "";
    Object.keys(PROVIDERS).forEach(pid => { const cc = catalog[pid], b = h("button", s.pid === pid ? "primary" : "", cc ? `${PROVIDERS[pid].label} (${cc.models.length})` : "Fetch " + PROVIDERS[pid].label);
      b.onclick = () => { const was = s.pid === pid; s.pid = pid; s.tier = "all"; render();     // switch the tab first, so a failed fetch never leaves the old tab showing
        if (!catalog[pid] || was) fetchCatalog(pid, status); }; provs.appendChild(b); });      // fetch if uncached; clicking the active tab refetches
    if (catalog[s.pid]) { const r = h("button", "", "↻"); r.title = "Refetch " + PROVIDERS[s.pid].label; r.onclick = () => fetchCatalog(s.pid, status); provs.appendChild(r); }
    [["full", "Full list"], ["picks", "★ Synth Picks"]].forEach(([k, l]) => { const b = h("button", "tab" + (s.tab === k ? " on" : ""), l); b.onclick = () => { s.tab = k; head(); list(); }; tabs.appendChild(b); });
    const r1 = h("div", "pk-row"), r2 = h("div", "pk-row"), r3 = h("div", "pk-row");
    ["all", "free", "cheap", "medium", "premium"].forEach(t => r1.appendChild(chip(t[0].toUpperCase() + t.slice(1), s.tier === t, () => { s.tier = t; head(); list(); })));
    TAG_KEYS.forEach(k => { const t = CONTENT_TAGS[k]; r2.appendChild(chip(t.label, s.tags.has(k), () => { s.tags.has(k) ? s.tags.delete(k) : s.tags.add(k); head(); list(); }, t.color, t.title)); });
    const sb = chip(s.sort === "asc" ? "↑ Price: low→high" : s.sort === "desc" ? "↓ Price: high→low" : "⇅ Sort by price", s.sort !== "tier", () => { s.sort = s.sort === "tier" ? "asc" : s.sort === "asc" ? "desc" : "tier"; head(); list(); });
    sb.style.flex = "1"; r3.appendChild(sb); chips.append(r1, r2, r3);
    search.style.display = catalog[s.pid] ? "block" : "none";
  }
  function list() {
    const c = catalog[s.pid]; rows.innerHTML = "";
    if (!c) { status.textContent = "Fetch this provider's live model list to browse it."; rows.style.display = "none"; return; }
    rows.style.display = "block";
    let ms = c.models; if (s.tab === "picks") ms = ms.filter(m => isPick(m.id));
    if (s.tier !== "all") ms = ms.filter(m => tierOf(m) === s.tier);
    if (s.tags.size) ms = ms.filter(m => contentTags(m).tags.some(t => s.tags.has(t)));
    const q = s.q.trim(); if (q) ms = ms.filter(m => modelMatch(m, q));
    ms = sortModels(ms, s.sort); status.textContent = `${ms.length} shown · fetched ${new Date(c.ts).toLocaleTimeString()}`;
    if (!ms.length) { rows.appendChild(h("div", "mfoot", s.tab === "picks" ? "No curated picks match this filter — try Full list or another tier." : "No models match.")); return; }
    const cap = q ? 150 : o.cap;
    ms.slice(0, cap).forEach(m => {
      const row = h("div", "mrow"), id = h("span", "mid", m.id), meta = h("div", "mmeta"); id.title = (m.name ? m.name + " — " : "") + m.desc; row.appendChild(id);
      if (m.ctx) meta.appendChild(h("span", "mtag ctx", (m.ctx >= 1e6 ? (m.ctx / 1e6).toFixed(1) + "M" : Math.round(m.ctx / 1000) + "K") + " ctx"));
      if (m.pIn === 0) meta.appendChild(h("span", "mtag free", "FREE")); else if (m.pIn != null) meta.appendChild(h("span", "mtag price", "$" + m.pIn.toFixed(2) + "/M in"));
      const ct = contentTags(m); ct.tags.forEach(k => { const t = CONTENT_TAGS[k], hz = ct.conf[k] === "heuristic", b = h("span", "mtag", t.label.toUpperCase() + (hz ? " ?" : ""));
        b.style.color = t.color; b.style.borderColor = t.color + "66"; if (hz) b.style.borderStyle = "dashed"; b.title = t.title + " (" + ct.conf[k] + " match)"; meta.appendChild(b); });
      row.appendChild(meta); o.onRow(meta, m, s.pid, row); rows.appendChild(row);
    });
    if (ms.length > cap) rows.appendChild(h("div", "mfoot", `Showing ${cap} of ${ms.length} — search or narrow with a chip.`));
  }
  function render() { head(); list(); }
  const api = { render, show(pid) { if (!PROVIDERS[pid]) pid = Object.keys(PROVIDERS)[0]; s.pid = pid; render(); const P = PROVIDERS[pid]; if (P && !catalog[pid] && (/openrouter\.ai/.test(P.url) || keyOf(P.cfg))) fetchCatalog(pid, status); } };
  pickers.push(api); render(); return api;
}
/* drawer picker: 1–4 / all buttons assign to stages */
makePicker($("#drawerPicker"), { title: "Catalog", cap: 150, onRow(meta, m, pid) {
  const val = pid + "::" + m.id;
  STAGES.map((_, i) => i).concat("all").forEach(k => { const b = h("button", "sb" + (k !== "all" && state.models[k] === val ? " on" : ""), k === "all" ? "all" : String(k + 1));
    b.title = k === "all" ? "Use for all " + STAGES.length + " stages" : "Use for stage " + (k + 1) + " (" + STAGES[k].name + ")"; b.onclick = () => assign(k, val); meta.appendChild(b); });
} });
/* per-stage popover: click a row to reassign that stage */
function togglePop(i) {
  const u = ui[i], was = u.pop.classList.contains("open"); ui.forEach(x => x.pop.classList.remove("open")); if (was) return;
  if (!u.picker) u.picker = makePicker(u.pop, { title: "Reassign", cap: 30, onRow(meta, m, pid, row) {
    const val = pid + "::" + m.id; row.classList.toggle("cur", state.models[i] === val);
    row.onclick = () => { assign(i, val); u.pop.classList.remove("open"); };
  } });
  u.picker.show(state.models[i].split("::")[0]); u.pop.classList.add("open");
  const s = u.pop.querySelector(".pk-search"); if (s && s.style.display !== "none") s.focus();
}
document.addEventListener("click", () => ui.forEach(x => x.pop.classList.remove("open")));
```

### B4. Token cap (one number, two jobs)

Each panel header has a `max tok` field (number, step 256, 0 = no cap, persisted). Defaults scale with the role: generous enough that reasoning models do not spend the whole cap thinking (reference: 2048 / 1536 / 2048 / 2048 for four stages). It does both of these:

1. Sent as `max_tokens` (a hard ceiling that cannot be exceeded).
2. Appends a soft target to the system prompt at run time, `Length: stay within roughly {round(cap * 0.5)} words so the answer finishes inside its {cap}-token budget`, so the model finishes naturally inside the cap instead of being cut mid-sentence.

If the core's result has `cut: true` (`finish_reason` was `length`), flag the panel "cut at token cap" (warning color) and still pass the text on; the user raises the number and re-runs. Where outputs chain into later calls, capping the earliest panels has the most leverage because everything downstream inherits their size.

### B5. Rate-limit patience (a wrapper over the core's strict `callModel`)

There is no second stream reader. `streamChat` is a thin wrapper over `callModel` in strict mode that adds what a sequential pipeline needs: a visible 429 countdown that honours the provider's own wait, abort support, and the `onDelta` / `onStatus` / `onServed` / `onFinish` callbacks the panel UI already uses. The core retries a 429 once itself; if the call still fails it throws an error carrying `status` and `retryAfter` (seconds, from the `retry-after` header or Groq's "try again in 26.6s" text). The wrapper counts down and calls again, up to 3 times; a wait over 90 seconds is treated as a daily cap and surfaced as an error. Rate limits on Groq are per model per minute and requests grow as context grows, so spreading panels across different models also helps. Call sites that used to pass `messages: [{role:"system"...},{role:"user"...}]` now pass `system` and `user` strings.

```javascript
/* ───────── Panel streaming wrapper over the Model Core ───────── */
async function streamChat({ model, system, user, signal, onDelta, onStatus, onServed, maxTokens, onFinish }) {
  const s = splitKey(model);
  for (let attempt = 0; ; attempt++) {
    try {
      const r = await callModel({ provider: s.provider, model: s.model, system, user, signal,
        maxTokens: maxTokens > 0 ? maxTokens : undefined,
        onText: (acc, served) => { onDelta(acc); if (served && served !== s.model && onServed) onServed(served); } });
      if (onFinish) onFinish(r.cut ? "length" : "stop");
      return r.text;
    } catch (e) {
      if (e.status === 429 && attempt < 3) {
        const w = e.retryAfter || 8;
        if (w > 90) throw new Error(`HTTP 429 — the provider asks for a ${Math.round(w)}s wait (likely a daily cap). ${e.message}`);
        for (let sec = Math.ceil(w) + 1; sec > 0; sec--) {
          onStatus(`Rate limit · retry in ${sec}s`); await sleep(1000);
          if (signal && signal.aborted) { const a = new Error("Aborted"); a.name = "AbortError"; throw a; }
        }
        onStatus("Streaming"); continue;
      }
      throw e;
    }
  }
}
```

### B6. Layout (hybrid-engine context)

Right gear drawer: Model catalog (drawer picker), then Keys (rows from config; Save writes each row with `setKey(p.keyStorageName || p.id, value)`), then any engine-specific settings as one more titled section. Left drawer: the editable system prompts, one per role, saved as you type, with a note that the cap appends a length line at run time. Header: `Config: Live / Local Fallback` badge and a gear button; no model control in the header (per-panel chips own the model). Keys UI reference:

```javascript
function renderKeyRows() {
  const box = $("#keyRows"); box.innerHTML = "";
  Object.values(PROVIDERS).forEach(P => { const p = P.cfg;
    if (!p.requiresKey) { box.appendChild(h("div", "cat-status", p.label + " — no key needed")); return; }
    const inp = h("input"); inp.type = "password"; inp.autocomplete = "off"; inp.placeholder = p.keyPlaceholder || ""; inp.dataset.pid = p.id; inp.value = keyOf(p);
    box.append(h("div", "lbl", p.keyLabel || p.label + " API key"), inp); if (p.keyNote) box.appendChild(h("div", "cat-status", p.keyNote)); });
}
function renderBadge() { const b = $("#cfgBadge"); b.textContent = configSource === "live" ? "Config: Live" : configSource === "fallback" ? "Config: Local Fallback" : "Config: loading…";
  b.className = "status" + (configSource === "live" ? " done" : ""); b.title = configSource === "live" ? "Providers and default models loaded from model.json" : configSource === "fallback" ? "model.json unreachable or malformed — using the built-in floor" : "Fetching model.json…"; }
function renderConfigUI() { normaliseModels(); save(); rebuildSelects(); refreshPickers(); renderKeyRows(); renderBadge(); }
```

---

---

## MODE A. LANES (reference: osho-refraction-standalone.html; earlier fan-out reference: capsule-tree-engine-v7.html)

Lanes engines run one input through many models at once. Everything in Sections 1 to 3 applies; this section adds lanes, pins and the single-path run. Native is not a lane (Section 1.1). `isArtifact` is already defined by the core.

### A1. Lanes

A **lane** is one (provider, model) pair that runs in the lane run. There are two kinds: **default lanes** (the config's `defaultLanes()`, two today) and **pinned lanes** (exactly the model the user chose from the catalog).

```javascript
function laneList() {
  var seen = {}, out = [];
  function add(key, pinned) { var s = splitKey(key); if (seen[key] || !PROVIDERS[s.provider]) return; seen[key] = 1; out.push({ key: key, pid: s.provider, m: s.model, pinned: pinned }); }
  defaultLanes().forEach(function (k) { add(k, false); });                      // the floor
  (S.settings.customLanes || []).forEach(function (c) { add(c.key, true); });   // pinned: exactly the model chosen, never a fallback
  return out;
}
function activeKeys() {
  var all = laneList().map(function (l) { return l.key; });
  if (!S.settings.lanesTouched) { var d = defaultLanes()[0]; return d && all.indexOf(d) > -1 ? [d] : []; }   // untouched: only the first default is ticked
  return S.settings.lanes.filter(function (k) { return all.indexOf(k) > -1; });
}
function setLane(key, on) {
  var cur = activeKeys().slice(), i = cur.indexOf(key);
  if (on && i < 0) { if (cur.length >= MAX_LANES) { toast('Max ' + MAX_LANES + ' lanes — deselect one first'); return false; } cur.push(key); }
  else if (!on && i > -1) cur.splice(i, 1);
  S.settings.lanes = cur; S.settings.lanesTouched = true; save(); return true;
}
```

**`modelChain` is no longer a lane roster.** In v2.0 every chain entry became a lane. Now the lanes are `defaultLanes()` plus pins; a chain entry beyond the defaults (Groq's `gpt-oss-20b`) is the core's fallback and shows up only if the user pins it from the catalog.

**Lane honesty law (non-negotiable).** A lane's label must be the truth about who answered.
1. Every lane calls `callModel` in strict mode: exactly the requested model, no `hardFallback`, no silent substitution by another model or provider.
2. Capture the model that actually served the reply (`served`, from the stream) and show it as a `served: X` tag when it differs from the requested id (this is how `openrouter/free` reveals what it routed to).
3. A lane that fails shows its own error in its own column; it never takes another lane's place.

**Default lane selection:** until the user has touched the lane list (`S.settings.lanesTouched`, set by any tick, untick, pin or unpin and restored from storage) only the first default is ticked, so a fresh engine behaves as a single voice and needs one key. After the first touch an empty selection stays empty (the run then toasts "Select lanes in settings"); never silently re-tick lanes the user cleared.

Limits: `MAX_LANES = 12`; toast "Max 12 lanes — deselect one first" when exceeded. Show `n of m lanes active (max 12)` and append " · large fan-outs can hit provider rate limits" when more than 6 are active.

Pin key format: `providerId::modelId` (the same `splitKey` format as `defaultLanes`).

```javascript
function togglePin(pid, m, cb) {
  var key = pid + '::' + m.id, cl = S.settings.customLanes, i = cl.map(function (c) { return c.key; }).indexOf(key);
  if (cb.checked) {
    if (!setLane(key, true)) { cb.checked = false; return; }                      // pinning also activates; the max-12 toast comes from setLane
    if (i < 0 && !laneList().some(function (l) { return l.key === key; })) cl.push({ key: key, provider: pid, model: m.id });
  } else { setLane(key, false); if (i > -1) cl.splice(i, 1); }
  save(); renderLanes(); cb.closest('.mrow').classList.toggle('pinned', cb.checked);
}
```

`ensureLanes()` (called by every render) drops lane keys that no longer exist in `laneList()` (provider removed from config, pin unpinned) and refreshes the header lane button: `Provider · model` for one lane, `n lanes` for several, with the dot of the first active lane's provider (`dotColor`) inside it. Clicking the lane button opens the drawer.

---

### A2. The single-path run

One Run button runs every ticked lane. There is no second "Fan out" button and no provider dropdown. With one lane ticked the output is one full-width voice; with several it is one column per lane (`grid`, `auto-fit`, `minmax(300px, 1fr)`), each with its own copy button and a header of `Provider · model` (plus `→ served: X` when it differs).

---

### A3. Dispatch (strict `callModel` per lane)

```javascript
async function dispatch() {                                     // single path: the one Run button runs every ticked lane
  var lanes = laneList().filter(function (l) { return activeKeys().indexOf(l.key) > -1; });
  if (!lanes.length) return toast('Select lanes in settings');
  resolveCustom(lanes);                                         // A4, before any request
  await Promise.all(lanes.map(function (l, i) { return sleep(i * 220).then(function () { return runLane(l, i); }); }));   // parallel, staggered start softens rate limits
}
async function runLane(l, idx) {
  var rec = recordFor(l, idx);                                  // the engine's own response record: provider, requested model, served
  try {
    var r = await callModel({ provider: l.pid, model: l.m, system: SYSTEM_BODY, user: USER_TEXT,
      onText: function (acc, served) { rec.text = acc; rec.status = 'streaming'; if (served && served !== l.m) rec.served = served; paint(rec); } });
    rec.status = 'done'; if (r.cut) rec.cut = true; paint(rec);
  } catch (e) { rec.status = 'error'; rec.text = String(e.message || e); paint(rec); }
}
```
(`recordFor`, `paint`, `SYSTEM_BODY`, `USER_TEXT` are the engine's own response record, painter and payload; wire them to the engine's existing names.) An engine that retrieves context first (a RAG engine) retrieves **once**, before `dispatch`, and passes the same grounded prompt to every lane.

---

### A3d. Matrix variant: a second dimension (lens x model)

Some engines already have a second axis of work: lenses, prompts, personas, stages. Then the fan-out is a matrix, one **cell** per (unit, lane), and these rules apply on top of A3c (reference build: system-prompt-slot-machine-v2).

- This is the one case that keeps two buttons: the engine's existing single-run path stays untouched (curated `callModel`, provider selector retained because the engine already has a second axis), and a separate `Fan out (n)` button runs the selected unit(s) across the ticked lanes. Do not overload Run.
- Cells = units x lanes, hard-capped (`MAX_CELLS = 12`). Over the cap: toast "N lenses x M lanes = K runs, max 12" and run nothing.
- Lanes run in parallel (220 ms stagger). **Within one lane the units run in order**, which honors any existing "compare is sequential" rule and keeps per-provider concurrency at one.
- Columns are grouped by unit, then lane. Header: unit name, then the lane label (`Provider . model`) with a `-> served: X` suffix when the served model differs.
- Each finished cell is saved as its own response record carrying `provider`, `model` (requested) and `served` (only when different). The saved list shows them.
- Single Run and the existing compare path also record the model that answered (`callModel` returns `model` and `served`).

**Reference code: matrix dispatch.** The engine supplies five hooks; the rest is verbatim.

- `getInput()` returns the text to run (empty means do nothing).
- `getUnits()` returns the units for this run, `[{ key, label, sub }]` (here: the three presets, `sub` being the coordinates).
- `buildCell(grid, cellKey, label, sub)` appends one result cell to `grid` and returns it (reuse the engine's own card builder).
- `runUnit(cellKey, unit, call, input)` runs one unit into its cell. `call(system, user, onPartial)` has the same shape as the engine's own model call but is bound to one lane, so the unit's code is identical for Run and Fan out. It resolves to the final text.
- `markServed(cellKey, served)` shows the `→ served: X` suffix in the cell header.

```javascript
/* ───────── Matrix dispatch: cells = units x lanes ───────── */
function laneCaller(l, cellKey) {                                // strict callModel bound to one lane
  return (system, user, onPartial) => callModel({ provider: l.pid, model: l.m, system, user,
    onText: (acc, served) => { onPartial(acc); if (served && served !== l.m) markServed(cellKey, served); } }).then(r => r.text);
}
async function fanOut() {
  const input = getInput(); if (!input) return;
  const lanes = laneList().filter(l => activeKeys().includes(l.key)); if (!lanes.length) return toast("Select lanes in settings");
  const units = getUnits(), cells = units.length * lanes.length;
  if (cells > MAX_CELLS) return toast(units.length + " units × " + lanes.length + " lanes = " + cells + " runs, max " + MAX_CELLS);
  resolveCustom(lanes);                                          // A4, before any request
  const out = $("fanOut"), fb = $("fanBtn"); out.innerHTML = ""; fb.disabled = true;
  const keyOf2 = (u, li) => "fan-" + u.key + "-" + li;
  units.forEach(u => {                                           // columns grouped by unit, then lane
    const g = document.createElement("div"); g.className = "fan-group"; const h = document.createElement("div"); h.className = "fan-h"; h.textContent = u.label; g.appendChild(h);
    const grid = document.createElement("div"); grid.className = "cards-grid"; g.appendChild(grid); out.appendChild(g);
    lanes.forEach((l, li) => buildCell(grid, keyOf2(u, li), laneLabel(l), u.sub));
  });
  await Promise.allSettled(lanes.map((l, li) => sleep(li * 220).then(async () => {        // lanes in parallel, staggered; within a lane the units run in order
    for (const u of units) { const k = keyOf2(u, li); await runUnit(k, u, laneCaller(l, k), input); }
  })));
  fb.disabled = false; renderLanes();
}
$("fanBtn").addEventListener("click", fanOut);
```


---

---

### A4. Alias / slug-rot resolution

Providers rename and retire slugs. A pinned id that vanishes from a fresh catalog is remapped to its closest live successor, and the user is told. The mechanism is the core's `resolveModelId(id, liveIds)`, fed by `model_aliases` in `model.json` (the fleet-wide list) plus the core's built-in aliases and a version-aware fuzzy match; this skill only decides when to run it.

```javascript
function resolveCustom(lanes) {
  var moved = [];
  lanes.forEach(function (l) {
    if (!l.pinned || !catalog[l.pid]) return;                                    // only against a catalog the user actually fetched
    var r = resolveModelId(l.m, catalog[l.pid].models.map(function (m) { return m.id; }));
    if (r.status === 'alias' || r.status === 'fuzzy') { moved.push(l.m.split('/').pop() + ' → ' + r.id.split('/').pop()); l.m = r.id; }
  });
  if (moved.length) toast('Model id updated: ' + moved.join(', '));
}
```
Rules: resolution only runs against a catalog the user has actually fetched (no catalog, no remap). Never remap across providers. `unresolved` is left as-is and will surface as a 404 with the "refresh the catalog" hint.

---

### A5. Drawer

Section order inside the right gear drawer: **Lanes**, **Model catalog**, **Keys** (rows from config, plus Clear), then any **engine-specific settings** (for example Corpus) as one more titled section. Width 400px (92% on phones); this is the one ui-contract width exception. Lane rows: checkbox, provider dot (`dotColor`), label `Provider · modelId`; pinned lanes are prefixed `★ ` and carry a `×` that unpins (`preventDefault` + `stopPropagation`). The catalog uses the Section 2 filters; add a **Pinned** tier chip showing the count of pins, and a pin checkbox per row (`togglePin`). Use the class names `.tchip` and `.mtag` because `.chip`, `.tag` and `.pin` are commonly taken by the host engine. Boot order: apply the floor (`applyConfigToPicker('fallback')`), render the UI, load the catalog cache, `ensureLanes()`, then `fetchModelConfig`; lane defaults recompute while untouched so they follow the live config once it loads.

**Reference code: the Lanes drawer (base set).** Markup ids the code expects, inside the right gear drawer: `laneCount`, `laneList`, `provBtns`, `catSearch`, `tierChips`, `catRows`, `catStatus`, `keyFields`, `saveKeysBtn`, `clearKeysBtn`; in the header, `cfgBadge` and either `laneBtn` (single path: a button holding `<span id="laneDot">` and `<span id="laneTxt">`) or `fanBtn` (matrix variant). Style `#cfgBadge[data-state="live"]` and `[data-state="fallback"]` in the engine's own CSS. Drawer open/close is the engine's own (ui-contract 06). Call `wireKeys()` once at build time.

```javascript
/* ───────── Lanes drawer: catalog, lanes, keys (base set; add the optional modules only if the brief asked) ───────── */
let catalog = lsGet(CAT_KEY, {}), tierSel = "all", activeProv = null;
const TIERS = ["free", "cheap", "medium", "premium", "n/a"];
const tierOf = m => /:free$/.test(m.id) || m.price === 0 ? "free" : m.price == null ? "n/a" : m.price * 1e6 < 0.5 ? "cheap" : m.price * 1e6 < 3 ? "medium" : "premium";
async function fetchCatalog(pid) {
  if (inflight[pid]) return; inflight[pid] = true;               // catalogHeaders + inflight: see Section 2
  const pv = PROVIDERS[pid], st = $("catStatus"); st.textContent = "Fetching " + pv.label + "…";
  try {
    const k = keyOf(pv.cfg), r = await fetch(pv.url.replace(/\/chat\/completions\/?$/, "/models"), { headers: catalogHeaders(pv.cfg, k) });
    if (r.status === 401 || r.status === 403) throw new Error(pv.label + " catalog needs a saved key (Keys below).");
    if (!r.ok) throw new Error(pv.label + " catalog failed (" + r.status + ")");
    const j = await r.json(), list = (j.data || []).map(m => ({ id: m.id, name: m.name || "", ctx: m.context_length || null, price: m.pricing && m.pricing.prompt != null ? parseFloat(m.pricing.prompt) : null }));
    list.forEach(m => m.tier = tierOf(m)); list.sort((a, b) => TIERS.indexOf(a.tier) - TIERS.indexOf(b.tier) || natCmp(a.id, b.id));
    catalog[pid] = { t: Date.now(), models: list }; lsSet(CAT_KEY, catalog); st.textContent = list.length + " models from " + pv.label + ".";
  } catch (e) { st.textContent = e.message; }
  finally { delete inflight[pid]; }
  renderCatalog();
}
function matcher(q) { q = q.trim(); if (!q) return () => true; const m = q.match(/^\/(.+)\/([a-z]*)$/); if (m) { try { const re = new RegExp(m[1], m[2]); return s => re.test(s); } catch (e) {} } q = q.toLowerCase(); return s => s.toLowerCase().includes(q); }
function chip(txt, on, fn) { const b = document.createElement("button"); b.type = "button"; b.className = "tchip" + (on ? " on" : ""); b.textContent = txt; b.addEventListener("click", fn); return b; }
function renderCatalog() {
  const pb = $("provBtns"); pb.innerHTML = "";
  Object.values(PROVIDERS).forEach(p => { const n = catalog[p.id] ? catalog[p.id].models.length : 0; pb.appendChild(chip(p.label + (n ? " (" + n + ") ↻" : " — fetch"), activeProv === p.id, () => { const was = activeProv === p.id; activeProv = p.id; renderCatalog(); if (!catalog[p.id] || was) fetchCatalog(p.id); })); });   // switch first, fetch second; the active tab refetches
  const tc = $("tierChips"); tc.innerHTML = "";
  ["all", "pinned"].concat(TIERS).forEach(t => tc.appendChild(chip(t === "pinned" ? "Pinned (" + S.settings.customLanes.length + ")" : t, tierSel === t, () => { tierSel = t; renderCatalog(); })));
  const box = $("catRows"); box.innerHTML = ""; const c = catalog[activeProv]; if (!c) return;
  const test = matcher($("catSearch").value), act = activeKeys(), isPin = id => S.settings.customLanes.some(x => x.key === activeProv + "::" + id);
  const rows = c.models.filter(m => (tierSel === "all" || (tierSel === "pinned" ? isPin(m.id) : m.tier === tierSel)) && test(m.id + " " + m.name));
  rows.slice(0, 150).forEach(m => {
    const lab = document.createElement("label"); lab.className = "mrow" + (isPin(m.id) ? " pinned" : "");
    const cb = document.createElement("input"); cb.type = "checkbox"; cb.checked = act.includes(activeProv + "::" + m.id); cb.addEventListener("change", () => togglePin(activeProv, m, cb));
    const meta = document.createElement("span"); meta.className = "meta";
    meta.textContent = [m.ctx ? Math.round(m.ctx / 1000) + "k ctx" : "", m.tier === "free" ? "FREE" : m.price != null ? "$" + (m.price * 1e6).toFixed(2) + "/M in" : ""].filter(Boolean).join(" · ");
    lab.appendChild(cb); lab.appendChild(document.createTextNode(m.id)); lab.appendChild(meta); box.appendChild(lab);       // textContent / text nodes only: catalog text is untrusted
  });
  if (rows.length > 150) { const f = document.createElement("div"); f.className = "key-note"; f.textContent = "Showing 150 of " + rows.length + " — narrow with search."; box.appendChild(f); }
}
const laneLabel = l => (PROVIDERS[l.pid] ? PROVIDERS[l.pid].label : l.pid) + " · " + l.m;
function updateRunControls() {                                   // single path: header lane button; matrix variant: Fan out (n)
  const act = laneList().filter(l => activeKeys().includes(l.key)), first = act[0];
  const fb = $("fanBtn"); if (fb) fb.textContent = "Fan out (" + act.length + ")";
  const lt = $("laneTxt"); if (lt) lt.textContent = !act.length ? "no lane" : act.length === 1 ? laneLabel(first) : act.length + " lanes";
  const ld = $("laneDot"); if (ld) ld.style.background = (first && PROVIDERS[first.pid] && PROVIDERS[first.pid].cfg.dotColor) || "#9090a8";
}
function renderLanes() {                                         // doubles as ensureLanes(): activeKeys() already drops stale keys
  const box = $("laneList"); box.innerHTML = ""; const act = activeKeys();
  laneList().forEach(l => {
    const lab = document.createElement("label"); lab.className = "mrow" + (l.pinned ? " pinned" : "");
    const cb = document.createElement("input"); cb.type = "checkbox"; cb.checked = act.includes(l.key);
    cb.addEventListener("change", () => { if (!setLane(l.key, cb.checked)) cb.checked = false; renderLanes(); renderCatalog(); });
    const dot = document.createElement("span"); dot.className = "provider-dot"; dot.style.cssText = "display:inline-block;margin-right:6px;background:" + ((PROVIDERS[l.pid] && PROVIDERS[l.pid].cfg.dotColor) || "#9090a8");
    lab.appendChild(cb); lab.appendChild(dot); lab.appendChild(document.createTextNode((l.pinned ? "★ " : "") + laneLabel(l)));
    if (l.pinned) { const x = document.createElement("span"); x.textContent = "  ×"; x.style.color = "var(--red, #ef4444)";
      x.addEventListener("click", e => { e.preventDefault(); e.stopPropagation(); S.settings.customLanes = S.settings.customLanes.filter(c => c.key !== l.key); setLane(l.key, false); renderLanes(); renderCatalog(); }); lab.appendChild(x); }
    box.appendChild(lab);
  });
  const n = act.length; $("laneCount").textContent = n + " of " + laneList().length + " lanes active (max " + MAX_LANES + ")" + (n > 6 ? " · large fan-outs can hit provider rate limits" : "");
  updateRunControls();
}
function renderKeyRows() {
  const box = $("keyFields"); box.innerHTML = "";
  usableProviders().filter(p => !p.native && p.requiresKey).forEach(p => {
    const wrap = document.createElement("div"), lab = document.createElement("label"), inp = document.createElement("input");
    lab.textContent = p.keyLabel || p.label + " Key"; inp.type = "password"; inp.placeholder = p.keyPlaceholder || ""; inp.id = "keyInput_" + p.keyStorageName; inp.value = getKey(p.keyStorageName);
    wrap.appendChild(lab); wrap.appendChild(inp);
    if (p.keyNote) { const n = document.createElement("div"); n.className = "key-note"; n.textContent = p.keyNote; wrap.appendChild(n); }
    box.appendChild(wrap);
  });
}
function wireKeys() {                                            // call once; closeDrawer() is the engine's own
  $("saveKeysBtn").addEventListener("click", () => { usableProviders().filter(p => !p.native && p.requiresKey).forEach(p => { const el = $("keyInput_" + p.keyStorageName); if (el) setKey(p.keyStorageName, el.value); }); closeDrawer(); });
  $("clearKeysBtn").addEventListener("click", () => { usableProviders().filter(p => !p.native).forEach(p => { try { localStorage.removeItem("hek_" + p.keyStorageName); } catch (e) {} }); renderKeyRows(); toast("Saved keys cleared from this device"); });
  $("catSearch").addEventListener("input", renderCatalog);
}
function renderConfigUI() {                                      // the hook applyConfigToPicker() calls after first paint
  const b = $("cfgBadge"); b.textContent = configSource === "live" ? "Config: Live" : "Config: Local Fallback"; b.dataset.state = configSource;
  if (!activeProv || !PROVIDERS[activeProv]) activeProv = Object.keys(PROVIDERS)[0];
  renderLanes(); renderCatalog(); renderKeyRows();
  if (typeof afterConfigUI === "function") afterConfigUI();      // matrix / curated engines define it: renderProviderSelector() + restore the saved provider
}
```

An engine that keeps its provider selector (the matrix variant) defines `afterConfigUI`; a single-path engine has no provider selector and does not.

State: `S.settings.lanes`, `S.settings.customLanes` and `S.settings.lanesTouched` travel with state export; the catalog cache does not. Every response record from a lane stores `provider`, the requested `model`, and `served` when it differs.

---

---

## BANNED PATTERNS

- NEVER re-implement a config loader, key store, request builder, stream reader or call layer: consume the Core API.
- NEVER route, list or count a native provider entry in a standalone engine.
- NEVER hard-code a provider name, model slug, endpoint or default in the HTML: defaults are `defaultLanes()`; the offline floor is the core's `LOCAL_FALLBACK_CONFIG`.
- NEVER leave a provider / endpoint / model field block, or a provider dropdown, beside the picker (single path).
- NEVER store keys outside `hek_{keyStorageName}`, or send a key to any host except its own provider.
- NEVER render catalog text with `innerHTML`.
- NEVER send `headersFor()` output, attribution headers or a key to a public catalog endpoint: catalog GETs go through `catalogHeaders`.
- NEVER start a second catalog fetch for a provider while one is in flight.
- NEVER auto-refetch the catalog on load, and never remap a model id across providers.
- NEVER put `openrouter/auto` (the paid router) anywhere.
- Mode A: NEVER let a lane fall through to another lane or provider; the label must be the truth.
- Mode B: NEVER add a free-text Custom entry to the dropdown; the catalog popover is the only route to non-config models.

## PRE-SHIP CHECKLIST (adds to the ui-contract pre-ship gates)

- [ ] Mode gate answered (lanes, panel or no picker); build plan names the mode
- [ ] Model Core pasted verbatim; the engine has no provider constant, key store, request builder or stream reader of its own
- [ ] Badge reads Config: Live with the network up and Config: Local Fallback with it blocked; both leave working defaults
- [ ] Defaults equal `defaultLanes()` (two today); Lanes: only the first is ticked until the user touches the list
- [ ] Single path: exactly one control chooses the model; no leftover provider / endpoint / model fields; an unknown saved selection falls back to the default instead of erroring
- [ ] Native entry present in config produces no dropdown row, lane, key row or button
- [ ] Mode B: dropdown has config groups, Recent (max 5, newest first, deduped) and Clear; no Custom; popover row click reassigns and records history; drawer `1..N` / `all` work
- [ ] Mode B: `max tok` sends `max_tokens`, appends the length line, and flags "cut at token cap"; a 429 shows the countdown and retries
- [ ] Mode A: pin adds a star lane and ticks it; the max-12 toast fires; lanes never show a model other than the one requested, except a visible `served:` tag
- [ ] Old ids migrate on boot (`openrouter::`, `provider|model`, `pin|provider|model` to `providerId::model`); saved keys under old names still work through `LEGACY_KEY_SLOTS`
- [ ] Optional modules (tags, Synth Picks, price sort) are present only if the brief asked for them
- [ ] Catalog fetch: with an OpenRouter key saved, the Network tab shows the `/models` GET with no `OPTIONS` preflight and no custom headers; Groq's carries only its auth header
- [ ] Clicking an unfetched provider tab switches to it at once; a failed fetch shows its error under that provider; rapid double clicks start one request

## QUICK REFERENCE

```
LAYER          : optional selection layer on the Model Core (model-config-contract v2); consumes the Core API, owns no config/keys/call code
MODES          : A lanes (parallel, pins, single path) | B panel (slot per panel + Recent history) | neither = no picker, stay on the core
DEFAULTS       : config defaultLanes() = groq::openai/gpt-oss-120b + or-auto::openrouter/free; Lanes ticks only the first until touched
STANDALONE     : native skipped; fallback = the core's LOCAL_FALLBACK_CONFIG (mirrors the live model.json)
CONFIG         : the core's fetchModelConfig; badge Live / Local Fallback; render the floor first
CATALOG        : provider /models via catalogHeaders (OpenRouter none, keyed providers auth only), one in-flight fetch per provider, tab switches before it fetches, cached, user-refreshed; auto-fetch only public endpoints or keyed providers
BASE FILTERS   : tiers, search + /regex/ | OPTIONAL MODULES: +tags (dashed ? = heuristic), +synth, +price
CALL           : callModel strict: system fold, 404 hint, fatal 401/402/403/413, served tag, reasoning liveness, empty-reply hint
A: RETRY       : core retries a 429 once (1800 ms)   | B: RETRY: countdown on status/retryAfter, 3 tries, <= 90 s
B: CAP         : max tok per panel = maxTokens + auto word target; result.cut flags "cut at token cap"
LANE KEYS      : providerId::modelId (v2 provider|model and pin|provider|model migrate at boot)
ALIASES        : model.json model_aliases via the core's resolveModelId, only against a fetched catalog, never across providers
NEW DATA       : catalog cache, A: customLanes + lanes + lanesTouched, B: history[][] + caps[]
OUTPUT         : updated .html per engine; model.json unchanged (defaults and aliases are model.json edits)
```
