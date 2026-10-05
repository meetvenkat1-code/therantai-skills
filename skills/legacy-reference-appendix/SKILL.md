---
name: legacy-reference-appendix
description: >
  Subordinate resource file, not an independently invokable skill. Holds the
  pre-config-driven (pre-model-config-contract) provider-routing code that
  hybrid-engine-contract used to carry inline as commented-out reference
  blocks — moved here so the main build-DNA file stays lean and actually
  readable in full before every build, per its own "read in full" mandate.
  Historical reference only. Never a build path for a new engine. Never
  invoked directly and carries no trigger phrase of its own — nothing in the
  three-skill stack should point here except when someone is hand-porting a
  pre-2026-08 engine and wants to see the exact shape it used to have before
  model-config-contract existed. For any current build, including one
  declaring PROVIDER_SOURCE: hardcoded, use hardcoded-provider-panel-SKILL.md
  instead — that file is the authoritative, current implementation for the
  hardcoded-provider path. This file is not that path.
metadata:
  scope: subordinate
  invokable: false
  triggers: []
  parent_skill: hybrid-engine-contract
  companion_stack: [hybrid-engine-contract, ui-contract, model-config-contract]
  phase: reference-only
  version: "1.0"
---

# Legacy Reference Appendix — Pre-Config-Driven Provider Code

(Companion resource to `hybrid-engine-contract`. This is not a fourth build-time skill and has no trigger of its own. It exists solely so the two large "REFERENCE ONLY" commented-out blocks that used to sit inline inside `hybrid-engine-contract-SKILL.md` — bulking up a file meant to be read in full before every build — live somewhere, without being read every time. If you are building or retrofitting an engine today, you almost certainly want `model-config-contract-SKILL.md` (config-driven default) or `hardcoded-provider-panel-SKILL.md` (the `hardcode` exception), not this file.)

## Why this exists

Before `model-config-contract` was split out, `hybrid-engine-contract` carried the full per-provider `if/else` routing chain, the OpenRouter model map, and the context-aware provider-selector code directly in its body. When the provider/model layer became config-driven, that code was superseded but kept as commented-out reference — inline, inside the file every build has to read in full. That's dead weight in the one file explicitly designated as "read before writing any code." This appendix is where that dead weight now lives: still available for anyone hand-porting a genuinely old engine, but no longer something every new build has to scroll past.

## REFERENCE 1 — Pre-config-driven `callAI()` routing (superseded)

Kept for retrofitting engines still on `PROVIDER_SOURCE: hardcoded` from before the companion file existed. Do not copy into new builds. For a new hardcoded-provider build, use `hardcoded-provider-panel-SKILL.md` instead — it is the current, authoritative implementation for that path, not this historical shape.

### OpenRouter — model map + helpers

```javascript
// ── OpenRouter: one route, one stable slug — no named models, no churn ──
// OR is TEXT-ONLY in every Therantai engine. Vision path is retired.
const OR_MODEL_MAP = {
  'or-text': 'openrouter/free'  // Free Models Router — dynamically picks a live free text model
};

function isOpenRouterProvider(p) { return p && p.startsWith('or-'); }
// isVisionModel RETIRED — OR is text-only. Do not re-introduce.
```

OR routing rule (historical): OpenRouter routed exclusively through the Free Models Router (`openrouter/free`) — one slug, no named models. Text-only: no image payloads, no vision logic. NEVER `openrouter/auto` — that's the paid Auto Router and it bills. Artifact routing rule: OpenRouter has no CORS proxy inside claude.ai — block `run()` and show the inline OR artifact notice when `isOpenRouterProvider(provider)` and `window.self !== window.top` are both true. Claude Native was the only artifact-safe path.

### `callAI()` — full three-provider if/else chain

