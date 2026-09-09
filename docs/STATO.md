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
