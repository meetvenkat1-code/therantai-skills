#!/usr/bin/env node
// Ground-truth verifier for an engine task. Offline: the model endpoint is mocked inside the page.
// Usage: node forge/verify.mjs tasks/<name>
// Output convention (the loop depends on it): one line per check, "PASS <id> ..." or "FAIL <id> ...",
// and a final "VERIFY: x/y passed". Exit code 0 only when every check passes.
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import crypto from 'node:crypto';
import http from 'node:http';
import { fileURLToPath } from 'node:url';
import { validateSpec, normQ } from './lib/spec.mjs';
import { buildEngine } from './build.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const taskDir = path.resolve(process.argv[2] || '');
const sha = (s) => crypto.createHash('sha256').update(s).digest('hex');
let pass = 0, total = 0;
const check = (id, ok, msg) => { total++; if (ok) pass++; console.log(`${ok ? 'PASS' : 'FAIL'} ${id} ${msg}`); return ok; };
const finish = () => { console.log(`VERIFY: ${pass}/${total} passed`); process.exit(pass === total ? 0 : 1); };
const norm = (s) => String(s).toLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim();

// ---------------------------------------------------------------- load inputs
const promptPath = path.join(taskDir, 'prompt.md'), specPath = path.join(taskDir, 'spec.json');
if (!fs.existsSync(promptPath)) { check('S0', false, `missing ${promptPath}`); finish(); }
const prompt = fs.readFileSync(promptPath, 'utf8');
let spec;
try { spec = JSON.parse(fs.readFileSync(specPath, 'utf8')); } catch (e) { check('S1', false, `spec.json unreadable: ${e.message}`); finish(); }

const { errors, warnings } = validateSpec(spec, prompt);
warnings.forEach((w) => console.log('WARN S1 ' + w));
check('S1', errors.length === 0, errors.length ? 'spec invalid: ' + errors.join(' | ') : 'spec schema and provenance ok');
if (errors.length) finish();

