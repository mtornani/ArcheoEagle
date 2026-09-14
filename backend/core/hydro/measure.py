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
# One request-response cycle, not a batch job. More tiles = more honest coverage
# but each is a network fetch; cap so /walk still answers. Truncation is reported,
# never hidden.
MAX_TILES_PER_REQUEST = 12


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


ANALYSIS_SCALE_M = 120.0   # scala a cui vive il cordone; vedi control.py


def _coarsen_to_scale(dem: np.ndarray, bbox: BBox, scale_m: float) -> np.ndarray:
    """Media d'area fino a ~scale_m per pixel. Vedi control.py, 14 set 2026.

    La Bama Ridge e' un gradino di ~8 m su ~1 km: a 30 m/pixel sta sotto la
    rugosita' delle dune, e tracciarci un'isolinea sopra restituisce migliaia
    di frammenti di rumore invece di un cordone. Mediando a ~120 m il cordone
    emerge. MEDIA, non campionamento: sottocampionare ripiega il rumore fine
    sulle scale grandi.
    """
    h, w = dem.shape
    if h < 16 or w < 16:
        return dem
    lon0, lat0, lon1, lat1 = (float(v) for v in bbox)
    lat_mid = (lat0 + lat1) / 2.0
    px_m = math.radians(abs(lon1 - lon0) / w) * 6371000.0 * math.cos(math.radians(lat_mid))
    f = int(round(scale_m / px_m)) if px_m > 0 else 1
    f = max(1, min(f, h // 16, w // 16))
    if f <= 1:
        return dem
    h2, w2 = h // f, w // f
    return dem[: h2 * f, : w2 * f].reshape(h2, f, w2, f).mean(axis=(1, 3))


def shoreline_from_dem(dem: np.ndarray, bbox: BBox, level_m: float,
                       scale_m: float = ANALYSIS_SCALE_M,
                       min_points: int = 8) -> List[List[LngLat]]:
    """Isolinee a level_m, tracciate davvero (marching squares).

    RISCRITTA IL 14 SET 2026. La versione precedente raccoglieva i punti di
    attraversamento e li ordinava per **angolo attorno al centroide**, poi
    chiudeva l'anello. Non e' un tracciatore di contorni: presuppone che il
    risultato sia un anello chiuso e convesso attorno a un centro. Su un
    segmento di sponda dentro un tile 1° produce un poligono a stella senza
    alcun rapporto con la geometria vera. Era un disegno, non una misura —
    cioe' precisamente cio' che CLAUDE.md §2b vieta.

    Ora: media d'area alla scala del cordone, poi marching squares, che
    restituisce piu' polilinee aperte separate — che e' la forma giusta di una
    sponda dentro un riquadro.

    Senza skimage restituisce [] e chi chiama vede `schematic`. Nessun anello
    inventato: meglio niente che una misura finta.
    """
    if dem.size == 0 or not np.isfinite(dem).any():
        return []
    filled = np.where(np.isfinite(dem), dem, np.nanmedian(dem))
    small = _coarsen_to_scale(filled, bbox, scale_m)
    lo, hi = float(np.nanmin(small)), float(np.nanmax(small))
    if not (lo < level_m < hi):
        return []
    try:
        from skimage.measure import find_contours
    except ImportError:
        return []

    out: List[List[LngLat]] = []
    for curve in find_contours(small, level_m):
        if len(curve) < min_points:
            continue          # frammento: non e' una sponda
        out.append([_rowcol_to_ll(float(r), float(c), bbox, small.shape)
                    for r, c in curve])
    # la piu' lunga per prima: chi legge vuole il cordone, non i ritagli
    out.sort(key=len, reverse=True)
    return out


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


def tiles_by_distance_to_schematic(tiles: List[Tuple[int, int]],
                                   schematic_id: str = "mega_chad_shore",
                                   ) -> List[Tuple[int, int]]:
    """Ordina i tile per vicinanza al tracciato schematico di letteratura.

    NATA DA UN ERRORE VISIBILE SOLO IL 14 SET 2026. La bbox del Mega-Chad
    chiede **156 tile** e il tetto per richiesta e' 12. `tiles_covering_bbox`
    li restituisce in ordine di griglia, quindi i 12 pagati finivano tutti
    nell'angolo sud-ovest — oltre 100 km dalla sponda attesa. Si misurava
    terreno a caso e lo si chiamava `dem-contour`. L'errore era invisibile
    finche' il tracciatore di isolinee era finto: due difetti che si
    nascondevano a vicenda.

    Il tracciato schematico e' un'**ipotesi**, non un bersaglio: usarlo per
    decidere *dove guardare* e' legittimo (e' la sola informazione a priori
    che abbiamo), usarlo per decidere *cosa hai trovato* no. Il numero che
    conta resta `vs_schematic_km`, cioe' di quanto la misura si discosta dal
    disegno — e quello si calcola dopo, sul DEM, senza sconti.
    """
    net = load_network()
    shore: List[LngLat] = []
    for feat in net.get("features") or []:
        if (feat.get("properties") or {}).get("id") == schematic_id:
            for c in (feat.get("geometry") or {}).get("coordinates") or []:
                shore.append((float(c[0]), float(c[1])))
    if not shore:
        return list(tiles)
    def _d(t: Tuple[int, int]) -> float:
        centre = (t[1] + 0.5, t[0] + 0.5)      # (lon, lat) del centro tile
        return min(haversine_km(centre, p) for p in shore)
    return sorted(tiles, key=_d)


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
    # Se il tetto taglia, i tile pagati vanno spesi dove la sponda dovrebbe
    # stare, non nell'angolo che capita per ordine di griglia. Vedi
    # tiles_by_distance_to_schematic.
    if len(wanted) > max_tiles:
        wanted = tiles_by_distance_to_schematic(wanted)
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

        # FILTRO A GRADINO — aggiunto il 14 set 2026.
        # Un'isolinea a 320 m e' una misura, ma chiamarla "la sponda" e' una
        # interpretazione che il dato non regge: su un bacino enorme e piatto
        # quella quota viene attraversata dappertutto (1136 polilinee al primo
        # giro sul Mega-Chad). Prima di accettare le isolinee di un tile si
        # chiede al rilevatore, ora validato sul controllo positivo, se a
        # quella quota il terreno si comporta davvero da gradino. Se no, le
        # isolinee restano nel contour come geometria ma NON diventano nodi.
        # Misurare non basta: bisogna misurare qualcosa che sia un cordone.
        from core.hydro.control import multiscale_step_score, STEP_SCORE_THRESHOLD
        # "non so decidere" non e' "non e' un gradino". Se il rilevatore non
        # riesce a valutare (griglia troppo piccola, dispersione nulla), le
        # isolinee restano — cancellare la misura in silenzio sarebbe peggio
        # del falso positivo che il filtro evita. Il tile viene marcato
        # `undecided` e finisce nel conteggio, cosi' chi legge lo sa.
        scored = multiscale_step_score(dem, level_m, bbox=tile_bbox)
        score = scored.get("step_score")
        is_step = None if score is None else bool(score >= STEP_SCORE_THRESHOLD)

        tile_lines = shoreline_from_dem(dem, tile_bbox, level_m)
        if is_step is not False:
            lines.extend(tile_lines)
        fetched_tiles.append({
            "tile": [lat_s, lon_s],
            "url": url,
            "zmin": float(np.nanmin(dem)),
            "zmax": float(np.nanmax(dem)),
            "step_score": score,
            "is_step": is_step,
            "scale_factor": scored.get("factor"),
            "lines": len(tile_lines),
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
            "tiles_used": [t["tile"] for t in fetched_tiles],
            # per tile: punteggio a gradino, scala, isolinee. Senza questi
            # un "dem-contour" non e' leggibile: non si sa quali tile hanno
            # davvero un cordone e quali hanno solo attraversato la quota.
            "tiles_scored": fetched_tiles,
            "tiles_with_step": sum(1 for t in fetched_tiles if t.get("is_step") is True),
            "tiles_undecided": sum(1 for t in fetched_tiles if t.get("is_step") is None),
            "tiles_no_step": sum(1 for t in fetched_tiles if t.get("is_step") is False),
            "tiles_failed": failed_tiles,
            "tiles_total": len(wanted),
            "truncated": truncated,
            "urls": [t["url"] for t in fetched_tiles],
            "zmin": min(t["zmin"] for t in fetched_tiles),
            "zmax": max(t["zmax"] for t in fetched_tiles),
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
