---
name: model-config-contract
description: "Model Core v2: the universal provider and model layer for every HTML engine that calls an LLM. Owns model.json (providers, chains, defaultLanes, model_aliases, per-provider timing), the standard two-model floor (Groq gpt-oss-120b plus the OpenRouter free router), key slots (hek_ with legacy-slot fallback), and the ONE hardened call layer, callModel: a curated chain-walk or a strict single-model call, streaming, 429 retry, system-role fold, fatal statuses, served-model tag, reasoning liveness. hybrid-engine-contract delegates to this skill for all provider and model handling; model-catalog-panel is the optional picker built on top of it and never re-implements any of it. Invoke with /model-config or \"invoke model config contract\". Implied by /hybrid-engine for new builds; invoke explicitly to retrofit an existing engine.\n"
---

# Model Core (model-config-contract v2)

> **STATUS: v2, released as a set of four.** Install together, replacing the old ones: `model-config-contract` (this file), `hybrid-engine-contract`, `ui-contract`, `model-catalog-panel` (v3.2). The live `model.json` was updated on GitHub on 2026-10-03 (`defaultLanes`, `model_aliases`, OpenRouter chain reduced to `openrouter/free`).

The one layer that makes provider and model handling **data and one shared runtime**, instead of four hand-built copies per engine. Every engine that calls an LLM gets it; engines that want a model picker add `model-catalog-panel` on top.

```
Invocation: implied by /hybrid-engine (new builds)  |  /model-config (retrofit an existing engine)
Pair with:  /hybrid-engine  (skeleton: its callAI / provider branches now delegate here)
            /ui-contract    (chassis: header, drawer, panels)
Optional:   /catalog lanes | /catalog panel   (picker layer; depends on this skill, never duplicates it)
```

## WHAT CHANGED IN v2 (the delta from v1)

1. **One call layer.** The curated chain-walk (v1) and the strict single-model call that `model-catalog-panel` carried are now one function, `callModel`, with two modes. The hardening (429 retry, system fold, fatal statuses, served tag, reasoning liveness, empty-reply hint) lives here once.
2. **The floor is explicit.** Groq `gpt-oss-120b` and the OpenRouter free router are the standard defaults, declared as data (`defaultLanes`), mirrored in `LOCAL_FALLBACK_CONFIG` so an engine runs with no network.
3. **Two new optional `model.json` fields:** `defaultLanes` and `model_aliases`. Non-breaking: older engines ignore fields they do not know.
4. **Key slots with a legacy fallback** (`LEGACY_KEY_SLOTS`), so engines that stored keys under their own names migrate without losing a saved key.
5. **Config validation relaxed from "exactly one native" to "at most one native, and at least one provider usable in this context"**, because standalone-only engines never route Claude Native.
6. **`$origin` no longer resolves to the string `null`** when an engine is opened from a file.
7. **Synced to the live `model.json` of 2026-10-03:** the OpenRouter chain is the router alone, `LOCAL_FALLBACK_CONFIG` mirrors the live file's providers and `defaultLanes` field for field (`model_aliases` is deliberately not duplicated: aliases are volatile and only matter against a fetched catalog), and the schema example below is the deployed file.
8. **A published Core API** (below): the stable seam the catalog layer consumes. It carries the hooks pickers need: `headersFor`, `retryAfterSeconds`, an abort `signal`, and `status` / `retryAfter` on thrown errors (so a panel engine can show a 429 countdown).
9. **Claude Native defaults to `max_tokens` 4000** (the figure `hybrid-engine-contract` always used), and its stream is always parsed as Anthropic format.

## WHERE THIS SITS

```
Engine
 |- Chassis ........ ui-contract + hybrid-engine-contract   (layout, panels, copy)
 |- Selection ...... model-catalog-panel, OPTIONAL          (Lanes mode | Panel mode)
 |- Model Core ..... THIS SKILL                             (loader, keys, callModel)
 '- Data ........... model.json on GitHub                   (providers, defaultLanes, aliases, timing)
```

---

## THE PROBLEM THIS SOLVES

Every prior engine — including the one just patched — had three surfaces of hardcoded provider truth living inside the `.html` file itself:

1. **The model itself** — `model: 'claude-sonnet-4-6'`, `model: groqChain[gi]` — literal strings in `callAI()`.
2. **The provider list** — `<option value="groq">Groq · gpt-oss-120b</option>` — literal markup in the selector.
3. **The key-collection UI** — `<div class="drawer-field"><label>Groq API Key</label>...` — literal markup in the drawer.

Patching (1) alone — as the earlier `model.json` fetch did — solves "a model got decommissioned." It does **not** solve "a provider got decommissioned" or "I want to add a new provider," because (2) and (3) are still HTML that has to be hand-edited in every one of ~60 files.

This contract closes all three. After adoption, the **only** file that ever needs to change when the model landscape shifts is `model.json`. Reload the engine, the change is live. No HTML touched, no redeploy, on any engine that has adopted this contract.

---

---

## WHAT STAYS HARDCODED — AND WHY (NON-NEGOTIABLE)

One thing is deliberately excluded from config-driven behavior, for security reasons, not convenience:

**Claude Native's no-Authorization-header behavior is a code-level branch, never a config-driven request template.**

