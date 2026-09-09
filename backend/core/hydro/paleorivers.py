"""Sahara paleodrainage: the road. Shape is not the target."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

BBox = Sequence[float]  # lon_min, lat_min, lon_max, lat_max
LngLat = Tuple[float, float]


def _data_path() -> Path:
    root = Path(__file__).resolve().parents[3]
    return root / "data" / "sahara_paleodrainage.geojson"


def load_network(path: Optional[Path] = None) -> Dict[str, Any]:
    p = path or _data_path()
    with p.open(encoding="utf-8") as f:
        return json.load(f)


# Human aliases → feature ids. Corridor is the unit of search, not a drawn box.
CORRIDOR_IDS: Dict[str, List[str]] = {
    "tamanrasset": ["tamanrasset"],
    "megachad": ["mega_chad_shore", "taffassasset"],
    "mega_chad": ["mega_chad_shore", "taffassasset"],
    "sahabi": ["sahabi"],
    "irharhar": ["irharhar"],
    "tilemsi": ["tilemsi"],
    "howar": ["wadi_howar"],
    "wadi_howar": ["wadi_howar"],
    "azawagh": ["azawagh"],
}


def corridor_features(corridor_id: str, network: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    net = network or load_network()
    wanted = set(CORRIDOR_IDS.get(corridor_id, [corridor_id]))
    wanted.add(corridor_id)
    out = []
    for feat in net.get("features") or []:
        props = feat.get("properties") or {}
        if props.get("id") in wanted or props.get("basin") in wanted:
            out.append(feat)
    return out


def corridor_bbox(corridor_id: str, pad_deg: float = 0.6) -> List[float]:
    feats = corridor_features(corridor_id)
    if not feats:
        raise ValueError(f"corridoio sconosciuto: {corridor_id}")
    lons: List[float] = []
    lats: List[float] = []
    for feat in feats:
        for lon, lat in _ring_coords(feat.get("geometry") or {}):
            lons.append(lon)
            lats.append(lat)
    return [
        min(lons) - pad_deg,
        min(lats) - pad_deg,
        max(lons) + pad_deg,
        max(lats) + pad_deg,
    ]


def bbox_to_aoi(bbox: BBox) -> Dict[str, Any]:
    lon0, lat0, lon1, lat1 = bbox
    return {
        "type": "Feature",
        "properties": {"generated": "corridor-walk"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [lon0, lat0], [lon1, lat0], [lon1, lat1], [lon0, lat1], [lon0, lat0],
            ]],
        },
    }


def _ring_coords(geom: Dict[str, Any]) -> List[LngLat]:
    gtype = geom.get("type")
    coords = geom.get("coordinates") or []
    if gtype == "LineString":
        return [(float(c[0]), float(c[1])) for c in coords]
    if gtype == "Polygon":
        return [(float(c[0]), float(c[1])) for c in coords[0]]
    if gtype == "MultiLineString":
        out: List[LngLat] = []
        for line in coords:
            out.extend((float(c[0]), float(c[1])) for c in line)
        return out
    return []


def haversine_km(a: LngLat, b: LngLat) -> float:
    lon1, lat1 = map(math.radians, a)
    lon2, lat2 = map(math.radians, b)
    dlon, dlat = lon2 - lon1, lat2 - lat1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371.0 * 2 * math.asin(min(1.0, math.sqrt(h)))


def point_in_bbox(pt: LngLat, bbox: BBox, pad_deg: float = 0.0) -> bool:
    lon, lat = pt
    return (
        bbox[0] - pad_deg <= lon <= bbox[2] + pad_deg
        and bbox[1] - pad_deg <= lat <= bbox[3] + pad_deg
    )


def bbox_from_geojson(geojson: Dict[str, Any]) -> List[float]:
    """Accept Feature, Geometry, or FeatureCollection."""
    geom = geojson
    if geojson.get("type") == "Feature":
        geom = geojson.get("geometry") or {}
    elif geojson.get("type") == "FeatureCollection":
        lons: List[float] = []
        lats: List[float] = []
        for feat in geojson.get("features") or []:
            for lon, lat in _ring_coords(feat.get("geometry") or {}):
                lons.append(lon)
                lats.append(lat)
        if not lons:
            return [0.0, 16.0, 8.0, 24.0]
        return [min(lons), min(lats), max(lons), max(lats)]

    coords = _ring_coords(geom)
    if not coords:
        # raw polygon rings sometimes live at geometry.coordinates without type handling
        raw = (geom or {}).get("coordinates") or geojson.get("coordinates")
        if raw and isinstance(raw[0][0], (int, float)):
            coords = [(float(c[0]), float(c[1])) for c in raw]
        elif raw:
            coords = [(float(c[0]), float(c[1])) for c in raw[0]]
    if not coords:
        return [0.0, 16.0, 8.0, 24.0]
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    return [min(lons), min(lats), max(lons), max(lats)]


def rivers_in_aoi(bbox: BBox, network: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    net = network or load_network()
    feats = []
    for feat in net.get("features") or []:
        pts = _ring_coords(feat.get("geometry") or {})
        if any(point_in_bbox(p, bbox, pad_deg=0.4) for p in pts):
            feats.append(feat)
    return {
        "type": "FeatureCollection",
        "features": feats,
        "metadata": net.get("metadata", {}),
    }


def _sample_along(pts: List[LngLat], step_km: float) -> List[LngLat]:
    if len(pts) < 2:
        return list(pts)
    out: List[LngLat] = [pts[0]]
    acc = 0.0
    for i in range(1, len(pts)):
        seg = haversine_km(pts[i - 1], pts[i])
        acc += seg
        if acc >= step_km:
            out.append(pts[i])
            acc = 0.0
    if pts[-1] != out[-1]:
        out.append(pts[-1])
    return out


def nodes_in_aoi(
    bbox: BBox,
    network: Optional[Dict[str, Any]] = None,
    step_km: float = 90.0,
    confluence_km: float = 25.0,
) -> List[Dict[str, Any]]:
    """Hydrologic nodes only. No city-shape prior."""
    net = network or load_network()
    rivers: List[Tuple[Dict[str, Any], List[LngLat]]] = []
    for feat in net.get("features") or []:
        pts = [p for p in _ring_coords(feat.get("geometry") or {}) if point_in_bbox(p, bbox, pad_deg=0.35)]
        if pts:
            rivers.append((feat, pts))

    nodes: List[Dict[str, Any]] = []
    seen: List[LngLat] = []

    def _near(pt: LngLat, radius_km: float = 18.0) -> bool:
        return any(haversine_km(pt, s) < radius_km for s in seen)

    def _add(pt: LngLat, feat: Dict[str, Any], node_type: str, hydro: float) -> None:
        if _near(pt):
            return
        props = feat.get("properties") or {}
        seen.append(pt)
        nodes.append({
            "lon": round(pt[0], 5),
            "lat": round(pt[1], 5),
            "node_type": node_type,
            "hydro_score": hydro,
            "river_id": props.get("id"),
            "river_name": props.get("name"),
            "basin": props.get("basin"),
            "kind": props.get("kind"),
        })

    # Confluences first (highest hydro prior — still not a city)
    for i, (fa, pa) in enumerate(rivers):
        for fb, pb in rivers[i + 1 :]:
            best = None
            best_d = confluence_km
            for a in pa:
                for b in pb:
                    d = haversine_km(a, b)
                    if d < best_d:
                        best_d = d
                        best = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            if best:
                _add(best, fa, "confluence", 0.92)

    for feat, pts in rivers:
        kind = (feat.get("properties") or {}).get("kind")
        if kind == "paleolake":
            for pt in _sample_along(pts, step_km=110.0):
                _add(pt, feat, "paleolake_shore", 0.84)
            continue
        samples = _sample_along(pts, step_km=step_km)
        if samples:
            _add(samples[0], feat, "head_or_mouth", 0.72)
        for pt in samples[1:-1]:
            _add(pt, feat, "channel", 0.58)
        if len(samples) > 1:
            _add(samples[-1], feat, "head_or_mouth", 0.72)

    return nodes


def nearest_node(lon: float, lat: float, nodes: Iterable[Dict[str, Any]]) -> Optional[Tuple[Dict[str, Any], float]]:
    best = None
    best_d = 1e9
    for n in nodes:
        d = haversine_km((lon, lat), (n["lon"], n["lat"]))
        if d < best_d:
            best_d = d
            best = n
    if best is None:
        return None
    return best, best_d
