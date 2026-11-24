// SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
// SCROLL mock interface. One page; the loading strategy (arm) is the only switch.
// The page records raw timestamps (performance.now() clock, ms) and raw
// PerformanceObserver entries. All metric formulas live in src/scroll/metrics.py.
(function () {
  'use strict';

  var VERSION = '0.1.0';
  var S = window.ScrollSchedule;
  var ARMS = { read: ['BLANK', 'SKELETON', 'PREFETCH'], write: ['BLANK', 'OPTIMISTIC'] };
  var errors = [];
  window.addEventListener('error', function (e) { errors.push(String(e.message)); });
  window.addEventListener('unhandledrejection', function (e) { errors.push('unhandled rejection: ' + String(e.reason && e.reason.message || e.reason)); });

  function parseConfig(search) {
    var q = new URLSearchParams(search);
    function get(name, def) { var v = q.get(name); return v === null ? def : v; }
    function num(name, def) {
      var raw = get(name, def);
      if (raw === undefined) throw new Error('missing parameter: ' + name);
      var v = Number(raw);
      if (raw === '' || !isFinite(v)) throw new Error('parameter ' + name + ' must be a finite number');
      return v;
    }
    var cfg = {
      path: get('path', undefined),
      arm: get('arm', undefined),
      seed: num('seed', undefined),
      L: num('L', undefined),
      p: num('p', '0'),
      jitter: num('jitter', '0.1'),
      items: num('items', '10'),
      settle: num('settle', '1000'),
      reserve: get('reserve', '0')
    };
    if (!Object.prototype.hasOwnProperty.call(ARMS, cfg.path)) throw new Error('path must be read or write');
    if (ARMS[cfg.path].indexOf(cfg.arm) < 0) throw new Error('arm ' + cfg.arm + ' is not defined for path ' + cfg.path);
    if (!Number.isInteger(cfg.seed) || cfg.seed < 0 || cfg.seed >= 4294967296) throw new Error('seed must be an integer in [0, 2^32)');
    if (cfg.L < 0) throw new Error('L must be >= 0');
    if (!(cfg.p >= 0 && cfg.p <= 1)) throw new Error('p must be in [0, 1]');
    if (cfg.path === 'read' && cfg.p !== 0) throw new Error('p must be 0 on the read path');
    if (!(cfg.jitter >= 0 && cfg.jitter < 1)) throw new Error('jitter must be in [0, 1)');
    if (!Number.isInteger(cfg.items) || cfg.items < 1 || cfg.items > 100) throw new Error('items must be an integer in [1, 100]');
    if (cfg.settle < 0) throw new Error('settle must be >= 0');
    if (cfg.reserve !== '0' && cfg.reserve !== '1') throw new Error('reserve must be 0 or 1');
    cfg.reserve = cfg.reserve === '1';
    return cfg;
  }

  var cfg;
  try {
    cfg = parseConfig(location.search);
  } catch (e) {
    var el = document.getElementById('config-error');
    el.textContent = 'Invalid configuration: ' + e.message;
    el.hidden = false;
    window.__scroll = { ready: false, error: e.message, version: VERSION };
    return;
  }

  // Raw PerformanceObserver buffers.
  var eventEntries = [], shiftEntries = [], elementEntries = [];
  function observe(type, sink, extra) {
    try {
      var po = new PerformanceObserver(function (list) { list.getEntries().forEach(function (e) { sink.push(e); }); });
      var opts = { type: type, buffered: true };
      for (var key in extra) opts[key] = extra[key];
      po.observe(opts);
    } catch (e) { errors.push('observer ' + type + ' unavailable: ' + e.message); }
  }
  observe('event', eventEntries, { durationThreshold: 16 });
  observe('layout-shift', shiftEntries, {});
  observe('element', elementEntries, {});

  // Mock transport: seeded delay and outcome; no network.
  var requests = [];
  function request(stream, index) {
    var s = S.schedule(cfg.seed, stream, index, cfg.L, cfg.jitter, stream === 'write' ? cfg.p : 0);
    var rec = { stream: stream, index: index, d_ms: s.delayMs, ok: s.ok, t_start: performance.now(), t_end: null };
    requests.push(rec);
    var promise = new Promise(function (resolve, reject) {
      setTimeout(function () { rec.t_end = performance.now(); if (s.ok) resolve(rec); else reject(rec); }, s.delayMs);
    });
    return { promise: promise, rec: rec };
  }

  var $ = function (id) { return document.getElementById(id); };
  var detail = $('detail'), list = $('list'), save = $('save'), statusEl = $('status');
  var current = null;
  var trials = {};
  var serverState = {};
  var prefetchCache = {};
  var strayClicks = 0;

  function copyFrame(f) {
    return { kind: f.kind, t_commit: f.t_commit, t_raf1: f.t_raf1, t_raf1_ts: f.t_raf1_ts, t_raf2: f.t_raf2, t_raf2_ts: f.t_raf2_ts, state: f.state };
  }

  function markFrame(t, kind, state) {
    var f = { kind: kind, t_commit: performance.now(), t_raf1: null, t_raf1_ts: null, t_raf2: null, t_raf2_ts: null, state: state, painted: false };
    t.frames.push(f);
    requestAnimationFrame(function (ts1) {
      f.t_raf1_ts = ts1; f.t_raf1 = performance.now();
      requestAnimationFrame(function (ts2) {
        f.t_raf2_ts = ts2; f.t_raf2 = performance.now(); f.painted = true;
        maybeFinish(t);
      });
    });
  }

  function maybeFinish(t) {
    if (t.finishing || !t.settled) return;
    for (var i = 0; i < t.frames.length; i++) if (!t.frames[i].painted) return;
    t.finishing = true;
    setTimeout(function () { finalize(t); }, cfg.settle);
  }

  function entryJSON(e) {
    var o = { name: e.name, entryType: e.entryType, startTime: e.startTime, duration: e.duration };
    if (e.entryType === 'event') { o.processingStart = e.processingStart; o.processingEnd = e.processingEnd; o.interactionId = e.interactionId; }
    if (e.entryType === 'layout-shift') { o.value = e.value; o.hadRecentInput = e.hadRecentInput; }
    if (e.entryType === 'element') { o.identifier = e.identifier; o.renderTime = e.renderTime; o.loadTime = e.loadTime; }
    return o;
  }

  function snapshot(t) {
    if (cfg.path === 'read') {
      var box = detail.querySelector('.box');
      return {
        content_item: box && box.dataset.item !== undefined ? Number(box.dataset.item) : null,
        skeleton_present: !!detail.querySelector('.sk'),
        aria_busy: detail.getAttribute('aria-busy')
      };
    }
    return {
      pressed: save.getAttribute('aria-pressed') === 'true',
      error_text: statusEl.textContent,
      focus_on_toggle: document.activeElement === save
    };
  }

  function finalize(t) {
    var since = t.t_prepare;
    t.result = {
      k: t.k, path: cfg.path, arm: cfg.arm, input_type: t.input_type,
      t_prepare: t.t_prepare, t_hover: t.t_hover, t_in: t.t_in, t_handler: t.t_handler,
      request: t.request, prefetch: t.prefetch,
      frames: t.frames.map(copyFrame),
      event_entries: eventEntries.filter(function (e) { return e.startTime >= since; }).map(entryJSON),
      layout_shifts: shiftEntries.filter(function (e) { return e.startTime >= since; }).map(entryJSON),
      element_entries: elementEntries.filter(function (e) { return e.identifier === 'content-' + t.k; }).map(entryJSON),
      final_display: snapshot(t),
      server_state_before: t.server_state_before,
      server_state_after: cfg.path === 'write' ? serverState[t.k] : null,
      t_finalize: performance.now()
    };
    t.done = true;
    t.resolve(t.result);
  }

  // ---------------- read path ----------------
  function itemText(i) {
    return { title: 'Item ' + (i + 1), body: 'Description of item ' + (i + 1) + '. Fixed-length mock text used only to give the detail region a realistic, constant size for every item.', price: (10 + (i % 7)) + '.00', stock: String(3 + (i % 5)) };
  }

  function renderContent(i) {
    var d = itemText(i);
    detail.innerHTML = '<div class="box" data-item="' + i + '"><h2 elementtiming="content-' + i + '">' + d.title +
      '</h2><p elementtiming="content-' + i + '">' + d.body + '</p><dl><dt>Price</dt><dd>' + d.price + '</dd><dt>In stock</dt><dd>' + d.stock + '</dd></dl></div>';
    detail.setAttribute('aria-busy', 'false');
  }

  function renderSkeleton() {
    detail.innerHTML = '<div class="box" aria-hidden="true"><div class="sk sk-h"></div><div class="sk sk-p"></div><div class="sk sk-d"></div></div>';
    detail.setAttribute('aria-busy', 'true');
  }

  function startPrefetch(i) {
    if (prefetchCache[i]) return;
    var stream = i < cfg.items ? 'read' : 'decoy';
    var idx = i < cfg.items ? i : i - cfg.items;
    var r = request(stream, idx);
    prefetchCache[i] = { promise: r.promise, rec: r.rec, used: false };
  }

  function onReadClick(ev) {
    var btn = ev.target.closest('button[data-index]');
    if (!btn) return;
    var i = Number(btn.dataset.index);
    var t = current;
    if (!t || t.k !== i || t.t_in !== null) { strayClicks++; return; }
    t.t_in = ev.timeStamp; t.t_handler = performance.now(); t.input_type = ev.detail === 0 ? 'keyboard' : 'pointer';
    if (cfg.arm === 'SKELETON') { renderSkeleton(); markFrame(t, 'skeleton', { content: false, aria_busy: 'true' }); }
    var promise;
    if (cfg.arm === 'PREFETCH' && prefetchCache[i]) {
      prefetchCache[i].used = true;
      t.prefetch = { hit: true, t_start: prefetchCache[i].rec.t_start };
      t.request = prefetchCache[i].rec;
      promise = prefetchCache[i].promise;
    } else {
      if (cfg.arm === 'PREFETCH') t.prefetch = { hit: false, t_start: null };
      var r = request('read', i);
      t.request = r.rec; promise = r.promise;
    }
    promise.then(function () {
      renderContent(i);
      markFrame(t, 'content', { content: true, item: i, aria_busy: 'false' });
      t.settled = true; maybeFinish(t);
    });
  }

  function onReadHover(ev) {
    var btn = ev.target.closest('button[data-index]');
    if (!btn) return;
    var i = Number(btn.dataset.index);
    if (current && current.k === i && current.t_hover === null) current.t_hover = ev.timeStamp;
    if (cfg.arm === 'PREFETCH') startPrefetch(i);
  }

  // ---------------- write path ----------------
  function setPressed(v) { save.setAttribute('aria-pressed', v ? 'true' : 'false'); save.textContent = v ? 'Saved' : 'Save'; }

  function onSave(ev) {
    var t = current;
    if (!t || t.t_in !== null) { strayClicks++; return; }
    t.t_in = ev.timeStamp; t.t_handler = performance.now(); t.input_type = ev.detail === 0 ? 'keyboard' : 'pointer';
    var k = t.k, old = serverState[k], desired = !old;
    if (cfg.arm === 'OPTIMISTIC') { setPressed(desired); statusEl.textContent = ''; markFrame(t, 'optimistic', { pressed: desired, error: false }); }
    var r = request('write', k);
    t.request = r.rec;
    r.promise.then(function () {
      serverState[k] = desired;
      if (cfg.arm === 'BLANK') { setPressed(desired); markFrame(t, 'confirmed', { pressed: desired, error: false }); }
      t.settled = true; maybeFinish(t);
    }, function () {
      setPressed(old);
      statusEl.textContent = 'Could not save ' + itemText(k).title + '. Your change was not kept.';
      markFrame(t, cfg.arm === 'OPTIMISTIC' ? 'rollback' : 'error', { pressed: old, error: true });
      t.settled = true; maybeFinish(t);
    });
  }

  // ---------------- harness API ----------------
  function prepare(k) {
    if (!Number.isInteger(k) || k < 0 || k >= cfg.items) throw new RangeError('k must be an integer in [0, items)');
    if (current && !current.done) throw new Error('trial ' + current.k + ' is not finished');
    if (trials[k]) throw new Error('trial ' + k + ' was already prepared');
    var t = { k: k, t_prepare: performance.now(), t_hover: null, t_in: null, t_handler: null, input_type: null, request: null, prefetch: null, frames: [], settled: false, finishing: false, done: false, server_state_before: null };
    t.promise = new Promise(function (resolve) { t.resolve = resolve; });
    trials[k] = t; current = t;
    if (cfg.path === 'read') {
      detail.innerHTML = '';
      detail.setAttribute('aria-busy', 'false');
      return { target: '#item-' + k, decoy: '#item-' + (cfg.items + k) };
    }
    serverState[k] = false;
    t.server_state_before = false;
    $('item-title').textContent = itemText(k).title;
    setPressed(false);
    statusEl.textContent = '';
    return { target: '#save', decoy: null };
  }

  function whenDone(k) {
    if (!trials[k]) return Promise.reject(new Error('trial ' + k + ' was not prepared'));
    return trials[k].promise;
  }

  function nextFrames() {
    return new Promise(function (resolve) { requestAnimationFrame(function () { requestAnimationFrame(function () { resolve(performance.now()); }); }); });
  }

  function a11yAudit() {
    var issues = [];
    if (!document.documentElement.lang) issues.push('html lang missing');
    Array.prototype.forEach.call(document.querySelectorAll('button'), function (b) {
      if (b.closest('[hidden]')) return;
      var name = (b.getAttribute('aria-label') || b.textContent || '').trim();
      if (!name) issues.push('button without accessible name: ' + b.id);
      if (b.tabIndex < 0) issues.push('button not focusable: ' + b.id);
      if (b.getAttribute('type') !== 'button') issues.push('button without type=button: ' + b.id);
    });
    if (cfg.path === 'write') {
      if (statusEl.getAttribute('role') !== 'status' || statusEl.getAttribute('aria-live') !== 'polite') issues.push('status region is not a polite live region');
      if (['true', 'false'].indexOf(save.getAttribute('aria-pressed')) < 0) issues.push('toggle without aria-pressed');
    } else {
      if (detail.getAttribute('aria-live') !== 'polite') issues.push('detail region is not a polite live region');
      if (['true', 'false'].indexOf(detail.getAttribute('aria-busy')) < 0) issues.push('detail region without aria-busy');
    }
    return { passed: issues.length === 0, issues: issues };
  }

  function sessionSummary() {
    var keys = Object.keys(prefetchCache);
    var used = keys.filter(function (k) { return prefetchCache[k].used; }).length;
    return {
      version: VERSION, config: cfg, user_agent: navigator.userAgent,
      prefetch: { started: keys.length, used: used, unused: keys.length - used },
      requests: requests.length, stray_clicks: strayClicks,
      a11y: a11yAudit(), errors: errors.slice(),
      supported_entry_types: (PerformanceObserver.supportedEntryTypes || []).slice()
    };
  }

  // ---------------- build the page ----------------
  if (cfg.path === 'read') {
    $('read-panel').hidden = false;
    if (cfg.reserve) detail.classList.add('reserve');
    for (var i = 0; i < 2 * cfg.items; i++) {
      var li = document.createElement('li');
      var b = document.createElement('button');
      b.type = 'button'; b.id = 'item-' + i; b.dataset.index = String(i); b.textContent = itemText(i).title;
      li.appendChild(b); list.appendChild(li);
    }
    list.addEventListener('click', onReadClick);
    list.addEventListener('pointerover', onReadHover);
  } else {
    $('write-panel').hidden = false;
    save.addEventListener('click', onSave);
  }

  window.__scroll = { ready: true, error: null, version: VERSION, config: cfg, prepare: prepare, whenDone: whenDone, nextFrames: nextFrames, sessionSummary: sessionSummary, a11yAudit: a11yAudit };
})();
