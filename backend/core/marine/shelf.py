"""Piattaforma continentale annegata: dove cercare, e perche' NON e' un'acropoli.

Il vincolo che decide tutto, e che il racconto popolare ignora:

    -30 / -130 m   20.000-7.000 anni fa   cacciatori-raccoglitori, primo
                                          neolitico. NIENTE monumenti.
     0  /  -20 m   < 7.000 anni           citta' vere (Pavlopetri, Eracleion)

L'architettura monumentale compare quando il mare si era gia' fermato. Una
citta' monumentale a -100 m e' un'impossibilita' cronologica, non un bersaglio
difficile. L'unica finestra in cui le due si sovrappongono sono le coste in
**subsidenza tettonica**, dove terra abitata di recente e' scesa piu' di quanto
spieghi il solo innalzamento eustatico.

Cosa questo modulo puo' dire: "qui la costa e' rimasta a lungo, l'acqua e'
arrivata in fretta, e il sedimento puo' aver conservato". Cioe' dove mandare un
sonar o un carotaggio.
Cosa NON puo' dire: che ci sia un sito. La batimetria libera ha risoluzione di
centinaia di metri; un villaggio neolitico e' largo cento. Si cercano
**paesaggi**, mai edifici.

Nessun punteggio di questo modulo significa qualcosa da solo: va sempre letto
come percentile contro un null di punti casuali sulla stessa piattaforma
(percentile_vs_null). Un estremo interno esiste sempre — vedi
docs/CALIBRAZIONE.md, otto tentativi che l'hanno imparato a caro prezzo.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

# Curva eustatica globale SEMPLIFICATA: (migliaia di anni fa, metri sul livello
# attuale). Approssima le curve pubblicate standard; il gradino fra 14.5 e 14.0
# ka e' il meltwater pulse 1A.
#
# ATTENZIONE: e' *eustatica*, cioe' globale. Il livello del mare RELATIVO in un
# posto preciso differisce anche di decine di metri per l'aggiustamento
# isostatico glaciale: la superficie del mare e' un'equipotenziale che si
# deforma col carico di ghiaccio e acqua. Per un sito specifico serve una curva
# RSL locale. Qui non ce l'abbiamo, e va detto in ogni output.
SEA_LEVEL_KYR_M: Tuple[Tuple[float, float], ...] = (
    (26.0, -130.0), (21.0, -128.0), (18.0, -120.0), (16.0, -105.0),
    (14.6,  -96.0), (14.2,  -80.0),                      # meltwater pulse 1A
    (13.0,  -70.0), (12.0,  -65.0), (11.0,  -55.0), (10.0, -40.0),
    ( 9.0,  -30.0), ( 8.0,  -20.0), ( 7.0,   -8.0), ( 6.0,  -4.0),
    ( 5.0,   -2.0), ( 2.0,   -0.5), ( 0.0,    0.0),
)

# Fascia verticale in cui il moto ondoso rimaneggia e distrugge.
SURF_BAND_M = 7.0

# Controlli positivi: siti sommersi gia' trovati e pubblicati. Posizioni
# approssimate da letteratura. Se il metodo non li mette in alto, non trovera'
# niente di nuovo — ed e' vietato tararlo su di loro.
KNOWN_SUBMERGED_SITES: Tuple[Dict[str, Any], ...] = (
    {"name": "Atlit-Yam", "lon": 34.935, "lat": 32.693, "depth_m": -10.0,
     "age_kyr": 9.0, "kind": "villaggio neolitico (PPNC), pozzi in pietra, megaliti"},
    {"name": "Bouldnor Cliff", "lon": -1.450, "lat": 50.722, "depth_m": -11.0,
     "age_kyr": 8.0, "kind": "mesolitico, legno lavorato, DNA sedimentario"},
    {"name": "Pavlopetri", "lon": 22.983, "lat": 36.513, "depth_m": -3.5,
     "age_kyr": 3.5, "kind": "citta' dell'eta' del bronzo (subsidenza)"},
)


def sea_level_at(kyr_bp: float) -> float:
    """Livello eustatico a una data, per interpolazione lineare."""
    ks = np.array([k for k, _ in SEA_LEVEL_KYR_M])[::-1]
    ms = np.array([m for _, m in SEA_LEVEL_KYR_M])[::-1]
    return float(np.interp(kyr_bp, ks, ms))


def _curve() -> Tuple[np.ndarray, np.ndarray]:
    ks = np.array([k for k, _ in SEA_LEVEL_KYR_M])[::-1]
    ms = np.array([m for _, m in SEA_LEVEL_KYR_M])[::-1]
    return ks, ms


def drowning_age_kyr(z_m: float) -> Optional[float]:
    """Quando il mare ha superato questa quota, in migliaia di anni fa.

    None se e' ancora emersa (z >= 0) o se non e' mai stata emersa nel periodo
    coperto (sotto il minimo glaciale). Assume che dopo l'ultimo massimo
    glaciale il livello sia salito in modo monotono: vero per questa curva
    semplificata, non esattamente vero nella realta'.
    """
    if z_m >= 0:
        return None
    ks, ms = _curve()          # ks cresce (0 -> 26 ka), ms cala (0 -> -130 m)
    if z_m < float(ms.min()):
        return None            # sotto il minimo glaciale: mai stata terra
    # eta' in funzione della quota: serve x crescente, quindi si ribalta
    return float(np.interp(z_m, ms[::-1], ks[::-1]))


def _time_in_band(z_lo: float, z_hi: float, step_kyr: float = 0.02) -> float:
    """Migliaia di anni in cui il livello del mare e' stato fra due quote."""
    ks, _ = _curve()
    t = np.arange(float(ks.min()), float(ks.max()), step_kyr)
    s = np.array([sea_level_at(x) for x in t])
    return float(np.sum((s >= z_lo) & (s <= z_hi)) * step_kyr)


