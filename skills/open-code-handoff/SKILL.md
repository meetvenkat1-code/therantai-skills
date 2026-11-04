---
name: open-code-handoff
description: Packages the current Claude session into one standalone prompt for Open Code, the local agent that executes HTML engine work and is the only writer to the shared ledger. Two modes. Ledger mode (Claude Desktop reads the ledger directly, or a web chat has STATE.md attached) takes current state from STATE.md and adds a LEDGER section; Paste mode (no ledger available) takes state from the session. Invoke with /oc-handoff [objective] [optional: path], or phrases like "handoff to open code", "package this for open code", "open code prompt". Names the contract and skill files Open Code must read first, summarizes current state, and issues strict ordered directives bound to the UI and Model contracts. Never fabricates paths or file contents. Never writes to the ledger. Do NOT confuse with /handoff, which compresses a session into a context block for a new Claude chat.
---

# open-code-handoff (v2.1)

## 1. Core Premise

Four roles share one practice.

- Director: decides, and carries prompts between Claude and Open Code.
- Architect: any Claude chat, or Claude Desktop. Plans, reads state, drafts handoff prompts. Holds the design intent, decisions made and options rejected.
- Executor: Open Code. Runs on the director's machine with full file access. The only writer to the ledger.
- Ledger: a folder of files on disk that holds shared state between sessions. It replaces memory, and it replaces end-of-session logging, which failed when session limits ended first.

Open Code knows nothing of any Claude conversation. Everything it needs must reach it in the prompt, or in a file the prompt names by absolute path.

Authority runs in a fixed order. The contracts on disk are highest. The ledger's STATE.md and DECISIONS.md are second. The prompt Claude writes is third. A directive that conflicts with a contract or a recorded decision is a stop condition, and Open Code reports instead of choosing.

## 2. Trigger

```
/oc-handoff [objective] [optional: path]
```

Equivalent phrases: "handoff to open code", "package this for open code", "write the open code prompt".

The command is deliberately not `/handoff`, which belongs to the session-compression skill.

- `objective`: one sentence naming the target and the next action. Required.
- `path`: local workspace folder. Optional. See section 4.

## 3. Mode Selection

Decide the mode by trying, never by assuming.

