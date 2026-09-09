"""Two-sided ledger. Plato is a test column, not a blueprint."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

VERDICT_SUPPORT = "support"
VERDICT_CONTRADICT = "contradict"
VERDICT_NA = "na"


def plato_tests(
    lon: float,
    lat: float,
    *,
    circularity: Optional[float] = None,
    near_paleolake_km: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """Each clause: support / contradict / na. Missing rings is NEVER contradict."""
    tests: List[Dict[str, Any]] = []

    # 1. Beyond Pillars — literal west of Gibraltar vs Egyptian "west of us"
    if lon <= -5.5:
        tests.append(_t(
            "beyond_pillars",
            "Oltre le Colonne d'Ercole",
            VERDICT_SUPPORT,
            "Longitudine a ovest di Gibilterra. Lettura letterale possibile.",
        ))
    else:
        tests.append(_t(
            "beyond_pillars",
            "Oltre le Colonne d'Ercole",
            VERDICT_NA,
            "Sahara è a est di Gibilterra. Da narratore egizio 'oltre' può voler dire ovest. "
            "Deriva linguistica: non contraddice e non prova.",
        ))

    # 2. Rings — measured after, never a hunt prior. Absence = N/A
    if circularity is not None and circularity >= 0.72:
        tests.append(_t(
            "concentric_rings",
            "Anelli di terra e acqua",
            VERDICT_SUPPORT,
            f"Circolarità misurata {circularity:.2f}. Compatibile. Non è prova: la forma resta aperta.",
        ))
    else:
        tests.append(_t(
            "concentric_rings",
            "Anelli di terra e acqua",
            VERDICT_NA,
            "Nessun anello misurato, oppure circolarità bassa. Assenza ≠ falsificazione. "
            "Forma pre-immaginata = pareidolia. Non contraddice.",
        ))

    # 3. Island — hydrologic reading
    if near_paleolake_km is not None and near_paleolake_km < 40:
        tests.append(_t(
            "island",
            "Isola",
            VERDICT_SUPPORT,
            f"Entro {near_paleolake_km:.0f} km da sponda di paleolago. "
            "'Isola' può essere alto su acqua stagionale, non oceano.",
        ))
    else:
        tests.append(_t(
            "island",
            "Isola",
            VERDICT_NA,
            "Nessun paleolago schematico vicino. 'Isola' può anche essere terra tra fiumi. Non applicabile.",
        ))

    # 4. Mountains to the north — Atlas fits west Sahara
    if lon < 5 and lat < 32:
        tests.append(_t(
            "mountains_north",
            "Montagne a nord",
            VERDICT_SUPPORT,
            "Sahara occidentale: Atlante sta a nord. Compatibile con una lettura geografica.",
        ))
    else:
        tests.append(_t(
            "mountains_north",
            "Montagne a nord",
            VERDICT_NA,
            "Fuori dal settore dove l'Atlante è il muro nord ovvio. Non contraddice.",
        ))

    # 5. Sudden destruction — cannot test from home
    tests.append(_t(
        "sudden_destruction",
        "Distrutta in un giorno e una notte",
        VERDICT_NA,
        "Satellitare non data un crollo. Megaflood, seppellimento da duna, morte del fiume: tutti N/A da casa.",
    ))

    # 6. Size — two readings, so N/A unless we pick one (we don't)
    tests.append(_t(
        "size_libya_asia",
        "Più grande della Libia e dell'Asia",
        VERDICT_NA,
        "Se è la terra irrigata (Sahara verde) sostiene. Se è una città, contraddice. "
        "Due letture: beneficio del dubbio entrambi i versi. Non si vota.",
    ))

    # 7. Elephants / fauna
    tests.append(_t(
        "elephants",
        "Elefanti e fauna",
        VERDICT_NA,
        "Sahara verde aveva megafauna. Indizio climatico, non pin. Non misurabile sul candidato.",
    ))

    # 8. Orichalcum
    tests.append(_t(
        "orichalcum",
        "Oricalco",
        VERDICT_NA,
        "Nessun proxy remoto onesto per un metallo da testo. Non cercare 'oro' sullo spettro.",
    ))

    return tests


def _t(clause_id: str, label: str, verdict: str, detail: str) -> Dict[str, Any]:
    return {"id": clause_id, "label": label, "verdict": verdict, "detail": detail}


def _circularity_from_eccentricity(ecc: Optional[float]) -> Optional[float]:
    if ecc is None:
        return None
    return max(0.0, min(1.0, 1.0 - float(ecc)))


def _residual(hydro: float, spectral: Optional[float], geometry: Optional[float], plato: List[Dict[str, Any]]) -> float:
    """Lower = more independent columns speak. N/A does not help or hurt."""
    cols = [hydro]
    if spectral is not None:
        cols.append(spectral)
    if geometry is not None:
        cols.append(geometry)
    applicable = [p for p in plato if p["verdict"] != VERDICT_NA]
    if applicable:
        support = sum(1 for p in applicable if p["verdict"] == VERDICT_SUPPORT)
        contradict = sum(1 for p in applicable if p["verdict"] == VERDICT_CONTRADICT)
        # contradictions raise residual; supports lower it; column exists only if applicable
        plato_score = (support - contradict) / len(applicable)
        cols.append(max(0.0, min(1.0, 0.5 + 0.5 * plato_score)))
    mean = sum(cols) / len(cols)
    spread = sum(abs(c - mean) for c in cols) / len(cols)
    # high agreement + high mean → low residual
    residual = (1.0 - mean) * 0.65 + spread * 0.35
    return round(max(0.05, min(0.95, residual)), 3)


def _kill_shot(hydro: float, node_type: Optional[str], plato: List[Dict[str, Any]]) -> str:
    contrad = [p for p in plato if p["verdict"] == VERDICT_CONTRADICT]
    if contrad:
        return f"Kill-shot remoto possibile: {contrad[0]['label']} contraddice e non è N/A."
    if hydro < 0.2 and node_type is None:
        return "Fuori rete paleoidrica nota. Da casa resta rumore finché un fiume o un radar non lo collega."
    return "Nessun kill-shot remoto. Resta aperto. Due umani, stessa rubrica, stessa classifica."


def build_ledger(
    hydro_nodes: List[Dict[str, Any]],
    spectral_features: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Merge hydrologic nodes (the road) with optional spectral blobs.
    Spectral near a river rides the node. Spectral far away is a separate
    high-residual candidate — not discarded (benefit of the doubt).
    """
    used_spectral = set()
    rows: List[Dict[str, Any]] = []

    for node in hydro_nodes:
        matched = None
        matched_i = None
        matched_d = 40.0
        for i, feat in enumerate(spectral_features):
            coords = (feat.get("geometry") or {}).get("coordinates") or [None, None]
            if coords[0] is None:
                continue
            dlon = abs(coords[0] - node["lon"])
            dlat = abs(coords[1] - node["lat"])
            # deg ~ km*0.01 at Sahara lats; 0.4 deg ~ 40km
            approx_km = (dlon ** 2 + dlat ** 2) ** 0.5 * 111.0
            if approx_km < matched_d:
                matched_d = approx_km
                matched = feat
                matched_i = i
        if matched_i is not None:
            used_spectral.add(matched_i)

        props = (matched or {}).get("properties") or {}
        ecc = props.get("eccentricity")
        circ = _circularity_from_eccentricity(ecc)
        spectral = props.get("score")
        if spectral is not None:
            spectral = float(spectral)
        near_lake = 0.0 if node.get("node_type") == "paleolake_shore" else None
        plato = plato_tests(
            node["lon"], node["lat"],
            circularity=circ,
            near_paleolake_km=near_lake if near_lake is not None else None,
        )
        geom_score = circ if circ is not None and circ >= 0.55 else None
        residual = _residual(node["hydro_score"], spectral, geom_score, plato)
        pro, contro = _split_reasons(node, props, plato)
        rows.append({
            "lon": node["lon"],
            "lat": node["lat"],
            "node_type": node.get("node_type"),
            "basin": node.get("basin"),
            "river_id": node.get("river_id"),
            "river_name": node.get("river_name"),
            "hydro_score": node["hydro_score"],
            "spectral_score": spectral,
            "geometry_score": geom_score,
            "circularity": circ,
            "residual": residual,
            "plato": plato,
            "pro": pro,
            "contro": contro,
            "kill_shot": _kill_shot(node["hydro_score"], node.get("node_type"), plato),
            "source": node.get("source") or ("hydro+spectral" if matched else "hydro"),
            "grade": node.get("grade") or "schematic",
            "vs_schematic_km": node.get("vs_schematic_km"),
            "level_m": node.get("level_m"),
            "spectral_label": props.get("label"),
        })

    for i, feat in enumerate(spectral_features):
        if i in used_spectral:
            continue
        coords = (feat.get("geometry") or {}).get("coordinates") or [None, None]
        if coords[0] is None:
            continue
        props = feat.get("properties") or {}
        ecc = props.get("eccentricity")
        circ = _circularity_from_eccentricity(ecc)
        spectral = float(props.get("score") or 0.4)
        plato = plato_tests(float(coords[0]), float(coords[1]), circularity=circ, near_paleolake_km=None)
        geom_score = circ if circ is not None and circ >= 0.55 else None
        residual = _residual(0.12, spectral, geom_score, plato)
        pro, contro = _split_reasons({"hydro_score": 0.12, "node_type": None}, props, plato)
        rows.append({
            "lon": round(float(coords[0]), 5),
            "lat": round(float(coords[1]), 5),
            "node_type": None,
            "basin": None,
            "river_id": None,
            "river_name": None,
            "hydro_score": 0.12,
            "spectral_score": spectral,
            "geometry_score": geom_score,
            "circularity": circ,
            "residual": residual,
            "plato": plato,
            "pro": pro,
            "contro": contro,
            "kill_shot": _kill_shot(0.12, None, plato),
            "source": "spectral",
            "spectral_label": props.get("label"),
        })

    rows.sort(key=lambda r: (r["residual"], -r["hydro_score"]))
    letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    for i, row in enumerate(rows):
        row["rank"] = i + 1
        row["label"] = letters[i] if i < len(letters) else str(i + 1)
    return rows


