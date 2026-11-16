"""Addestra e misura il rilevatore su Chactun. Uso:

    python -m vaglio.train <cartella_chactun> fit      # addestra + sceglie soglia (0-1764)
    python -m vaglio.train <cartella_chactun> test     # misura sul TEST (1765-2093), una volta
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from . import model as M


def load(root: Path, i: int):
    import tifffile

    b = tifffile.imread(root / "lidar" / f"tile_{i}_lidar.tif")
    t = np.zeros(b.shape[:2], bool)
    for c in ("building", "platform"):
        t |= tifffile.imread(root / "masks" / f"tile_{i}_mask_{c}.tif") == 0   # 0 = struttura
    return b, t


def fit(root: Path) -> None:
    import joblib
    from sklearn.ensemble import HistGradientBoostingClassifier

    rng = np.random.default_rng(0)
    X, y = [], []
    for i in M.TRAIN:
        b, t = load(root, i)
        f = M.features(b).reshape(-1, 27)
        t = t.ravel()
        pos, neg = np.flatnonzero(t), np.flatnonzero(~t)
        idx = np.concatenate([rng.choice(pos, min(len(pos), 600), replace=False),
                              rng.choice(neg, min(len(neg), 900), replace=False)])
        X.append(f[idx]); y.append(t[idx])
    X, y = np.concatenate(X), np.concatenate(y)
    print("campioni", X.shape, "positivi", round(float(y.mean()), 3), flush=True)
    clf = HistGradientBoostingClassifier(max_iter=400, learning_rate=0.1, max_leaf_nodes=63,
                                         l2_regularization=1.0, random_state=0)
    clf.fit(X, y)
    probs = [(M.predict(clf, b), t) for b, t in (load(root, i) for i in M.VALID)]
    best = None
    for thr in (0.5, 0.6, 0.7, 0.8, 0.9, 0.95):
        s = M.summarize([M.score_tile(p, t, thr) for p, t in probs])
        f1 = 2 * s["recall"] * s["precision"] / max(1e-9, s["recall"] + s["precision"])
        print("soglia", thr, s, "F1", round(f1, 3), flush=True)
        if best is None or f1 > best[0]:
            best = (f1, thr, s)
    M.MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump({"clf": clf, "thr": best[1], "valid": best[2],
                 "source": "Kokalj et al. 2023, doi:10.6084/m9.figshare.22202395, CC BY 4.0"},
                M.MODEL_PATH, compress=3)
    print("soglia scelta", best[1], "->", M.MODEL_PATH, flush=True)


def test(root: Path) -> None:
    import joblib

    m = joblib.load(M.MODEL_PATH)
    s = M.summarize([M.score_tile(M.predict(m["clf"], b), t, m["thr"])
                     for b, t in (load(root, i) for i in M.TEST)])
    s["passed"] = bool(s["recall"] >= 0.70 and s["precision"] >= 0.70)
    s["thr"] = m["thr"]
    print(json.dumps(s))


if __name__ == "__main__":
    {"fit": fit, "test": test}[sys.argv[2]](Path(sys.argv[1]))
