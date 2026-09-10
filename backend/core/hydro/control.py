"""Calibrazione dello strumento: prima di misurare una sponda ignota,
dimostra di saperne riconoscere una nota.

Il resto del codice sa disegnare l'isolinea a quota z. Nessuno finora
verificava che quella quota sia *speciale* nel terreno: un'isolinea esiste
a qualunque quota, anche dove non c'e' niente da vedere.

Qui il test e' auto-controllato: la quota bersaglio viene confrontata con le
quote vicine **nello stesso tile**, non con altri tile. Confrontare tile
diversi confonde il segnale con la topografia regionale — misurato, e
scartato, il 9 set 2026 (vedi docs/CALIBRAZIONE.md).

Controllo positivo: Bama Ridge (Borno, Nigeria), paleosponda del Mega-Chad
gia' mappata in letteratura, creste a 320/335/338 m, datazione OSL
6.1+-0.54 - 9.6+-0.7 ka.

Cosa dice step_score: "a questa quota, in questo tile, il terreno si comporta
come un gradino, piu' che alle quote vicine".
Cosa NON dice: "qui c'e' una sponda". Uno scarpato di faglia, un fronte
montuoso o un bordo di duna danno la stessa firma. Il salto da gradino a
sponda lo fa la letteratura o il campo, non questa funzione.

STATO: il controllo positivo FALLISCE (9 set 2026), dopo sei statistiche
diverse. Lo strumento non ha dimostrato di riconoscere la sponda documentata.
Finche' e' cosi', nessuna schermata e nessun export puo' dire "sponda
individuata" — solo "isolinea disegnata".

Diagnosi strutturale: tutte e sei aggregano sull'intera scena, ma a una data
quota un tile produce 2.000-14.000 frammenti di contorno e la sponda e' UNO di
quelli. Nessuna statistica globale vede un oggetto che pesa l'1% del proprio
input. Serve isolare il lineamento e poi misurarlo, non un settimo aggregato.
Registro completo dei sei tentativi in docs/CALIBRAZIONE.md.
"""
from __future__ import annotations

import math

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

# Controllo positivo. La letteratura e' la fonte, non il nostro DEM.
BAMA_RIDGE: Dict[str, Any] = {
    "name": "Bama Ridge",
    "tile": (11, 13),  # Copernicus GLO-30, angolo SW: lat 11-12, lon 13-14
    "levels_m": (320.0, 335.0, 338.0),
    "grade": "literature",
    "source": (
        "Bama Beach Ridge, Bornu sub-basin, NE Nigeria — paleosponda Mega-Chad, "
        "creste 320/335/338 m, OSL 6.1+-0.54 / 9.6+-0.7 ka"
    ),
}

# Controllo negativo: terreno che attraversa i 320 m, nessuna sponda mappata li'.
CONTROL_TILE: Tuple[int, int] = (15, 18)

# Un gradino va dichiarato solo se e' anomalo su ENTRAMBE le statistiche.
# Soglia conservativa in unita' di MAD: sotto, si dice "nessun gradino".
STEP_SCORE_THRESHOLD = 2.0


@dataclass
class LevelStats:
    """Come si comporta il terreno a una quota."""
    level_m: float
    occupancy: float    # px nella banda / px nella finestra. Diagnostica, non punteggio
    mean_slope: float   # pendenza media nella banda (m per pixel). Alto = ripido
    elongation: float   # forma della banda: linea lunga -> alto, macchia -> ~2
    n_band: int


def _elongation(mask: np.ndarray, bbox: Optional[BBox] = None) -> float:
    """Quanto la banda a questa quota e' una linea invece che una macchia.

    ATTENZIONE: statistica confondibile, vedi docs/CALIBRAZIONE.md. Una macchia
    estesa che attraversa il tile prende un punteggio alto quanto una linea
    sottile. Resta nel punteggio solo perche' l'alternativa e' un test a
    statistica singola, e il verdetto e' comunque "fallito".

    Due bug corretti il 9 set 2026, entrambi distruggevano *esattamente* le
    linee sottili diagonali, cioe' la forma del Bama Ridge:
    - la decimazione `mask[::2, ::2]` spezzava in puntini una linea larga 1-3 px;
    - `ndimage.label` di default usa la connettivita' a 4, e una linea diagonale
      sottile si tocca solo negli angoli: veniva letta come mille frammenti.
    Correggerli non ha fatto passare il controllo (la 320 m resta bassa): erano
    bug veri, ma non erano la causa del fallimento.
    """
    from scipy import ndimage

    small = mask
    if small.sum() < 4:
        return 0.0
    lab, n = ndimage.label(small, structure=np.ones((3, 3), bool))
    if n == 0:
        return 0.0
    sizes = ndimage.sum(small, lab, range(1, n + 1))
    ys, xs = np.nonzero(lab == int(np.argmax(sizes)) + 1)
    area = ys.size
    if area < 4:
        return 0.0
    px = pixel_metres(bbox, mask.shape)
    if px is None:
        span = float(np.hypot(ys.max() - ys.min(), xs.max() - xs.min()))
        return span * span / area
    dx, dy = px
    dxm = float(np.mean(dx[ys.min():ys.max() + 1])) if ys.max() >= ys.min() else float(dx[0])
    span = float(np.hypot((ys.max() - ys.min()) * dy, (xs.max() - xs.min()) * dxm))
    area_m2 = area * dxm * dy
    return span * span / area_m2


