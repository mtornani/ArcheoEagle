"""Measure paleolake shoreline from a DEM. Schematic geojson is not a measurement.

SRTM/Copernicus see the *modern* surface. Buried AHP channels (Tamanrasset,
Sahabi) need L-band radar — this module will not fake them. Mega-Chad ~320 m
highstand is a topographic bench. That is the first from-home measurement.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from core.hydro.paleorivers import haversine_km, load_network

BBox = Sequence[float]
LngLat = Tuple[float, float]

MEGA_CHAD_HIGHSTAND_M = 320.0
MEGA_CHAD_IDS = {"megachad", "mega_chad"}


def copernicus_cog_url(lat_s: int, lon_s: int) -> str:
    ns = "N" if lat_s >= 0 else "S"
    ew = "E" if lon_s >= 0 else "W"
    name = f"Copernicus_DSM_COG_10_{ns}{abs(lat_s):02d}_00_{ew}{abs(lon_s):03d}_00_DEM"
    return f"https://copernicus-dem-30m.s3.amazonaws.com/{name}/{name}.tif"


def _cache_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "dem"


def _rowcol_to_ll(row: float, col: float, bbox: BBox, shape: Tuple[int, int]) -> LngLat:
    h, w = shape
    lon0, lat0, lon1, lat1 = bbox
    lon = lon0 + (col / max(w - 1, 1)) * (lon1 - lon0)
    lat = lat1 - (row / max(h - 1, 1)) * (lat1 - lat0)
    return float(lon), float(lat)


def shoreline_from_dem(dem: np.ndarray, bbox: BBox, level_m: float) -> List[List[LngLat]]:
    """Contour polylines at level_m. Numpy only — no skimage, no invented terrain."""
    if dem.size == 0 or not np.isfinite(dem).any():
        return []
    filled = np.where(np.isfinite(dem), dem, np.nanmedian(dem))
    lo, hi = float(np.nanmin(filled)), float(np.nanmax(filled))
    if not (lo < level_m < hi):
        return []
    left, right = filled[:, :-1], filled[:, 1:]
    mask_h = np.isfinite(left) & np.isfinite(right) & (left != right)
    mask_h &= ((left - level_m) * (right - level_m) <= 0)
    rh, ch = np.nonzero(mask_h)
    th = (level_m - left[mask_h]) / (right[mask_h] - left[mask_h])

    top, bot = filled[:-1, :], filled[1:, :]
    mask_v = np.isfinite(top) & np.isfinite(bot) & (top != bot)
    mask_v &= ((top - level_m) * (bot - level_m) <= 0)
    rv, cv = np.nonzero(mask_v)
    tv = (level_m - top[mask_v]) / (bot[mask_v] - top[mask_v])

    pts: List[LngLat] = []
    shape = filled.shape
    for r, c, t in zip(rh, ch, th):
        pts.append(_rowcol_to_ll(float(r), float(c) + float(t), bbox, shape))
    for r, c, t in zip(rv, cv, tv):
        pts.append(_rowcol_to_ll(float(r) + float(t), float(c), bbox, shape))
    if len(pts) < 8:
        return []
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    ordered = sorted(pts, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
    ordered.append(ordered[0])
    return [ordered]


def _sample_along(pts: List[LngLat], step_km: float) -> List[LngLat]:
    if len(pts) < 2:
        return list(pts)
    out: List[LngLat] = [pts[0]]
    acc = 0.0
    for i in range(1, len(pts)):
        acc += haversine_km(pts[i - 1], pts[i])
        if acc >= step_km:
            out.append(pts[i])
            acc = 0.0
    if pts[-1] != out[-1]:
        out.append(pts[-1])
    return out


def nodes_from_contour(
    lines: List[List[LngLat]],
    *,
    level_m: float,
    node_type: str,
    basin: str,
    river_id: str,
    river_name: str,
    step_km: float = 70.0,
) -> List[Dict[str, Any]]:
    seen: List[LngLat] = []
    nodes: List[Dict[str, Any]] = []

    def _near(pt: LngLat) -> bool:
        return any(haversine_km(pt, s) < 18.0 for s in seen)

    for line in lines:
        for pt in _sample_along(line, step_km):
            if _near(pt):
                continue
            seen.append(pt)
            nodes.append({
                "lon": round(pt[0], 5),
                "lat": round(pt[1], 5),
                "node_type": node_type,
                "hydro_score": 0.88,
                "river_id": river_id,
                "river_name": river_name,
                "basin": basin,
                "kind": "paleolake",
                "source": "dem-contour",
                "grade": "dem-contour",
                "level_m": level_m,
            })
    return nodes


def vs_schematic_km(nodes: List[Dict[str, Any]], schematic_id: str = "mega_chad_shore") -> None:
    net = load_network()
    shore: List[LngLat] = []
    for feat in net.get("features") or []:
        if (feat.get("properties") or {}).get("id") == schematic_id:
            geom = feat.get("geometry") or {}
            for c in geom.get("coordinates") or []:
                shore.append((float(c[0]), float(c[1])))
    if not shore:
        return
    for node in nodes:
        d = min(haversine_km((node["lon"], node["lat"]), p) for p in shore)
        node["vs_schematic_km"] = round(d, 1)


def _ne_tile(bbox: BBox) -> Tuple[int, int]:
    lat = int(math.floor(min(float(bbox[3]) - 1e-6, 89.0)))
    lon = int(math.floor(min(float(bbox[2]) - 1e-6, 179.0)))
    return lat, lon


def fetch_copernicus_tile(lat_s: int, lon_s: int, timeout: int = 90) -> Optional[Tuple[np.ndarray, List[float], str]]:
    """One 1° GLO-30 COG. None if the network or rasterio fails. Never invents terrain."""
    import requests

    url = copernicus_cog_url(lat_s, lon_s)
    cache = _cache_dir()
    cache.mkdir(parents=True, exist_ok=True)
    name = url.rsplit("/", 1)[-1]
    dest = cache / name
    try:
        if not dest.exists() or dest.stat().st_size < 1000:
            resp = requests.get(url, timeout=timeout, stream=True)
            resp.raise_for_status()
            tmp = dest.with_suffix(".part")
            with tmp.open("wb") as f:
                for chunk in resp.iter_content(1 << 16):
                    f.write(chunk)
            tmp.replace(dest)
        import rasterio
        with rasterio.open(dest) as src:
            dem = src.read(1).astype(np.float64)
            nodata = src.nodata
            if nodata is not None:
                dem[dem == nodata] = np.nan
            b = src.bounds
            bbox = [float(b.left), float(b.bottom), float(b.right), float(b.top)]
        return dem, bbox, url
    except Exception:
        return None


def measure_highstand(bbox: BBox, level_m: float = MEGA_CHAD_HIGHSTAND_M) -> Dict[str, Any]:
    """Attempt a real 320 m shoreline on the NE 1° tile of bbox. Honest empty if DEM missing."""
    lat_s, lon_s = _ne_tile(bbox)
    fetched = fetch_copernicus_tile(lat_s, lon_s)
    if fetched is None:
        return {
            "nodes": [],
            "contour": {"type": "FeatureCollection", "features": []},
            "dem": {"real": False, "reason": "copernicus-dem-unavailable", "tile": [lat_s, lon_s]},
        }
    dem, tile_bbox, url = fetched
    lines = shoreline_from_dem(dem, tile_bbox, level_m)
    nodes = nodes_from_contour(
        lines,
        level_m=level_m,
        node_type="paleolake_shore",
        basin="mega_chad",
        river_id="mega_chad_highstand",
        river_name="Mega-Chad highstand (DEM)",
        step_km=70.0,
    )
    vs_schematic_km(nodes)
    contour = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"id": "mega_chad_dem_contour", "grade": "dem-contour", "level_m": level_m},
                "geometry": {"type": "LineString", "coordinates": [[p[0], p[1]] for p in line]},
            }
            for line in lines
        ],
    }
    return {
        "nodes": nodes,
        "contour": contour,
        "dem": {
            "real": True,
            "source": "copernicus-glo30",
            "url": url,
            "tile": [lat_s, lon_s],
            "bbox": tile_bbox,
            "zmin": float(np.nanmin(dem)),
            "zmax": float(np.nanmax(dem)),
            "level_m": level_m,
        },
    }


def trap_richat() -> Dict[str, Any]:
    """The telephone-game attractor. A real circular landform. Not a city. Not a ranking."""
    return {
        "message": (
            "Richat è una struttura circolare reale nel Sahara. Non è una città. "
            "È il bacino attrattore della pareidolia concettuale: il telefono senza fili "
            "ha bisogno di anelli, e la Terra ne ha uno fotografabile. "
            "Questo tool rifiuta di classificarla come tappa. Vai su un fiume."
        ),
        "method": "trap",
        "trap_id": "richat",
        "corridor_id": "richat",
        "candidates": {"type": "FeatureCollection", "features": []},
        "ranking": [],
        "blind": {
            "algorithm": "sha256",
            "hash": "",
            "timestamp": "",
            "ranking": [],
            "note": "Nessun pack. La trappola non si classifica.",
        },
        "rivers": {"type": "FeatureCollection", "features": []},
        "stats": {
            "grade": "trap",
            "warning": "Pareidolia visiva + telefono senza fili. Non è evidenza.",
            "candidates_found": 0,
            "hydro_nodes": 0,
            "dem_enabled": False,
            "spectral_enabled": False,
        },
        "layers": {},
        "bbox": [-12.0, 20.5, -10.5, 21.7],
    }
