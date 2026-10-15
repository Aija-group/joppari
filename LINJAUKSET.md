# Äijä Groupin sivustolinjaukset

Yleiset säännöt kaikille Äijä Groupin tekemille sivustoille. Noudata näitä muutoksissa.

## feedback-ei-ajatusviivoja

Sulo 4.10.2026 (Kyrönlahden Porakaivo): "Ota kaikista sivuston teksteistä ajatusviiva pois ja korjaa ne pilkuilla." Koskee kaikkea: otsikot, SEO-titlet, ingressit, painikkeet, myös asiakkaan vanhat blogiartikkelit ja EN-versiot.

**Why:** ajatusviiva on tyypillinen tekoälytekstin tuntomerkki (liittyy feedback-ei-ai-ilmetta-eika-toistoa).

**How to apply:** kirjoita tekstit alusta asti ilman " – "-rakennetta. Pelkkä mekaaninen pilkku ei riitä: lisää sidesana (niin, joten, sillä, ja) tai jaa kahdeksi virkkeeksi, ja pienennä pilkun jälkeinen iso alkukirjain. Titleissä erottimena "|" tai kaksoispiste. Vanhan sivun artikkeleihin build.py:n no_dash() (malli: Kyronlahden-Porakaivo/build.py). Numerovälit (60–120 m, 1–2 päivää) eivät ole ajatusviivoja.

## feedback-ei-lupauksia

Sivustotekstiin ei lisätä palvelulupauksia, joita asiakkaan omassa materiaalissa ei ole: "koehionta ennen kauppaa", "maksuton", "ennen laitepäätöstä", "ennen investointia" jne. Kirjoita asiakkaan oma väite sellaisenaan (Finnris: "testit ja koeajot tuotteillenne").

**Why:** Finnris 27.9.2026: kirjoitin "koehionta ennen kauppaa" pääviestiksi; Sulo epäili ja pyysi tarkistamaan kahdesti – vanha sivu ei luvannut sitä. Myös teetetyn uudelleenkirjoituksen vastaavat muotoilut poistettiin: "Ei luvata mitään vielä."

**How to apply:** Myyvä teksti rakennetaan tosiasioista. Jos lupaus parantaisi sivua, lisää se README:n vahvistuslistalle, älä sivulle. Tarkista myös ulkopuolelta tulevat (teetetyt) tekstit tätä vasten ennen vientiä ja kerro Sulolle mitä poistit. Liittyy project-finnris-sivustouudistus.

**Hinnat (Jääkärihirsi 3.10.2026):** "älä laita hintoja jos niitä ei ole ilmoitettu missään" – näytä vain asiakkaan itse ilmoittamat mallikohtaiset hinnat. Ei johdettuja hintoja: tuoteryhmän "alkaen" vain jos jokaisella mallilla on hinta, ei summia, ei "Hinta tarjouksella" -täytteitä.

## feedback-ei-ai-ilmetta-eika-toistoa

Sivustoissa vältetään: beige/kerma-taustat, seriffi-display + lämmin aksentti -yhdistelmä, koristeelliset muodonrikkojat (esim. teltan aaltohelma), pienet versaali-yläotsikot (eyebrow) otsikoiden päällä, keksityt kuvalogot kun tekstilogo riittää. Etusivu pidetään tiiviinä: jokainen osio tekee eri asian; ei erillistä työkalua + samaa listaa kortteina, ei kahta CTA-bändiä peräkkäin.

**Why:** Rent A Tent v1 (2.10.2026): "Poista tuo beige taustaväri, huutaa tekoälyä", logo ja punavalkoiset lipakkeet "ei hyvännäköinen", "etusivu tuhottoman pitkä", "vältä päällekkäisiä elementtejä", "älä ala oikomaan". v2 hyväksyttäväksi: valkoinen + viileä harmaa, punainen vain korosteena, groteski (Schibsted Grotesk), kaksisävyiset otsikot (nimi + harmaa alarivi), vierasmäärä suodattaa suoraan telttakortit, tarjouslomake etusivulla.

**How to apply:** Lähde neutraalista modernista pohjasta (valkoinen/harmaa, yksi brändiväri korosteena, groteski). Ennen rakentamista listaa etusivun osiot ja poista ne, jotka toistavat toisiaan. Myyntielementit = toiminnallisia (suodatin, laskuri, lomake, hinnat näkyvissä), ei koristeita. Liittyy feedback-visuaalinen-laatutaso-ja-palautetapa.

