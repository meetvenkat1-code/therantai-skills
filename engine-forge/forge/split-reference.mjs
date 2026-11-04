#!/usr/bin/env node
// Derives template/{core.js,helpers.js,style.css,shell.html,manifest.json} from the reference engine.
// Core, helpers and CSS are copied VERBATIM. Only the shell receives {{SLOTS}}. Every anchor must match exactly once.
// engine.pre.js / engine.post.js are authored by hand and never touched here.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const refPath = path.resolve(process.argv[2] || path.join(root, 'reference', 'slot-grammar-script-engine.html'));
const sha = (s) => crypto.createHash('sha256').update(s).digest('hex');
const die = (m) => { console.error('split-reference: ' + m); process.exit(1); };

const html = fs.readFileSync(refPath, 'utf8');

function between(str, a, b, label) {
  const i = str.indexOf(a);
  if (i < 0 || str.indexOf(a, i + 1) >= 0) die(`start marker for ${label} not found exactly once: ${a}`);
  const j = str.indexOf(b, i + a.length);
  if (j < 0) die(`end marker for ${label} not found: ${b}`);
  return str.slice(i, j);
}
function once(str, re, repl, label) {
  const g = new RegExp(re.source, re.flags.includes('g') ? re.flags : re.flags + 'g');
  const n = [...str.matchAll(g)].length;
  if (n !== 1) die(`anchor "${label}" matched ${n}x (need exactly 1)`);
  return str.replace(re, () => repl);
}

// ---- script regions -------------------------------------------------------
const sOpen = html.indexOf('<script>\n');
const sClose = html.lastIndexOf('</script>');
if (sOpen < 0 || sClose < 0) die('script tag not found');
const script = html.slice(sOpen + '<script>\n'.length, sClose);

const core = between(script, '/* MODEL CORE v2', 'window.EnginePanels', 'core');
const helpers = between(script, '/* storage abstraction', '/* prompt library', 'helpers');

// ---- style ----------------------------------------------------------------
const styleOpen = html.indexOf('<style>\n'), styleClose = html.indexOf('\n</style>');
if (styleOpen < 0 || styleClose < 0) die('style block not found');
const style = html.slice(styleOpen + '<style>\n'.length, styleClose);

// ---- shell ----------------------------------------------------------------
// Replace the later region first so earlier indices stay valid.
let shell = html;
shell = shell.slice(0, sOpen) + '<script>\n{{CORE}}{{ENGINE_PRE}}{{HELPERS}}{{ENGINE_POST}}' + shell.slice(sClose);
shell = shell.slice(0, styleOpen) + '<style>\n{{STYLE}}' + shell.slice(styleClose);
shell = once(shell, /<title>Slot-Grammar Script Engine<\/title>/, '<title>{{TITLE}}</title>', 'title');
shell = once(shell, /<span class="name">Slot-Grammar Script Engine<\/span>/, '<span class="name">{{TITLE}}</span>', 'header name');
shell = once(shell, /<span>Monologue<\/span>/, '<span>{{CARD_LABEL}}</span>', 'card label');
shell = once(shell, /<span class="empty">Offer a seed idea below[^<]*<\/span>/, '{{EMPTY_HTML}}', 'empty state');
shell = once(shell, /placeholder="Seed idea[^"]*"/, 'placeholder="{{PLACEHOLDER}}"', 'placeholder');
shell = once(shell, /<div class="row">[\s\S]*?<button id="run">Forge<\/button>/, '<div class="row">\n  {{CONTROLS}}\n  <button id="run">{{RUN_LABEL}}</button>', 'controls row');
shell = once(shell, /id="promptName" value="slot-grammar-script-engine"/, 'id="promptName" value="{{SLUG}}"', 'prompt name');
shell = once(shell, /<div class="mut">FIDELITY and OUTPUT_MODE lines[^<]*<\/div>/, '<div class="mut">{{PARAM_NOTE}}</div>', 'param note');

const out = path.join(root, 'template');
fs.mkdirSync(out, { recursive: true });
fs.writeFileSync(path.join(out, 'core.js'), core);
fs.writeFileSync(path.join(out, 'helpers.js'), helpers);
fs.writeFileSync(path.join(out, 'style.css'), style);
fs.writeFileSync(path.join(out, 'shell.html'), shell);
fs.writeFileSync(path.join(out, 'manifest.json'), JSON.stringify({
  reference: path.basename(refPath), coreSha256: sha(core), helpersSha256: sha(helpers), styleSha256: sha(style),
}, null, 2) + '\n');

// ---- regression fixture: the reference's own prompt ------------------------
const m = html.match(/var DEFAULT_PROMPT = (".*");\n/);
if (m) {
  const ex = path.join(root, 'examples', 'slot-grammar');
  fs.mkdirSync(ex, { recursive: true });
  fs.writeFileSync(path.join(ex, 'prompt.md'), JSON.parse(m[1]));
}
console.log(`template written from ${path.basename(refPath)}: core ${core.length}B, helpers ${helpers.length}B, style ${style.length}B, shell ${shell.length}B`);
