/* MODEL CORE v2 (model-config-contract). Paste verbatim. Edit only the three CONSTANTS. */
var ENGINE_NAME = 'My Engine';                                   // CONSTANT 1: shown in X-Title
var CANONICAL_CONFIG_URL = 'https://raw.githubusercontent.com/meetvenkat1-code/therantai-config/refs/heads/main/model.json';   // CONSTANT 2: never vary
var LEGACY_KEY_SLOTS = {};                                       // CONSTANT 3: read-only fallbacks, e.g. { groq: ['rl.key.gq'], openrouter: ['rl.key.or'] }
var DEFAULT_TIMEOUT_MS = 15000, DEFAULT_IDLE_MS = 3000;
var isArtifact = window.self !== window.top;

var LOCAL_FALLBACK_CONFIG = {                                    // mirrors the live model.json providers and defaultLanes (2026-10-03); model_aliases are deliberately not duplicated
  native_model: 'claude-sonnet-4-6',
  defaultLanes: ['groq::openai/gpt-oss-120b', 'or-auto::openrouter/free'],
  providers: [
    { id: 'claude', native: true, label: 'Claude · Native', dotColor: '#ef4444', requiresKey: false, defaultFor: ['artifact'] },
    { id: 'groq', native: false, label: 'Groq', dotColor: '#22c55e', requiresKey: true, keyStorageName: 'groq', keyLabel: 'Groq API Key', keyPlaceholder: 'gsk_…', defaultFor: ['standalone'],
      endpoint: 'https://api.groq.com/openai/v1/chat/completions', authHeader: 'Authorization', authPrefix: 'Bearer ', requestFormat: 'openai-chat', streamFormat: 'openai',
      modelChain: ['openai/gpt-oss-120b', 'openai/gpt-oss-20b'], softFallback: { on: [429, 500, 502, 503], within: true }, hardFallback: 'or-auto', timeoutMs: 15000, idleMs: 3000 },
    { id: 'or-auto', native: false, label: 'OR · Free Router', dotColor: '#f97316', requiresKey: true, keyStorageName: 'openrouter', keyLabel: 'OpenRouter API Key', keyPlaceholder: 'sk-or-…',
      keyNote: 'Standalone only — OpenRouter has no CORS proxy inside claude.ai', standaloneOnly: true,
      endpoint: 'https://openrouter.ai/api/v1/chat/completions', authHeader: 'Authorization', authPrefix: 'Bearer ',
      extraHeaders: { 'HTTP-Referer': '$origin', 'X-Title': '$engineName' }, requestFormat: 'openai-chat', streamFormat: 'openai', modelChain: ['openrouter/free'], softFallback: { on: [429, 500, 502, 503], within: true }, timeoutMs: 45000, idleMs: 9000 }
  ]
};
var liveModelConfig = LOCAL_FALLBACK_CONFIG;                     // boot on the floor, upgrade when the fetch lands

var sleep = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };
function natCmp(a, b) { return a.localeCompare(b, undefined, { numeric: true }); }
function cfgProviders() { return liveModelConfig.providers; }
function P(id) { return cfgProviders().filter(function (p) { return p.id === id; })[0] || null; }
function splitKey(k) { var i = k.indexOf('::'); return { provider: k.slice(0, i), model: k.slice(i + 2) }; }

function isValidConfig(j) {
  if (!j || !Array.isArray(j.providers) || !j.providers.length) return false;
  var ids = {}, natives = 0, usable = false;
  for (var i = 0; i < j.providers.length; i++) {
    var p = j.providers[i];
    if (!p || !p.id || !p.label || ids[p.id]) return false;
    ids[p.id] = 1;
    if (p.native === true) { natives++; if (isArtifact) usable = true; }
    else if (p.endpoint && p.requestFormat === 'openai-chat' && !(p.standaloneOnly && isArtifact)) usable = true;
  }
  return natives <= 1 && usable;                                 // never adopt a half-valid config
}
function usableProviders() {                                     // native only inside claude.ai; standalone never routes it
  return cfgProviders().filter(function (p) { return p.native === true ? isArtifact : !(p.standaloneOnly && isArtifact); });
}
function defaultLanes() {                                        // the floor: config's defaultLanes, else first model of the first usable provider
  var ok = usableProviders().map(function (p) { return p.id; });
  var list = (liveModelConfig.defaultLanes || []).filter(function (k) {
    if (k.indexOf('::') < 1) return false; var s = splitKey(k); return ok.indexOf(s.provider) > -1 && !P(s.provider).native;
  });
  if (!list.length) {
    var p = usableProviders().filter(function (x) { return !x.native && x.modelChain && x.modelChain.length; })[0];
    if (p) list = [p.id + '::' + p.modelChain[0]];
  }
  return list;
}

