# spec.json reference

`build.mjs` turns `tasks/<name>/spec.json` + `prompt.md` into one HTML engine. All fields below are validated by `forge/lib/spec.mjs`.

| field | type | meaning |
|---|---|---|
| `slug` | `^[a-z0-9][a-z0-9-]{1,40}$` | storage key + file name (`out/<slug>.html`) |
| `title` | string ≤ 60 | page title and header name |
| `cardLabel` | string | label above the output card (the noun for what the engine produces) |
| `emptyText` | string | shown in the output card before the first run |
| `placeholder` | string | textarea placeholder; mention Ctrl/Cmd+Enter |
| `runLabel` / `runBusyLabel` | string ≤ 18 / ≤ 22 | run button idle / busy text (short; it sits on a button) |
| `busyText` | string | shown in the output card while the model is working |
| `description`, `triggers[]` | string, string[] | metadata stored with the prompt-library entry |
| `paramNote` | string, optional | note under the prompt editor; auto-generated if omitted |
| `controls[]` | array, `[]` for none | one control per `KEY = value` line in the prompt (see below) |
| `emptyInputReply` | string or `null` | if the prompt dictates a fixed reply to empty input, put it here (verbatim). The engine prints it locally with no model call. Otherwise `null` |
| `contract` | object, optional | machine-checkable output rules (see below) |
| `tests[]` | array, ≥ 1 | `{input, output, valid}`; at least one `valid:true` realistic sample. `valid:false` samples must be rejected by the contract. Not shipped in the HTML |

## controls
- slider: `{type:"slider", key:"FIDELITY", label:"FIDELITY", min, max, step, default, bands:[[upTo,"label"],...]}`
- chips: `{type:"chips", key:"OUTPUT_MODE", options:["a","b"], default:"a"}`

`key` must be UPPER_SNAKE and the prompt must contain a line starting `KEY =`. At each run that line is rewritten to the control's current value.
A prompt with no such lines gets `"controls": []` and is sent exactly as written.

## contract (all fields optional, all checked live in the engine and by verify)
- `sections`: header names in required order, verbatim from the prompt. A header must sit alone on its line (markdown `#`, bold `**..**`, and a leading `1.` are tolerated).
- `endsWith`: required final character, e.g. `"?"`.
- `fixedReplies`: exact strings the prompt mandates in certain situations. Each must appear verbatim in the prompt. A response equal to one of them is valid.
- `forbid`: any of `"lists"` (bullets / numbered lines in body), `"bold"` (`**x**` in body), `"extra-headers"` (`#` headers in body).
- `singleQuestionInLast`: the last section contains exactly one `?`.
- `noPreface`: default true. Text before the first header is invalid. Set `false` to allow it.

The verifier derives broken variants of your valid sample (drop a header, swap two, add a preface, add a bullet, add chatter after the ending, ...) and **fails if your contract accepts any of them**.
It also scans the prompt for statements like "ends with a question mark", "return exactly "..."", "no bullet points" and fails if the contract does not encode them.
