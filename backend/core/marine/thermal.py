"""Subsidenza termica della litosfera oceanica: quando un guyot era isola.

NATO PER RISPONDERE A UNA DOMANDA DEL 1969. Heezen et al. dragarono calcare
dall'Atlantis Seamount, videro litificazione in condizioni subaeree, e con
l'unico orologio che avevano — il radiocarbonio — conclusero che il seamount
fosse stato un'isola negli ultimi 12.000 anni. L'osservazione era giusta: la
vetta piatta a -268 m e' una piattaforma di abrasione annegata, e il Great
Meteor nella stessa catena ne ha una a -274 m. Ma il 14C su carbonato marino
a ~12 ka e' il caso peggiore possibile: pochi punti percentuali di carbonio
moderno da ricristallizzazione fanno leggere 12.000 anni a un calcare di
qualunque eta'.

Questo modulo usa l'orologio giusto. La litosfera oceanica sprofonda mentre si
raffredda, con una legge nota e calibrata su tutti gli oceani. Un guyot spianato
al livello del mare affonda insieme alla piastra che lo porta: la profondita'
della sua cima **e'** un cronometro.

Due modelli, perche' la dipendenza dal modello e' reale e va mostrata:

  Parsons & Sclater (1977)  semispazio che raffredda, d = 2500 + 350*sqrt(t)
                            sopra i ~70 Ma sovrastima: la piastra si appiattisce
  Stein & Stein (1992) GDH1 modello a piastra, d = 5651 - 2473*exp(-0.0278 t)
                            per t > 20 Ma. Il riferimento moderno.

ATTENZIONE, LIMITE DICHIARATO. La sola subsidenza termica di piastra a 85 Ma
(la crosta sotto il Great Meteor, da anomalia magnetica 34) da' ~6,5 m/Ma: in
10-26 Ma sono 65-170 m, non 268. La differenza viene da due cose che questo
modulo NON calcola: il decadimento del rigonfiamento del punto caldo, e la
flessura da carico vulcanico. Entrambe reali e attese su un edificio costruito
da hotspot. Quindi i numeri qui sono un **ordine di grandezza**, non una data.
Per la domanda in oggetto bastano e avanzano: il divario da spiegare e' 1000x.
"""
from __future__ import annotations

import math
from typing import Any, Dict, Optional, Tuple

# Catena Atlantis-Great Meteor (Seewarte), placca africana sopra il punto caldo
# del New England. Eta' da letteratura.
SEEWARTE_CHAIN = {
    "crust_age_ma": 85.0,           # anomalia magnetica 34 sotto il Great Meteor
    "volcanism_ma": (26.0, 10.0),   # formazione della catena sulla placca africana
    "basalt_ages_ma": (16.0, 11.0), # datazioni radiometriche, Great Meteor
    "source": "Tucholke & Smoot 1990; eta' crosta da An34",
    "grade": "literature",
}


def plate_depth_m(age_ma: float, model: str = "gdh1") -> float:
    """Profondita' del fondo oceanico a una data eta' della crosta, in metri."""
    t = max(float(age_ma), 0.0)
    if model == "ps77":
        return 2500.0 + 350.0 * math.sqrt(t) if t < 70.0 else 6400.0 - 3200.0 * math.exp(-t / 62.8)
    return 2600.0 + 365.0 * math.sqrt(t) if t <= 20.0 else 5651.0 - 2473.0 * math.exp(-0.0278 * t)


def subsidence_rate_m_per_myr(age_ma: float, model: str = "gdh1", window: float = 5.0) -> float:
    """Quanto sprofonda la piastra per milione di anni, a una data eta'.

    Cala con l'eta': una piastra vecchia e' gia' fredda e si muove poco. E' il
    motivo per cui un seamount su crosta di 85 Ma non puo' essere sceso di
    centinaia di metri in tempi archeologici.
    """
    a = max(float(age_ma), window)
    return (plate_depth_m(a + window, model) - plate_depth_m(a - window, model)) / (2 * window)


def implied_rate_mm_yr(summit_m: float, planation_ma: float) -> float:
    """Tasso medio implicito se la cima fu spianata al livello del mare allora.

    summit_m negativo (profondita' sotto il mare di oggi).
    """
    if planation_ma <= 0:
        raise ValueError("l'eta' di spianamento deve essere positiva")
    return (abs(float(summit_m)) / (float(planation_ma) * 1e6)) * 1000.0


def planation_age_range_ma(summit_m: float,
                           chain: Dict[str, Any] = SEEWARTE_CHAIN) -> Tuple[float, float]:
    """Quando la cima fu al livello del mare, dalla finestra vulcanica della catena.

    Un guyot viene spianato dalle onde mentre il vulcano e' attivo o poco dopo:
    l'eta' del volcanismo e' il limite superiore del tempo trascorso. Restituisce
    (piu' recente, piu' antico) in Ma.
    """
    young, old = min(chain["volcanism_ma"]), max(chain["volcanism_ma"])
    return (young, old)


def verdict_vs_claim(summit_m: float, claim_kyr: float, sea_level_then_m: float,
                     chain: Dict[str, Any] = SEEWARTE_CHAIN) -> Dict[str, Any]:
    """Confronta un'eta' rivendicata col tasso implicito dalla geologia della catena.

    Non e' retorica: e' il rapporto fra due tassi, e dice di quanto si sbaglia.
    """
    need = ((sea_level_then_m - float(summit_m)) / (float(claim_kyr) * 1000.0)) * 1000.0
    young, old = planation_age_range_ma(summit_m, chain)
    r_young = implied_rate_mm_yr(summit_m, young)
    r_old = implied_rate_mm_yr(summit_m, old)
    return {
        "claim_kyr": float(claim_kyr),
        "rate_required_mm_yr": round(need, 2),
        "implied_rate_range_mm_yr": (round(r_old, 4), round(r_young, 4)),
        "planation_range_ma": (old, young),
        "overstatement_factor": (round(need / r_young), round(need / r_old)),
        "verdict": "falsificato" if need / r_young > 10 else "compatibile",
        "cannot_say": (
            "che il seamount non sia mai stato un'isola: lo e' stato, e la cima "
            "piatta lo dimostra. Solo il QUANDO e' sbagliato."
        ),
    }
