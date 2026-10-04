/* St1 Joppari – NordicHost cPanel "AI App Hosting" -palvelin.
 *
 * Tarjoilee valmiiksi rakennetun sivuston site/-kansiosta, käsittelee lomakkeet (POST /lahetys)
 * ja lounaslistan sekä sivuston tiedotteen (GET /api/lounas, POST /api/login, POST /api/lounas, Päivin hallintasivu /hallinta/).
 * Sivusto rakennetaan omalla koneella (python3 build.py) ja site/ commitoidaan repoon – palvelimella ei tarvita Pythonia.
 *
 * Ympäristömuuttujat (cPanel → sovelluksen asetukset):
 *   PORT            palvelimen antama portti (asettuu yleensä automaattisesti)
 *   MAIL_TO         mihin lomakeviestit tulevat (oletus paivi@joppari.fi)
 *   MAIL_FROM       lähettäjä, saman domainin osoite (oletus no-reply@joppari.fi)
 *   SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
 *                   cPanelin sähköpostitilin SMTP-tiedot. Jos puuttuvat, käytetään palvelimen sendmailia.
 *   MAIL_DRYRUN=1   testaus: viestiä ei lähetetä
 *   ADMIN_PASSWORD  hallintasivun (/hallinta/) salasana lounaslistan päivitykseen. Ilman tätä tallennus on pois päältä.
 *   DATA_DIR        mihin lounaslista ja tiedote tallennetaan (oletus ~/joppari-data). Docker-ympäristössä tämän pitää olla
 *                   pysyvä kansio, joka säilyy uudelleenjulkaisuissa, muuten lista nollautuu jokaisen deployn jälkeen.
 */
'use strict';
const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');
const { URLSearchParams } = require('url');

const ROOT = path.join(__dirname, 'site');
const PORT = process.env.PORT || 3000;
const MAIL_TO = process.env.MAIL_TO || 'paivi@joppari.fi';
const MAIL_FROM = process.env.MAIL_FROM || 'no-reply@joppari.fi';
const SITE_NAME = 'St1 Joppari';
const THANKS = '/kiitos/';
// Lomakkeet: piilokenttä "lomake" valitsee kentät. Oletus = yhteydenotto.
const FORMS = {
  yhteydenotto: {
    subject: 'Yhteydenotto verkkosivulta', error: '/yhteystiedot/?virhe=1',
    fields: [['aihe', 'Aihe'], ['nimi', 'Nimi'], ['puhelin', 'Puhelin'], ['email', 'Sähköposti'], ['viesti', 'Viesti'], ['sivu', 'Lähetetty sivulta']],
  },
  majoitus: {
    subject: 'Majoitustiedustelu', error: '/majoitus/?virhe=1#tiedustelu',
    fields: [['saapuminen', 'Saapuminen'], ['lahto', 'Lähtö'], ['henkilot', 'Henkilömäärä'], ['lemmikki', 'Lemmikki'],
      ['nimi', 'Nimi'], ['puhelin', 'Puhelin'], ['email', 'Sähköposti'], ['viesti', 'Lisätiedot'], ['sivu', 'Lähetetty sivulta']],
  },
};
// Vanhan sivuston osoitteet (build.py kirjoittaa site/redirects.json)
let REDIRECTS = {};
try { REDIRECTS = JSON.parse(fs.readFileSync(path.join(ROOT, 'redirects.json'), 'utf8')); } catch (e) {}

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json', '.xml': 'application/xml; charset=utf-8', '.txt': 'text/plain; charset=utf-8',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon', '.mp4': 'video/mp4', '.woff2': 'font/woff2', '.pdf': 'application/pdf',
};
const SECURITY = {
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'X-Frame-Options': 'SAMEORIGIN',
};

let transport = null;
function mailer() {
  if (transport) return transport;
  const nodemailer = require('nodemailer');
  if (process.env.MAIL_DRYRUN) return (transport = nodemailer.createTransport({ jsonTransport: true }));
  transport = process.env.SMTP_HOST
    ? nodemailer.createTransport({
        host: process.env.SMTP_HOST, port: +(process.env.SMTP_PORT || 465), secure: +(process.env.SMTP_PORT || 465) === 465,
        auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
      })
    : nodemailer.createTransport({ sendmail: true, newline: 'unix', path: '/usr/sbin/sendmail' });
  return transport;
}

function redirect(res, to, code = 303) {
  res.writeHead(code, { Location: to, ...SECURITY });
  res.end();
}

