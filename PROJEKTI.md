# St1 Joppari: projektin tausta ja päätökset

Kopio Äijä Groupin projektimuistiosta. Asiakkaan linjaukset ja tehdyt päätökset.

St1 Joppari, Pellontie 31, 95700 Pello; 016 512 771, paivi@joppari.fi, yhteyshenkilö Päivi. Aseman virallinen nimi St1 Pello.
Asemalla HelmiSimpukka Express ja Driver's → St1 valvoo brändiä.

**Asiakkaan linjaukset 29.9.2026 (kierros 2):** nimi aina "St1 Joppari", St1:tä ja Jopparia EI saa erottaa. Ilme HelmiSimpukan/St1 Wayn maailmasta
(vihreä #00463c, kerma #f3f1d1, Nunito Sans, pilleripainikkeet) – ei omaa "sooloilua". À la cartea ei ole ollut vuosiin, grillilista poistettu;
joka päivä kotiruoka- ja salaattibuffet klo 11–16. Hinnat vain asiakkaan hinnastokuvista (pizzat 2026, majoitus 2026) – ensimmäisen kierroksen
vanhan sivun hinnat olivat väärät. Lounaslista etusivulle + helppo hallinta Päiville.

Toteutus: /hallinta/ (salasana env ADMIN_PASSWORD) → server.js POST /api/lounas → DATA_DIR (~/joppari-data) lounas.json; sivut GET /api/lounas.
Demoissa (Netlify/artifakti) esimerkkiviikko + localStorage. Preview-artifact https://claude.ai/artifact/6Ua4VCmkdXvDkmfcaSWNsi.

**Kierros 3 (1.10.2026):** "makuukammarit" liian erottelevaksi → "Jopparin majoitus". Driver's-painikkeet St1-punaisella #ed1b2e.
HelmiSimpukka Express -logo ei löydy St1:n omilta sivuilta; virallinen PNG on st1leppavirta.fi/uploads/.../helmisimpukka-express-logo_orig.png (300 px) → vektori pyydettävä St1:ltä.

**4.10.2026:** hallintaan lisätty sivuston yläreunan tiedote (notice), lomakkeisiin ?virhe=2 (SlatePron SMTP-oppi), ajatusviivat poistettu.
Git-repo iCloudin Joppari/-kansiossa, **pushattu 6.10.2026 → github.com/Aija-group/joppari (julkinen, main)**. NordicHost-tiimin Admin-oikeutta ei voitu tarkistaa täältä. Live odottaa Päivin domainin siirtoavainta (Domainkeskus/Euronic Plesk).
Avoin riski: DATA_DIR pysyvyys AI App Hostingin Docker-kontissa → Valtterin varmistettava.

**6.10.2026:** tarkistettu puhtaasta kloonista, demotekstit pois tuotannosta, lisäohjaukset /hampurilaiset-suolaiset/ /fb/ /po-russki/, hallinnan salasana sovittu (ei kirjattu mihinkään). Obsidian-kortti nimetty uudelleen `Asiakkaat/St1 Joppari.md`.

**How to apply:** iteroi scratchpadissa, launch.json "joppari-site" ajaa oikeaa Node-palvelinta (testisalasana, DATA_DIR scratchpadissa).
Asiakkaan hinnat/tiedot aina asiakkaalta, ei vanhalta sivulta. Liittyy feedback-ei-lupauksia.

- **27.10.2026 Search Console:** URL-etuliiteominaisuus https://joppari.fi/ Sulon Google-tilillä, vahvistettu HTML-tagilla (`content.py` COMPANY["google_verification"], build.py lisää metan robots-metan perään), sitemap.xml lähetetty (6 sivua, Onnistui), etusivun indeksointipyyntö lähetetty. Sivu on tuotannossa joppari.fi:ssä (NordicHost 1239/1321, julkinen repo-osoite). **Avoinna julkaisun jälkeisistä toimista:** Lighthouse ennen/jälkeen, laite- ja selaintesti, nopeus (Google Fonts ladataan googleapis.comista → omalle palvelimelle), metat (etusivun kuvaus 178 ja lounas 162 merkkiä), geneerinen sähköposti, Bing Webmaster Tools.
