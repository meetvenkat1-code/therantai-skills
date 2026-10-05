---
name: openrouter-free-path-integration
description: Complete, stable pattern for integrating the OpenRouter free path (`openrouter/free`) into any hybrid HTML engine. Includes automatic routing, manual model selection, conditional UI dropdown pattern (secondary + tertiary), defensive coding practices, recommended free models, and lessons from real implementation friction. Allows upgrading older hybrid engines with robust OpenRouter free tier support.
triggers:
  - /openrouter-free-path
  - integrate openrouter free path
  - apply openrouter integration skill
  - openrouter free path
category: Hybrid Engine Integration > Provider Routing
scope: global
version: 1.0
date: 2026-07-11
author: meet.venkat1@gmail.com
---

# OpenRouter Free Path Integration Skill

**Core philosophy:** individual free models on OpenRouter are unstable (frequent 404s/rate limits) — automatic routing should primarily use `openrouter/free`, with manual control via a "Specific Model" option.

## Final architecture
| Mode | Model Used | Description | Status |
|---|---|---|---|
| Auto Router (OpenRouter) | `openrouter/free` | auto-selects best available free model | Recommended |
| Auto Text Fallback | `openrouter/free` | same, for consistency | Stable |
| Specific Model | user selected | manual pick from curated list | Available |

## UI pattern (required)
On selecting OpenRouter from the main provider dropdown: show a second dropdown (`Auto Router (OpenRouter)` / `Auto Text Fallback (Smart)` / `Specific Model`); if Specific Model chosen, show a third dropdown of curated free models. Secondary/tertiary dropdowns appear only when OpenRouter is active. Don't modify the existing header, provider pills, or gear drawer — maintain visual consistency.

## Implementation logic
```javascript
if (provider === 'openrouter') {
    let modelId;
    if (orRoutingMode === 'auto-openrouter' || orRoutingMode === 'auto-text-fallback') {
        modelId = 'openrouter/free';
    } else if (orRoutingMode === 'specific' && selectedOrModel) {
        modelId = selectedOrModel;
    } else {
        modelId = 'openrouter/free';
    }
    // Proceed with OpenRouter API call using modelId
}
```

## Recommended models (Specific Model dropdown)
`meta-llama/llama-4-maverick:free` (Vision+Text) · `google/gemma-4-31b-it:free` (Vision+Text) · `qwen/qwen2.5-vl-72b-instruct:free` (Vision) · `meta-llama/llama-4-scout:free` (Text) · `z-ai/glm-4.5-air:free` (Text) · `nvidia/nemotron-3-super-120b-a12b:free` (Text)

## Key constraints
1. Stability first — no complex client-side fallback logic around individual free models.
2. UI Contract compliance — new controls conditional, non-breaking.
3. Defensive coding — always `Array.isArray()` check before `.join()` on fields like `weaknesses`; never reference `imageData`/`imageMime` unless explicitly passed.
4. Clear error messages when the OpenRouter key is missing or requests fail.

## Friction resolved
| Friction | Solution | Lesson |
|---|---|---|
| Frequent 404s from specific free models | Use `openrouter/free` for auto modes | Free models are unreliable |
| ReferenceError extending `callAI` | Optional, guarded new parameters | Defensive coding essential |
| Inconsistent JSON from Evaluator | Safe array checks before `.join()` | Free models return weak JSON |
| Over-engineering too early | Start with `openrouter/free`, add complexity later | Stability > cleverness |

## Future improvements (ascent)
Proper multi-model retry in auto-text-fallback mode. Re-introduce vision support with guards. Display which model was actually selected in auto mode. Loading indicator while auto mode resolves.
