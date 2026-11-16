"""Banco di calibrazione "non naturale" n.1: rilievo a tumulo (tell) sul DEM.

Domanda (CLAUDE.md §13): il DEM gratuito a 30 m sa distinguere un tumulo di
insediamento dal terreno intorno, e con quale tasso di falsi allarmi?

Controllo positivo: Menze & Ur 2012 (PNAS), alto Khabur, Siria NE. 14.324 siti,
CC0, doi:10.7910/DVN/7H8K3N. Le posizioni vengono dalla firma SPETTRALE (ASTER,
antrosuoli) e le altezze da SRTM. Noi misuriamo su Copernicus GLO-30 (TanDEM-X):
sensore diverso sia dalla posizione sia dall'altezza del catalogo.

PRE-REGISTRAZIONE (16 nov 2026, scritta e committata PRIMA di eseguire).
Parametri fissi, nessuna taratura sui dati:
  - sfondo  = mediana su ~1 km (BG_KM), rilievo residuo = DEM - sfondo
  - cella   = CELL_PX x CELL_PX pixel (~300 m); punteggio = max residuo nella cella
  - impronta del rilievo = celle entro FOOT_KM da un sito del catalogo
  - classi  : ALTO  = cella con sito di altezza catalogo >= TALL_M
              BASSO = cella con soli siti piu' bassi o senza altezza
              VUOTO = nessun sito nella cella ne' nelle 8 adiacenti
  - soglia  = 99 percentile dei VUOTI (falsi allarmi 1% per costruzione)
Tile: N36E040 e N36E041, entrambi di test (non c'e' un tile di taratura).

PASSA se, su ciascun tile:
  (a) recall ALTO >= 0.50 alla soglia;
  (b) recall BASSO <= 0.05 (lo strumento vede rilievo, non "magia di catalogo":
      i siti piatti DEVONO restare invisibili al DEM).
Si riporta comunque, e conta piu' di (a): la PRECISIONE = ALTO sopra soglia /
(ALTO + VUOTO sopra soglia). E' il numero che dice cosa succede scansionando al
buio. Se e' bassa, lo strumento ritrova i noti ma non puo' proporne di nuovi.

Cosa NON dice nessun esito: "tumulo = artificiale". Un cono vulcanico, un
inselberg, una duna fissa hanno la stessa firma. Quelli stanno fra i VUOTI
sopra soglia e li separa solo un secondo dato (geologia, spettro, CORONA).
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

BG_KM = 1.0
CELL_PX = 10
FOOT_KM = 5.0
TALL_M = 5.0
FPR = 0.01
PASS_RECALL_TALL = 0.50
PASS_RECALL_LOW = 0.05

SITES_CSV = Path(__file__).resolve().parents[3] / "data" / "controls" / "menze-ur_khabur_sites-data.csv"
UTM_ZONE_EPSG = 32637  # WGS84 / UTM 37N (dichiarato nel readme del dataset)


def residual_relief(dem: np.ndarray, px_m: float = 30.0) -> np.ndarray:
    """DEM meno sfondo mediano a ~BG_KM. Lo sfondo si stima a 1/4 di risoluzione."""
    from scipy import ndimage

    f = 4
    h, w = (dem.shape[0] // f) * f, (dem.shape[1] // f) * f
    d = np.where(np.isfinite(dem[:h, :w]), dem[:h, :w], np.nanmedian(dem))
    small = d.reshape(h // f, f, w // f, f).mean(axis=(1, 3))
    size = max(3, int(round(BG_KM * 1000 / (px_m * f))) | 1)
    bg = ndimage.zoom(ndimage.median_filter(small, size=size, mode="nearest"), f, order=1)
    return d - bg


def cell_scores(res: np.ndarray) -> np.ndarray:
    """Max residuo per cella CELL_PX x CELL_PX."""
    c = CELL_PX
    h, w = (res.shape[0] // c) * c, (res.shape[1] // c) * c
    return res[:h, :w].reshape(h // c, c, w // c, c).max(axis=(1, 3))


def load_sites(path: Path = SITES_CSV) -> List[Tuple[float, float, float]]:
    """(lon, lat, altezza_m | nan). La colonna 'latitude (UTM)' e' il northing."""
    from pyproj import Transformer

    tr = Transformer.from_crs(UTM_ZONE_EPSG, 4326, always_xy=True)
    out = []
    with path.open(encoding="utf-8") as fh:
        rows = csv.reader(fh, skipinitialspace=True)
        next(rows)
        for r in rows:
            lon, lat = tr.transform(float(r[1]), float(r[0]))
            out.append((lon, lat, float(r[6]) if r[6] not in ("NA", "") else float("nan")))
    return out


