# Rapporto divulgativo di Vaglio

Sito statico, pensato per il telefono, con i fatti già pubblici nel repository.
Non è il rapporto scientifico per la revisione tra pari.

Dopo il merge su `main` e l'attivazione di GitHub Pages (ramo `main`, cartella `/docs`):

**https://mtornani.github.io/ArcheoEagle/vaglio/**

## Cosa c'è, e cosa no

- Testo da `vaglio/materiali/FATTI.md` e `pack_cieco.json`, con le frasi obbligatorie delle istruzioni.
- Schede dei 40 candidati rivisti (identificativo del pack, punteggio d'ordine, esito, voti, note). **Niente coordinate.**
- Mappa Leaflet dei transetti già descritti in `transects.json`, più Chactún (sito pubblicato, Wikidata). **I candidati non sono sulla mappa.**
- Riquadri di controllo di Chactún già in `vaglio/vaglio/data/controls/`, colorati con viridis (le originali sono in scala di grigi). Non sono le immagini dei candidati dello Yucatán.

Le posizioni dei candidati restano in `vaglio_lavoro/`, che non si pubblica, per non esporre i luoghi al saccheggio (`ISTRUZIONI.md` §2.4 e S4).

## Rigenerare le immagini

Dalla radice del repository, con numpy, matplotlib e Pillow:

```bash
python3 docs/vaglio/build_assets.py
```

## Attivare GitHub Pages

Nel repository: Settings → Pages → Build and deployment.

- Source: Deploy from a branch
- Branch: `main`
- Folder: `/docs`

Oppure, con i diritti di amministrazione:

```bash
gh api -X POST repos/mtornani/ArcheoEagle/pages \
  -f build_type=legacy \
  -F 'source[branch]=main' \
  -F 'source[path]=/docs'
```

È già presente `docs/.nojekyll` perché il sito è HTML statico.
