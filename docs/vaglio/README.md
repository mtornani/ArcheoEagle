# Sotto la foresta — rapporto divulgativo di Vaglio

Sito statico, pensato per il telefono, in italiano e inglese. Unisce il racconto «Sotto la foresta», le figure kit dei 15 che reggono alla revisione, la mappa dei transetti, le schede dei 40 candidati già rivisti e il protocollo del test cieco pre-registrato.

Dopo il merge su `main` (GitHub Pages è già attivo sul ramo `main`, cartella `/docs`):

**https://mtornani.github.io/ArcheoEagle/vaglio/**

## Cosa c'è, e cosa no

- Testo da `vaglio/materiali/FATTI.md`, dalla pagina «Sotto la foresta» e da `pack_cieco.json`, con le frasi obbligatorie delle istruzioni (S1–S5). Qualifica: ricercatore indipendente, non archeologo.
- Figure dei 15 che reggono (kit, a colori, senza posizioni) e prova su 8 riquadri di Chactún.
- Schede dei 40 candidati rivisti (identificativo del pack, punteggio d'ordine, esito, voti). **Niente coordinate.**
- Mappa Leaflet dei transetti già descritti in `transects.json`, più Chactún (sito pubblicato, Wikidata). **I candidati non sono sulla mappa.**
- Impronta del pack cieco `84fd816a59a7ba02b8f11b6cea7dcb6d85442b49f1e10896027d563c15158520` e link al deposito sigillato (`vaglio/test_cieco/`, commit `525c212`, prova OpenTimestamps).
- Riquadri di controllo di Chactún già in `vaglio/vaglio/data/controls/`, colorati con viridis. Non sono le immagini dei candidati dello Yucatán.

Le posizioni dei candidati restano in `vaglio_lavoro/`, che non si pubblica, per non esporre i luoghi al saccheggio (`ISTRUZIONI.md` §2.4 e S4).

## Rigenerare le immagini di controllo

Dalla radice del repository, con numpy, matplotlib e Pillow:

```bash
python3 docs/vaglio/build_assets.py
```

Le figure dei 15 e le immagini della prova si copiano da `vaglio/materiali/uscite/` (già versionate): non vanno ricolorate né ritagliate.