def coastal_residence_kyr(z_m: float, slope: float, corridor_km: float = 5.0) -> float:
    """Quanto a lungo questo punto e' stato entro corridoio_km dalla riva.

    E' un integrale sulla curva del livello del mare: il punto e' costiero
    finche' il livello sta entro una fascia verticale larga corridoio * pendenza.
    Su una piattaforma piattissima la riva sfreccia via e la residenza e' breve;
    su un pendio ripido resta a lungo — ma il ripido non e' abitabile ne'
    conservativo. L'ottimo e' intermedio, e questa tensione e' voluta.
    """
    if z_m >= 0:
        return 0.0
    half = max(abs(slope) * corridor_km * 1000.0, 1.0)  # metri di quota
    return _time_in_band(z_m - half, z_m + half)


def surf_exposure_kyr(z_m: float, surf_band_m: float = SURF_BAND_M) -> float:
    """Tempo passato nella fascia in cui le onde rimaneggiano. Meno e' meglio:
    se il mare ci passa sopra in fretta, il sito si conserva."""
    if z_m >= 0:
        return 0.0
    return _time_in_band(z_m - surf_band_m, z_m + surf_band_m)


def rapid_drowning_ratio(z_m: float, surf_band_m: float = SURF_BAND_M) -> Optional[float]:
    """Quanto in fretta l'acqua ha attraversato questa quota, rispetto al ritmo
    tipico. >1 = annegamento rapido (impulso di scioglimento) = conservazione
    migliore. E' la ragione per cui certe fasce di profondita' sono
    privilegiate, ed e' una previsione falsificabile: dice DOVE, in verticale.
    """
    if z_m >= 0:
        return None
    t = surf_exposure_kyr(z_m, surf_band_m)
    if t <= 0:
        return None
    ks, ms = _curve()
    total = float(ks.max() - ks.min())
    span = float(ms.max() - ms.min())
    tipico = total * (2 * surf_band_m) / span
    return float(tipico / t)


@dataclass
class ShelfCell:
    """Le componenti, mai un numero solo. Ognuna dice una cosa diversa."""
    z_m: float
    slope: float
    drowned_kyr: Optional[float]
    residence_kyr: float       # quanto e' stato costiero -> occupazione
    surf_kyr: float            # quanto e' stato nella risacca -> distruzione
    rapid_ratio: Optional[float]  # >1 annegamento rapido -> conservazione


def shelf_cell(z_m: float, slope: float, corridor_km: float = 5.0) -> ShelfCell:
    return ShelfCell(
        z_m=float(z_m),
        slope=float(slope),
        drowned_kyr=drowning_age_kyr(z_m),
        residence_kyr=coastal_residence_kyr(z_m, slope, corridor_km),
        surf_kyr=surf_exposure_kyr(z_m),
        rapid_ratio=rapid_drowning_ratio(z_m),
    )


# Pendenza oltre la quale il terreno non e' ne' abitabile ne' conservativo.
SLOPE_MAX = 0.05  # 5%, ~3 gradi


