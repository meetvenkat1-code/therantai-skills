---
name: compress
description: >
  Guards invocation signal integrity in skill files by stripping behavioral fog — prose, rationale, framing, and transitional language that carries no behavioral weight and degrades Claude's execution clarity at the moment of firing. Invoke with /compress, "execution-weight pass", "strip this skill", "compress to execution weight", "remove the prose from this skill". Fires on any skill file where accumulated prose has begun to dilute the signal-to-noise ratio of the executable content. Length is not the trigger — fog density is. The governing act at every line is signal protection: does this line hold signal? If not, it is fog. Borderline lines are retained — false removal is the only fear.
---

# Compress

**Conviction:** a skill file is a behavioral surface to be executed, not a document to be understood. Every line of framing/rationale/motivational prose that helped the forge make sense has no place in the installed artifact — it's weight carried at every firing for no behavioral return. The governing act is signal *protection*, not reduction or summarization.

## The signal test (supersedes length/format/redundancy heuristics)
> Does this line alter how Claude behaves at invocation?
- Yes → signal, retain unconditionally.
- No → fog, remove.
- Ambiguous → **retain**. False removal is the only fear — compression that loses a constraint has amputated, not compressed.

## Fog vs. signal
Remove: "this exists because..." rationale, framing that restates an already-unambiguous rule, transitional language, examples that duplicate rather than extend a rule, motivational framing with no decision consequence, headers emptied by their own content's removal.
Retain unconditionally: every rule/constraint/anti-pattern, every trigger phrase, every output format spec, every explicit "does NOT do," every decision-fork, any example whose removal leaves a governing rule ambiguous.

**Borderline protocol:** genuinely ambiguous lines are retained as-is, intact — never rewritten to resolve the ambiguity (rewriting is out of scope).

## Protocol
1. Read the whole file first — map signal vs. fog before touching anything (compression decisions interact; a line that looks like fog alone may anchor a downstream rule).
2. Apply the signal test line by line.
3. Borderline protocol fires before any ambiguous removal — when uncertain, retain.
4. Deliver the compressed file whole, ready to replace the original, no narration unless asked. Optional receipt:
```
COMPRESS RECEIPT
Fog removed: [N] | Signal retained: [N] | Borderline retained: [N]
```

## Triggers
Fog density, not length — a long fog-free file doesn't need this; a short file where framing outruns its rules does.

## Relations
Distill ascends to the generative seed; compress stays at the same level, inside the file. Core-extractor ports identity out for reuse elsewhere; compress reduces in place. Moult questions ecosystem membership; compress never does — operates only on skills that already earned their place. Not a summarizer — loses nothing behavioral, only never-load-bearing fog.

## Anti-patterns
Don't remove for length/style alone — only for absent behavioral signal. Don't strip examples that resolve real ambiguity. Don't run on a file that hasn't actually accumulated fog. Don't reword spine in compression's name — output is the same contract, stripped, not rephrased. Scope: SKILL.md files in this ecosystem only.
