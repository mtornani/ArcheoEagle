# ARCHAEO-SENTINEL: Prompt di Handover Completo per Continuazione Sviluppo

## CHI SONO
Mirko Tornani. Sviluppatore, appassionato di archeologia e analisi satellitare. Voglio un tool usabile, non un prototipo accademico.

---

## OBIETTIVO DEL PROGETTO

**Archaeo-Sentinel** e' una piattaforma open-source che permette ad archeologi, ricercatori indipendenti e appassionati di storia antica di:
1. Selezionare un'area di interesse (AOI) su una mappa interattiva
2. Acquisire immagini satellitari gratuite (Sentinel-2 da Copernicus)
3. Eseguire analisi multi-spettrale automatica (NDVI, BSI) per rilevare anomalie compatibili con siti archeologici sepolti
4. Ricevere spiegazioni dettagliate del PERCHE' un'anomalia e' stata segnalata
5. Esportare i risultati in GeoJSON per uso in QGIS o Google Earth

L'ispirazione viene dall'approccio di Randall Carlson + paper Nature 2023 "A human-AI collaboration workflow for archaeological sites detection" + dataset DAFA-LS + progetto EAMENA.

**Il gap colmato**: tutti i pezzi tecnologici esistono (imagery gratuita, modelli ML, API), ma nessuno li ha assemblati in un tool usabile senza competenze di coding.

---

## ARCHITETTURA

```
Frontend (React 19 + TypeScript + Vite 8 + Tailwind v4 + Leaflet)
    |
    | fetch POST /api/v1/analysis/run
    | fetch POST /api/v1/imagery/acquire/sentinel2
    | fetch POST /api/v1/export/geojson
    |
Backend (FastAPI + Python 3.11 + NumPy)
    |
    |-- core/imagery/sentinel2.py      (Copernicus CDSE client, OAuth2)
    |-- core/preprocessing/spectral.py (NDVI, BSI calculation)
    |-- core/detection/rule_based.py   (anomaly detection + reasoning)
    |
Docker (PostGIS + Redis + Celery worker) -- NON ANCORA ATTIVO, dev mode locale
```

---

## STATO ATTUALE DEL CODICE (22 Marzo 2026)

### Cosa FUNZIONA:
- Frontend: mappa Leaflet con imagery satellitare Esri + OpenStreetMap
- Frontend: draw tool per rettangolo/poligono AOI (leaflet-draw)
- Frontend: pannello analisi a 3 step (seleziona AOI -> configura -> risultati)
- Frontend: popup sulla mappa con spiegazioni dettagliate delle anomalie
- Backend: FastAPI con 3 router (imagery, analysis, export)
- Backend: Copernicus CDSE client con autenticazione OAuth2 (fallback mock senza credenziali)
- Backend: calcolo NDVI e BSI su bande simulate
- Backend: detection rule-based con reasoning chain (3 regole spiegate)
- Backend: export GeoJSON
- TypeScript compila senza errori, ESLint passa a 0 errori

### Cosa e' MOCK / INCOMPLETO:
- **L'analisi usa dati SIMULATI** (numpy random arrays 100x100 con anomalia iniettata a 45:55,45:55). NON scarica ancora immagini reali.
- **Lo score e' hardcoded a 0.88** — deve essere calcolato dinamicamente
- **Il candidato e' sempre 1 solo punto** nel centroide dell'AOI — deve generare candidati multipli nelle posizioni reali delle anomalie
- **Non c'e' database** (PostgreSQL/PostGIS previsto ma non implementato)
- **Non c'e' Celery** (task queue per processing pesante)
- **Non c'e' sistema di progetti** (CRUD per salvare analisi)
- **Non ci sono modelli ML** (U-Net, autoencoder, Siamese planned ma non implementati)
- **Non c'e' DEM/CORONA/GEE** integration
- **Non c'e' layer toggle** sulla mappa (NDVI heatmap, BSI heatmap, etc.)
- **Non c'e' timeline slider** per navigazione temporale
- **API endpoint hardcoded** a http://127.0.0.1:8000 nel frontend

