---
name: prompt-engine-interface-contract
description: A domain-specific interface and logic contract for building prompt-testing, prompt-management, and prompt-comparison tools. Encodes resolved friction from production builds across panel architecture, active prompt orientation, scratchpad modal, copy mechanism, stream safety, and design constraints. Invoke when building any tool whose primary purpose is testing or managing system prompts.
triggers:
  - "prompt engine"
  - "prompt tester"
  - "prompt library"
  - "system prompt manager"
  - "Apply Prompt Engine Interface Contract"
scope: domain-specific
registry: Therantai Skill Library
version: "1.0"
date: 2026-06
author: meet.venkat1@gmail.com
---

# SKILL — Prompt Engine Interface Contract

Complete interface/logic contract for any tool testing, saving, comparing, or managing system prompts. Governs architecture, layout, interaction, copy behavior — no re-explanation needed once invoked.

**Core tension solved:** a single textarea can't scale to prompt comparison — users need many named prompts, any one loadable as active context, fired against, output visible, without losing orientation or rebuilding state each run.

## Station 1 — Use-case-first gate
Never accept spatial descriptions as the starting point. Before any layout decision: core use case (what beats a plain textarea?), primary action loop (what, in what sequence, every session?), non-negotiables (what must never break/be lost?). Only then release layout to model judgment. Trigger: the moment the user describes *where* before *what* — surface this gate immediately.

## Station 2 — Panel architecture
```
LEFT PANEL  → Prompt Library (saved, named, persistent)
RIGHT PANEL → Session History (current session only)
```
Never swapped — library is a reference object (primary side), history is a review object (trailing side). Both slide from their edge; one at a time, opening one closes the other. Single backdrop closes whichever is open. Toggle buttons in header Zone B, flanking the provider selector.

## Station 3 — Prompt Library (left panel)
Pre-load 5+ default prompts across distinct registers (Neutral, Analytical, Depth-Psychological, Socratic, Creative). Each card: name (prominent) + preview (~100 chars, muted, 2-line clamp). Click card body → selects as active (accent border + ✓). Pencil icon → scratchpad modal (edit). `＋` at panel bottom → scratchpad modal (new). Active selection + all prompts persist in localStorage — never session-only.

## Station 4 — Active prompt orientation (mandatory)
A named chip above the input bar, non-negotiable: `[ ⚡ Jungian Analyst ▸ ]` — always visible, zero-click orientation. Click → opens Library. No selection → muted italic "No system prompt selected — click Library to choose one." User must always know the active prompt without opening any panel.

## Station 5 — Scratchpad modal
Full overlay modal always — never inline, never a popover.
```
HEADER: "New System Prompt" / "Edit Prompt"  [✕]
BODY: PROMPT NAME [full-width input] / SYSTEM PROMPT [textarea, min 260px, monospace]
FOOTER: [Delete] (edit mode only)  [Cancel]  [Save Prompt]
```
Esc closes. Save → update library, re-render cards, set active if new. Delete → remove from library, clear active if it was deleted.

## Station 6 — Copy mechanism (artifact context)
Never `navigator.clipboard.writeText()` inside iframe/artifact contexts — claude.ai's runner is cross-origin, Clipboard API is blocked, silent failure is worse than no copy.
```
[⎘ Copy] → reveals a pre-selected <textarea> below output header, raw response text
           Label: "SELECT ALL → Ctrl+C / Cmd+C" · textarea.select() on reveal · Copy again collapses
```
No clipboard API dependency; one Ctrl+C from reveal to copy; identical in artifact and standalone.

## Station 7 — Input bar
```
ACTIVE PROMPT CHIP ROW: [ ⚡ Prompt Name ]  or muted "no prompt"
USER INPUT ROW: [textarea] [Clear] [Run →]
```
System prompt textarea permanently removed from here — the library replaces it entirely. Enter runs, Shift+Enter newlines. Auto-resize to ~90px then scroll. Clear resets output + input only, never library/active prompt.

## Station 8 — API routing
| Provider | Default Model | Key Storage |
|---|---|---|
| Claude | claude-sonnet-4-6 | Auto-routed in claude.ai — no key |
| Groq | llama-3.3-70b-versatile | `hek_groq` |
| OpenAI | gpt-4o | `hek_openai` |
| Gemini | gemini-1.5-pro | `hek_gemini` |
| LM Studio | local | `hek_lmstudio` (base URL) |

Default: `claude` in artifact, `groq` standalone. Missing key → warn banner + gear panel. Keys under `hek_{provider}`, never hardcoded.

## Station 9 — Stream safety (three-layer)
Every streaming call: `[DONE]` sentinel (immediate) · `stream.done` flag (natural end) · idle timer (3000ms reset per chunk, fires `finalize()` on silence) · hard timeout (20000ms absolute). `finalize()` idempotent, guarded by a `done` boolean — first call only executes.

## Station 10 — Design constraints
Typography: Space Grotesk (heading/identity) + system-ui (body) — Syne deprecated (descender clipping at 700+ weight in flex/grid). Zone A: compressed identity mark only, never repeats H1 verbatim ("∆PE" not "Prompt Engine"). Zone C: "crafted by" lowercase italic + email, header only, no footer. Palette: `#0a0a0f` void / `#12121a` surface / `#1a1a28` elevated / `#2a2a3d` border. Accent `#7c6ef5`; provider dots red/green/blue/purple/amber matching identity. Chip dots (library): left-side glowing pulse, unique accent per entry. Tab dots (history): right-side small pulse, matched to tab accent — never interchangeable with chip dots.

## Invocation
Paste as context: "Apply the Prompt Engine Interface Contract and build [description]." Or mid-session: "Apply the Prompt Engine Interface Contract to what we're building." All constraints active from Station 1 forward — no re-explanation needed.
