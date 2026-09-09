# GeoLibre — perché è la svolta

Upstream: https://github.com/opengeos/GeoLibre  
Web: https://web.geolibre.app/  
Docs: https://geolibre.app  
Plugin API: https://github.com/opengeos/GeoLibre/blob/main/docs/plugin-api.md  
Skill agent: `.claude/skills/geolibre/` (copiata da upstream, per Claude Code mobile)

## Cosa risolve

Il frontend attuale (`frontend/`, Leaflet + draw) è un GIS fatto in casa. GeoLibre è già:

- browser + desktop + **iOS + Android**
- MapLibre + DuckDB-WASM + deck.gl
- **1000+ tool in WASM** (hydrology 100, remote sensing 154, terrain 99)
- dati **locali** — niente server, niente leak di pin
- progetto portabile `.geolibre.json`
- Plugin API (pannello, layer GeoJSON, COG, toolbar)
- skill + MCP per Claude Code (`geolibre-mcp`)

Hydrology WASM (flow accumulation, watershed, stream network) è il pezzo che il walk schematico su `sahara_paleodrainage.geojson` non può fare da solo. Sahabi (radar sotto sabbia) vive di DEM + RS, non di un LineString da paper.

## Architettura target

```
GeoLibre (host GIS, mobile/desktop/web)
    └── plugin archeoeagle  OR  progetto .geolibre.json
            ├── layer paleodrenaggi (schematici, grade dichiarato)
            ├── tool Whitebox: hydrology / RS / terrain
            └── chiama backend ArcheoEagle solo per:
                    walk nodi → ledger → pack cieco SHA-256
```

Backend FastAPI resta. Non si butta. Si toglie il GIS duplicato.

## Fasi

1. **Ora** — `data/sahara_paleodrainage.geolibre.json` apribile in GeoLibre. Repo su GitHub per Claude Code da telefono.
2. **Plugin** — `id: archeoeagle`. Pannello destro: corridoio, classifica nodi, ledger, export pack cieco. `addGeoJsonLayer` per i nodi. Niente pin nel pack.
3. **Hydrology** — DEM reale (OpenTopography / Copernicus) → Whitebox stream/watershed **accanto** ai tracciati schematici, come controllo. Irharhar/Howar come negativo, non un solo mare.
4. **Campo** — GeoLibre app nativa + GPS. Note e pack cieco restano on-device.

## Fuori scope

- Fork di GeoLibre
- “Atlantide found” button
- Pubblicare coordinate del dossier locale
- Sostituire uno scavo o uno storico
- Infra a pagamento

## Come aprirlo adesso

1. Installa GeoLibre (app store / https://geolibre.app/downloads/) oppure apri https://web.geolibre.app
2. File → Open → `data/sahara_paleodrainage.geolibre.json`
3. I LineString oro sono schematici. Un vertice non è un sito.
