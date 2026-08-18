  (function(){
  "use strict";
  const $ = (id)=>document.getElementById(id);
  const DEFAULTS = {mode:'contour',engine:'auto',colors:8,bg:'none',smooth:0.5,corner:60,seam:0.5,cell:0,shape:'auto',gap:0.15,seed:1,upscale:1,vtracer_preset:'poster',vtracer_mode:'spline',vtracer_color_precision:8,vtracer_filter_speckle:0};
  const state = {file:null,svg:'',busy:false,objUrl:null,thumbUrl:null,dims:null,engineInfo:null,progressTimer:null,schema:null,history:[],idx:0,compareOn:false,controller:null};
  const ZOOM = 4;
  const zoomEl = $('zoom');
  const zoomLabel = $('zoomLabel');

  function esc(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
  function fmtBytes(n){if(n==null)return '—';if(n<1024)return n+' B';if(n<1048576)return (n/1024).toFixed(1)+' KB';return (n/1048576).toFixed(2)+' MB';}

  function upscaleFile(file, scale){
    return new Promise((resolve, reject)=>{
      const url = URL.createObjectURL(file);
      const img = new Image();
      img.onload = ()=>{
        const canvas = document.createElement('canvas');
        canvas.width = img.naturalWidth * scale;
        canvas.height = img.naturalHeight * scale;
        const ctx = canvas.getContext('2d');
        ctx.imageSmoothingEnabled = true;
        ctx.imageSmoothingQuality = 'high';
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        URL.revokeObjectURL(url);
        canvas.toBlob((blob)=>{
          if(!blob){ reject(new Error('toBlob')); return; }
          if(blob.size > 20*1024*1024){ reject(new Error('limit')); return; }
          resolve(new File([blob], file.name, {type:'image/png'}));
        }, 'image/png');
      };
      img.onerror = ()=>{ URL.revokeObjectURL(url); reject(new Error('decode')); };
      img.src = url;
    });
  }

  async function checkHealth(){
    try{
      const r = await fetch('/health');
      const d = await r.json();
      const ok = !!d.vtracer_available;
      state.engineInfo = {vtracer: ok};
      const el = $('status');
      el.textContent = ok ? 'vtracer: доступен' : 'vtracer: не установлен (native-трассер)';
      el.classList.add(ok?'ok':'warn');
    }catch(e){
      const el = $('status');
      el.textContent = 'Не удалось проверить движок';
      el.classList.add('warn');
    }
    syncEngineOpts();
  }

  async function loadDefaults(){
    // Single source of truth: ranges/choices/defaults come from GET /defaults
    // (server reads them from raster_to_svg.PARAMS). HTML attributes stay as
    // an offline fallback.
    try{
      const r = await fetch('/defaults');
      if(!r.ok) throw new Error('defaults status ' + r.status);
      const d = await r.json();
      const P = d.params;
      if(!P || typeof P !== 'object') throw new Error('bad defaults payload');
      state.schema = P;
      for(const [k, s] of Object.entries(P)){
        const el = $(k);
        if(!el) continue;
        const ui = s.ui || {};
        if(s.type === 'int' || s.type === 'float'){
          if(ui.min !== undefined) el.min = ui.min;
          else if(s.min !== undefined) el.min = s.min;
          if(ui.max !== undefined) el.max = ui.max;
          else if(s.max !== undefined) el.max = s.max;
          if(ui.step !== undefined) el.step = ui.step;
        }else if(s.type === 'choice' && el.tagName === 'SELECT'){
          const existing = Array.from(el.options).map(o=>o.value);
          for(const c of s.choices){
            if(!existing.includes(c)){
              const o = document.createElement('option');
              o.value = c; o.textContent = c;
              el.appendChild(o);
            }
          }
        }
        const dv = ui.default !== undefined ? ui.default : s.default;
        if(dv !== undefined && dv !== null) DEFAULTS[k] = dv;
      }
    }catch(e){
      // offline: keep HTML defaults and DEFAULTS fallback
    }
    applySettings(DEFAULTS);
    let saved = null;
    try{ saved = JSON.parse(localStorage.getItem('r2s.settings.v1') || 'null'); }catch(e){}
    if(saved && typeof saved === 'object') applySettings(saved);
    state.history = [snapshotSettings()];
    state.idx = 0;
    syncEngineOpts();
  }

  function syncEngineOpts(){
    const eng = $('engine').value;
    const mode = document.querySelector('#modeSeg .active').dataset.mode;
    const vtOk = state.engineInfo && state.engineInfo.vtracer;
    // Зеркалит выбор движка на сервере (raster_to_svg_server.py: convert()):
    // vtracer используется только для mode=contour; мозаика — всегда native.
    const usesVtracer = eng === 'vtracer' || (eng === 'auto' && vtOk && mode === 'contour');
    $('vtracerOpts').classList.toggle('opt-disabled', !usesVtracer);
    $('nativeOpts').classList.toggle('opt-disabled', usesVtracer || mode !== 'contour');
    $('mosaicOnly').classList.toggle('opt-disabled', usesVtracer || mode !== 'mosaic');
  }

  function showError(msg){
    const b = $('errorBanner');
    b.textContent = msg;
    b.hidden = false;
  }
  function hideError(){const b=$('errorBanner');b.hidden=true;b.textContent='';}

  function showZoom(e){
    const img = $('svgImg');
    if($('previewPanel').hidden || img.hidden || img.naturalWidth === 0){ hideZoom(); return; }
    const rect = img.getBoundingClientRect();
    let relX = (e.clientX - rect.left) / rect.width;
    let relY = (e.clientY - rect.top) / rect.height;
    relX = Math.max(0, Math.min(1, relX));
    relY = Math.max(0, Math.min(1, relY));
    const bw = img.naturalWidth * ZOOM;
    const bh = img.naturalHeight * ZOOM;
    zoomEl.style.backgroundImage = 'url("' + img.src + '")';
    zoomEl.style.backgroundSize = bw + 'px ' + bh + 'px';
    zoomEl.style.backgroundPosition = (-relX * bw + 110) + 'px ' + (-relY * bh + 110) + 'px';
    let left = e.clientX + 18;
    let top = e.clientY + 18;
    if(left + 220 > window.innerWidth) left = e.clientX - 238;
    if(top + 220 > window.innerHeight) top = e.clientY - 238;
    left = Math.max(4, left);
    top = Math.max(4, top);
    zoomEl.style.left = left + 'px';
    zoomEl.style.top = top + 'px';
    zoomEl.hidden = false;
    document.body.classList.add('zooming');
  }

  function hideZoom(){
    zoomEl.hidden = true;
    document.body.classList.remove('zooming');
  }

  function handleFile(file){
    if(!file) return;
    const isPng = file.type === 'image/png' || /\.png$/i.test(file.name);
    if(isPng){
      hideError();
      state.file = file;
      if(state.thumbUrl) URL.revokeObjectURL(state.thumbUrl);
      state.thumbUrl = URL.createObjectURL(file);
      $('thumb').src = state.thumbUrl;
      $('fileName').textContent = file.name;
      const img = new Image();
      img.onload = ()=>{ $('fileDims').textContent = img.naturalWidth + ' × ' + img.naturalHeight + ' px'; state.dims = {w: img.naturalWidth, h: img.naturalHeight}; };
      img.src = state.thumbUrl;
      $('dzEmpty').hidden = true;
      $('dzPreview').hidden = false;
      $('convertBtn').disabled = false;
      $('result').hidden = true;
      $('staleNote').hidden = true;
      return;
    }
    hideError();
    if(state.thumbUrl) URL.revokeObjectURL(state.thumbUrl);
    state.thumbUrl = URL.createObjectURL(file);
    $('thumb').src = state.thumbUrl;
    $('fileName').textContent = file.name;
    $('dzEmpty').hidden = true;
    $('dzPreview').hidden = false;
    $('result').hidden = true;
    $('staleNote').hidden = true;
    const img = new Image();
    img.onload = ()=>{
      $('fileDims').textContent = img.naturalWidth + ' × ' + img.naturalHeight + ' px';
      state.dims = {w: img.naturalWidth, h: img.naturalHeight};
      const canvas = document.createElement('canvas');
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      canvas.getContext('2d').drawImage(img, 0, 0);
      canvas.toBlob((blob)=>{
        if(!blob){ showError('Не удалось перекодировать изображение.'); return; }
        const base = file.name.replace(/\.[^.]+$/, '');
        state.file = new File([blob], base + '.png', { type: 'image/png' });
        $('convertBtn').disabled = false;
      }, 'image/png');
    };
    img.onerror = ()=>{ showError('Не удалось прочитать изображение. Файл повреждён или формат не поддерживается.'); };
    img.src = state.thumbUrl;
  }

  function removeFile(){
    state.file = null; state.svg = ''; state.dims = null;
    if(state.thumbUrl){ URL.revokeObjectURL(state.thumbUrl); state.thumbUrl = null; }
    if(state.objUrl){ URL.revokeObjectURL(state.objUrl); state.objUrl = null; }
    $('thumb').src = '';
    $('dzEmpty').hidden = false;
    $('dzPreview').hidden = true;
    hideZoom();
    $('convertBtn').disabled = true;
    $('result').hidden = true;
    $('staleNote').hidden = true;
    stopProgress();
    hideError();
    state.compareOn = false;
    $('compareBtn').hidden = true;
    $('comparePanel').hidden = true;
    $('checker').hidden = false;
  }

  function buildParams(){
    const p = new URLSearchParams();
    const mode = document.querySelector('#modeSeg .active').dataset.mode;
    const v = (id)=>$(id).value;
    if(mode !== DEFAULTS.mode) p.set('mode', mode);
    if(v('engine') !== DEFAULTS.engine) p.set('engine', v('engine'));
    const colors = parseInt(v('colors'),10);
    if(colors !== DEFAULTS.colors) p.set('colors', colors);
    const bg = v('bg').trim();
    if(bg && bg !== DEFAULTS.bg) p.set('bg', bg);
    const smooth = parseFloat(v('smooth'));
    if(smooth !== DEFAULTS.smooth) p.set('smooth', smooth);
    const corner = parseInt(v('corner'),10);
    if(corner !== DEFAULTS.corner) p.set('corner', corner);
    const seam = parseFloat(v('seam'));
    if(seam !== DEFAULTS.seam) p.set('seam', seam);
    const cell = parseInt(v('cell'),10);
    if(cell !== DEFAULTS.cell) p.set('cell', cell);
    if(v('shape') !== DEFAULTS.shape) p.set('shape', v('shape'));
    const gap = parseFloat(v('gap'));
    if(gap !== DEFAULTS.gap) p.set('gap', gap);
    const seed = parseInt(v('seed'),10);
    if(seed !== DEFAULTS.seed) p.set('seed', seed);
    if(v('vtracer_preset') !== DEFAULTS.vtracer_preset) p.set('vtracer_preset', v('vtracer_preset'));
    if(v('vtracer_mode') !== DEFAULTS.vtracer_mode) p.set('vtracer_mode', v('vtracer_mode'));
    const vcp = parseInt(v('vtracer_color_precision'),10);
    if(vcp !== DEFAULTS.vtracer_color_precision) p.set('vtracer_color_precision', vcp);
    const vfs = parseInt(v('vtracer_filter_speckle'),10);
    if(vfs !== DEFAULTS.vtracer_filter_speckle) p.set('vtracer_filter_speckle', vfs);
    return p;
  }

  function setBusy(b){
    const btn = $('convertBtn');
    if(b){
      btn.dataset.label = btn.textContent;
      btn.innerHTML = '<span class="spinner"></span>Конвертация…';
    }else{
      btn.textContent = btn.dataset.label || 'Конвертировать';
    }
  }

  function estimateSeconds(){
    if(!state.dims) return null;
    const upscale = parseInt($('upscale').value,10) || 1;
    const px = state.dims.w * state.dims.h * upscale * upscale;
    const mode = document.querySelector('#modeSeg .active').dataset.mode;
    const engine = $('engine').value;
    if(engine === 'vtracer' || (engine === 'auto' && state.engineInfo && state.engineInfo.vtracer)){
      return 0.1 + px * 0.0000025;
    }
    if(mode === 'mosaic'){
      return 0.03 + px * 0.0000034;
    }
    return 0.15 + px * 0.000009;
  }

  function startProgress(stream){
    const fill = $('progressFill');
    const text = $('progressText');
    $('progress').hidden = false;
    if(stream){
      fill.style.width = '2%';
      text.textContent = 'Квантование цветов… 2%';
      return;
    }
    const est = estimateSeconds();
    if(est === null){
      fill.style.width = '40%';
      text.textContent = 'Конвертация…';
      return;
    }
    const t0 = Date.now();
    state.progressTimer = setInterval(()=>{
      const elapsed = (Date.now() - t0) / 1000;
      const pct = Math.min(90, Math.round(elapsed / est * 90));
      fill.style.width = pct + '%';
      if(elapsed > est){
        fill.style.width = '90%';
        text.textContent = 'Конвертация… прошло ' + Math.round(elapsed) + ' с';
      }else{
        text.textContent = 'Конвертация… прошло ' + Math.round(elapsed) + ' с · оценка ~' + Math.ceil(est) + ' с';
      }
    }, 250);
  }

  function stopProgress(){
    if(state.progressTimer){ clearInterval(state.progressTimer); state.progressTimer = null; }
    $('progress').hidden = true;
    $('progressFill').style.width = '0%';
  }

  const STAGE_LABELS = {
    quantize:'Квантование цветов…',
    contour:'Контуры и кривые…',
    metrics:'Оценка качества…',
    done:'Готово'
  };

  function setStageProgress(stage, pct){
    $('progressFill').style.width = Math.max(2, Math.min(95, pct)) + '%';
    $('progressText').textContent = (STAGE_LABELS[stage] || 'Конвертация…') + ' ' + pct + '%';
  }

  function readStream(resp){
    return new Promise((resolve, reject) => {
      const reader = resp.body.getReader();
      const dec = new TextDecoder();
      let buf = '';
      function pump(){
        reader.read().then(({done, value}) => {
          if(done){ resolve(null); return; }
          buf += dec.decode(value, {stream:true});
          let nl;
          while((nl = buf.indexOf('\n')) !== -1){
            const line = buf.slice(0, nl).trim();
            buf = buf.slice(nl+1);
            if(!line) continue;
            let ev;
            try{ ev = JSON.parse(line); }catch{ continue; }
            if(ev.stage != null){
              setStageProgress(ev.stage, ev.pct);
            }else if(ev.done || ev.error){
              resolve(ev);
              return;
            }
          }
          pump();
        }).catch(reject);
      }
      pump();
    });
  }

  async function convert(){
    if(!state.file || state.busy) return;
    state.busy = true;
    setBusy(true);
    hideError();
    const mode = document.querySelector('#modeSeg .active').dataset.mode;
    const engine = $('engine').value;
    const useStream = mode === 'contour' && engine !== 'vtracer' &&
      !(engine === 'auto' && state.engineInfo && state.engineInfo.vtracer);
    state.controller = new AbortController();
    startProgress(useStream);
    try{
      const upscale = parseInt($('upscale').value,10) || 1;
      let body = state.file;
      if(upscale > 1){
        try{
          body = await upscaleFile(state.file, upscale);
        }catch(err){
          showError(err.message === 'limit' ? 'После увеличения файл превышает 20 МБ (лимит сервера). Уменьшите масштаб.' : 'Не удалось увеличить изображение.');
          return;
        }
      }
      const qs = buildParams();
      if(useStream) qs.set('progress','1');
      const resp = await fetch('/convert' + (qs.toString() ? '?'+qs.toString() : ''), {
        method:'POST',
        headers:{'Content-Type':'image/png'},
        body,
        signal: state.controller.signal
      });
      if(!resp.ok){
        const data = await resp.json().catch(()=>({}));
        showError(data.error || ('Ошибка сервера (код '+resp.status+')'));
        return;
      }
      if(useStream){
        const result = await readStream(resp);
        if(!result) return;
        if(result.error){ showError(result.error); return; }
        showResult(result.svg, result.report);
        return;
      }
      const data = await resp.json().catch(()=>({}));
      showResult(data.svg, data.report);
    }catch(e){
      if(e.name === 'AbortError'){
        showError('Конвертация отменена.');
      }else{
        showError('Сетевая ошибка: '+e.message);
      }
    }finally{
      state.controller = null;
      state.busy = false;
      stopProgress();
      setBusy(false);
    }
  }

  function showResult(svg, report){
    state.svg = svg;
    if(state.objUrl) URL.revokeObjectURL(state.objUrl);
    const blob = new Blob([svg], {type:'image/svg+xml'});
    state.objUrl = URL.createObjectURL(blob);
    $('svgImg').src = state.objUrl;
    $('svgCode').textContent = svg;
    $('result').hidden = false;
    $('staleNote').hidden = true;
    renderReport(report);
    $('compareBtn').hidden = !state.thumbUrl;
    $('paletteBtn').hidden = false;
    $('exportBtn').hidden = false;
    $('palettePanel').hidden = true;
    state.compareOn = false;
    renderCompare();
  }

  function renderCompare(){
    const on = state.compareOn && !!state.thumbUrl && !!state.objUrl;
    $('comparePanel').hidden = !on;
    $('checker').hidden = on;
    if(on){
      $('origImg').src = state.thumbUrl;
      $('cmpImg').src = state.objUrl;
    }
    $('compareBtn').classList.toggle('active', on);
  }

  function toggleCompare(){
    state.compareOn = !state.compareOn;
    renderCompare();
  }

  function renderReport(r){
    if(!r) return;
    const eng = r.engine === 'vtracer' ? 'vtracer' : (r.mode === 'mosaic' ? 'native-mosaic' : 'native-contour');
    const parts = [];
    parts.push('<span><b>Движок</b>'+esc(eng)+'</span>');
    parts.push('<span><b>Размер</b>'+r.width+' × '+r.height+'</span>');
    parts.push('<span><b>Цвета</b>'+r.colors+'</span>');
    parts.push('<span><b>Пути</b>'+(r.paths!=null?r.paths:'—')+'</span>');
    parts.push('<span><b>Элементы</b>'+(r.elements!=null?r.elements:'—')+'</span>');
    parts.push('<span><b>Вход</b>'+fmtBytes(r.input_bytes)+'</span>');
    parts.push('<span><b>Выход</b>'+fmtBytes(r.output_bytes)+'</span>');
    parts.push('<span><b>Сжатие</b>'+(r.compression_ratio!=null?Math.round(r.compression_ratio*100)/100+'×':'—')+'</span>');
    parts.push('<span><b>Время</b>'+r.duration_ms+' мс</span>');
    if(r.mean_color_error!=null) parts.push('<span><b>Ошибка цвета</b>'+esc(r.mean_color_error)+'</span>');
    $('report').innerHTML = parts.join('');
    const nEl = $('statCount'), lbl = $('statLabel'), pxEl = $('statPx');
    const els = r.elements || 0, paths = r.paths || 0;
    if(els > 0){
      nEl.textContent = els.toLocaleString('ru-RU');
      lbl.textContent = 'элементов';
    }else{
      nEl.textContent = paths.toLocaleString('ru-RU');
      lbl.textContent = 'путей';
    }
    const total = (r.width || 0) * (r.height || 0);
    pxEl.textContent = (r.width||'—') + ' × ' + (r.height||'—') + ' px · ' + total.toLocaleString('ru-RU') + ' пикселей';
    $('statsBar').hidden = false;
  }

  function markDirty(){
    if(state.svg){
      $('staleNote').hidden = false;
    }else{
      $('staleNote').hidden = true;
    }
  }

  function setMode(mode){
    document.querySelectorAll('#modeSeg button').forEach(b=>b.classList.toggle('active', b.dataset.mode===mode));
    $('mosaicOnly').style.display = mode==='mosaic' ? '' : 'none';
    $('modeDesc').textContent = mode==='mosaic'
      ? 'Мозаика: декоративный постер из примитивов — для афиш, обложек, стилизации.'
      : 'Контур: чёткие границы и заливки — для логотипов, иконок, схем.';
    syncEngineOpts();
    markDirty();
  }

  function setRange(id, value){
    const el = $(id);
    el.value = String(value);
    el.dispatchEvent(new Event('input', {bubbles:true}));
  }
  function setSelect(id, value){
    const el = $(id);
    el.value = value;
    el.dispatchEvent(new Event('change', {bubbles:true}));
  }

  const PRESETS = {
    logo:{mode:'contour',engine:'native',colors:4,smooth:0.2,corner:60,seam:0.3,bg:'none'},
    photo_flat:{mode:'contour',engine:'auto',colors:12,smooth:1.2,corner:40,seam:1.0,
               vtracer_preset:'poster',vtracer_color_precision:4,vtracer_filter_speckle:8,bg:'none'},
    mosaic:{mode:'mosaic',cell:16,shape:'rect',gap:0.2,colors:8},
    bw:{mode:'contour',engine:'native',colors:2,smooth:0.3,corner:60,seam:0.5,bg:'none'}
  };

  function loadCustomPresets(){
    try{ return JSON.parse(localStorage.getItem('r2s.presets.v1') || '[]'); }catch(e){ return []; }
  }
  function saveCustomPresets(list){
    try{ localStorage.setItem('r2s.presets.v1', JSON.stringify(list)); }catch(e){}
  }

  function applyPreset(name, params){
    if(!params) params = PRESETS[name];
    if(!params) return;
    pushHistory();
    applySettings(params);
    persistSettings(snapshotSettings());
    document.querySelectorAll('#presetRow .preset[data-preset]').forEach(b=>
      b.classList.toggle('active', b.dataset.preset === name));
  }

  function renderCustomPresets(){
    const list = loadCustomPresets();
    const host = $('customPresets');
    host.textContent = '';
    list.forEach((p, i)=>{
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'preset';
      btn.dataset.customIdx = String(i);
      btn.title = p.name;
      btn.innerHTML = esc(p.name) + ' <span class="x" data-idx="' + i + '" title="Удалить">✕</span>';
      host.appendChild(btn);
    });
  }

  function saveCustomPreset(){
    const name = prompt('Имя своего пресета:');
    if(!name || !name.trim()) return;
    const list = loadCustomPresets();
    list.push({name: name.trim(), params: snapshotSettings()});
    saveCustomPresets(list);
    renderCustomPresets();
  }

  function deleteCustomPreset(idx){
    const list = loadCustomPresets();
    list.splice(idx, 1);
    saveCustomPresets(list);
    renderCustomPresets();
  }

  const SETTING_KEYS = Object.keys(DEFAULTS);

  function setUiMode(mode){
    const simple = mode === 'simple';
    $('vtracerOpts').classList.toggle('ui-hidden', simple);
    $('advDetails').classList.toggle('ui-hidden', simple);
    document.querySelectorAll('#uiSeg button').forEach(b=>
      b.classList.toggle('active', b.dataset.ui === mode));
    try{ localStorage.setItem('r2s.ui.mode', mode); }catch(e){}
  }

  function snapshotSettings(){
    const s = {};
    for(const k of SETTING_KEYS){
      if(k === 'mode'){ s[k] = document.querySelector('#modeSeg .active').dataset.mode; continue; }
      const el = $(k);
      if(el) s[k] = el.value;
    }
    return s;
  }

  function persistSettings(s){
    try{ localStorage.setItem('r2s.settings.v1', JSON.stringify(s)); }catch(e){}
  }

  function pushHistory(){
    if(state.applying) return;
    const s = snapshotSettings();
    const top = state.history[state.history.length-1];
    if(top && JSON.stringify(top) === JSON.stringify(s)) return;
    if(state.idx < state.history.length-1) state.history = state.history.slice(0, state.idx+1);
    state.history.push(s);
    if(state.history.length > 100) state.history.shift();
    state.idx = state.history.length-1;
    persistSettings(s);
  }

  function applySettings(s){
    state.applying = true;
    try{
      for(const k in s){
        if(k === 'mode'){ setMode(s[k]); continue; }
        const el = $(k);
        if(!el) continue;
        let v = s[k];
        if(el.tagName !== 'SELECT' && el.type !== 'number' && el.type !== 'text'){
          const n = parseFloat(v);
          if(isFinite(n)){
            const min = parseFloat(el.min), max = parseFloat(el.max);
            v = n;
            if(!isNaN(min)) v = Math.max(min, v);
            if(!isNaN(max)) v = Math.min(max, v);
          }
        }
        el.value = v;
        const badgeId = k === 'vtracer_color_precision' ? 'vtracerColorPrecisionBadge' : k === 'vtracer_filter_speckle' ? 'vtracerSpeckleBadge' : k + 'Badge';
        const badge = $(badgeId);
        if(badge) badge.textContent = el.value;
      }
      syncEngineOpts();
      markDirty();
    }finally{ state.applying = false; }
  }

  function undo(){ if(state.idx > 0){ state.idx--; applySettings(state.history[state.idx]); } }
  function redo(){ if(state.idx < state.history.length-1){ state.idx++; applySettings(state.history[state.idx]); } }
  function resetSettings(){
    pushHistory();
    const s = {};
    for(const k of SETTING_KEYS) s[k] = DEFAULTS[k];
    applySettings(s);
    persistSettings(snapshotSettings());
  }

  function download(){
    if(!state.svg) return;
    const blob = new Blob([state.svg], {type:'image/svg+xml'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    const name = (state.file ? state.file.name.replace(/\.png$/i,'') : 'image') + '.svg';
    a.href = url; a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(()=>URL.revokeObjectURL(url), 1000);
  }

  async function copy(){
    const btn = $('copyBtn');
    const done = ()=>{ const o=btn.textContent; btn.textContent='Скопировано ✓'; btn.disabled=true; setTimeout(()=>{btn.textContent=o;btn.disabled=false;},1500); };
    try{
      await navigator.clipboard.writeText(state.svg);
      done();
    }catch(e){
      const ta=document.createElement('textarea');
      ta.value=state.svg; document.body.appendChild(ta); ta.select();
      try{ document.execCommand('copy'); done(); }catch(_){}
      ta.remove();
    }
  }

  // ---------------------------------------------------------------
  // Палитра: свотчи цветов из SVG, перекраска, слияние цветов
  // ---------------------------------------------------------------
  const SW_RE = /(?:fill|stroke)="(#[\da-fA-F]{3,8})"/g;
  let paletteState = {colors: [], mergeFrom: null};

  function collectPalette(){
    const counts = new Map();
    let m;
    while((m = SW_RE.exec(state.svg))){
      const c = m[1].toLowerCase();
      counts.set(c, (counts.get(c) || 0) + 1);
    }
    paletteState.colors = Array.from(counts.entries())
      .map(([hex, n]) => ({hex, n}))
      .sort((a, b) => b.n - a.n);
  }

  function applyRecolor(fromHex, toHex){
    const from = fromHex.toLowerCase();
    const to = toHex.toLowerCase();
    if(from === to) return;
    const next = state.svg.replace(/(?:fill|stroke)="#([\da-fA-F]{3,8})"/g, (full, h) =>
      h.toLowerCase() === from.slice(1) ? full.replace('#'+h, to) : full);
    updateSvg(next);
  }

  function updateSvg(svg){
    state.svg = svg;
    if(state.objUrl) URL.revokeObjectURL(state.objUrl);
    const blob = new Blob([svg], {type:'image/svg+xml'});
    state.objUrl = URL.createObjectURL(blob);
    $('svgImg').src = state.objUrl;
    $('svgCode').textContent = svg;
    renderCompare();
  }

  function renderPalette(){
    const host = $('paletteSwatches');
    host.textContent = '';
    if(!paletteState.colors.length){
      const p = document.createElement('p');
      p.className = 'palette-hint';
      p.textContent = 'Цвета не найдены.';
      host.appendChild(p);
      return;
    }
    for(const c of paletteState.colors){
      const sw = document.createElement('button');
      sw.type = 'button';
      sw.className = 'swatch' + (paletteState.mergeFrom === c.hex ? ' active' : '');
      sw.title = c.hex + ' — клик: перекрасить, «→»: слить в другой цвет';
      const chip = document.createElement('span');
      chip.className = 'sw-color';
      chip.style.background = c.hex;
      const hex = document.createElement('span');
      hex.className = 'sw-hex';
      hex.textContent = c.hex;
      const cnt = document.createElement('span');
      cnt.className = 'sw-count';
      cnt.textContent = '×' + c.n;
      const merge = document.createElement('i');
      merge.className = 'sw-merge';
      merge.textContent = '→';
      sw.append(chip, hex, cnt, merge);
      sw.addEventListener('click', ()=>{
        if(paletteState.mergeFrom){
          applyRecolor(paletteState.mergeFrom, c.hex);
          paletteState.mergeFrom = null;
          collectPalette();
          renderPalette();
          markDirty();
          return;
        }
        const to = prompt('Новый цвет (' + c.hex + '):', c.hex);
        if(!to || !/^#[\da-fA-F]{3,8}$/.test(to.trim())) return;
        applyRecolor(c.hex, to.trim());
        collectPalette();
        renderPalette();
        markDirty();
      });
      merge.addEventListener('click', (ev)=>{
        ev.stopPropagation();
        paletteState.mergeFrom = paletteState.mergeFrom === c.hex ? null : c.hex;
        renderPalette();
      });
      host.appendChild(sw);
    }
  }

  function togglePalette(){
    if($('palettePanel').hidden){
      collectPalette();
      renderPalette();
      $('palettePanel').hidden = false;
    }else{
      $('palettePanel').hidden = true;
    }
  }

  // ---------------------------------------------------------------
  // Пакетная обработка: очередь файлов -> /convert по одному -> /zip
  // ---------------------------------------------------------------
  let batchItems = [];

  function renderBatch(){
    const host = $('batchList');
    host.textContent = '';
    const anyOk = batchItems.some(it => it.status === 'ok');
    $('batchZipBtn').disabled = !anyOk;
    for(const [i, it] of batchItems.entries()){
      const row = document.createElement('div');
      row.className = 'batch-item' + (it.status === 'ok' ? ' ok' : it.status === 'err' ? ' err' : '');
      const name = document.createElement('span');
      name.className = 'bi-name';
      name.textContent = it.file.name;
      const size = document.createElement('span');
      size.className = 'bi-size';
      size.textContent = fmtBytes(it.file.size);
      const status = document.createElement('span');
      status.className = 'bi-status';
      status.textContent = it.status === 'ok' ? 'OK' : it.status === 'err' ? (it.error || 'ошибка') : 'в очереди';
      const x = document.createElement('i');
      x.className = 'bi-x';
      x.textContent = '✕';
      x.title = 'Убрать из списка';
      x.addEventListener('click', ()=>{
        batchItems.splice(i, 1);
        renderBatch();
      });
      row.append(name, size, status, x);
      host.appendChild(row);
    }
  }

  function batchSetProgress(pct, text){
    $('batchProgressFill').style.width = pct + '%';
    $('batchProgressText').textContent = text;
  }

  async function runBatch(){
    for(const it of batchItems){
      if(it.status !== 'pending') continue;
      try{
        let body = it.file;
        const upscale = parseInt($('upscale').value, 10) || 1;
        if(upscale > 1){
          body = await upscaleFile(it.file, upscale);
        }
        const qs = buildParams();
        const resp = await fetch('/convert' + (qs.toString() ? '?'+qs.toString() : ''), {
          method:'POST',
          headers:{'Content-Type':'image/png'},
          body
        });
        if(!resp.ok){
          const data = await resp.json().catch(()=>({}));
          throw new Error(data.error || ('код '+resp.status));
        }
        const data = await resp.json();
        it.svg = data.svg;
        it.status = 'ok';
      }catch(e){
        it.status = 'err';
        it.error = e.message;
      }
      renderBatch();
      const done = batchItems.filter(b => b.status === 'ok' || b.status === 'err').length;
      batchSetProgress(Math.round(done / batchItems.length * 100), 'Обработано ' + done + ' из ' + batchItems.length);
    }
    $('batchProgress').hidden = true;
  }

  function addBatchFiles(files){
    const added = Array.from(files).filter(f =>
      f.type === 'image/png' || /\.png$/i.test(f.name));
    if(!added.length) return;
    for(const f of added) batchItems.push({file: f, status: 'pending', svg: null});
    renderBatch();
    $('batchProgress').hidden = false;
    batchSetProgress(0, 'Старт…');
    runBatch();
  }

  async function zipBatch(){
    const ok = batchItems.filter(it => it.status === 'ok' && it.svg);
    if(!ok.length) return;
    const files = ok.map(it => ({
      name: it.file.name.replace(/\.png$/i, '') + '.svg',
      svg: it.svg
    }));
    try{
      const resp = await fetch('/zip', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({files})
      });
      if(!resp.ok){
        const data = await resp.json().catch(()=>({}));
        showError(data.error || ('Ошибка сервера (код '+resp.status+')'));
        return;
      }
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'raster-to-svg.zip';
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(()=>URL.revokeObjectURL(url), 1000);
    }catch(e){
      showError('Сетевая ошибка: '+e.message);
    }
  }

  // ---------------------------------------------------------------
  // Экспорт: PNG (клиентский canvas) / DXF / EPS (POST /export)
  // ---------------------------------------------------------------
  function exportSvgAsPng(scale){
    return new Promise((resolve, reject)=>{
      const img = new Image();
      img.onload = ()=>{
        const canvas = document.createElement('canvas');
        canvas.width = img.naturalWidth * scale;
        canvas.height = img.naturalHeight * scale;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        canvas.toBlob((blob)=>{
          if(!blob){ reject(new Error('toBlob')); return; }
          resolve(blob);
        }, 'image/png');
      };
      img.onerror = ()=>reject(new Error('decode'));
      img.src = state.objUrl;
    });
  }

  function saveBlob(blob, name){
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(()=>URL.revokeObjectURL(url), 1000);
  }

  async function doExport(){
    const btn = $('exportGoBtn');
    btn.disabled = true;
    btn.textContent = 'Экспорт…';
    const base = (state.file ? state.file.name.replace(/\.\w+$/i, '') : 'image');
    try{
      const fmt = document.querySelector('#exportFormatSeg .active').dataset.fmt;
      if(fmt === 'png'){
        const scale = parseInt($('exportScale').value, 10) || 1;
        const blob = await exportSvgAsPng(scale);
        saveBlob(blob, base + '.png');
      }else{
        const layers = $('exportLayers').checked ? '1' : '0';
        const resp = await fetch('/export', {
          method:'POST',
          headers:{'Content-Type':'application/json'},
          body: JSON.stringify({svg: state.svg, fmt, layers})
        });
        if(!resp.ok){
          const data = await resp.json().catch(()=>({}));
          showError(data.error || ('Ошибка сервера (код '+resp.status+')'));
          return;
        }
        const text = await resp.text();
        saveBlob(new Blob([text], {type: fmt === 'dxf' ? 'application/dxf' : 'application/postscript'}),
                 base + '.' + fmt);
      }
      $('exportModal').hidden = true;
    }catch(e){
      showError('Экспорт не удался: '+e.message);
    }finally{
      btn.disabled = false;
      btn.textContent = 'Скачать';
    }
  }

  function toggleExportModal(show){
    $('exportModal').hidden = !show;
  }

  // wiring
  const dz = $('dropzone');
  dz.addEventListener('click',(e)=>{ if(e.target.closest('#removeFile')) return; $('fileInput').click(); });
  dz.addEventListener('dragover',(e)=>{ e.preventDefault(); dz.classList.add('drag'); });
  dz.addEventListener('dragleave',()=>dz.classList.remove('drag'));
  dz.addEventListener('drop',(e)=>{ e.preventDefault(); dz.classList.remove('drag'); if(e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]); });
  $('fileInput').addEventListener('change',(e)=>{ if(e.target.files[0]) handleFile(e.target.files[0]); e.target.value=''; });
  $('removeFile').addEventListener('click',(e)=>{ e.stopPropagation(); removeFile(); });
  $('svgImg').addEventListener('mousemove', showZoom);
  $('svgImg').addEventListener('mouseleave', hideZoom);

  document.querySelectorAll('#modeSeg button').forEach(b=>b.addEventListener('click',()=>setMode(b.dataset.mode)));
  $('presetRow').addEventListener('click',(e)=>{
    const del = e.target.closest('.x');
    if(del){ deleteCustomPreset(parseInt(del.dataset.idx,10)); return; }
    const custom = e.target.closest('.preset[data-custom-idx]');
    if(custom){
      const list = loadCustomPresets();
      const p = list[parseInt(custom.dataset.customIdx,10)];
      if(p) applyPreset(null, p.params);
      return;
    }
    const b = e.target.closest('.preset[data-preset]');
    if(b) applyPreset(b.dataset.preset);
  });
  $('savePresetBtn').addEventListener('click',saveCustomPreset);
  document.querySelectorAll('#uiSeg button').forEach(b=>b.addEventListener('click',()=>setUiMode(b.dataset.ui)));
  $('engine').addEventListener('change',markDirty);
  $('engine').addEventListener('change',syncEngineOpts);
  $('colors').addEventListener('input',()=>{ $('colorsBadge').textContent=$('colors').value; markDirty(); });
  $('bg').addEventListener('input',markDirty);
  $('smooth').addEventListener('input',()=>{ $('smoothBadge').textContent=$('smooth').value; markDirty(); });
  $('corner').addEventListener('input',()=>{ $('cornerBadge').textContent=$('corner').value; markDirty(); });
  $('seam').addEventListener('input',()=>{ $('seamBadge').textContent=$('seam').value; markDirty(); });
  $('cell').addEventListener('input',markDirty);
  $('shape').addEventListener('change',markDirty);
  $('gap').addEventListener('input',()=>{ $('gapBadge').textContent=$('gap').value; markDirty(); });
  $('seed').addEventListener('input',markDirty);
  $('upscale').addEventListener('change',markDirty);
  $('vtracer_preset').addEventListener('change',markDirty);
  $('vtracer_mode').addEventListener('change',markDirty);
  $('vtracer_color_precision').addEventListener('input',()=>{ $('vtracerColorPrecisionBadge').textContent=$('vtracer_color_precision').value; markDirty(); });
  $('vtracer_filter_speckle').addEventListener('input',()=>{ $('vtracerSpeckleBadge').textContent=$('vtracer_filter_speckle').value; markDirty(); });
  $('convertBtn').addEventListener('click',convert);

  document.querySelectorAll('.tabs button').forEach(b=>b.addEventListener('click',()=>{
    document.querySelectorAll('.tabs button').forEach(x=>x.classList.toggle('active',x===b));
    const tab=b.dataset.tab;
    $('previewPanel').hidden = tab!=='preview';
    $('codePanel').hidden = tab!=='code';
    hideZoom();
  }));
  $('downloadBtn').addEventListener('click',download);
  $('copyBtn').addEventListener('click',copy);
  $('resetBtn').addEventListener('click',resetSettings);
  $('compareBtn').addEventListener('click',toggleCompare);
  $('cancelBtn').addEventListener('click',()=>{ if(state.controller) state.controller.abort(); });
  $('paletteBtn').addEventListener('click',togglePalette);
  $('paletteCloseBtn').addEventListener('click',()=>{ $('palettePanel').hidden = true; });
  $('batchToggleBtn').addEventListener('click',()=>{
    $('batchPanel').hidden = !$('batchPanel').hidden;
    $('batchToggleBtn').classList.toggle('active', !$('batchPanel').hidden);
  });
  $('batchPickBtn').addEventListener('click',()=>$('batchInput').click());
  $('batchInput').addEventListener('change',(e)=>{ addBatchFiles(e.target.files); e.target.value=''; });
  $('batchZipBtn').addEventListener('click',zipBatch);
  $('exportBtn').addEventListener('click',()=>toggleExportModal(true));
  $('exportCloseBtn').addEventListener('click',()=>toggleExportModal(false));
  $('exportCancelBtn').addEventListener('click',()=>toggleExportModal(false));
  $('exportGoBtn').addEventListener('click',doExport);
  document.querySelectorAll('#exportFormatSeg button').forEach(b=>b.addEventListener('click',()=>{
    document.querySelectorAll('#exportFormatSeg button').forEach(x=>x.classList.toggle('active', x===b));
    const isPng = b.dataset.fmt === 'png';
    $('exportLayersRow').hidden = isPng;
    $('exportScaleRow').hidden = !isPng;
  }));
  $('exportModal').addEventListener('click',(e)=>{ if(e.target === $('exportModal')) toggleExportModal(false); });
  document.querySelector('.controls').addEventListener('input',(e)=>{ if(SETTING_KEYS.includes(e.target.id)) pushHistory(); });
  document.querySelector('.controls').addEventListener('change',(e)=>{ if(SETTING_KEYS.includes(e.target.id)) pushHistory(); });
  window.addEventListener('keydown',(e)=>{
    const mod = e.metaKey || e.ctrlKey;
    if(mod && e.key.toLowerCase() === 'z'){ e.preventDefault(); e.shiftKey ? redo() : undo(); }
    else if(mod && e.key.toLowerCase() === 'y'){ e.preventDefault(); redo(); }
  });

  syncEngineOpts(); // сразу, не дожидаясь /health — без вспышки неверного состояния
  checkHealth();
  loadDefaults();
  renderCustomPresets();
  setUiMode(localStorage.getItem('r2s.ui.mode') === 'simple' ? 'simple' : 'advanced');
})();