### Bug NOTI / Problemi UX:
- Il rettangolo disegnato sulla mappa ha visibilita' limitata (fill azzurro molto tenue su sfondo satellite scuro) — servirebbero bordi piu' spessi o colori piu' contrastanti
- Il cloud cover slider nel pannello non viene usato nella request all'API analysis
- Il marker dell'anomalia appare come un cerchietto piccolo ambra che puo' passare inosservato — servirebbe un'animazione piu' evidente o un'area evidenziata
- Su mobile il pannello copre tutta la mappa — serve UX mobile migliore
- Le spiegazioni delle anomalie sono in italiano misto inglese — uniformare

---

## TUTTI I FILE SORGENTE ATTUALI

### Struttura directory:
```
ArcheoEagle/
├── .env.example
├── README.md
├── archaeo-sentinel-prompt.md     (prompt originale di design, 760 righe)
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   ├── api/
│   │   ├── __init__.py            (vuoto)
│   │   └── routes/
│   │       ├── __init__.py        (importa imagery, analysis, export)
│   │       ├── imagery.py
│   │       ├── analysis.py
│   │       └── export.py
│   └── core/
│       ├── __init__.py            (vuoto)
│       ├── imagery/
│       │   ├── __init__.py        (vuoto)
│       │   └── sentinel2.py
│       ├── preprocessing/
│       │   ├── __init__.py        (vuoto)
│       │   └── spectral.py
│       └── detection/
│           ├── __init__.py        (vuoto)
│           └── rule_based.py
├── frontend/
│   ├── Dockerfile
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   ├── eslint.config.js
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── App.css               (vuoto)
│       ├── index.css
│       └── components/
│           ├── MapCanvas.tsx
│           └── ControlPanel.tsx
├── data/                          (vuoto, per cache e modelli)
├── notebooks/                     (vuoto, per Jupyter)
└── docs/                          (vuoto, per documentazione)
```

### FILE: backend/main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import imagery, analysis, export

app = FastAPI(title="Archaeo-Sentinel API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(imagery.router, prefix="/api/v1/imagery", tags=["imagery"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(export.router, prefix="/api/v1/export", tags=["export"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Archaeo-Sentinel API"}
```

### FILE: backend/requirements.txt
```
numpy>=1.24
rasterio>=1.3
gdal>=3.6
geopandas>=0.14
shapely>=2.0
pyproj>=3.6
torch>=2.0
segmentation-models-pytorch>=0.3
scikit-image>=0.21
opencv-python>=4.8
requests>=2.31
fastapi>=0.100
uvicorn>=0.23
pydantic>=2.4
sqlalchemy>=2.0
geoalchemy2>=0.14
celery>=5.3
redis>=5.0
openeo>=0.28
sentinelhub>=3.9
```

### FILE: backend/api/routes/imagery.py
```python
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict, List
from core.imagery.sentinel2 import copernicus_client

router = APIRouter()

class AOIRequest(BaseModel):
    geojson: Dict[str, Any]
    date_range: List[str] = None
    max_cloud_cover: int = 20

def get_bbox_from_geojson(geojson: Dict[str, Any]) -> List[float]:
    try:
        coords = geojson['geometry']['coordinates'][0]
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        return [min(lons), min(lats), max(lons), max(lats)]
    except Exception:
        return [43.0, 32.0, 44.0, 33.0]

@router.post("/acquire/sentinel2")
def acquire_sentinel2(request: AOIRequest):
    bbox = get_bbox_from_geojson(request.geojson)
    results = copernicus_client.search_sentinel2(bbox, max_cloud_cover=request.max_cloud_cover)
    return {"message": "Sentinel-2 search completed", "aoi_bbox": bbox, "results": results}
```

### FILE: backend/api/routes/analysis.py
```python
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict
import numpy as np
from core.detection.rule_based import detect_anomalies

