# ARCHAEO-SENTINEL: Open-Source Archaeological Discovery Platform
## Vibe-Coding Master Prompt

---

## 🎯 VISIONE DEL PRODOTTO

Costruisci **Archaeo-Sentinel**, una piattaforma open-source che permette ad archeologi, ricercatori indipendenti e appassionati di storia antica di analizzare immagini satellitari archiviate per individuare anomalie compatibili con siti archeologici non ancora scoperti, e di indirizzare ricerche sul campo in modo mirato.

L'ispirazione viene dall'approccio di Randall Carlson (analisi geomorfologica da satellite per ricostruire eventi catastrofici e civilizzazioni perdute), combinato con la ricerca accademica più recente: il paper Nature 2023 "A human–AI collaboration workflow for archaeological sites detection" (segmentazione semantica su immagini satellite per rilevamento di tell mesopotamici, ~80% accuratezza), il dataset DAFA-LS (looting detection in Afghanistan via Sentinel-2 time series), e il progetto EAMENA (change detection con Sentinel-2 + Google Earth Engine).

**Il prodotto colma un gap preciso**: tutti i pezzi tecnologici esistono (imagery gratuita, modelli ML, API), ma nessuno li ha assemblati in un tool usabile senza competenze di coding.

---

## 🏗️ ARCHITETTURA COMPLESSIVA

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND (React)                  │
│  Map Explorer │ Analysis Dashboard │ Report Builder  │
├─────────────────────────────────────────────────────┤
│                   API LAYER (FastAPI)                │
│  /imagery  │  /analysis  │  /projects  │  /export   │
├─────────────────────────────────────────────────────┤
│               PROCESSING ENGINE (Python)             │
│  Imagery │ Preprocessing │ ML Inference │ Scoring    │
├─────────────────────────────────────────────────────┤
│                  DATA SOURCES (Free)                 │
│ Copernicus │ USGS/CORONA │ Google Earth │ OpenTopo   │
│ Sentinel-2 │  Declassified │  Engine     │  Map      │
└─────────────────────────────────────────────────────┘
```

---

## 📦 STACK TECNOLOGICO

### Backend
- **Python 3.11+** — core language
- **FastAPI** — API REST async
- **Celery + Redis** — task queue per processing pesante
- **PostgreSQL + PostGIS** — database spaziale per siti, anomalie, progetti
- **SQLAlchemy + GeoAlchemy2** — ORM con supporto geometrie
- **Rasterio + GDAL** — lettura/manipolazione imagery geospaziale
- **PyTorch** — inference ML (segmentazione semantica)
- **scikit-image** — preprocessing immagini
- **Shapely + GeoPandas** — manipolazione geometrie vettoriali

### Frontend
- **React 18 + TypeScript**
- **Leaflet.js / react-leaflet** — mappa interattiva
- **Deck.gl** — visualizzazione tile satellitari ad alte prestazioni
- **TailwindCSS** — styling
- **Zustand** — state management leggero
- **React Query** — data fetching/caching

### Data Sources (tutti gratuiti)
- **Copernicus Data Space Ecosystem** — Sentinel-2 L2A (10m, multispettrale, dal 2015)
- **Sentinel-1 SAR** — radar, penetra nuvole e vegetazione leggera
- **USGS EarthExplorer** — CORONA declassified (1960-1972, fino a 1.8m risoluzione)
- **Google Earth Engine** — processamento cloud-based di archivi Landsat (dal 1972)
- **OpenTopography / SRTM** — dati altimetrici (DEM)
- **OpenStreetMap** — dati vettoriali di contesto

### ML Models
- **Segmentation**: U-Net / DeepLabV3+ pre-trained su satellite imagery, fine-tuned per anomaly detection archeologica
- **Change Detection**: Siamese Networks per confronto multi-temporale
- **Classification**: ResNet-50 per classificazione tile (anomalia / non anomalia)
- **Anomaly Scoring**: Ensemble di features (spettrali, morfologiche, contestuali)

---

## 🔧 MODULI DA COSTRUIRE (in ordine di priorità)

### MODULO 1: Imagery Acquisition Engine
**Priorità: CRITICA — Costruisci questo per primo**

```python
# Obiettivo: scaricare e cachare imagery satellitare per una Area of Interest (AOI)

