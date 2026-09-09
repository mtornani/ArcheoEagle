from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
import numpy as np
from core.imagery.sentinel2 import copernicus_client
from core.imagery.srtm import srtm_client
from core.detection.rule_based import detect_anomalies
from core.layers import array_to_colormap_png_fast
from core.hydro.paleorivers import (
    bbox_from_geojson, bbox_to_aoi, corridor_bbox, load_network,
    nodes_in_aoi, rivers_in_aoi,
)
from core.ledger.hypotheses import build_ledger
from core.ledger.blind import make_blind_pack

router = APIRouter()


class AnalysisRequest(BaseModel):
    aoi_geojson: Dict[str, Any]
    layer_id: str = "sentinel-2"
    max_cloud_cover: int = 20
    include_dem: bool = True
    include_spectral: bool = False


class WalkRequest(BaseModel):
    corridor_id: str
    include_dem: bool = True
    include_spectral: bool = False


@router.get("/network")
def hydro_network():
    """Schematic Sahara paleodrainage for the map. Not survey-grade."""
    net = load_network()
    return net


@router.post("/walk")
def walk_corridor(request: WalkRequest):
    """
    Default path. Human picks a river, not a shape.
    Spectral off: crop-marks are a 2026 prior.
    """
    try:
        bbox = corridor_bbox(request.corridor_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _execute(
        aoi=bbox_to_aoi(bbox),
        bbox=bbox,
        include_dem=request.include_dem,
        include_spectral=request.include_spectral,
        method="corridor-walk",
        corridor_id=request.corridor_id,
    )


@router.post("/run")
def run_analysis(request: AnalysisRequest):
    """Manual AOI. Bias enters here — used only to restrict a corridor."""
    bbox = bbox_from_geojson(request.aoi_geojson)
    return _execute(
        aoi=request.aoi_geojson,
        bbox=bbox,
        include_dem=request.include_dem,
        include_spectral=request.include_spectral,
        method="aoi-restrict",
        corridor_id=None,
    )


def _execute(*, aoi, bbox, include_dem, include_spectral, method, corridor_id):
    hydro_nodes = nodes_in_aoi(bbox)
    rivers = rivers_in_aoi(bbox)

    bands, _bbox_img = copernicus_client.acquire_and_download(aoi, 20)
    if _bbox_img and method == "aoi-restrict":
        bbox = _bbox_img

    dem = None
    if include_dem:
        dem = srtm_client.fetch_dem(bbox, target_shape=bands["B04"].shape)

    results = detect_anomalies(bands, dem=dem)
    if not results.get("success", False):
        return {"message": "Errore nell'analisi", "error": results.get("error", "Unknown")}

    spectral_features = _spectral_features(bands, results, bbox) if include_spectral else []

    ranking = build_ledger(hydro_nodes, spectral_features)
    blind = make_blind_pack(ranking)
    features = [_feature_from_row(row) for row in ranking]

    layers = {}
    if include_spectral:
        ndvi_map = results.get("ndvi_map")
        bsi_map = results.get("bsi_map")
        if ndvi_map is not None:
            layers["ndvi"] = array_to_colormap_png_fast(ndvi_map, cmap="ndvi", vmin=-0.5, vmax=0.9, alpha=0.6)
        if bsi_map is not None:
            layers["bsi"] = array_to_colormap_png_fast(bsi_map, cmap="bsi", vmin=-0.5, vmax=0.6, alpha=0.6)
    if dem is not None:
        layers["dem"] = array_to_colormap_png_fast(dem, cmap="dem", alpha=0.5)
        slope_map = results.get("slope_map")
        if slope_map is not None:
            layers["slope"] = array_to_colormap_png_fast(slope_map, cmap="slope", vmin=0, vmax=30, alpha=0.5)

    stats = {
        k: v for k, v in results.items()
        if k not in ("ndvi_map", "bsi_map", "slope_map", "tpi_map", "dem")
    }

    return {
        "message": "Tappe sul fiume. Non è una prova.",
        "method": method,
        "corridor_id": corridor_id,
        "candidates": {"type": "FeatureCollection", "features": features},
        "ranking": ranking,
        "blind": blind,
        "rivers": rivers,
        "stats": {
            **stats,
            "candidates_found": len(features),
            "hydro_nodes": len(hydro_nodes),
            "dem_enabled": dem is not None,
            "spectral_enabled": include_spectral,
            "off_network": len(hydro_nodes) == 0,
        },
        "layers": layers,
        "bbox": bbox,
    }


def _spectral_features(bands, results, bbox):
    try:
        from skimage.measure import label, regionprops
    except ImportError:
        return []

    nir = bands["B08"]
    swir = bands["B11"]
    combined = np.logical_and(
        nir < np.mean(nir) * 0.65,
        swir > np.mean(swir) * 1.35,
    )
    labeled = label(combined)
    props = regionprops(labeled)

    total_pixels = bands["B04"].size
    anomaly_ratio = results.get("anomaly_pixels_detected", 0) / max(total_pixels, 1)
    base_score = min(0.98, 0.45 + anomaly_ratio * 3.2)
    if results.get("ndvi_anomaly_mean") is not None:
        base_score = min(0.98, base_score + abs(results["ndvi_anomaly_mean"]) * 0.8)

    lon_min, lat_min, lon_max, lat_max = bbox
    h, w = bands["B04"].shape
    features = []
    rng = np.random.default_rng(7)
    for prop in sorted(props, key=lambda p: p.area, reverse=True)[:5]:
        cy, cx = prop.centroid
        lon = lon_min + (cx / w) * (lon_max - lon_min)
        lat = lat_max - (cy / h) * (lat_max - lat_min)
        size_factor = min(1.0, prop.area / 500)
        score = round(float(base_score * (0.85 + size_factor * 0.15) + rng.uniform(-0.03, 0.03)), 2)
        score = max(0.10, min(0.99, score))
        eccentricity = float(getattr(prop, "eccentricity", 0.5) or 0.5)
        if eccentricity > 0.85:
            anom_type, anom_label = "linear_feature", "Firma lineare (canale/strada)"
        elif prop.area > 2000:
            anom_type, anom_label = "large_structure", "Firma estesa"
        else:
            anom_type, anom_label = "buried_structure", "Firma sepolta"
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
            "properties": {
                "score": score,
                "type": anom_type,
                "label": anom_label,
                "pixels": int(prop.area),
                "area_m2": int(prop.area * 100),
                "eccentricity": round(eccentricity, 3),
                "reasons": results.get("reasons", []),
            },
        })
    return features


def _feature_from_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [row["lon"], row["lat"]]},
        "properties": {
            "label": row["label"],
            "rank": row["rank"],
            "residual": row["residual"],
            "hydro_score": row["hydro_score"],
            "spectral_score": row.get("spectral_score"),
            "node_type": row.get("node_type"),
            "basin": row.get("basin"),
            "source": row.get("source"),
            "pro": row.get("pro"),
            "contro": row.get("contro"),
            "kill_shot": row.get("kill_shot"),
            "plato": row.get("plato"),
        },
    }
