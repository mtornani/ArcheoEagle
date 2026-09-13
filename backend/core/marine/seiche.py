"""Confinamento: perche' 25 milioni di m3 battono 600 km3.

NATO DA DICKSON FJORD. Il 16 settembre 2023, in Groenlandia orientale, ~25
milioni di m3 di roccia e ghiaccio cadono nel Dickson Fjord. Run-up ~200 m.
Poi l'acqua, chiusa fra due pareti, comincia a oscillare da un lato all'altro
con periodo ~92 secondi, e continua per **nove giorni**: un segnale sismico a
10,88 mHz visto da tutta la rete globale (Svennevig et al., Science, 2024).

Confronto che vale piu' di ogni argomento:

    Sahara Slide     ~600 km3 = 600.000 milioni di m3   giudicato NON tsunamigenico
    Dickson Fjord      ~25 milioni di m3  (24.000x meno)   run-up 200 m

Il volume non e' il criterio — questo `basin.py` lo diceva gia', e Dickson lo
conferma. Ma Dickson aggiunge la variabile che mancava: **dove finisce
l'energia**. Su un pendio aperto l'onda irradia e si diluisce con la distanza.
In un bacino chiuso non ha uscita: si riflette, si somma, e torna. Non un'onda:
un'onda ogni 90 secondi per giorni.

## Cosa di tutto questo e' misurabile da noi, e cosa no

  MISURABILE     la geometria. Confinamento, lunghezza, profondita' -> periodo
                 atteso della seiche (Merian). Restringimento e basso fondale ->
                 amplificazione (Green). Tutto da DEM/batimetria, che abbiamo.

  NON MISURABILE il segnale. Nessun proxy geologico registra un'oscillazione di
                 90 secondi avvenuta 12.000 anni fa. Quei 9 giorni si vedono
                 solo perche' esiste una rete sismica broadband globale dal
                 ~1990. Per il passato remoto il segnale non e' debole: e'
                 **assente**. Non cercarlo.

  PRESERVATO     il deposito di run-up: sedimento portato SOPRA il piano
                 d'acqua. Quello resta, e nessun processo di riva normale lo
                 mette a 100 m di quota. E' l'unico test falsificabile del
                 meccanismo. Non sta in questo modulo (e' stratigrafia), ma e'
                 qui che questo modulo dice di andare a guardare.

Quindi: questo file NON rileva catastrofi. Ordina bacini per **quanto sarebbero
stati pericolosi se una frana fosse caduta dentro**, e dice dove il deposito
dovrebbe trovarsi. Un punteggio alto e' un posto dove andare a cercare uno
strato, non un evento avvenuto.
"""
from __future__ import annotations

import math
from typing import Any, Dict, Optional, Tuple

import numpy as np

G = 9.81

# Controllo positivo. Geometria approssimata del sito Dickson: il video e le
# cronache dicono "da una parete all'altra", quindi il modo eccitato e'
# TRASVERSALE e la lunghezza in gioco e' la larghezza del fiordo, non la sua
# estensione. La profondita' efficace e' incerta (il fondale non e' piatto):
# per questo il controllo verifica l'ordine di grandezza, non il decimale.
DICKSON = {
    "name": "Dickson Fjord",
    "date": "2023-09-16",
    "volume_Mm3": 25.0,
    "runup_m": 200.0,
    "observed_period_s": 92.0,
    "signal_days": 9.0,
    "signal_mHz": 10.88,
    "width_m": 2700.0,       # larghezza approssimata, modo trasversale
    "depth_m": 400.0,        # profondita' efficace, incerta
    "mode": "closed",
    "source": "Svennevig et al., Science (2024)",
    "grade": "literature",
}

# Il Sahara Slide, per tenere il confronto dentro il codice e non solo nei
# commenti: e' il promemoria che un numero enorme puo' valere zero.
SAHARA_SLIDE = {
    "name": "Sahara Slide",
    "volume_Mm3": 600000.0,
    "tsunamigenic": False,
    "why_not": "pendio dolce, accelerazione bassa, rottura retrogressiva",
    "grade": "literature",
}


