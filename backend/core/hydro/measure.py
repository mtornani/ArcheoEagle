"""Measure paleolake shoreline from a DEM. Schematic geojson is not a measurement.

SRTM/Copernicus see the *modern* surface. Buried AHP channels (Tamanrasset,
Sahabi) need L-band radar — this module will not fake them. Mega-Chad ~320 m
highstand is a topographic bench. That is the first from-home measurement.
"""
from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from core.hydro.paleorivers import haversine_km, load_network

BBox = Sequence[float]
LngLat = Tuple[float, float]
RC = Tuple[float, float]

MEGA_CHAD_HIGHSTAND_M = 320.0
MEGA_CHAD_IDS = {"megachad", "mega_chad"}
# One request-response cycle, not a batch job. More tiles = more honest coverage
# but each is a network fetch; cap so /walk still answers. Truncation is reported,
# never hidden.
MAX_TILES_PER_REQUEST = 12
# Local 320 m wiggles on a flat basin are not a shoreline.
MIN_CONTOUR_KM = 10.0


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


def _interp_rc(r0: float, c0: float, r1: float, c1: float, z0: float, z1: float, level: float) -> RC:
    if z1 == z0:
        t = 0.5
    else:
        t = (level - z0) / (z1 - z0)
    t = min(1.0, max(0.0, float(t)))
    return (r0 + t * (r1 - r0), c0 + t * (c1 - c0))


def _length_km(line: List[LngLat]) -> float:
    return sum(haversine_km(line[i - 1], line[i]) for i in range(1, len(line)))