function getKey(name) {
  try {
    var v = localStorage.getItem('hek_' + name); if (v) return v.trim();
    var old = LEGACY_KEY_SLOTS[name] || [];
    for (var i = 0; i < old.length; i++) { var o = localStorage.getItem(old[i]); if (o) return o.trim(); }
  } catch (e) {}
  return '';
}
function setKey(name, value) { try { localStorage.setItem('hek_' + name, (value || '').trim()); } catch (e) {} }

function headersFor(cfg, key) {                                  // CHAT requests only (POST /chat/completions). The picker's GET /models does NOT use this: it uses catalogHeaders (model-catalog-panel v3.2), because these headers force a CORS preflight on a cross-origin GET
  var h = { 'Content-Type': 'application/json' };
  if (key && cfg.authHeader) h[cfg.authHeader] = (cfg.authPrefix || '') + key;
  Object.keys(cfg.extraHeaders || {}).forEach(function (k) {
    var v = cfg.extraHeaders[k];
    h[k] = v === '$origin' ? (window.location.origin !== 'null' ? window.location.origin : 'http://localhost') : v === '$engineName' ? ENGINE_NAME : v;
  });
  return h;
}
function retryAfterSeconds(res, msg) {                           // header first, then Groq's "try again in 26.6s / 1m3.5s / 250ms"
  var ra = parseFloat(res.headers && res.headers.get && res.headers.get('retry-after')); if (!isNaN(ra)) return ra;
  var m = /try again in\s+([0-9hms.]+)/i.exec(msg || ''); if (!m) return null;
  var t = 0; m[1].replace(/(\d+(?:\.\d+)?)(ms|h|m|s)/g, function (_, n, u) { t += parseFloat(n) * { ms: 0.001, s: 1, m: 60, h: 3600 }[u]; });
  return t || null;
}

function buildRequest(cfg, modelId, system, user, stream, maxTokens) {
  if (cfg.native === true) {                                     // HARDCODED BRANCH. Never built from cfg fields.
    return { url: 'https://api.anthropic.com/v1/messages',
      headers: { 'Content-Type': 'application/json', 'anthropic-version': '2023-06-01', 'anthropic-dangerous-direct-browser-access': 'true' },
      body: { model: modelId, max_tokens: maxTokens || 4000, stream: stream, system: system || '', messages: [{ role: 'user', content: user }] } };
  }
  if (cfg.requestFormat !== 'openai-chat') throw new Error('Unknown requestFormat: ' + cfg.requestFormat);
  var h = headersFor(cfg, getKey(cfg.keyStorageName));
  var body = { model: modelId, stream: stream, messages: (system ? [{ role: 'system', content: system }] : []).concat([{ role: 'user', content: user }]) };
  if (maxTokens) body.max_tokens = maxTokens;
  return { url: cfg.endpoint, headers: h, body: body };
}

