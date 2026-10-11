---
engine: dimensions
source_file: engines/dimensions-V2-header-layout-fixed.html
extracted_from: dimensions (:443-499), taxonomy (:501-526), buildMappingPrompt (:2061-2086), buildExpansionPrompt (:1963-1968), buildApplicationPrompt (:1970-1982), callLaneStrict (:1212-1216)
archetype: Multi-Step-Bespoke
note: taxonomy has 23 entries (3×dim1 + 11×dim2 + 6×dim3 + 1×dim4 + 1×dim5 + 1×dim6)
---

# Dimensions — Mapping Prompts (verbatim)

> `js:<id>` blocks are verbatim JS source, injected raw into the compiled
> chassis. `buildMappingPrompt` injects the TAXONOMY + DIMENSIONS lists at call
> time (`${list}`, `${dimList}`) — the compiler must not pre-render them.

```js:taxonomy
        // Dimension Data
        const dimensions = [
            {
                id: 1,
                number: "01",
                name: "Foundations of Thinking",
                tagline: "Precision, distinctions & clarity",
                icon: "fa-solid fa-search",
                color: "#6366f1",
                outcome: "From vague → High-resolution thinking"
            },
            {
                id: 2,
                number: "02",
                name: "Core Mental Models",
                tagline: "Rewiring fundamental perception",
                icon: "fa-solid fa-eye",
                color: "#a855f7",
                outcome: "From default → Multi-dimensional seeing"
            },
            {
                id: 3,
                number: "03",
                name: "Powerful Frameworks",
                tagline: "Structured approaches to complexity",
                icon: "fa-solid fa-project-diagram",
                color: "#ec4899",
                outcome: "From reactive → Systematic thinking"
            },
            {
                id: 4,
                number: "04",
                name: "Interconnections & Trade-offs",
                tagline: "Seeing the web of reality",
                icon: "fa-solid fa-project-diagram",
                color: "#f43f5e",
                outcome: "From isolated → Systems thinking"
            },
            {
                id: 5,
                number: "05",
                name: "Application & Shadow",
                tagline: "Wise use, limitations & failure modes",
                icon: "fa-solid fa-exclamation-triangle",
                color: "#f59e0b",
                outcome: "From naive → Discernment"
            },
            {
                id: 6,
                number: "06",
                name: "Meta & Meta-Meta Thinking",
                tagline: "Architecting your own mind",
                icon: "fa-solid fa-infinity",
                color: "#10b981",
                outcome: "From user → Architect of thinking"
            }
        ];
        // Taxonomy the classifier ranks against — every named model/framework, tagged to its dimension
        const taxonomy = [
            { dim: 1, name: "Necessary vs. Sufficient Conditions" },
            { dim: 1, name: "Ladder of Inference" },
            { dim: 1, name: "Facts vs. Interpretations vs. Judgments" },
            { dim: 2, name: "Inversion" },
            { dim: 2, name: "Second-Order Thinking" },
            { dim: 2, name: "Incentives" },
            { dim: 2, name: "Compounding" },
            { dim: 2, name: "Opportunity Cost" },
            { dim: 2, name: "Circle of Competence" },
            { dim: 2, name: "Hanlon's Razor" },
            { dim: 2, name: "Availability Heuristic" },
            { dim: 2, name: "Lindy Effect" },
            { dim: 2, name: "Via Negativa" },
            { dim: 2, name: "Map vs. Territory" },
            { dim: 3, name: "OODA Loop" },
            { dim: 3, name: "First Principles Thinking" },
            { dim: 3, name: "Eisenhower Matrix" },
            { dim: 3, name: "Feynman Technique" },
            { dim: 3, name: "Pre-Mortem Analysis" },
            { dim: 3, name: "Regret Minimization Framework" },
            { dim: 4, name: "Interconnections & Trade-offs (systems view)" },
            { dim: 5, name: "Application & Shadow (limitations, failure modes)" },
            { dim: 6, name: "Meta & Meta-Meta Thinking (thinking about your thinking)" }
        ];
```

```js:mapping
        function buildMappingPrompt(fragment) {
            const list = taxonomy.map((t, i) => `${i}. [Dim ${t.dim}] ${t.name}`).join('\n');
            const dimList = dimensions.map(d => `${d.id}. ${d.name} — ${d.tagline}`).join('\n');
            const system = `You are the interpretive mapping engine for a mental-models learning tool called Dimensions.

A person will hand you a raw fragment — a half-formed tension, a passing intuition, a complaint, an observation, anything. It will rarely name a model explicitly. Your job is generative, not lexical matching: reason about what is actually going on underneath the fragment, then connect that underlying dynamic to the models and frameworks below that illuminate it.

Every fragment connects to something in this list — the list spans foundational clarity, mental models, decision frameworks, systems/trade-offs, failure modes, and meta-thinking, which together cover almost any kind of thinking a person could be doing. Your task is never to decide whether a connection exists — it does. Your task is to find the sharpest ones and explain the mechanism, not just the label.

