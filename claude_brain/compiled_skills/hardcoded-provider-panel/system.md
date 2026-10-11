---
skill: hardcoded-provider-panel
source_file: skills/hardcoded-provider-panel/SKILL.md
source_sha: 61fd24751a2ada2f58e7ead07323b681f5b853162da001440f7630dce40110d9
---

# hardcoded-provider-panel (skill behavior, verbatim)

```skill:body
# Hardcoded Provider Panel — Retrofit Instructions

(Companion resource to the three-skill stack: `ui-contract` + `hybrid-engine-contract` + `model-config-contract`. Invoke all three as normal. This is not a fourth skill — it's the declared override inside `model-config-contract`'s own retrofit path: "Per-engine override is still permitted for the rare engine whose provider set genuinely diverges" (see RETROFIT PROCEDURE step 1). This file has no trigger of its own; it is reached only via `model-config-contract`'s `hardcode` trigger.)

## When this applies

Use only when an engine's provider set genuinely diverges from the canonical config — offline use, fixed vendor set, no dependency on the GitHub-hosted `model.json` wanted. Not a default. Not a style preference.

## Declare at top of build, before any panel code fires

```js
window.EnginePanels = {
  library: false,
  importExport: false,
  settings: true
};

window.ProviderConfig = {
  source: 'hardcoded',        // 'config' | 'hardcoded'
  providers: [
    // name the fixed list explicitly — no fetch, no CANONICAL_CONFIG_URL
    { id: 'claude', label: 'Claude Native', native: true },
    { id: 'groq',   label: 'Groq' },
    { id: 'or-auto', label: 'OpenRouter' }
  ]
};
```

Record the reason inline as a comment — not optional:

```js
// PROVIDER_SOURCE: hardcoded
// REASON: <why this engine diverges from config-driven default>
```

## What changes vs. the config-driven default

- `model-config-contract`'s fetch/validate/fallback logic (`CANONICAL_CONFIG_URL` fetch, `providers` array validation, `Config: Live / Local Fallback` badge) does not run. No badge is rendered at all in this mode — there is nothing to report live/fallback status on.
- The provider list is written directly into `window.ProviderConfig.providers` at build time. Changing providers later means editing this HTML file, not editing `model.json` — that's the accepted tradeoff of choosing this branch.

## What does NOT change — applies identically in both branches

- **Claude-native carve-out** (`model-config-contract`, WHAT STAYS HARDCODED section): endpoint (`https://api.anthropic.com/v1/messages`), headers (no Authorization), and model string stay hardcoded in the adapter in code, regardless of `source`. Never make this configurable "for consistency" — it's the entire reason native routing exists.
- **Dot-color table** (fixed: Claude / Groq / OR `#f97316` for all `or-` prefixed routes) — `ui-contract` Constraint 18B (Provider Dot Standard). Unchanged.
- **Key storage convention** — `localStorage` under `hek_{provider}` (or `hek_{keyStorageName}` if declared) — unchanged.
- **OR artifact-blocking rule** — block `run()` inside iframe context for any `or-` provider, surface the notice — unchanged.
- **Panel mechanics** — collapsible overlay, `EnginePanels` flag model, persistence layer (Constraint 22/23) — unchanged. The provider source is the only variable; panel chassis is constant.

## Explicitly avoid

Do not restate dot logic, key convention, or panel mechanics inside this doc's engine implementation "for completeness" — those live once, in `ui-contract`, and apply the same regardless of `source`. This doc only ever holds the one thing that's actually different: the provider list source and the reason it diverged.

Keep this as a standing companion file, resolved automatically by `model-config-contract`'s `hardcode` trigger — no manual pasting required once filed in the ecosystem. Do not merge into `ui-contract` or `model-config-contract`; do not promote this to an independently-triggerable skill.
```
