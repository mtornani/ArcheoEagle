"""Addestra e misura il rilevatore su Chactun. Uso:

    python -m vaglio.train <cartella_chactun> fit      # addestra + sceglie soglia (0-1764)
    python -m vaglio.train <cartella_chactun> valid    # rimisura la validazione col modello salvato
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
        f = M.features(b)
        f = f.reshape(-1, f.shape[-1])
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
    v = M.summarize([M.score_tile(M.predict(clf, b), t) for b, t in (load(root, i) for i in M.VALID)])
    print("validazione", v, flush=True)
    M.MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump({"clf": clf, "valid": v, "hi": M.HI, "lo": M.LO,
                 "source": "Kokalj et al. 2023, doi:10.6084/m9.figshare.22202395, CC BY 4.0"},
                M.MODEL_PATH, compress=3)


def test(root: Path) -> None:
    import joblib

    m = joblib.load(M.MODEL_PATH)
    s = M.summarize([M.score_tile(M.predict(m["clf"], b), t) for b, t in (load(root, i) for i in M.TEST)])
    s["passed"] = bool(s["recall"] >= 0.70 and s["precision"] >= 0.70)
    print(json.dumps(s))


def valid(root: Path) -> None:
    import joblib

    m = joblib.load(M.MODEL_PATH)
    print(json.dumps(M.summarize([M.score_tile(M.predict(m["clf"], b), t) for b, t in (load(root, i) for i in M.VALID)])))


if __name__ == "__main__":
    {"fit": fit, "test": test, "valid": valid}[sys.argv[2]](Path(sys.argv[1]))
