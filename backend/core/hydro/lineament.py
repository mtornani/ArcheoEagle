"""Isolate the lineament, then measure it.

Scene-wide stats cannot see a shore that is ~1% of the contour fragments
(CALIBRAZIONE.md). Polar-sort around a centroid is not a contour: it closes
open shores into a fake ring. This module traces polylines and asks whether
they continue across a tile edge at the same level.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from core.hydro.measure import (
    BBox,
    LngLat,
    MIN_CONTOUR_KM,
    _length_km,
    _rowcol_to_ll,
    shoreline_from_dem,
)
from core.hydro.paleorivers import haversine_km

# ~330 m. A 30 m DEM pixel is smaller; this is "on the tile frame", not on a site.
EDGE_TOL_DEG = 0.003
JOIN_TOL_KM = 2.0


def polar_sort_contour(dem, bbox: BBox, level_m: float) -> List[List[LngLat]]:
    """Legacy algorithm. Comparison only. Closes every cloud into one ring."""
    import numpy as np

    if dem.size == 0 or not np.isfinite(dem).any():
        return []
    filled = np.where(np.isfinite(dem), dem, np.nanmedian(dem))
    lo, hi = float(np.nanmin(filled)), float(np.nanmax(filled))
    if lo == hi or not (lo <= level_m <= hi):
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
    import math
    ordered = sorted(pts, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
    ordered.append(ordered[0])
    return [ordered]


def edge_side(pt: LngLat, bbox: BBox, tol: float = EDGE_TOL_DEG) -> Optional[str]:
    lon, lat = pt
    lon0, lat0, lon1, lat1 = (float(v) for v in bbox)
    if abs(lon - lon0) <= tol:
        return "W"
    if abs(lon - lon1) <= tol:
        return "E"
    if abs(lat - lat0) <= tol:
        return "S"
    if abs(lat - lat1) <= tol:
        return "N"
    return None


def termini(line: List[LngLat], bbox: BBox) -> List[Tuple[LngLat, str]]:
    out: List[Tuple[LngLat, str]] = []
    if len(line) < 2:
        return out
    for pt in (line[0], line[-1]):
        side = edge_side(pt, bbox)
        if side:
            out.append((pt, side))
    return out


def summarize(lines: List[List[LngLat]], bbox: BBox) -> Dict[str, Any]:
    lengths = [_length_km(ln) for ln in lines]
    n_open = sum(1 for ln in lines if ln[0] != ln[-1])
    n_edge = sum(1 for ln in lines if termini(ln, bbox))
    longest = max(lines, key=_length_km) if lines else []
    return {
        "n": len(lines),
        "n_open": n_open,
        "n_with_edge": n_edge,
        "longest_km": round(max(lengths), 1) if lengths else 0.0,
        "total_km": round(sum(lengths), 1),
        "longest_closed": bool(longest) and longest[0] == longest[-1],
        "min_contour_km": MIN_CONTOUR_KM,
    }


def shared_sides(bbox_a: BBox, bbox_b: BBox, tol: float = 0.01) -> Optional[Tuple[str, str]]:
    """If A and B share a meridian or parallel, return (side_on_A, side_on_B)."""
    a0, a1, a2, a3 = (float(v) for v in bbox_a)
    b0, b1, b2, b3 = (float(v) for v in bbox_b)
    if abs(a2 - b0) <= tol:
        return ("E", "W")
    if abs(a0 - b2) <= tol:
        return ("W", "E")
    if abs(a3 - b1) <= tol:
        return ("N", "S")
    if abs(a1 - b3) <= tol:
        return ("S", "N")
    return None


def join_count(
    lines_a: List[List[LngLat]],
    bbox_a: BBox,
    lines_b: List[List[LngLat]],
    bbox_b: BBox,
    tol_km: float = JOIN_TOL_KM,
) -> int:
    """How many edge-termini on the shared side sit within tol_km of a neighbour."""
    sides = shared_sides(bbox_a, bbox_b)
    if not sides:
        return 0
    side_a, side_b = sides
    ends_a = [pt for ln in lines_a for pt, s in termini(ln, bbox_a) if s == side_a]
    ends_b = [pt for ln in lines_b for pt, s in termini(ln, bbox_b) if s == side_b]
    used = set()
    n = 0
    for pa in ends_a:
        best_i = None
        best_d = tol_km
        for i, pb in enumerate(ends_b):
            if i in used:
                continue
            d = haversine_km(pa, pb)
            if d < best_d:
                best_d = d
                best_i = i
        if best_i is not None:
            used.add(best_i)
            n += 1
    return n


def _sample_dem(dem, bbox: BBox, lon: float, lat: float) -> Optional[float]:
    import numpy as np

    h, w = dem.shape
    lon0, lat0, lon1, lat1 = (float(v) for v in bbox)
    if lon1 == lon0 or lat1 == lat0:
        return None
    col = (lon - lon0) / (lon1 - lon0) * (w - 1)
    row = (lat1 - lat) / (lat1 - lat0) * (h - 1)
    if col < 0 or col > w - 1 or row < 0 or row > h - 1:
        return None
    z = float(dem[int(round(row)), int(round(col))])
    if not np.isfinite(z):
        return None
    return z


def relief_across(
    dem,
    bbox: BBox,
    line: List[LngLat],
    offset_deg: float = 0.01,
    step: int = 20,
) -> Dict[str, Any]:
    """Mean elevation drop across an isolated polyline. Not a shore label.

    offset_deg ~1 km. Samples both sides of the tangent. A beach ridge should
    show a one-sided step; a wiggle on a flat basin should not.
    """
    if len(line) < 3:
        return {"n": 0, "drop_m": None, "reason": "line too short"}
    drops: List[float] = []
    for i in range(0, len(line) - 1, max(1, len(line) // max(step, 1))):
        j = min(i + 1, len(line) - 1)
        lon0, lat0 = line[i]
        lon1, lat1 = line[j]
        dx, dy = lon1 - lon0, lat1 - lat0
        norm = (dx * dx + dy * dy) ** 0.5
        if norm < 1e-12:
            continue
        px, py = -dy / norm * offset_deg, dx / norm * offset_deg
        mid = ((lon0 + lon1) / 2, (lat0 + lat1) / 2)
        za = _sample_dem(dem, bbox, mid[0] + px, mid[1] + py)
        zb = _sample_dem(dem, bbox, mid[0] - px, mid[1] - py)
        if za is None or zb is None:
            continue
        drops.append(abs(za - zb))
    if len(drops) < 4:
        return {"n": len(drops), "drop_m": None, "reason": "too few samples"}
    drops.sort()
    return {
        "n": len(drops),
        "drop_m": round(sum(drops) / len(drops), 1),
        "drop_median_m": round(drops[len(drops) // 2], 1),
        "offset_deg": offset_deg,
    }


def compare_methods(dem, bbox: BBox, level_m: float) -> Dict[str, Any]:
    traced = shoreline_from_dem(dem, bbox, level_m)
    polar = polar_sort_contour(dem, bbox, level_m)
    return {
        "level_m": level_m,
        "traced": summarize(traced, bbox),
        "polar": summarize(polar, bbox),
        "traced_lines": traced,
        "polar_lines": polar,
    }