router = APIRouter()

class AnalysisRequest(BaseModel):
    aoi_geojson: Dict[str, Any]
    layer_id: str = "sentinel-2"

@router.post("/run")
def run_analysis(request: AnalysisRequest):
    # MOCK: dati simulati — DA SOSTITUIRE con imagery reale
    shape = (100, 100)
    mock_bands = {
        'B02': np.random.rand(*shape) * 1000,
        'B04': np.random.rand(*shape) * 1000,
        'B08': np.random.rand(*shape) * 4000,
        'B11': np.random.rand(*shape) * 2000,
    }
    # Anomalia iniettata artificialmente
    mock_bands['B08'][45:55, 45:55] = 500
    mock_bands['B04'][45:55, 45:55] = 2000
    mock_bands['B11'][45:55, 45:55] = 3000
    mock_bands['B02'][45:55, 45:55] = 500

    results = detect_anomalies(mock_bands)

    try:
        coords = request.aoi_geojson['geometry']['coordinates'][0][0]
        lon, lat = coords[0], coords[1]
    except (KeyError, IndexError, TypeError):
        lon, lat = 44.3661, 33.3152

    candidate = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {
            "score": 0.88,  # HARDCODED — da calcolare
            "type": "spectral_anomaly",
            "pixels": results.get("anomaly_pixels_detected", 0),
            "reasons": results.get("reasons", []),
        }
    }

    return {
        "message": "Analysis completed successfully",
        "candidates": {"type": "FeatureCollection", "features": [candidate]},
        "stats": results
    }
```

### FILE: backend/api/routes/export.py
```python
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List
import datetime

router = APIRouter()

class ExportRequest(BaseModel):
    candidates: List[Dict[str, Any]]
    project_name: str = "archaeo_export"

@router.post("/geojson")
def export_geojson(request: ExportRequest):
    feature_collection = {
        "type": "FeatureCollection",
        "features": request.candidates,
        "metadata": {
            "project": request.project_name,
            "export_date": datetime.datetime.now().isoformat(),
            "generator": "Archaeo-Sentinel MVP"
        }
    }
    headers = {"Content-Disposition": f"attachment; filename={request.project_name}.geojson"}
    return JSONResponse(content=feature_collection, headers=headers)
```

### FILE: backend/core/imagery/sentinel2.py
```python
import os
import requests
from typing import Dict, Any, List

