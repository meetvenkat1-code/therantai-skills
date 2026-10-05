# Provenance Format Reference

This file defines the markup standard for friction provenance within the Updated Contract (Artifact 2).

---

## Purpose

Every constraint absorbed via Fuse Delta must carry its origin story inline.

This preserves the **reason** behind each rule, not just the rule itself.

Without provenance: rules become decorative over time.  
With provenance: rules remain load-bearing.

---

## Inline Provenance Block

Use this format when inserting an absorbed delta into the Updated Contract:

```markdown
> **[DELTA — absorbed from Contract B]**  
> *Friction:* What problem kept occurring before this rule existed.  
> *Resolution:* What the builder discovered that eliminated the friction.

[The constraint text itself follows here, written in the contract's native voice]
```

---

## Inline Fork Marker

When a Contradictory Fork was resolved and the winning resolution was applied:

```markdown
> **[FORK RESOLVED — Contract A resolution adopted]**  
> *Rationale:* Why A's resolution was structurally preferred.  
> *Trade-off:* What B's approach had that this sacrifices.

[The constraint text itself follows here]
```

---

## Unresolved Fork Marker

When a fork could not be resolved and is pending user judgment:

```markdown
> **[FORK: UNRESOLVED — User judgment required]**  
> *Territory:* What this constraint governs.  
> *Contract A says:* [A's resolution]  
> *Contract B says:* [B's resolution]  
> *Decision needed:* [Specific question for the user]

[Placeholder — do not insert either resolution until decided]
```

---

## Clean Version Protocol

The Updated Contract (Artifact 2) always includes provenance blocks.

If the user requests a **clean version** (for installation without attribution markup), strip:
- All `> **[DELTA...]**` blocks
- All `> **[FORK...]**` blocks
- All `> **[FORK: UNRESOLVED...]**` blocks

Retain only the constraint text that follows each block.

The clean version should read as an organic, unified contract — not a patchwork.

---

## Provenance Decay Prevention

When a contract is evolved through multiple Fuse Delta sessions, provenance blocks accumulate.

After **3+ sessions**, offer to consolidate:

- Merge all provenance into a separate `HISTORY.md` file
- Strip inline blocks from the main contract
- The contract body returns to clean constraint text
- All friction history is preserved in `HISTORY.md` for reference

This prevents the contract from becoming more provenance than substance.

---

## Example: Full Absorbed Delta in Context

```markdown
### Typography Selection

Always use system font stacks for body text unless a design system explicitly specifies otherwise.

> **[DELTA — absorbed from Contract B]**  
> *Friction:* Builder repeatedly chose decorative fonts for body copy, causing readability issues that required rework on every third build.  
> *Resolution:* Encoding system fonts as the unconditional default eliminated the decision point entirely.

Do not import web fonts unless the operator's design system requires a specific typeface. When in doubt, inherit from the OS.
```

The constraint reads naturally. The provenance explains why. Both survive together.
