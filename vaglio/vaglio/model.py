"""Rilevatore di strutture: probabilita' per pixel, poi oggetti.

Addestrato sulle annotazioni manuali di Chactun (Kokalj et al. 2023, CC BY 4.0,
doi:10.6084/m9.figshare.22202395): 2.094 riquadri da 240 m, edifici e
piattaforme delineati da archeologi, in parte verificati sul campo.

PRE-REGISTRAZIONE (16 nov 2026, committata PRIMA di toccare i riquadri di test).
  Divisione: quella degli autori del dataset. 0-1499 addestramento,
  1500-1764 scelta della soglia, 1765-2093 TEST (mai guardati prima).
  Bersaglio: edificio OPPURE piattaforma ("struttura").
  Oggetto annotato  = componente connessa della maschera, area >= MIN_AREA_M2.
  Oggetto previsto  = componente connessa di prob >= soglia, area >= MIN_AREA_M2.
  Annotato TROVATO  = almeno HIT_FRAC dei suoi pixel previsti.
  Previsto CORRETTO = almeno HIT_FRAC dei suoi pixel dentro la maschera
                      allargata di SLOP_M (i bordi a mano non sono al pixel).
  PASSA se sul TEST: recall >= 0.70 E precisione >= 0.70.
  Si riporta anche l'IoU per pixel (i vincitori della gara ECML-PKDD 2021
  stavano attorno a 0.8 con reti profonde: quello e' il termine di paragone).

LIMITE NOTO PRIMA DI MISURARE: ogni riquadro di Chactun contiene almeno una
struttura. La precisione qui e' misurata in terreno DENSO di rovine. In terreno
vuoto (colline carsiche, campi arati) non la misura questo banco: la misura la
revisione con controlli piantati (vaglio/review.py).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

PX_M = 0.5
MIN_AREA_M2 = 25.0
HIT_FRAC = 0.30
SLOP_M = 2.0
SIGMAS_PX = (2, 4, 8, 16)
TRAIN, VALID, TEST = range(0, 1500), range(1500, 1765), range(1765, 2094)
MODEL_PATH = Path(__file__).resolve().parent / "data" / "structures.joblib"


def features(b: np.ndarray) -> np.ndarray:
    """(H,W,3 uint8) -> (H,W,F float32). Solo contesto locale a piu' scale: niente forma imparata a memoria."""
    from scipy import ndimage

    out: List[np.ndarray] = []
    for i in range(3):
        x = b[..., i].astype(np.float32) / 255.0
        g = [ndimage.gaussian_filter(x, s) for s in SIGMAS_PX]
        out += [x, *g, g[0] - g[2], g[1] - g[3]]
        m2 = ndimage.gaussian_filter(x * x, 4)
        out.append(np.sqrt(np.maximum(m2 - g[1] ** 2, 0)))   # rugosita' locale
    return np.stack(out, axis=-1)


def predict(model: Any, b: np.ndarray) -> np.ndarray:
    f = features(b)
    return model.predict_proba(f.reshape(-1, f.shape[-1]))[:, 1].reshape(b.shape[:2]).astype(np.float32)


def objects(mask: np.ndarray, px_m: float = PX_M) -> Tuple[np.ndarray, int]:
    """Componenti connesse con area >= MIN_AREA_M2. Ritorna (etichette, n)."""
    from scipy import ndimage

    lab, n = ndimage.label(mask)
    if n == 0:
        return lab, 0
    area = ndimage.sum_labels(np.ones_like(lab), lab, np.arange(1, n + 1)) * px_m * px_m
    keep = np.zeros(n + 1, bool)
    keep[1:] = area >= MIN_AREA_M2
    lab = np.where(keep[lab], lab, 0)
    return ndimage.label(lab > 0)


def score_tile(prob: np.ndarray, truth: np.ndarray, thr: float) -> Dict[str, int]:
    """Conteggi a livello di oggetto e di pixel per un riquadro."""
    from scipy import ndimage

    pred = ndimage.binary_opening(prob >= thr, iterations=1)
    pl, pn = objects(pred)
    tl, tn = objects(truth)
    pred_m, truth_m = pl > 0, tl > 0
    slop = ndimage.binary_dilation(truth, iterations=int(round(SLOP_M / PX_M)))
    found = sum(pred_m[tl == i].mean() >= HIT_FRAC for i in range(1, tn + 1))
    right = sum(slop[pl == i].mean() >= HIT_FRAC for i in range(1, pn + 1))
    return {"truth": tn, "found": int(found), "pred": pn, "right": int(right),
            "inter": int((pred_m & truth).sum()), "union": int((pred_m | truth).sum())}


def summarize(rows: List[Dict[str, int]]) -> Dict[str, float]:
    s = {k: sum(r[k] for r in rows) for k in rows[0]}
    return {"n_truth": s["truth"], "n_pred": s["pred"],
            "recall": round(s["found"] / max(1, s["truth"]), 3),
            "precision": round(s["right"] / max(1, s["pred"]), 3),
            "iou": round(s["inter"] / max(1, s["union"]), 3)}
