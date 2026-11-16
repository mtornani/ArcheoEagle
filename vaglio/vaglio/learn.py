"""Le revisioni insegnano l'ordine: cosa far guardare per primo la prossima volta.

Dopo ogni pacco rivisto, un modello minuscolo (regressione logistica su sei
misure) impara cosa distingue cio' che i revisori calibrati hanno tenuto da
cio' che hanno scartato, SU QUESTO rilievo. Serve solo a riordinare la coda.
La sua bonta' si misura lasciando fuori un candidato alla volta, e si dichiara.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List

FEATURES = ("log_area", "n_objects", "max_height_m", "mean_prob", "ortho", "max_rect")
MIN_PER_CLASS = 8


def vector(c: Dict[str, Any]) -> List[float]:
    return [math.log10(max(1.0, c["area_m2"])), min(20, c["n_objects"]), min(6.0, c["max_height_m"]),
            c["mean_prob"], c.get("ortho", 0.0), c.get("max_rect", 0.0)]


def fit(cands: List[Dict[str, Any]], outcomes: Dict[str, str]) -> Dict[str, Any]:
    """outcomes: id -> esito. Usa solo 'regge_alla_revisione' (1) e 'scartato' (0)."""
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import LeaveOneOut, cross_val_predict

    rows = [(vector(c), 1 if outcomes[c["id"]] == "regge_alla_revisione" else 0)
            for c in cands if outcomes.get(c["id"]) in ("regge_alla_revisione", "scartato")]
    n1 = sum(y for _, y in rows)
    if min(n1, len(rows) - n1) < MIN_PER_CLASS:
        return {"fitted": False, "why": f"servono almeno {MIN_PER_CLASS} tenuti e {MIN_PER_CLASS} scartati (ora {n1} e {len(rows) - n1})"}
    X = np.array([r[0] for r in rows]); y = np.array([r[1] for r in rows])
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Z = (X - mu) / sd
    clf = LogisticRegression(C=1.0, max_iter=500)
    p = cross_val_predict(clf, Z, y, cv=LeaveOneOut(), method="predict_proba")[:, 1]
    pos, neg = p[y == 1], p[y == 0]
    auc = float((pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean())
    clf.fit(Z, y)
    return {"fitted": True, "n": len(rows), "n_kept": int(n1), "auc_loo": round(auc, 3), "features": list(FEATURES),
            "mu": mu.tolist(), "sd": sd.tolist(), "coef": clf.coef_[0].tolist(), "intercept": float(clf.intercept_[0])}


def priority(c: Dict[str, Any], m: Dict[str, Any]) -> float:
    z = sum(w * (v - mu) / sd for w, v, mu, sd in zip(m["coef"], vector(c), m["mu"], m["sd"])) + m["intercept"]
    return round(1 / (1 + math.exp(-z)), 3)


def load(work: Path) -> Dict[str, Any] | None:
    p = work / "review" / "ordine.json"
    m = json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
    return m if m and m.get("fitted") else None
