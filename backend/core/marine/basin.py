"""Soglie, sfioratori e conche: la geometria di dove l'acqua entra ed esce.

NATO CORRETTO DA UN DUBBIO. L'ipotesi iniziale diceva: cercare un bacino con
una soglia che viene scavalcata e si riempie in fretta. Poi Vajont e il Nepal
2026 hanno mostrato che i due casi reali piu' chiari di "catastrofe d'acqua che
uccide gente e lascia un racconto" NON sono ne' bacini ne' soglie:

  Vajont 1963   la diga TENNE. Una frana cadde dentro il lago e sposto'
                l'acqua. Il killer e' una massa solida, l'onda e' l'effetto.
  Nepal 2026    NON un lago glaciale che esonda: il crollo di un ghiacciaio
                sul Langtang Lirung. 1.357 morti, 72 km di insediamenti,
                corpi a 240 km. Massa solida, colata, valle.

In entrambi la catastrofe e' **lineare e a valle**, non una conca che si
riempie. E un bacino che si riempie lentamente (anche il Mar Nero
"catastrofico" sale ~15 cm al giorno) e' una cosa da cui ci si allontana
camminando: sposta, non uccide. Niente corpi, niente livello di abbandono
improvviso — **ne' memoria ne' giacimento**.

Tre meccanismi, non uno:

  1. RIEMPIMENTO      soglia scavalcata, la conca si allaga. Lento anche quando
                      e' "rapido". Conserva male, ricorda poco.
                      -> pour_point(), hypsometry()
  2. SPOSTAMENTO      una massa cade in acqua e genera un'onda. Vajont,
                      Storegga ~8.150 anni fa (che colpi' proprio Doggerland).
                      Uccide in minuti. Lascia uno strato di sedimento, NON una
                      geometria: questo modulo non lo vede.
                      -> collapse_source_potential() da' solo la sorgente
  3. RILASCIO         massa o acqua liberata dall'alto, piena incanalata a
                      valle. Nepal 2026, GLOF, Missoula. Uccide in minuti lungo
                      una LINEA. Il bacino si SVUOTA: la distruzione e' a valle.
                      -> pour_point() + spillway_path()

La stessa primitiva geometrica serve 1 e 3: il **punto di sfioro**, cioe' il
punto piu' basso dell'orlo. Cambia solo da che parte sta l'acqua.

Attenzione alle prestazioni: priority-flood in Python puro. Va usato su griglie
ridotte (centinaia di celle di lato), che per lavoro di bacino e' comunque la
scala giusta.
"""
from __future__ import annotations

import heapq
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

NEIGH = ((1, 0), (-1, 0), (0, 1), (0, -1))


def priority_flood(dem: np.ndarray) -> np.ndarray:
    """Quota a cui l'acqua che entra dal bordo arriverebbe, cella per cella.

    filled - dem = profondita' della depressione. E' l'algoritmo standard
    (priority-flood): si parte da tutto il bordo e si procede dal piu' basso.
    """
    h, w = dem.shape
    filled = np.array(dem, dtype=np.float64, copy=True)
    closed = np.zeros((h, w), bool)
    pq: List[Tuple[float, int, int]] = []

    for r in range(h):
        for c in (0, w - 1):
            if not closed[r, c]:
                closed[r, c] = True
                heapq.heappush(pq, (float(dem[r, c]), r, c))
    for c in range(w):
        for r in (0, h - 1):
            if not closed[r, c]:
                closed[r, c] = True
                heapq.heappush(pq, (float(dem[r, c]), r, c))

    while pq:
        z, r, c = heapq.heappop(pq)
        for dr, dc in NEIGH:
            rr, cc = r + dr, c + dc
            if 0 <= rr < h and 0 <= cc < w and not closed[rr, cc]:
                closed[rr, cc] = True
                filled[rr, cc] = max(float(dem[rr, cc]), z)
                heapq.heappush(pq, (float(filled[rr, cc]), rr, cc))
    return filled