// heuristics: stop a lenient contract from sneaking past (the planner cannot "forget" a rule the prompt states)
{
  const C = spec.contract || {};
  const issues = [];
  if (/ends? with a question mark|always ends with a question/i.test(prompt) && C.endsWith !== '?') issues.push('prompt says output ends with a question mark but contract.endsWith is not "?"');
  const fixed = (C.fixedReplies || []).map(normQ);
  for (const m of prompt.matchAll(/(?:return exactly|return only|state only|reply only|respond only)[^"\n]{0,12}"([^"\n]{12,})"/gi))
    if (!fixed.includes(normQ(m[1]))) issues.push(`prompt mandates fixed reply "${m[1].slice(0, 45)}..." but it is not in contract.fixedReplies`);
  if (/\bno (bullet points|bullets|numbered lists)/i.test(prompt) && !(C.forbid || []).includes('lists')) issues.push('prompt forbids lists but contract.forbid lacks "lists"');
  if (/\bno bold\b|bold text/i.test(prompt) && /\bno\b[^.\n]{0,40}bold/i.test(prompt) && !(C.forbid || []).includes('bold')) issues.push('prompt forbids bold but contract.forbid lacks "bold"');
  check('S1b', issues.length === 0, issues.length ? issues.join(' | ') : 'contract covers the prompt\'s stated output rules');
}

// ---------------------------------------------------------------- static checks on a fresh build
let html;
try { ({ html } = buildEngine(taskDir)); } catch (e) { check('S2', false, 'build failed: ' + e.message.split('\n')[0]); finish(); }
const outFile = path.join(taskDir, 'out', `${spec.slug}.html`);
fs.mkdirSync(path.dirname(outFile), { recursive: true });
fs.writeFileSync(outFile, html);
check('S2', html.length < 400_000, `engine built, ${(html.length / 1024).toFixed(1)} KB`);

const manifest = JSON.parse(fs.readFileSync(path.join(root, 'template', 'manifest.json'), 'utf8'));
const slice = (a, b) => { const i = html.indexOf(a), j = html.indexOf(b, i); return i < 0 || j < 0 ? '' : html.slice(i, j); };
check('S3', sha(slice('/* MODEL CORE v2', 'window.EnginePanels')) === manifest.coreSha256, 'Model Core is byte-identical to the reference');
check('S4', sha(slice('/* storage abstraction', '/* prompt library')) === manifest.helpersSha256, 'UI helpers are byte-identical to the reference');
{
  const i = html.indexOf('<style>\n'), j = html.indexOf('\n</style>');
  check('S5', i >= 0 && sha(html.slice(i + 8, j)) === manifest.styleSha256, 'CSS is byte-identical to the reference');
}
const scriptSrc = html.slice(html.indexOf('<script>\n') + 9, html.lastIndexOf('</script>'));
try { new vm.Script(scriptSrc, { filename: 'engine.js' }); check('S6', true, 'script compiles'); }
catch (e) { check('S6', false, 'script syntax error: ' + e.message); }
{
  const ids = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map((m) => m[1]));
  const used = [...new Set([...scriptSrc.matchAll(/\$\('([A-Za-z0-9_]+)'\)/g)].map((m) => m[1]))];
  const dyn = (id) => /^ctl\d+[vb]?$/.test(id);
  const missing = used.filter((u) => !ids.has(u) && !dyn(u));
  check('S7', missing.length === 0, missing.length ? `script references ids missing from the DOM: ${missing.join(', ')}` : `all ${used.length} referenced element ids exist`);
}
{
  const m = scriptSrc.match(/var DEFAULT_PROMPT = (".*");\n/);
  let got = null; try { got = JSON.parse(m[1]); } catch { /* handled below */ }
  check('S8', got === prompt, 'DEFAULT_PROMPT is byte-identical to prompt.md');
}

// ---------------------------------------------------------------- runtime (headless chromium, mocked model)
let chromium;
try { ({ chromium } = await import('playwright')); }
catch { check('E1', false, 'playwright is not installed. Run: npm run setup'); finish(); }
// Serve over http: Chromium's file:// origins lose localStorage across reloads ~20% of the time, which is a test-env artifact.
const server = http.createServer((q, r) => { r.writeHead(200, { 'content-type': 'text/html; charset=utf-8' }); r.end(fs.readFileSync(outFile)); }).listen(0, '127.0.0.1');
await new Promise((r) => server.once('listening', r));
const pageUrl = `http://127.0.0.1:${server.address().port}/`;
let browser;
try { browser = await chromium.launch({ headless: true }); }
catch (e) { check('E1', false, 'chromium failed to launch (npm run setup installs it): ' + e.message.split('\n')[0]); finish(); }

const sample = spec.tests.find((t) => t.valid === true);
const initMock = () => {
  localStorage.setItem('hek_groq', 'test-key');
  window.__captured = []; window.__mock = { mode: 'ok', text: '' };
  const realFetch = window.fetch.bind(window);
  window.fetch = async (url, opts) => {
    const u = String(url);
    if (u.includes('raw.githubusercontent.com')) return new Response('nf', { status: 404 });
    if (u.includes('api.groq.com') || u.includes('openrouter.ai')) {
      let body = {}; try { body = JSON.parse(opts.body); } catch { /* ignore */ }
      window.__captured.push(body);
      const m = window.__mock;
      if (m.mode === '401') return new Response(JSON.stringify({ error: { message: 'Invalid API Key (mock)' } }), { status: 401, headers: { 'content-type': 'application/json' } });
      const enc = new TextEncoder(), text = m.text, parts = [];
      for (let i = 0; i < text.length; i += 11) parts.push(text.slice(i, i + 11));
      const stream = new ReadableStream({ async start(c) {
        for (const p of parts) { c.enqueue(enc.encode('data: ' + JSON.stringify({ choices: [{ delta: { content: p }, finish_reason: null }] }) + '\n\n')); await new Promise((r) => setTimeout(r, 2)); }
        c.enqueue(enc.encode('data: ' + JSON.stringify({ choices: [{ delta: {}, finish_reason: 'stop' }] }) + '\n\n'));
        c.enqueue(enc.encode('data: [DONE]\n\n')); c.close();
      } });
      return new Response(stream, { status: 200, headers: { 'content-type': 'text/event-stream' } });
    }
    return realFetch(url, opts);
  };
};

const decimals = (c) => (String(c.step).split('.')[1] || '').length;
const ctlStr = (c, v) => (c.type === 'slider' ? Number(v).toFixed(decimals(c)) : String(v));
const expectedSystem = (vals) => spec.controls.reduce((s, c) =>
  s.replace(new RegExp('^' + c.key + '\\s*=.*$', 'm'), () => `${c.key} = ${ctlStr(c, vals[c.key])}`), prompt);
const defaults = Object.fromEntries(spec.controls.map((c) => [c.key, c.default]));

async function openPage(errors) {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await ctx.newPage();
  await page.addInitScript(initMock);
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push('console.error: ' + m.text()); });
  await page.goto(pageUrl);
  await page.waitForFunction(() => document.getElementById('promptBody') && document.getElementById('promptBody').value.length > 0, null, { timeout: 8000 });
  return page;
}
async function runOnce(page, seed, mock) {
  await page.evaluate((m) => { Object.assign(window.__mock, m); window.__captured.length = 0; }, mock);
  await page.fill('#seed', seed);
  await page.click('#run');
  await page.waitForFunction((label) => { const b = document.getElementById('run'); return !b.disabled && b.textContent === label; }, spec.runLabel, { timeout: 15000 });
  return page.evaluate(() => ({ captured: window.__captured.slice(), out: document.getElementById('out').innerText, stat: document.getElementById('stat').textContent }));
}

