"""Deposito sigillato per il test cieco (vaglio/test_cieco/PREREGISTRATION.md).

Scrive l'elenco completo dei complessi candidati, con le coordinate, in un CSV
dal formato fisso, e ne calcola l'impronta SHA-256. Il CSV resta privato e va
solo a chi custodisce la chiave; l'impronta si pubblica PRIMA, cosi' nessuno
puo' cambiare l'elenco dopo aver visto il catalogo.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

COLUMNS = ("deposit_id", "transect", "lon", "lat", "radius_m", "extent_m", "area_m2", "n_objects",
           "max_height_m", "outcome")
MATCH_PAD_M = 20.0      # dichiarato nella pre-registrazione: tolleranza oltre l'ingombro del complesso
MIN_HALF_M = 10.0


def radius_m(c: Dict[str, Any]) -> float:
    """Raggio di confronto: meta' dell'estensione del complesso (o raggio equivalente dell'area) + tolleranza."""
    half = (c.get("extent_m") or 0) / 2 or math.sqrt(c["area_m2"] / math.pi)
    return round(max(half, MIN_HALF_M) + MATCH_PAD_M, 1)


def rows(scans: List[Dict[str, Any]], reviewed: Dict[str, str]) -> List[Dict[str, Any]]:
    cands = sorted((c for s in scans for c in s["candidates"]), key=lambda c: (c["transect"], c["lat"], c["lon"]))
    out = []
    for k, c in enumerate(cands, 1):
        out.append({"deposit_id": f"D{k:05d}", "transect": c["transect"], "lon": f"{c['lon']:.6f}", "lat": f"{c['lat']:.6f}",
                    "radius_m": radius_m(c), "extent_m": c.get("extent_m") if c.get("extent_m") is not None else "",
                    "area_m2": c["area_m2"], "n_objects": c["n_objects"], "max_height_m": c["max_height_m"],
                    "outcome": reviewed.get(c["id"], "da_rivedere")})
    return out


def write(work: Path) -> Dict[str, Any]:
    from .__main__ import load_scans

    scans = load_scans(work)
    reviewed = {k: v["outcome"] for f in sorted((work / "review" / "results").glob("*.json"))
                for k, v in json.loads(f.read_text(encoding="utf-8"))["candidates"].items()} \
        if (work / "review" / "results").exists() else {}
    data = rows(scans, reviewed)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(data)
    blob = buf.getvalue().encode("utf-8")
    out = work / "deposito"
    out.mkdir(parents=True, exist_ok=True)
    (out / "deposito.csv").write_bytes(blob)
    manifest = {"file": "deposito.csv", "sha256": hashlib.sha256(blob).hexdigest(), "rows": len(data),
                "transects": len({r["transect"] for r in data}), "created": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                "match_pad_m": MATCH_PAD_M, "columns": list(COLUMNS),
                "note": "Il CSV ha coordinate: resta privato e va solo a chi custodisce la chiave. L'impronta si pubblica prima."}
    (out / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    return manifest