class CopernicusClient:
    def __init__(self):
        self.username = os.getenv("COPERNICUS_USER")
        self.password = os.getenv("COPERNICUS_PASSWORD")
        self.token = None
        self.auth_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
        self.odata_url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

    def authenticate(self) -> bool:
        if not self.username or not self.password:
            return False
        data = {"client_id": "cdse-public", "username": self.username, "password": self.password, "grant_type": "password"}
        try:
            response = requests.post(self.auth_url, data=data, timeout=15)
            response.raise_for_status()
            self.token = response.json().get("access_token")
            return True
        except Exception:
            return False

    def search_sentinel2(self, bbox: List[float], max_cloud_cover: int = 20) -> List[Dict[str, Any]]:
        if not self.token:
            if not self.authenticate():
                return [{"id": "mock-scene-1234", "Name": "S2A_MSIL2A_MOCK_SCENE", "cloudCover": 5.0}]
        polygon = f"POLYGON(({bbox[0]} {bbox[1]}, {bbox[2]} {bbox[1]}, {bbox[2]} {bbox[3]}, {bbox[0]} {bbox[3]}, {bbox[0]} {bbox[1]}))"
        filter_query = (
            f"OData.CSC.Intersects(area=geography'SRID=4326;{polygon}') "
            f"and Collection/Name eq 'SENTINEL-2' "
            f"and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/Value eq 'S2MSI2A') "
            f"and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/Value le {max_cloud_cover})"
        )
        params = {"$filter": filter_query, "$top": 5, "$orderby": "ContentDate/Start desc"}
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(self.odata_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json().get("value", [])
        except Exception:
            return []

copernicus_client = CopernicusClient()
```

### FILE: backend/core/preprocessing/spectral.py
```python
import numpy as np

def calculate_ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
    denominator = nir + red
    np.seterr(invalid='ignore', divide='ignore')
    return np.where(denominator == 0, 0, (nir - red) / denominator)

def calculate_bsi(swir: np.ndarray, red: np.ndarray, nir: np.ndarray, blue: np.ndarray) -> np.ndarray:
    term1 = swir + red
    term2 = nir + blue
    denominator = term1 + term2
    np.seterr(invalid='ignore', divide='ignore')
    return np.where(denominator == 0, 0, (term1 - term2) / denominator)
```

### FILE: backend/core/detection/rule_based.py
```python
import numpy as np
from core.preprocessing.spectral import calculate_ndvi, calculate_bsi

def detect_anomalies(sentinel_bands: dict) -> dict:
    try:
        nir = sentinel_bands.get('B08')
        red = sentinel_bands.get('B04')
        swir = sentinel_bands.get('B11')
        blue = sentinel_bands.get('B02')

        if any(b is None for b in [nir, red, swir, blue]):
            return {"error": "Missing required bands (B02, B04, B08, B11)"}

        ndvi_map = calculate_ndvi(nir, red)
        bsi_map = calculate_bsi(swir, red, nir, blue)

        ndvi_mean = np.nanmean(ndvi_map)
        ndvi_std = np.nanstd(ndvi_map)
        ndvi_threshold = ndvi_mean - 1.5 * ndvi_std
        ndvi_anomaly = ndvi_map < ndvi_threshold

        bsi_threshold = 0.2
        bsi_anomaly = bsi_map > bsi_threshold

        combined_anomaly = np.logical_and(ndvi_anomaly, bsi_anomaly)
        anomaly_pixel_count = int(np.sum(combined_anomaly))

        ndvi_anomaly_mean = float(np.nanmean(ndvi_map[combined_anomaly])) if anomaly_pixel_count > 0 else None
        bsi_anomaly_mean = float(np.nanmean(bsi_map[combined_anomaly])) if anomaly_pixel_count > 0 else None

        reasons = []
        if anomaly_pixel_count > 0:
            reasons.append({
                "rule": "NDVI Crop Mark",
                "triggered": True,
                "detail": (
                    f"La vegetazione nella zona anomala ha NDVI medio {ndvi_anomaly_mean:.3f}, "
                    f"significativamente sotto la media circostante ({ndvi_mean:.3f}). "
                    f"Soglia applicata: < {ndvi_threshold:.3f} (media - 1.5 deviazioni standard). "
                    f"Strutture sepolte alterano la crescita radicale, creando 'crop marks' visibili nello spettro NIR."
                ),
            })
            reasons.append({
                "rule": "BSI Soil Mark",
                "triggered": True,
                "detail": (
                    f"L'indice di suolo nudo (BSI) nella zona anomala e' {bsi_anomaly_mean:.3f}, "
                    f"sopra la soglia {bsi_threshold}. "
                    f"Terreno con riflettanza SWIR/Red elevata indica suolo disturbato o compattato, "
                    f"tipico di fondamenta, muri o strutture interrate che alterano il drenaggio."
                ),
            })
            reasons.append({
                "rule": "Combinazione Multi-Indice",
                "triggered": True,
                "detail": (
                    f"La sovrapposizione di anomalia vegetativa (NDVI basso) e suolo esposto (BSI alto) "
                    f"su {anomaly_pixel_count} pixel contigui e' un pattern compatibile con strutture "
                    f"archeologiche sepolte (muri, fondamenta, canali)."
                ),
            })

        return {
            "ndvi_mean": float(ndvi_mean),
            "ndvi_threshold": float(ndvi_threshold),
            "ndvi_anomaly_mean": ndvi_anomaly_mean,
            "bsi_threshold_applied": bsi_threshold,
            "bsi_anomaly_mean": bsi_anomaly_mean,
            "anomaly_pixels_detected": anomaly_pixel_count,
            "reasons": reasons,
            "success": True
        }
    except Exception as e:
        return {"error": str(e), "success": False}
```

### FILE: frontend/package.json
```json
{
  "name": "frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "@tailwindcss/vite": "^4.2.2",
    "@types/leaflet": "^1.9.21",
    "@types/leaflet-draw": "^1.0.13",
    "clsx": "^2.1.1",
    "leaflet": "^1.9.4",
    "leaflet-draw": "^1.0.4",
    "lucide-react": "^0.577.0",
    "react": "^19.2.4",
    "react-dom": "^19.2.4",
    "react-leaflet": "^5.0.0",
    "react-leaflet-draw": "^0.21.0",
    "tailwind-merge": "^3.5.0",
    "zustand": "^5.0.12"
  },
  "devDependencies": {
    "@eslint/js": "^9.39.4",
    "@tailwindcss/postcss": "^4.2.2",
    "@types/node": "^24.12.0",
    "@types/react": "^19.2.14",
    "@types/react-dom": "^19.2.3",
    "@vitejs/plugin-react": "^6.0.1",
    "autoprefixer": "^10.4.27",
    "eslint": "^9.39.4",
    "eslint-plugin-react-hooks": "^7.0.1",
    "eslint-plugin-react-refresh": "^0.5.2",
    "globals": "^17.4.0",
    "postcss": "^8.5.8",
    "tailwindcss": "^4.2.2",
    "typescript": "~5.9.3",
    "typescript-eslint": "^8.57.0",
    "vite": "^8.0.1"
  }
}
```

### FILE: frontend/src/App.tsx
```tsx
/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState } from 'react'
import MapCanvas from './components/MapCanvas'
import ControlPanel from './components/ControlPanel'
import { Menu, X, Radar } from 'lucide-react'

