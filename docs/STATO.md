# Stato — 14 settembre 2026

**Giornata di consolidamento, non di espansione.** Zero piste nuove. Suite **117/117**.
Da oggi il punto d'ingresso è `docs/README.md`, non questo file.

## Il controllo positivo passa — era un errore di scala

`CALIBRAZIONE.md` diceva: otto rilevatori falliti, bersaglio invisibile alle statistiche d'insieme. **Sbagliato.** `run_positive_control` girava a 30 m nativi, e la Bama Ridge è un gradino di ~8 m su ~1 km.

| scala | Bama | controllo |
|---|---|---|
| 90 m | +1,80 | −0,82 |
| **120 m** | **+4,42** | −0,71 |
| 150 m | +0,49 | −0,63 |

Picco unimodale con media d'area; col sottocampionamento era una lama isolata fra due valli, cioè aliasing. Aggiunte `coarsen()` e `multiscale_step_score()` con flag `isolated_spike`. **Verdetto: passato.**

Spiega l'hillshade che trovava il cordone a occhio: guardare un'immagine la rimpicciolisce — l'occhio faceva la media che il codice non faceva.

## Casella §9 Mega-Chad chiusa — tre difetti che si coprivano a vicenda

1. `shoreline_from_dem` ordinava i punti **per angolo attorno al centroide**: non un tracciatore di contorni, un disegno. → marching squares.
2. 156 tile richiesti, tetto 12, presi in ordine di griglia → tutti nell'angolo sud-ovest. → ordinati per vicinanza alla sponda attesa.
3. Un'isolinea non è una sponda: 1136 polilinee a 320 m. → filtro a gradino col rilevatore validato.

**Risultato: 1 tile su 12 ha un gradino a 320 m. `vs_schematic_km` mediana 82,8 km.** E il tile della Bama Ridge è **23° su 156** per vicinanza al tracciato schematico: *il solo posto dove sappiamo che c'è una sponda non è dove il disegno dice di cercare.*

Ipotesi registrata e **non testata**: un livello unico per 500 km di sponda può essere il modello sbagliato — nel Great Basin l'isostasia deforma la stessa riva fino a 71 m.

## Audit dei parametri — per metodo, non per fortuna

Due bug della stessa specie trovati per caso in quattro giorni. `AUDIT-PARAMETRI.md` è la tabella: metrica sferica, scala d'analisi, soglie adimensionali, modulo per modulo. Ha trovato subito la dipendenza dalla scala non dichiarata in `basin.py` — non corretta nel codice ma **dichiarata**, perché la conclusione che ne dipende è verificata ai due estremi (Qattara 27 m e 240 m → 0; Sognefjord 118 m → 0,356).

**Regola nuova:** un modulo che tocca un DEM dichiara in testata se converte i pixel in metri, a che scala analizza, se le soglie sono adimensionali.

## Pista C parcheggiata, con ragione scritta

Il suo unico kill-shot — deposito di run-up sopra il piano d'acqua — **non esiste nei bacini chiusi**: riflusso ed erosione lo rimuovono entro decenni, e in letteratura non c'è un solo caso endoreico 15–5 ka. Il sostituto (torbidite di fondo) è stratigrafia da carota: esce dalla capacità "da casa". Riapre solo con accesso a dati di carotaggio.

## Round Gemini valutato

2 affermazioni su 8 non hanno retto. La Bama a 329 m è **contraddetta** dalla mia misura (320 resta). Accettata invece la correzione su GeoB7920-2: la granulometria **è** pubblicata, la mia dichiarazione di impossibilità era sbagliata. Da usare come indice bibliografico, mai come fonte.

---

# Stato — 13 settembre 2026

Tre giorni dopo la consegna. **Una pista nuova aperta (C), una tesi grossa valutata e messa nel ledger (Younger Dryas), due bug miei trovati e corretti.** Nessuna scoperta. Suite **111/111**.

## Pista C — confinamento (APERTA, come strumento)

Innesco: Dickson Fjord, Groenlandia, 16 set 2023. 25 milioni di m3 di roccia e ghiaccio, run-up 200 m, e poi l'acqua chiusa fra due pareti che oscilla ogni ~92 s **per nove giorni** (Svennevig et al., Science 2024).

Il confronto che vale tutto il resto:

| | volume | esito |
|---|---|---|
| Sahara Slide | ~600.000 milioni di m3 | **non** tsunamigenico |
| Dickson Fjord | ~25 milioni di m3 (**24.000x meno**) | run-up 200 m |

`collapse_source_potential()` diceva gia' pendenza-non-volume. Dickson lo conferma. La variabile che mancava e' **dove finisce l'energia**: su pendio aperto l'onda irradia, in un catino torna.

Scritto `backend/core/marine/seiche.py` — Merian, Green, confinamento, `displacement_hazard` (il volume **non** e' nella firma, c'e' un test che lo verifica).

**PRIMO CONTROLLO POSITIVO DEL PROGETTO CHE PASSA: 86,2 s previsti vs 92 s osservati, scarto 6%.** Non sono diventato bravo: il bersaglio qui e' un **numero** (un periodo), la Bama Ridge era una **forma dentro una scena**. Le statistiche d'insieme sanno fare la prima cosa, non la seconda. E' la diagnosi piu' utile uscita da `CALIBRAZIONE.md`.

**Limite definitivo:** il segnale sismico di una seiche antica non e' debole, e' **assente** — esiste solo grazie alla rete broadband post-1990. L'unico test falsificabile e' il **deposito di run-up sopra il piano d'acqua**.

Dettaglio: `docs/PISTA-C-confinamento.md`.

## Screening bacini — previsione registrata prima, e sbagliata al primo giro

Previsione committata **prima** di correre (`8e173a6`): no su tutta la linea. Primo giro: hazard 0,9–1,0 su tutti e dieci. Non una scoperta — un **metro rotto**, che era la seconda possibilita' scritta nella previsione stessa.

**Due bug, uno vecchio e mio.** `collapse_source_potential` usava `np.gradient` grezzo = metri per **indice di pixel**, confrontato con una soglia adimensionale: su DEM decimato tornava ~1,0 ovunque. `control.py` aveva la correzione dal 9 set, `basin.py` no — **due moduli miei con due unita' diverse per quattro giorni.** E `filled - dem > 1 m` prendeva fino a 1674 componenti sparse per tile, nessuna a contatto col bordo: `enclosure` 1,0 sempre. Misuravo la granulosita' del DEM.

Corretto (`px_m`/`py_m`, `largest_depression()`), 6 test di regressione. Secondo giro, con controllo positivo:

| | pixel | rilievo | orlo ripido |
|---|---|---|---|
| **Sognefjord (controllo +)** | 118 m | 1913 m | **0,356** |
| Hoggar (montagne vere) | 113 m | 1955 m | 0,0 |
| Qattara, **27 m/pixel** | 27 m | 73 m | 0,0 |
| tutti i corridoi sahariani | ~115 m | — | **0,0** |

**Il Sahara ha montagne. Non ha catini a pareti ripide.** Qattara a piena risoluzione da' zero, quindi non e' la decimazione. Nessun bacino sahariano ha la geometria di Dickson.

Dettaglio: `docs/SCREENING-BACINI.md`.

## Gravità — verificata, non scaricata, e la scelta e' motivata

Grado massimo pubblico (ICGEM, verificato 13/9): **2190 -> 9,1 km**. Serve il doppio per vedere un oggetto. Insediamento 0,1 km e nicchia di frana 2 km: **invisibili**. Bacino sedimentario 20 km: visibile.

**GGMplus da' 200 m ma le lunghezze corte sono modellate in avanti dalla topografia.** Usarlo per trovare massa sepolta e' **circolare** — stesso peccato del DEM sintetico vietato da §0, con una citazione accademica addosso. GRACE misura la derivata nel tempo e parte dal 2002.

Uso legittimo: **pesare il riempimento di un bacino** gia' selezionato (informazione che il DEM non ha), correggere la profondita' antica in Merian, kill-shot su strutture >=18 km. **Mai come ricerca**: sarebbe anomalia-prima. Non scaricata perche' lo screening ha azzerato i candidati.

Dettaglio: `docs/GRAVITA.md`.

## Younger Dryas — tesi valutata, anello del diluvio ROTTO

Trattata come CLAUDE.md §2.3 impone: lente non oracolo, con fonte, puo' prendere un `−`. Catena spezzata in tre anelli.

- **Anello 1, impatto ~12,9 ka: APERTO.** L'anomalia di **platino** GISP2 (Petaev 2013; Moore 2017) e' misura vera e replicata, prende `+`. Nanodiamanti e sferule non hanno superato la replica. **Hiawatha, l'unico cratere artico grande, ridatato nel 2022 a ~58 Ma**: Paleocene. Non nostro da chiudere.
- **Anello 2, impulso d'acqua: `−`, MISURATO.** Younger Dryas intero = 7,5 m in 1200 anni = **6,2 mm/anno**, il tratto **piu' lento** della deglaciazione fra 18 e 7 ka (e' un raffreddamento: il ghiaccio riavanza). MWP1A = 16 m in 340 anni = **47 mm/anno**, 7,5x piu' rapido, e comincia **1750 anni PRIMA**. Un effetto non precede la causa di diciassette secoli. 4 test lo bloccano.
- **Anello 3, localizza: N/A.** Un evento emisferico non ha indirizzo. Il platino e' un **cronometro, non una bussola**.

Dettaglio: `docs/YOUNGER-DRYAS.md`, obiezione MWP1B inclusa.

## Kill-shot aperti (chi li chiude, chiude qualcosa)

1. **YD anello 2:** un record di livello del mare con salto metrico rapido **dentro** 12,9–12,5 ka. Se esiste, il mio `−` cade.
2. **Pista C:** un deposito di run-up sopra il piano d'acqua in un bacino confinato, 15–5 ka.
3. **Pista A:** una seconda carota con carbone **e** cere fogliari appaiati (fuori portata da casa, materiale a Brema).

## Cosa NON fare

- Non riaprire A o B raccontandole meglio.
- **Non riformulare il YD spostando la finestra finche' un diluvio ci cade dentro** — e' l'errore gia' commesso col carbone.
- Non costruire il nono rilevatore di sponda prima che il controllo positivo della Bama Ridge passi.
- Non usare la gravita' come ricerca, e non usare GGMplus per massa sepolta.

---

# Stato — 10 settembre 2026

Sessione lunga. Due piste aperte, **due piste chiuse**. Nessuna scoperta. Il tool è più onesto di ieri.
Per chi arriva dopo (Grok, Claude, chiunque): **non riaprire §A e §B senza un dato nuovo.** Sotto c'è cosa le ha uccise.

## Fatto (codice, testabile)

- `backend/core/hydro/measure.py` — Mega-Chad su **tutti** i tile 1° del bbox, non uno solo (era l'item 1 di §11 CLAUDE.md). Riporta `tiles_used / tiles_failed / tiles_total / truncated`. Un tile è un angolo del lago, non la sponda.
- `backend/api/routes/analysis.py` — **bug di produzione risolto**: `load_network` non era importato → 500 su ogni `GET /api/v1/analysis/network`. Trovato solo *avviando l'app*, non dai test. Aggiunto `backend/tests/test_analysis_routes.py` come regressione.
- `backend/core/hydro/control.py` — **banco di calibrazione** con controllo positivo (Bama Ridge, la sponda del Mega-Chad datata OSL) e un tile di controllo negativo. Metrica sferica corretta (larghezza pixel ∝ cos φ su EPSG:4326). Effect size su MAD, non percentili: *un percentile mette sempre qualcosa al primo posto, anche nel rumore puro.*
- `backend/core/marine/shelf.py` — piattaforma annegata. Guida col vincolo cronologico, non col punteggio: −30/−130 m = 20–7 ka (niente monumenti); 0/−20 m = <7 ka (paesi veri). Sovrapposizione solo per subsidenza tettonica.
- `backend/core/marine/basin.py` — priority-flood, pour point, spillway. Nato già corretto dai tre meccanismi di catastrofe (riempimento soglia / dislocamento di massa / rilascio a valle). Misura ripidezza del bordo, non volume.
- Suite: **79/79 verde**, tutta offline.

## Il controllo positivo FALLISCE — ed è il risultato

Otto rilevatori automatici, otto fallimenti su un bersaglio **noto e nel riquadro**. Diagnosi in `docs/CALIBRAZIONE.md`: la Bama Ridge è ~1% di migliaia di frammenti di isolinea; nessuna statistica d'insieme la vede. L'**hillshade guardato a occhio** la trova in un secondo (`docs/calibrazione-bama-ridge.png`).

**Conseguenza operativa: nessuna schermata può dire "sponda individuata".** Finché il controllo positivo non passa, un punteggio alto è rumore che non sappiamo distinguere.

## Pista A — carbone (CHIUSA). `docs/PISTA-A-carbone.md`

Carbone per unità di biomassa (cere fogliari) 3× più alto a 5.5–8.8 ka, p<0.001, sopravvissuto a cinque spiegazioni alternative. Sembrava una pista.
**Uccisa da Sr-Nd su ODP 658C** (PANGAEA.785476), carotato ~300 m da GeoB7920-2: ⁸⁷Sr/⁸⁶Sr sale monotòno 0.714 → 0.722 **attraverso esattamente quella finestra**. Bacino sorgente diverso ⇒ il rapporto confronta materiale non confrontabile.
Ammissione mia, agli atti: la finestra 5.5–8.8 ka l'ho scelta *perché lì il rapporto era alto*. Quasi tautologico.

## Pista B — catastrofe (CHIUSA). `docs/PISTA-B-catastrofe.md`

Tre linee indipendenti: Sahara Slide (600 km³) giudicato non-tsunamigenico perché dolce e retrogressivo; Mauritania Slide Complex (10.5–10.9 cal ka BP, dentro finestra) anch'esso retrogressivo; nessun deposito transatlantico mai legato a frane delle Canarie. **L'assenza è informativa: mette un tetto alla taglia.**

## Sorgenti verificate dal vivo (no key)

Copernicus GLO-30 su S3 · GMRT GridServer (bbox→GeoTIFF) · ALOS PALSAR via DE Africa (af-south-1, anonimo) · PANGAEA (`pangaeapy`) · p3k14c · SESAR.
**IMLGS è morto** — dismesso il 5 maggio 2025. XRONOS raggiungibile, endpoint non identificato.

## Fuori portata da casa (non è pigrizia, è che il dato non esiste ancora)

- Granulometria su GeoB7920-2 stessa.
- Una seconda carota con carbone **e** cere appaiati.
Entrambe richiedono misure nuove su materiale in archivio a Brema.

## Cosa NON fare al prossimo giro

- Non riaprire A o B raccontandole meglio. Servono misure nuove.
- Non costruire il nono rilevatore prima che il controllo positivo passi.
- Non tradurre un punteggio in "trovato". Lo strumento che abbiamo non trova: **falsifica**.

---

# Stato — 9 settembre 2026

OB1 in manutenzione. ArcheoEagle attivo. Repo GitHub + path `D:\AI\ArcheoEagle`.

**Svolta GIS:** GeoLibre (`docs/GEOLIBRE.md`). Frontend Leaflet resta avviabile. Mappa da aprire: `data/sahara_paleodrainage.geolibre.json`.

---

# Stato — 16 agosto 2026

Freeze OB1 sollevato da Mirko per questa sessione. Continua da qui.

## Cosa è il prodotto ora

Motore forense: Atlantide-nel-Sahara da PC di casa. Non cerca anelli. Cammina paleofiumi. Platone è colonna `+ / − / N/A`. Pack cieco + SHA-256. Operatore ≠ peer.

## Come si avvia

```
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000

cd frontend
npm run dev
```

Apri http://localhost:5173/ — LAN: http://192.168.1.77:5173/

## Flusso

1. Fascicolo: *Come indaghi* → tap un corridoio (non disegnare).
2. Tappa: “in parole povere” → Platone → domande.
3. Confronta A|B|C.
4. Capire: perché questo fiume, cosa puoi/non puoi dire, lessico.
5. Pack cieco (niente pin). Disegno solo sotto *Restringi a mano — bias*.

## Verificato ieri

- 14 unit test (`backend`: paleorivers, ledger, blind).
- `POST /api/v1/analysis/walk` Tamanrasset → tappa A confluenza, ρ ~0.05, hash senza coord.
- TypeScript pulito. Vite + API su.

## Non fatto / prossimo

- Radar L-band (sotto sabbia) — Sahabi è il corridoio dove serve.
- Imagery Copernicus/DEM reali (ora mock se mancano le key).
- Terminale umano: non esiste. Non inventarlo. Pack cieco è pronto.
- Camminare Tamanrasset **e** Irharhar/Howar come controllo, non un solo mare.

## File nuovi chiave

- `backend/core/hydro/paleorivers.py`
- `backend/core/ledger/` (hypotheses, blind)
- `frontend/src/investigate.ts` (guide per corridoio)
- `frontend/src/components/ControlPanel.tsx` (fascicolo)
- `data/sahara_paleodrainage.geojson`