**Ledger mode, direct.** Claude Desktop, with a local file tool whose scope includes the ledger. Attempt to load the file tools once. List `E:\Desktop Backups\claude_brain\ledger\<project>\` and read STATE.md. If both succeed, this is the mode.

**Ledger mode, attached.** A web chat where the director attached STATE.md. Treat the attachment as ground truth. Claude cannot list the runs folder in this case, so the interrupted-run check is left to Open Code.

**Paste mode.** No ledger folder is reachable and no STATE.md is attached, or the project has no ledger yet. Behave as in the earlier version of this skill: state comes from the session, the prompt travels by paste, and the director pastes the return report back.

**Scope limit.** A file tool may reach only part of the disk. At the time of writing, the Desktop tool reaches the claude_brain folder and nothing on the C: drive. Anything outside the tool's scope (contracts, engine folders, the batch folder) is unverified by Claude. Never claim to have checked it. Name it in the prompt for Open Code to verify.

## 4. Defaults and Gates

**Fixed local architecture.** Confirmed by the director. Use as written; never tell Open Code to search for these.

- Root workspace: `C:\Users\meetv\Music\github-files`
- Skills directory: `C:\Users\meetv\Music\github-files\skills`, each skill at `<skill-name>\SKILL.md` in its own subfolder.
- Engines: `C:\Users\meetv\Music\github-files\engines`. Intake batch: `engines\incoming_batch`.
- Ledger: `E:\Desktop Backups\claude_brain\ledger\<project>\`. Rules in `E:\Desktop Backups\claude_brain\ledger\README.md`.
- Seed folder for long prompts: `E:\Desktop Backups\ledger-seed\`.
- The claude_brain folder inside github-files is a separate repo copy. It is not the ledger.

The director's statement in a session overrides this file for that session.

**Default workspace.** In Ledger mode, take the workspace and target paths from the "Where things are" block of STATE.md. In Paste mode, or when STATE.md names none, default to `C:\Users\meetv\Music\github-files\engines\incoming_batch`.

**Default project.** `creative-think`, until the director names another.

**Objective gate.** If the objective is missing, empty, or a bracketed placeholder, ask exactly one question and stop. If STATE.md names a next step, offer it in that question as the recommendation. Never infer an objective and proceed.

**Speed rule.** Beyond the objective gate, ask nothing. Resolve every other ambiguity by marking it `[UNKNOWN]` and delegating verification to Open Code.

## 5. Integrity Rules for Claude

1. Never invent a file path, file name, line number, function name or file content. Name only what the session, the ledger or the director has stated.
2. In Paste mode and for anything outside the tool's scope: where a location is uncertain, write "confirm the path exists; if absent, stop and report it". Never tell Open Code to search the drive for the known paths in section 4.
3. In Ledger mode, CURRENT STATE comes from STATE.md. Reconcile it against what the director says in this session. If they conflict, flag the conflict before issuing the handoff, and let STATE.md stand as the record unless the director rules otherwise.
4. In Paste mode, summarize state only from the session. Separate finished and verified, finished but unverified, in progress, and not started. Never present an unverified claim as done.
5. Carry across locked decisions and rejected options, with a clause of reasoning each. In Ledger mode, cite D-numbers from DECISIONS.md and do not restate settled rulings as open.
6. Quote a contract only when it was read in this session. Otherwise cite the file and tell Open Code to read the governing section.
7. Do not soften or pad. The prompt is an instrument, not a letter.

## 6. Output Specification

On a valid trigger, produce one prompt addressed to Open Code in the second person. Deliver it as one fenced code block, or as a seed file when section 7 applies. Add nothing except a final line of at most two sentences naming any `[UNKNOWN]` the director may wish to fill. The prompt contains these sections, in this order.

**ROLE.** Open Code is the executor. It builds exactly what is specified, inside the contracts and recorded decisions, and reports what it did. It does not redesign.

**WORKSPACE.** Working directory, target file, new or existing. In Ledger mode, include the ledger path and project slug.

**READ FIRST.** Absolute paths, in order. In Ledger mode the first entry is the project's STATE.md. Then the base set for any HTML engine:

1. `C:\Users\meetv\Music\github-files\skills\ui-contract\SKILL.md`
2. `C:\Users\meetv\Music\github-files\skills\hybrid-engine-contract\SKILL.md`
3. `C:\Users\meetv\Music\github-files\skills\model-config-contract\SKILL.md`

There is no local `model.json`. Configuration is fetched live from the canonical raw GitHub URL named inside model-config-contract, with the inline `LOCAL_FALLBACK_CONFIG` from the same contract as the offline floor. Never tell Open Code to read, search for or create a local `model.json`. Tell it to install the contract's own pasted config block verbatim.

Add conditionally, only when the objective touches them, at `C:\Users\meetv\Music\github-files\skills\<skill-name>\SKILL.md`: `model-catalog-panel` (model pickers, lanes, panels), `typography` (fonts, theme bundles), `prompt-engine-interface-contract` (prompt tools), `carousel-engine` (carousel builds), `openrouter-free-path-integration` (OpenRouter free routing).

Open Code confirms each path exists, stops and reports any missing path, uses offset reads until each file is fully read, and states in one line the full paths it actually read before any edit.

**CURRENT STATE.** Per section 5, rules 3 and 4.

**OBJECTIVE.** The director's sentence verbatim, then a one-paragraph precise restatement.

**DIRECTIVES.** Numbered, atomic, ordered. Each names the target, the change, and the check that proves it. Before the first change, back up the target file with a timestamp. Never batch unrelated changes.

**CONTRACT GUARDRAILS.**

- Contract and skill files are read-only. Open Code never edits them, and never edits this skill.
- Provider and model handling comes from the model-config contract through its single hardened call layer, configuration from the canonical URL with `LOCAL_FALLBACK_CONFIG` as floor, both taken verbatim from the contract's pasted block. No provider names, model strings or keys as literals outside that block.
- One self-contained HTML file per engine unless the objective says otherwise.
- UI contract for layout, copy, rendering and the provider indicator; hybrid contract for streaming, palette and banned patterns.
- No new dependencies, no refactors beyond the objective, no files outside the workspace.
- A conflict between a directive and a contract: stop, quote both, ask.

**ACCEPTANCE CHECKS.** Observable conditions Open Code can test without judgment.

**STOP CONDITIONS.** A required path is missing; a contract or recorded decision conflicts with a directive; the target's structure differs from CURRENT STATE; a step needs a change outside the objective; in Ledger mode, any LEDGER check (a) fails.

**RETURN REPORT.** In Ledger mode, Open Code writes it to `runs\NNN-report.md` and also prints it. In Paste mode, it is a block for the director to paste back. Contents: files changed with backup paths, each directive done, skipped or blocked, each acceptance check pass or fail, contract deviations, open items.

**LEDGER.** Ledger mode only. See section 8.

## 7. Delivery

A long prompt pasted into Open Code was truncated once (D-010). Therefore:

1. A prompt of roughly 80 lines or fewer may be pasted as a code block.
2. A longer prompt is delivered as a file. Write it as strict UTF-8 without BOM, with ASCII punctuation. Name it `run-NNN-<slug>.md`, NNN being the next free number in `runs\`. Compute its SHA-256 over the exact final bytes, uppercase, 64 characters, using code execution. Present the file. The director saves it to `E:\Desktop Backups\ledger-seed\`.
3. The launch message the director sends Open Code carries the path and the hash, never the brief itself: read that file, its SHA-256 must equal the stated hash (case-insensitive), stop if it does not. The hash never appears inside the file it hashes.
4. If code execution is unavailable and the prompt is long, say so and split it by section rather than risk silent truncation.

## 8. Ledger Protocol

The ledger is a folder of files that only Open Code writes. Per project, at `ledger\<project>\`: STATE.md (one page, at most 80 lines, rewritten by Open Code after every run), DECISIONS.md (append-only, one line per decision), an optional INVENTORY.md, and `runs\NNN-report.md`. Shared: `_backups\` for dated copies of anything Open Code replaces.

Rules for the architect:

1. Claude never writes to the ledger. Not STATE, not DECISIONS, not a task file. Claude Desktop reads; Open Code writes. If asked to write into the ledger, decline, cite the single-writer rule, and offer the seed-file route in section 7.
2. In Ledger mode, read STATE.md first, then the highest-numbered report, then the tail of DECISIONS.md. Check that STATE's "Last run" equals the highest report number. A mismatch means an interrupted run: report it to the director before drafting anything.
2a. If `BRIEF-FORMAT.md` exists in the active project's ledger root, you must read it to learn the project's specific formatting rules before drafting any directives.
3. Put the STATE.md path first in READ FIRST.
4. After RETURN REPORT, add a LEDGER section containing: the project slug; DECISIONS TO APPEND, one line each in the form `decision | reason | source`, written from this session only and without D-numbers, which Open Code assigns; and the six instructions below.
5. The six LEDGER instructions to Open Code, verbatim: (a) read STATE.md first and state whether it matches CURRENT STATE; also compare its Last run with the highest runs\NNN-report.md and report any mismatch as an interrupted run; if either check fails, stop and report; (b) list the runs folder and take the next free number NNN; (c) append the DECISIONS TO APPEND lines to DECISIONS.md with the next D-numbers and today's date, never editing an existing line; (d) at the end, write the RETURN REPORT to runs\NNN-report.md and also print it; (e) rewrite STATE.md in at most 80 lines by writing STATE.tmp and renaming it over STATE.md, moving detail into DECISIONS.md or the report; (f) write nothing else in the ledger.
6. Briefs name one engine per run, state its title, storage prefix and export names, and treat a canonical prompt as one byte-exact slice of one source (D-023, D-028).
7. Ledger files are strict UTF-8 without BOM, ASCII punctuation preferred. Reports carry full uppercase SHA-256 hashes and never a pointer to a section that does not exist (D-036, D-037, D-047).
8. Claude never claims to have written to disk. It only issues the prompt.

## 9. Re-entry

In Ledger mode, direct: read STATE.md and the latest report from disk; treat the file as truth over any pasted copy. In Ledger mode, attached: the director attaches STATE.md and, if needed, the latest report. In Paste mode: the director pastes the RETURN REPORT. In every mode, reconcile against the prior CURRENT STATE, flag divergence from the architecture or from recorded decisions, and continue as architect. Do not re-issue a handoff unless asked.

## 10. Revision Notes

- v1: trigger `/oc-handoff` (not `/handoff`); objective gate; anti-fabrication rule; return report; absolute skills path; no local `model.json` (canonical URL plus `LOCAL_FALLBACK_CONFIG`).
- v2: Ledger mode and Paste mode added, chosen by trial, with an explicit scope limit on what Desktop can verify. Ledger protocol (the former skill-section-8.md) absorbed as section 8 and extended with the Desktop-direct reading path. Single-writer law stated as a hard rule for Claude: the architect reads, Open Code writes, so no task files go into the ledger. Seed-file delivery with a SHA-256 launch gate added after a long paste was truncated. Workspace paths in Ledger mode come from STATE.md.
- v2.1: project-specific formatting constraints moved out of this skill into the project ledger. Section 8 gains rule 2a: read `BRIEF-FORMAT.md` from the project's ledger root, when present, before drafting any directives.
- Open Code does not edit this skill. The director installs it at `skills\open-code-handoff\SKILL.md` and in the claude.ai copy (D-009).
