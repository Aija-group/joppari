# St1 Joppari (joppari.fi): ylläpito-ohje

**Tila: KAUPPA, asiakkaan tuotantosivusto.** Muutokset tehdään harkiten, ja jokainen julkaisu tallennetaan versioksi (git commit) ennen vientiä.

## Ennen kuin muutat mitään
1. Lue projektin muistitiedosto `~/.claude/projects/-Users-sulomaki-Library-Mobile-Documents-com-apple-CloudDocs-Sulon-setit/memory/project-joppari-sivustouudistus.md`: asiakkaan linjaukset, päätökset ja mitä on kesken.
2. Tausta ja aiemmat muutoskierrokset löytyvät keskusteluista (Obsidian, `~/Desktop/Postly/Postly/`):
   - `Postly/Claude-keskustelut/Claude Chat 2026-09-22 – Joppari (5932346a).md`
   - `Postly/Claude-keskustelut/Claude Chat 2026-09-28 – Joppari (1dffeeb9).md`
3. Noudata Sulon yleisiä linjauksia (muistin indeksi, osio "Toimintaohjeet ja palaute").

## Rakentaminen
- Lähde: `content.py` (tekstit) + `build.py` (ulkoasu) + Node-palvelin `server.js`. Aja `python3 build.py`, tulos `site/`.
- Tarkemmin README.md (alla).

## Julkaisu
- Julkaisutapa on yhteinen kaikille asiakassivustoille: muistitiedosto `project-sivustojen-julkaisuputki.md`. Siirtymässä NordicHostin MCP:hen, jolloin GitHub jää välistä pois.
- GitHub-repo: git@github.com-aijagroup:Aija-group/joppari.git
- Ennen julkaisua: `git add -A && git commit -m "<mitä muuttui>"`. Vanhan version palautus: `git log`, sitten `git checkout <commit> -- .`

## Versionhallinta
Paikallinen git säilyttää versiohistorian. `site/`, zipit ja `_materiaali/` eivät ole gitissä: `site/` generoidaan, muut ovat tallessa iCloudissa.

@README.md
