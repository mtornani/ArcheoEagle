"""Il controllo che e' mancato a Miotti: "non nel registro" non vuol dire "sconosciuto".

Ogni candidato viene confrontato con elenchi di siti noti, e ogni rilievo porta
con se' la lista di chi l'ha gia' analizzato. Un candidato su un rilievo gia'
studiato si PRESUME gia' visto, finche' non si dimostra il contrario.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple

SHIPPED = Path(__file__).resolve().parent / "data" / "known_sites.csv"

# Chi ha gia' guardato questi dati. Si aggiorna a mano, con la fonte.
PRIOR_WORK = {
    "G-LiHT Yucatan 2013": [
        "Estrada-Belli et al. 2025 — insediamento maya su 95.000 km2 di LiDAR NASA G-LiHT",
        "Britton 2026 — catalogo di 57.181 strutture su questi stessi transetti riprocessati (catalogo non pubblico al 16 nov 2026)",
        "Britton et al. 2026, J Archaeol Method Theory 33:15 — rilevamento con reti profonde su G-LiHT",
    ],
}


def load_sites(extra_dir: Path | None = None) -> List[Tuple[str, float, float, str]]:
    """(nome, lat, lon, fonte). Elenco fornito + ogni CSV nome,lat,lon,fonte in extra_dir."""
    out: List[Tuple[str, float, float, str]] = []
    for p in [SHIPPED] + (sorted(extra_dir.glob("*.csv")) if extra_dir and extra_dir.exists() else []):
        with p.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                try:
                    out.append((r["name"], float(r["lat"]), float(r["lon"]), r.get("source") or p.stem))
                except (KeyError, ValueError):
                    continue
    return out


def km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(a))


def nearest(lat: float, lon: float, sites: List[Tuple[str, float, float, str]]) -> Dict[str, Any] | None:
    if not sites:
        return None
    d, s = min((km(lat, lon, s[1], s[2]), s) for s in sites)
    return {"name": s[0], "km": round(d, 2), "source": s[3]}


def status(cand: Dict[str, Any], sites: List[Tuple[str, float, float, str]], survey: str) -> Dict[str, Any]:
    """Cosa si sa gia'. Tre gradini, nessuno dei quali e' 'nuovo'."""
    near = nearest(cand["lat"], cand["lon"], sites)
    prior = PRIOR_WORK.get(survey, [])
    if near and near["km"] <= 2.0:
        label = "sito_noto_vicino"
    elif prior:
        label = "rilievo_gia_analizzato"
    else:
        label = "non_negli_elenchi_consultati"
    return {"label": label, "nearest": near, "prior_work": prior}
