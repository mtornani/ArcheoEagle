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
