"""Option B: public pack has no coordinates. Hash + timestamp = priority."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List


BLIND_DROP = {"lon", "lat", "river_name", "river_id"}


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def strip_row(row: Dict[str, Any]) -> Dict[str, Any]:
    out = {
        "label": row["label"],
        "rank": row["rank"],
        "residual": row["residual"],
        "hydro_score": row["hydro_score"],
        "spectral_score": row.get("spectral_score"),
        "geometry_score": row.get("geometry_score"),
        "node_type": row.get("node_type"),
        "basin": row.get("basin"),
        "source": row.get("source"),
        "grade": row.get("grade"),
        "vs_schematic_km": row.get("vs_schematic_km"),
        "pro": row.get("pro") or [],
        "contro": row.get("contro") or [],
        "kill_shot": row.get("kill_shot"),
        "plato": [
            {"id": p["id"], "verdict": p["verdict"]}
            for p in (row.get("plato") or [])
        ],
    }
    for k in BLIND_DROP:
        out.pop(k, None)
    return out


def make_blind_pack(rows: List[Dict[str, Any]], timestamp: str | None = None) -> Dict[str, Any]:
    ts = timestamp or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    ranking = [strip_row(r) for r in rows]
    payload = {"algorithm": "sha256", "ranking": ranking, "timestamp": ts}
    digest = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    return {
        "algorithm": "sha256",
        "hash": digest,
        "timestamp": ts,
        "ranking": ranking,
        "note": "Niente coordinate. Stessa rubrica, stessa classifica. Hash = priorità, non prova.",
    }


def verify_hash(pack: Dict[str, Any]) -> bool:
    payload = {
        "algorithm": pack.get("algorithm", "sha256"),
        "ranking": pack.get("ranking"),
        "timestamp": pack.get("timestamp"),
    }
    digest = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    return digest == pack.get("hash")
