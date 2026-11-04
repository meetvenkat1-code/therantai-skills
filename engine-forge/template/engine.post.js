/* prompt library: the system prompt is an editable entry, never a sealed constant (Hybrid Contract) */
async function loadPrompt(){
  var raw = await sGet('prompts:'+PROMPT_SLUG), e = null;
  try{ e = raw ? JSON.parse(raw) : null; }catch(x){}
  promptEntry = e || { name:PROMPT_SLUG, triggers:SPEC.triggers, description:SPEC.description, body:DEFAULT_PROMPT, source:'manual', imported:new Date().toISOString() };
  $('promptName').value = promptEntry.name; $('promptBody').value = promptEntry.body;
}
async function savePrompt(entry){ promptEntry = entry; await sSet('prompts:'+PROMPT_SLUG, JSON.stringify(entry)); $('promptName').value=entry.name; $('promptBody').value=entry.body; }

/* controls: each control owns exactly one "KEY = value" line of the system prompt */
function decimals(c){ return (String(c.step).split('.')[1]||'').length; }
function ctlStr(c){ return c.type==='slider' ? Number(CTL[c.key]).toFixed(decimals(c)) : String(CTL[c.key]); }
function bandFor(c, v){ for(var i=0;i<c.bands.length;i++){ if(v<=c.bands[i][0]) return c.bands[i][1]; } return c.bands[c.bands.length-1][1]; }
function syncControls(){
  SPEC.controls.forEach(function(c,i){
    if(c.type==='slider'){
      var v = parseFloat($('ctl'+i).value); CTL[c.key] = v;
      $('ctl'+i+'v').textContent = v.toFixed(decimals(c));
      if(c.bands && c.bands.length) $('ctl'+i+'b').textContent = bandFor(c, v);
    }else{
      Array.prototype.forEach.call(document.querySelectorAll('[data-ctl="'+c.key+'"]'), function(b){ b.classList.toggle('on', b.dataset.v===String(CTL[c.key])); });
    }
  });
}
function applyParams(p){
  if(!p) return;
  SPEC.controls.forEach(function(c,i){ if(p[c.key]!==undefined){ CTL[c.key] = c.type==='slider' ? parseFloat(p[c.key]) : p[c.key]; if(c.type==='slider') $('ctl'+i).value = CTL[c.key]; } });
  syncControls();
}
function buildSystem(){
  var s = $('promptBody').value;
  SPEC.controls.forEach(function(c){ s = s.replace(new RegExp('^'+c.key+'\\s*=.*$','m'), function(){ return c.key+' = '+ctlStr(c); }); });
  return s;
}

