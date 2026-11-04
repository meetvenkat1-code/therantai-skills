// netlify/functions/openrouter.js
// Holds the real OpenRouter API key server-side (Netlify env var
// OPENROUTER_API_KEY) so visitors never see or need one. Client calls this at
// /api/openrouter with { model, messages } and no key attached; this function
// attaches the real key and forwards to OpenRouter, returning the response
// body as-is.
//
// Naming note: the engine's provider id for this route is `or-auto`
// (from model.json defaultLanes). The function file is named `openrouter.js`
// — one function per provider, clean URL — and the client maps
// or-auto → /api/openrouter (see PROXY_PATH in index.html).

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method not allowed' };
  }

  let payload;
  try { payload = JSON.parse(event.body || '{}'); }
  catch (e) { return { statusCode: 400, body: 'Invalid JSON body' }; }

  // Lightweight probe support — the client's once-per-page-load availability
  // check. Answered cheaply: no key needed, no upstream call.
  if (payload.probe) {
    return { statusCode: 200, body: JSON.stringify({ ok: true, probe: true }) };
  }

  const apiKey = process.env.OPENROUTER_API_KEY;
  if (!apiKey) {
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: 'OPENROUTER_API_KEY not set on the server. Add it in Netlify → Site settings → Environment variables, then redeploy.'
      })
    };
  }

  const { model, messages } = payload;
  if (!Array.isArray(messages)) {
    return { statusCode: 400, body: JSON.stringify({ error: 'Missing messages' }) };
  }

  try {
    const upstream = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${apiKey}` },
      body: JSON.stringify({ model, stream: true, messages })
    });
    // Netlify Functions (classic runtime) buffer the whole body rather than
    // true byte-stream passthrough. Read the full upstream stream, hand back
    // as one body — client's readStream() parses SSE-style text either way.
    const text = await upstream.text();
    return {
      statusCode: upstream.status,   // pass upstream status through UNCHANGED —
                                     // this is what lets the client detect 429s
      headers: { 'Content-Type': 'text/event-stream' },
      body: text
    };
  } catch (e) {
    return { statusCode: 502, body: JSON.stringify({ error: e.message || 'Upstream fetch failed' }) };
  }
};
