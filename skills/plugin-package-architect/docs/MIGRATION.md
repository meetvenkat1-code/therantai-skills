# MIGRATION — custom-gpt-package V1.0 → plugin-package-architect V2.0.0

## Source audit (V1 baseline)

- Supplied archive: `custom-gpt-package.zip`, containing exactly one file, `SKILL.md` (4,275 bytes).
- SHA-256 of V1 `SKILL.md`: `904390f495356c869d9863b0ae1c4aa4386f419c7269ca317e74434843c7541f`.
- Name `custom-gpt-package`, version 1.0, dated 2026-07-02, scope global, author meet.venkat1@gmail.com.
- Triggers (7): `/custom-gpt-package`, "build a custom GPT package", "turn this into a custom GPT", "package this for ChatGPT", "custom GPT from this spine", "make a custom GPT out of this", "render this for the GPT builder".
- Workflow: single-pass render of a spine, idea, or prompt into a five-section package. No interview unless source is genuinely missing something required.
- Output order: NAME, DESCRIPTION, INSTRUCTIONS (IDENTITY, INPUT HANDLING, MODE SELECTION if multi-mode, TONE, OUTPUT RULES, ANTI-DRIFT BLOCK), CONVERSATION STARTERS (3–4), CAPABILITIES TABLE (all Off by default).
- Hard constraints: anti-drift block mandatory in every package; soft complexity ceilings warned-not-blocked; capabilities enabled only when the core function requires them, with a one-line reason; delivery as one block, no preamble or summary.
- Upstream references: `core-extractor` and `spinal-column` (named, not supplied).
- No modules, historical instructions, or capabilities were added or inferred beyond this file. Filename variants of this skill are treated as one version (per the work order).

## Architecture comparison

| Aspect | V1 `custom-gpt-package` | V2 `plugin-package-architect` |
|---|---|---|
| Deployment targets | One: ChatGPT Custom GPT | Four: PLUGIN_CREATOR (default), PORTABLE_PLUGIN, SKILL_ONLY, CUSTOM_GPT_LEGACY |
| Pipeline | Implicit single render step | Explicit four stages: Source Interpretation, Engine Specification, Target Compilation, Anti-drift and Dependency hardening |
| Output contract | Five fixed sections | Per-target: 15-section spec / plugin tree / SKILL.md / legacy five sections |
| Source discipline | "Note the assumption inline" | Every item tagged SPECIFIED / INFERRED / DEFAULT / UNRESOLVED; contradictions reported |
| Anti-drift | One universal block, plain-prose lock by default | Same mandatory block, rebuilt as a source-dependent invariant system with four rule categories |
| Capabilities | Custom GPT table (Browsing, Canvas, Image Gen, Code Interpreter, Actions) | Least-privilege dependency model: Required / Optional / Unavailable / Unsupported across 10 capability kinds |
| Prompt-injection handling | Not addressed | Source treated as data; embedded instructions never executed |
| Routing | Triggers only | Explicit precedence rules; legacy aliases retained |
| Validation | None | 12 designed behavioral tests plus executed static checks |
| Packaging | Copy-paste text | Plugin ZIP, source/backup ZIP, `.skill` file, checksums |
| Platform claims | Assumes Configure tab | Only Target 4 assumes it; Targets 1–3 do not |

## Preserved behaviors

One-pass operation with no interview unless essential; source-driven tone, role, and output; mandatory anti-drift block; deterministic output contracts; explicit input bounds and edge behavior; multi-mode handling when the source needs it; domain independence; soft ceilings as warnings; no unsolicited functional expansion; all 7 V1 triggers; the full V1 five-section structure and its eight anti-drift items (reachable via Target 4); the upstream relationship to `core-extractor` and `spinal-column` (conceptual only, internals not assumed).

## Intentional behavioral changes

1. **Default target changed.** Unqualified V2 triggers produce a Plugin Creator spec. V1 triggers still produce the Custom GPT package. This is a change only for the new trigger phrases.
2. **Plain-prose lock is now source-dependent.** V1 applied it universally unless the source required structure. V2 applies it only when the source calls for prose or specifies no structure, and never imposes it on engines whose output is structured (Mermaid, ASCII, tables). Inside Target 4 the V1 rule is kept as written.
3. **No "no preamble" rule for non-legacy targets.** V1's "no preamble, no summary" applies in Target 4. Targets 1–3 add an Assumptions and Deployment Notes section, because a plugin spec that hides its assumptions is not reviewable.
4. **Capabilities table replaced** in Targets 1–3 by a dependency architecture. Retained in Target 4.
5. **New protections:** injection resistance, no fabricated tools or results, contradiction reporting, no leakage of context between unrelated conversions.
6. **Anti-drift is described as a behavioral control, not a guarantee.** V1 did not say so.

## Compatibility constraints

- V2 cannot guarantee that a slash command works literally; only the host decides. Natural-language triggers are the portable path.
- Plugin packaging conventions were verified against OpenAI's published pages on 2026-10-26 through a summarizing fetch tool; the submission page was partly truncated (details in `references/verified-conventions.md`). Re-verify before submission.
- The portable ZIP has no logo or icon assets. The documented requirements for Codex submissions include `logo` and `composerIcon`; this package does not claim submission readiness. It is a skills-only plugin with no MCP server, no apps, and no hooks.
- If you load both V1 and V2 skills simultaneously, legacy phrases may match either description. V2's precedence rules route legacy aliases to Target 4; to avoid duplicate-trigger ambiguity, deactivate V1 once V2 is installed, or keep V1 only as a rollback copy.
- `core-extractor` and `spinal-column` were not supplied to the original build session and are not modified or reimplemented.

## Traceability map (V1 → V2)

| V1 element | V2 location |
|---|---|
| Frontmatter description and triggers | SKILL.md frontmatter; Section 1 |
| "Don't interview first" | Preamble paragraph; Section 7 |
| "Why" (drift rationale) | Preamble "Why" |
| Five-section output | Section 4, Target 4 |
| IDENTITY / INPUT HANDLING / MODE / TONE / OUTPUT RULES | Section 3 (Stage B); Target 4 |
| Anti-drift block (8 items) | Section 5 (12 items, superset); Target 4 retains V1 list verbatim in meaning |
| Conversation starters 3–4 | Target 4 |
| Capabilities table, all Off | Target 4; generalized in Section 6 |
| Delivery: one block, no preamble | Target 4; Section 8 |
| Relations (core-extractor, spinal-column) | Section 2 "Upstream relations"; Section 9 |
| Scope | Section 10 |

## Assumptions and unresolved items

- Assumption: "Plugin Creator" refers to ChatGPT's plugin-building feature as named in your work order and in search results; its invocation details are not documented in the pages read.
- Assumption: the `.skill` format is a ZIP containing the skill folder (the official packager script was not available in the build session, so the `.skill` was produced with a plain ZIP).
- Unresolved: whether ChatGPT's Plugin Creator accepts the portable ZIP as-is. Not install-tested.
- Unresolved: total ZIP size limit and whether a top-level folder is required (not documented in the pages read).

## Rollback

V1 is untouched at `skills\custom-gpt-package\SKILL.md` (live) and preserved as the supplied ZIP copy (SHA-256 above). Nothing existing was overwritten. To roll back: delete or move the `skills\plugin-package-architect` folder and keep using `custom-gpt-package` V1.0 as before. No V1 file needs restoring.