class ImageryEngine:
    """
    Gestisce l'acquisizione di immagini satellitari da fonti gratuite.
    L'utente disegna un'AOI sulla mappa → il sistema scarica le immagini migliori.
    """
    
    def acquire_sentinel2(self, aoi_geojson, date_range, max_cloud_cover=20):
        """
        Scarica tile Sentinel-2 L2A da Copernicus Data Space Ecosystem.
        - Usa OpenEO Python client o OData API diretta
        - Filtra per copertura nuvolosa
        - Scarica bande: B02(Blue), B03(Green), B04(Red), B08(NIR), B11(SWIR), B12(SWIR2)
        - Calcola indici derivati: NDVI, NDWI, Soil-Adjusted indices
        - Cache locale con struttura: /data/sentinel2/{tile_id}/{date}/
        """
        pass
    
    def acquire_corona(self, aoi_geojson):
        """
        Cerca e scarica immagini CORONA declassificate da USGS EarthExplorer.
        - API: https://m2m.cr.usgs.gov/ (richiede registrazione gratuita)
        - Dataset: 'DECLASSII' (Declass 1 - CORONA/ARGON/LANYARD)
        - Risoluzione fino a 1.8m (KH-4B)
        - NOTA: le immagini CORONA hanno distorsioni panoramiche severe
          → serve orthorettificazione prima dell'uso
        - Priorità: KH-4B (migliore) > KH-4A > KH-4
        """
        pass
    
    def acquire_dem(self, aoi_geojson, source='srtm'):
        """
        Scarica Digital Elevation Model per l'AOI.
        - SRTM 30m: via OpenTopography API o USGS
        - Copernicus DEM 30m: via Copernicus Data Space
        - Calcola derivati: slope, aspect, hillshade, TPI (Topographic Position Index)
        - I derivati topografici sono fondamentali per rilevare tell/mound
        """
        pass
    
    def acquire_historical_landsat(self, aoi_geojson, year_range=(1972, 2025)):
        """
        Via Google Earth Engine Python API.
        - Crea compositi multitemporali (mediane stagionali)
        - Utile per change detection decennale
        - Risoluzione 30m ma archivio dal 1972
        """
        pass