def label_cells(shape: Tuple[int, int], bbox: Sequence[float],
                sites: Sequence[Tuple[float, float, float]]) -> Dict[str, np.ndarray]:
    """Maschere ALTO / BASSO / VUOTO sulla griglia di celle. bbox = W,S,E,N."""
    from scipy import ndimage

    ny, nx = shape
    w, s, e, n = bbox
    tall = np.zeros(shape, bool)
    low = np.zeros(shape, bool)
    for lon, lat, hgt in sites:
        if not (w <= lon < e and s <= lat < n):
            continue
        i = min(ny - 1, int((n - lat) / (n - s) * ny))
        j = min(nx - 1, int((lon - w) / (e - w) * nx))
        if hgt >= TALL_M:
            tall[i, j] = True
        else:
            low[i, j] = True
    low &= ~tall
    any_site = tall | low
    near = ndimage.binary_dilation(any_site, structure=np.ones((3, 3), bool))
    cell_km = 111.0 * (n - s) / ny
    foot = ndimage.distance_transform_edt(~any_site) * cell_km <= FOOT_KM
    return {"tall": tall, "low": low, "empty": foot & ~near}


def evaluate(scores: np.ndarray, labels: Dict[str, np.ndarray]) -> Dict[str, Any]:
    """Recall, precisione e AUC alla soglia pre-registrata. Nessun parametro libero."""
    t, l, e = scores[labels["tall"]], scores[labels["low"]], scores[labels["empty"]]
    if len(t) < 20 or len(e) < 1000:
        return {"passed": None, "reason": "troppo pochi casi per misurare", "n_tall": len(t), "n_empty": len(e)}
    thr = float(np.quantile(e, 1 - FPR))
    tp, fp = int((t > thr).sum()), int((e > thr).sum())
    # AUC = P(punteggio ALTO > punteggio VUOTO), via ranghi
    order = np.argsort(np.concatenate([t, e]), kind="mergesort")
    ranks = np.empty(len(order)); ranks[order] = np.arange(1, len(order) + 1)
    auc = (ranks[: len(t)].sum() - len(t) * (len(t) + 1) / 2) / (len(t) * len(e))
    r_tall, r_low = tp / len(t), float((l > thr).mean()) if len(l) else float("nan")
    return {
        "n_tall": len(t), "n_low": len(l), "n_empty": len(e),
        "threshold_m": round(thr, 2), "auc": round(float(auc), 3),
        "recall_tall": round(r_tall, 3), "recall_low": round(r_low, 3),
        "false_alarms": fp, "precision": round(tp / (tp + fp), 3) if tp + fp else None,
        "passed": bool(r_tall >= PASS_RECALL_TALL and r_low <= PASS_RECALL_LOW),
    }


def run_tile(lat_s: int, lon_s: int) -> Dict[str, Any]:
    """Un tile GLO-30 reale. None-safe: senza DEM non inventa niente."""
    from core.hydro.measure import fetch_copernicus_tile

    got = fetch_copernicus_tile(lat_s, lon_s)
    if got is None:
        return {"tile": (lat_s, lon_s), "passed": None, "reason": "DEM non disponibile"}
    dem, bbox, url = got
    px_m = 111_000.0 * (bbox[3] - bbox[1]) / dem.shape[0]
    scores = cell_scores(residual_relief(dem, px_m))
    out = evaluate(scores, label_cells(scores.shape, bbox, load_sites()))
    return {"tile": (lat_s, lon_s), "source": url, **out}


if __name__ == "__main__":
    import json
    for tile in ((36, 40), (36, 41)):
        print(json.dumps(run_tile(*tile)))
