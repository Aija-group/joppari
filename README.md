# St1 Joppari – sivustouudistus (joppari.fi)

Staattinen sivusto + pieni Node-palvelin. `content.py` (tekstit, hinnat, aukioloajat, ohjaukset) + `build.py` → `site/`.
Tyylit `src/style.css`, toiminnot `src/app.js`, kuvat `src/kuvat/`, logot `src/st1-logo.png` ja `src/helmisimpukka-express-logo.png`.

    python3 build.py                                        # NordicHost (server.js + site/) + ../joppari-nordichost.zip
    HOSTING=netlify python3 build.py                        # Netlify-demo + ../joppari-netlify.zip
    HOSTING=netlify python3 build.py --preview --artifact   # esikatselu Claude-artifaktina (preview/)

Yritys: **St1 Joppari** – aseman virallinen nimi **St1 Pello**. Pellontie 31, 95700 Pello. 016 512 771, paivi@joppari.fi.
Nimeä ei saa erottaa: aina "St1 Joppari", ei pelkkä "Joppari" tai "Kahvila-Ravintola Joppari" (asiakkaan linjaus 29.9.2026).

Esikatselu: https://claude.ai/artifact/6Ua4VCmkdXvDkmfcaSWNsi

## Kierros 2 (29.9.2026, asiakkaan palaute)
- **Ilme St1:n HelmiSimpukka-maailmaan** (asemalla HelmiSimpukka Express ja Driver's; St1 valvoo brändiä): tummanvihreä #00463c,
  kerma #f3f1d1, valkoinen pohja, Nunito Sans (HelmiSimpukan oma fontti), pilleripainikkeet, 24 px kortit, vihreä header ja footer.
  Logo = St1-logo + "Joppari" samassa lukituksessa. Footerissa St1- ja HelmiSimpukka-logot (haettu helmisimpukka.fi:n footerista).
- **Pizzahinnat** päivitetty painetusta hinnastosta 2026 (myös pannupizzat, lounaspizzat 11,20 / 12,20 / 13,20, valkosipuli 1,60 / 3,20).
  Kasvis- ja Tulinen-merkinnät kuten hinnastossa.
- **Majoitushinnat 2026**: 80 / 105 / 130 / 155 / 185 €, lisävuode 50 €, aamupala erikseen 10 €, koirista siivousmaksu 20 €,
  aamiainen arkisin 7.30–9.30 ja viikonloppuna 9–10, ovien leveydet (WC 60 cm, muut 80 cm).
- **À la carte ja grillilista poistettu.** Tilalle `/lounas/`: kotiruoka- ja salaattibuffet joka päivä klo 11–16. Vanha `/la-carte/` → 301 `/lounas/`.
  Driver's-pikaruoasta linkki HelmiSimpukan Pello-sivulle (siellä ketjun hinnat ja edut) – ei omaa hintalistaa.
- **Lounaslista etusivulla** heti herossa ("Päivän lounas" -kermakortti HelmiSimpukan tapaan) + koko viikko `/lounas/`-sivulla.

## Kierros 3 (1.10.2026)
- Driver's-ruokalista-painikkeet St1-punaisella (#ed1b2e, mitattu St1-logosta), myös lounassivun Driver's-kortti.
- "Jopparin makuukammarit" → **"Jopparin majoitus"** (etusivu, majoitussivun otsikko, schema).
- HelmiSimpukka-logo vaihdettu **HelmiSimpukka Express** -logoon (asema-osio + footer). Virallinen logo löytyi St1 Leppävirran sivulta
  (st1leppavirta.fi, musta PNG valkoisella) – värjätty kermaksi vihreälle pohjalle. Alkuperäinen `_materiaali/helmisimpukka-express-logo-orig.png`.
  Logo on vain 300 px leveä → pyydä St1:ltä vektoriversio (SVG/PDF) ennen julkaisua.
- Pizza- ja majoitushinnat tarkistettu asiakkaan listaa vasten – kaikki täsmäävät (vkl-aamiainen 9.00–10.00 käsinkirjoitetun listan mukaan).

## Lounaslistan hallinta (Päivi)
- Osoite **joppari.fi/hallinta/** (ei valikossa, ei hakukoneissa). Kirjautuminen salasanalla (env `ADMIN_PASSWORD`). Toimii puhelimella.
- Päivi päivittää:
  - **viikon lounaslistan** ma–su, yksi ruoka per rivi, ruokavaliomerkinnät sulkuihin perään, esim. `Lihamureke ja ruskea kastike (L, G)`;
    viikkoja voi selata eteen ja taakse, "Kopioi edellinen viikko" täyttää tyhjät päivät
  - **buffetin hinnan** ja **lisätiedon** (näkyvät listan alla)
  - **tiedotteen koko sivuston yläreunaan** (esim. poikkeavat aukioloajat), tyhjä = ei tiedotetta
- "Tallenna ja julkaise" päivittää heti etusivun "Päivän lounas" -kortin, /lounas/-sivun viikkolistan ja tiedotteen.
- Tekniikka: `POST /api/lounas` → `DATA_DIR/lounas.json`; sivut lukevat `GET /api/lounas`. Salasana tarkistetaan vakioaikaisesti,
  10 väärää yritystä / 10 min / IP → 429. Netlify-demossa ja artifaktissa (ei palvelinta) näkyy esimerkkiviikko ja tallennus menee vain selaimen muistiin.
- Lomakkeet: puuttuva tieto → `?virhe=1`, tekninen lähetysvirhe (SMTP) → `?virhe=2`, jolloin lomake pyytää soittamaan. Syy lokiin.

## Rakenne
- **Etusivu**: kuvakortti-hero (oikea ilmakuva asemasta) + Päivän lounas → tietonauha (auki nyt, buffet, puhelin, osoite) → Lounas/Pizzat/Majoitus →
  Päivi + tervetuloa → Jopparin pizza → St1 Pello -asema (HelmiSimpukka Express, Driver's, St1 Way, polttoaineet, nestekaasu) → majoitus →
  ryhmät/linja-autot (55 paikkaa) + English/svenska → aukiolo ja kartta
- `/lounas/`, `/pizzat/` (suodattimet, FI/SV-kytkin), `/majoitus/` (hinnasto, galleria, tiedustelulomake), `/yhteystiedot/`, `/hallinta/`,
  `/tietosuojaseloste/`, `/kiitos/`, 404
- Ohjaukset: `/la-carte/` ja `/lounaslista/` → `/lounas/`, `/hankietukortti/` → `/#asema`, `/in-english/` → `/#english`. Kanoninen joppari.fi.

## Kuvat
- Oikeat: Travel Pellon kuvat (asema ilmasta, huoneet, sauna), vanhan sivun huonegalleria, Päivin kuva.
- AI (Higgsfield gpt_image_2_5, merkitty "Havainnekuva"): buffet, salaattipöytä, poropizza, kahvi+pulla, Tornionjoki. Vaihda oikeisiin kun saadaan.

## Vahvistettava ennen julkaisua
1. **St1:n brändihyväksyntä**: St1- ja HelmiSimpukka-logojen käyttö sekä värit/fontti – kannattaa näyttää St1:n aluepäällikölle ennen julkaisua.
2. **Buffetin hinta** – ei tiedossa. Päivi voi kirjoittaa sen hallintaan (näkyy listan alla).
3. Aukioloajat ma–pe 7–20, la–su 9–20 (vanha sivu + HelmiSimpukan Pello-sivu).
4. Päivin sukunimi/rooli ja lupa kuvan käyttöön.
5. Sisältääkö buffet salaattipöydän lisäksi leivän/juoman/kahvin? (ei luvattu sivulla – Päivi voi lisätä lisätietoon)
6. Lomakkeiden vastaanottaja paivi@joppari.fi (server.js `MAIL_TO`).

## Asennus NordicHostiin (Valtteri)
Repo: **github.com/Aija-group/joppari** (julkinen, NordicHost-tiimillä Admin). `site/` on valmiiksi rakennettu ja commitoitu, palvelimella ei tarvita Pythonia.
AI App Hosting: Build `npm install`, Start `npm run start` (package.jsonissa no-op `build`-skripti).

**Ympäristömuuttujat (ei koskaan repoon):**
| Muuttuja | Arvo |
|---|---|
| `ADMIN_PASSWORD` | Päivin hallintasivun salasana (sovitaan Päivin kanssa) |
| `DATA_DIR` | **Pysyvä kansio**, joka säilyy uudelleenjulkaisuissa. Muuten lounaslista ja tiedote nollautuvat jokaisen deployn jälkeen. |
| `MAIL_TO` | `paivi@joppari.fi` (oletus) |
| `MAIL_FROM`, `SMTP_HOST`, `SMTP_PORT=465`, `SMTP_USER`, `SMTP_PASS` | cPanel-sähköpostitili, esim. no-reply@joppari.fi; `SMTP_HOST` = palvelimen hostname, ei Cloudflaren takana oleva mail.joppari.fi |

**Domain ja posti:** joppari.fi on nyt Domainkeskuksella / Euronicin Plesk-palvelimella (blade8.euronic.fi), ja paivi@joppari.fi -posti on siellä.
Siirtoon tarvitaan Päiviltä **domainin siirtoavain** (välittäjänvaihto). NordicHost siirtää myös postilaatikot sisältöineen.
Kanoninen osoite joppari.fi (www ohjautuu juureen). Vanhat osoitteet `/la-carte/`, `/lounaslista/`, `/hankietukortti/`, `/in-english/` ohjautuvat 301:llä (site/redirects.json).

**Julkaisun jälkeen tarkista:** `/api/lounas` vastaa JSONia, `/hallinta/` kirjautuu, tallennus näkyy etusivulla, lomake lähtee (muuten `?virhe=2`
ja syy sovelluksen lokissa), ja lista säilyy seuraavan deployn yli.

## Testattu (Node 22, 4.10.2026)
Sivut 200, vanhat URL:t 301, 404, kirjautuminen (väärä 401, oikea 200), tallennus ilman salasanaa 401, tallennus → etusivu, /lounas/ ja tiedote,
lomakkeet → /kiitos/, puuttuvat tiedot → ?virhe=1, SMTP-virhe → ?virhe=2.