/* contract: machine-checkable output rules declared in the spec (all fields optional) */
function normQ(s){ return String(s).replace(/[\u2018\u2019]/g,"'").replace(/[\u201C\u201D]/g,'"').replace(/\s+/g,' ').trim(); }
function headerKey(line){ return line.replace(/^[\s>#]*(\d+[.)]\s*)?/,'').replace(/[*_`:]/g,'').trim().toUpperCase(); }
function checkContract(text){
  var C = SPEC.contract;
  if(!C) return { ok:true, kind:'free', found:0, total:0, issues:[], summary:'' };
  var t = String(text).trim(), issues = [];
  var fixed = (C.fixedReplies||[]).map(normQ);
  if(fixed.indexOf(normQ(t))>-1) return { ok:true, kind:'fixed', found:0, total:0, issues:[], summary:'fixed reply ✓' };
  var secs = (C.sections||[]).map(function(s){ return s.toUpperCase(); });
  var lines = t.split('\n'), first = {}, count = {}, isHdr = [], lastHdrLine = -1;
  lines.forEach(function(l,i){
    var j = secs.indexOf(headerKey(l)); isHdr[i] = j>-1;
    if(j>-1){ count[j] = (count[j]||0)+1; if(first[j]===undefined) first[j] = i; lastHdrLine = i; }
  });
  var found = 0, prev = -1;
  secs.forEach(function(s,j){
    if(first[j]===undefined){ issues.push('missing header '+s); return; }
    found++;
    if(count[j]>1) issues.push('duplicate header '+s);
    if(first[j] < prev) issues.push('out of order: '+s);
    prev = Math.max(prev, first[j]);
  });
  if(secs.length && C.noPreface!==false){
    var firstIdx = Math.min.apply(null, Object.keys(first).map(function(k){ return first[k]; }));
    if(isFinite(firstIdx) && lines.slice(0,firstIdx).join('').trim()) issues.push('text before first header');
  }
  var forbid = C.forbid||[];
  lines.forEach(function(l,i){
    if(isHdr[i]) return;
    if(forbid.indexOf('lists')>-1 && /^\s*([-*•]|\d+[.)])\s+/.test(l)) issues.push('list item in body');
    if(forbid.indexOf('bold')>-1 && /\*\*[^*\n]+\*\*/.test(l)) issues.push('bold in body');
    if(forbid.indexOf('extra-headers')>-1 && /^\s*#{1,6}\s/.test(l)) issues.push('extra header');
  });
  if(C.endsWith && t.slice(-1)!==C.endsWith) issues.push('does not end with '+C.endsWith);
  if(C.singleQuestionInLast && secs.length && first[secs.length-1]!==undefined){
    var lastBody = lines.slice(first[secs.length-1]+1).join('\n');
    var qn = (lastBody.match(/\?/g)||[]).length;
    if(qn!==1) issues.push('last section has '+qn+' question marks (need 1)');
  }
  var uniq = issues.filter(function(x,i){ return issues.indexOf(x)===i; });
  var kind = secs.length ? 'structured' : 'free';
  return { ok:uniq.length===0, kind:kind, found:found, total:secs.length, issues:uniq,
           summary: (secs.length ? found+'/'+secs.length+' sections' : 'contract')+(uniq.length ? ' ✗ '+uniq[0] : ' ✓') };
}
window.__forge = { SPEC:SPEC, checkContract:checkContract, buildSystem:buildSystem, controls:function(){ return Object.assign({},CTL); } };

/* response library: auto-saves on completion, tagged with source prompt (UI Contract 20) */
async function saveResponse(text){
  var id = 'r'+Date.now().toString(36);
  var e = { id:id, name:lastSeed.slice(0,60), promptSlug:PROMPT_SLUG, params:Object.assign({},CTL), input:lastSeed, output:text, created:new Date().toISOString() };
  await sSet('responses:'+id, JSON.stringify(e));
}
async function allResponses(){ var ks = await sList('responses:'), out=[]; for(var i=0;i<ks.length;i++){ var v = await sGet(ks[i]); try{ if(v) out.push(JSON.parse(v)); }catch(e){} } return out.sort(function(a,b){ return a.created<b.created?1:-1; }); }
function paramsOf(r){
  var p = r.params ? Object.assign({},r.params) : {};
  if(!r.params){ if(r.fidelity!==undefined) p.FIDELITY = r.fidelity; if(r.mode!==undefined) p.OUTPUT_MODE = r.mode; }
  return p;
}
async function renderResponses(){
  var list = await allResponses(), c = $('rList'); c.innerHTML='';
  if(!list.length){ c.innerHTML='<div class="mut">No responses yet.</div>'; return; }
  list.forEach(function(r){
    var d=document.createElement('div'); d.className='item'; d.innerHTML='<b></b><small></small>';
    var p = paramsOf(r), meta = Object.keys(p).map(function(k){ return k.toLowerCase()+' '+p[k]; });
    d.firstChild.textContent = r.name||'(untitled)';
    d.lastChild.textContent = [r.created.slice(0,16).replace('T',' ')].concat(meta).join(' · ');
    d.addEventListener('click',function(){ $('out').innerHTML=renderMarkdown(r.output); lastText=r.output; lastSeed=r.input; $('seed').value=r.input; applyParams(p); stat(r.output, true); setPanel('R',false); });
    c.appendChild(d);
  });
}
function pickFile(inp, cb){ inp.value=''; inp.onchange=function(){ var f=inp.files[0]; if(!f) return; var rd=new FileReader(); rd.onload=function(){ cb(String(rd.result), f.name); }; rd.readAsText(f); }; inp.click(); }

/* run: one call, curated mode, accumulated text (Hybrid Contract; no Promise.all) */
function stat(t, final){
  var s = t.split(/\n```/)[0];
  var parts = [ s.trim().split(/\s+/).filter(Boolean).length+' words' ];
  if(final && SPEC.contract){ var r = checkContract(t); if(r.summary) parts.push(r.summary); }
  $('stat').textContent = parts.join(' · ');
}
async function run(){
  if(running) return;
  var seed = $('seed').value.trim();
  if(!seed){
    if(SPEC.emptyInputReply){ lastSeed=''; lastText=SPEC.emptyInputReply; $('out').innerHTML=renderMarkdown(lastText); $('stat').textContent='fixed reply · no model call'; }
    return;
  }
  var pid = getSelectedProvider();
  if(providerBlockedHere(pid)){ updateBanner(); return; }
  running = true; $('run').disabled = true; $('run').textContent = SPEC.runBusyLabel; lastSeed = seed; $('out').innerHTML='<span class="empty">'+esc(SPEC.busyText)+'</span>';
  try{
    var r = await callModel({ provider:pid, system:buildSystem(), user:seed, onText:function(acc){ $('out').innerHTML = renderMarkdown(acc); lastText = acc; stat(acc, false); $('outArea').scrollTop = 0; } });
    lastText = r.text; $('out').innerHTML = renderMarkdown(r.text); stat(r.text, true);
    await saveResponse(r.text);
  }catch(e){ $('out').innerHTML = '<p style="color:var(--coral)">'+esc(e.message||String(e))+'</p>'; }
  running = false; $('run').disabled = false; $('run').textContent = SPEC.runLabel;
}

/* boot */
syncControls(); bindPanel('L','btnL'); bindPanel('R','btnR'); bindPanel('G','btnG');
SPEC.controls.forEach(function(c,i){
  if(c.type==='slider'){ $('ctl'+i).addEventListener('input',syncControls); }
  else{ Array.prototype.forEach.call(document.querySelectorAll('[data-ctl="'+c.key+'"]'), function(b){ b.addEventListener('click',function(){ CTL[c.key]=b.dataset.v; syncControls(); }); }); }
});
$('run').addEventListener('click',run);
$('seed').addEventListener('keydown',function(e){ if(e.key==='Enter' && (e.ctrlKey||e.metaKey)){ e.preventDefault(); run(); } });
$('providerSelect').addEventListener('change',function(){ updateProviderDot(); updateBanner(); });
$('copyAll').addEventListener('click',function(){ copyToClipboard(lastText||liveText(), this); });
$('copyCard').addEventListener('click',function(){ copyToClipboard(liveText(), this); });
$('expTxt').addEventListener('click',function(){ var t=lastText||liveText(); if(t) download(PROMPT_SLUG+'-'+Date.now()+'.txt', t); });
$('clearKeys').addEventListener('click',function(){ try{ cfgProviders().forEach(function(p){ if(p.keyStorageName){ localStorage.removeItem('hek_'+p.keyStorageName); (LEGACY_KEY_SLOTS[p.keyStorageName]||[]).forEach(function(o){ localStorage.removeItem(o); }); } }); }catch(e){} renderDrawerKeyRows(); updateBanner(); });
$('pSave').addEventListener('click',function(){ var e=Object.assign({},promptEntry,{ name:$('promptName').value||PROMPT_SLUG, body:$('promptBody').value }); savePrompt(e); });
$('pReset').addEventListener('click',function(){ savePrompt(Object.assign({},promptEntry,{ body:DEFAULT_PROMPT })); });
$('pImp').addEventListener('click',function(){ pickFile($('fMd'),function(t,n){ savePrompt(Object.assign({},promptEntry,{ body:t, source:'markdown', imported:new Date().toISOString(), name:n.replace(/\.\w+$/,'') })); }); });
$('pExp').addEventListener('click',function(){ download('prompts-'+PROMPT_SLUG+'.json', JSON.stringify([Object.assign({},promptEntry,{ body:$('promptBody').value })],null,2),'application/json'); });
$('pImpJ').addEventListener('click',function(){ pickFile($('fPJ'),function(t){ try{ var a=JSON.parse(t); if(Array.isArray(a) && a[0]) savePrompt(Object.assign({},promptEntry,a[0],{ imported:new Date().toISOString() })); }catch(e){} }); });
$('rExp').addEventListener('click',async function(){ download('responses-'+PROMPT_SLUG+'.json', JSON.stringify(await allResponses(),null,2),'application/json'); });
$('rImp').addEventListener('click',function(){ pickFile($('fRJ'),async function(t){ try{ var a=JSON.parse(t); for(var i=0;i<a.length;i++){ if(a[i] && a[i].id && !(await sGet('responses:'+a[i].id))) await sSet('responses:'+a[i].id, JSON.stringify(a[i])); } renderResponses(); }catch(e){} }); });
renderProviderSelector(); renderDrawerKeyRows(); loadPrompt();
fetchModelConfig(function(src){ renderProviderSelector(); renderDrawerKeyRows(); setCfgBadge(src); });