function readStream(res, format, onChunk, timeoutMs, idleMs, signal) {   // resolves { reason, error }; never rejects
  var rd = res.body.getReader(), dec = new TextDecoder(), buf = '', done = false, idleT, hardT, reason = null, err = null;
  timeoutMs = timeoutMs || DEFAULT_TIMEOUT_MS; idleMs = idleMs || DEFAULT_IDLE_MS;
  return new Promise(function (resolve) {
    function finish() { if (done) return; done = true; clearTimeout(idleT); clearTimeout(hardT); try { rd.cancel(); } catch (e) {} resolve({ reason: reason, error: err }); }
    function resetIdle() { clearTimeout(idleT); idleT = setTimeout(finish, idleMs); }
    hardT = setTimeout(finish, timeoutMs); resetIdle();
    if (signal) { if (signal.aborted) return finish(); signal.addEventListener('abort', finish, { once: true }); }
    (function pump() {
      if (done) return;
      rd.read().then(function (r) {
        if (done) return;
        if (r.done) return finish();
        buf += dec.decode(r.value, { stream: true });
        var lines = buf.split('\n'); buf = lines.pop();
        for (var i = 0; i < lines.length; i++) {
          var t = lines[i].trim();
          if (format === 'anthropic' && t === 'event: message_stop') return finish();   // named event line precedes its data: line
          if (t.indexOf('data:') !== 0) continue;
          var d = t.slice(5).trim(); if (d === '[DONE]') return finish();
          try {
            var p = JSON.parse(d);
            if (p.error) { err = (p.error.message || 'stream error'); return finish(); }
            if (format === 'anthropic') {
              if (p.type === 'content_block_delta' && p.delta && p.delta.text) { onChunk(p.delta.text, null); resetIdle(); }
              else if (p.type === 'message_delta' && p.delta && p.delta.stop_reason) reason = p.delta.stop_reason === 'max_tokens' ? 'length' : p.delta.stop_reason;
              else if (p.type === 'message_stop') return finish();
            } else {
              var c0 = p.choices && p.choices[0], dl = c0 && c0.delta;
              if (c0 && c0.finish_reason) reason = c0.finish_reason;
              if (dl && dl.content) { onChunk(dl.content, p.model || null); resetIdle(); }
              else if (dl && (dl.reasoning || dl.reasoning_content)) resetIdle();   // thinking counts as alive
            }
          } catch (e) {}
        }
        pump();
      }).catch(finish);
    })();
  });
}

/* ONE call layer, two modes.
   curated: callModel({ provider, system, user, onText, validate })         -> walks modelChain, soft/hard fallback
   strict : callModel({ provider, model, system, user, onText, maxTokens }) -> exactly that model, never falls through (lanes, panels)
   onText(accumulatedText, servedModelOrNull) fires on every chunk. Returns { text, model, served, cut }. */