# Raggio terrestre come nel resto del repo (paleorivers.haversine_km).
EARTH_R_M = 6371000.0


def pixel_metres(bbox: Optional[BBox], shape: Tuple[int, int]) -> Optional[Tuple[np.ndarray, float]]:
    """Larghezza (per riga) e altezza di un pixel, in metri.

    Il DEM sta in EPSG:4326, cioe' in *gradi*: un pixel in longitudine e uno in
    latitudine non misurano lo stesso. Trattare la griglia come euclidea usa un
    righello che si accorcia andando verso i poli — 1.4% a lat 11, 14% a lat 32.
    Piccolo dentro un tile, ma rende NON confrontabili corridoi a latitudini
    diverse, che e' esattamente cio' che il tool fa. Il resto del repo usa gia'
    la metrica sferica (haversine_km); questo modulo no, fino al 9 set 2026.

    None se manca la bbox: i test sintetici lavorano su array senza georeferenza
    e li' il pixel e' l'unita', dichiarata.
    """
    if bbox is None:
        return None
    h, w = shape
    lon0, lat0, lon1, lat1 = (float(v) for v in bbox)
    dlat = abs(lat1 - lat0) / max(h, 1)
    dlon = abs(lon1 - lon0) / max(w, 1)
    rad = math.radians(1.0)
    # latitudine al centro di ogni riga (lat1 = bordo nord)
    rows = lat1 - (np.arange(h) + 0.5) * dlat
    dx = EARTH_R_M * rad * dlon * np.cos(np.radians(rows))
    dy = EARTH_R_M * rad * dlat
    return dx, float(dy)


def _slope_map(dem: np.ndarray, bbox: Optional[BBox] = None) -> np.ndarray:
    """Pendenza adimensionale (m/m) se c'e' la bbox, in m/pixel senza.

    I buchi si riempiono con la mediana solo per derivare: non inventiamo quota,
    e la banda viene comunque mascherata sui pixel originali validi.
    """
    finite = np.isfinite(dem)
    if not finite.any():
        return np.full(dem.shape, np.nan)
    filled = np.where(finite, dem, np.nanmedian(dem))
    gy, gx = np.gradient(filled)
    px = pixel_metres(bbox, dem.shape)
    if px is not None:
        dx, dy = px
        gx = gx / dx[:, None]
        gy = gy / dy
    return np.sqrt(gy * gy + gx * gx)


def level_stats(
    dem: np.ndarray,
    level_m: float,
    *,
    band_m: float = 0.5,
    window_m: float = 25.0,
    slope: Optional[np.ndarray] = None,
    bbox: Optional[BBox] = None,
) -> Optional[LevelStats]:
    """Statistiche a una quota. None se il terreno a quella quota non c'e':
    zero pixel non e' un gradino, e' assenza di dato."""
    finite = np.isfinite(dem)
    if not finite.any():
        return None
    delta = np.abs(dem - level_m)
    band = finite & (delta <= band_m)
    n_band = int(band.sum())
    if n_band == 0:
        return None
    window = finite & (delta <= window_m)
    n_window = int(window.sum())
    if n_window == 0:
        return None
    if slope is None:
        slope = _slope_map(dem, bbox)
    return LevelStats(
        level_m=float(level_m),
        occupancy=n_band / n_window,
        mean_slope=float(np.nanmean(slope[band])),
        elongation=_elongation(band, bbox),
        n_band=n_band,
    )