function send(res, status, file, extra = {}, req = null, size = 0) {
  const ext = path.extname(file).toLowerCase();
  const headers = { 'Content-Type': TYPES[ext] || 'application/octet-stream', ...SECURITY, ...extra };
  if (ext === '.html') headers['Cache-Control'] = 'no-cache';
  else if (file.includes(`${path.sep}img${path.sep}`)) headers['Cache-Control'] = 'public, max-age=31536000, immutable';
  else headers['Cache-Control'] = 'public, max-age=86400';
  // Video: Range-tuki (Safari/iOS ei toista videota ilman 206-vastauksia)
  if (ext === '.mp4' && size) {
    headers['Accept-Ranges'] = 'bytes';
    const m = /^bytes=(\d*)-(\d*)$/.exec((req && req.headers.range) || '');
    if (m) {
      let start = m[1] === '' ? size - +m[2] : +m[1];
      let end = m[1] !== '' && m[2] !== '' ? Math.min(+m[2], size - 1) : size - 1;
      if (start >= size || start > end) { res.writeHead(416, { 'Content-Range': `bytes */${size}`, ...SECURITY }); return res.end(); }
      res.writeHead(206, { ...headers, 'Content-Range': `bytes ${start}-${end}/${size}`, 'Content-Length': end - start + 1 });
      return fs.createReadStream(file, { start, end }).pipe(res);
    }
    headers['Content-Length'] = size;
  }
  res.writeHead(status, headers);
  if (req && req.method === 'HEAD') return res.end();
  fs.createReadStream(file).pipe(res);
}

function notFound(res) {
  send(res, 404, path.join(ROOT, '404.html'));
}

function serveStatic(req, res, url) {
  let rel;
  try { rel = decodeURIComponent(url.pathname); } catch { return notFound(res); }
  const file = path.normalize(path.join(ROOT, rel));
  if (!file.startsWith(ROOT)) return notFound(res);
  fs.stat(file, (err, st) => {
    if (!err && st.isFile()) return send(res, 200, file, {}, req, st.size);
    if (!err && st.isDirectory()) {
      if (!rel.endsWith('/')) return redirect(res, rel + '/' + url.search, 301);
      const index = path.join(file, 'index.html');
      return fs.stat(index, (e2, s2) => (!e2 && s2.isFile() ? send(res, 200, index) : notFound(res)));
    }
    notFound(res);
  });
}

function clean(s) {
  return String(s || '').replace(/[\r\n]+/g, ' ').trim();
}

function handleForm(req, res) {
  let body = '';
  req.on('data', (c) => {
    body += c;
    if (body.length > 50000) req.destroy();
  });
  req.on('end', async () => {
    const sp = new URLSearchParams(body);
    const f = {};
    for (const [k, v] of sp) f[k] = f[k] ? `${f[k]}, ${v}` : v;
    // Roskapostisuoja: piilokenttä täytetty tai lomake täytetty alle 3 sekunnissa → hiljainen "kiitos"
    if (f['bot-field']) return redirect(res, THANKS);
    const ts = parseInt(f.ts, 10);
    if (ts && Date.now() / 1000 - ts < 3) return redirect(res, THANKS);
    const form = FORMS[f.lomake] || FORMS.yhteydenotto;
    const ERROR = form.error;
    // Pakollinen: nimi + puhelin tai sähköposti
    if (!clean(f.nimi) || (!clean(f.puhelin) && !clean(f.email))) return redirect(res, ERROR);
    if (clean(f.email) && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(clean(f.email))) return redirect(res, ERROR);

    const text = form.fields.filter(([k]) => String(f[k] || '').trim())
      .map(([k, label]) => `${label}:\n${String(f[k]).trim()}`).join('\n\n');
    try {
      await mailer().sendMail({
        from: `"${SITE_NAME}, verkkosivu" <${MAIL_FROM}>`,
        to: MAIL_TO,
        replyTo: clean(f.email) || undefined,
        subject: `${form.subject}: ${clean(f.nimi)}`,
        text: `${text}\n\n—\nLähetetty verkkosivun lomakkeella (${SITE_NAME}).`,
      });
      redirect(res, THANKS);
    } catch (e) {
      // Tekninen lähetysvirhe (SMTP/sendmail) erotetaan kenttävirheestä: ?virhe=2 → sivu pyytää soittamaan
      const how = process.env.SMTP_HOST ? `SMTP ${process.env.SMTP_HOST}` : 'sendmail (SMTP_HOST puuttuu)';
      console.error(`Lomakkeen lähetys epäonnistui [${how}]:`, e.code || '', e.message);
      redirect(res, ERROR.replace('virhe=1', 'virhe=2'));
    }
  });
}

// ---------------------------------------------------------------------------
// Lounaslista
// ---------------------------------------------------------------------------
const DATA_DIR = process.env.DATA_DIR || path.join(os.homedir(), 'joppari-data');
const LUNCH_FILE = path.join(DATA_DIR, 'lounas.json');
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || '';
const attempts = new Map(); // ip → [aikaleimat]

