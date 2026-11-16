# Ripresa della scansione Vaglio — consegna fra assistenti

Aggiornata il 16 nov 2026, 17:40 UTC. Scritto per chi riprende il lavoro (persona o code assistant).
Leggi prima `CLAUDE.md` §0 e §14 alla radice del repo: vincono su questa nota.

## Dove sta cosa

| Cosa | Dove |
|---|---|
| Codice | repo `mtornani/ArcheoEagle`, branch `claude/agent-fleet-supervisor-skqdwc`, cartella `vaglio/` |
| Modello addestrato | `vaglio/vaglio/data/structures.joblib` (nel repo) |
| Catalogo dei 456 transetti | `vaglio/vaglio/data/transects.json` (nel repo) |
| **Checkpoint finale** | archivio `vaglio_checkpoint_456_20261116_182656.zip`, consegnato a parte. **Non è nel repo**: contiene coordinate |
| Immagini dei candidati (facoltative) | archivio `vaglio_lavoro_immagini.zip`, consegnato a parte |

Il checkpoint ha come radice la cartella `vaglio_lavoro/`. Va estratto **dentro `vaglio/`**,
così da ottenere (Windows):

```
D:\AI\ArcheoEagle\vaglio\vaglio_lavoro\scan\Centro_GLAS_l0s435.json   ... 456 file
D:\AI\ArcheoEagle\vaglio\vaglio_lavoro\review\...
D:\AI\ArcheoEagle\vaglio\vaglio_lavoro\chips\...     (solo dall'archivio immagini)
D:\AI\ArcheoEagle\vaglio\vaglio_lavoro\context\...   (solo dall'archivio immagini)
```

`vaglio_lavoro/` è in `.gitignore`: **non committarla, non pubblicarla.**

## A che punto è

- Scansione completa: 456/456 transetti (1.272,7 km²), 11.916 complessi candidati.
- Revisione: 40 candidati del `pacco-2` (3 revisori agenti), 15 reggono e 25 restano incerti; 11.876 sono da rivedere e 0 sono scartati. Il `pacco-1` è in `review/annullati/`: annullato per un difetto nei controlli, non va riusato.
- Il pack cieco senza coordinate è versionato in `vaglio/pack_cieco.json`. I file in `vaglio_lavoro/`, incluso il dossier, contengono coordinate e non vanno committati.

## Come riprendere

```bash
cd D:\AI\ArcheoEagle\vaglio            # i comandi vanno lanciati da qui
pip install -r requirements.txt
python -m unittest discover -s tests   # deve dire OK
python -m vaglio catalogo              # deve dire: scansionati qui: 456
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

## Prossimo passo: revisione

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