async function callModel(o) {
  var cfg = P(o.provider), strict = !!o.model;
  if (!cfg) throw new Error('Unknown provider: ' + o.provider);
  if (cfg.standaloneOnly && isArtifact) throw new Error(cfg.label + ' is standalone only. It has no proxy inside claude.ai.');
  if (cfg.requiresKey && !getKey(cfg.keyStorageName)) throw new Error('No ' + (cfg.keyLabel || cfg.label) + ' saved. Open settings.');
  var models = strict ? [o.model] : (o.chain || (cfg.native ? [liveModelConfig.native_model] : cfg.modelChain) || []);
  var lastStatus = null, lastRetry = null;
  function fail(m) { var e = new Error(m); e.status = lastStatus; e.retryAfter = lastRetry; return e; }   // lets a panel engine show a 429 countdown
  function aborted() { if (o.signal && o.signal.aborted) { var e = new Error('Aborted'); e.name = 'AbortError'; throw e; } }
  var advance = ((cfg.softFallback && cfg.softFallback.on) || [429, 500, 502, 503]).concat([400, 404, 422]);
  var last = '';
  for (var i = 0; i < models.length; i++) {
    var retried = false, folded = false, fatal = null;
    for (var a = 0; a < 3; a++) {
      aborted();
      var acc = '', served = null, res;
      var sys = folded ? '' : o.system, usr = folded ? (o.system ? o.system + '\n\n---\n\n' : '') + o.user : o.user;
      try {
        var rq = buildRequest(cfg, models[i], sys, usr, true, o.maxTokens);
        res = await fetch(rq.url, { method: 'POST', headers: rq.headers, body: JSON.stringify(rq.body), signal: o.signal });
      } catch (e) { if (e && e.name === 'AbortError') throw e; last = cfg.id + ': network error ' + e.message; break; }
      if (!res.ok) {
        var msg = ''; try { var eb = await res.json(); msg = (eb.error && eb.error.message) || ''; } catch (e) {}
        lastStatus = res.status; lastRetry = retryAfterSeconds(res, msg);
        if (res.status === 429 && !retried) { retried = true; await sleep(1800); continue; }                       // one retry, then advance
        if (res.status === 400 && !folded && /system|developer|instruction/i.test(msg)) { folded = true; continue; }   // model rejects the system role
        last = cfg.id + ':' + res.status + (msg ? ' ' + String(msg).slice(0, 140) : '') + (res.status === 404 ? ' — model not found, refresh the catalog' : '');
        if (advance.indexOf(res.status) < 0) fatal = last;                                                          // 401/402/403/413: another model will not heal it
        break;
      }
      var out = await readStream(res, cfg.native === true ? 'anthropic' : (cfg.streamFormat || 'openai'), function (c, s) { acc += c; if (s) served = s; if (o.onText) o.onText(acc, served); }, cfg.timeoutMs, cfg.idleMs, o.signal);
      aborted();
      if (!acc.trim()) { last = cfg.id + ': empty reply' + (out.reason === 'length' ? ' — the token cap was spent on reasoning' : out.error ? ' — ' + out.error : ''); break; }
      if (o.validate && !cfg.native) { try { o.validate(acc); } catch (e) { last = cfg.id + ': rejected — ' + e.message; break; } }
      return { text: acc, model: models[i], served: served, cut: out.reason === 'length' };
    }
    if (fatal) throw fail(fatal);                                                                              // stops everything, hardFallback included
  }
  var hf = !strict && !o._noHard && cfg.hardFallback ? P(cfg.hardFallback) : null;                                 // strict calls never reach here: lane honesty
  if (hf) {
    if (hf.standaloneOnly && isArtifact) throw new Error('All providers exhausted (' + last + '). The fallback (' + hf.label + ') is standalone only.');
    if (hf.requiresKey && !getKey(hf.keyStorageName)) throw new Error('Provider unavailable (' + last + '). Fallback ' + hf.label + ' has no key.');
    return callModel({ provider: hf.id, chain: hf.modelChain, system: o.system, user: o.user, onText: o.onText, validate: o.validate, maxTokens: o.maxTokens, _noHard: true });
  }
  throw fail(strict ? last : 'Provider unavailable (' + last + ')');
}

function fetchModelConfig(onApplied) {                           // call once on load, after rendering from the floor
  return fetch(CANONICAL_CONFIG_URL + '?v=' + Date.now())
    .then(function (r) { if (!r.ok) throw new Error('Config fetch failed: ' + r.status); return r.json(); })
    .then(function (j) { if (!isValidConfig(j)) throw new Error('Malformed config'); liveModelConfig = j; return 'live'; })
    .catch(function () { liveModelConfig = LOCAL_FALLBACK_CONFIG; return 'fallback'; })
    .then(function (src) { if (onApplied) onApplied(src); return src; });
}

var KNOWN_MODEL_ALIASES = { 'mistralai/mistral-large': 'mistralai/mistral-large-2411', 'meta-llama/llama-3-70b-instruct': 'meta-llama/llama-3.3-70b-instruct' };
function modelAliases() { return Object.assign({}, KNOWN_MODEL_ALIASES, liveModelConfig.model_aliases || {}); }
function modelIdBase(id) { var q = id.split('-'); while (q.length > 1 && /^(v?\d[\d.]*|\d{4,})$/i.test(q[q.length - 1])) q.pop(); return q.join('-'); }
function resolveModelId(id, live) {                              // only against a catalog the user actually fetched; never across providers
  if (!live || !live.length || live.indexOf(id) > -1) return { id: id, status: 'ok' };
  var al = modelAliases()[id]; if (al && live.indexOf(al) > -1) return { id: al, status: 'alias' };
  var base = modelIdBase(id), c = live.filter(function (x) { return modelIdBase(x) === base; });
  if (c.length) return { id: c.sort(natCmp).reverse()[0], status: 'fuzzy' };
  return { id: id, status: 'unresolved' };
}