```

**Dettagli implementativi critici:**

1. **Copernicus CDSE Registration**: L'utente deve registrarsi su https://dataspace.copernicus.eu (gratuito). Il sistema deve gestire OAuth2 token refresh automatico.

2. **Tile Management**: Sentinel-2 usa il grid MGRS. Il sistema deve:
   - Convertire AOI → lista tile MGRS intersecanti
   - Gestire mosaicking quando l'AOI copre più tile
   - Cachare tile già scaricati (hash: tile_id + date + bands)

3. **Band Composites & Indices**:
   ```
   True Color:      B04, B03, B02 (RGB)
   False Color NIR: B08, B04, B03 (vegetazione)
   SWIR Composite:  B12, B08, B04 (suolo/umidità)
   NDVI:            (B08 - B04) / (B08 + B04)
   NDWI:            (B03 - B08) / (B03 + B08)
   BSI:             ((B11 + B04) - (B08 + B02)) / ((B11 + B04) + (B08 + B02))
   ```
   Il BSI (Bare Soil Index) è particolarmente rilevante per archeologia.

---

### MODULO 2: Preprocessing & Feature Engineering
**Priorità: ALTA**

```python
class ArchaeoPreprocessor:
    """
    Trasforma imagery raw in feature maps ottimizzate per detection archeologica.
    Basato su letteratura: Menze & Ur 2012 (PNAS), paper Nature 2023.
    """
    
    def compute_spectral_features(self, sentinel2_bands):
        """
        Feature spettrali note per rivelare tracce archeologiche:
        
        1. CROP MARKS: differenze di crescita vegetale sopra strutture sepolte
           → NDVI anomalies in serie temporale (confronto con campo circostante)
        
        2. SOIL MARKS: differenze di colore/umidità del suolo
           → BSI (Bare Soil Index), moisture indices
           → Analisi in bande SWIR (B11, B12) che penetrano più in profondità
        
        3. SHADOW MARKS: micro-rilievi visibili con sole basso
           → Hillshade analysis dal DEM
           → Analisi immagini acquisite in orari specifici
        
        4. ANTHROSOL SIGNATURES: firma spettrale dei suoli antropici
           → Multi-temporal composites (mediana stagionale su più anni)
           → I tell/mound hanno firma spettrale distinta dal terreno naturale
        """
        pass
    
    def compute_morphological_features(self, dem_data):
        """
        Feature morfologiche dal DEM:
        - TPI (Topographic Position Index): evidenzia rilievi anomali
        - Slope variance: tell hanno profilo caratteristico
        - Curvatura: concavità/convessità anomale
        - Local Relief Model (LRM): rimuove trend regionale, evidenzia micro-rilievi
        - Sky-View Factor: utile per rilevare depressioni (fossati, canali)
        """
        pass
    
    def compute_temporal_features(self, image_time_series):
        """
        Feature multi-temporali (chiave per detection):
        - Seasonal NDVI variance: siti sepolti hanno pattern vegetativo diverso
        - Multi-year change detection: Siamese approach
        - Historical comparison: CORONA (1960s) vs Sentinel-2 (oggi)
          → Siti visibili nel 1960 e oggi scomparsi = indicatore fortissimo
        """
        pass
    
    def generate_tile_dataset(self, aoi, tile_size=256, overlap=64):
        """
        Taglia l'AOI in tile quadrati per inference ML.
        - tile_size: 256x256 pixel standard per segmentazione
        - overlap: 64px per evitare artefatti ai bordi
        - Output: cartella di tile PNG/TIFF con metadata GeoJSON
        - Ogni tile ha coordinate geografiche associate
        """
        pass
```

---

### MODULO 3: ML Detection Pipeline
**Priorità: ALTA**

```python
class ArchaeoDetector:
    """
    Pipeline ML per rilevamento anomalie archeologiche.
    
    STRATEGIA A DUE LIVELLI:
    1. RULE-BASED SCREENING (veloce, bassa soglia): 
       Filtra tile "interessanti" basandosi su indici spettrali e morfologici.
       Obiettivo: ridurre il dataset del 90% prima dell'inference ML pesante.
    
    2. ML INFERENCE (più lento, più preciso):
       Segmentazione semantica sui tile pre-filtrati.
       Modello: U-Net con backbone ResNet-50, pre-trained su ImageNet,
       fine-tuned su dataset archeologici.
    """
    
    def rule_based_screening(self, feature_stack):
        """
        Screening rapido basato su regole:
        
        CRITERI DI ANOMALIA (OR logic — basta uno):
        - NDVI locale devia >2σ dalla media regionale
        - BSI indica suolo esposto in area altrimenti vegetata
        - TPI indica rilievo anomalo (>1.5σ sopra media locale)
        - Forma circolare/rettangolare rilevata in edge detection
        - Firma spettrale compatibile con anthrosol (training da siti noti)
        
        Output: binary mask di tile candidati + confidence score
        """
        pass
    
    def ml_inference(self, candidate_tiles, model_name='unet_archeo_v1'):
        """
        Inference con modello di segmentazione semantica.
        
        MODELLI DISPONIBILI:
        
        a) PRETRAINED GENERICO:
           - U-Net con backbone ResNet-50 pre-trained su satellite imagery
           - Da: segmentation_models_pytorch library
           - Fine-tune minimo su dataset disponibili (DAFA-LS, Mesopotamia tells)
        
        b) TRANSFER LEARNING DA BUILDING DETECTION:
           - I modelli per building detection (es. SpaceNet) hanno feature
             utili per rilevare strutture antropiche → transfer learning
        
        c) ANOMALY DETECTION (UNSUPERVISED):
           - Autoencoder: addestrato su tile "normali" (no siti)
           - Anomalia = alta reconstruction error
           - Vantaggioso: non serve dataset etichettato di siti
        
        Output per ogni tile:
        - Segmentation mask (pixel-level probability)
        - Anomaly score (0-1)
        - Feature vector (per clustering/similarity search)
        """
        pass
    
    def ensemble_scoring(self, rule_scores, ml_scores, temporal_scores):
        """
        Combina scores da diversi detector in un punteggio finale.
        
        Pesi suggeriti (configurabili dall'utente):
        - Rule-based spectral:  0.2
        - Rule-based morphological: 0.2
        - ML segmentation: 0.35
        - Temporal anomaly: 0.25
        
        Output: ranked list di candidate sites con:
        - coordinate centroide
        - bounding box
        - confidence score composito
        - breakdown per componente
        - thumbnail con heatmap overlay
        """
        pass
