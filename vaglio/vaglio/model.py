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

EMENDAMENTO v1.1 (16 nov 2026, PRIMA di eseguire il test; test mai toccato).
  In validazione la soglia secca dava recall 0.67 / precisione 0.79: sotto
  l'asticella. Cambiata la sola estrazione degli oggetti, scelta sui riquadri
  1500-1764: probabilita' lisciata (SMOOTH_PX), poi soglia a isteresi — un
  oggetto e' una componente di prob >= LO che contiene almeno un pixel >= HI.
  Validazione: recall 0.75, precisione 0.80. Per velocita' la probabilita' si
  calcola un pixel si' e uno no (STRIDE) e si interpola. Criterio PASSA invariato.

ESITO SUL TEST (16 nov 2026, commit b592a1e, eseguito una volta): PASSA.
  942 oggetti annotati, 677 previsti: recall 0.764, precisione 0.830, IoU 0.566.
  L'IoU resta sotto le reti profonde della gara (~0.8): i contorni sono
  grossolani. Il rilevatore serve a dire DOVE guardare, non a disegnare piante.

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
SMOOTH_PX, HI, LO, STRIDE = 2.0, 0.98, 0.60, 2
TRAIN, VALID, TEST = range(0, 1500), range(1500, 1765), range(1765, 2094)
MODEL_PATH = Path(__file__).resolve().parent / "data" / "structures.joblib"
# Esito del test pre-registrato (vedi docstring). Sta qui perche' i materiali lo citino da una sola fonte.
TEST_RESULT = {"data": "2026-11-16", "commit": "b592a1e", "riquadri_di_test": 329, "strutture_annotate": 942,
               "oggetti_previsti": 677, "recall": 0.764, "precisione": 0.830, "iou": 0.566,
               "criterio": "recall >= 0.70 e precisione >= 0.70, scritto prima", "passato": True}


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


def predict(model: Any, b: np.ndarray, stride: int = STRIDE) -> np.ndarray:
    """Probabilita' di struttura per pixel, gia' lisciata. Calcolata su una griglia rada e interpolata."""
    from scipy import ndimage

    f = features(b)[::stride, ::stride]
    p = model.predict_proba(f.reshape(-1, f.shape[-1]))[:, 1].reshape(f.shape[:2]).astype(np.float32)
    if stride > 1:
        p = ndimage.zoom(p, stride, order=1)[: b.shape[0], : b.shape[1]]
        p = np.pad(p, ((0, b.shape[0] - p.shape[0]), (0, b.shape[1] - p.shape[1])), mode="edge")
    return ndimage.gaussian_filter(p, SMOOTH_PX)


def extract(prob: np.ndarray, allowed: np.ndarray | None = None) -> np.ndarray:
    """Maschera degli oggetti previsti: isteresi HI/LO, poi apertura. `allowed` esclude zone senza dato."""
    from scipy import ndimage

    low = prob >= LO if allowed is None else (prob >= LO) & allowed
    lab, n = ndimage.label(low)
    if n == 0:
        return low
    keep = np.zeros(n + 1, bool)
    keep[1:] = ndimage.maximum(prob, lab, np.arange(1, n + 1)) >= HI
    return ndimage.binary_opening(keep[lab])


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


def score_tile(prob: np.ndarray, truth: np.ndarray) -> Dict[str, int]:
    """Conteggi a livello di oggetto e di pixel per un riquadro."""
    from scipy import ndimage

    pl, pn = objects(extract(prob))
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
