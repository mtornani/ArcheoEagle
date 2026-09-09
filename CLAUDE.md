# ArcheoEagle — Claude Code

Motore forense sui paleofiumi del Sahara. Open source. €0 infra.

Non è un bottone “Atlantide found”. Non cerca anelli. Cammina la rete idrica fossile, misura dopo la forma, Platone è colonna `+ / − / N/A`. Assenza di anelli non contraddice.

Repo: https://github.com/mtornani/ArcheoEagle
Path locale: `D:\AI\ArcheoEagle`

## Svolta: GeoLibre, non un secondo GIS

GIS host = [GeoLibre](https://github.com/opengeos/GeoLibre) (browser, desktop, iOS, Android, Jupyter). 1000+ tool WASM (idrologia, remote sensing, terrain). Dati restano sul device.

ArcheoEagle **non** rifà Leaflet. ArcheoEagle è il **dominio forense** sopra GeoLibre:

| Tiene (nostro) | Delegato a GeoLibre |
|---|---|
| Walk paleofiumi → nodi | Mappa, layer, stile, mobile |
| Ledger pro/contro/residuo/kill-shot | Hydrology WASM (flow, watershed, stream) |
| Pack cieco A/B/C + SHA-256 | Remote sensing (indici, band math) |
| Platone `+ / − / N/A` | DEM/terrain, COG, GeoJSON |
| Grade schematic vs rilievo | Plugin API + `.geolibre.json` |

Dettaglio: `docs/GEOLIBRE.md`. Skill agent: `.claude/skills/geolibre/`.

## Avvio locale

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000

cd frontend
npm install
npm run dev
```

UI: http://127.0.0.1:5173 — LAN: `http://<IP>:5173`

Mappa GeoLibre (senza backend): apri `data/sahara_paleodrainage.geolibre.json` su https://web.geolibre.app/ (File → Open) oppure GeoLibre app mobile.

## Test

```bash
cd backend
python -m unittest discover -s tests -v
```

## Regole

- Tracciati in `data/sahara_paleodrainage.geojson` = schematici da letteratura. Un vertice **non** è un sito.
- Dossier locale (coord) resta sul disco. Pack cieco = niente pin.
- Operatore ≠ peer. Due umani, stessi layer, mai 100%.
- Mock Copernicus se mancano `COPERNICUS_USER` / `COPERNICUS_PASSWORD`. Dichiaralo.
- Non inventare un “terminale umano”. Pack cieco è il deliverable.
- Non forkare GeoLibre. Plugin esterno o progetto `.geolibre.json`.
- Stack €0. Niente infra a pagamento.

## Mobile (questa è la via)

1. Clone `https://github.com/mtornani/ArcheoEagle`
2. Apri la cartella in Claude Code
3. Leggi questo file + `docs/GEOLIBRE.md`
4. Per la mappa: GeoLibre app (iOS/Android) o https://web.geolibre.app
5. Per il forense: `backend/` (ledger, blind, paleorivers)

Prossimo lavoro: plugin GeoLibre `archeoeagle` (pannello ledger + pack cieco), poi hydrology WASM al posto del solo walk su geojson schematico.