```

**Nota sul training dei modelli:**

Il sistema deve funzionare OUT-OF-THE-BOX con modelli pre-trained generici. Il fine-tuning è opzionale e progressivo:

1. **Giorno 1**: U-Net pre-trained su satellite imagery + rule-based screening → risultati basici ma funzionanti
2. **Settimana 1**: Fine-tune su DAFA-LS dataset (open access, 675 siti afghani)
3. **Mese 1**: Community contribuisce annotazioni → training incrementale
4. **Long-term**: Modello specifico per regione/periodo storico

---

### MODULO 4: Map Explorer (Frontend)
**Priorità: ALTA**

```typescript
/**
 * Interfaccia mappa interattiva — il cuore dell'esperienza utente.
 * L'archeologo deve poter:
 * 1. Navigare sulla mappa e selezionare un'AOI
 * 2. Vedere layer satellitari sovrapposti
 * 3. Lanciare analisi con un click
 * 4. Esplorare risultati visivamente
 * 5. Annotare e classificare findings
 */

// COMPONENTI PRINCIPALI:

// A) MapCanvas — Leaflet/Deck.gl
// - Base layers: OSM, Satellite (Bing/Google), Terrain
// - Overlay layers (toggle on/off):
//   · Sentinel-2 True Color
//   · Sentinel-2 False Color (NIR)
//   · NDVI heatmap
//   · BSI (Bare Soil) heatmap
//   · DEM hillshade
//   · CORONA historical (dove disponibile)
//   · Anomaly detection heatmap (risultati ML)
//   · Known archaeological sites (da OpenStreetMap + database pubblici)

// B) AOI Selector
// - Draw rectangle/polygon/circle sull'area da analizzare
// - Oppure: inserisci coordinate / nome località
// - Mostra: stima dimensione, n° tile Sentinel-2, tempo analisi stimato

// C) Analysis Panel
// - Seleziona date range
// - Seleziona fonti dati (Sentinel-2, CORONA, DEM...)
// - Configura parametri detection (soglie, pesi ensemble)
// - Pulsante "Avvia Analisi" → mostra progress bar
// - Al completamento: zoom sui risultati, mostra ranked candidates

// D) Results Inspector
// - Click su candidato → popup con:
//   · Thumbnail multi-layer (True Color, False Color, NDVI, DEM)
//   · Anomaly score breakdown
//   · Comparison slider: prima/dopo, storico/attuale
//   · Distanza da siti noti più vicini
//   · Contesto geologico/geomorfologico
//   · Bottoni: "Conferma", "Rigetta", "Incerto" (feedback per training)

