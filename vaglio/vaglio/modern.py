"""La spiegazione moderna: cosa c'e' OGGI sopra il candidato.

Naturale, moderno, antico: tre classi, non due. I revisori vedono la forma ma
non sanno se sopra c'e' un paese o un campo arato. Qui lo si chiede a un dato
indipendente dal LiDAR: ESA WorldCover 2021, uso del suolo a 10 m, pubblico
(CC BY 4.0), senza chiave.

E' uno SPIEGATORE, non un rilevatore: non promuove e non scarta niente. Aggiunge
una colonna. Limiti da ripetere: il LiDAR e' del 2013 e la carta del 2021; un
paese moderno sta spesso SOPRA un sito antico, quindi "costruito oggi" non vuol
dire "non antico"; e la classe 'costruito' a 10 m non vede una casa isolata.

Soglie fissate prima di guardare i candidati (16 nov 2026), non tarate:
  costruito oggi : almeno BUILT_MIN del riquadro di 120 m e' classe 'costruito'
  coltivato oggi : almeno CROP_MIN del riquadro e' classe 'coltivo'
"""
from __future__ import annotations

import math
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

URL = "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_{tile}_Map.tif"
SOURCE = "ESA WorldCover 10 m 2021 v200 (CC BY 4.0)"
CLASSES = {10: "alberi", 20: "arbusti", 30: "prato", 40: "coltivo", 50: "costruito", 60: "suolo nudo",
           70: "neve", 80: "acqua", 90: "zona umida", 95: "mangrovie", 100: "muschi e licheni"}
BUILT, CROP = 50, 40
BUILT_MIN, CROP_MIN = 0.05, 0.30
HALF_PX = 6          # +-6 pixel da ~9,3 m: lo stesso riquadro di 120 m che vede il revisore


def tile_name(lat: float, lon: float) -> str:
    """Le tessere WorldCover sono 3 x 3 gradi, col nome dell'angolo sud-ovest."""
    la, lo = math.floor(lat / 3) * 3, math.floor(lon / 3) * 3
    return f"{'N' if la >= 0 else 'S'}{abs(la):02d}{'E' if lo >= 0 else 'W'}{abs(lo):03d}"


def fetch_tile(name: str, cache: Path) -> Path:
    """Scarica una tessera (2-95 MB) una volta sola."""
    cache.mkdir(parents=True, exist_ok=True)
    dest = cache / f"{name}.tif"
    if not dest.exists():
        tmp = dest.with_suffix(".part")
        urllib.request.urlretrieve(URL.format(tile=name), tmp)
        tmp.replace(dest)
    return dest


def classify(window: Any) -> Dict[str, Any]:
    """Da un riquadro di codici WorldCover alla colonna del fascicolo. 0 = nessun dato."""
    import numpy as np

    w = np.asarray(window).ravel()
    w = w[w > 0]
    if w.size == 0:
        return {"label": "nessun dato", "built": None, "crop": None, "dominant": None}
    built, crop = float((w == BUILT).mean()), float((w == CROP).mean())
    vals, counts = np.unique(w, return_counts=True)
    dom = CLASSES.get(int(vals[counts.argmax()]), str(int(vals[counts.argmax()])))
    label = "costruito oggi" if built >= BUILT_MIN else "coltivato oggi" if crop >= CROP_MIN else "nessun uso moderno evidente"
    return {"label": label, "built": round(built, 2), "crop": round(crop, 2), "dominant": dom}


def land_use(cands: List[Dict[str, Any]], cache: Path) -> Dict[str, Dict[str, Any]]:
    """id -> colonna 'uso del suolo oggi' per ogni candidato (servono lat e lon: gira solo in locale)."""
    import rasterio
    from rasterio.windows import Window

    out: Dict[str, Dict[str, Any]] = {}
    by_tile: Dict[str, List[Dict[str, Any]]] = {}
    for c in cands:
        by_tile.setdefault(tile_name(c["lat"], c["lon"]), []).append(c)
    for name, group in sorted(by_tile.items()):
        with rasterio.open(fetch_tile(name, cache)) as src:
            for c in group:
                row, col = src.index(c["lon"], c["lat"])
                win = Window(col - HALF_PX, row - HALF_PX, 2 * HALF_PX + 1, 2 * HALF_PX + 1)
                out[c["id"]] = classify(src.read(1, window=win, boundless=True, fill_value=0))
    return out