function App() {
  const [panelOpen, setPanelOpen] = useState(true)
  const [aoi, setAoi] = useState<any>(null)
  const [candidates, setCandidates] = useState<any>(null)

  return (
    <div className="relative h-screen w-full bg-dark text-light overflow-hidden flex flex-col">
      <header className="flex items-center justify-between px-4 py-2.5 bg-darker/80 backdrop-blur-lg z-30 border-b border-white/5 shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-secondary/20 flex items-center justify-center">
            <Radar size={18} className="text-secondary" />
          </div>
          <div>
            <h1 className="font-bold text-sm tracking-wide leading-none">
              ARCHAEO<span className="text-secondary">SENTINEL</span>
            </h1>
            <p className="text-[10px] text-muted leading-none mt-0.5">Anomaly Detection Platform</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {aoi && (
            <span className="hidden sm:flex items-center gap-1.5 text-xs text-success bg-success/10 px-2.5 py-1 rounded-full">
              <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
              AOI selezionata
            </span>
          )}
          <button onClick={() => setPanelOpen(!panelOpen)} className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
            {panelOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden relative">
        <div className="flex-1 relative z-0">
          <MapCanvas aoi={aoi} setAoi={setAoi} candidates={candidates} />
        </div>
        <div className={`${panelOpen ? 'translate-x-0' : 'translate-x-full'} absolute md:static right-0 top-0 w-full sm:w-96 h-full bg-darker/95 backdrop-blur-xl border-l border-white/5 z-20 transition-transform duration-300 ease-out flex flex-col`}>
          <ControlPanel closePanel={() => setPanelOpen(false)} aoi={aoi} setCandidates={setCandidates} />
        </div>
      </div>
    </div>
  )
}

export default App
```

### FILE: frontend/src/components/MapCanvas.tsx
```tsx
/* eslint-disable @typescript-eslint/no-explicit-any */
import { MapContainer, TileLayer, FeatureGroup, GeoJSON, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet-draw/dist/leaflet.draw.css'
import { useEffect, useRef } from 'react'
import L from 'leaflet'

;(window as any).L = L
import "leaflet-draw"

delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

function RawDrawControl({ setAoi, fgRef }: { setAoi: (aoi: any) => void, fgRef: any }) {
  const map = useMap();
  useEffect(() => {
    if (!map || !fgRef.current) return;
    const drawnItems = fgRef.current;
    const drawControl = new L.Control.Draw({
      edit: { featureGroup: drawnItems },
      draw: { polyline: false, polygon: {}, circle: false, rectangle: {}, marker: false, circlemarker: false }
    });
    map.addControl(drawControl)
    const onDrawCreated = (e: any) => { drawnItems.clearLayers(); drawnItems.addLayer(e.layer); setAoi(e.layer.toGeoJSON()) }
    const onDrawEdited = (e: any) => { e.layers.eachLayer((layer: any) => setAoi(layer.toGeoJSON())) }
    const onDrawDeleted = () => { if (drawnItems.getLayers().length === 0) setAoi(null) }
    map.on('draw:created', onDrawCreated)
    map.on('draw:edited', onDrawEdited)
    map.on('draw:deleted', onDrawDeleted)
    return () => { map.removeControl(drawControl); map.off('draw:created', onDrawCreated); map.off('draw:edited', onDrawEdited); map.off('draw:deleted', onDrawDeleted) }
  }, [map, fgRef, setAoi])
  return null
}

export default function MapCanvas({ setAoi, candidates }: { aoi: any, setAoi: (a: any) => void, candidates: any }) {
  const featureGroupRef = useRef(null)
  return (
    <MapContainer center={[33.3152, 44.3661]} zoom={7} className="w-full h-full" zoomControl={false}>
      <TileLayer attribution='&copy; OpenStreetMap' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <TileLayer url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}" attribution="Tiles &copy; Esri" maxZoom={18} />
      <FeatureGroup ref={featureGroupRef}>
        <RawDrawControl setAoi={setAoi} fgRef={featureGroupRef} />
      </FeatureGroup>
      {candidates && (
        <GeoJSON
          data={candidates}
          key={JSON.stringify(candidates._timestamp)}
          pointToLayer={(_feature, latlng) => L.circleMarker(latlng, { radius: 14, fillColor: "#f59e0b", color: "#fff", weight: 2, opacity: 1, fillOpacity: 0.85, className: 'anomaly-marker' })}
          onEachFeature={(feature, layer) => {
            if (feature.properties) {
              const p = feature.properties
              const reasonsHtml = (p.reasons || []).map((r: any) =>
                `<div class="popup-reason"><div class="popup-reason-title">${r.rule}</div><div class="popup-reason-detail">${r.detail}</div></div>`
              ).join('')
              layer.bindPopup(
                `<div class="popup-header">Anomalia Rilevata</div>` +
                `<div class="popup-badges"><span class="popup-badge popup-badge-score">Score ${p.score}</span><span class="popup-badge popup-badge-pixels">${p.pixels} pixel</span></div>` +
                reasonsHtml,
                { maxWidth: 360, minWidth: 280 }
              );
            }
            layer.openPopup()
          }}
        />
      )}
    </MapContainer>
  )
}
```

### FILE: frontend/src/components/ControlPanel.tsx
(vedi il file completo nel repo — 209 righe con StepCard e MetricBox helper components, pannello a 3 step, accordion reasons, error handling)

### FILE: frontend/src/index.css
(vedi il file completo nel repo — 173 righe con theme colors Tailwind v4, leaflet overrides con !important per Tailwind SVG reset, custom popup classes, anomaly marker pulse animation)

### FILE: docker-compose.yml
```yaml
services:
  db:
    image: postgis/postgis:16-3.4
    environment:
      POSTGRES_DB: archaeo_sentinel
      POSTGRES_USER: archeo
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes: [pgdata:/var/lib/postgresql/data]
    ports: ["5432:5432"]
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://archeo:${DB_PASSWORD}@db:5432/archaeo_sentinel
      REDIS_URL: redis://redis:6379
      COPERNICUS_USER: ${COPERNICUS_USER}
      COPERNICUS_PASSWORD: ${COPERNICUS_PASSWORD}
    volumes: [./data:/app/data]
    ports: ["8000:8000"]
    depends_on: [db, redis]
  worker:
    build: ./backend
    command: celery -A tasks.celery_app worker -l info
    depends_on: [db, redis]
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    depends_on: [backend]
volumes:
  pgdata:
```

---

## PROBLEMI TECNICI SPECIFICI DA CONOSCERE

1. **Tailwind v4 rompe Leaflet SVG**: Tailwind v4 resetta `fill`, `stroke`, `stroke-width` su tutti gli SVG path. Per questo i rettangoli disegnati con leaflet-draw diventano invisibili. La fix e' in `index.css` con `!important` su `.leaflet-container svg path.leaflet-interactive`.

2. **leaflet-draw + Vite ESM**: leaflet-draw patcha l'oggetto globale `L`, ma Vite ESM lo isola. La fix e' `(window as any).L = L` prima dell'import di leaflet-draw.

3. **Python __pycache__**: quando modifichi i file Python del backend, se usi `uvicorn --reload`, a volte il reload non prende le modifiche perche' Python carica i `.pyc` dalla cache. Devi cancellare `__pycache__` manualmente in tutte le sotto-directory e riavviare uvicorn.

4. **CORS**: il backend FastAPI accetta solo origini specifiche (localhost:5173/5174). Se cambi porta frontend, aggiorna `main.py`.

---

## PROSSIMI PASSI PRIORITARI

### IMMEDIATO (prima iterazione):
1. **Sostituire i dati mock con imagery reale**: usare il `CopernicusClient` gia' implementato per scaricare veramente le bande B02/B04/B08/B11 di Sentinel-2 per l'AOI selezionata, e passarle a `detect_anomalies()`
2. **Calcolare lo score dinamicamente** invece di hardcoded 0.88
3. **Generare candidati multipli** nelle posizioni reali delle anomalie (clustering dei pixel anomali con coordinate geografiche)
4. **Usare il cloud cover slider** che l'utente configura nel frontend

### FASE 2:
5. Aggiungere DEM (SRTM) + features morfologiche (TPI, slope)
6. Layer toggle sulla mappa (NDVI heatmap, BSI heatmap overlay)
7. Timeline slider per navigazione temporale (stagioni diverse)
8. Comparison slider prima/dopo
9. Database PostgreSQL/PostGIS per salvare progetti e analisi

### FASE 3:
10. Primo modello ML: autoencoder per anomaly detection unsupervised
11. Ensemble scoring (rule + ML + temporal)
12. Report generator (PDF/HTML)
13. CORONA (immagini declassificate 1960s) integration

---

## PRINCIPI DI DESIGN

1. **Archeologo-first**: l'utente target non sa programmare. Tutto da UI.
2. **Progressive disclosure**: risultati semplici di default, dettagli su richiesta.
3. **Human-in-the-loop**: l'AI propone, l'umano decide. Ogni candidato va validato.
4. **Spiegabilita'**: ogni anomalia DEVE avere un "perche'" chiaro e leggibile.
5. **Offline-capable**: il frontend deve funzionare con dati pre-scaricati.
6. **Open everything**: codice MIT, dati CC-BY-SA, modelli open-weight.

---

## COME LANCIARE IL PROGETTO IN DEV

```bash
# Backend
cd backend
pip install numpy fastapi uvicorn pydantic requests
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Frontend (in un altro terminale)
cd frontend
npm install
npm run dev
# Apri http://localhost:5173
```

---

*Prompt generato il 22 Marzo 2026 — Stato: MVP funzionante con dati mock*
*Autore: Mirko Tornani*
