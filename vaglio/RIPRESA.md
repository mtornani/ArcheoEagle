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

## Prossimi passi, in quest'ordine

### 1. Aggiornare e completare le colonne

```bash
git pull                              # comandi nuovi: moderno, kit, controlla, verifica; pacco --ordine
python -m unittest discover -s tests  # OK
python -m vaglio moderno              # uso del suolo di oggi (ESA WorldCover); scarica alcune centinaia di MB, una volta
python -m vaglio dossier
python -m vaglio verifica             # a posto
```

### 2. Pacco 3: la prima revisione sulla scansione completa (pre-registrata)

Scritto il 16 nov 2026, **prima** che il pacco esista. I 40 candidati rivisti finora vengono tutti dal
blocco «Centro» e, nella scansione completa, dei primi 100 per punteggio ne sono stati rivisti 3.
Quindi non sappiamo se il punteggio ordina bene fuori da quel blocco.

```bash
python -m vaglio pacco --top 40 --misto --controlli 20 --ordine punteggio --seme 3    # crea pacco-3
```

`--ordine punteggio` è obbligatorio: questo pacco prova il punteggio grezzo, non l'ordine appreso.
**Non lanciare `impara` prima di aver creato il pacco 3.**

Previsioni, valide per revisori che sui controlli del pacco risultano in grado di confermare:

- P1. Dei 20 col punteggio più alto ne reggono **almeno 10**. Se sono meno, l'affermazione «il
  punteggio mette in cima le costruzioni» vale solo per il blocco Centro, e va scritto.
- P2. Dei 20 presi a caso ne reggono **meno** che dei 20 più alti, e **non più di 8**.
- Se in questo pacco nessun revisore risulta in grado di confermare, il pacco non prova niente e
  si rifà con altri revisori. Non si abbassano le soglie.

### 3. Chi rivede, e come resta al buio

Ogni revisore riceve **solo** la cartella `vaglio_lavoro/review/pacco-3/` (immagini `r_NNNN.jpg`,
`RUBRICA.md`, `risposte_modello.json`) e restituisce un JSON. La cartella non contiene posizioni e
si può mandare a servizi esterni. La chiave (`review/keys/pacco-3.json`) non esce mai.

- Un assistente che ha accesso alla cartella di lavoro **non è un revisore valido**: può leggere la
  chiave. Il revisore è una sessione nuova, che vede solo la cartella del pacco.
- Servono revisori di tipo diverso: gli agenti Claude misurati finora confermano ma non scartano.
  Grok, ChatGPT, Gemini e soprattutto una persona esperta vanno misurati sugli stessi controlli.
- Per far rivedere il pacco agli agenti Claude: caricare lo zip della cartella del pacco nella
  sessione Claude Code, oppure aprire una sessione Claude Code nuova nella sola cartella del pacco
  e usare l'agente `vaglio-revisore`.

```bash
python -m vaglio esiti pacco-3 grok=grok.json chatgpt=gpt.json claude1=c1.json claude2=c2.json
```

### 4. Solo dopo: l'ordine appreso, e la sua prova

```bash
python -m vaglio impara        # impara cosa i revisori tengono; stampa quanti casi e quanto separa
python -m vaglio pacco --top 40 --misto --controlli 20 --ordine appreso --seme 4      # crea pacco-4
```

Sui primi 40 l'ordine appreso separa quasi perfettamente, ma è un numero gonfiato dal campione e,
applicato alla scansione completa, porta in cima i rilievi più alti, colline comprese. Regola scritta
prima: l'ordine appreso si adotta per la coda **solo se** nel pacco 4 i suoi 20 più alti reggono
almeno quanto i 20 più alti del pacco 3. Altrimenti resta il punteggio.

### 5. Materiali per esperti e altri

```bash
python -m vaglio kit                          # vaglio_lavoro/kit/: numeri, figure, pack cieco. Nessuna posizione
python -m vaglio controlla uscite/rapporto.md # ogni testo, prima che esca
```

Cosa scrivere, per chi, con quali parole: `vaglio/materiali/ISTRUZIONI.md`. I fatti: `vaglio/materiali/FATTI.md`.

## Regole che non si cambiano per far tornare i numeri

1. I criteri di test del rilevatore sono pre-registrati in `vaglio/vaglio/model.py`. Il test su Chactún è stato eseguito una volta ed è passato. Non si ritocca il modello e non si rifà il test senza committare prima la modifica.
2. Nessun esito si chiama "trovato", "scoperto", "nuovo", "confermato". Sullo Yucatán esiste un catalogo di 57.181 strutture (Britton 2026, non pubblico): un candidato lì si presume già noto.
3. I revisori vedono le immagini senza sapere quali sono i controlli. La chiave sta in `review/keys/` e non va mai data a un revisore.
4. Un revisore conferma solo se scarta i vuoti noti, scarta solo se trova le strutture note (`review.py`). Gli agenti misurati finora possono confermare ma non scartare.
5. Coordinate solo in `vaglio_lavoro/`. Da condividere ci sono solo `pack_cieco.json` e la cartella `vaglio_lavoro/kit/`.
6. Un testo destinato a uscire passa prima da `python -m vaglio controlla`.
