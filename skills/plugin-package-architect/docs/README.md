# plugin-package-architect V2.0.0

A skill that compiles an idea, conversation, system prompt, framework, existing skill, or existing Custom GPT into a deployable package for one of four targets. It is the V2 successor to `custom-gpt-package` V1 and keeps V1 as its legacy target.

## Deployment targets

| Target | Output | When |
|---|---|---|
| `PLUGIN_CREATOR` (default) | 15-section build specification plus a paste-ready Plugin Creator build request | No target named, or a V2 trigger |
| `PORTABLE_PLUGIN` | `plugin.json` + `skills/<name>/SKILL.md` package | "portable plugin" |
| `SKILL_ONLY` | One standalone `SKILL.md` | "as a SKILL.md", "reusable skill" |
| `CUSTOM_GPT_LEGACY` | V1 five-section Custom GPT package | Any V1 alias, or explicitly requested |

## Invocation

Documented triggers (what the skill's description asks the host to match): `/plugin-package-architect`, "build a plugin from this", "convert this conversation into a reusable plugin", "package this workflow for Plugin Creator", "transform this system prompt into a plugin", "convert this Custom GPT into a plugin", "generate a portable plugin package", "build a reusable skill from this framework". Legacy aliases still route to `CUSTOM_GPT_LEGACY`: `/custom-gpt-package`, "build a custom GPT package", "turn this into a custom GPT", "package this for ChatGPT", "custom GPT from this spine", "make a custom GPT out of this", "render this for the GPT builder".

A slash command works literally only if your host supports it; natural-language triggers are the portable path. Name a target explicitly to override defaults.

## Dependencies

None required. The skill is instructions-only: no MCP server, connectors, hooks, or code execution. `core-extractor` and `spinal-column` are optional upstream skills; they are not included and not assumed.

## Local layout (this folder)

```
plugin-package-architect/
  SKILL.md
  references/verified-conventions.md
  docs/  README, CHANGELOG, MIGRATION, TESTS, EXAMPLE, plugin-creator-build-request, UPGRADE-REPORT
```

The portable plugin ZIP, source/backup ZIP, and `.skill` file were produced in the build session and delivered separately; their checksums are in `docs/UPGRADE-REPORT.md`.

## Installation

Placed as files in the local skills folder; not loaded or install-tested in any host. Options:

1. **As a skill:** upload the `.skill` file, or let your skill host read this folder.
2. **As a portable plugin:** per OpenAI's plugin docs, a portable plugin has `plugin.json` at its root and skills under `skills/`. Upload the portable ZIP through the ChatGPT plugin flow you use. Public listing has extra requirements (icons, listing metadata, review details); see `references/verified-conventions.md`.
3. **Via Plugin Creator:** paste `docs/plugin-creator-build-request.md` into ChatGPT Plugin Creator, then review before publishing.

## Updating

Bump `version`, edit `SKILL.md`, add a CHANGELOG entry, rerun the static validator, rebuild the archives.

## Rollback

V1 is untouched at `skills\custom-gpt-package\SKILL.md`. See `MIGRATION.md`.

## Maker's mark

meet.venkat1@gmail.com
