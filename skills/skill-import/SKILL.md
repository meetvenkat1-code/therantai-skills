---
name: skill-import
description: The universal reception organ for the Therantai skill ecosystem zip. Runs a three-verdict merge protocol when a zip or skill bundle arrives from another builder — unique-to-receiver skills are left untouched, overlapping skills are overwritten by the zip (zip is canonical), and unique-to-zip skills are staged and flagged for permanent installation. Self-contained — designed to travel inside the zip so the receiver has the import protocol the moment they have the skills. Invoke with /skill-import, "import these skills", "install the zip", "I received a skill bundle", "help me install Venkatesh's skills", "how do I install this zip", or any moment a zip or folder of external SKILL.md files arrives and the question is how to bring them in without collision or silent overwrite.
triggers:
  - /skill-import
  - import these skills
  - install the zip
  - I received a skill bundle
  - how do I install this zip
  - merge the skill bundle
  - I got a skill zip from a friend
scope: global
version: 1.0
date: 2026-06-23
author: meet.venkat1@gmail.com
---

# Skill-Import

Closes the transfer loop: sending-side skills (transit-block, graft-out, handoff, intake) exist, but none handled a full zip bundle arriving in front of a receiver with their own living skills and no protocol. Every share was a manual "do I overwrite/merge/keep mine?" negotiation. This runs from the zip itself, no expertise in the sending ecosystem required.

## The hard constraint — state first, every time
`/mnt/skills/user/` is **read-only**. Claude cannot write/copy/install there directly. Claude can: stage incoming skills at `/home/claude/` for review, generate a structured install report, run the three-verdict protocol to produce copy-paste-ready commands. The receiver must execute the final copy to `/mnt/skills/user/` on their own host machine. Structural fact, not a limitation — surface it at the threshold every time.

## The three-verdict protocol
**LEAVE** — exists in receiver's ecosystem, not in the zip. Untouched, no review needed. If it isn't in the zip, this protocol doesn't touch it.
**OVERWRITE** — exists in both. Zip is canonical, whole file replaces installed version — no line-by-line merge (degrades the zip's tested coherence for little gain). Local modifications the receiver wants kept → run `/fuse-delta` on that specific skill *after* import, as a deliberate second pass. Never fuse during import.
**STAGE** — exists in zip only, new to receiver. No installed analog to compare against — can't drop in silently. Stage at `/home/claude/<skill-name>/`, surface with a one-line description, confirm before permanent install, then `/place` to earn a registry entry. A skill installed without placement is an orphan; enough orphans flattens the ecosystem.

## Execution
1. State the read-only constraint. 2. Inventory both surfaces (bundle + installed) explicitly, no assuming. 3. Classify every incoming skill LEAVE/OVERWRITE/STAGE, present the full list before touching anything. 4. Receive confirmation or amendment — no file moves before this. 5. Stage OVERWRITE skills at `/home/claude/`, generate exact shell commands. 6. Stage STAGE skills, surface name + function + arc-phase from the bundle's README/registry. 7. Generate the installation report — three sections, exact paths, shell commands, fuse-delta flags. 8. Flag (name only, don't run) any OVERWRITE skill the receiver says they've locally modified.

## Relations
Intake = single-skill reception; skill-import = bundle reception — complementary, not competing. Fuse-delta runs after, never during — skill-import recommends it, never merges inline. Placement-protocol locates every STAGE skill after confirmation — skill-import stages/surfaces, placement locates. Moult `--check` recommended (not mandatory) after a large overwrite, to surface any phantom entries the import introduced.

## Not
Not a merger (fuse-delta). Not single-skill orientation (intake). Not a registry writer (placement-protocol). Not a conflict resolver (fuse-delta, post-import). Owns one decision at scale — which verdict, how to land cleanly — transparent, confirmed before touching files, handed off after.

## Installation note
Travels inside the zip it governs: unzip, copy `skill-import/` to `/mnt/skills/user/skill-import/`. One-time; available on `/skill-import` for every future bundle.