def merian_period(length_m: float, depth_m: float, mode: str = "closed") -> Optional[float]:
    """Periodo fondamentale della seiche, in secondi (formula di Merian).

        chiuso ai due capi   T = 2L / sqrt(g*h)      (mezza onda nel bacino)
        aperto a un capo     T = 4L / sqrt(g*h)      (quarto d'onda)

    Approssimazione del prim'ordine: bacino rettangolare a fondale uniforme. Un
    fiordo vero non e' ne' l'uno ne' l'altro, quindi il numero serve a dire
    "decine di secondi" contro "ore", non a datare una riflessione.
    """
    if length_m <= 0 or depth_m <= 0:
        return None
    c = math.sqrt(G * depth_m)          # velocita' dell'onda lunga
    k = 2.0 if mode == "closed" else 4.0
    return k * length_m / c


def greens_amplification(depth_from: float, depth_to: float,
                         width_from: float, width_to: float) -> Optional[float]:
    """Di quanto cresce l'ampiezza entrando in acqua bassa e in un imbuto.

    Legge di Green: A2/A1 = (h1/h2)^(1/4) * (b1/b2)^(1/2).

    E' la ragione fisica per cui un fiordo stretto amplifica e una costa aperta
    no. Vale per onde lunghe che non frangono: sopra un certo punto la formula
    esagera, quindi trattala come limite superiore.
    """
    if min(depth_from, depth_to, width_from, width_to) <= 0:
        return None
    return (depth_from / depth_to) ** 0.25 * (width_from / width_to) ** 0.5


def confinement(water_mask: np.ndarray) -> Dict[str, float]:
    """Quanto e' chiuso il corpo d'acqua: 1 = catino, 0 = mare aperto.

    Si contano le celle di bordo del corpo d'acqua e si guarda quante confinano
    con terra invece che con il margine della griglia (= acqua che continua
    fuori scena). Un fiordo ha solo la bocca aperta -> vicino a 1. Una
    piattaforma tagliata dal riquadro -> basso.

    ATTENZIONE AL RIQUADRO. Se ritagli stretto attorno a una baia, il mare
    aperto esce dalla griglia e il valore crolla; se ritagli largo su un lago,
    sale a 1 qualunque cosa succeda. Il numero descrive **la griglia che gli
    hai dato**, non il pianeta. Va letto insieme a `open_cells`.
    """
    mask = np.asarray(water_mask, bool)
    h, w = mask.shape
    land_contacts = 0
    open_contacts = 0
    rs, cs = np.nonzero(mask)
    for r, c in zip(rs, cs):
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, c + dc
            if not (0 <= rr < h and 0 <= cc < w):
                open_contacts += 1        # l'acqua esce dalla scena
            elif not mask[rr, cc]:
                land_contacts += 1        # l'acqua sbatte contro terra
    total = land_contacts + open_contacts
    if total == 0:
        return {"enclosure": 0.0, "land_cells": 0.0, "open_cells": 0.0}
    return {
        "enclosure": land_contacts / total,
        "land_cells": float(land_contacts),
        "open_cells": float(open_contacts),
    }


def basin_axes_m(water_mask: np.ndarray, px_m: float, py_m: float) -> Tuple[float, float]:
    """Estensione del corpo d'acqua lungo i due assi, in metri.

    Il lato corto e' quello che conta per il modo trasversale: a Dickson ha
    oscillato da parete a parete, non per la lunghezza del fiordo.
    """
    mask = np.asarray(water_mask, bool)
    if not mask.any():
        return 0.0, 0.0
    rs, cs = np.nonzero(mask)
    span_y = (rs.max() - rs.min() + 1) * py_m
    span_x = (cs.max() - cs.min() + 1) * px_m
    return float(min(span_x, span_y)), float(max(span_x, span_y))


