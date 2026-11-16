"""Scansione di un DTM: blocchi -> probabilita' -> oggetti -> complessi candidati.

Funziona su qualunque GeoTIFF di terreno nudo in coordinate metriche (UTM).
Non decide cosa e' antico: misura e mette in fila. Ogni candidato porta le
misure con cui e' stato scelto, cosi' un altro puo' rifarle.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, Iterator, List, Tuple

import numpy as np

from . import model as M
from . import relief

BLOCK_M = 1000.0      # altezza di un blocco
OVERLAP_M = 40.0      # sovrapposizione fra blocchi (un complesso non si taglia a meta')
EDGE_M = 6.0          # distanza minima dal bordo del dato: la' l'interpolazione inventa
LINK_M = 60.0         # due oggetti entro questa distanza sono lo stesso complesso
CHIP_M = 120.0        # lato del riquadro mostrato a chi rivede


def _blocks(src: Any) -> Iterator[Tuple[np.ndarray, float, float]]:
    """Blocchi a 0.5 m ritagliati sul dato valido. Ritorna (dem, x_sinistra, y_alto)."""
    from rasterio.enums import Resampling
    from rasterio.windows import Window

    rx, ry = src.res
    step = int((BLOCK_M - OVERLAP_M) / ry)
    rows = int(BLOCK_M / ry)
    for r0 in range(0, src.height, step):
        n = min(rows, src.height - r0)
        if n < 50:
            break
        shape = (int(round(n * ry / relief.PX_M)), int(round(src.width * rx / relief.PX_M)))
        dem = src.read(1, window=Window(0, r0, src.width, n), out_shape=shape,
                       resampling=Resampling.average).astype(np.float32)
        if src.nodata is not None:
            dem[dem == np.float32(src.nodata)] = np.nan
        dem[np.abs(dem) > 1e5] = np.nan
        cols = np.flatnonzero(np.isfinite(dem).any(axis=0))
        if len(cols) < 40:
            continue
        c0, c1 = max(0, cols[0] - 20), min(shape[1], cols[-1] + 21)
        px_x = src.width * rx / shape[1]
        yield dem[:, c0:c1], src.bounds.left + c0 * px_x, src.bounds.top - r0 * ry


def _shape(ys: np.ndarray, xs: np.ndarray) -> Tuple[float, float]:
    """(allungamento, rettangolarita') dagli assi principali dell'oggetto."""
    p = np.stack([xs - xs.mean(), ys - ys.mean()], 1).astype(np.float64)
    if len(p) < 6:
        return 1.0, 1.0
    w, v = np.linalg.eigh(np.cov(p.T))
    q = p @ v
    ext = q.max(0) - q.min(0) + 1.0
    return float(max(ext) / max(1.0, min(ext))), float(min(1.0, len(p) / (ext[0] * ext[1])))


def scan_dtm(path: Path, clf: Any, name: str = "") -> List[Dict[str, Any]]:
    """Tutti gli oggetti di un DTM, in coordinate del raster (x, y in metri)."""
    import rasterio
    from scipy import ndimage

    objs: List[Dict[str, Any]] = []
    with rasterio.open(path) as src:
        for dem, x0, y0 in _blocks(src):
            b, valid = relief.bands(dem)
            if valid.mean() < 0.02:
                continue
            prob = M.predict(clf, b)
            inner = ndimage.distance_transform_edt(valid) * relief.PX_M >= EDGE_M
            lab, n = M.objects(M.extract(prob, inner))
            if n == 0:
                continue
            lrm = relief.local_relief(dem)
            sl = ndimage.find_objects(lab)
            for i in range(1, n + 1):
                m = lab[sl[i - 1]] == i
                ys, xs = np.nonzero(m)
                ys, xs = ys + sl[i - 1][0].start, xs + sl[i - 1][1].start
                el, rect = _shape(ys, xs)
                objs.append({
                    "x": round(x0 + (xs.mean() + 0.5) * relief.PX_M, 1),
                    "y": round(y0 - (ys.mean() + 0.5) * relief.PX_M, 1),
                    "area_m2": round(len(ys) * relief.PX_M ** 2, 1),
                    "prob": round(float(prob[ys, xs].mean()), 3),
                    "height_m": round(float(np.percentile(lrm[ys, xs], 95)), 2),
                    "elong": round(el, 2), "rect": round(rect, 2),
                })
    return _dedupe(objs)


def _dedupe(objs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Lo stesso oggetto visto in due blocchi sovrapposti conta una volta (il piu' grande)."""
    from scipy.spatial import cKDTree

    if len(objs) < 2:
        return objs
    objs = sorted(objs, key=lambda o: -o["area_m2"])
    tree = cKDTree([(o["x"], o["y"]) for o in objs])
    drop = set()
    for i, j in sorted(tree.query_pairs(5.0)):
        if i not in drop:
            drop.add(j)
    return [o for k, o in enumerate(objs) if k not in drop]


def cluster(objs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Oggetti vicini -> complessi. Un complesso e' l'unita' che si rivede e si riferisce."""
    from scipy.spatial import cKDTree

    if not objs:
        return []
    parent = list(range(len(objs)))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for i, j in cKDTree([(o["x"], o["y"]) for o in objs]).query_pairs(LINK_M):
        parent[find(i)] = find(j)
    groups: Dict[int, List[Dict[str, Any]]] = {}
    for k, o in enumerate(objs):
        groups.setdefault(find(k), []).append(o)
    out = []
    for g in groups.values():
        area = sum(o["area_m2"] for o in g)
        big = max(g, key=lambda o: o["area_m2"])
        out.append({
            "x": round(sum(o["x"] * o["area_m2"] for o in g) / area, 1),
            "y": round(sum(o["y"] * o["area_m2"] for o in g) / area, 1),
            "n_objects": len(g), "area_m2": round(area, 1),
            "max_height_m": max(o["height_m"] for o in g),
            "mean_prob": round(sum(o["prob"] * o["area_m2"] for o in g) / area, 3),
            "max_rect": max(o["rect"] for o in g if o["area_m2"] >= 50) if any(o["area_m2"] >= 50 for o in g) else big["rect"],
            "extent_m": round(max(math.hypot(a["x"] - b["x"], a["y"] - b["y"]) for a in g for b in g), 1) if len(g) < 400 else None,
            # punteggio d'ordine: area sicura, premiando chi sporge. Serve a decidere cosa guardare prima.
            "score": round(sum(o["area_m2"] * o["prob"] * min(2.0, max(0.2, o["height_m"])) for o in g), 1),
        })
    return sorted(out, key=lambda c: -c["score"])


def chip_bands(path: Path, x: float, y: float, side_m: float = CHIP_M) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Riquadro centrato su (x, y): (bande uint8, maschera valida, rilievo locale m)."""
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.windows import from_bounds

    pad = 10.0
    h = side_m / 2 + pad
    with rasterio.open(path) as src:
        win = from_bounds(x - h, y - h, x + h, y + h, src.transform)
        n = int(round(2 * h / relief.PX_M))
        dem = src.read(1, window=win, out_shape=(n, n), resampling=Resampling.average,
                       boundless=True, fill_value=np.nan).astype(np.float32)
        if src.nodata is not None:
            dem[dem == np.float32(src.nodata)] = np.nan
    dem[np.abs(dem) > 1e5] = np.nan
    b, valid = relief.bands(dem)
    p = int(pad / relief.PX_M)
    return b[p:-p, p:-p], valid[p:-p, p:-p], relief.local_relief(dem)[p:-p, p:-p]


def render_gray(b: np.ndarray, valid: np.ndarray | None = None, size: int = 480) -> "Any":
    """Immagine per chi rivede: SVF moltiplicato per pendenza. Uguale per ogni sorgente."""
    from PIL import Image

    g = (b[..., 0].astype(np.float32) / 255) * (0.35 + 0.65 * b[..., 2].astype(np.float32) / 255)
    g = (np.clip(g, 0, 1) * 255).astype(np.uint8)
    if valid is not None:
        g[~valid] = 0
    return Image.fromarray(g).resize((size, size), Image.BICUBIC)
