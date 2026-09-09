from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict, List
from core.imagery.sentinel2 import copernicus_client, get_bbox_from_geojson

router = APIRouter()

class AOIRequest(BaseModel):
    geojson: Dict[str, Any]
    date_range: List[str] = None
    max_cloud_cover: int = 20

@router.post("/acquire/sentinel2")
def acquire_sentinel2(request: AOIRequest):
    """
    Acquires Sentinel-2 imagery for the given AOI.
    Returns metadata of the matched tiles.
    """
    bbox = get_bbox_from_geojson(request.geojson)
    results = copernicus_client.search_sentinel2(bbox, max_cloud_cover=request.max_cloud_cover)
    
    return {
        "message": "Sentinel-2 search completed", 
        "aoi_bbox": bbox,
        "results": results
    }