Concretely: read the fragment for its underlying mechanism (what force, incentive, bias, structural pattern, or blind spot is actually driving what they described), then match that mechanism to the models/frameworks that name or explain it — even when the fragment never uses the model's own vocabulary. "I get distracted by my phone" never says "incentive" or "second-order" but is centrally about both.

Always return between 3 and 6 matches, ordered most dominant first. Do not return an empty list — if the fragment is very short or abstract, that just means you reach one level further to find the generative connection (their example is one instance of a broader mechanism; name the mechanism, then map it). Never pad with a weak filler match just to hit 3, but do the interpretive work required to find real ones — thin surface phrasing is not a reason to stop early.

Important: you are never evaluating whether the fragment's claim is true, wise, or advisable. You are analyzing the SHAPE of the thinking in it — what kind of inference, leap, generalization, incentive, or blind spot the fragment exhibits — regardless of whether you personally agree with the content. A sweeping claim, a controversial opinion, or a confident prediction all map cleanly (e.g. onto Availability Heuristic, Lindy Effect, Map vs. Territory, Second-Order Thinking) without you needing to endorse, caveat, or correct the claim itself. Do not add disclaimers, safety caveats, or hedging about the fragment's subject matter anywhere in your response — output is JSON only, always, no matter what the fragment says.

TAXONOMY (index. [Dim n] Name):
${list}

DIMENSIONS:
${dimList}

Respond with ONLY valid JSON — your entire response must start with { and end with }. No prose before or after, no code fences, no preamble, no caveats. Exact shape:
{"matches":[{"index":<taxonomy index>,"strength":"high"|"medium"|"low","reason":"<one sentence naming the specific mechanism in THEIR fragment and how this model illuminates it>"}]}`;

            return { system, user: fragment };
        }
```

```js:expansion
        function buildExpansionPrompt(fragment, taxonomyItem, shortReason) {
            const dim = dimensions.find(d => d.id === taxonomyItem.dim);
            const system = `You are the interpretive mapping engine for a mental-models learning tool called Dimensions. A person's fragment has already been matched to a specific model/framework. Write a short generative paragraph (3-5 sentences) that walks through HOW and WHY this model illuminates their fragment — the mechanism, not just the label. Be specific to their exact fragment, not generic textbook explanation of the model. Do not evaluate whether their fragment's claim is true — only the reasoning structure. Plain prose only, no JSON, no headers, no markdown.`;
            const user = `Fragment: "${fragment}"\n\nMatched model: ${taxonomyItem.name} (${dim ? dim.name : 'Dimension ' + taxonomyItem.dim})\nShort reason already given: "${shortReason}"\n\nExpand this into the generative paragraph.`;
            return { system, user };
        }
        function buildApplicationPrompt(fragment, taxonomyItem, shortReason) {
            const dim = dimensions.find(d => d.id === taxonomyItem.dim);
            const system = `You are the applied-practice engine for a mental-models learning tool called Dimensions. A person's fragment has already been matched to a specific model/framework, and the mechanism has been explained. Your job now is different: give them a concrete, usable protocol for applying THIS model to THEIR exact situation — not a definition, not a restatement of the mechanism.

Structure the response as:
1. One sentence naming the specific move this model prescribes for their situation.
2. 3-5 concrete, sequential steps they can actually run — each step an action, not a concept. Steps should reference specifics from their fragment where possible, not generic textbook steps.
3. One sentence on what to watch for — the failure mode of applying this model badly, or the signal that it's working.

Keep it tight and operational — this is a protocol to run, not an essay to read. Do not evaluate whether their fragment's claim is true. Plain prose with a numbered list for the steps, no JSON, no markdown headers.`;
            const user = `Fragment: "${fragment}"\n\nMatched model: ${taxonomyItem.name} (${dim ? dim.name : 'Dimension ' + taxonomyItem.dim})\nWhy it matches: "${shortReason}"\n\nGive me the applied protocol.`;
            return { system, user };
        }
        async function callLaneStrict(lane, systemPrompt, userMessage) {
            var r = await callModel({ provider: lane.pid, model: lane.m, system: systemPrompt, user: userMessage,
                onText: function () {} });
            return r;
        }
```

## Multi-lane orchestration (plumbing notes, implemented by runner)

- One shared `{system, user}` from `buildMappingPrompt(fragment)` fanned to every ticked lane: `Promise.all(lanes.map((l,i) => sleep(i*220).then(() => runLaneMapping(l, …))))`
- Strict per-lane `callModel({provider: lane.pid, model: lane.m, …})` — no chain-walk substitution (lane honesty); each lane fails in its own column, never aborts siblings
- Parse: JSON `{matches:[{index, strength, reason}]}`; drop unknown indices; sort high→medium→low
- Per match: Expand (generative paragraph via `buildExpansionPrompt`) + Apply (protocol via `buildApplicationPrompt`), same lane
- Journey/progress/response-library/meta-OS are presentation layers over these entries; registry projection keeps mapping + expand/apply, persists entries to localStorage under `dimensions_response:*`
