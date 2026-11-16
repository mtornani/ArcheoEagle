"""Le revisioni insegnano l'ordine: cosa far guardare per primo la prossima volta.

Dopo ogni pacco rivisto, un modello minuscolo (regressione logistica su sei
misure) impara cosa distingue cio' che i revisori hanno tenuto da cio' che
hanno giudicato non costruito, SU QUESTO rilievo. Serve solo a riordinare la
coda. La sua bonta' si misura lasciando fuori un candidato alla volta, e si
dichiara.

EMENDAMENTO (16 nov 2026, a scansione finita). La prima versione imparava solo
da 'regge' contro 'scartato'. Ma i revisori misurati finora non possono
scartare (review.py), quindi non imparava mai. Ora l'etichetta e':
  1 = regge alla revisione;
  0 = scartato, oppure almeno due revisori e almeno due terzi dei voti dicono
      naturale / moderno / artefatto;
  niente = tutto il resto (voti "incerto", disaccordo): non si usa.
Gli zeri del secondo tipo sono ETICHETTE DEBOLI: vengono da revisori che
riconoscono solo il 30-40% delle strutture vere, quindi fra loro ci sono
strutture vere dall'aspetto consumato. Per questo il modello impara "cosa i
revisori confermeranno", non "cosa e' vero", e l'esito del candidato NON cambia:
resta 'incerto'. Cambia solo il posto in coda.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

FEATURES = ("log_area", "n_objects", "max_height_m", "mean_prob", "ortho", "max_rect")
MIN_PER_CLASS = 8
NO = ("naturale", "moderno", "artefatto")


def vector(c: Dict[str, Any]) -> List[float]:
    return [math.log10(max(1.0, c["area_m2"])), min(20, c["n_objects"]), min(6.0, c["max_height_m"]),
            c["mean_prob"], c.get("ortho", 0.0), c.get("max_rect", 0.0)]


def label(reviewed: Dict[str, Any]) -> Optional[int]:
    """1 tenuto, 0 giudicato non costruito, None se i revisori non si sono pronunciati."""
    if reviewed["outcome"] == "regge_alla_revisione":
        return 1
    if reviewed["outcome"] == "scartato":
        return 0
    votes = [v["verdict"] for v in reviewed.get("all_votes", [])]
    no = sum(v in NO for v in votes)
    return 0 if len(votes) >= 2 and no >= 2 and no / len(votes) >= 2 / 3 else None


def fit(cands: List[Dict[str, Any]], reviewed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """reviewed: id -> {outcome, all_votes} come in review/results/*.json."""
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import LeaveOneOut, cross_val_predict

    rows = [(vector(c), label(reviewed[c["id"]])) for c in cands if c["id"] in reviewed]
    rows = [r for r in rows if r[1] is not None]
    n1 = sum(y for _, y in rows)
    if min(n1, len(rows) - n1) < MIN_PER_CLASS:
        return {"fitted": False,
                "why": f"servono almeno {MIN_PER_CLASS} tenuti e {MIN_PER_CLASS} giudicati non costruiti (ora {n1} e {len(rows) - n1})"}
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
