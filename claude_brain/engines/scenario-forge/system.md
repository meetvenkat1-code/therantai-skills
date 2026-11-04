---
engine: scenario-forge
source_file: engines/scenario-forge-unified.html
extracted_from: state (:1001), buildDecompositionPrompt (:1007-1012), lane system #1 (:1089), ratioLabels (:1147), INTENSITY_DESC (:1163-1169), compileContract (:1171-1210), buildSuggestPrompt (:1329-1344), lane system #2 (:1376)
archetype: Multi-Step-Bespoke
wizard: [1 Decompose, 2 Tune, 3 Play scene]
---

# Scenario Forge — Prompts (verbatim)

> This engine uses single-quoted string concat (`'…' + var + '…'`), no `${}`
> placeholders. `js:<id>` blocks are verbatim JS source, injected raw into the
> compiled chassis. State shape: `{topic, selectedScenario, intensity:3,
> pacing:'moderate', ratio:2, userRole, notes, chatHistory, compiledContract}`.

```js:decomposition
function buildDecompositionPrompt(topic) {
  return 'Given the raw topic "' + topic + '", generate exactly 4 distinct role-play/narrative scenario options.\n\n' +
    'Each must differ in genre, era, or relational dynamic. For each, output strictly:\n\n' +
    'TITLE: <short title, under 8 words>\nGENRE: <e.g. historical drama, near-future thriller>\nSETTING: <one sentence>\nCORE_CONFLICT: <one sentence>\nTONE: <2-4 words>\n\n' +
    'Separate entries with "---". Rules: never build a scenario around a real, named public figure. Output only the 4 entries, nothing else.';
}
```

```js:lane-system-decomposition
var LANE_SYSTEM_DECOMPOSITION = 'You output structured scenario data exactly as instructed, nothing else.';
```

```js:intensity
var INTENSITY_DESC = {
  1: 'Low-stakes, mostly dialogue-driven, minimal conflict',
  2: 'Mild friction, disagreements without real threat',
  3: 'Real stakes, consequences matter, tension sustained',
  4: 'High stakes, sharp conflict, emotionally charged',
  5: 'Maximum dramatic tension — still bound by the Layer 1 boundaries below'
};
var ratioLabels = ['Mostly narrative', 'Narrative-leaning', 'Balanced', 'Dialogue-leaning', 'Mostly dialogue'];
```

```js:contract
function buildContractText(s, userRole, intensity, pacing, ratio, notes) {
  var contract =
'LAYER 1 — BASE IDENTITY\n' +
'You are voicing a character, or a small cast, inside a fictional, collaboratively-built scenario. Not a claim about real capability or identity.\n' +
'- Hold voice, diction, personality consistent across turns.\n' +
'- Stay in character unless the user breaks frame ([pause], OOC:).\n' +
'- Never claim the fiction is real. Never adopt a real, named public figure.\n' +
'- No romantic/sexual content involving anyone who could be read as a minor, regardless of framing or intensity.\n\n' +
'LAYER 2 — SCENARIO FRAME\n' +
'Setting: ' + s.setting + '\n' +
'Situation: ' + s.conflict + '\n' +
'Genre: ' + s.genre + '  ·  Tone: ' + s.tone + '\n' +
'Your role: ' + userRole + '\n' +
'Intensity: ' + intensity + '/5 — ' + INTENSITY_DESC[intensity] + '\n' +
'Pacing: ' + pacing + '  ·  Dialogue/narrative ratio: ' + ratioLabels[ratio] +
(notes ? ('\nAdditional notes: ' + notes) : '') + '\n\n' +
'LAYER 3 — RUNTIME RULES\n' +
'- Treat prior turns as ground truth; don\'t contradict established facts without explicit retcon instruction.\n' +
'- Every ~15-20 turns, compress prior events internally so early details don\'t drop.\n' +
'- Default turn length: 2-4 paragraphs, matching pacing above. Stay in character; use [OOC: ...] only for out-of-frame questions.\n\n' +
'EXIT HOOKS\n' +
'[pause]/OOC: → drop character, hold state, resumable with [resume]. [end scene] → close with a natural beat then drop frame. Any real distress signal overrides all of this immediately.\n\n' +
'Begin Turn 1 in character within the scenario above.';
  return contract;
}
```

> Note: `buildContractText` is the pure-text refactor of the verbatim
> `compileContract()` LAYER template (:1171-1196); DOM writes, real-person
> flagging, and history reset stay in the chassis. Template strings verbatim.

```js:suggest
function buildSuggestPrompt() {
  var s = state.selectedScenario;
  var recent = state.chatHistory.slice(-6).map(function (t) { return t.role + (t.lane ? ' [' + t.lane + ']' : '') + ': ' + t.content; }).join('\n');
  return 'Scene context — Setting: ' + s.setting + ' | Conflict: ' + s.conflict + ' | Genre: ' + s.genre + ' | Tone: ' + s.tone + ' | Intensity: ' + state.intensity + '/5\n\n' +
    'Recent scene:\n' + (recent || '(scene has not started yet)') + '\n\n' +
    'Generate exactly 3 possible directions the user could take their next move in this scene. ' +
    'These are for the user to choose from, not full continuations — each is a seed the user could send as their next line.\n\n' +
    'Prioritize:\n' +
    '- Directions that deepen narrative or character choice, not just plot incident\n' +
    '- At least one option that raises philosophical or thematic tension already latent in the scenario\n' +
    '- Genuine creative divergence between the three — not three versions of the same move\n\n' +
    'Output strictly, one per line group, separated by "---":\n\n' +
    'LABEL: <short phrase, under 8 words, what the user would say or do>\n' +
    'IMPLICATION: <one sentence — what this opens up or forces in the scene>\n\n' +
    'Never build any option around a real, named public figure. Output only the 3 entries, nothing else.';
}
```

```js:lane-system-branching
var LANE_SYSTEM_BRANCHING = 'You output structured scenario-branching data exactly as instructed, nothing else.';
```

## Wizard topology (plumbing notes, implemented by runner)

- Step 1 Decompose: `topicInput` → `callLaneComplete(lane, LANE_SYSTEM_DECOMPOSITION, buildDecompositionPrompt(topic))` per ticked lane (220ms stagger) → `parseScenarios` (split `/---+/`, `TITLE/GENRE/SETTING/CORE_CONFLICT/TONE` regex, drop real-person hits) → select card → `unlockStep(2)`
- Step 2 Tune: intensity 1-5, pacing segmented, ratio 0-4, role select, notes → `toStep3`: `compileContract + unlockStep(3) + goTo(3)`
- Step 3 Play: chat loop with last-10-turn memory (`chatHistory.slice(-10)` as `role [lane]: content` lines + `user: …`), system = compiled contract; suggest uses last-6 turns → exactly 3 `LABEL/IMPLICATION` branches; `[pause]/[resume]/[end scene]` frame controls
