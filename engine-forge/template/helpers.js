/* storage abstraction (UI Contract 21): window.storage in artifacts, localStorage standalone */
async function sGet(k){ try{ if(isArtifact){ var r = await window.storage.get(k); return r ? r.value : null; } return localStorage.getItem(k); }catch(e){ return null; } }
async function sSet(k,v){ try{ if(isArtifact){ await window.storage.set(k,v); } else localStorage.setItem(k,v); return true; }catch(e){ return false; } }
async function sList(p){ try{ if(isArtifact){ var r = await window.storage.list(p); return r ? r.keys : []; } var a=[]; for(var i=0;i<localStorage.length;i++){ var k=localStorage.key(i); if(k && k.indexOf(p)===0) a.push(k); } return a; }catch(e){ return []; } }

/* markdown (UI Contract 02): innerHTML + parser, escape first, rendered per chunk */
function esc(s){ return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function inl(s){ return s.replace(/`([^`]+)`/g,'<code>$1</code>').replace(/\*\*\*(.+?)\*\*\*/g,'<strong><em>$1</em></strong>').replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>').replace(/(^|[\s(])[*_]([^*_\n]+)[*_](?=[\s).,;:!?]|$)/g,'$1<em>$2</em>'); }
function renderMarkdown(t){
  var parts = esc(t).split(/```[a-z]*\n?/), html = '';
  parts.forEach(function(seg,i){
    if(i%2){ html += '<pre><code>'+seg.replace(/\n$/,'')+'</code></pre>'; return; }
    seg.split(/\n{2,}/).forEach(function(b){
      b = b.trim(); if(!b) return;
      if(/^---+$/.test(b)) html += '<hr>';
      else if(/^#{1,3} /.test(b)){ var n=b.match(/^#+/)[0].length; html += '<h'+n+'>'+inl(b.replace(/^#+ /,''))+'</h'+n+'>'; }
      else if(/^([-*]) /.test(b)) html += '<ul>'+b.split('\n').map(function(l){ return '<li>'+inl(l.replace(/^[-*] /,''))+'</li>'; }).join('')+'</ul>';
      else if(/^\d+\. /.test(b)) html += '<ol>'+b.split('\n').map(function(l){ return '<li>'+inl(l.replace(/^\d+\. /,''))+'</li>'; }).join('')+'</ol>';
      else html += '<p>'+inl(b).replace(/\n/g,'<br>')+'</p>';
    });
  });
  return html;
}

/* canonical copy (UI Contract 05), sole transport */
function copyToClipboard(text, btn) {
  if (!text || !text.trim()) return;
  var origHTML = btn.innerHTML;
  var ICON_CHECK = '<svg viewBox="0 0 24 24" style="width:11px;height:11px;stroke:currentColor;fill:none;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round"><polyline points="20 6 9 17 4 12"></polyline></svg>';
  function onSuccess() { btn.innerHTML = ICON_CHECK + ' Copied'; btn.classList.add('copied'); setTimeout(function(){ btn.innerHTML=origHTML; btn.classList.remove('copied'); },2000); }
  function onFail() { btn.textContent = '✗ Failed'; setTimeout(function(){ btn.innerHTML=origHTML; },2000); }
  function execCopy() {
    var ta = document.createElement('textarea'); ta.value = text;
    ta.style.cssText = 'position:fixed;left:-9999px;top:-9999px;opacity:0;font-size:12px;pointer-events:none;';
    ta.setAttribute('readonly','');
    document.body.appendChild(ta); ta.focus(); ta.select(); ta.setSelectionRange(0,text.length);
    var ok=false; try{ ok=document.execCommand('copy'); }catch(e){}
    document.body.removeChild(ta); ok ? onSuccess() : onFail();
  }
  if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(text).then(onSuccess).catch(execCopy); }
  else { execCopy(); }
}
function liveText(){ return $('out').innerText.trim(); }
function download(name, text, type){ var a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([text],{type:type||'text/plain'})); a.download=name; document.body.appendChild(a); a.click(); document.body.removeChild(a); setTimeout(function(){ URL.revokeObjectURL(a.href); },1000); }

/* provider layer (rendered from config; Model Core owns the rest) */
function getSelectedProvider(){ var s=$('providerSelect'); return (s && s.value) || defaultProviderId(); }
function providerBlockedHere(id){ var p=P(id); return !!(p && p.standaloneOnly && isArtifact); }
function defaultProviderId(){ var ps=usableProviders(), want=isArtifact?'artifact':'standalone'; var d=ps.filter(function(p){ return (p.defaultFor||[]).indexOf(want)>-1; })[0]||ps[0]; return d && d.id; }
function updateProviderDot(){ var p=P($('providerSelect').value); $('providerDot').style.background=(p && p.dotColor)||'#9090a8'; }
function renderProviderSelector(){ var sel=$('providerSelect'), keep=sel.value; sel.innerHTML=''; usableProviders().forEach(function(p){ sel.appendChild(new Option(p.label,p.id)); }); sel.value=usableProviders().some(function(p){ return p.id===keep; })?keep:defaultProviderId(); updateProviderDot(); updateBanner(); }
function updateBanner(){
  var p=P(getSelectedProvider()), b=$('banner'), msg='';
  if(p && !p.native){ if(p.standaloneOnly && isArtifact) msg=p.keyNote||'Standalone only.'; else if(p.requiresKey && !getKey(p.keyStorageName)) msg='No '+(p.keyLabel||p.label)+' saved. Open ⚙ settings to add one.'; }
  b.textContent=msg; b.classList.toggle('on',!!msg);
}
function renderDrawerKeyRows(){
  var c=$('drawerKeyRows'); c.innerHTML='';
  cfgProviders().forEach(function(p){
    var row=document.createElement('div'); row.style.marginBottom='12px';
    var lab=document.createElement('div'); lab.textContent=p.keyLabel||p.label; row.appendChild(lab);
    if(!p.requiresKey){ var n=document.createElement('div'); n.className='mut'; n.textContent='No key needed — platform routes natively'; row.appendChild(n); c.appendChild(row); return; }
    var inp=document.createElement('input'); inp.type='password'; inp.placeholder=p.keyPlaceholder||''; inp.value=getKey(p.keyStorageName); row.appendChild(inp);
    if(p.keyNote){ var kn=document.createElement('div'); kn.className='note'; kn.textContent=p.keyNote; row.appendChild(kn); }
    var sv=document.createElement('button'); sv.className='copy-btn'; sv.textContent='Save'; sv.style.marginTop='6px';
    sv.addEventListener('click',function(){ setKey(p.keyStorageName,inp.value); sv.textContent='✓ Saved'; updateBanner(); setTimeout(function(){ sv.textContent='Save'; setPanel('G',false); },1500); });
    row.appendChild(sv); c.appendChild(row);
  });
}
function setCfgBadge(src){ var b=$('cfgBadge'); b.textContent='Config: '+(src==='live'?'Live':'Local Fallback'); b.classList.toggle('live',src==='live'); }

/* panels (UI Contract 01): independent backdrop + toggle per panel */
function setPanel(k,open){ var el=k==='L'?$('leftPanel'):k==='R'?$('rightPanel'):$('gearDrawer'); el.classList.toggle('open',open); $('bd'+k).classList.toggle('on',open); }
function bindPanel(k,btn){ $(btn).addEventListener('click',function(){ var el=k==='L'?$('leftPanel'):k==='R'?$('rightPanel'):$('gearDrawer'); setPanel(k,!el.classList.contains('open')); if(k==='R') renderResponses(); }); $('bd'+k).addEventListener('click',function(){ setPanel(k,false); }); }

