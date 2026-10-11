# Cognitive Shift Engine v7 — Netlify Deployable Bundle

Drag-and-drop this folder onto Netlify (or link it as a Git site) and the engine runs publicly with **zero visitor setup**: the operator's API keys live server-side, visitors never see or paste one, and a visitor-pasted key still works as automatic fallback.

## Contents

- `index.html` — the engine (v7 + proxy-first routing; Settings/paste-key drawer retained as the fallback layer)
- `netlify.toml` — publishes `.`, registers functions, maps `/api/groq` and `/api/openrouter`
- `netlify/functions/groq.js` — proxy for Groq (`GROQ_API_KEY`)
- `netlify/functions/openrouter.js` — proxy for the OpenRouter route (`OPENROUTER_API_KEY`)

## Operator setup (post-deploy)

1. Deploy this folder.
2. Go to **Netlify → Site settings → Environment variables** and add:
   - `GROQ_API_KEY` = your Groq key (`gsk_…`)
   - `OPENROUTER_API_KEY` = your OpenRouter key (`sk-or-…`)
3. **Redeploy the site** (Deploys → Trigger deploy). Netlify Functions bind env vars at **deploy time, not live** — a key added after the last deploy has zero effect until a fresh deploy runs. This is the #1 cause of "I set the key but visitors are still asked to paste one."

No key ever goes in any file in this folder — not `.env`, not a config fallback, nowhere.

## How it behaves (no rebuild between states)

- **Server key healthy:** banner hidden, every lens routes through `/api/*` on the operator's key.
- **No server key:** engine works if a visitor pastes their own key in ⚙ Settings (stored only in their browser).
- **Server key exhausted/failing (429/5xx):** that request auto-falls back to the visitor's key; the next request retries the proxy automatically (self-healing, nothing sticks).

## Debugging ("visitors still have to paste a key")

1. Fresh deploy after the env var change? If not, redeploy.
2. Env var name matches `process.env.X` exactly (`GROQ_API_KEY`, `OPENROUTER_API_KEY`)?
3. Network tab: `/api/groq` on page load — 404 means the function/redirect isn't deployed; anything else means the proxy path is live.
4. Real request 429/5xx = shared-key limit or upstream outage — fallback doing its job; self-resolves.

## Local development

`netlify dev` serves `index.html` with working `/api/*` functions (reads env vars from a local `.env` you create yourself — never commit it).