```javascript
async function callAI(systemPrompt, userMessage, onChunk, imageData, imageMime) {
  const provider = getSelectedProvider();

  if (provider === 'claude') {
    const res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01',
        'anthropic-dangerous-direct-browser-access': 'true'
        // NO Authorization header — intentional. Platform proxies it.
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

  } else if (provider === 'groq') {
    // ── Groq — model-family fallback, three tries, label never changes ──
    // Try 1: gpt-oss-120b. Try 2 (soft, same provider): gpt-oss-20b on 429/5xx.
    // Try 3 (hard, cross-provider): openrouter/free if Groq itself is dead/404/deprecated.
    // GROQ_MODEL_CHAIN is canonical — do not hardcode model strings elsewhere.
    const GROQ_MODEL_CHAIN = ['openai/gpt-oss-120b', 'openai/gpt-oss-20b'];
    let res, lastErr;
    for (const model of GROQ_MODEL_CHAIN) {
      try {
        res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${getKey('groq')}` },
          body: JSON.stringify({
            model,
            stream: true,
            messages: [{ role: 'system', content: systemPrompt }, { role: 'user', content: userMessage }]
          })
        });
        if (res.status === 429 || res.status >= 500) { lastErr = `groq:${res.status}`; res = null; continue; }
        if (!res.ok) { lastErr = `groq:${res.status}`; res = null; continue; } // 404/dead endpoint → hard fallback
        break; // success — stop trying further Groq models
      } catch (e) { lastErr = e; res = null; }
    }
    if (res) {
      await readStream(res, 'openai', onChunk);
    } else {
      // Hard fallback — Groq lane is fully unavailable. Route to OpenRouter's free router.
      // Silent to the user: dropdown still reads "Groq · gpt-oss-120b".
      const orKey = getKey('openrouter');
      if (!orKey) throw new Error(`Groq unavailable (${lastErr}) and no OpenRouter key set for fallback.`);
      const fbRes = await fetch('https://openrouter.ai/api/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${orKey}`,
          'HTTP-Referer': 'https://therantai.engine',
          'X-Title': 'Therantai Hybrid Engine'
        },
        body: JSON.stringify({
          model: 'openrouter/free',
          stream: true,
          messages: [{ role: 'system', content: systemPrompt }, { role: 'user', content: userMessage }]
        })
      });
      await readStream(fbRes, 'openai', onChunk);
    }

  } else if (isOpenRouterProvider(provider)) {
    // ── OpenRouter — text-only ──────────────────────────────────
    // Standalone only. No CORS proxy inside claude.ai — block at run() before reaching here.
    // Text-only: no image payload, no vision logic. OR_MODEL_MAP['or-text'] = 'openrouter/free'.
    const orKey = getKey('openrouter');
    if (!orKey) throw new Error('OpenRouter key not set. Open Settings (⚙) and save your sk-or- key.');

    const modelId = OR_MODEL_MAP[provider] || 'openrouter/free';

    const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${orKey}`,
        'HTTP-Referer': 'https://therantai.engine',  // app attribution on openrouter.ai
        'X-Title': 'Therantai Hybrid Engine'
      },
      body: JSON.stringify({
        model: modelId,
        stream: true,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userMessage }
        ]
      })
    });
    await readStream(res, 'openai', onChunk);  // OR uses OpenAI SSE format — same parser as Groq
  }
}
```

## REFERENCE 2 — Pre-config-driven provider selector + context-aware default (superseded)

Kept for retrofitting engines still on `PROVIDER_SOURCE: hardcoded` predating the companion file.

Default was set programmatically on load — never hardcoded in HTML:

```javascript
const isArtifact = window.self !== window.top;
const defaultProvider = isArtifact ? 'claude' : 'groq';
document.getElementById('providerSelect').value = defaultProvider;
```

HTML selector — two optgroup structure, no `selected` attribute on any option. Extended group (OpenAI/Gemini/LM Studio) is retired — do not include:

```html
<select id="providerSelect">
  <optgroup label="── Core ──────────────">
    <option value="claude">Claude · Sonnet 4.6</option>
    <option value="groq">Groq · llama-3.3-70b</option>
  </optgroup>
  <optgroup label="── OpenRouter ─────────">
    <option value="or-text">OR · Free Router (text)</option>
  </optgroup>
</select>
```

Warning banner logic (historical): Artifact + Claude selected → no banner. Artifact + any `or-` provider → OR artifact notice, block `run()`. Standalone + `or-` provider + no `hek_openrouter` key → key warning banner. Standalone + Groq + no `hek_groq` key → key warning banner. Any provider + key stored → no banner.

```javascript
function getKey(provider) { return localStorage.getItem(`hek_${provider}`) || ''; }
function storeKey(provider, val) { localStorage.setItem(`hek_${provider}`, val); }
function getSelectedProvider() { return document.getElementById('providerSelect')?.value || 'claude'; }
// OpenRouter key stored as hek_openrouter
```

Gear drawer key rows (historical): Claude → read-only "No key needed — platform routes natively". Groq → password input, placeholder `gsk_…`. OpenRouter → password input, placeholder `sk-or-…` + inline orange note: "Standalone only — OR has no CORS proxy inside claude.ai".

---

Do not merge either reference block back into `hybrid-engine-contract` or `model-config-contract`. Do not promote this file to an independently-triggerable skill. If you find yourself reaching for this file on a *new* build, stop — you want `model-config-contract` (default) or `hardcoded-provider-panel-SKILL.md` (the `hardcode` exception) instead.
