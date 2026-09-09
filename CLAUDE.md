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

Prossimo lavoro in ordine: (1) più tile Copernicus sulla sponda Mega-Chad 320 m — un tile 1° non è il lago, (2) L-band / ammissione onesta su Sahabi, (3) solo dopo: plugin GeoLibre che **ripete** ledger + pack cieco, non un GIS nuovo. Ogni PR cita l’item di §9 che chiude.
