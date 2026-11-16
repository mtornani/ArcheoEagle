# Ripresa della scansione Vaglio — consegna fra assistenti

Stato al 16 nov 2026, 13:15 UTC. Scritto per chi riprende il lavoro (persona o code assistant).
Leggi prima `CLAUDE.md` §0 e §14 alla radice del repo: vincono su questa nota.

## Dove sta cosa

| Cosa | Dove |
|---|---|
| Codice | repo `mtornani/ArcheoEagle`, branch `claude/agent-fleet-supervisor-skqdwc`, cartella `vaglio/` |
| Modello addestrato | `vaglio/vaglio/data/structures.joblib` (nel repo) |
| Catalogo dei 456 transetti | `vaglio/vaglio/data/transects.json` (nel repo) |
| **Checkpoint della scansione** | archivio `vaglio_lavoro_essenziale.zip`, consegnato a parte. **Non è nel repo**: contiene coordinate |
| Immagini dei candidati (facoltative) | archivio `vaglio_lavoro_immagini.zip`, consegnato a parte |

Gli archivi hanno come radice la cartella `vaglio_lavoro/`. Vanno estratti **dentro `vaglio/`**,
così da ottenere (Windows):

```
D:\AI\ArcheoEagle\vaglio\vaglio_lavoro\scan\Centro_GLAS_l0s435.json   ... 51 file
D:\AI\ArcheoEagle\vaglio\vaglio_lavoro\review\...
D:\AI\ArcheoEagle\vaglio\vaglio_lavoro\chips\...     (solo dall'archivio immagini)
D:\AI\ArcheoEagle\vaglio\vaglio_lavoro\context\...   (solo dall'archivio immagini)
```

`vaglio_lavoro/` è in `.gitignore`: **non committarla, non pubblicarla.**

## A che punto è

- 51 transetti su 456 scansionati (160 km² su 1.273), 1.548 complessi candidati.
- Restano 405 transetti (1.112 km²). Ognuno: 35–85 MB da scaricare, 1–2 minuti di CPU.
- I 51 fatti sono tutti `Centro_GLAS_*` più 11 `Centro_NFI_*` (elenco esatto: i nomi dei file in `scan/`).
- Tutti i 51 sono stati fatti con lo stesso codice (commit `9c34a0f` in poi: ortogonalità dei bordi, bordo del dato a 15 m). Il codice di scansione non è cambiato dopo: si può proseguire senza rifare niente.
- Revisione: 40 candidati rivisti nel `pacco-2` (3 revisori agenti), 15 reggono, 25 incerti. Il `pacco-1` è in `review/annullati/`: annullato per un difetto nei controlli, non va riusato.

## Come riprendere

```bash
cd D:\AI\ArcheoEagle\vaglio            # i comandi vanno lanciati da qui
pip install -r requirements.txt
python -m unittest discover -s tests   # deve dire OK
python -m vaglio catalogo              # deve dire: scansionati qui: 51
```

Se dice 0, l'archivio è estratto nel posto sbagliato (vedi sopra) oppure passa `--lavoro <percorso>`.

Scansione, un processo:

```bash
python -m vaglio scansiona --tutti
```

In parallelo, un terminale per parte (4 core, circa 3–4 ore in tutto):

```bash
python -m vaglio scansiona --tutti --parte 1/4
python -m vaglio scansiona --tutti --parte 2/4
python -m vaglio scansiona --tutti --parte 3/4
python -m vaglio scansiona --tutti --parte 4/4
```

Su Linux/macOS conviene `OMP_NUM_THREADS=1` per ogni processo; su PowerShell `$env:OMP_NUM_THREADS=1`.

Come funziona la ripresa: un transetto è fatto se esiste `scan/<id>.json`, che si scrive solo a
transetto finito. Chi viene interrotto riparte da capo su quel transetto e salta tutti gli altri
già fatti. Le parti `--parte K/N` si possono cambiare fra un'esecuzione e l'altra. Ogni DTM scaricato
viene cancellato dopo la scansione, salvo `--tieni-dtm`. Un transetto che fallisce (rete) viene
scritto `FALLITO` nel log e salvato al giro dopo.

## Dopo la scansione

```bash
python -m vaglio pacco --top 40 --misto --controlli 20     # crea pacco-3 (40 candidati + 20 controlli)
# far rivedere la cartella vaglio_lavoro/review/pacco-3 a 2-3 revisori diversi
# (agente Claude Code `vaglio-revisore`, Grok, ChatGPT, persone): ognuno legge RUBRICA.md e scrive un JSON
python -m vaglio esiti pacco-3 grok=grok.json chatgpt=gpt.json claude=claude.json
python -m vaglio impara        # quando ci sono >= 8 candidati tenuti e >= 8 scartati
python -m vaglio dossier       # dossier.html (mappa, schede), candidati.csv, candidati.geojson, pack_cieco.json
```

## Regole che non si cambiano per far tornare i numeri

1. I criteri di test del rilevatore sono pre-registrati in `vaglio/vaglio/model.py`. Il test su Chactún è stato eseguito una volta ed è passato. Non si ritocca il modello e non si rifà il test senza committare prima la modifica.
2. Nessun esito si chiama "trovato", "scoperto", "nuovo", "confermato". Sullo Yucatán esiste un catalogo di 57.181 strutture (Britton 2026, non pubblico): un candidato lì si presume già noto.
3. I revisori vedono le immagini senza sapere quali sono i controlli. La chiave sta in `review/keys/` e non va mai data a un revisore.
4. Un revisore conferma solo se scarta i vuoti noti, scarta solo se trova le strutture note (`review.py`). Gli agenti misurati finora possono confermare ma non scartare.
5. Coordinate solo in `vaglio_lavoro/`. Da condividere c'è solo `pack_cieco.json`.