def _split_reasons(node: Dict[str, Any], props: Dict[str, Any], plato: List[Dict[str, Any]]) -> tuple:
    pro: List[str] = []
    contro: List[str] = []
    nt = node.get("node_type")
    if nt == "confluence":
        pro.append("Nodo di confluenza sulla rete fossile.")
    elif nt == "paleolake_shore":
        if node.get("grade") == "dem-contour":
            pro.append(
                f"Sponda misurata sul DEM alla quota {node.get('level_m', 320):.0f} m. "
                "Non è il LineString disegnato."
            )
        else:
            pro.append("Sponda di paleolago schematico. Disegno da letteratura, non misura.")
    elif nt in ("channel", "head_or_mouth"):
        pro.append("Sul tracciato di un paleofiume schematico.")
    else:
        contro.append("Nessun paleofiume noto sotto il punto.")
    if props.get("score"):
        pro.append("Anomalia spettrale (NDVI/BSI) nello stesso intorno.")
    for p in plato:
        if p["verdict"] == VERDICT_SUPPORT:
            pro.append(f"Platone +: {p['label']}")
        elif p["verdict"] == VERDICT_CONTRADICT:
            contro.append(f"Platone −: {p['label']}")
    if not contro:
        contro.append("Nessun contro remoto solido. Residuo resta: non è una prova.")
    return pro, contro