def depression_at(dem: np.ndarray, seed: Tuple[int, int]) -> Optional[Dict[str, Any]]:
    """La conca che contiene il seme, con il suo punto di sfioro.

    None se il seme non sta in una depressione: nessuna conca inventata.
    """
    r0, c0 = seed
    h, w = dem.shape
    if not (0 <= r0 < h and 0 <= c0 < w):
        return None
    filled = priority_flood(dem)
    spill = float(filled[r0, c0])
    if spill <= float(dem[r0, c0]) + 1e-9:
        return None  # il seme non e' in una depressione

    # regione connessa allagata allo stesso livello di sfioro
    mask = np.zeros((h, w), bool)
    stack = [(r0, c0)]
    mask[r0, c0] = True
    while stack:
        r, c = stack.pop()
        for dr, dc in NEIGH:
            rr, cc = r + dr, c + dc
            if (0 <= rr < h and 0 <= cc < w and not mask[rr, cc]
                    and abs(float(filled[rr, cc]) - spill) < 1e-9
                    and float(dem[rr, cc]) < spill - 1e-9):
                mask[rr, cc] = True
                stack.append((rr, cc))

    touches_edge = bool(mask[0, :].any() or mask[-1, :].any()
                        or mask[:, 0].any() or mask[:, -1].any())
    return {
        "spill_level": spill,
        "mask": mask,
        "n_cells": int(mask.sum()),
        "max_depth": float(np.max(np.where(mask, spill - dem, 0.0))),
        "truncated": touches_edge,
        "warning": (
            "la conca tocca il bordo della finestra: la soglia trovata puo' "
            "essere un artefatto del ritaglio, non un orlo vero"
            if touches_edge else None
        ),
    }


def pour_point(dem: np.ndarray, basin: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Il punto piu' basso dell'orlo: da li' l'acqua entra (riempimento) o esce
    (rilascio). E' lo stesso punto — cambia da che parte sta l'acqua."""
    mask = basin["mask"]
    h, w = dem.shape
    best = None
    rs, cs = np.nonzero(mask)
    for r, c in zip(rs, cs):
        for dr, dc in NEIGH:
            rr, cc = r + dr, c + dc
            if 0 <= rr < h and 0 <= cc < w and not mask[rr, cc]:
                z = float(dem[rr, cc])
                if best is None or z < best[0]:
                    best = (z, rr, cc)
    if best is None:
        return None
    return {"level": best[0], "row": int(best[1]), "col": int(best[2])}


def spillway_path(dem: np.ndarray, start: Tuple[int, int], max_steps: int = 10000) -> List[Tuple[int, int]]:
    """Dove va l'acqua se la soglia cede: discesa ripida dal punto di sfioro.

    E' la zona di distruzione del meccanismo 3 (Nepal 2026, GLOF, Missoula):
    la catastrofe e' A VALLE del bacino, mentre il bacino si svuota. Il modello
    originale, che guardava solo il riempimento, non la vedeva affatto.
    """
    h, w = dem.shape
    r, c = start
    path = [(int(r), int(c))]
    seen = {(int(r), int(c))}
    for _ in range(max_steps):
        z = float(dem[r, c])
        nxt = None
        for dr, dc in NEIGH:
            rr, cc = r + dr, c + dc
            if 0 <= rr < h and 0 <= cc < w and (rr, cc) not in seen:
                zz = float(dem[rr, cc])
                if zz < z and (nxt is None or zz < nxt[0]):
                    nxt = (zz, rr, cc)
        if nxt is None:
            break
        r, c = nxt[1], nxt[2]
        path.append((int(r), int(c)))
        seen.add((int(r), int(c)))
    return path


def hypsometry(dem: np.ndarray, mask: np.ndarray, levels: Sequence[float]) -> List[Dict[str, float]]:
    """Curva area-volume del bacino. E' l'integrale che rende la conca
    riconoscibile senza sapere dove sia la sponda: l'integrazione sopprime il
    rumore che affossa le statistiche locali."""
    z = dem[mask]
    out = []
    for lvl in levels:
        sotto = z[z <= lvl]
        out.append({
            "level": float(lvl),
            "area_cells": int(sotto.size),
            "volume": float(np.sum(lvl - sotto)) if sotto.size else 0.0,
        })
    return out


def collapse_source_potential(dem: np.ndarray, water_mask: np.ndarray,
                              steep: float = 0.30) -> float:
    """Frazione di orlo del corpo d'acqua che e' ripida: potenziale sorgente di
    frana che sposta l'acqua (meccanismo 2, Vajont/Storegga).

    Da' solo la SORGENTE. L'onda e il suo deposito non stanno nella geometria:
    stanno nella stratigrafia, e questo modulo non li vede. E' un limite
    dichiarato, non una lacuna da colmare qui.
    """
    h, w = dem.shape
    gy, gx = np.gradient(dem)
    slope = np.sqrt(gy * gy + gx * gx)
    rim = np.zeros((h, w), bool)
    rs, cs = np.nonzero(water_mask)
    for r, c in zip(rs, cs):
        for dr, dc in NEIGH:
            rr, cc = r + dr, c + dc
            if 0 <= rr < h and 0 <= cc < w and not water_mask[rr, cc]:
                rim[rr, cc] = True
    if not rim.any():
        return 0.0
    return float((slope[rim] > steep).mean())
