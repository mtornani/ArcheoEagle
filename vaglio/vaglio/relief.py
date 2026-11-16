"""Dal DTM alle tre bande che un archeologo guarda davvero.

Sky-view factor, apertura positiva e pendenza, con i parametri e la
normalizzazione di Kokalj et al. 2023 (Sci Data 10:558, "general terrain"):
raggio 5 m, 16 direzioni; SVF 0.7-1.0, apertura 68-93 gradi, pendenza 0-50
gradi invertita. Stessi numeri = il modello tarato su Chactun vede gli altri
rilievi nella stessa lingua.

Solo numpy: niente dipendenze che a casa non si installano.
"""
from __future__ import annotations

import math
from typing import Tuple

import numpy as np

RADIUS_M = 5.0
N_DIR = 16
PX_M = 0.5  # risoluzione di lavoro: quella delle annotazioni di Chactun


def fill_nan(dem: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Riempie i vuoti col valore valido piu' vicino (solo per il calcolo). Ritorna (pieno, maschera_valida)."""
    from scipy import ndimage

    valid = np.isfinite(dem)
    if valid.all() or not valid.any():
        return dem, valid
    idx = ndimage.distance_transform_edt(~valid, return_distances=False, return_indices=True)
    return dem[tuple(idx)], valid


def svf_openness(dem: np.ndarray, px_m: float = PX_M) -> Tuple[np.ndarray, np.ndarray]:
    """(SVF in 0..1, apertura positiva in gradi). `dem` senza NaN."""
    r_px = max(1, int(round(RADIUS_M / px_m)))
    pad = np.pad(dem, r_px, mode="edge")
    h, w = dem.shape
    sum_sin = np.zeros_like(dem, dtype=np.float32)
    sum_ang = np.zeros_like(dem, dtype=np.float32)
    for k in range(N_DIR):
        a = 2 * math.pi * k / N_DIR
        best = np.full(dem.shape, -np.inf, dtype=np.float32)
        seen = set()
        for r in range(1, r_px + 1):
            dy, dx = int(round(r * math.sin(a))), int(round(r * math.cos(a)))
            if (dy, dx) in seen or (dy, dx) == (0, 0):
                continue
            seen.add((dy, dx))
            dist = math.hypot(dy, dx) * px_m
            sh = pad[r_px + dy: r_px + dy + h, r_px + dx: r_px + dx + w]
            np.maximum(best, (sh - dem) / dist, out=best)
        gamma = np.arctan(best)                      # angolo di elevazione dell'orizzonte
        sum_sin += np.sin(np.maximum(gamma, 0))
        sum_ang += gamma
    svf = 1.0 - sum_sin / N_DIR
    opn = 90.0 - np.degrees(sum_ang / N_DIR)
    return svf, opn


def slope_deg(dem: np.ndarray, px_m: float = PX_M) -> np.ndarray:
    gy, gx = np.gradient(dem, px_m)
    return np.degrees(np.arctan(np.hypot(gx, gy))).astype(np.float32)


def _stretch(a: np.ndarray, lo: float, hi: float) -> np.ndarray:
    return (np.clip((a - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)


def bands(dem: np.ndarray, px_m: float = PX_M) -> Tuple[np.ndarray, np.ndarray]:
    """DTM (con NaN) -> (H,W,3 uint8: SVF, apertura, pendenza invertita), maschera valida."""
    full, valid = fill_nan(dem.astype(np.float32))
    svf, opn = svf_openness(full, px_m)
    out = np.stack([
        _stretch(svf, 0.7, 1.0),
        _stretch(opn, 68.0, 93.0),
        255 - _stretch(slope_deg(full, px_m), 0.0, 50.0),
    ], axis=-1)
    return out, valid


def local_relief(dem: np.ndarray, px_m: float = PX_M, radius_m: float = 15.0) -> np.ndarray:
    """Quota meno la media locale: quanto sporge (m). Serve alla scheda-prova, non al rilevatore."""
    from scipy import ndimage

    full, _ = fill_nan(dem.astype(np.float32))
    size = int(round(2 * radius_m / px_m)) | 1
    return full - ndimage.uniform_filter(full, size=size, mode="nearest")