def raw_score(cell: ShelfCell) -> Optional[float]:
    """Punteggio grezzo = occupazione x conservazione, penalizzato dal ripido.

    NON significa niente da solo. Va letto con percentile_vs_null() contro
    punti casuali della stessa piattaforma. Un massimo interno esiste sempre:
    e' la lezione di docs/CALIBRAZIONE.md, pagata con otto tentativi.
    """
    if cell.drowned_kyr is None or cell.rapid_ratio is None:
        return None
    if cell.residence_kyr <= 0:
        return None
    ripido = 1.0 / (1.0 + (abs(cell.slope) / SLOPE_MAX) ** 2)
    return float(cell.residence_kyr * cell.rapid_ratio * ripido)


def percentile_vs_null(score: float, null_scores: Sequence[float]) -> Optional[float]:
    """Dove sta questo punteggio nella distribuzione di punti casuali della
    stessa piattaforma. Sotto i 30 campioni non si risponde: meglio niente che
    un percentile inventato."""
    vals = np.array([s for s in null_scores if s is not None and np.isfinite(s)])
    if vals.size < 30:
        return None
    return float((vals < score).mean() * 100.0)


def gmrt_tile(bbox: Sequence[float], timeout: int = 90):
    """Batimetria+topografia GMRT per una bbox. GeoTIFF, nessuna chiave.
    None se la rete o rasterio falliscono: non si inventa il fondale."""
    import io
    import requests

    lon0, lat0, lon1, lat1 = (float(v) for v in bbox)
    url = (
        "https://www.gmrt.org/services/GridServer"
        f"?minlongitude={lon0}&maxlongitude={lon1}"
        f"&minlatitude={lat0}&maxlatitude={lat1}"
        "&format=geotiff&resolution=max"
    )
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        import rasterio
        with rasterio.MemoryFile(io.BytesIO(r.content)) as mem:
            with mem.open() as src:
                arr = src.read(1).astype(np.float64)
                b = src.bounds
                return arr, [float(b.left), float(b.bottom), float(b.right), float(b.top)]
    except Exception:
        return None


# Impulso di scioglimento 1A: 14-18 m in <=340 anni dal 14.65 ka, dai coralli
# di Tahiti e Barbados (Deschamps et al.). Revisione recente da Tahiti: 13.8
# +- 1.3 m, forse iniziato 300 anni prima. Si usa il valore centrale.
MWP1A = {
    "start_kyr": 14.65,
    "end_kyr": 14.31,
    "rise_m": 16.0,
    "source": "coralli Tahiti/Barbados; 14-18 m in <=340 anni",
}

# Il minimo glaciale: sotto questa quota nulla e' MAI stato terra emersa in
# questo ciclo. Non e' un limite dello strumento, e' un limite del mondo.
GLACIAL_LOWSTAND_M = -130.0


def was_ever_land(z_m: float) -> bool:
    """Se questa quota sia mai stata terra emersa nell'ultimo ciclo glaciale.

    Serve a chiudere un errore ricorrente: cercare paleocoste a -200 o -300 m.
    Il mare non e' mai sceso cosi'. Sotto il ciglio della piattaforma c'e'
    scarpata continentale, che era fondale anche al massimo glaciale.
    """
    return GLACIAL_LOWSTAND_M <= z_m < 0.0


def vertical_rate_m_per_yr(kyr_a: float, kyr_b: float) -> Optional[float]:
    """Ritmo di innalzamento fra due date, in metri all'anno."""
    if kyr_a == kyr_b:
        return None
    dz = sea_level_at(min(kyr_a, kyr_b)) - sea_level_at(max(kyr_a, kyr_b))
    dt = abs(kyr_a - kyr_b) * 1000.0
    return float(dz / dt)


def horizontal_retreat_m_per_yr(gradient: float, vertical_rate_m_per_yr: float) -> Optional[float]:
    """Quanti metri di costa si perdono ogni anno.

    E' il criterio della MEMORIA, distinto da quello della conservazione: un
    innalzamento verticale modesto diventa un arretramento orizzontale
    spettacolare su una piattaforma piatta. 4.7 cm/anno su pendenza 1:5000
    fanno 235 m di costa persi ogni anno — chilometri nell'arco di una vita.
    Quello si vede accadere, e si racconta.

    None se la pendenza e' nulla: li' l'allagamento non e' un arretramento ma
    un evento istantaneo su tutta la superficie, e questa formula non vale.
    """
    if gradient <= 0:
        return None
    return float(vertical_rate_m_per_yr / gradient)


def witnessed_loss_km(gradient: float, vertical_rate_m_per_yr: float,
                      years: float = 60.0) -> Optional[float]:
    """Costa persa nell'arco di una vita umana. La soglia del ricordo."""
    r = horizontal_retreat_m_per_yr(gradient, vertical_rate_m_per_yr)
    return None if r is None else float(r * years / 1000.0)