def _stitch_polylines(segments: List[Tuple[LngLat, LngLat]]) -> List[List[LngLat]]:
    """Join marching-squares segments. Open shore stays open. No polar-sort ring."""
    if not segments:
        return []

    def key(p: LngLat) -> Tuple[int, int]:
        return (round(p[0] * 1e5), round(p[1] * 1e5))

    adj: Dict[Tuple[int, int], List[Tuple[int, int]]] = defaultdict(list)
    coord: Dict[Tuple[int, int], LngLat] = {}
    for a, b in segments:
        ka, kb = key(a), key(b)
        if ka == kb:
            continue
        coord[ka] = a
        coord[kb] = b
        adj[ka].append(kb)
        adj[kb].append(ka)

    def pop_nb(u: Tuple[int, int], v: Tuple[int, int]) -> None:
        if v in adj[u]:
            adj[u].remove(v)
        if u in adj[v]:
            adj[v].remove(u)

    def walk(start: Tuple[int, int], first: Optional[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
        path = [start]
        cur = start
        if first is not None:
            pop_nb(cur, first)
            path.append(first)
            cur = first
        while adj[cur]:
            nxt = adj[cur][0]
            pop_nb(cur, nxt)
            path.append(nxt)
            cur = nxt
            if cur == start:
                break
        return path

    lines: List[List[LngLat]] = []
    for start in [n for n, nbs in list(adj.items()) if len(nbs) == 1]:
        if not adj[start]:
            continue
        path = walk(start)
        if len(path) >= 4:
            lines.append([coord[p] for p in path])
    for node in list(adj.keys()):
        while adj[node]:
            path = walk(node, first=adj[node][0])
            if len(path) >= 4:
                lines.append([coord[p] for p in path])
    return lines


def shoreline_from_dem(dem: np.ndarray, bbox: BBox, level_m: float) -> List[List[LngLat]]:
    """Marching-squares polylines at level_m. Open contours stay open.

    Polar-sort around the centroid is forbidden: that closes a shore fragment
    into a fake ring. CALIBRAZIONE.md left this as the next honest step.
    """
    if dem.size == 0 or not np.isfinite(dem).any():
        return []
    filled = np.where(np.isfinite(dem), dem, np.nanmedian(dem))
    lo, hi = float(np.nanmin(filled)), float(np.nanmax(filled))
    if lo == hi or not (lo <= level_m <= hi):
        return []

    tl, tr = filled[:-1, :-1], filled[:-1, 1:]
    bl, br = filled[1:, :-1], filled[1:, 1:]
    zmin = np.minimum.reduce([tl, tr, bl, br])
    zmax = np.maximum.reduce([tl, tr, bl, br])
    crosses = (zmin <= level_m) & (zmax >= level_m) & (zmin != zmax)
    rows, cols = np.nonzero(crosses)
    if rows.size == 0:
        return []

    shape = filled.shape
    segments: List[Tuple[LngLat, LngLat]] = []
    pairs_of = {
        1: [("left", "top")],
        2: [("top", "right")],
        3: [("left", "right")],
        4: [("right", "bot")],
        5: [("left", "top"), ("right", "bot")],
        6: [("top", "bot")],
        7: [("left", "bot")],
        8: [("left", "bot")],
        9: [("top", "bot")],
        10: [("top", "right"), ("left", "bot")],
        11: [("right", "bot")],
        12: [("left", "right")],
        13: [("top", "right")],
        14: [("left", "top")],
    }
    for r, c in zip(rows.tolist(), cols.tolist()):
        ztl, ztr, zbl, zbr = float(tl[r, c]), float(tr[r, c]), float(bl[r, c]), float(br[r, c])
        case = (
            (1 if ztl >= level_m else 0)
            | (2 if ztr >= level_m else 0)
            | (4 if zbr >= level_m else 0)
            | (8 if zbl >= level_m else 0)
        )
        if case in (0, 15):
            continue
        edges = {
            "top": _interp_rc(r, c, r, c + 1, ztl, ztr, level_m),
            "right": _interp_rc(r, c + 1, r + 1, c + 1, ztr, zbr, level_m),
            "bot": _interp_rc(r + 1, c, r + 1, c + 1, zbl, zbr, level_m),
            "left": _interp_rc(r, c, r + 1, c, ztl, zbl, level_m),
        }
        for e0, e1 in pairs_of.get(case, []):
            p0 = _rowcol_to_ll(edges[e0][0], edges[e0][1], bbox, shape)
            p1 = _rowcol_to_ll(edges[e1][0], edges[e1][1], bbox, shape)
            segments.append((p0, p1))
    lines = _stitch_polylines(segments)
    return [ln for ln in lines if _length_km(ln) >= MIN_CONTOUR_KM]


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


def tiles_covering_bbox(bbox: BBox) -> List[Tuple[int, int]]:
    """Every 1° Copernicus GLO-30 tile (SW-corner lat, lon) whose footprint
    touches bbox. A single tile is a corner of the lake, not the shore."""
    lon0, lat0, lon1, lat1 = (float(v) for v in bbox)
    lat_start = int(math.floor(lat0))
    lat_end = int(math.floor(min(lat1 - 1e-9, 89.0)))
    lon_start = int(math.floor(lon0))
    lon_end = int(math.floor(min(lon1 - 1e-9, 179.0)))
    return [
        (lat_s, lon_s)
        for lat_s in range(lat_start, lat_end + 1)
        for lon_s in range(lon_start, lon_end + 1)
    ]


def _read_dem(path: Path, lat_s: int, lon_s: int) -> Optional[Tuple[np.ndarray, List[float]]]:
    try:
        import rasterio
        with rasterio.open(path) as src:
            dem = src.read(1).astype(np.float64)
            nodata = src.nodata
            if nodata is not None:
                dem[dem == nodata] = np.nan
            b = src.bounds
            bbox = [float(b.left), float(b.bottom), float(b.right), float(b.top)]
        dem[dem < -500] = np.nan
        return dem, bbox
    except Exception:
        pass
    try:
        import tifffile
        dem = np.asarray(tifffile.imread(path), dtype=np.float64)
        if dem.ndim > 2:
            dem = np.squeeze(dem)
        if dem.ndim > 2:
            dem = dem[0]
        dem[dem < -500] = np.nan
        bbox = [float(lon_s), float(lat_s), float(lon_s + 1), float(lat_s + 1)]
        return dem, bbox
    except Exception:
        return None


def fetch_copernicus_tile(lat_s: int, lon_s: int, timeout: int = 90) -> Optional[Tuple[np.ndarray, List[float], str]]:
    """One 1° GLO-30 COG. None if network or reader fails. Never invents terrain."""
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
        read = _read_dem(dest, lat_s, lon_s)
        if read is None:
            return None
        dem, bbox = read
        return dem, bbox, url
    except Exception:
        return None


def measure_highstand(
    bbox: BBox,
    level_m: float = MEGA_CHAD_HIGHSTAND_M,
    max_tiles: int = MAX_TILES_PER_REQUEST,
) -> Dict[str, Any]:
    """Real 320 m shoreline over every Copernicus GLO-30 tile touching bbox,
    up to max_tiles. One tile is a corner, not the lake — this walks the grid
    and says plainly how much of it it covered. A tile that fails to fetch is
    dropped, not filled in."""
    wanted = tiles_covering_bbox(bbox)
    tiles = wanted[:max_tiles]
    truncated = len(wanted) > max_tiles

    lines: List[List[LngLat]] = []
    fetched_tiles: List[Dict[str, Any]] = []
    failed_tiles: List[List[int]] = []
    for lat_s, lon_s in tiles:
        fetched = fetch_copernicus_tile(lat_s, lon_s)
        if fetched is None:
            failed_tiles.append([lat_s, lon_s])
            continue
        dem, tile_bbox, url = fetched
        lines.extend(shoreline_from_dem(dem, tile_bbox, level_m))
        fetched_tiles.append({
            "tile": [lat_s, lon_s],
            "url": url,
            "zmin": float(np.nanmin(dem)),
            "zmax": float(np.nanmax(dem)),
        })

    if not fetched_tiles:
        return {
            "nodes": [],
            "contour": {"type": "FeatureCollection", "features": []},
            "dem": {
                "real": False,
                "reason": "copernicus-dem-unavailable",
                "tiles_attempted": [list(t) for t in tiles],
                "tiles_total": len(wanted),
            },
        }

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
                "properties": {
                    "id": "mega_chad_dem_contour",
                    "grade": "dem-contour",
                    "level_m": level_m,
                    "length_km": round(_length_km(line), 1),
                },
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
            "tiles_used": [t["tile"] for t in fetched_tiles],
            "tiles_failed": failed_tiles,
            "tiles_total": len(wanted),
            "truncated": truncated,
            "urls": [t["url"] for t in fetched_tiles],
            "zmin": min(t["zmin"] for t in fetched_tiles),
            "zmax": max(t["zmax"] for t in fetched_tiles),
            "level_m": level_m,
            "n_contours": len(lines),
            "note": "Isolinea disegnata, non sponda individuata. Calibrazione Bama Ridge: fallita.",
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
