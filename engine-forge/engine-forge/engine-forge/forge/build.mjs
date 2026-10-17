#!/usr/bin/env node
// Deterministic build: tasks/<name>/{spec.json,prompt.md} + template/* -> tasks/<name>/out/<slug>.html
// Usage: node forge/build.mjs tasks/<name>      (exit 1 and "FAIL build: ..." lines on any problem)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { validateSpec } from './lib/spec.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const T = (n) => fs.readFileSync(path.join(root, 'template', n), 'utf8');
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const jsonForScript = (v) => JSON.stringify(v).replace(/</g, '\\u003c').replace(/\u2028/g, '\\u2028').replace(/\u2029/g, '\\u2029');

// one-pass slot fill: substituted content is never rescanned, so prompts may contain "{{...}}" safely
function fill(str, map, label) {
  return str.replace(/\{\{([A-Z_]+)\}\}/g, (m, k) => {
    if (!(k in map)) throw new Error(`template ${label} uses unknown slot {{${k}}}`);
    return map[k];
  });
}

function controlsHtml(controls) {
  return controls.map((c, i) => {
    if (c.type === 'slider') {
      return `<span>${esc(c.label)}</span><input type="range" id="ctl${i}" min="${c.min}" max="${c.max}" step="${c.step}" value="${c.default}" style="flex:1;min-width:140px;max-width:340px;accent-color:var(--accent-main)"><span class="fv" id="ctl${i}v"></span><span class="band" id="ctl${i}b"></span>`;
    }
    return c.options.map((o) => `<button class="chip${o === c.default ? ' on' : ''}" data-ctl="${esc(c.key)}" data-v="${esc(o)}">${esc(o)}</button>`).join('');
  }).join('\n  ');
}

export function buildEngine(taskDir) {
  const specPath = path.join(taskDir, 'spec.json'), promptPath = path.join(taskDir, 'prompt.md');
  if (!fs.existsSync(promptPath)) throw new Error(`missing ${promptPath}`);
  if (!fs.existsSync(specPath)) throw new Error(`missing ${specPath} (the planner writes it; see forge/SPEC.md)`);
  const prompt = fs.readFileSync(promptPath, 'utf8');
  let spec;
  try { spec = JSON.parse(fs.readFileSync(specPath, 'utf8')); } catch (e) { throw new Error(`spec.json is not valid JSON: ${e.message}`); }
  const { errors, warnings } = validateSpec(spec, prompt);
  if (errors.length) throw new Error('spec invalid:\n  - ' + errors.join('\n  - '));

  // the runtime only needs these; test fixtures stay out of the shipped file
  const { tests, ...runtimeSpec } = spec;
  const paramNote = spec.paramNote || (spec.controls.length
    ? `${spec.controls.map((c) => c.key).join(' and ')} line${spec.controls.length > 1 ? 's are' : ' is'} set from the controls at each run.`
    : 'This prompt has no parameter lines; it is sent exactly as written.');

  const small = {
    SPEC_JSON: jsonForScript(runtimeSpec),
    PROMPT_JSON: jsonForScript(prompt),
  };
  const pre = fill(T('engine.pre.js'), small, 'engine.pre.js');
  const post = fill(T('engine.post.js'), {}, 'engine.post.js');
  const html = fill(T('shell.html'), {
    TITLE: esc(spec.title), CARD_LABEL: esc(spec.cardLabel),
    EMPTY_HTML: `<span class="empty">${esc(spec.emptyText)}</span>`,
    PLACEHOLDER: esc(spec.placeholder), CONTROLS: controlsHtml(spec.controls),
    RUN_LABEL: esc(spec.runLabel), SLUG: esc(spec.slug), PARAM_NOTE: esc(paramNote),
    STYLE: T('style.css'), CORE: T('core.js'), ENGINE_PRE: pre, HELPERS: T('helpers.js'), ENGINE_POST: post,
  }, 'shell.html');
  return { html, spec, warnings };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const taskDir = path.resolve(process.argv[2] || '');
  try {
    const { html, spec, warnings } = buildEngine(taskDir);
    const out = path.join(taskDir, 'out');
    fs.mkdirSync(out, { recursive: true });
    const file = path.join(out, `${spec.slug}.html`);
    fs.writeFileSync(file, html);
    warnings.forEach((w) => console.log('WARN build: ' + w));
    console.log(`built ${path.relative(root, file)} (${(html.length / 1024).toFixed(1)} KB)`);
  } catch (e) {
    console.log('FAIL build: ' + e.message);
    process.exit(1);
  }
}