def seiche_profile(water_mask: np.ndarray, depth_m: float,
                   px_m: float, py_m: float) -> Dict[str, Any]:
    """Ritratto del bacino: quanto e' chiuso, e con che ritmo suonerebbe.

    Restituisce entrambi i modi. Quello trasversale (lato corto) e' il caso
    Dickson: piu' corto -> periodo piu' breve -> piu' ritorni d'acqua nello
    stesso tempo. Il periodo NON e' un punteggio di pericolo, e' la firma del
    bacino; serve a dire dove gli antinodi (i due capi) dovrebbero aver
    lasciato i depositi piu' alti.
    """
    short_m, long_m = basin_axes_m(water_mask, px_m, py_m)
    conf = confinement(water_mask)
    return {
        "enclosure": round(conf["enclosure"], 3),
        "open_cells": conf["open_cells"],
        "short_axis_m": round(short_m, 1),
        "long_axis_m": round(long_m, 1),
        "depth_m": depth_m,
        "transverse_period_s": _r(merian_period(short_m, depth_m, "closed")),
        "longitudinal_period_s": _r(merian_period(long_m, depth_m, "closed")),
        "note": (
            "Periodi da Merian, bacino rettangolare a fondale uniforme: ordine "
            "di grandezza, non misura. Gli antinodi stanno ai due capi: e' li' "
            "che un deposito di run-up dovrebbe essere piu' alto."
        ),
    }


def displacement_hazard(water_mask: np.ndarray, rim_steep_fraction: float,
                        depth_m: float, px_m: float, py_m: float) -> Dict[str, Any]:
    """Quanto sarebbe pericoloso questo bacino SE una frana ci cadesse dentro.

    Due fattori, moltiplicati, entrambi necessari:

        orlo ripido      da collapse_source_potential(): serve una sorgente che
                         acceleri. Senza, vedi Sahara Slide.
        confinamento     serve che l'energia non abbia dove andare. Senza, vedi
                         una qualunque costa aperta.

    Nessun volume compare qui dentro, ed e' voluto: Dickson ha fatto 200 m di
    run-up con 1/24.000 del materiale del Sahara Slide.

    NON e' una probabilita', e non dice che sia successo qualcosa. Dice: se
    cerchi un deposito di run-up sopra il piano d'acqua, i bacini con punteggio
    alto sono quelli dove ha senso guardare per primi. Il test resta il
    deposito, non questo numero.
    """
    prof = seiche_profile(water_mask, depth_m, px_m, py_m)
    score = float(prof["enclosure"]) * float(max(0.0, min(1.0, rim_steep_fraction)))
    return {
        **prof,
        "rim_steep_fraction": round(float(rim_steep_fraction), 3),
        "hazard": round(score, 3),
        "grade": "geometry",
        "kill_shot": (
            "Assenza di sedimento lacustre/marino sopra il piano d'acqua "
            "lungo i capi del bacino. Se non c'e' deposito di run-up, il "
            "meccanismo non ha operato qui."
        ),
        "cannot_say": (
            "Che sia successo. La geometria e' una predisposizione, non un "
            "evento. Il segnale sismico di una seiche antica non esiste in "
            "nessun archivio: non e' recuperabile, e' assente."
        ),
    }


def dickson_control() -> Dict[str, Any]:
    """Controllo positivo: Merian deve ritrovare i ~92 s osservati.

    Se un giorno questo smette di tornare, il colpevole e' la formula o le
    costanti qui sopra, non il bacino che stai studiando.
    """
    predicted = merian_period(DICKSON["width_m"], DICKSON["depth_m"], DICKSON["mode"])
    observed = DICKSON["observed_period_s"]
    ratio = predicted / observed if predicted else None
    return {
        "site": DICKSON["name"],
        "source": DICKSON["source"],
        "observed_period_s": observed,
        "predicted_period_s": _r(predicted),
        "ratio": round(ratio, 3) if ratio else None,
        # Merian su un fiordo a fondale irregolare: entro un fattore 1,5 e'
        # accordo. Chiedere di piu' sarebbe fingere una precisione che la
        # formula non ha.
        "passes": bool(ratio and 1 / 1.5 <= ratio <= 1.5),
        "volume_ratio_vs_sahara_slide": round(
            SAHARA_SLIDE["volume_Mm3"] / DICKSON["volume_Mm3"]
        ),
    }


def _r(v: Optional[float]) -> Optional[float]:
    return round(v, 1) if v is not None else None
