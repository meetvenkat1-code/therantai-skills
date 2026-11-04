window.EnginePanels = { library:true, importExport:true, settings:true };
var SPEC = {{SPEC_JSON}};
ENGINE_NAME = SPEC.title;
var DEFAULT_PROMPT = {{PROMPT_JSON}};
var PROMPT_SLUG = SPEC.slug;
var $ = function(id){ return document.getElementById(id); };
var running = false, lastText = '', lastSeed = '', promptEntry = null;
var CTL = {};
SPEC.controls.forEach(function(c){ CTL[c.key] = c.default; });