// E) Timeline Slider
// - Scrolla nel tempo sulle immagini disponibili
// - Animazione multi-temporale (stagioni, anni)
// - Evidenzia quando un'anomalia appare/scompare
```

---

### MODULO 5: Project & Collaboration System
**Priorità: MEDIA**

```python
class ProjectManager:
    """
    Gestione progetti di ricerca collaborativi.
    Un archeologo crea un "progetto" legato a una regione/periodo.
    """
    
    # Database Models (PostGIS):
    
    # Project: {name, description, aoi_geojson, owner, team, created_at}
    # Analysis: {project_id, params, status, results_path, created_at}
    # Candidate: {analysis_id, geom_point, geom_polygon, score, 
    #             status: [new, confirmed, rejected, field_verified],
    #             classification: [tell, mound, wall, canal, road, unknown],
    #             notes, photos[], verified_by}
    # Annotation: {candidate_id, user_id, label, confidence, timestamp}
    
    def create_project(self, name, aoi, description):
        """Nuovo progetto di ricerca per una regione."""
        pass
    
    def run_analysis(self, project_id, params):
        """Lancia pipeline di analisi (Celery task)."""
        pass
    
    def export_candidates(self, project_id, format='geojson'):
        """
        Esporta candidati per uso in:
        - QGIS (.geojson, .gpkg, .shp)
        - Google Earth (.kml)
        - Report PDF con mappe e thumbnails
        - CSV per analisi statistica
        """
        pass
    
    def import_known_sites(self, project_id, file):
        """
        Importa siti archeologici noti (da database pubblici o survey).
        Usati come:
        1. Training data per ML
        2. Riferimento per escludere falsi positivi (sito già noto)
        3. Validazione: il sistema li rileva? (benchmark)
        """
        pass
```

---

### MODULO 6: Report Generator
**Priorità: MEDIA**

```python
class ReportGenerator:
    """
    Genera report professionali per presentazione a istituzioni,
    pubblicazione, o pianificazione survey sul campo.
    """
    
    def generate_field_survey_plan(self, project_id, top_n=20):
        """
        Per ogni top-N candidato:
        - Mappa di localizzazione con coordinate precise
        - Indicazioni di accesso (strade, sentieri più vicini)
        - Multi-layer imagery comparativa
        - Stagione ottimale per survey (basata su crop mark visibility)
        - Attrezzatura suggerita per verifica
        - Priorità (basata su score + fattibilità accesso)
        
        Output: PDF navigabile + pacchetto dati per tablet/GPS
        """
        pass
    
    def generate_academic_report(self, project_id):
        """
        Report stile paper scientifico:
        - Metodologia utilizzata
        - Parametri di analisi
        - Statistiche risultati
        - Mappe tematiche
        - Confronto con letteratura
        
        Output: HTML interattivo + PDF
        """
        pass
