"""Catalogo dei rilievi LiDAR pubblici che Vaglio sa scaricare da solo.

Oggi: i 456 transetti NASA G-LiHT sullo Yucatan (2013), riprocessati a 33 cm
da B. J. Britton (2026) e distribuiti da OpenTopography in pubblico dominio
(PDDL), senza chiave. 1.273 km2. Sono gli stessi dati della "scoperta" di
Miotti (nov 2026) e del lavoro di Estrada-Belli et al. (2025).
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

DATA = Path(__file__).resolve().parent / "data" / "transects.json"


def load() -> Dict[str, Any]:
    return json.loads(DATA.read_text(encoding="utf-8"))


def transects() -> List[Dict[str, Any]]:
    return load()["transects"]


def fetch_dtm(t: Dict[str, Any], cache: Path) -> Path:
    """Scarica il DTM di un transetto (35-85 MB). Riusa la copia locale se intera."""
    cache.mkdir(parents=True, exist_ok=True)
    dest = cache / (t["id"] + ".tif")
    if dest.exists() and dest.stat().st_size > 0.95 * t["dtm_mb"] * 1e6:
        return dest
    tmp = dest.with_suffix(".part")
    urllib.request.urlretrieve(load()["base_url"] + t["dtm"], tmp)
    tmp.replace(dest)
    return dest
