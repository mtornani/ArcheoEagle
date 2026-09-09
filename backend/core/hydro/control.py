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

STATO: il controllo positivo FALLISCE (9 set 2026). Lo strumento non ha ancora
dimostrato di riconoscere la sponda documentata. Finche' e' cosi', nessuna
schermata e nessun export puo' dire "sponda individuata" — solo "isolinea
disegnata". Il registro completo dei tentativi sta in docs/CALIBRAZIONE.md.
"""
from __future__ import annotations

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


def _elongation(mask: np.ndarray, stride: int = 2) -> float:
    """Quanto la banda a questa quota e' una linea invece che una macchia.

    Una sponda e' lunga e sottile; uno scarpato qualunque e' un chiazzo.
    Su una linea di lunghezza L e spessore 1 il valore vale ~L; su un quadrato
    vale ~2, indipendentemente dal lato. Si guarda la componente connessa piu'
    grande: una banda spezzata in mille frammenti non e' una sponda.
    """
    from scipy import ndimage

    small = mask[::stride, ::stride]
    if small.sum() < 4:
        return 0.0
    lab, n = ndimage.label(small)
    if n == 0:
        return 0.0
    sizes = ndimage.sum(small, lab, range(1, n + 1))
    ys, xs = np.nonzero(lab == int(np.argmax(sizes)) + 1)
    area = ys.size
    if area < 4:
        return 0.0
    span = float(np.hypot(ys.max() - ys.min(), xs.max() - xs.min()))
    return span * span / area


def _slope_map(dem: np.ndarray) -> np.ndarray:
    """Pendenza in m/pixel. I buchi si riempiono con la mediana solo per
    derivare: non inventiamo quota, e la banda viene comunque mascherata
    sui pixel originali validi."""
    finite = np.isfinite(dem)
    if not finite.any():
        return np.full(dem.shape, np.nan)
    filled = np.where(finite, dem, np.nanmedian(dem))
    gy, gx = np.gradient(filled)
    return np.sqrt(gy * gy + gx * gx)


def level_stats(
    dem: np.ndarray,
    level_m: float,
    *,
    band_m: float = 0.5,
    window_m: float = 25.0,
    slope: Optional[np.ndarray] = None,
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
        slope = _slope_map(dem)
    return LevelStats(
        level_m=float(level_m),
        occupancy=n_band / n_window,
        mean_slope=float(np.nanmean(slope[band])),
        elongation=_elongation(band),
        n_band=n_band,
    )


def step_profile(
    dem: np.ndarray,
    levels: Sequence[float],
    *,
    band_m: float = 0.5,
    window_m: float = 25.0,
) -> List[LevelStats]:
    """Profilo su piu' quote. La pendenza si calcola una volta sola."""
    slope = _slope_map(dem)
    out: List[LevelStats] = []
    for lvl in levels:
        st = level_stats(dem, lvl, band_m=band_m, window_m=window_m, slope=slope)
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
    target = level_stats(dem, level_m, band_m=band_m, window_m=window_m)
    if target is None:
        return {
            "level_m": float(level_m),
            "step_score": None,
            "reason": "nessun terreno a questa quota nel tile",
        }

    slope = _slope_map(dem)
    ref: List[LevelStats] = []
    n = int(sweep_m / sweep_step_m)
    for k in range(-n, n + 1):
        if k == 0:
            continue  # il bersaglio non fa parte del proprio riferimento
        lvl = level_m + k * sweep_step_m
        st = level_stats(dem, lvl, band_m=band_m, window_m=window_m, slope=slope)
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
        out["positive"] = step_score(got[0], level_m)

    got_ctrl = fetch_copernicus_tile(*CONTROL_TILE)
    if got_ctrl is None:
        out["negative"] = {"error": "tile di controllo non scaricabile"}
    else:
        out["negative"] = step_score(got_ctrl[0], level_m)

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
