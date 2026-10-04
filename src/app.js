/* St1 Joppari – sivuston toiminnot (ei ulkoisia kirjastoja) */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var PREVIEW = !!window.JOPPARI_PREVIEW;
  var LS_KEY = 'joppari-lounas';
  document.documentElement.classList.add('js');

  /* Mobiilivalikko */
  var hdr = $('.hdr'), burger = $('.burger');
  if (burger) burger.addEventListener('click', function () {
    var open = hdr.classList.toggle('open');
    burger.setAttribute('aria-expanded', open);
    document.documentElement.classList.toggle('lock', open);
  });
  $$('.mnav a').forEach(function (a) { a.addEventListener('click', function () { hdr.classList.remove('open'); document.documentElement.classList.remove('lock'); }); });

  /* Suomen aika */
  function fiParts(d) {
    try {
      var p = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Helsinki', year: 'numeric', month: '2-digit', day: '2-digit', weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false }).formatToParts(d || new Date());
      var o = {}; p.forEach(function (x) { o[x.type] = x.value; });
      var days = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
      return { d: days[o.weekday], m: (parseInt(o.hour, 10) % 24) * 60 + parseInt(o.minute, 10), iso: o.year + '-' + o.month + '-' + o.day };
    } catch (e) { var n = new Date(); return { d: n.getDay(), m: n.getHours() * 60 + n.getMinutes(), iso: n.toISOString().slice(0, 10) }; }
  }
  function hm(m) { return Math.floor(m / 60) + (m % 60 ? '.' + ('0' + m % 60).slice(-2) : ''); }
  var NOW = fiParts();

  /* Auki nyt -merkki */
  $$('[data-open]').forEach(function (el) {
    var h; try { h = JSON.parse(el.dataset.open); } catch (e) { return; }
    var t = h[NOW.d], txt = $('span', el);
    if (t && NOW.m >= t[0] && NOW.m < t[1]) {
      el.classList.add('is-open'); txt.textContent = 'Auki nyt, suljemme klo ' + hm(t[1]);
    } else {
      el.classList.add('is-closed');
      var nd = NOW.d, nt = t && NOW.m < t[0] ? t : null;
      if (!nt) { nd = (NOW.d + 1) % 7; nt = h[nd]; }
      var dn = ['su', 'ma', 'ti', 'ke', 'to', 'pe', 'la'];
      txt.textContent = 'Suljettu, avaamme ' + (nd === NOW.d ? 'tänään' : nd === (NOW.d + 1) % 7 ? 'huomenna' : dn[nd]) + ' klo ' + hm(nt[0]);
    }
  });

  /* Ilmestymisanimaatiot */
  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -6% 0px' }) : null;
  $$('.rv').forEach(function (el) { io ? io.observe(el) : el.classList.add('in'); });

  /* ---------------- Lounaslista ---------------- */
  var DAYN = ['Sunnuntai', 'Maanantai', 'Tiistai', 'Keskiviikko', 'Torstai', 'Perjantai', 'Lauantai'];
  function isoAdd(iso, n) { var d = new Date(iso + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); }
  function dow(iso) { return new Date(iso + 'T12:00:00Z').getUTCDay(); }
  function monday(iso) { return isoAdd(iso, -((dow(iso) + 6) % 7)); }
  function fiDate(iso) { var p = iso.split('-'); return parseInt(p[2], 10) + '.' + parseInt(p[1], 10) + '.'; }
  function weekNo(iso) { var d = new Date(iso + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() + 3 - (d.getUTCDay() + 6) % 7); var y = new Date(Date.UTC(d.getUTCFullYear(), 0, 4)); return 1 + Math.round(((d - y) / 864e5 - 3 + (y.getUTCDay() + 6) % 7) / 7); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function dishHTML(line) {
    var m = /^(.*?)\s*\(([^()]{1,24})\)\s*$/.exec(line);
    return m ? esc(m[1]) + ' <small>' + esc(m[2]) + '</small>' : esc(line);
  }
  function lsGet() { try { var v = localStorage.getItem(LS_KEY); return v ? JSON.parse(v) : null; } catch (e) { return null; } }
  function lsSet(d) { try { localStorage.setItem(LS_KEY, JSON.stringify(d)); return true; } catch (e) { return false; } }
  /* Esikatselun esimerkkiviikko siirretään aina kuluvalle viikolle */
  function shiftSample(d) {
    if (!d || !d.days) return d;
    var keys = Object.keys(d.days).sort(), mon = monday(NOW.iso), days = {};
    keys.forEach(function (k, i) { days[isoAdd(mon, i)] = d.days[k]; });
    return Object.assign({}, d, { days: days });
  }
  function loadLunch() {
    if (PREVIEW) return Promise.resolve(lsGet() || shiftSample(window.JOPPARI_SAMPLE) || {});
    return fetch('/api/lounas', { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; });
  }

  function renderToday(card, data) {
    var list = data.days && data.days[NOW.iso];
    $('[data-lunch-date]', card).textContent = DAYN[NOW.d] + ' ' + fiDate(NOW.iso);
    if (list && list.length) $('[data-lunch-list]', card).innerHTML = list.map(function (l) { return '<li>' + dishHTML(l) + '</li>'; }).join('');
    if (data.price) $('[data-lunch-price]', card).textContent = data.price;
    var demo = $('[data-lunch-demo]', card); if (demo) demo.hidden = !data.sample;
  }
  function renderWeek(box, data) {
    var mon = monday(NOW.iso), days = data.days || {}, html = '', tabs = '', any = false;
    for (var i = 0; i < 7; i++) {
      var iso = isoAdd(mon, i), list = days[iso] || [], today = iso === NOW.iso;
      if (list.length) any = true;
      tabs += '<button type="button" role="tab" data-day="' + iso + '"' + (today ? ' class="on"' : '') + '>' + DAYN[dow(iso)].slice(0, 2) + ' ' + fiDate(iso) + (today ? '<span class="today">tänään</span>' : '') + '</button>';
      html += '<div class="wday' + (today ? ' is-today show' : '') + '" data-wday="' + iso + '"><h3>' + DAYN[dow(iso)] + '<small>' + fiDate(iso) + '</small></h3>' +
        (list.length ? '<ul class="lc-list">' + list.map(function (l) { return '<li>' + dishHTML(l) + '</li>'; }).join('') + '</ul>'
          : '<p class="lc-empty">Lista päivitetään. Kysy päivän ruoat puhelimitse.</p>') + '</div>';
    }
    $('[data-week-label]', box).textContent = 'Viikko ' + weekNo(mon) + ' · ' + fiDate(mon) + '–' + fiDate(isoAdd(mon, 6));
    if (!any) return;
    var wrap = $('[data-week-days]', box), tabBox = $('[data-week-tabs]', box);
    wrap.innerHTML = html;
    tabBox.innerHTML = tabs;
    if (data.price) $('[data-lunch-price]', box).textContent = data.price;
    if (data.note) { var n = $('[data-lunch-note]', box); n.textContent = data.note; n.hidden = false; }
    var demo = $('[data-lunch-demo]', box); if (demo) demo.hidden = !data.sample;
    $$('button', tabBox).forEach(function (b) {
      b.addEventListener('click', function () {
        $$('button', tabBox).forEach(function (x) { x.classList.toggle('on', x === b); });
        wrap.classList.add('one');
        $$('.wday', wrap).forEach(function (w) { w.classList.toggle('show', w.dataset.wday === b.dataset.day); });
      });
    });
  }
  /* Lounaslista + sivuston tiedote (sama data, haetaan kerran) */
  var lunchBoxes = $$('[data-lunch]'), noticeBar = $('[data-notice]');
  if ((lunchBoxes.length || noticeBar) && !$('[data-admin-login]')) loadLunch().then(function (data) {
    lunchBoxes.forEach(function (b) { b.dataset.lunch === 'week' ? renderWeek(b, data) : renderToday(b, data); });
    if (noticeBar && data.notice) { $('[data-notice-text]', noticeBar).textContent = data.notice; noticeBar.hidden = false; }
  });

  /* ---------------- Hallinta ---------------- */
  var login = $('[data-admin-login]'), app = $('[data-admin-app]');
  if (login && app) {
    var pw = '', data = {}, weekStart = monday(NOW.iso);
    try { pw = sessionStorage.getItem('joppari-pw') || ''; } catch (e) {}
    if (PREVIEW) $('[data-preview-note]').hidden = false;
    var status = $('[data-admin-status]');
    function setStatus(t, cls) { status.textContent = t; status.className = 'admin-status' + (cls ? ' ' + cls : ''); }
    function drawWeek() {
      $('[data-week-title]').textContent = 'Viikko ' + weekNo(weekStart) + ' · ' + fiDate(weekStart) + '–' + fiDate(isoAdd(weekStart, 6));
      var html = '';
      for (var i = 0; i < 7; i++) {
        var iso = isoAdd(weekStart, i), list = (data.days && data.days[iso]) || [];
        html += '<div class="aday' + (iso === NOW.iso ? ' is-today' : '') + '"><label for="d-' + iso + '">' + DAYN[dow(iso)] + '<small>' + fiDate(iso) + (iso === NOW.iso ? ' · tänään' : '') + '</small></label>' +
          '<textarea id="d-' + iso + '" data-iso="' + iso + '" rows="5" placeholder="Yksi ruoka per rivi">' + esc(list.join('\n')) + '</textarea></div>';
      }
      $('[data-admin-days]').innerHTML = html;
      $('#adm-price').value = data.price || '';
      $('#adm-note').value = data.note || '';
      $('#adm-notice').value = data.notice || '';
      setStatus('');
    }
    function collect() {
      var days = {};
      Object.keys(data.days || {}).forEach(function (k) { if (k >= isoAdd(NOW.iso, -21)) days[k] = data.days[k]; });
      $$('[data-admin-days] textarea').forEach(function (t) {
        var rows = t.value.split('\n').map(function (s) { return s.trim(); }).filter(Boolean).slice(0, 15);
        if (rows.length) days[t.dataset.iso] = rows; else delete days[t.dataset.iso];
      });
      return { price: $('#adm-price').value.trim().slice(0, 120), note: $('#adm-note').value.trim().slice(0, 240),
        notice: $('#adm-notice').value.trim().slice(0, 200), days: days };
    }
    function openApp() {
      login.hidden = true; app.hidden = false;
      loadLunch().then(function (d) { data = d && !d.sample ? d : { days: {} }; if (d && d.sample && PREVIEW) data = d; drawWeek(); });
    }
    $('[data-login-form]').addEventListener('submit', function (e) {
      e.preventDefault();
      var val = $('#adm-pw').value, err = $('[data-login-err]');
      err.classList.remove('on');
      if (PREVIEW) { pw = val || 'demo'; return openApp(); }
      fetch('/api/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ password: val }) })
        .then(function (r) {
          if (!r.ok) { err.textContent = r.status === 429 ? 'Liian monta yritystä. Odota hetki.' : r.status === 503 ? 'Salasanaa ei ole vielä asetettu palvelimelle.' : 'Väärä salasana. Yritä uudelleen.'; err.classList.add('on'); return; }
          pw = val; try { sessionStorage.setItem('joppari-pw', val); } catch (x) {}
          openApp();
        }).catch(function () { err.textContent = 'Yhteysvirhe. Yritä uudelleen.'; err.classList.add('on'); });
    });
    if (pw && !PREVIEW) openApp();
    $('[data-week-prev]').addEventListener('click', function () { data = Object.assign(data, collect()); weekStart = isoAdd(weekStart, -7); drawWeek(); });
    $('[data-week-next]').addEventListener('click', function () { data = Object.assign(data, collect()); weekStart = isoAdd(weekStart, 7); drawWeek(); });
    $('[data-copy-prev]').addEventListener('click', function () {
      var n = 0;
      $$('[data-admin-days] textarea').forEach(function (t) {
        var prev = (data.days || {})[isoAdd(t.dataset.iso, -7)];
        if (prev && prev.length && !t.value.trim()) { t.value = prev.join('\n'); n++; }
      });
      setStatus(n ? 'Kopioitu ' + n + ' päivää. Muista tallentaa.' : 'Edelliseltä viikolta ei löytynyt kopioitavaa tyhjiin päiviin.');
    });
    $('[data-logout]').addEventListener('click', function () { try { sessionStorage.removeItem('joppari-pw'); } catch (e) {} location.reload(); });
    $('[data-admin-save]').addEventListener('click', function () {
      var payload = collect();
      setStatus('Tallennetaan…');
      if (PREVIEW) {
        payload.sample = false; data = payload;
        return setStatus(lsSet(payload) ? 'Tallennettu ✓ (esikatselu: vain tähän selaimeen)' : 'Selaimen tallennus ei ole käytössä.', 'ok');
      }
      fetch('/api/lounas', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Admin-Password': pw }, body: JSON.stringify(payload) })
        .then(function (r) {
          if (r.status === 401) { setStatus('Kirjautuminen vanhentui. Kirjaudu uudelleen.', 'bad'); return; }
          if (!r.ok) { setStatus('Tallennus epäonnistui (' + r.status + '). Yritä uudelleen.', 'bad'); return; }
          data = payload;
          var t = new Date(); setStatus('Tallennettu ja julkaistu klo ' + t.getHours() + '.' + ('0' + t.getMinutes()).slice(-2) + ' ✓', 'ok');
        }).catch(function () { setStatus('Yhteysvirhe, muutoksia ei tallennettu.', 'bad'); });
    });
  }

  /* Pizzalista: suodatus + ruotsinkieliset rivit */
  var list = $('[data-pizzas]');
  if (list) {
    $$('.filters button').forEach(function (b) {
      b.addEventListener('click', function () {
        $$('.filters button').forEach(function (x) { x.classList.toggle('on', x === b); });
        var f = b.dataset.f, n = 0;
        $$('.pz', list).forEach(function (p) {
          var show = f === 'kaikki' || (' ' + p.dataset.tags + ' ').indexOf(' ' + f + ' ') > -1;
          p.classList.toggle('hide', !show); if (show) n++;
        });
        $('[data-empty]').hidden = n > 0;
      });
    });
    var sv = $('[data-sv]');
    if (sv) sv.addEventListener('change', function () { document.body.classList.toggle('no-sv', !sv.checked); });
  }

  /* Lomakkeen aihe osoitteesta (?aihe=Ryhmävaraus) */
  var q = new URLSearchParams(location.search);
  if (q.get('aihe')) $$('select[name="aihe"]').forEach(function (s) { s.value = q.get('aihe'); });

  /* Galleria + lightbox */
  var lb = $('.lb'), lbImg = lb && $('img', lb), lbCap = lb && $('figcaption', lb), group = [], idx = 0;
  function show(i) { idx = (i + group.length) % group.length; var a = group[idx]; lbImg.src = a.getAttribute('href'); lbImg.alt = a.dataset.lb || ''; lbCap.textContent = (a.dataset.lb || '') + '  ·  ' + (idx + 1) + ' / ' + group.length; }
  function close() { lb.hidden = true; document.documentElement.classList.remove('lock'); }
  $$('a[data-lb]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      if (!lb) return;
      e.preventDefault();
      group = $$('a[data-lb]', a.closest('.gal') || document);
      lb.hidden = false; document.documentElement.classList.add('lock');
      show(group.indexOf(a));
    });
  });
  if (lb) {
    $('.lb-x', lb).addEventListener('click', close);
    $('.lb-p', lb).addEventListener('click', function () { show(idx - 1); });
    $('.lb-n', lb).addEventListener('click', function () { show(idx + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
    document.addEventListener('keydown', function (e) {
      if (lb.hidden) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(idx - 1);
      if (e.key === 'ArrowRight') show(idx + 1);
    });
    var tx = null;
    lb.addEventListener('touchstart', function (e) { tx = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', function (e) { if (tx === null) return; var d = e.changedTouches[0].clientX - tx; if (Math.abs(d) > 50) show(idx + (d < 0 ? 1 : -1)); tx = null; });
  }

  /* Palvelimen palauttama lomakevirhe: ?virhe=1 = puuttuva tieto, ?virhe=2 = tekninen lähetysvirhe */
  var virhe = new URLSearchParams(location.search).get('virhe');
  if (virhe) $$('form.form').forEach(function (f) {
    var err = $('[data-err]', f); if (!err) return;
    if (virhe === '2') err.innerHTML = 'Viestin lähetys ei onnistunut teknisen vian vuoksi. Soita meille: <a href="tel:+35816512771">016 512 771</a>';
    err.classList.add('on');
    f.scrollIntoView({ block: 'center' });
  });

  /* Lomakkeet: tarkistus, esikatselutila */
  $$('form.form').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      var err = $('[data-err]', f), bad = [];
      var nimi = f.nimi, tel = f.puhelin, mail = f.email;
      $$('.bad', f).forEach(function (x) { x.classList.remove('bad'); });
      if (!nimi.value.trim()) bad.push(nimi);
      if (!tel.value.trim() && !mail.value.trim()) bad.push(tel);
      var ts = $('input[type=checkbox][required]', f);
      if (ts && !ts.checked) bad.push(ts);
      if (bad.length) { bad.forEach(function (x) { x.classList.add('bad'); }); if (err) err.classList.add('on'); e.preventDefault(); bad[0].focus(); return; }
      if (f.dataset.preview) { e.preventDefault(); location.href = 'kiitos.html'; }
    });
  });
})();