`model.json` is a public, unauthenticated file. Anyone can read it. If the *request-construction logic* for the Claude Native path were built from a generic template the same way every other provider is, a corrupted or maliciously-edited `model.json` could inject an `Authorization` header into the Claude Native call, or repoint its endpoint — defeating the entire reason Native routing exists (the platform's own proxy, zero key exposure).

So: config may **declare** `"native": true` on the Claude entry for display and selector purposes. The engine's adapter, in code, checks `if (provider.native === true)` and takes a **hardcoded, non-configurable branch** — fixed endpoint (`https://api.anthropic.com/v1/messages`), fixed headers (no Authorization), fixed model string. `model.json` cannot change what "native" *does* — only whether an entry claims to be native, which only matters for how it's labeled and ordered in the selector. If you want to change the Claude model string itself, that still goes through config (see Native Model Override below) — but the *header omission* behavior itself is pinned in code, permanently.

Every other field, for every other provider, is fully data-driven.

---

---

## CANONICAL CONFIG URL — FIXED, DO NOT VARY PER ENGINE

Every engine that adopts this contract fetches from the same live, GitHub-hosted URL. This is not a placeholder or an example — it is the actual, permanent config source for the ecosystem, decided and confirmed:

```
CANONICAL_CONFIG_URL = "https://raw.githubusercontent.com/meetvenkat1-code/therantai-config/refs/heads/main/model.json"
```

The fetch itself is `fetchModelConfig()` in the Model Core block below (cache-busted, validated, falls back to `LOCAL_FALLBACK_CONFIG`).

**What this means in practice:** a decommissioned model, a new provider, a renamed slug — none of it touches any `.html` file, ever. You edit `model.json` in the `therantai-config` repo, commit, and every engine already pointing at `CANONICAL_CONFIG_URL` picks up the change on its next page load. No per-engine testing is required for a pure data change, because the HTML code path itself does not change — only the data it reads.

**One caveat that is real, not hypothetical:** `raw.githubusercontent.com` sits behind a CDN that caches for a few minutes after a commit. The `?v=Date.now()` cache-buster on the fetch defeats *browser* caching but not the CDN edge cache — so a commit can take a few minutes to actually propagate to engines fetching it, even with cache-busting in place. This is not a bug in the contract; it is a property of the hosting choice. If a change needs to be instant, that is the one thing still worth knowing.

Per-engine override is still permitted for the rare engine whose provider set genuinely diverges (see RETROFIT PROCEDURE step 1) — but `CANONICAL_CONFIG_URL` above is the default for all ~60 engines, not `./model.json`.

---

---

## THE FLOOR: STANDARD DEFAULTS

Every engine ships on the floor unless it asks for more: **Groq `openai/gpt-oss-120b`** (fast, keyed) and the **OpenRouter free router `openrouter/free`** (slow, free). These are the two working defaults across the ecosystem.

- The floor is **data**: `defaultLanes` in `model.json`, `"providerId::modelSlug"` entries. `LOCAL_FALLBACK_CONFIG` carries the same two so a first load, or a failed fetch, still works.
- Context rule, unchanged: inside claude.ai the default is Claude Native (`defaultFor: ["artifact"]`); standalone, the default is the first provider whose `defaultFor` includes `"standalone"`.
- **No picker (Build 1):** the header provider selector lists `usableProviders()`; calls use curated mode and walk each provider's `modelChain` with its fallbacks. The OpenRouter route is the free router alone (`openrouter/free`); named free models arrive only through the catalog.
- **With a picker (Builds 2 and 3):** the catalog layer seeds lanes or panels from `defaultLanes()`. Anything beyond the floor arrives through the catalog, never by hardcoding a slug in the HTML.
- An engine must not name a model slug in its own HTML. If it needs a different default, that is a `defaultLanes` edit.

---

## MODEL.JSON — CANONICAL SCHEMA

```json
{
  "updated": "2026-10-03",
  "native_model": "claude-sonnet-4-6",
  "defaultLanes": ["groq::openai/gpt-oss-120b", "or-auto::openrouter/free"],
  "model_aliases": {},
  "defaultLanes": ["groq::openai/gpt-oss-120b", "or-auto::openrouter/free"],
  "model_aliases": {
    "llama-3.1-8b-instant": "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile": "openai/gpt-oss-120b",
    "qwen/qwen3-32b": "openai/gpt-oss-120b",
    "meta-llama/llama-4-scout-17b-16e-instruct": "openai/gpt-oss-120b"
  },
  "providers": [
    {
      "id": "claude",
      "native": true,
      "label": "Claude · Native",
      "dotColor": "#ef4444",
      "requiresKey": false,
      "defaultFor": ["artifact"]
    },
    {
      "id": "groq",
      "native": false,
      "label": "Groq",
      "dotColor": "#22c55e",
      "requiresKey": true,
      "keyStorageName": "groq",
      "keyLabel": "Groq API Key",
      "keyPlaceholder": "gsk_…",
      "defaultFor": ["standalone"],
      "endpoint": "https://api.groq.com/openai/v1/chat/completions",
      "authHeader": "Authorization",
      "authPrefix": "Bearer ",
      "requestFormat": "openai-chat",
      "streamFormat": "openai",
      "modelChain": ["openai/gpt-oss-120b", "openai/gpt-oss-20b"],
      "softFallback": { "on": [429, 500, 502, 503], "within": true },
      "hardFallback": "or-auto",
      "timeoutMs": 15000,
      "idleMs": 3000
    },
    {
      "id": "or-auto",
      "native": false,
      "label": "OR · Free Router",
      "dotColor": "#f97316",
      "requiresKey": true,
      "keyStorageName": "openrouter",
      "keyLabel": "OpenRouter API Key",
      "keyPlaceholder": "sk-or-…",
      "keyNote": "Standalone only — OpenRouter has no CORS proxy inside claude.ai",
      "standaloneOnly": true,
      "endpoint": "https://openrouter.ai/api/v1/chat/completions",
      "authHeader": "Authorization",
      "authPrefix": "Bearer ",
      "extraHeaders": { "HTTP-Referer": "$origin", "X-Title": "$engineName" },
      "requestFormat": "openai-chat",
      "streamFormat": "openai",
      "modelChain": ["openrouter/free"],
      "softFallback": { "on": [429, 500, 502, 503], "within": true },
      "timeoutMs": 45000,
      "idleMs": 9000
    }
  ],
  "or_specific_models": []
}
```

This is the live `model.json` as deployed on 2026-10-03. `or-auto` carries the free router alone (`openrouter/free`); the named free models that used to precede it (Nemotron, GLM) were removed from the chain because they are the volatile, rate-limited layer, and remain reachable as catalog pins. `groq` keeps `gpt-oss-120b` then `gpt-oss-20b`, hard-falling to `or-auto`. `model_aliases` is seeded with Groq's published replacements for models it retired in July and August 2026. `or-auto` is the terminal fallback target, so it declares no `hardFallback` of its own.

**New in v2 (both optional):**

- `defaultLanes` — array of `"providerId::modelSlug"` strings (split on the first `::`; slugs may contain `/` and `:`). The floor. Each entry must name a provider present in `providers[]` and a slug that provider can serve. Entries that name a native provider, or a provider not usable in the current context, are ignored. If the field is absent or filters to nothing, the engine falls back to the first model of the first usable provider.
- `model_aliases` — map of retired slug to live successor, e.g. `{"old/slug": "new/slug"}`. Values must be existing ids. Used by `resolveModelId` against a catalog the user has actually fetched. This is the fleet-wide counterpart to per-user remapping.

**Field notes:**

- `providers[]` is the entire selector, top to bottom, in order. Adding an entry adds a provider. Removing one removes it. No HTML edit either way.
- `native: true` — see the hardcoded carve-out above. At most one entry should carry this; the adapter enforces the fixed-behavior branch regardless of what else the entry claims.
- `requiresKey` — drives whether a drawer row renders for this provider at all.
- `keyStorageName` — the `localStorage` suffix (`hek_{keyStorageName}`). Lets a provider's *id* (used for selector value / routing) diverge from its *key namespace* if ever needed (e.g. two OR-family entries sharing one key).
- `defaultFor` — array containing `"artifact"` and/or `"standalone"`. The adapter picks the first provider whose `defaultFor` matches the current context (mirrors hybrid-engine-contract's Constraint 12 logic, now data-driven instead of a hardcoded ternary).
- `standaloneOnly` — replicates the existing OR-in-artifact block; adapter refuses to run this provider when `window.self !== window.top` and shows the inline notice, same UX as before, now driven by a flag instead of an `isOpenRouterProvider()` string check.
- `endpoint`, `authHeader`, `authPrefix`, `extraHeaders`, `requestFormat`, `streamFormat` — the generic adapter's template. `requestFormat: "openai-chat"` and `requestFormat: "anthropic-messages"` are the two shapes currently needed; new shapes get added to the adapter's format map only if a genuinely new API shape appears (rare — this is the one seam that can still require a code change, but it's a one-time addition to the adapter, not a per-engine edit).
- `modelChain` + `softFallback` + `hardFallback` — generalizes the Groq chain-walk logic that used to be hardcoded per-engine. Any provider can now declare a fallback chain and a hard-fallback target by id.
- `timeoutMs` / `idleMs` — optional per-provider stream timing (hard ceiling / silence window). Omit either to fall back to the module defaults (15000ms / 3000ms). Give `or-auto` a wider pair than Groq/Claude — see PER-PROVIDER STREAM TIMING below.
- `or_specific_models` — deprecated and empty; kept in the file because older engines may still read the key. Named OR models are no longer part of the chain: pin them from the catalog (Lanes or Panel mode).

---

---

## KEY SLOTS

Key values live **only** in the browser: `localStorage` under `hek_{keyStorageName}`. Never in `model.json`, never round-tripped.

- `getKey(name)` reads `hek_{name}` first, then each name listed in `LEGACY_KEY_SLOTS[name]` (read-only fallbacks). `setKey(name, value)` writes only the `hek_` slot and never touches a legacy one.
- An engine that stored keys under its own names declares them once in `LEGACY_KEY_SLOTS`, e.g. `{ groq: ['rl.key.gq'], openrouter: ['rl.key.or'] }`. Saved keys keep working; the first save in the drawer migrates them.
- A "Clear saved keys" control must clear both the `hek_` slots and every legacy slot, or the old key silently reappears.
- If the engine has a storage abstraction (ui-contract Constraint 21), route `getKey`/`setKey` through it instead of raw `localStorage`.

---

## THE MODEL CORE (paste verbatim, edit only the three CONSTANTS)

This block replaces v1's "generic adapter" and every per-engine provider branch, `callAI`, and `readStream`. It was smoke-tested against mocked streams and storage (15 checks): strict streaming with served tag, system fold, fatal 401 stopping everything, a strict call never falling through on 429, a curated chain advancing on 404, the empty-reply hint, the floor, config validation, aliases, the legacy key fallback, 429 `status` and `retryAfter` (header and Groq text forms), abort, a Claude Native Anthropic stream with no Authorization header, and `headersFor` placeholder resolution.

```javascript
/* MODEL CORE v2 (model-config-contract). Paste verbatim. Edit only the three CONSTANTS. */
var ENGINE_NAME = 'My Engine';                                   // CONSTANT 1: shown in X-Title
var CANONICAL_CONFIG_URL = 'https://raw.githubusercontent.com/meetvenkat1-code/therantai-config/refs/heads/main/model.json';   // CONSTANT 2: never vary
var LEGACY_KEY_SLOTS = {};                                       // CONSTANT 3: read-only fallbacks, e.g. { groq: ['rl.key.gq'], openrouter: ['rl.key.or'] }
var DEFAULT_TIMEOUT_MS = 15000, DEFAULT_IDLE_MS = 3000;
var isArtifact = window.self !== window.top;

var LOCAL_FALLBACK_CONFIG = {                                    // mirrors the live model.json providers and defaultLanes (2026-10-03); model_aliases are deliberately not duplicated
  native_model: 'claude-sonnet-4-6',
  defaultLanes: ['groq::openai/gpt-oss-120b', 'or-auto::openrouter/free'],
  providers: [
    { id: 'claude', native: true, label: 'Claude · Native', dotColor: '#ef4444', requiresKey: false, defaultFor: ['artifact'] },
    { id: 'groq', native: false, label: 'Groq', dotColor: '#22c55e', requiresKey: true, keyStorageName: 'groq', keyLabel: 'Groq API Key', keyPlaceholder: 'gsk_…', defaultFor: ['standalone'],
      endpoint: 'https://api.groq.com/openai/v1/chat/completions', authHeader: 'Authorization', authPrefix: 'Bearer ', requestFormat: 'openai-chat', streamFormat: 'openai',
      modelChain: ['openai/gpt-oss-120b', 'openai/gpt-oss-20b'], softFallback: { on: [429, 500, 502, 503], within: true }, hardFallback: 'or-auto', timeoutMs: 15000, idleMs: 3000 },
    { id: 'or-auto', native: false, label: 'OR · Free Router', dotColor: '#f97316', requiresKey: true, keyStorageName: 'openrouter', keyLabel: 'OpenRouter API Key', keyPlaceholder: 'sk-or-…',
      keyNote: 'Standalone only — OpenRouter has no CORS proxy inside claude.ai', standaloneOnly: true,
      endpoint: 'https://openrouter.ai/api/v1/chat/completions', authHeader: 'Authorization', authPrefix: 'Bearer ',
      extraHeaders: { 'HTTP-Referer': '$origin', 'X-Title': '$engineName' }, requestFormat: 'openai-chat', streamFormat: 'openai', modelChain: ['openrouter/free'], softFallback: { on: [429, 500, 502, 503], within: true }, timeoutMs: 45000, idleMs: 9000 }
  ]
};
var liveModelConfig = LOCAL_FALLBACK_CONFIG;                     // boot on the floor, upgrade when the fetch lands

var sleep = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };
function natCmp(a, b) { return a.localeCompare(b, undefined, { numeric: true }); }
function cfgProviders() { return liveModelConfig.providers; }
function P(id) { return cfgProviders().filter(function (p) { return p.id === id; })[0] || null; }
function splitKey(k) { var i = k.indexOf('::'); return { provider: k.slice(0, i), model: k.slice(i + 2) }; }

function isValidConfig(j) {
  if (!j || !Array.isArray(j.providers) || !j.providers.length) return false;
  var ids = {}, natives = 0, usable = false;
  for (var i = 0; i < j.providers.length; i++) {
    var p = j.providers[i];
    if (!p || !p.id || !p.label || ids[p.id]) return false;
    ids[p.id] = 1;
    if (p.native === true) { natives++; if (isArtifact) usable = true; }
    else if (p.endpoint && p.requestFormat === 'openai-chat' && !(p.standaloneOnly && isArtifact)) usable = true;
  }
  return natives <= 1 && usable;                                 // never adopt a half-valid config
}
function usableProviders() {                                     // native only inside claude.ai; standalone never routes it
  return cfgProviders().filter(function (p) { return p.native === true ? isArtifact : !(p.standaloneOnly && isArtifact); });
}
function defaultLanes() {                                        // the floor: config's defaultLanes, else first model of the first usable provider
  var ok = usableProviders().map(function (p) { return p.id; });
  var list = (liveModelConfig.defaultLanes || []).filter(function (k) {
    if (k.indexOf('::') < 1) return false; var s = splitKey(k); return ok.indexOf(s.provider) > -1 && !P(s.provider).native;
  });
  if (!list.length) {
    var p = usableProviders().filter(function (x) { return !x.native && x.modelChain && x.modelChain.length; })[0];
    if (p) list = [p.id + '::' + p.modelChain[0]];
  }
  return list;
}

function getKey(name) {
  try {
    var v = localStorage.getItem('hek_' + name); if (v) return v.trim();
    var old = LEGACY_KEY_SLOTS[name] || [];
    for (var i = 0; i < old.length; i++) { var o = localStorage.getItem(old[i]); if (o) return o.trim(); }
  } catch (e) {}
  return '';
}
function setKey(name, value) { try { localStorage.setItem('hek_' + name, (value || '').trim()); } catch (e) {} }

function headersFor(cfg, key) {                                  // CHAT requests only (POST /chat/completions). The picker's GET /models does NOT use this: it uses catalogHeaders (model-catalog-panel v3.2), because these headers force a CORS preflight on a cross-origin GET
  var h = { 'Content-Type': 'application/json' };
  if (key && cfg.authHeader) h[cfg.authHeader] = (cfg.authPrefix || '') + key;
  Object.keys(cfg.extraHeaders || {}).forEach(function (k) {
    var v = cfg.extraHeaders[k];
    h[k] = v === '$origin' ? (window.location.origin !== 'null' ? window.location.origin : 'http://localhost') : v === '$engineName' ? ENGINE_NAME : v;
  });
  return h;
}
function retryAfterSeconds(res, msg) {                           // header first, then Groq's "try again in 26.6s / 1m3.5s / 250ms"
  var ra = parseFloat(res.headers && res.headers.get && res.headers.get('retry-after')); if (!isNaN(ra)) return ra;
  var m = /try again in\s+([0-9hms.]+)/i.exec(msg || ''); if (!m) return null;
  var t = 0; m[1].replace(/(\d+(?:\.\d+)?)(ms|h|m|s)/g, function (_, n, u) { t += parseFloat(n) * { ms: 0.001, s: 1, m: 60, h: 3600 }[u]; });
  return t || null;
}

function buildRequest(cfg, modelId, system, user, stream, maxTokens) {
  if (cfg.native === true) {                                     // HARDCODED BRANCH. Never built from cfg fields.
    return { url: 'https://api.anthropic.com/v1/messages',
      headers: { 'Content-Type': 'application/json', 'anthropic-version': '2023-06-01', 'anthropic-dangerous-direct-browser-access': 'true' },
      body: { model: modelId, max_tokens: maxTokens || 4000, stream: stream, system: system || '', messages: [{ role: 'user', content: user }] } };
  }
  if (cfg.requestFormat !== 'openai-chat') throw new Error('Unknown requestFormat: ' + cfg.requestFormat);
  var h = headersFor(cfg, getKey(cfg.keyStorageName));
  var body = { model: modelId, stream: stream, messages: (system ? [{ role: 'system', content: system }] : []).concat([{ role: 'user', content: user }]) };
  if (maxTokens) body.max_tokens = maxTokens;
  return { url: cfg.endpoint, headers: h, body: body };
}

function readStream(res, format, onChunk, timeoutMs, idleMs, signal) {   // resolves { reason, error }; never rejects
  var rd = res.body.getReader(), dec = new TextDecoder(), buf = '', done = false, idleT, hardT, reason = null, err = null;
  timeoutMs = timeoutMs || DEFAULT_TIMEOUT_MS; idleMs = idleMs || DEFAULT_IDLE_MS;
  return new Promise(function (resolve) {
    function finish() { if (done) return; done = true; clearTimeout(idleT); clearTimeout(hardT); try { rd.cancel(); } catch (e) {} resolve({ reason: reason, error: err }); }
    function resetIdle() { clearTimeout(idleT); idleT = setTimeout(finish, idleMs); }
    hardT = setTimeout(finish, timeoutMs); resetIdle();
    if (signal) { if (signal.aborted) return finish(); signal.addEventListener('abort', finish, { once: true }); }
    (function pump() {
      if (done) return;
      rd.read().then(function (r) {
        if (done) return;
        if (r.done) return finish();
        buf += dec.decode(r.value, { stream: true });
        var lines = buf.split('\n'); buf = lines.pop();
        for (var i = 0; i < lines.length; i++) {
          var t = lines[i].trim();
          if (format === 'anthropic' && t === 'event: message_stop') return finish();   // named event line precedes its data: line
          if (t.indexOf('data:') !== 0) continue;
          var d = t.slice(5).trim(); if (d === '[DONE]') return finish();
          try {
            var p = JSON.parse(d);
            if (p.error) { err = (p.error.message || 'stream error'); return finish(); }
            if (format === 'anthropic') {
              if (p.type === 'content_block_delta' && p.delta && p.delta.text) { onChunk(p.delta.text, null); resetIdle(); }
              else if (p.type === 'message_delta' && p.delta && p.delta.stop_reason) reason = p.delta.stop_reason === 'max_tokens' ? 'length' : p.delta.stop_reason;
              else if (p.type === 'message_stop') return finish();
            } else {
              var c0 = p.choices && p.choices[0], dl = c0 && c0.delta;
              if (c0 && c0.finish_reason) reason = c0.finish_reason;
              if (dl && dl.content) { onChunk(dl.content, p.model || null); resetIdle(); }
              else if (dl && (dl.reasoning || dl.reasoning_content)) resetIdle();   // thinking counts as alive
            }
          } catch (e) {}
        }
        pump();
      }).catch(finish);
    })();
  });
}

/* ONE call layer, two modes.
   curated: callModel({ provider, system, user, onText, validate })         -> walks modelChain, soft/hard fallback
   strict : callModel({ provider, model, system, user, onText, maxTokens }) -> exactly that model, never falls through (lanes, panels)
   onText(accumulatedText, servedModelOrNull) fires on every chunk. Returns { text, model, served, cut }. */
async function callModel(o) {
  var cfg = P(o.provider), strict = !!o.model;
  if (!cfg) throw new Error('Unknown provider: ' + o.provider);
  if (cfg.standaloneOnly && isArtifact) throw new Error(cfg.label + ' is standalone only. It has no proxy inside claude.ai.');
  if (cfg.requiresKey && !getKey(cfg.keyStorageName)) throw new Error('No ' + (cfg.keyLabel || cfg.label) + ' saved. Open settings.');
  var models = strict ? [o.model] : (o.chain || (cfg.native ? [liveModelConfig.native_model] : cfg.modelChain) || []);
  var lastStatus = null, lastRetry = null;
  function fail(m) { var e = new Error(m); e.status = lastStatus; e.retryAfter = lastRetry; return e; }   // lets a panel engine show a 429 countdown
  function aborted() { if (o.signal && o.signal.aborted) { var e = new Error('Aborted'); e.name = 'AbortError'; throw e; } }
  var advance = ((cfg.softFallback && cfg.softFallback.on) || [429, 500, 502, 503]).concat([400, 404, 422]);
  var last = '';
  for (var i = 0; i < models.length; i++) {
    var retried = false, folded = false, fatal = null;
    for (var a = 0; a < 3; a++) {
      aborted();
      var acc = '', served = null, res;
      var sys = folded ? '' : o.system, usr = folded ? (o.system ? o.system + '\n\n---\n\n' : '') + o.user : o.user;
      try {
        var rq = buildRequest(cfg, models[i], sys, usr, true, o.maxTokens);
        res = await fetch(rq.url, { method: 'POST', headers: rq.headers, body: JSON.stringify(rq.body), signal: o.signal });
      } catch (e) { if (e && e.name === 'AbortError') throw e; last = cfg.id + ': network error ' + e.message; break; }
      if (!res.ok) {
        var msg = ''; try { var eb = await res.json(); msg = (eb.error && eb.error.message) || ''; } catch (e) {}
        lastStatus = res.status; lastRetry = retryAfterSeconds(res, msg);
        if (res.status === 429 && !retried) { retried = true; await sleep(1800); continue; }                       // one retry, then advance
        if (res.status === 400 && !folded && /system|developer|instruction/i.test(msg)) { folded = true; continue; }   // model rejects the system role
        last = cfg.id + ':' + res.status + (msg ? ' ' + String(msg).slice(0, 140) : '') + (res.status === 404 ? ' — model not found, refresh the catalog' : '');
        if (advance.indexOf(res.status) < 0) fatal = last;                                                          // 401/402/403/413: another model will not heal it
        break;
      }
      var out = await readStream(res, cfg.native === true ? 'anthropic' : (cfg.streamFormat || 'openai'), function (c, s) { acc += c; if (s) served = s; if (o.onText) o.onText(acc, served); }, cfg.timeoutMs, cfg.idleMs, o.signal);
      aborted();
      if (!acc.trim()) { last = cfg.id + ': empty reply' + (out.reason === 'length' ? ' — the token cap was spent on reasoning' : out.error ? ' — ' + out.error : ''); break; }
      if (o.validate && !cfg.native) { try { o.validate(acc); } catch (e) { last = cfg.id + ': rejected — ' + e.message; break; } }
      return { text: acc, model: models[i], served: served, cut: out.reason === 'length' };
    }
    if (fatal) throw fail(fatal);                                                                              // stops everything, hardFallback included
  }
  var hf = !strict && !o._noHard && cfg.hardFallback ? P(cfg.hardFallback) : null;                                 // strict calls never reach here: lane honesty
  if (hf) {
    if (hf.standaloneOnly && isArtifact) throw new Error('All providers exhausted (' + last + '). The fallback (' + hf.label + ') is standalone only.');
    if (hf.requiresKey && !getKey(hf.keyStorageName)) throw new Error('Provider unavailable (' + last + '). Fallback ' + hf.label + ' has no key.');
    return callModel({ provider: hf.id, chain: hf.modelChain, system: o.system, user: o.user, onText: o.onText, validate: o.validate, maxTokens: o.maxTokens, _noHard: true });
  }
  throw fail(strict ? last : 'Provider unavailable (' + last + ')');
}

function fetchModelConfig(onApplied) {                           // call once on load, after rendering from the floor
  return fetch(CANONICAL_CONFIG_URL + '?v=' + Date.now())
    .then(function (r) { if (!r.ok) throw new Error('Config fetch failed: ' + r.status); return r.json(); })
    .then(function (j) { if (!isValidConfig(j)) throw new Error('Malformed config'); liveModelConfig = j; return 'live'; })
    .catch(function () { liveModelConfig = LOCAL_FALLBACK_CONFIG; return 'fallback'; })
    .then(function (src) { if (onApplied) onApplied(src); return src; });
}

var KNOWN_MODEL_ALIASES = { 'mistralai/mistral-large': 'mistralai/mistral-large-2411', 'meta-llama/llama-3-70b-instruct': 'meta-llama/llama-3.3-70b-instruct' };
function modelAliases() { return Object.assign({}, KNOWN_MODEL_ALIASES, liveModelConfig.model_aliases || {}); }
function modelIdBase(id) { var q = id.split('-'); while (q.length > 1 && /^(v?\d[\d.]*|\d{4,})$/i.test(q[q.length - 1])) q.pop(); return q.join('-'); }
function resolveModelId(id, live) {                              // only against a catalog the user actually fetched; never across providers
  if (!live || !live.length || live.indexOf(id) > -1) return { id: id, status: 'ok' };
  var al = modelAliases()[id]; if (al && live.indexOf(al) > -1) return { id: al, status: 'alias' };
  var base = modelIdBase(id), c = live.filter(function (x) { return modelIdBase(x) === base; });
  if (c.length) return { id: c.sort(natCmp).reverse()[0], status: 'fuzzy' };
  return { id: id, status: 'unresolved' };
}
```

### The two call modes

| | Curated | Strict |
|---|---|---|
| Call | `callModel({ provider, system, user, onText, validate, signal })` | `callModel({ provider, model, system, user, onText, maxTokens, signal })` |
| Models tried | the provider's `modelChain`, in order | exactly `model`, nothing else |
| On failure | advance the chain, then `hardFallback` | throw; never substitute another model |
| Use for | engines with a provider dropdown, one answer | lanes, panels, any picker: what the user chose is what runs |

Shared by both: streaming only; one 429 retry then advance; one system-role fold per model (a 400 mentioning system, developer or instruction retries with the system text inside the user turn); 401, 402, 403, 413 are fatal and stop the whole call so a wrong key never reads as "all routes failed"; a 404 says "model not found, refresh the catalog" and never silently swaps; an empty reply is an error, with a specific hint when `finish_reason` is `length`; reasoning deltas count as alive for idle timing; the served model (`model` on stream chunks) is reported so the UI can show `served: X` when `openrouter/free` routes elsewhere. `validate` applies to curated mode only and never to the Native branch (see CONTENT-LEVEL VALIDATION). `signal` is an optional `AbortSignal`: abort cancels the fetch and the stream and throws an error named `AbortError`. Every thrown error carries `status` (last HTTP status or null) and `retryAfter` (seconds, from the `retry-after` header or Groq's "try again in 26.6s" text, else null); `callModel` itself retries a 429 once, so a panel engine that wants a visible countdown catches `status === 429` and waits `retryAfter` before calling again.

### Core API (the seam model-catalog-panel consumes)

`fetchModelConfig(onApplied)`, `liveModelConfig`, `usableProviders()`, `P(id)`, `defaultLanes()`, `splitKey(k)`, `getKey(name)`, `setKey(name, v)`, `headersFor(cfg, key)` (chat requests; catalog GETs go through the picker's own `catalogHeaders`), `retryAfterSeconds(res, msg)`, `buildRequest(...)`, `readStream(...)`, `callModel(opts)`, `resolveModelId(id, liveIds)`, `modelAliases()`, `natCmp`, `sleep`. **A selection layer calls these. It must not re-implement a config loader, key store, request builder, stream reader, or call layer.** Boot order: render from the floor immediately, then `fetchModelConfig(render)`.

---

## PER-PROVIDER STREAM TIMING

*v2 note: the streaming variant is implemented once in the Model Core block above (`readStream`, with idle and hard timers). The non-streaming variant below is legacy: ui-contract forbids non-streaming calls in new builds.*

The invariant across engines is the **rule**, not one function signature: every provider entry may declare its own `timeoutMs` (and, for engines with a streaming reader, `idleMs`), and the adapter falls back to module-level defaults — `DEFAULT_TIMEOUT_MS` (15000) and `DEFAULT_IDLE_MS` (3000), where idle timing applies at all — when a provider entry omits them.

```javascript
// Streaming variant (hard timeout + idle timeout):
function readStream(response, format, onChunk, timeoutMs, idleMs) {
  timeoutMs = timeoutMs || DEFAULT_TIMEOUT_MS;
  idleMs = idleMs || DEFAULT_IDLE_MS;
  // hardTimer: aborts if the whole response never completes within timeoutMs
  // idleTimer: resets on each chunk; aborts if no chunk arrives within idleMs
}

// Non-streaming variant (single timeout, no idle concept):
async function attemptCall(providerCfg, modelId, systemPrompt, userMessage, validate) {
  const timeoutMs = providerCfg.timeoutMs || DEFAULT_TIMEOUT_MS;
  // Promise.race against a timeout — no AbortController in sandboxed/artifact contexts,
  // since AbortSignal can't cross a postMessage-proxied fetch boundary.
}
```

Structural rules that hold regardless of which variant an engine uses:

- **Timing is per-provider, never global.** A single 15s/3s budget tuned for fast providers (Claude, Groq) causes real truncation on slower ones — free-tier OpenRouter is measurably slower to first-byte and less consistent between chunks. This is a per-provider tuning knob, not a universal timeout change: fast providers keep the tight default that protects UX, the slow provider gets room to actually finish.
- **Fallback timing isolation.** A fallback-chain link uses *its own* config's timing (`fbCfg.timeoutMs`/`fbCfg.idleMs`), never the primary provider's timing carried over. Applying the primary's tight budget to a fallback provider defeats the point of giving that fallback more room.
- **`model.json` schema:** any provider entry may declare `"timeoutMs": <number>` and, where the engine's reader supports it, `"idleMs": <number>`. Omitting either just means that provider uses the defaults — no engine-code change required either way. A config carrying only fast providers (e.g. a `LOCAL_FALLBACK_CONFIG` limited to Claude + Groq) can validly omit both and rely on defaults being already correct there.
- **Give slow/queued providers (`or-auto`) a materially wider budget** than fast ones in `model.json` — a `timeoutMs`/`idleMs` pair sized for Groq will false-positive-abort a healthy free-tier OpenRouter request.

---

---

## CONTENT-LEVEL VALIDATION

**This is a universal principle of the contract, not one engine's local pattern.** Confirmed independently — different code, same problem, same fix shape — across five engines: `Single-vector.html`, `dimensions.html`, `dimensions__1_.html`, `session_flywheel_engine.html` all built some version of it on their own; `fan_ramify_flywheel_engine.html` has none and that's a legitimate gap, not a counterexample (its call sites don't gate on structured JSON). Convergent, independent reinvention across that many engines is exactly the signal that something belongs in the shared contract rather than staying implicit per build.

**The principle.** Transport-level retry (soft/hard fallback) only fires on a non-2xx HTTP status. It has no visibility into whether the response *body* is usable — a model can return `200 OK` with garbled, truncated, or non-JSON text, pass straight through as a "successful" call, and fail only when a downstream parser chokes on it, with no retry attempted. This is a real, recurring gap distinct from timing — it happens even with a correctly-tuned timeout. Any call site expecting structured JSON back from a `modelChain` has this exposure, regardless of that engine's specific streaming architecture.

**The fix, in principle:** an optional `validate` callback threaded into the call function. When supplied, a chain link's response is checked before being accepted; a thrown/falsy result is treated exactly like an HTTP failure — advance to the next link in `modelChain`, then to `hardFallback`, rather than surfacing a raw parse error to the user.

```javascript
function jsonValidator(text) {
  const parsed = parseJSON(text); // existing lenient/repair-pass parser
  if (!parsed) throw new Error('Unparseable JSON from model');
  return parsed; // or `true` — engines disagree; match the specific engine's existing convention
}
```

**Two legitimate implementation shapes — choose by whether the engine streams to the UI at all:**

1. **Buffer-then-validate** (`dimensions.html`, `Single-vector.html`'s validated path): await the full response with no live rendering, then run `validate()` against the complete text. Correct default for a non-streaming engine, or the simplest correct option for any engine — there is nothing lost by buffering if there was no live typing effect to begin with.
2. **Stream-live-and-validate-concurrently** (`session_flywheel_engine.html`): render each chunk to the screen via `onChunk` as it arrives *and* accumulate the full text in parallel; run `validate()` against the accumulation once the stream completes. This preserves the live-typing UX that buffer-then-validate would sacrifice. Prefer this shape for any engine that already streams prose-like JSON-gate responses to the UI — it strictly dominates buffer-then-validate when streaming is already present, since it costs nothing extra and loses no UX.

Neither shape is "the" canonical one — pick based on whether the engine already streams. What's non-negotiable is the underlying behavior: a failed validation must be caught inside the chain-walk and treated as a chain-advance signal, not allowed to reach the caller as a raw parse error.

**Where to wire it in, and where not to — this part is universal regardless of shape:**

- Wire a validator into every call site that parses the response as structured JSON downstream — commit/extraction gates, traceability gates, confirmation probes, path-fidelity checks, or any engine-specific equivalent.
- Do **not** wire it into call sites that stream or return plain prose (deepen/revise/free-form generation) — there's nothing to validate against, and forcing a JSON check there would reject legitimate prose output.
- Do **not** wire it into the Claude Native branch. Native is a single fixed model with no chain to fall back within — a validator there has no next link to advance to, so the existing behavior (parse fails downstream, user sees the error) is already correct and simpler than adding a dead-end validation path.
- Extend the same validation into the `hardFallback` branch, not just the primary `modelChain` — a hard-fallback target's first (and possibly only) attempt should be validated exactly like any other chain link, not treated as unconditionally trusted.
- If a request still fails after every model in the chain has been content-validated and rejected, that's a meaningfully different signal than one flaky provider — it points at the prompt itself being too demanding for reliable JSON compliance across all available models, not at any single provider.
- **Genuinely optional per engine, not mandatory.** An engine whose call sites don't gate on structured JSON, or that's fine surfacing raw failures, doesn't need this at all — `fan_ramify_flywheel_engine.html` is evidence that's a valid state, not an unfinished one.

---

*v2 note: the `validate` callback is `callModel`'s `validate` option (curated mode only).*

---

## DYNAMIC PROVIDER SELECTOR

Replaces the hardcoded `<option>` list entirely. On config load:

```javascript
function renderProviderSelector() {
  var select = document.getElementById('providerSelect');
  select.innerHTML = '';
  liveModelConfig.providers.forEach(function(p) {
    var opt = document.createElement('option');
    opt.value = p.id;
    opt.textContent = p.label;
    select.appendChild(opt);
  });
  // OR specific-model sub-entries, if any, expand under the or-auto parent — same
  // expansion logic as the prior patch, now sourced from provider metadata for
  // dotColor/standaloneOnly instead of a hardcoded check.
}
```

`DOT_COLORS` as a hardcoded object is retired — `updateProviderDot()` reads `dotColor` off the resolved provider's config entry instead.

---

**Picker engines:** when `model-catalog-panel` is in use, the header provider dropdown is replaced by a lane button (Lanes mode) or removed in favour of per-stage model chips (Panel mode). A dropdown beside a picker recreates the two-path conflict, so there is exactly one place a model is chosen; the one exception is the catalog skill's matrix variant (A3d), where an engine that already has a second axis of work keeps its curated Run and provider selector and adds a separate `Fan out (n)` button for lanes. The provider dot, from `dotColor`, lives inside whichever control remains.

---

## DYNAMIC DRAWER KEY ROWS

Replaces the hardcoded `groqKey` / `openrouterKey` `<div class="drawer-field">` blocks. On config load:

```javascript
function renderDrawerKeyRows() {
  var container = document.getElementById('drawerKeyRows');
  container.innerHTML = '';
  liveModelConfig.providers.forEach(function(p) {
    if (!p.requiresKey) {
      // Native / no-key providers still get a note row, not an input — mirrors
      // the existing "No key needed — platform routes natively" pattern.
      container.appendChild(buildNativeNoteRow(p));
      return;
    }
    container.appendChild(buildKeyInputRow(p)); // label, placeholder, storage name, save button, optional keyNote — all from p
  });
}
```

**What is explicitly NOT dynamic, restated for clarity:** the key *value* the user types into that row. It is read from the input, written to `localStorage` under `hek_{p.keyStorageName}`, and read back from `localStorage` on every API call — exactly as before. `model.json` never carries, receives, or has any path to a real key. The dynamism is scoped entirely to *whether the row exists and what it says* — not to the secret itself.

---

**v2:** rows read their current value through `getKey` (so a legacy slot pre-fills), and write through `setKey`. Engines with a model picker use `renderKeyRows()` from `model-catalog-panel` (A5), which does exactly this.

---

## CONFIG: LIVE / LOCAL FALLBACK BADGE

Behavior unchanged: fetch success plus a valid config gives `Config: Live` (green); anything else holds `LOCAL_FALLBACK_CONFIG` and reads `Config: Local Fallback`. The fallback is now the floor (Claude Native for artifacts, Groq `gpt-oss-120b`, and the OpenRouter free router), defined in the Model Core block.

**Validation (`isValidConfig`) requires:** `providers` is a non-empty array; every entry has a unique `id` and a `label`; **at most one** entry has `native: true`; and **at least one provider is usable in the current context** (Native inside claude.ai, otherwise an OpenAI-compatible provider with an endpoint that is not standalone-only in an artifact). Malformed config is treated as fetch failure, never partially adopted. v1 required exactly one native entry; that blocked standalone-only engines, which never route Native.

---

## RETROFIT PROCEDURE FOR EXISTING ENGINES

**Step 0: classify the engine.**

| Class | Signs | Work |
|---|---|---|
| A. Hardcoded hybrid | literal provider branches, fixed `<option>`s, hardcoded model chain | full retrofit, steps 1 to 5 |
| B. Config-driven with its own copy | fetches `model.json`, but carries its own call layer and stream reader | delete the duplicate, keep the UI |
| C. Self-contained | provider list and defaults in a constant, own key names, own stream loop | replace the constant with config; migrate keys through `LEGACY_KEY_SLOTS` |

**Steps**

1. Paste the Model Core block; set the three CONSTANTS (`ENGINE_NAME`; the canonical URL stays as is; `LEGACY_KEY_SLOTS` if the engine stored keys under its own names).
2. Delete the engine's own provider constant, config loader, key getter, request builder, stream reader and `callAI`. Route every model call through `callModel`: curated mode for a dropdown engine, strict mode for lanes and panels.
3. Render the selector and drawer key rows from config (sections above). Remove any hardcoded `<option>`, key `<div>`, or `DOT_COLORS`.
4. If the engine has a picker, seed lanes or panels from `defaultLanes()`; remove any list of default slugs from the HTML.
5. Optional and incremental: thread `timeoutMs` and `idleMs` through (already done by `callModel`); add `validate` at JSON-gate call sites only.
6. Check: with the network blocked the engine runs on the floor and the badge reads Local Fallback; a bad key surfaces a key message, not "all routes failed"; a strict lane never shows a model other than the one requested, except a visible `served:` tag.

**Known engines**

- *fragment-to-angles* (A): hardcoded routing becomes config plus curated `callModel`; keeps its own panels.
- *sequential-pipeline-v5* (B): Panel mode already; drop its duplicate config and call code, call strict `callModel`.
- *capsule-relay-loop-engine-v2* (C): replace its `PROV` constant with config; keys move from its own `rl.key.*` slots via `LEGACY_KEY_SLOTS`; gains the retry, system fold, served tag and reasoning liveness its stream loop lacks.
- *osho-refraction-standalone* (B): Lanes mode already; replace its `DEFAULT_SLUGS` list with `defaultLanes()`.
- *prompt-generator-engine-v2* (B): retrofitted as the Lanes matrix test bed (3 presets × lanes, curated Run kept). Its config URL had been a placeholder path, so it never read `model.json` and ran on a stale built-in copy.

---

## MODEL.JSON CHANGE CHECKLIST

- `defaultLanes` entries reference provider ids that exist and slugs those providers serve; `model_aliases` values are existing ids.
- At most one `native: true`; every entry has `id` and `label`; OpenAI-compatible entries have `endpoint` and `requestFormat: "openai-chat"`.
- `timeoutMs` and `idleMs` are numbers; give slow providers (`or-auto`) a wider pair than fast ones.
- Commit, wait a few minutes for the CDN, reload one engine and confirm the badge reads `Config: Live`.
- Never put `openrouter/auto` in a chain, a default or an alias: it is OpenRouter's paid Auto Router, the `:free` suffix does not restrict it, and it will bill. The free router is `openrouter/free`.
- Text models only: no vision or image-generation slugs in any chain.
- Never put a key, token or secret in this file.

---

## MIGRATION NOTE: RELATIONSHIP TO EXISTING CONTRACTS

v1 said this skill's pattern wins wherever it conflicts with `hybrid-engine-contract` and `ui-contract`, and deferred trimming those files. In this release the trims are made, so the priority clause is no longer needed:

- **hybrid-engine-contract:** its API ROUTING and OPENROUTER MODEL MAP sections are replaced by "Providers and models: delegated to the Model Core" (a thin `callAI` wrapper over `callModel`); its provider selector is rendered from config; `OR_MODEL_MAP`, `GROQ_MODEL_CHAIN` and the engine-local `readStream` are retired; the stale `llama-3.3-70b` dropdown example is gone.
- **ui-contract:** Constraints 06, 07, 12, 13 and 18B are patched (config-driven key rows, 400 px catalog drawer, lane button, `defaultFor`, per-provider timing, `dotColor`) and Constraint 25 (Model delegation) is added.
- **model-catalog-panel v3.0:** re-scoped to selection only (Lanes and Panel modes, single-path default, extras opt-in), consuming this Core API.
- **model-catalog-panel v3.2:** catalog GET hardening only (`catalogHeaders`, instant provider tabs, in-flight guard). No Core API change: `headersFor` stays as it is, scoped to chat requests, and its comment now says so.

Engines built before this release keep working: they ignore the new `model.json` fields and run on their own code until retrofitted (see RETROFIT PROCEDURE).

---

## QUICK REFERENCE

```
CONTRACT         : model-config-contract v2 = Model Core (config + keys + callModel)
IMPLIED BY       : hybrid-engine-contract (new builds); explicit /model-config for retrofits
OPTIONAL LAYER   : model-catalog-panel (Lanes | Panel) consumes the Core API, never re-implements it
FLOOR            : Groq openai/gpt-oss-120b + OpenRouter openrouter/free; data = defaultLanes, mirrored in LOCAL_FALLBACK_CONFIG
CONFIG SOURCE    : CANONICAL_CONFIG_URL (fixed); cache-busted fetch once per load; CDN lag of a few minutes
CONFIG SHAPE     : providers[] + native_model + defaultLanes (new) + model_aliases (new) + or_specific_models (deprecated, empty)
CONFIG VALIDATE  : non-empty, unique id+label, at most one native, at least one provider usable in context
CALL LAYER       : callModel(opts): curated (chain + fallbacks + validate) | strict (opts.model, no fall-through)
HARDENING        : 429 retry once, system fold, fatal 401/402/403/413, 404 hint, empty-reply hint, served tag, reasoning liveness
TIMING           : per-provider timeoutMs/idleMs, defaults 15000/3000; fallback link uses its own timing
KEYS             : hek_{keyStorageName} client-side only; LEGACY_KEY_SLOTS read-only fallback; clear both
SELECTOR         : rendered from providers[]; replaced by lane button / panel chips when a picker is present
HARDCODED FOREVER: Claude Native's header-omission branch in buildRequest
CONTENT VALIDATE : optional validate in curated mode; JSON gate call sites only; never prose, never Native
RETROFIT         : classify A/B/C, paste core, delete duplicates, route through callModel, seed from defaultLanes()
OUTPUT           : updated .html per engine + shared model.json
```
