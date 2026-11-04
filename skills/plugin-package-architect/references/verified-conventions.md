# Verified platform conventions (snapshot)

Verified 2026-10-26 by reading OpenAI's published developer documentation:

- https://developers.openai.com/plugins/build/plugins ("Package your plugin")
- https://developers.openai.com/plugins/deploy/submission ("Upload and submit your plugin")

Caveat: the pages were read through a summarizing fetch tool; the submission page was truncated (the final ~4.8k characters were not read). Treat this file as a snapshot and re-verify before relying on it.

## Portable plugin layout (documented)

- `plugin.json` at the plugin root is the manifest. Required.
- Skills live at `skills/<skill-name>/SKILL.md`, with `name` and `description` frontmatter. The manifest needs no `skills` field; portable packages discover skills from `skills/`.
- MCP servers are configured in root `mcp.json`. Skills-only plugins omit it.
- `assets/` holds icons, logos, screenshots.
- Manifest examples use `$schema` (https://agent-plugins.org/schemas/1.0.0/plugin.schema.json), `name` (kebab-case), `version` (semver), `description`; optional `author`, `homepage`, `repository`, `license`, `keywords`.
- OpenAI-specific settings go under `extensions.com.openai` (documented sub-fields: `apps`, `hooks`, `onboardingSkill`, `interface`).
- Codex compatibility: `.codex-plugin/plugin.json` (legacy fallback), `.mcp.json`.

## Submission constraints (documented)

- Submit the package as a ZIP via the plugin submission portal; fix automated findings and re-upload.
- Keep secrets out of the ZIP.
- Paths in manifests are `./`-prefixed, relative to the plugin root; include every referenced file.
- ZIPs containing app references (`apps` / `.app.json`) or lifecycle hooks cannot currently be submitted.
- `name` max 64 chars; `description` max 4000 chars; `displayName` and `shortDescription` max 30 chars.
- Images: PNG, JPEG, WebP, SVG; at most 5 MiB; icons square and at least 48x48.
- Codex submissions require `logo` and `composerIcon`.
- MCP plugins need review test cases (five positive, three negative), a demo recording URL, release notes, and four HTTPS listing URLs.

## Not documented (do not assume)

- A total ZIP size limit.
- Whether the archive needs a top-level folder (this package puts files at the ZIP root, matching "plugin.json at the plugin root").
- The `.app.json` schema.
- Whether Plugin Creator is invoked by a literal command.