**Tarkennus 3.10.2026 (Jääkärihirsi):** puhdas valkoinen oli liian kylmä hirsirakentajalle – Sulo pyysi "hieman lämpimämpää kuin valkoista". Hyväksytty suunta: hyvin vaalea lämmin pohja (#faf7f2), hiekansävyiset paneelit (#f2ece2), lämpimät harmaat; ei voimakasta beigeä/kermaa. Lämpö sovitetaan toimialaan (puu/hirsi = lämmin).

## feedback-klinininen-ilme-vahan-pikkutekstia

Mik-Mak 3.10.2026: v1 (tumma täysleveä hero, tietonauha, chipit, luvut, kuvabändit, yläotsikot joka osiossa) sai palautteen
"enemmän kliiniä, selkeää ilmettä, aivan liikaa pikkutekstiä ja turhaa pikkupränttiä – nosta tärkeimmät asiat ylös ja tee kaunista kädenjälkeä".
Referenssinä vaalea catering-sivu: off-white tausta, iso serif-otsikko jossa yksi sana kullalla, ylhäältä kuvattu ruoka valkoisella pohjalla oikealla,
kolme ikonikorttia (otsikko + yksi rivi), kuvakortit joissa otsikko + yksi rivi, kultainen pilleripainike.

**Why:** Liika pieni teksti tekee sivusta levottoman ja halvan näköisen, vaikka sisältö olisi oikeaa. Tämä tarkentaa feedback-visuaalinen-laatutaso-ja-palautetapa:
"Omia-taso" ei tarkoita tummaa täysleveää heroa vaan viimeisteltyä kokonaisuutta.

**How to apply:** Osio = otsikko + korkeintaan yksi lause + sisältö. Ei kickereitä joka osioon, ei näkyviä murupolkuja, ei kuvien päälle leimoja
(AI-kuvat kerrotaan README:ssä/Sulolle). Tärkein asiakkaan asia (esim. päivän lounas) heti heron jälkeen. Mobiilissa kortit tiiviiksi listaksi.
Vaalean heron kuvaksi toimii AI-kuva "overhead, ruoka oikeassa reunassa, vasen 55 % tyhjää off-white taustaa" + liukuvärihäivytys sivun taustaan.

**Tarkennus samana päivänä (v3):** kliini ei saa olla tyhjä – "voisi lisätä taustalle muutakin kuvia kuin pelkkää beigeä". Ratkaisu (hyväksyntä vielä auki):
vaaleat flat lay -taustakuvat (raaka-aineet vain reunoilla, keskusta tyhjä, tekstit/kortit päällä) + täysleveät kuvabändit (tumma liukuväri, valkoinen otsikko + yksi lause).

## feedback-ei-ai-taloja

Tekoälykuva valmiista talosta (laajennus, huvila tms.) näyttää epäluonnolliselta eikä sitä saa käyttää sivustolla lainkaan – ei edes "havainnekuvana" alt-tekstillä.

**Why:** A2 4.10.2026: Sulo näki laajennussivun AI-talon ja kysyi "mikäs tämä kuva on?" → "Tuo on niin epäluonnollinen kuva että älä laita yhden ainutta tuollaista sivustolle." Lisäksi se antaa väärän kuvan asiakkaan kädenjäljestä.

**How to apply:** Rakennus-/talo-/kohdekuvat aina asiakkaan omista kuvista (tarvittaessa Higgsfield upscale tai remove_background omasta kuvasta). AI vain työ- ja tunnelmakuviin, joissa ei ole valmista rakennusta (piirustuspöytä, luonnos, CAD-näyttö, runkovaihe). Puuttuvan kohdekuvan tilalle asiakkaan piirustus tai toinen oma kuva. Liittyy feedback-visuaalinen-laatutaso-ja-palautetapa, project-a2-sivustouudistus.

## feedback-wau-taso-brandivari

Rasol v1 (siisti, navy + aurinko-oranssi CTA) sai palautteen: ei tarpeeksi moderni/visuaalisesti hieno, "sininen on heillä selkeästi brändiväri, nyt sitä on täysin alihyödynnetty", "tästä ei tule WAU-fiilistä", lomakkeiden kulmat pyöristettäviksi.

**Why:** Teknisesti valmis ja siisti ei riitä; ensivaikutelma ratkaisee myynnin.

**How to apply:** (1) Rakenna paletti asiakkaan logon väristä alusta asti: brändiväri painikkeisiin, korostuksiin ja tummiin osioihin, ei vieraaksi toimintaväriksi. (2) Lähde liikkeestä ja syvyydestä: herovideo (Higgsfield Kling std ~6 kr), lasipinnat, hehkut, nauhat, parallaksi. (3) Älä upota iframe-lomakkeita (Leadoo tms.), joiden ulkoasua ei voi säätää; käytä omaa lomaketta ja pidä vain chat-kupla. Liittyy feedback-visuaalinen-laatutaso-ja-palautetapa, project-rasol-sivustouudistus.

## feedback-aito-hero-ei-ai-videota

Rakennus Viiru 6.10.2026: Kling-herovideo (AI-työmaa) sai palautteen "heroa pitää saada aidommaksi, liian AI haisee tuosta videosta". Henkilöhero (irrotettu työntekijä brändi-taustalla) hylättiin myös: "Ei heroa noin." Hyväksytty suunta: asiakkaan oma toteutettu kohde täysleveänä valokuvana, teksti tumman häivytyksen päällä.

**Why:** Hero on ensivaikutelma; AI-tunnistettava kuva heikentää luottamusta. Lisäksi "vanhan sivun kuvat" ≠ asiakkaan omat kuvat – usein kuvapankkia.

**How to apply:** Älä tee AI-herovideota/-kuvaa ensisijaisena. Erottele vanhan sivun kuvat: aidot (henkilöt, työmaat, puhelinkuvat) vs. kuvapankki (unsplash/AdobeStock-nimet, liian täydelliset) ja kerro jako Sulolle. Herossa asiakkaan oma kohdekuva täysleveänä (ei irrotettuja henkilöitä); AI vain sivuosioiden työvaihekuviin. Liittyy feedback-ei-ai-taloja, feedback-visuaalinen-laatutaso-ja-palautetapa.

## feedback-kuvat-ennen-toimintoja

Jyväskiinteistö v1 (uurrelasihero, kiuaslaskuri, lattiavalitsin, SVG-leikkaus, 3-askelinen velho) sai palautteen: "pitää olla PALJON enemmän kuvamateriaalia, vähemmän toiminnallisuuksia, enemmän kuvia jotka aidosti kertovat mistä on kyse, liian design, mallia Omiasta". Lisäksi: markkinointiystävällinen, paljon asiakasta hyödyttävää infoa, Google-arvostelut näkyvästi, brändi-ilme saa modernisoitua.

**Why:** Sivun pitää myydä ja näyttää, mitä yritys tekee. Työkalut ja koristeefektit eivät korvaa kuvia, ja ilman kuvia sivu näyttää designharjoitukselta.

**How to apply:** Jos asiakkaalla ei ole omia kuvia, tee heti alussa 25–35 Higgsfield-kuvaa (työvaiheet kasvottomina + valmiit tilat) ja rakenna sivu niiden varaan Omia-rakenteella. Korkeintaan yksi työkalu, jos se on aidosti hyödyllinen (esim. KTV-laskuri oppaassa). Lisää oppaat/UKK asiakasta hyödyttäväksi sisällöksi ja nosta Google-arvostelut heroon. Käytä brändin väriä ja fonttia (vanhan sivun CSS:stä). Liittyy feedback-wau-taso-brandivari, feedback-visuaalinen-laatutaso-ja-palautetapa, project-jyvaskiinteisto-sivustouudistus.

## feedback-isot-elementit-kokonaiset-kuvat

Rakennus Kangasniemi v1 (kaari-ikkunasuikaleet herossa, pinoutuvat kortit, sumea huonepaneeli, pientä harvennettua versaalia) sai palautteen: "suhteellisen epäselkeä elementeiltään, isompia elementtejä, kokonaisia kuvia ja siistimpää ulkoasua".

**Why:** Talo/kohde pitää nähdä kokonaisena. Rajaukset (kaaret, kapeat suikaleet, pystykuva vaakakehyksessä) ja monta pientä tekstiä tekevät designista levottoman, vaikka ideat ovat hienoja.

**How to apply:** Kohdekuvat 3:2 tai luonnollisessa kuvasuhteessa, isot kortit 1–2 palstassa, otsikko + yksi tietorivi. Hero = yksi koko näkymän valokuva (tai hidas kuvaslideri). Efektimuodot vain logoon/henkilökuviin. Leipäteksti 18 px, ei pieniä versaalitunnisteita. Liittyy feedback-klinininen-ilme-vahan-pikkutekstia, feedback-kuvat-ennen-toimintoja, project-rakennuskangasniemi-sivustouudistus.

## feedback-kieliversiot-samalla-sisallolla

Kun asiakkaan vanhalla sivulla on EN/SV-versiot, uusi sivu tarvitsee ne kokonaisina: samat palvelusivut, laskurit ja lomakkeet käännettyinä, kielivalitsin samaan sivuun toisella kielellä, hreflang. Artikkelit/referenssit saavat jäädä suomeksi, jos vanhallakin sivulla jäivät.

**Why:** Lotus Demolition 29.9.2026: tein EN/SV yksisivuisina, Sulo: "miksi kielikännöksillä sivu ei toimi" / "ei ole samaa sisältöä kielikäännöksillä". Vanhan sivun omat käännökset olivat 3–8× lyhyempiä, joten käännettiin FI-tekstit itse.

**How to apply:** Rakenna kieliversiot heti alussa mukaan (malli: Lotus-Demolition/i18n/ – translate.py kääntää valmiin FI-sivun). Liittyy project-lotus-demolition-sivustouudistus.

## feedback-shopify-kopio-ei-sellaisenaan

Messupuu 6.10.2026: Sulo pyysi "samanlainen kuin Saven", mutta suora Inova-kopio (jättilogo, versaalit, marquee, somepalkki, hotspotit, kuvapilleriteksti) ei sopinut puukaupan brändiin. Korjaus: "pidä rakenne ja pyöreys, poista turhuus, kliinimpi, enemmän Aureskoskea".

**Why:** Referenssisivusta Sulo hakee yleensä tunnelmaa ja rakennetta, ei sen koristeita; koristeet tekevät sivusta levottoman ja vieraan asiakkaan brändille.

**How to apply:** Kun Sulo viittaa toiseen sivuun mallina, ota rakenne (osiojärjestys, kortit, pyöristykset, karusellit) ja sovita asiakkaan brändiin; jätä teeman erikoisefektit pois tai kysy. Liittyy feedback-klinininen-ilme-vahan-pikkutekstia, project-messupuu-sivustouudistus.

## feedback-mainostavat-asiakkaat-urlit-ja-seuranta

Sulo 7.10.2026 (Kyrönlahden Porakaivo): sivuston vaihdossa pitää huomioida, mainostaako asiakas esim. Googlessa – linkkien pitää olla samat kuin nykyisellä sivulla, jotta mainokset eivät ohjaa 404:ään, ja seurannat (GTM) ja evästeet kuntoon.

**Why:** mainosliikenne ja konversioseuranta katkeavat julkaisuhetkellä huomaamatta, jos URL vaihtuu tai GTM/consent puuttuu.

**How to apply:** jokaisen uudistuksen alussa: (1) tarkista Google Ads Transparency (adstransparency.google.com, hae domainilla; RPC `/anji/_/rpc/SearchService/SearchCreatives` palauttaa mainoskuvat) ja Meta Ad Library; (2) kerää vanhat URL:t sitemapeista talteen (`src/vanhat-osoitteet.txt`) ja testaa jokainen uutta server.js:ää vasten (200 tai 301 → 200); (3) ohjaukset säilyttävät kyselyparametrit (gclid, utm); (4) grep vanhasta HTML:stä GTM-/G-/AW-tunnukset, consent default -skripti, evästebanneri (CookieYes/Cookiebot) ja google-site-verification ja siirrä ne vain tuotantobuildiin (ei demoon); (5) Google Fonts omalle palvelimelle; (6) README:hen julkaisun tarkistuslista (GTM-triggerit, banneriskannaus, Ads Final URL:t). Malli: Kyronlahden-Porakaivo/build.py (TRACKING_HEAD) ja server.js (notFound-prefiksiohjaukset). Liittyy project-sivustojen-julkaisuputki.
