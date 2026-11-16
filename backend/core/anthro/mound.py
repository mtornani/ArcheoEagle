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

ESITO v1 (16 nov 2026, commit 174a87f): FAIL su entrambi i tile.
  N36E040: recall ALTO 0.016, precisione 0.009, soglia 28.5 m, AUC 0.856
  N36E041: recall ALTO 0.054, precisione 0.008, soglia 31.5 m, AUC 0.934
Diagnosi: il segnale c'e' (AUC), ma la soglia all'1% la fissano colline e
incisioni naturali (~30 m): un tell di 5-20 m ci annega sotto. Il rilievo
grezzo non separa. E il criterio (b) era disegnato male: BASSO mescola siti
piatti e tumuli di 1-5 m, che il DEM vede legittimamente.

PRE-REGISTRAZIONE v2 (16 nov 2026, dopo esplorazione DICHIARATA sui due tile
sopra, che da ora sono bruciati e non contano piu' come test).
  - punteggio = residuo / (rugosita' locale + ROUGH_FLOOR_M), dove rugosita' =
    mediana su ~3 km del |residuo| medio di cella. Cioe': "quanto sporge
    rispetto a quanto e' mosso il terreno li' intorno". Tutto il terreno, nessun
    filtro di pianura.
  - PIATTO = cella con soli siti senza altezza o altezza 0 (sostituisce BASSO
    nel criterio b). I tumuli 0-5 m si riportano ma non entrano nel criterio.
  - soglia = 99 percentile dei VUOTI, come prima.
Tile di test, mai guardati: N37E040, N37E041, N36E042.
PASSA v2 se su ciascuno: recall ALTO >= 0.40 e recall PIATTO <= 0.05.
(0.40 e' fissato sapendo che l'esplorazione dava 0.375 e 0.554: l'asticella
e' vicina all'osservato, non sotto.)

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
ROUGH_KM = 3.0
ROUGH_FLOOR_M = 0.5
PASS_RECALL_TALL_V2 = 0.40

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


def cell_scores_v2(res: np.ndarray, px_m: float = 30.0) -> np.ndarray:
    """Max residuo di cella diviso la rugosita' del terreno intorno (adimensionale)."""
    from scipy import ndimage

    c = CELL_PX
    s = cell_scores(res)
    mean_abs = np.abs(res[: s.shape[0] * c, : s.shape[1] * c]).reshape(s.shape[0], c, s.shape[1], c).mean(axis=(1, 3))
    size = max(3, int(round(ROUGH_KM * 1000 / (px_m * c))) | 1)
    return s / (ndimage.median_filter(mean_abs, size=size, mode="nearest") + ROUGH_FLOOR_M)


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
    mid = np.zeros(shape, bool)  # tumuli 0-5 m: visibili al DEM, fuori dal criterio v2
    for lon, lat, hgt in sites:
        if not (w <= lon < e and s <= lat < n):
            continue
        i = min(ny - 1, int((n - lat) / (n - s) * ny))
        j = min(nx - 1, int((lon - w) / (e - w) * nx))
        if hgt >= TALL_M:
            tall[i, j] = True
        else:
            low[i, j] = True
            mid[i, j] |= hgt > 0
    low &= ~tall
    any_site = tall | low
    near = ndimage.binary_dilation(any_site, structure=np.ones((3, 3), bool))
    cell_km = 111.0 * (n - s) / ny
    foot = ndimage.distance_transform_edt(~any_site) * cell_km <= FOOT_KM
    return {"tall": tall, "low": low, "flat": low & ~mid, "empty": foot & ~near}


def evaluate(scores: np.ndarray, labels: Dict[str, np.ndarray], low: str = "low",
             min_recall: float = PASS_RECALL_TALL) -> Dict[str, Any]:
    """Recall, precisione e AUC alla soglia pre-registrata. Nessun parametro libero."""
    t, l, e = scores[labels["tall"]], scores[labels[low]], scores[labels["empty"]]
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
        "threshold": round(thr, 2), "auc": round(float(auc), 3),
        "recall_tall": round(r_tall, 3), "recall_low": round(r_low, 3),
        "false_alarms": fp, "precision": round(tp / (tp + fp), 3) if tp + fp else None,
        "passed": bool(r_tall >= min_recall and r_low <= PASS_RECALL_LOW),
    }


def run_tile(lat_s: int, lon_s: int, version: int = 2) -> Dict[str, Any]:
    """Un tile GLO-30 reale. None-safe: senza DEM non inventa niente."""
    from core.hydro.measure import fetch_copernicus_tile

    got = fetch_copernicus_tile(lat_s, lon_s)
    if got is None:
        return {"tile": (lat_s, lon_s), "passed": None, "reason": "DEM non disponibile"}
    dem, bbox, url = got
    px_m = 111_000.0 * (bbox[3] - bbox[1]) / dem.shape[0]
    res = residual_relief(dem, px_m)
    if version == 1:
        scores = cell_scores(res)
        out = evaluate(scores, label_cells(scores.shape, bbox, load_sites()))
    else:
        scores = cell_scores_v2(res, px_m)
        out = evaluate(scores, label_cells(scores.shape, bbox, load_sites()), "flat", PASS_RECALL_TALL_V2)
    return {"tile": (lat_s, lon_s), "version": version, "source": url, **out}


if __name__ == "__main__":
    import json
    for tile in ((37, 40), (37, 41), (36, 42)):  # v2: tile mai guardati
        print(json.dumps(run_tile(*tile)))