def step_profile(
    dem: np.ndarray,
    levels: Sequence[float],
    *,
    band_m: float = 0.5,
    window_m: float = 25.0,
    bbox: Optional[BBox] = None,
) -> List[LevelStats]:
    """Profilo su piu' quote. La pendenza si calcola una volta sola."""
    slope = _slope_map(dem, bbox)
    out: List[LevelStats] = []
    for lvl in levels:
        st = level_stats(dem, lvl, band_m=band_m, window_m=window_m, slope=slope, bbox=bbox)
        if st is not None:
            out.append(st)
    return out


def _mad(values: np.ndarray) -> float:
    """Deviazione robusta, riscalata per essere confrontabile a una sigma."""
    med = np.median(values)
    return float(np.median(np.abs(values - med)) * 1.4826)


def step_score(
    dem: np.ndarray,
    level_m: float,
    *,
    sweep_m: float = 40.0,
    sweep_step_m: float = 2.0,
    band_m: float = 0.5,
    window_m: float = 25.0,
    bbox: Optional[BBox] = None,
) -> Dict[str, Any]:
    """Quanto la quota si comporta da gradino rispetto alle quote vicine.

    Il punteggio e' una dimensione dell'effetto (unita' di MAD), non un
    percentile: un percentile mette sempre qualcosa al primo posto, anche
    dentro il rumore puro — proprio il difetto che questo modulo esiste per
    non ripetere. Una rampa a pendenza costante deve dare ~0 a ogni quota.

    step_score = min(slope_z, elongation_z): servono entrambe le condizioni,
    ripido E lungo. Il minimo e' la scelta conservativa.

    Storia di questa scelta, perche' conti: la prima versione usava
    min(occupancy_z, slope_z) e il controllo positivo l'ha bocciata
    (Bama 1.56 contro soglia 2.0). Diagnosi: la pendenza separava benissimo
    (+9.9 sigma sul Bama contro -1.4 sul controllo) mentre l'occupazione no
    (+0.8 contro -0.8), e trascinava giu' il minimo. L'occupazione confonde
    "gradino ripido" con "terreno che a quella quota quasi non arriva" — lo
    stesso difetto gia' visto sull'istogramma. E' stata sostituita dalla
    continuita' laterale, non e' stata spostata la soglia. L'occupazione
    resta nell'output come diagnostica.

    Nota: le quote adiacenti fanno parte dello stesso gradino e gonfiano il
    riferimento, quindi il punteggio sottostima. L'errore va in quella
    direzione apposta.
    """
    target = level_stats(dem, level_m, band_m=band_m, window_m=window_m, bbox=bbox)
    if target is None:
        return {
            "level_m": float(level_m),
            "step_score": None,
            "reason": "nessun terreno a questa quota nel tile",
        }

    slope = _slope_map(dem, bbox)
    ref: List[LevelStats] = []
    n = int(sweep_m / sweep_step_m)
    for k in range(-n, n + 1):
        if k == 0:
            continue  # il bersaglio non fa parte del proprio riferimento
        lvl = level_m + k * sweep_step_m
        st = level_stats(dem, lvl, band_m=band_m, window_m=window_m, slope=slope, bbox=bbox)
        if st is not None:
            ref.append(st)

    if len(ref) < 8:
        return {
            "level_m": float(level_m),
            "step_score": None,
            "reason": f"quote di riferimento insufficienti ({len(ref)})",
        }

    occ = np.array([r.occupancy for r in ref])
    slp = np.array([r.mean_slope for r in ref])
    elo = np.array([r.elongation for r in ref])
    occ_mad, slp_mad, elo_mad = _mad(occ), _mad(slp), _mad(elo)
    if slp_mad <= 0 or elo_mad <= 0:
        return {
            "level_m": float(level_m),
            "step_score": None,
            "reason": "nessuna dispersione nel riferimento: non discrimina",
        }

    # positivo = piu' ripido del normale / piu' lungo del normale
    slope_z = float((target.mean_slope - np.median(slp)) / slp_mad)
    elongation_z = float((target.elongation - np.median(elo)) / elo_mad)
    score = float(min(slope_z, elongation_z))
    # diagnostica, non entra nel punteggio: vedi docstring
    occupancy_z = (
        float((np.median(occ) - target.occupancy) / occ_mad) if occ_mad > 0 else None
    )

    return {
        "level_m": float(level_m),
        "step_score": round(score, 2),
        "slope_z": round(slope_z, 2),
        "elongation_z": round(elongation_z, 2),
        "occupancy_z": round(occupancy_z, 2) if occupancy_z is not None else None,
        "occupancy": round(target.occupancy, 5),
        "mean_slope": round(target.mean_slope, 4),
        "elongation": round(target.elongation, 2),
        "n_band": target.n_band,
        "n_reference_levels": len(ref),
        "is_step": bool(score >= STEP_SCORE_THRESHOLD),
        "puoi_dire": (
            "a questa quota il terreno e' piu' ripido e la banda piu' continua "
            "che alle quote vicine dello stesso tile"
        ),
        "non_puoi_dire": (
            "che sia una sponda: faglia, fronte montuoso e bordo di duna "
            "danno la stessa firma"
        ),
    }


