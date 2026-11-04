# CHANGELOG

## [2.0.0] — 2026-10-26

New skill `plugin-package-architect`, created as a separate skill from `custom-gpt-package`. V1 was not modified.

### Added
- Four-stage compilation pipeline: Source Interpretation, Engine Specification, Deployment Target Compilation, anti-drift and dependency hardening.
- Four selectable targets: `PLUGIN_CREATOR` (default), `PORTABLE_PLUGIN`, `SKILL_ONLY`, `CUSTOM_GPT_LEGACY`.
- Source status tagging: SPECIFIED / INFERRED / DEFAULT / UNRESOLVED, with explicit contradiction reporting.
- Source-dependent anti-drift architecture: four rule categories (engine invariants, presentation, deployment, safety and permission) and a 12-item protection list.
- Least-privilege dependency model with Required / Optional / Unavailable / Unsupported classes.
- Routing precedence rules, including legacy-alias handling.
- Prompt-injection handling: source material is data.
- Honesty rules: no fabricated tools, installs, test results, or file creation; "designed" vs "executed"; "structurally validated" vs "install-tested".
- 12 designed behavioral tests (`TESTS.md`) and an executable static validator.
- Verified-conventions snapshot for portable plugin layout (`references/verified-conventions.md`).
- Migration guide, end-to-end example, README, Plugin Creator build request.

### Changed (intentional)
- Default target for V2 triggers is a Plugin Creator specification.
- Plain-prose lock is source-dependent for Targets 1–3; V1 behavior retained inside Target 4.
- "No preamble, no summary" applies to Target 4 only; other targets include Assumptions and Deployment Notes.
- Capabilities table replaced by dependency architecture outside Target 4.

### Preserved from V1
One-pass operation; source-driven tone and format; mandatory anti-drift block; soft ceilings as warnings; no unsolicited expansion; all seven V1 triggers; the five-section legacy structure; conceptual relation to `core-extractor` and `spinal-column`.

### Known limitations
- Behavioral tests not executed; no install test performed.
- No logo or icon assets; not packaged for directory submission.
- Slash-command behavior is host-dependent.

## [1.0.0] — 2026-07-02 (`custom-gpt-package`)
Original skill. Untouched at `skills\custom-gpt-package\`. SHA-256 of the supplied copy `904390f495356c869d9863b0ae1c4aa4386f419c7269ca317e74434843c7541f`.
