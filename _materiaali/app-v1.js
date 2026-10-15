/* Joppari – sivuston toiminnot (ei ulkoisia kirjastoja) */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* Header: läpinäkyvä herossa, kiinteä vierittäessä */
  var hdr = $('.hdr');
  function onScroll() { if (hdr) hdr.classList.toggle('solid', window.scrollY > 40); }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* Mobiilivalikko */
  var burger = $('.burger');
  if (burger) burger.addEventListener('click', function () {
    var open = hdr.classList.toggle('open');
    burger.setAttribute('aria-expanded', open);
    document.documentElement.classList.toggle('lock', open);
  });
  $$('.mnav a').forEach(function (a) { a.addEventListener('click', function () { hdr.classList.remove('open'); document.documentElement.classList.remove('lock'); }); });

  /* Auki nyt -merkki (Suomen aika) */
  function fiNow() {
    try {
      var p = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Helsinki', weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false }).formatToParts(new Date());
      var o = {}; p.forEach(function (x) { o[x.type] = x.value; });
      var days = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
      return { d: days[o.weekday], m: (parseInt(o.hour, 10) % 24) * 60 + parseInt(o.minute, 10) };
    } catch (e) { var n = new Date(); return { d: n.getDay(), m: n.getHours() * 60 + n.getMinutes() }; }
  }
  function hm(m) { return Math.floor(m / 60) + (m % 60 ? '.' + ('0' + m % 60).slice(-2) : ''); }
  $$('[data-open]').forEach(function (el) {
    var h; try { h = JSON.parse(el.dataset.open); } catch (e) { return; }
    var now = fiNow(), t = h[now.d], txt = $('span', el);
    if (t && now.m >= t[0] && now.m < t[1]) {
      el.classList.add('is-open'); txt.textContent = 'Auki nyt – suljemme klo ' + hm(t[1]);
    } else {
      el.classList.add('is-closed');
      var nd = now.d, nt = t && now.m < t[0] ? t : null;
      if (!nt) { nd = (now.d + 1) % 7; nt = h[nd]; }
      var dn = ['su', 'ma', 'ti', 'ke', 'to', 'pe', 'la'];
      txt.textContent = 'Suljettu – avaamme ' + (nd === now.d ? 'tänään' : nd === (now.d + 1) % 7 ? 'huomenna' : dn[nd]) + ' klo ' + hm(nt[0]);
    }
  });

  /* Ilmestymisanimaatiot */
  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -8% 0px' }) : null;
  $$('.rv').forEach(function (el) { io ? io.observe(el) : el.classList.add('in'); });

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