```

---

## 🗂️ STRUTTURA DEL PROGETTO

```
archaeo-sentinel/
├── README.md
├── LICENSE (MIT o Apache 2.0)
├── docker-compose.yml
├── .env.example
│
├── backend/
│   ├── main.py                    # FastAPI app
│   ├── config.py                  # Settings & env vars
│   ├── requirements.txt
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── imagery.py         # endpoints acquisizione imagery
│   │   │   ├── analysis.py        # endpoints lancio/status analisi
│   │   │   ├── projects.py        # CRUD progetti
│   │   │   ├── candidates.py      # gestione candidati/annotazioni
│   │   │   └── export.py          # download report/dati
│   │   └── deps.py                # dependencies (auth, db)
│   │
│   ├── core/
│   │   ├── imagery/
│   │   │   ├── sentinel2.py       # Copernicus CDSE client
│   │   │   ├── corona.py          # USGS EarthExplorer client
│   │   │   ├── dem.py             # DEM acquisition
│   │   │   ├── gee.py             # Google Earth Engine client
│   │   │   └── cache.py           # tile cache manager
│   │   │
│   │   ├── preprocessing/
│   │   │   ├── spectral.py        # indici spettrali (NDVI, BSI, etc.)
│   │   │   ├── morphological.py   # features DEM-based
│   │   │   ├── temporal.py        # features multi-temporali
│   │   │   └── tiling.py          # AOI → tile grid
│   │   │
│   │   ├── detection/
│   │   │   ├── rule_based.py      # screening basato su regole
│   │   │   ├── ml_inference.py    # inference modelli ML
│   │   │   ├── ensemble.py        # scoring composito
│   │   │   └── postprocessing.py  # clustering, dedup, ranking
│   │   │
│   │   └── reporting/
│   │       ├── field_plan.py      # survey plan generator
│   │       ├── academic.py        # report accademico
│   │       └── templates/         # Jinja2 templates HTML/PDF
│   │
│   ├── models/
│   │   ├── database.py            # SQLAlchemy + PostGIS models
│   │   └── schemas.py             # Pydantic schemas
│   │
│   ├── ml/
│   │   ├── architectures/
│   │   │   ├── unet.py            # U-Net per segmentazione
│   │   │   ├── siamese.py         # Change detection
│   │   │   └── autoencoder.py     # Anomaly detection unsupervised
│   │   ├── training/
│   │   │   ├── train.py           # training loop
│   │   │   ├── datasets.py        # PyTorch datasets
│   │   │   └── augmentation.py    # data augmentation geospaziale
│   │   └── pretrained/            # modelli pre-trained (.pth)
│   │
│   └── tasks/
│       ├── celery_app.py          # Celery config
│       └── analysis_tasks.py      # task asincroni di analisi
│
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── MapCanvas.tsx      # mappa Leaflet/Deck.gl
│   │   │   ├── AOISelector.tsx    # disegno area di interesse
│   │   │   ├── LayerPanel.tsx     # toggle layer satellitari
│   │   │   ├── AnalysisPanel.tsx  # configurazione analisi
│   │   │   ├── ResultsInspector.tsx # esplorazione candidati
│   │   │   ├── TimelineSlider.tsx # navigazione temporale
│   │   │   ├── ComparisonSlider.tsx # before/after imagery
│   │   │   └── CandidateCard.tsx  # card singolo candidato
│   │   ├── hooks/
│   │   │   ├── useImagery.ts      # fetch imagery layers
│   │   │   ├── useAnalysis.ts     # lancio/polling analisi
│   │   │   └── useProject.ts      # gestione progetto
│   │   ├── stores/
│   │   │   └── appStore.ts        # Zustand store
│   │   └── utils/
│   │       ├── geo.ts             # utility geospaziali
│   │       └── tiles.ts           # tile math (MGRS, etc.)
│   └── public/
│
├── data/
│   ├── known_sites/               # database siti noti (training/validation)
│   │   ├── mesopotamia_tells.geojson
│   │   ├── dafa_ls_afghanistan.csv
│   │   └── eamena_north_africa.geojson
│   └── models/                    # modelli ML pre-trained
│
├── notebooks/                     # Jupyter per esplorazione/demo
│   ├── 01_sentinel2_acquisition.ipynb
│   ├── 02_spectral_analysis.ipynb
│   ├── 03_anomaly_detection.ipynb
│   └── 04_model_training.ipynb
│
└── docs/
    ├── installation.md
    ├── user_guide.md
    ├── api_reference.md
    └── contributing.md