function json(res, status, obj) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', ...SECURITY });
  res.end(JSON.stringify(obj));
}
function readBody(req, limit, cb) {
  let body = '';
  req.on('data', (c) => { body += c; if (body.length > limit) req.destroy(); });
  req.on('end', () => cb(body));
}
function clientIp(req) {
  return (req.headers['x-forwarded-for'] || '').split(',')[0].trim() || req.socket.remoteAddress || '';
}
function limited(req) {
  const ip = clientIp(req), now = Date.now();
  const list = (attempts.get(ip) || []).filter((t) => now - t < 10 * 60 * 1000);
  attempts.set(ip, list);
  return list.length >= 10;
}
function failed(req) { const ip = clientIp(req); attempts.set(ip, (attempts.get(ip) || []).concat(Date.now())); }
function passwordOk(given) {
  if (!ADMIN_PASSWORD || typeof given !== 'string') return false;
  const a = crypto.createHash('sha256').update(given).digest();
  const b = crypto.createHash('sha256').update(ADMIN_PASSWORD).digest();
  return crypto.timingSafeEqual(a, b);
}
function readLunch() {
  try { return JSON.parse(fs.readFileSync(LUNCH_FILE, 'utf8')); } catch (e) { return { days: {} }; }
}
function sanitizeLunch(input) {
  const out = { price: String(input.price || '').slice(0, 120), note: String(input.note || '').slice(0, 240),
    notice: String(input.notice || '').replace(/[\r\n]+/g, ' ').trim().slice(0, 200), days: {}, updated: new Date().toISOString() };
  const cutoff = new Date(Date.now() - 60 * 864e5).toISOString().slice(0, 10);
  const days = input.days && typeof input.days === 'object' ? input.days : {};
  Object.keys(days).filter((k) => /^\d{4}-\d{2}-\d{2}$/.test(k) && k >= cutoff).sort().slice(-70).forEach((k) => {
    const rows = Array.isArray(days[k]) ? days[k] : [];
    const clean = rows.map((r) => String(r).replace(/[\r\n]+/g, ' ').trim().slice(0, 160)).filter(Boolean).slice(0, 15);
    if (clean.length) out.days[k] = clean;
  });
  return out;
}
function handleApi(req, res, url) {
  if (url.pathname === '/api/lounas' && (req.method === 'GET' || req.method === 'HEAD')) {
    const d = readLunch();
    return json(res, 200, { price: d.price || '', note: d.note || '', notice: d.notice || '', days: d.days || {}, updated: d.updated || null });
  }
  if (url.pathname === '/api/login' && req.method === 'POST') {
    if (!ADMIN_PASSWORD) return json(res, 503, { error: 'ADMIN_PASSWORD puuttuu' });
    if (limited(req)) return json(res, 429, { error: 'liian monta yritystä' });
    return readBody(req, 2000, (body) => {
      let pw = ''; try { pw = JSON.parse(body).password; } catch (e) {}
      if (!passwordOk(pw)) { failed(req); return json(res, 401, { error: 'väärä salasana' }); }
      json(res, 200, { ok: true });
    });
  }
  if (url.pathname === '/api/lounas' && req.method === 'POST') {
    if (!ADMIN_PASSWORD) return json(res, 503, { error: 'ADMIN_PASSWORD puuttuu' });
    if (limited(req)) return json(res, 429, { error: 'liian monta yritystä' });
    if (!passwordOk(req.headers['x-admin-password'])) { failed(req); return json(res, 401, { error: 'väärä salasana' }); }
    return readBody(req, 60000, (body) => {
      let data; try { data = sanitizeLunch(JSON.parse(body)); } catch (e) { return json(res, 400, { error: 'virheellinen data' }); }
      try {
        fs.mkdirSync(DATA_DIR, { recursive: true });
        const tmp = LUNCH_FILE + '.tmp';
        fs.writeFileSync(tmp, JSON.stringify(data, null, 1));
        fs.renameSync(tmp, LUNCH_FILE);
      } catch (e) { console.error('Lounaslistan tallennus epäonnistui:', e.message); return json(res, 500, { error: 'tallennus epäonnistui' }); }
      json(res, 200, { ok: true, updated: data.updated });
    });
  }
  json(res, 404, { error: 'ei löydy' });
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost');
  // www → juuri (yksi kanoninen osoite)
  const host = req.headers.host || '';
  if (host.startsWith('www.')) return redirect(res, `https://${host.slice(4)}${req.url}`, 301);
  const rp = url.pathname.endsWith('/') ? url.pathname : url.pathname + '/';
  if (rp === '/redirects.json/') return notFound(res);
  if (REDIRECTS[rp]) return redirect(res, REDIRECTS[rp], 301);
  if (req.method === 'POST' && url.pathname === '/lahetys') return handleForm(req, res);
  if (url.pathname.startsWith('/api/')) return handleApi(req, res, url);
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    res.writeHead(405, { Allow: 'GET, HEAD', ...SECURITY });
    return res.end();
  }
  serveStatic(req, res, url);
});

server.listen(PORT, () => {
  console.log(`St1 Joppari käynnissä portissa ${PORT}, lounaslista: ${LUNCH_FILE}`);
  if (!ADMIN_PASSWORD) console.warn('ADMIN_PASSWORD puuttuu: lounaslistan tallennus /hallinta/ on pois päältä.');
});
