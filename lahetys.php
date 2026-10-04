<?php
/* Äijä Group – yhteydenottolomakkeen käsittelijä webhotelliin (Plesk/cPanel).
   Korvaa Netlify Formsin. Kopioi site/-kansion juureen, säädä ASETUKSET.
   Vaatii: PHP 7.4+ ja toimivan mail()-funktion (on kaikissa webhotelleissa). */

/* ============ ASETUKSET ============ */
$VASTAANOTTAJA = 'info@asiakas.fi';          // mihin viestit tulevat
$LAHETTAJA     = 'no-reply@asiakas.fi';      // PITÄÄ olla saman domainin osoite (SPF)
$SIVUSTO       = 'Asiakas Oy';
$KIITOS_URL    = '/kiitos/';
$VIRHE_URL     = '/tarjouspyynto/?virhe=1';
$KENTAT        = ['palvelu', 'kohdetyyppi', 'laajuus', 'sijainti', 'aikataulu', 'kuvat', 'viesti', 'terasluettelo', 'nimi', 'yritys', 'email', 'puhelin'];  // näytettävät kentät
$PAKOLLISET    = ['nimi', 'email', 'puhelin'];
/* =================================== */

function pois($url) { header('Location: ' . $url, true, 303); exit; }
function siisti($s) { return trim(str_replace(["\r", "\n", "%0a", "%0d"], ' ', (string)$s)); }

if ($_SERVER['REQUEST_METHOD'] !== 'POST') pois($VIRHE_URL);

// 1. Honeypot – botit täyttävät piilokentän
if (!empty($_POST['bot-field'])) pois($KIITOS_URL);   // hiljainen hylkäys

// 2. Aikaleima – alle 3 s täyttö on botti
$ts = isset($_POST['ts']) ? (int)$_POST['ts'] : 0;
if ($ts > 0 && (time() - $ts) < 3) pois($KIITOS_URL);

// 3. Pakolliset kentät
foreach ($PAKOLLISET as $k) {
    if (empty(trim($_POST[$k] ?? ''))) pois($VIRHE_URL);
}
$email = filter_var(trim($_POST['email'] ?? ''), FILTER_VALIDATE_EMAIL);
if (!$email) pois($VIRHE_URL);

// 4. Koosta viesti
$rivit = [];
foreach ($KENTAT as $k) {
    $v = trim($_POST[$k] ?? '');
    if ($v !== '') $rivit[] = ucfirst($k) . ":\n" . $v;
}
$rivit[] = "---\nLähetetty: " . date('j.n.Y H:i') . "\nSivu: " . siisti($_POST['sivu'] ?? '-')
         . "\nIP: " . ($_SERVER['REMOTE_ADDR'] ?? '-');

$otsikko = 'Yhteydenotto verkkosivuilta – ' . siisti($_POST['nimi']);
$runko   = implode("\n\n", $rivit);

$otsakkeet = [
    'From: ' . mb_encode_mimeheader($SIVUSTO, 'UTF-8') . ' <' . $LAHETTAJA . '>',
    'Reply-To: ' . $email,
    'Content-Type: text/plain; charset=UTF-8',
    'MIME-Version: 1.0',
    'X-Mailer: PHP/' . phpversion(),
];

$ok = @mail($VASTAANOTTAJA,
            mb_encode_mimeheader($otsikko, 'UTF-8'),
            $runko,
            implode("\r\n", $otsakkeet),
            '-f' . $LAHETTAJA);

// 5. Varmuuskopio levylle – sähköposti voi kadota, tämä ei
@file_put_contents(__DIR__ . '/.lomake-loki.txt',
    date('c') . " | " . ($ok ? 'OK' : 'FAIL') . " | " . str_replace("\n", ' / ', $runko) . "\n",
    FILE_APPEND | LOCK_EX);

pois($ok ? $KIITOS_URL : $VIRHE_URL);
