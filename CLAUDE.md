# St1 Joppari (joppari.fi): ylläpito-ohje

**Tila: KAUPPA, asiakkaan tuotantosivusto.** Tämä kansio on itsenäinen: kaikki ylläpitoon tarvittava on tässä, eikä se riipu Äijä Groupin koneesta tai tileistä.

## Lue ennen muutoksia
1. `PROJEKTI.md`: asiakkaan linjaukset, päätökset ja historia.
2. `LINJAUKSET.md`: Äijä Groupin yleiset tyylisäännöt (esim. ei ajatusviivoja, kliini ilme).
3. `README.md` (alla): rakenne ja tekninen toteutus.

## Rakentaminen
- Lähde: `content.py` (tekstit) + `build.py` (ulkoasu) + Node-palvelin `server.js`. Aja `python3 build.py` (vaatii Pillow), tulos `site/`.
- `site/` generoidaan aina lähteestä, sitä ei muokata käsin.

## Versionhallinta ja julkaisu
- Jokainen muutos tallennetaan versioksi ennen julkaisua: `git add -A && git commit -m "<mitä muuttui>"`. Vanhan version palautus: `git log`, sitten `git checkout <commit> -- .`
- GitHub-repo: git@github.com-aijagroup:Aija-group/joppari.git
- `site/`, zipit ja `_materiaali/` eivät ole gitissä.

## Äijä Groupin oma työympäristö (vain Sulon koneella)
- Muistitiedosto: `~/.claude/projects/-Users-sulomaki-Library-Mobile-Documents-com-apple-CloudDocs-Sulon-setit/memory/project-joppari-sivustouudistus.md`
- Julkaisuputki: muistitiedosto `project-sivustojen-julkaisuputki.md` (siirtymässä NordicHostin MCP:hen).
- Keskustelut (Obsidian `~/Desktop/Postly/Postly/`):
   - `Postly/Claude-keskustelut/Claude Chat 2026-09-22 – Joppari (5932346a).md`
   - `Postly/Claude-keskustelut/Claude Chat 2026-09-28 – Joppari (1dffeeb9).md`

@README.md