```

---

## 🚀 ROADMAP DI IMPLEMENTAZIONE

### FASE 1: MVP — "Il Cercatore" (settimane 1-3)
**Obiettivo: funziona end-to-end su un'area piccola**

1. Backend FastAPI minimal con 3 endpoint: upload AOI, get imagery, get analysis
2. Sentinel-2 acquisition via Copernicus OData API (una data, true color + NDVI)
3. Rule-based screening solo (no ML): NDVI anomaly + BSI thresholding
4. Frontend: mappa Leaflet, draw AOI, mostra heatmap risultati
5. Output: GeoJSON dei candidati scaricabile

**Tecnicamente, il minimo per avere qualcosa di dimostrabile.**

### FASE 2: Multi-Source — "L'Esploratore" (settimane 4-6)
1. Aggiungere DEM (SRTM) + features morfologiche
2. Multi-temporal: mediana stagionale su 2+ anni
3. CORONA integration (dove disponibile)
4. Primo modello ML: U-Net anomaly detection (autoencoder, unsupervised)
5. Frontend: layer toggle, timeline slider, comparison view
6. Export: GeoJSON, KML, report HTML basico

### FASE 3: Intelligence — "L'Oracolo" (settimane 7-10)
1. ML training pipeline completo (fine-tune su DAFA-LS / tell dataset)
2. Ensemble scoring (rule + ML + temporal)
3. Known sites database integration
4. Collaborative annotations (multi-user)
5. Report generator professionale (PDF con mappe)
6. Docker deployment completo

### FASE 4: Community — "La Rete" (settimane 11+)
1. Public model hub (condivisione modelli community-trained)
2. Crowdsourced validation (like Zooniverse model)
3. Integration con QGIS plugin
4. Google Earth Engine backend per processing heavy
5. Mobile app per field verification (GPS + foto + confirm)

---

## ⚙️ CONFIGURAZIONE INIZIALE

```yaml
# docker-compose.yml
services:
  db:
    image: postgis/postgis:16-3.4
    environment:
      POSTGRES_DB: archaeo_sentinel
      POSTGRES_USER: archeo
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://archeo:${DB_PASSWORD}@db:5432/archaeo_sentinel
      REDIS_URL: redis://redis:6379
      COPERNICUS_USER: ${COPERNICUS_USER}
      COPERNICUS_PASSWORD: ${COPERNICUS_PASSWORD}
      USGS_USER: ${USGS_USER}
      USGS_PASSWORD: ${USGS_PASSWORD}
    volumes:
      - ./data:/app/data
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
  
  worker:
    build: ./backend
    command: celery -A tasks.celery_app worker -l info
    environment:
      DATABASE_URL: postgresql://archeo:${DB_PASSWORD}@db:5432/archaeo_sentinel
      REDIS_URL: redis://redis:6379
    volumes:
      - ./data:/app/data
    depends_on:
      - db
      - redis
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  pgdata:
```

```env
# .env.example
DB_PASSWORD=your_secure_password
COPERNICUS_USER=your_copernicus_email
COPERNICUS_PASSWORD=your_copernicus_password
USGS_USER=your_usgs_username
USGS_PASSWORD=your_usgs_password
# Opzionale:
GEE_SERVICE_ACCOUNT=path/to/gee-credentials.json
```

---

## 📚 RISORSE & RIFERIMENTI CHIAVE

### Paper scientifici fondamentali (da cui estrarre logica):
1. **Nature 2023**: "A human–AI collaboration workflow for archaeological sites detection" — U-Net su Bing Maps imagery per tell in Mesopotamia, ~80% accuracy
2. **PNAS 2020**: "Automated detection of archaeological mounds using ML classification of multisensor and multitemporal satellite data" — Random Forest su Sentinel-1/2 + DEM in Pakistan
3. **MDPI Remote Sensing 2020**: "Detecting Change at Archaeological Sites in North Africa Using Open-Source Satellite Imagery" — Workflow EAMENA con Sentinel-2 + GEE, 85-91% accuracy
4. **arXiv 2024**: "Detecting Looted Archaeological Sites from Satellite Image Time Series" — Dataset DAFA-LS, 675 siti afghani, Sentinel-2 time series

### Dataset open access per training:
1. **DAFA-LS**: 55,480 immagini, 675 siti afghani, 2016-2023 — https://github.com/ (cercalo, è open)
2. **Mesopotamian Tells**: dataset dal paper Nature 2023 — ~5000 siti annotati
3. **SpaceNet**: dataset generici building/road detection — utili per transfer learning

### API Documentation:
1. **Copernicus CDSE**: https://documentation.dataspace.copernicus.eu/APIs.html
2. **USGS M2M API**: https://m2m.cr.usgs.gov/
3. **Google Earth Engine**: https://developers.google.com/earth-engine
4. **OpenTopography**: https://opentopography.org/developers

### Librerie Python essenziali:
```
rasterio>=1.3          # lettura/scrittura raster geospaziali
gdal>=3.6              # processing geospaziale heavy
geopandas>=0.14        # dataframes geospaziali
shapely>=2.0           # geometrie
pyproj>=3.6            # proiezioni coordinate
torch>=2.0             # ML
segmentation-models-pytorch>=0.3  # U-Net et al pre-built
scikit-image>=0.21     # image processing
opencv-python>=4.8     # computer vision
fastapi>=0.100         # API
sqlalchemy>=2.0        # ORM
geoalchemy2>=0.14      # PostGIS support
celery>=5.3            # task queue
openeo>=0.28           # Copernicus OpenEO client
sentinelhub>=3.9       # Sentinel Hub API
```

---

## 🎯 PRINCIPI DI DESIGN

1. **Archeologo-first**: L'utente target non sa programmare. Ogni feature deve essere accessibile da UI.

2. **Progressive disclosure**: Mostra risultati semplici (heatmap) di default, dettagli tecnici su richiesta.

3. **Human-in-the-loop**: L'AI propone, l'umano decide. Ogni candidato deve essere validato. Il feedback migliora il modello.

4. **Offline-capable**: Il frontend deve funzionare con dati pre-scaricati. Gli archeologi spesso sono sul campo senza internet.

5. **Reproducibilità**: Ogni analisi deve essere ripetibile. Log completi di parametri e versioni.

6. **Open everything**: Codice MIT, dati CC-BY-SA, modelli open-weight. La comunità archeologica è piccola e collaborativa — l'openness è il vantaggio competitivo.

---

## 💡 NOTA STRATEGICA PER L'AI CODER

Quando costruisci questo progetto:

- **Inizia dal MODULO 1 (Imagery) + MODULO 4 (Map Frontend) minimal**. Un utente deve poter disegnare un rettangolo su una mappa e vedere un'immagine Sentinel-2 in meno di 2 minuti. Tutto il resto è iterazione.

- **Il rule-based screening (MODULO 3, prima parte) è più importante del ML** nella fase iniziale. NDVI anomaly + BSI + TPI funzionano sorprendentemente bene e non richiedono training data.

- **Non ottimizzare prematuramente il ML**. Un autoencoder basic addestrato su tile "normali" della stessa regione è un ottimo primo passo. Fine-tuning su dataset archeologici viene dopo.

- **Il comparison slider (oggi vs CORONA 1960s) è la killer feature** dal punto di vista UX. Un sito visibile nel 1960 e scomparso oggi sotto un campo arato è quasi certamente archeologico.

- **Testa su regioni ben documentate**: Mesopotamia (migliaia di tell noti), Egitto (EAMENA database), Afghanistan (DAFA-LS). Se il sistema rileva siti noti, funziona.

---

*Questo prompt è stato progettato per essere utilizzato con qualsiasi AI coding assistant (Claude Code, Cursor, Windsurf, Copilot, Aider) per costruire il prodotto in modo incrementale.*

*Versione: 1.0 — Marzo 2026*
*Autore: Mirko Tornani*
*Licenza: CC-BY-SA 4.0*
