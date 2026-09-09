import sys
import io
# Fix Windows cp1252 encoding for print() statements
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import imagery, analysis, export
from api.routes import projects

app = FastAPI(title="ArcheoEagle API", version="1.2.0")

# LAN / phone on the same network (field mode)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(imagery.router, prefix="/api/v1/imagery", tags=["imagery"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(export.router, prefix="/api/v1/export", tags=["export"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])


@app.get("/")
def read_root():
    return {
        "message": "ArcheoEagle API v1.2",
        "method": "hydro-first",
        "features": [
            "paleorivers",
            "uncertainty-ledger",
            "plato-two-sided",
            "blind-pack-sha256",
            "NDVI-BSI-DEM",
        ],
    }


@app.get("/health")
def health():
    return {"ok": True}
