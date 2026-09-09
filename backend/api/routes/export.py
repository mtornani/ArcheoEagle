from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, List
from datetime import datetime, timezone

from core.ledger.blind import make_blind_pack, verify_hash

router = APIRouter()


class ExportRequest(BaseModel):
    candidates: List[Dict[str, Any]]
    project_name: str = "archeoeagle_export"


class DossierRequest(BaseModel):
    ranking: List[Dict[str, Any]]
    project_name: str = "archeoeagle"
    include_coords: bool = True


@router.post("/geojson")
def export_geojson(request: ExportRequest):
    feature_collection = {
        "type": "FeatureCollection",
        "features": request.candidates,
        "metadata": {
            "project": request.project_name,
            "export_date": datetime.now(timezone.utc).isoformat(),
            "generator": "ArcheoEagle",
            "warning": "Coordinate nel file locale. Non è un pack cieco.",
        },
    }
    headers = {
        "Content-Disposition": f"attachment; filename={request.project_name}.geojson"
    }
    return JSONResponse(content=feature_collection, headers=headers)


@router.post("/dossier")
def export_dossier(request: DossierRequest):
    """Full local dossier. Has coordinates. Do not publish."""
    body = {
        "project": request.project_name,
        "kind": "operator-dossier",
        "export_date": datetime.now(timezone.utc).isoformat(),
        "ranking": request.ranking if request.include_coords else make_blind_pack(request.ranking)["ranking"],
        "warning": "Dossier operatore. Coordinate private. Gli squali non lo vedono.",
    }
    headers = {
        "Content-Disposition": f"attachment; filename={request.project_name}_dossier.json"
    }
    return JSONResponse(content=body, headers=headers)


@router.post("/blind")
def export_blind(request: DossierRequest):
    """Public pack: labels + rubric + hash. No coordinates."""
    pack = make_blind_pack(request.ranking)
    pack["project"] = request.project_name
    pack["kind"] = "blind-pack"
    headers = {
        "Content-Disposition": f"attachment; filename={request.project_name}_blind.json"
    }
    return JSONResponse(content=pack, headers=headers)


@router.post("/verify")
def verify_blind(pack: Dict[str, Any]):
    return {"ok": verify_hash(pack), "hash": pack.get("hash")}