def run_positive_control(level_m: float = 320.0) -> Dict[str, Any]:
    """Fa girare il test sul Bama Ridge e sul tile di controllo. Tocca la rete.

    Se lo strumento non trova il gradino dove la letteratura lo mette, quello
    che dice sulle sponde ignote non vale niente. E' il punto del controllo.
    """
    from core.hydro.measure import fetch_copernicus_tile

    out: Dict[str, Any] = {"level_m": level_m, "reference": BAMA_RIDGE}

    got = fetch_copernicus_tile(*BAMA_RIDGE["tile"])
    if got is None:
        out["positive"] = {"error": "tile Bama non scaricabile"}
    else:
        out["positive"] = step_score(got[0], level_m, bbox=got[1])

    got_ctrl = fetch_copernicus_tile(*CONTROL_TILE)
    if got_ctrl is None:
        out["negative"] = {"error": "tile di controllo non scaricabile"}
    else:
        out["negative"] = step_score(got_ctrl[0], level_m, bbox=got_ctrl[1])

    pos = (out.get("positive") or {}).get("step_score")
    neg = (out.get("negative") or {}).get("step_score")
    if pos is None or neg is None:
        out["verdict"] = "incompleto: manca un tile, nessun verdetto"
    elif pos >= STEP_SCORE_THRESHOLD and neg < STEP_SCORE_THRESHOLD:
        out["verdict"] = "passato: gradino dove la letteratura lo mette, non nel controllo"
    elif pos < STEP_SCORE_THRESHOLD:
        out["verdict"] = "fallito: nessun gradino sulla sponda documentata"
    else:
        out["verdict"] = "ambiguo: gradino anche nel controllo, il test non separa"
    return out


def run_lineament_control(level_m: float = 320.0) -> Dict[str, Any]:
    """Traced polylines vs polar-sort, and whether they join across a tile edge.

    Does not say 'sponda individuata'. Reports lengths and joins. Touches network.
    """
    from core.hydro.lineament import compare_methods, join_count, summarize
    from core.hydro.measure import fetch_copernicus_tile, shoreline_from_dem

    pairs = {
        "bama": (BAMA_RIDGE["tile"], (11, 14)),  # ridge runs SE toward east
        "control": (CONTROL_TILE, (15, 19)),
        "basin": ((13, 14), (13, 15)),  # modern lake floor, not the outer rim
    }
    out: Dict[str, Any] = {"level_m": level_m, "pairs": {}}
    for name, (t0, t1) in pairs.items():
        got0 = fetch_copernicus_tile(*t0)
        got1 = fetch_copernicus_tile(*t1)
        rec: Dict[str, Any] = {"tiles": [list(t0), list(t1)]}
        if got0 is None or got1 is None:
            rec["error"] = "tile non scaricabile"
            out["pairs"][name] = rec
            continue
        dem0, bbox0, _ = got0
        dem1, bbox1, _ = got1
        rec["a"] = compare_methods(dem0, bbox0, level_m)
        rec["b"] = compare_methods(dem1, bbox1, level_m)
        rec["a"].pop("traced_lines", None)
        rec["a"].pop("polar_lines", None)
        rec["b"].pop("traced_lines", None)
        rec["b"].pop("polar_lines", None)
        rec["a"]["zmin"] = float(np.nanmin(dem0))
        rec["a"]["zmax"] = float(np.nanmax(dem0))
        rec["b"]["zmin"] = float(np.nanmin(dem1))
        rec["b"]["zmax"] = float(np.nanmax(dem1))
        lines0 = shoreline_from_dem(dem0, bbox0, level_m)
        lines1 = shoreline_from_dem(dem1, bbox1, level_m)
        rec["joins"] = join_count(lines0, bbox0, lines1, bbox1)
        rec["traced_a"] = summarize(lines0, bbox0)
        rec["traced_b"] = summarize(lines1, bbox1)
        out["pairs"][name] = rec
    return out