try {
  const errs = [];
  let page = await openPage(errs);

  // R1 labels
  const ui = await page.evaluate(() => ({
    title: document.title, name: document.querySelector('.header .name').textContent,
    card: document.querySelector('.card-header span').textContent, run: document.getElementById('run').textContent,
    ph: document.getElementById('seed').placeholder, empty: document.getElementById('out').innerText,
  }));
  const labelBad = [];
  if (ui.title !== spec.title) labelBad.push('document.title');
  if (ui.name !== spec.title) labelBad.push('header name');
  if (ui.card !== spec.cardLabel) labelBad.push('card label');
  if (ui.run !== spec.runLabel) labelBad.push('run label');
  if (ui.ph !== spec.placeholder) labelBad.push('placeholder');
  if (ui.empty.trim() !== spec.emptyText) labelBad.push('empty text');
  check('R1', labelBad.length === 0, labelBad.length ? 'labels not applied: ' + labelBad.join(', ') : 'title, labels, placeholder and empty state match the spec');

  // R2 prompt library holds the exact prompt
  const body = await page.inputValue('#promptBody');
  check('R2', body.replace(/\r\n/g, '\n') === prompt.replace(/\r\n/g, '\n'), 'prompt library body equals prompt.md');

  // R3 initial control state
  const ctlBad = [];
  for (const [i, c] of spec.controls.entries()) {
    if (c.type === 'slider') {
      const v = await page.$eval('#ctl' + i, (el) => parseFloat(el.value));
      const shown = await page.$eval('#ctl' + i + 'v', (el) => el.textContent);
      if (v !== c.default) ctlBad.push(`${c.key} slider default ${v} != ${c.default}`);
      if (shown !== ctlStr(c, c.default)) ctlBad.push(`${c.key} readout "${shown}"`);
      if (c.bands && c.bands.length && !(await page.$eval('#ctl' + i + 'b', (el) => el.textContent.trim()))) ctlBad.push(`${c.key} band label empty`);
    } else {
      const on = await page.$$eval(`[data-ctl="${c.key}"].on`, (els) => els.map((e) => e.dataset.v));
      if (on.length !== 1 || on[0] !== c.default) ctlBad.push(`${c.key} chips on=[${on}] expected [${c.default}]`);
    }
  }
  check('R3', ctlBad.length === 0, ctlBad.length ? ctlBad.join(' | ') : `${spec.controls.length} control(s) render in their default state`);

  // R4 first run: request shape + output rendering + stat
  const r1 = await runOnce(page, sample.input, { mode: 'ok', text: sample.output });
  const req = r1.captured[0];
  const sys = req && req.messages && req.messages[0], usr = req && req.messages && req.messages[req.messages.length - 1];
  check('R4', !!req && sys.role === 'system' && sys.content === expectedSystem(defaults) && usr.role === 'user' && usr.content === sample.input.trim(),
    req ? 'request carries the exact system prompt (defaults applied) and the user seed' : 'no model request was made');
  const rendered = norm(r1.out).includes(norm(sample.output));
  check('R5', rendered, rendered ? 'streamed output renders in full' : `rendered output differs from the mocked stream (got: "${r1.out.slice(0, 80).replace(/\n/g, ' ')}...")`);
  check('R6', /\d+ words/.test(r1.stat) && (!spec.contract || /✓|✗/.test(r1.stat) || spec.contract.sections === undefined && !spec.contract.fixedReplies && !spec.contract.endsWith), `stat line: "${r1.stat}"`);

  // R7 response library + persistence
  const countItems = async () => {   // renderResponses is async: wait for the list to settle
    await page.waitForFunction(() => document.querySelectorAll('#rList .item').length > 0, null, { timeout: 2500 }).catch(() => {});
    return page.$$eval('#rList .item', (e) => e.length);
  };
  await page.click('#btnR');
  const n1 = await countItems();
  await page.reload();
  await page.waitForFunction(() => document.getElementById('promptBody').value.length > 0);
  await page.click('#btnR');
  const n2 = await countItems();
  check('R7', n1 === 1 && n2 === 1, `response saved and persists across reload (${n1} -> ${n2})`);
  await page.evaluate(() => document.getElementById('bdR').click());

  // R8 each control reaches the system prompt
  const c8 = [], vals = { ...defaults };   // cumulative: earlier changes stay applied on the page
  for (const [i, c] of spec.controls.entries()) {
    if (c.type === 'slider') { vals[c.key] = c.max; await page.$eval('#ctl' + i, (el, v) => { el.value = v; el.dispatchEvent(new Event('input')); }, c.max); }
    else { vals[c.key] = c.options[c.options.length - 1]; await page.click(`[data-ctl="${c.key}"][data-v="${vals[c.key]}"]`); }
    const r = await runOnce(page, sample.input, { mode: 'ok', text: sample.output });
    const got = r.captured[0] && r.captured[0].messages[0].content;
    if (got !== expectedSystem(vals)) c8.push(`${c.key}=${vals[c.key]} not reflected in the system prompt`);
  }
  check('R8', c8.length === 0, c8.length ? c8.join(' | ') : spec.controls.length ? 'every control rewrites its own prompt line at run time' : 'no controls; prompt is sent unchanged');

  // R9 empty-input behaviour
  if (spec.emptyInputReply) {
    await page.evaluate(() => { window.__captured.length = 0; });
    await page.fill('#seed', ''); await page.click('#run');
    const o = await page.$eval('#out', (e) => e.innerText), calls = await page.evaluate(() => window.__captured.length);
    check('R9', norm(o) === norm(spec.emptyInputReply) && calls === 0, 'empty input prints the fixed reply locally, no model call');
  } else {
    await page.evaluate(() => { window.__captured.length = 0; });
    await page.fill('#seed', ''); await page.click('#run');
    const calls = await page.evaluate(() => window.__captured.length);
    check('R9', calls === 0, 'empty input makes no model call');
  }

  // R10 provider error surfaces and the UI recovers
  const rErr = await runOnce(page, sample.input, { mode: '401' });
  check('R10', /invalid api key|401/i.test(rErr.out), `provider error is shown and the run button recovers ("${rErr.out.slice(0, 60).replace(/\n/g, ' ')}")`);

  // R11 panels
  const pBad = [];
  for (const [k, btn, el] of [['L', 'btnL', 'leftPanel'], ['R', 'btnR', 'rightPanel'], ['G', 'btnG', 'gearDrawer']]) {
    await page.evaluate((b) => document.getElementById(b).click(), btn);
    const open = await page.$eval('#' + el, (e) => e.classList.contains('open'));
    await page.evaluate((k2) => document.getElementById('bd' + k2).click(), k);
    const closed = await page.$eval('#' + el, (e) => !e.classList.contains('open'));
    if (!open || !closed) pBad.push(el);
  }
  check('R11', pBad.length === 0, pBad.length ? 'panels failed to toggle: ' + pBad.join(', ') : 'prompt, response and settings panels open and close');

  // R12 no horizontal overflow on a phone
  await page.setViewportSize({ width: 390, height: 800 });
  const over = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  check('R12', over <= 1, over <= 1 ? 'no horizontal overflow at 390px' : `horizontal overflow of ${over}px at 390px`);

  check('R13', errs.length === 0, errs.length ? 'runtime errors: ' + [...new Set(errs)].slice(0, 3).join(' | ') : 'no page errors or console errors');

  // ------------------------------------------------------------ contract: positives + mutation tests
  const C = spec.contract;
  if (!C) check('C0', true, 'no contract declared (free-form output)');
  else {
    const verdict = (t) => page.evaluate((x) => window.__forge.checkContract(x), t);
    const cBad = [];
    for (const [i, t] of spec.tests.entries()) {
      const v = await verdict(t.output);
      if (v.ok !== t.valid) cBad.push(`tests[${i}] expected ${t.valid ? 'valid' : 'invalid'}, checker says ${v.ok ? 'valid' : 'invalid: ' + v.issues[0]}`);
    }
    for (const f of C.fixedReplies || []) if (!(await verdict(f)).ok) cBad.push(`fixed reply rejected: "${f.slice(0, 40)}..."`);
    check('C1', cBad.length === 0, cBad.length ? cBad.join(' | ') : 'checker accepts every valid sample and fixed reply, and rejects declared-invalid samples');

    const mut = [], good = sample.output, secs = C.sections || [];
    const hk = (l) => l.replace(/^[\s>#]*(\d+[.)]\s*)?/, '').replace(/[*_`:]/g, '').trim().toUpperCase();
    const lines = good.split('\n');
    const hIdx = secs.map((s) => lines.findIndex((l) => hk(l) === s.toUpperCase()));
    if (secs.length >= 2 && hIdx.every((i) => i >= 0)) {
      mut.push(['missing header', lines.filter((_, i) => i !== hIdx[0]).join('\n')]);
      const sw = [...lines]; [sw[hIdx[0]], sw[hIdx[1]]] = [sw[hIdx[1]], sw[hIdx[0]]]; mut.push(['swapped headers', sw.join('\n')]);
      mut.push(['duplicate header', good + '\n\n' + lines[hIdx[0]] + '\nextra.']);
      mut.push(['text before first header', 'Here is the analysis.\n\n' + good]);
      const ins = (k, s) => [...lines.slice(0, hIdx[k] + 1), s, ...lines.slice(hIdx[k] + 1)].join('\n');
      if ((C.forbid || []).includes('lists')) mut.push(['list item in body', ins(0, '- a bullet point')]);
      if ((C.forbid || []).includes('bold')) mut.push(['bold in body', ins(0, 'This has **bold emphasis** inside.')]);
      if ((C.forbid || []).includes('extra-headers')) mut.push(['extra header', ins(0, '## An Extra Header')]);
      if (C.singleQuestionInLast) mut.push(['two questions in last section', ins(secs.length - 1, 'Is that one question? And is this another?')]);
    } else if (secs.length) {
      cBad.push('the valid sample must contain every section header on its own line (so mutation tests can run)');
    }
    if (C.endsWith) {
      const last = good.lastIndexOf(C.endsWith);
      mut.push([`missing final "${C.endsWith}"`, good.slice(0, last) + (C.endsWith === '.' ? ',' : '.') + good.slice(last + 1)]);
      mut.push(['trailing courtesy after the ending', good.trimEnd() + '\n\nHope this helps' + (C.endsWith === '.' ? '!' : '.')]);   // must end in a different char than the contract requires
    }
    if ((C.fixedReplies || []).length && secs.length) mut.push(['fixed reply with appended chatter', C.fixedReplies[0] + ' Let me know if you need more.']);
    const survived = [];
    for (const [name, text] of mut) { if ((await verdict(text)).ok) survived.push(name); }
    check('C2', survived.length === 0 && cBad.length === 0, survived.length ? `checker is too lenient; these broken outputs were accepted: ${survived.join(', ')}` : `checker rejected all ${mut.length} mutated outputs`);
  }
} catch (e) {
  check('R0', false, 'runtime test crashed: ' + e.message.split('\n')[0]);
} finally {
  await browser.close();
  server.close();
}
finish();
