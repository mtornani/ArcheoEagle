"""Cap Timiris Canyon is the Tamanrasset mouth. The core is the flight recorder.

First principles, Carlson/Musk edition:
- Water moves sediment. A dead river leaves a dead canyon. A live river
  dumps dated beds. Cap Timiris is 2.5 km wide and a kilometre deep, plugged
  into a paleoriver that would rank ~12th on Earth if it still ran
  (Skonieczny 2015). That is the scale. Plato is a column, not a map.
- Si/Al is a quartz-vs-clay stick. Wien used it to mark turbidites. A glacial
  sand cannon spikes Si. A vegetated mud river should not look like that cannon.
- T1 on GeoB8502-2 sits at 10.1 ka — inside the African Humid Period. Compare
  it to the pelagite above it and to the Pleistocene Si bombs deeper in the
  same hole. If T1 equals the bombs, the AHP pulse is just another canyon fill.
  If T1 is a modest bump, the humid-period river is mud, not a dust storm.

Does not say a city was here. Says whether the chemistry of the only AHP
turbidite on this levee looks like sand or like mud.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Tuple

Row = Tuple[float, float, float, float, float, float]  # z, Al, Si, Fe, Ca, Ti


def _data_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "cores"


def load_xrf(path: Path | None = None) -> List[Row]:
    p = path or (_data_dir() / "geob8502_xrf_slim.csv")
    out: List[Row] = []
    with p.open(encoding="utf-8") as f:
        for rec in csv.DictReader(f):
            out.append((
                float(rec["depth_m"]),
                float(rec["Al_pct"]),
                float(rec["Si_pct"]),
                float(rec["Fe_pct"]),
                float(rec["Ca_pct"]),
                float(rec["Ti_pct"]),
            ))
    return out


def load_turbidites(path: Path | None = None, core: str = "GeoB8502-2") -> List[Dict[str, float | str]]:
    p = path or (_data_dir() / "timiris_turbidites.csv")
    out = []
    with p.open(encoding="utf-8") as f:
        for rec in csv.DictReader(f):
            if rec["core"] != core:
                continue
            out.append({
                "core": rec["core"],
                "event": rec["event"],
                "top_m": float(rec["top_m"]),
                "bot_m": float(rec["bot_m"]),
                "age_ka": float(rec["age_ka"]),
            })
    return out


def sial(row: Row) -> float:
    z, al, si, *_ = row
    if al <= 0:
        raise ValueError("Al must be positive")
    return si / al


def mean_sial(rows: List[Row], z0: float, z1: float) -> Dict[str, float]:
    xs = [sial(r) for r in rows if z0 <= r[0] <= z1]
    if not xs:
        raise ValueError(f"no XRF samples in {z0}-{z1} m")
    return {"n": float(len(xs)), "sial": sum(xs) / len(xs), "sial_max": max(xs)}


def sial_windows(rows: List[Row] | None = None) -> Dict[str, Dict[str, float]]:
    """T1 (AHP 10.1 ka) vs pelagite vs Pleistocene Si bombs on the same core."""
    data = rows if rows is not None else load_xrf()
    return {
        "t1_ahp_10ka": mean_sial(data, 0.25, 0.47),
        "pelagite_above": mean_sial(data, 0.02, 0.22),
        "pelagite_below": mean_sial(data, 0.50, 1.40),
        "pleistocene_bombs": mean_sial(data, 8.40, 12.60),
        "core": mean_sial(data, 0.02, 14.80),
    }


def ahp_events(core: str = "GeoB8509-2", lo_ka: float = 5.5, hi_ka: float = 14.5) -> int:
    n = 0
    p = _data_dir() / "timiris_turbidites.csv"
    with p.open(encoding="utf-8") as f:
        for rec in csv.DictReader(f):
            if rec["core"] != core:
                continue
            age = float(rec["age_ka"])
            if lo_ka <= age <= hi_ka:
                n += 1
    return n
