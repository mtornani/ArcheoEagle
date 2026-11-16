# ArcheoEagle — Spec

Questo file è la **spec di prodotto**. Il codice è derivato. Se codice e spec divergono, vince la spec finché non la si cambia. Ogni requisito qui ha criterio di accettazione. Non implementare ciò che non è in spec.

Repo: https://github.com/mtornani/ArcheoEagle  
Path: `D:\AI\ArcheoEagle`  
GIS host: [GeoLibre](https://github.com/opengeos/GeoLibre) — dettaglio in `docs/GEOLIBRE.md`

---

## 0. Standing orders — Claude Code, Grok, qualunque agente

Non sei l’estensione di Mirko. Non lucidare il mito. Risolvi il problema: **prove da casa che sopravvivono a uno scettico**.

1. **Misura ≠ disegno.** Un LineString da paper è ipotesi. Un contour DEM / un canale radar è misura. Se non hai misura, `grade=schematic` e lo dici. Non coprire il buco.
2. **Vietato:** DEM sintetico, valle piantata, bottone “Atlantide found”, camminare Richat come sito, crop-mark/NDVI sul walk di default, U-Net “detect Atlantis”, forkare GeoLibre, pubblicare pin.
3. **Richat = trappola.** `POST /walk` `richat` → `method=trap`, ranking vuoto. Non “fixarlo” in corridoio.
4. **SRTM non vede i fiumi sepolti.** Tamanrasset/Sahabi sotto sabbia = L-band o ammissione. Non inventare alvei col noise.
5. **Prossimo colpo vero:** più tile DEM sulla sponda Mega-Chad 320 m, oppure un layer radar L-band su Sahabi. Non un secondo GIS. Non un altro pannello Leaflet.
6. Ogni PR cita un checkbox di §9. Test: `cd backend && python -m unittest discover -s tests -v` deve restare verde.
7. `archaeo-sentinel-prompt.md` è **archivio**. Non è la spec. Questa è la spec.

Se un task contraddice questo blocco, vince questo blocco.

---

## 1. Job (una cosa sola)

Tool **mobile-first**, usabile da **casa / remoto**, su **qualunque dispositivo con browser o app GeoLibre**.

Fa **una** cosa: cercare **prove oggettive** (misurabili, citabili, falsificabili da casa) che possano **restringere dove cercare** il referente reale dietro il racconto di Atlantide.

Non “trova Atlantide”. Non certifica una scoperta. Produce un **fascicolo forense** e un **pack cieco**.

---

## 2. Tesi di lavoro (ipotesi, mai risultato)

Etichetta obbligatoria in UI e report: **ipotesi di lavoro**, non conclusione.

1. Il referente geografico più onesto da testare **da casa** è il **Sahara** (paleoidrologia del periodo umido africano, ~14.500–5.500 anni fa), non l’isola-anello in mezzo all’Atlantico.
2. La narrativa popolare (anelli concentrici, isola atlantica, città da film) **non è la cosa**. È un caso di **pareidolia concettuale** + **telefono senza fili**: un concetto iniziale (una terra sull’acqua, un collasso, una memoria trasmessa) è stato ingigantito e distorto a ogni passaggio (preti egizi → Solone → Platone → medioevo → TV → YouTube/Richat).
3. Lettura allineata a **Randall Carlson** (geomorfologia, acqua, catastrofe, forma **dopo** la misura) e **Graham Hancock** (civiltà/memoria pre-racconto, non il cartone platonico letterale). Carlson/Hancock sono **lenti**, non oracoli. Ogni loro claim entra nel ledger come tesi, con fonte, e può prendere `−`.
4. Platone è **testo da testare**, non mappa da ricalcare. Assenza di anelli **non contraddice**. Anelli cercati a priori = pareidolia.

Se un giorno i dati uccidono la tesi Sahara, la tesi muore. Il tool resta.

---

## 2b. Fisica — misura vs disegno (non negoziabile)

Camminare un LineString copiato da un paper **non è una prova**. È un’ipotesi disegnata. Il vecchio DEM sintetico con valle piantata “dove stanno i siti” è frode. Vietato.

| Cosa | Da casa, oggi | Non fare |
|---|---|---|
| Mega-Chad ~320 m | Isolinea sul DEM Copernicus GLO-30 (AWS, no key). Sponda = misura. `vs_schematic_km` = quanto il disegno sbaglia. | Trattare l’anello schematico come costa vera |
| Tamanrasset / Sahabi sepolti | SRTM vede la pelle del deserto, non l’AHP sotto sabbia. Serve L-band. Assente → `grade=schematic` + warning | Inventare canali col noise |
| Crop mark / NDVI blob | Prior da archeologia inglese su campo. Nel Sahara è un altro stampo. Default **off** | `detect_anomalies` sul walk |
| Richat | Trappola. Struttura circolare reale. Il telefono senza fili ci porta. Il tool **rifiuta** la classifica | Camminarla come corridoio |

Prima misura vera: **sponda Mega-Chad a 320 m su un tile 1°**. Un segmento misurato batte un continente disegnato.

---

## 3. Diagnosi del mito (spec intellettuale)

| Strato | Cos’è | Come il tool lo tratta |
|---|---|---|
| Referente possibile | Terra sull’acqua in un Sahara verde; nodi idrici; sponde; alvei sepolti | Oggetto della caccia. Cammina la rete. Misura. |
| Memoria | Racconto passato di bocca in bocca, poi scritto | Colonna Platone `+ / − / N/A`. Deriva linguistica ≠ prova. |
| Cartone | Anelli, oricalco, palazzo, “Atlantide found” | **Non è un target.** Non è un prior. Non è un bottone. |
| Pareidolia visiva | Il cervello 2026 vede cerchi nella Richat / nel deserto | Forma solo **dopo** idro. Se la cerchi, stai usando lo strumento contro di te. |
| Pareidolia concettuale | Prendere il cartone (anelli + Atlantico + tech) e cercarlo nel mondo | Vietato come algoritmo. La narrativa è sospetto, non guida. |
| Telefono senza fili | Ogni copia del racconto aggiunge scala, metallo, geometria, morale | Ogni clause platonica si testa da sola. N/A è legale. Non forzare + o −. |

Frase di metodo: **misura dopo la forma. Acqua prima del mito. Testo come colonna, non come stampo.**

---

## 4. Cosa il prodotto fa

Da remoto, su telefono o desktop, l’operatore:

1. Sceglie un **corridoio** sahariano (Tamanrasset, Irharhar, Sahabi, Mega-Chad, Tilemsi, Azawagh, Wadi Howar) — non “disegna Atlantide”.
2. Cammina la **rete idrica fossile** → **nodi** (confluenza, sponda, alveo, testa/foce). Nessun prior di forma urbana.
3. Accumula **prove oggettive** su ogni nodo: idro, (se ci sono) RS/DEM, fonte, grado (schematico vs rilievo).
4. Compila un **ledger** a due facce: pro, contro, residuo ρ, kill-shot remoto, test platonici `+ / − / N/A`.
5. Confronta A | B | C con **le stesse colonne**.
6. Esporta:
   - **Dossier locale** — coordinate. Resta sul device. Non si pubblica.
   - **Pack cieco** — etichette A/B/C + rubrica + **SHA-256 + timestamp**. Niente pin. Priorità senza dare la preda.

Due umani, stessi layer, stessa classifica. Mai 100%. Operatore ≠ peer.

---

## 5. Prove oggettive (cosa conta)

Una riga è “prova” solo se ha **tutti** questi campi:

- **claim** — frase misurabile (“confluenza su tracciato Tamanrasset schematico”)
- **tipo** — `hydro` | `rs` | `terrain` | `radar` | `literature` | `plato_text`
- **fonte** — paper / dataset / strumento (es. Skonieczny 2015; SIR-A; Sentinel-2)
- **grado** — `schematic` | `survey` | `mock`
- **cosa puoi dire** / **cosa non puoi dire**
- **kill-shot** — cosa, da casa, chiuderebbe il claim. Se manca: resta **aperto**. Aperto ≠ trovato.

### Ammesse

- Paleodrenaggi e paleolaghi da **letteratura citata** (grado `schematic` finché non c’è DEM/radar)
- Nodi derivati dal walk (confluenza > sponda > alveo)
- NDVI / BSI / DEM / slope **come colonna**, non come bersaglio “sito”
- Radar L-band / canali sepolti (Sahabi) quando il layer esiste; senno dichiarato assente
- Testo platonico spezzato in clause, ciascuna `+ / − / N/A`

### Vietate come prova

- “Sembra un anello”
- “Hancock/Carlson dicono X” senza dato indipendente
- Un vertice del geojson schematico trattato come sito
- Mock Copernicus venduto come Sentinel reale
- Classifica o ρ basso tradotti in “è Atlantide”
- Coordinate nel pack pubblico

I tracciati in `data/sahara_paleodrainage.geojson` sono **schematici da letteratura**. Un vertice **non è un sito**.

---

## 6. Metodo forense (invarianti)

Queste regole non si “semplificano” in un refactor.

| Invariante | Deve essere vero |
|---|---|
| Acqua prima | Il walk parte dalla rete idrica, non da una forma |
| Forma dopo | Circolarità / anelli solo se misurati. Assenza = `N/A`, mai `−` |
| Platone colonna | Ogni clause indipendente. N/A legale. Non è blueprint |
| Residuo ρ | Disaccordo tra colonne. Basso = nodi coerenti, **non** “più Atlantide” |
| Kill-shot | Se da casa non chiudi, resta aperto |
| Controllo | Tamanrasset **e** Irharhar/Howar. Un solo mare = bias |
| Cieco | Pack senza lon/lat/river_name. Hash = priorità |
| Mock dichiarato | Senza key Copernicus/DEM, layer `mock` visibile in UI |
| Operatore ≠ peer | Chi cammina non è chi valuta il pack cieco |

Corridoi e lessico: `frontend/src/investigate.ts`. Ledger: `backend/core/ledger/`. Blind: `backend/core/ledger/blind.py`. Walk: `backend/core/hydro/paleorivers.py`.

---

## 7. UX — mobile first, ogni dispositivo

**Primario = telefono.** Desktop è lo stesso prodotto, layout più largo. Non due app.

### Layout

- Viewport minimo **360×640**. Usabile con un pollice.
- Target touch **≥ 44×44 px**. Niente azione solo-hover.
- Un compito per schermata: fascicolo → corridoio → tappa → confronto A|B|C → export.
- Pannello a **foglio dal basso** su stretto; su largo può diventare colonna.
- Mappa occupa lo schermo; i controlli non coprono il nodo attivo.
- Testo “in parole povere” prima dei numeri. ρ e score visibili, non primi.
- Ipotesi di lavoro visibile in testata (Sahara / non-cartone). Mai un badge “Atlantide”.

### Flusso (stesso su telefono e PC)

1. Apri → capisci **cosa stai cercando** (prove, non la città del cartone).
2. Tap un corridoio (bottoni). Disegno AOI è **opzionale** e sotto “restringi a mano — bias”.
3. Classifica nodi → tappa A in evidenza, brief del corridoio.
4. Confronta A|B|C. Stesse colonne.
5. Export: dossier locale (device) / pack cieco (condivisibile).

### Dispositivi

| Superficie | Ruolo |
|---|---|
| Telefono browser / PWA | Uso quotidiano da casa |
| GeoLibre iOS/Android | Mappa nativa + GPS campo |
| Desktop / tablet | Stesso flusso, più mappa |
| Claude Code mobile | Cambia spec e codice; non sostituisce l’UI |

GIS: **GeoLibre**, non un secondo Leaflet. Frontend Leaflet = legacy avviabile finché il plugin GeoLibre copre il flusso sopra.

---

## 8. Architettura (confini, non ricette)

```
dispositivo (telefono/desktop)
    ├── GeoLibre          mappa, layer, hydrology/RS/terrain WASM, GPS
    └── ArcheoEagle       dominio forense
            ├── walk nodi
            ├── ledger + Platone
            ├── dossier locale / pack cieco
            └── hypotesi Sahara etichettata
```

- Non forkare GeoLibre. Plugin `archeoeagle` o progetto `.geolibre.json`.
- Backend FastAPI resta per walk/ledger/blind. Non si butta.
- Stack €0. Niente infra a pagamento.
- Dati sul device. Niente upload di pin.

Mappa oggi: `data/sahara_paleodrainage.geolibre.json` su https://web.geolibre.app  
Skill agent GeoLibre: `.claude/skills/geolibre/`

---

## 9. Accettazione (se non è testabile, non è requisito)

### Job

- [ ] In UI non esiste stato, bottone o stringa “Atlantide found” / “scoperta confermata”.
- [ ] Testata (o fascicolo) dichiara **ipotesi di lavoro Sahara** e che il cartone (anelli/Atlantico) è sospetto, non target.
- [ ] Un ciclo completo (corridoio → classifica → A/B/C → pack cieco) è eseguibile su viewport 360px senza zoom di pagina.

### Prove

- [ ] Ogni nodo in classifica ha fonte + grado + kill-shot (o “aperto”).
- [ ] Layer mock ha badge `mock`. Layer schematico ha badge `schematic`.
- [ ] Walk default **non** chiama crop-mark / NDVI come caccia siti.
- [ ] Senza DEM reale, `fetch_dem` ritorna `None`. Nessuna valle sintetica.
- [ ] Mega-Chad: se il contour 320 m esiste, `grade=dem-contour` e i nodi non sono i vertici del geojson.
- [ ] `POST /walk` `richat` → `method=trap`, ranking vuoto.
- [ ] Pack cieco: zero `lon`/`lat`/`river_name`; SHA-256 verificabile (`backend/tests/test_blind.py`).
- [ ] Assenza anelli → Platone `concentric_rings` = `N/A`, mai `contradict` (`test_ledger.py`).

### Metodo

- [ ] Walk produce nodi di tipo idrico, non “temple” / “ring”.
- [ ] Confrontare un corridoio ovest e uno di controllo (Irharhar o Howar) è il default documentato, non un extra.
- [ ] ρ non è etichettato come “probabilità Atlantide”.

### Mobile

- [ ] Target ≥ 44px sugli hit principali (corridoio, classifica, A/B/C, export).
- [ ] Nessuna azione essenziale richiede hover.
- [ ] Dossier locale non lascia il device; pack cieco sì.

### Flotta (§12)

- [ ] Una segnalazione senza null, o con `p × n_tested > 0.05`, esce `SOTTO_IL_CASO` (`test_fleet.py`).
- [ ] Controllo positivo assente o fallito → `NON_CALIBRATO`, mai in coda.
- [ ] `VERIFICA_APPROFONDITA` solo con revisore ≠ autore **e** sorgente indipendente verificata.
- [ ] Testo / letteratura → `COLONNA`. Trappole (Richat, Bimini, Yonaguni, Gunung Padang) → `RESPINTO`.
- [ ] Sorgente fuori registro o `dead` → `RESPINTO`. `report --blind` non contiene `where`/`lon`/`lat`.

### Non naturale (§13)

- [ ] Nessun rilevatore "non naturale" segnala finche' il suo banco su siti noti non passa con criteri committati prima (`core/anthro/mound.py`: oggi FAIL).
- [ ] Sorgente con ruolo spiegatore (geologia, faglie, magnetico, moderno) non regge una segnalazione → `RESPINTO` (`test_fleet.py`).
- [ ] Nessuna stringa "artificiale" / "non naturale" su un punto di mappa: solo "spiegazioni naturali e moderne testate: …".

### Vaglio (§14)

- [ ] Il rilevatore dichiara recall e precisione misurate su riquadri annotati da archeologi e mai usati in addestramento, con criterio scritto prima (`vaglio/vaglio/model.py`).
- [ ] Ogni pacco di revisione contiene controlli a risposta nota, non riconoscibili dal nome; un revisore conferma o scarta solo nella direzione in cui i controlli lo dicono affidabile (`vaglio/tests`).
- [ ] Nessun esito si chiama "trovato", "scoperto", "nuovo", "confermato". Su un rilievo già analizzato da altri l'etichetta è "presumi già visto".
- [ ] `pack_cieco.json` non contiene coordinate, transetto, id, né il nome del sito noto più vicino.
- [ ] `dossier.html` si usa a 360 px senza scorrimento orizzontale, bersagli ≥ 44 px.

### GeoLibre (direzione)

- [ ] Il geojson schematico apre come progetto GeoLibre senza backend.
- [ ] Plugin/pannello forense, quando esiste, ripete il flusso §7. Non un GIS nuovo.

---

## 10. Fuori scope

- Datare un crollo, trovare oricalco, scavalcare uno scavo.
- Sostituire archeologo / storico. Il peer, se arriva, lavora sul pack cieco.
- Trasformare una classifica in una scoperta.
- Caccia anelli Richat / Mauritania come default.
- Terminale umano inventato.
- Pubblicare il dossier con coordinate.
- Fork GeoLibre. Infra a pagamento. ML “detect Atlantis” come prior.

---

## 11. Avvio e test (agent)

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
python -m unittest discover -s tests -v

cd frontend
npm install
npm run dev
```

UI legacy: http://127.0.0.1:5173 — LAN `http://<IP>:5173`  
GeoLibre: apri `data/sahara_paleodrainage.geolibre.json`

File da leggere prima di toccare codice: **§0 di questo file**, poi il resto, `docs/GEOLIBRE.md`, `frontend/src/investigate.ts`. Ignora `archaeo-sentinel-prompt.md` come piano di build.

Flotta: `/flotta` (§12). Prossimo lavoro in ordine: (1) più tile Copernicus sulla sponda Mega-Chad 320 m — un tile 1° non è il lago, (2) L-band / ammissione onesta su Sahabi, (3) solo dopo: plugin GeoLibre che **ripete** ledger + pack cieco, non un GIS nuovo. Ogni PR cita l’item di §9 che chiude.

---

## 12. Flotta — scout, cancello, scettico

Aggiunta del 16 nov 2026 (richiesta operatore: "troppo specifico"). §0 vince su questa sezione.

**Cosa fa.** Un supervisore (`/flotta`, `.claude/skills/flotta/`) lancia agenti scout, uno per dominio di banca dati pubblica, **sul mondo e non solo sul Sahara**. Gli scout scremano e propongono. All'operatore arriva solo ciò che merita una **seconda verifica** o una **verifica approfondita**. L'esito normale è zero.

**Correzione all'obiettivo "portami le anomalie".** Un'anomalia senza null è un massimo interno, e un massimo interno esiste sempre (`docs/CALIBRAZIONE.md`). Più agenti × più banche dati = più falsi positivi, non più scoperte. Quindi gli agenti **non decidono** cosa è anomalo: lo decide un cancello deterministico (`backend/core/fleet/gate.py`), uguale per tutti, testato offline.

| Agente | Dominio | Controllo positivo |
|---|---|---|
| `scout-sismo-tsunami` | terremoti, tsunami, eruzioni | Cascadia 1700 |
| `scout-mare` | batimetria, livello marino | Doggerland / Atlit-Yam, null condizionato sulla profondità |
| `scout-terreno` | DEM, radar L-band | Bama Ridge — **oggi fallisce** → tutto `NON_CALIBRATO` |
| `scout-carote` | XRF, isotopi, pollini | evento datato noto nella stessa classe di serie |
| `scout-datazioni` | ¹⁴C, dati di scavo | crollo ¹⁴C sahariano ~5.5 ka |
| `scout-fonti` | testi, letteratura | — gira per ultimo, al buio, produce `COLONNA` |
| `scettico` | seconda verifica | il suo lavoro riuscito è un `FAIL` |

**Esiti del cancello.** `RESPINTO` (incompleta, trappola, sorgente fuori registro, candidato partito dal mito) · `NON_CALIBRATO` · `SOTTO_IL_CASO` · `COLONNA` · `SECONDA_VERIFICA` · `VERIFICA_APPROFONDITA` · `FAIL`. Nessuno significa "trovato". Tutti restano agli atti, FAIL compresi.

**Invarianti.**

- `n_tested` = quanti candidati lo scout ha guardato, non quanti ne consegna. Soglia: `p × n_tested ≤ 0.05`.
- Scout cieco al mito (`myth_blind`). Area dai cataloghi fisici, criterio scritto prima (`triangolazione/METODO-v1.md`).
- Chi segnala non si rivede. "Sopravvive" vale solo con una sorgente **diversa** e verificata dal vivo.
- Solo sorgenti in `data/fleet/sources.json`, con `status` da sonda reale (`python -m core.fleet probe`). Non verificata ≠ ok.
- Coda in `data/fleet/runs/` (gitignored, ha coordinate). Condivisibile: solo `report --blind`.
- Gli scout usano il codice di misura che c'è. La flotta non è una scusa per il nono rilevatore.

**Fuori scope.** Agenti che girano da soli a orario. Agenti che scrivono codice o spec. "Tutte le banche dati": entra una sorgente alla volta, sondata.

---

## 13. "Non naturale" — direzione aperta il 16 nov 2026

Richiesta operatore: una mappa, da casa, delle anomalie **non riconducibili all'azione naturale**, con le prove. §0 vince. Il §1 non è riscritto: questa è una seconda domanda che usa la stessa flotta e lo stesso cancello, e a differenza di "Atlantide" passa le cinque colonne di `docs/BERSAGLIO.md` (firma, scala, contesto, null, **migliaia** di controlli positivi).

**Tre classi, non due.** Naturale · moderno · antico. Da casa non si dimostra "antico": si esclude naturale e moderno, una spiegazione alla volta, e si scrive quali.

**Ruoli delle sorgenti** (`data/fleet/sources.json`, campo `role`).

| Ruolo | Esempi | Uso |
|---|---|---|
| `detector` | DEM, Sentinel-2, radar | può reggere una segnalazione |
| `known_sites` | Menze & Ur (14.324 siti, CC0), Wikidata, toponimi GeoNames | controlli positivi |
| `natural_explainer` | geologia Macrostrat, faglie GEM, magnetico EMAG2 | lo scettico ci **uccide** |
| `modern_explainer` | WorldCover, CORONA, OSM | idem |

**Anomalie magnetiche, termiche, sismiche: cosa sono davvero da casa.** Magnetico globale = griglia a ~3,7 km: vede la crosta, non un muro (la magnetometria archeologica si fa a piedi). Termico gratuito = ~100 m: strutture grandi e umidità, non edifici. Sismico = cataloghi di eventi e faglie: non trova niente, **spiega** i lineamenti. Per questo entrano come spiegatori, non come rilevatori. Venderli come rilevatori sarebbe il DEM sintetico con un altro nome.

**Stato del primo banco (tumuli sul DEM a 30 m, alto Khabur).** Pre-registrato, eseguito, **FAIL due volte**. Scansione al buio: su 100 allarmi, 86–98 non sono tumuli a catalogo. Numeri e diagnosi nel docstring di `backend/core/anthro/mound.py`.

**Prossimo colpo, in ordine.** (1) Secondo dato sugli allarmi del DEM: spettro Sentinel-2 multi-temporale (è la firma con cui Menze & Ur i siti li hanno trovati), poi geologia e toponimi come filtro. Pre-registrato, su tile non bruciati (restano N36E039, N37E039, N37E042). (2) Solo se la combinazione passa: scansione fuori dal Khabur e mappa GeoLibre con scheda-prova. (3) Non una v3 sul solo rilievo.

---

## 14. Vaglio — prodotto a sé (`vaglio/`)

Aggiunto il 16 nov 2026 su richiesta dell'operatore. È il rilevatore che a §13 mancava: lavora dove esiste LiDAR pubblico ad alta risoluzione invece che sul DEM a 30 m. §0 vince.

**Cosa fa.** `python -m vaglio`: scarica un rilievo LiDAR pubblico, calcola le visualizzazioni, segnala i rilievi a forma di costruzione, li raggruppa in complessi, li fa rivedere al buio, li confronta col già noto, scrive un fascicolo HTML offline. Istruzioni in `vaglio/README.md`.

**Perché non è il compitino.** Nasce dal caso Miotti (nov 2026: 48 agenti, un sito maya "non mappato" che era già pubblicato). Copia il metodo e aggiunge le tre misure che lì mancavano: errore del rilevatore, errore dei revisori, controllo del già noto.

**Invarianti.**

- Il rilevatore si tara solo su annotazioni di archeologi (oggi: Chactún, Kokalj et al. 2023) con divisione addestramento/test degli autori del dataset. Ogni modifica si committa prima di rieseguire il test.
- I revisori (agenti o persone) vedono immagini senza nome né posizione, con controlli piantati. Conferma solo chi scarta i vuoti noti; scarta solo chi trova le strutture note. Servono due revisori.
- Un candidato su un rilievo già studiato si presume già visto. Sullo Yucatán esiste il catalogo Britton 2026 (57.181 strutture, non pubblico): lì Vaglio **riproduce**, non scopre.
- Coordinate solo in `vaglio_lavoro/` (gitignored). Condivisibile: `pack_cieco.json`.
- Il punteggio d'ordine decide cosa guardare prima. Non è una probabilità e non si mostra come tale.

**Stato al 16 nov 2026.** Rilevatore: test pre-registrato **passato** (recall 0,76, precisione 0,83 su 942 strutture mai viste). Scansione completa: 456/456 transetti, 1.272,7 km² e 11.916 complessi candidati. Dei 40 candidati rivisti, 15 reggono (12 dei 20 più alti e 3 dei 20 casuali) e 25 restano incerti; i revisori agenti confermano ma non scartano. Altri 11.876 candidati sono da rivedere. Numeri e pack cieco in `vaglio/README.md` e `vaglio/pack_cieco.json`. Prossimo: aggiungere revisori di altro tipo (Grok, ChatGPT, persone) per poter anche scartare, chiedere a Britton il confronto col suo catalogo.

**Fuori scope.** Dichiarare un sito. Contattare enti a nome dell'operatore. Pubblicare coordinate. Scansionare rilievi con licenza che non lo consente.
