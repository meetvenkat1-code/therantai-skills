// Spec schema + provenance checks. Returns { errors, warnings }. No dependencies.
export const normQ = (s) => String(s).replace(/[\u2018\u2019]/g, "'").replace(/[\u201C\u201D]/g, '"').replace(/\s+/g, ' ').trim();

const isStr = (v) => typeof v === 'string' && v.trim().length > 0;

export function validateSpec(spec, promptText) {
  const errors = [], warnings = [];
  const E = (m) => errors.push(m), W = (m) => warnings.push(m);
  if (!spec || typeof spec !== 'object' || Array.isArray(spec)) return { errors: ['spec must be a JSON object'], warnings };

  if (!/^[a-z0-9][a-z0-9-]{1,40}$/.test(spec.slug || '')) E('slug must match /^[a-z0-9][a-z0-9-]{1,40}$/');
  for (const k of ['title', 'cardLabel', 'emptyText', 'placeholder', 'runLabel', 'runBusyLabel', 'busyText', 'description'])
    if (!isStr(spec[k])) E(`${k} must be a non-empty string`);
  if (isStr(spec.title) && spec.title.length > 60) E('title too long (max 60)');
  if (isStr(spec.runLabel) && spec.runLabel.length > 18) E('runLabel too long (max 18, it sits on a button)');
  if (isStr(spec.runBusyLabel) && spec.runBusyLabel.length > 22) E('runBusyLabel too long (max 22)');
  if (!Array.isArray(spec.triggers) || !spec.triggers.length || !spec.triggers.every(isStr)) E('triggers must be a non-empty array of strings');
  if (spec.paramNote !== undefined && !isStr(spec.paramNote)) E('paramNote must be a string when present');
  if (spec.emptyInputReply !== null && spec.emptyInputReply !== undefined && !isStr(spec.emptyInputReply)) E('emptyInputReply must be a string or null');

  // controls ---------------------------------------------------------------
  if (!Array.isArray(spec.controls)) E('controls must be an array (use [] for none)');
  else {
    const seen = new Set();
    spec.controls.forEach((c, i) => {
      const p = `controls[${i}]`;
      if (!c || typeof c !== 'object') return E(`${p} must be an object`);
      if (!/^[A-Z][A-Z0-9_]*$/.test(c.key || '')) E(`${p}.key must be UPPER_SNAKE`);
      if (seen.has(c.key)) E(`${p}.key duplicated`); seen.add(c.key);
      if (c.type === 'slider') {
        for (const k of ['min', 'max', 'step', 'default']) if (typeof c[k] !== 'number') E(`${p}.${k} must be a number`);
        if (typeof c.min === 'number' && typeof c.max === 'number' && c.min >= c.max) E(`${p}: min must be < max`);
        if (typeof c.default === 'number' && (c.default < c.min || c.default > c.max)) E(`${p}.default out of range`);
        if (!isStr(c.label)) E(`${p}.label required`);
        if (c.bands !== undefined && !(Array.isArray(c.bands) && c.bands.every((b) => Array.isArray(b) && typeof b[0] === 'number' && isStr(b[1])))) E(`${p}.bands must be [[upTo:number,label:string],...]`);
      } else if (c.type === 'chips') {
        if (!Array.isArray(c.options) || c.options.length < 2 || !c.options.every(isStr)) E(`${p}.options must be >=2 strings`);
        else if (!c.options.includes(c.default)) E(`${p}.default must be one of options`);
      } else E(`${p}.type must be "slider" or "chips"`);
      if (promptText && c.key && !new RegExp('^' + c.key + '\\s*=', 'm').test(promptText))
        E(`${p}: prompt has no line starting "${c.key} =" so this control would do nothing`);
    });
    if (promptText) {
      const declared = new Set(spec.controls.map((c) => c.key));
      for (const m of promptText.matchAll(/^([A-Z][A-Z0-9_]{2,})\s*=\s*\S/gm))
        if (!declared.has(m[1])) W(`prompt line "${m[1]} = ..." looks like a parameter but has no control`);
    }
  }

  // contract (optional) ------------------------------------------------------
  const C = spec.contract;
  if (C !== undefined && C !== null) {
    if (typeof C !== 'object') E('contract must be an object');
    else {
      const hay = promptText ? normQ(promptText).toLowerCase() : null;
      if (C.sections !== undefined) {
        if (!Array.isArray(C.sections) || !C.sections.every(isStr)) E('contract.sections must be an array of strings');
        else if (hay) C.sections.forEach((s) => { if (!hay.includes(normQ(s).toLowerCase())) E(`contract.sections "${s}" does not appear in the prompt`); });
      }
      if (C.fixedReplies !== undefined) {
        if (!Array.isArray(C.fixedReplies) || !C.fixedReplies.every(isStr)) E('contract.fixedReplies must be an array of strings');
        else if (hay) C.fixedReplies.forEach((s) => { if (!hay.includes(normQ(s).toLowerCase())) E(`contract.fixedReplies "${s.slice(0, 40)}..." is not verbatim in the prompt`); });
      }
      if (C.endsWith !== undefined && !(isStr(C.endsWith) && C.endsWith.length === 1)) E('contract.endsWith must be a single character');
      if (C.forbid !== undefined && !(Array.isArray(C.forbid) && C.forbid.every((f) => ['lists', 'bold', 'extra-headers'].includes(f)))) E('contract.forbid items: lists | bold | extra-headers');
      if (!C.sections && !C.fixedReplies && !C.endsWith) W('contract has no sections, fixedReplies or endsWith; it checks nothing');
    }
  }
  if (isStr(spec.emptyInputReply) && promptText && !normQ(promptText).toLowerCase().includes(normQ(spec.emptyInputReply).toLowerCase()))
    E('emptyInputReply is not verbatim in the prompt');

  // tests --------------------------------------------------------------------
  if (!Array.isArray(spec.tests) || !spec.tests.length) E('tests must contain at least one { input, output, valid:true } sample');
  else {
    spec.tests.forEach((t, i) => {
      if (!t || !isStr(t.input) || !isStr(t.output) || typeof t.valid !== 'boolean') E(`tests[${i}] needs input, output (strings) and valid (boolean)`);
    });
    if (!spec.tests.some((t) => t && t.valid === true)) E('tests needs at least one sample with valid:true (a realistic output that follows the prompt)');
  }
  return { errors, warnings };
}
