# Foce Tamanrasset — archivi pubblici, 10 settembre 2026

Non è Cap Blanc. Non è GeoB7920 (pista A, chiusa). La foce è il **Canyon di Capo Timiris**, ~19.2–19.7°N, 17.7–18.9°W. Skonieczny et al. 2015 allineano il paleofiume sepolto in Mauritania con la testa di questo canyon.

## Archivi (aperti, no key)

| dove | cosa | DOI |
|---|---|---|
| PANGAEA / MARUM GeoB | turbiditi datate, 4 carote M58/1 | [10.1594/PANGAEA.738191](https://doi.pangaea.de/10.1594/PANGAEA.738191) |
| idem | granulometria sand/silt/clay GeoB8509-2 | [10.1594/PANGAEA.665705](https://doi.pangaea.de/10.1594/PANGAEA.665705) |
| idem | ¹⁴C AMS GeoB8509-2 | [10.1594/PANGAEA.710992](https://doi.pangaea.de/10.1594/PANGAEA.710992) |
| idem | XRF fase solida GeoB8502-2 | [10.1594/PANGAEA.134703](https://doi.pangaea.de/10.1594/PANGAEA.134703) |
| MARUM | carote fisiche, cruise Meteor M58/1 (2003) | Brema |

Carote sulla foce:

| carota | lat | lon | z | ruolo |
|---|---|---|---|---|
| GeoB8502-2 | 19.220 | −18.934 | −2956 m | levee, 14.8 m |
| GeoB8506-2 | 19.710 | −17.716 | −1827 m | levee |
| GeoB8507-3 | 19.475 | −18.100 | −2411 m | levee |
| GeoB8509-2 | 19.451 | −18.089 | −2585 m | intra-canyon |

ODP 658C / GeoB7920 (~20.75°N) è l’asse della **piuma di polvere**, 1.5° più a nord. Non è la foce.

IMLGS NOAA: dismesso 5 mag 2025. SESAR tiene i campioni, non i proxy.

## Cosa è pistola, cosa no

**Necessità** (il fiume, se scorre, deve lasciare questo): fango fluviale e/o torbiditi nel canyon durante il periodo umido, poi fame.

**Già misurato da terzi, scaricabile:**

Turbiditi Wien 2006 (`Duration` = età di messa in posto, unità `ka`, non durata):

- GeoB8509-2: 18 eventi, dal 14.6 ka al 0.5 ka. Fitta tra 14.6 e 12.3 ka, poi rare.
- GeoB8502-2: T1 a **10.1 ka** (dentro AHP), poi 24–245 ka (fuori finestra recente).

Questo dice: **sedimento arrivava nel canyon quando il Sahara era umido.** Grado: letteratura + tabella aperta. Non promuove il LineString da `schematic` a `survey`.

## XRF Si/Al su GeoB8502-2 — first principles

Carlson: l'acqua muove il quarzo. Musk: se T1 a 10.1 ka è un cannone di sabbia glaciale, Si/Al deve sembrare i letti a 8–12 m (Si/Al 8–10). Se è un fiume di fango su Sahara vegetato, no.

Misura (PANGAEA.134703, `data/cores/geob8502_xrf_slim.csv`, test `test_timiris.py`):

| finestra | profondità | Si/Al medio | Si/Al max |
|---|---|---|---|
| pelagite sopra T1 | 0.02–0.22 m | 2.73 | — |
| **T1 AHP 10.1 ka** | 0.25–0.47 m | **3.89** | **6.42** |
| pelagite sotto | 0.50–1.40 m | 3.60 | — |
| bombe Pleistocene | 8.40–12.60 m | 3.84 (media diluita) | **10.57** |

T1 è un impulso rispetto al pelagite che lo copre. Non è il cannone di sabbia del Pleistocene. Fango, non duna in transito. Resta una torbidite: fiume o scarpata. La chimica non decide l'origine. Decide che **non** è lo stesso oggetto dei dump glaciali.

Codice: `backend/core/cores/timiris.py`. Claude: attacca il cutoff 0.25–0.47, il confronto max-vs-media, o tira Si/Al su 8507.

**Testato qui, e non è la pistola:** frazione argilla su GeoB8509-2 (PANGAEA.665705) vs modello d’età 710992.

Cutoff 5.5 ka interpolato ~2.44 m. Esclusi i campioni sabbiosi (turbiditi, sand ≥15%):

| finestra | n | clay % media | sand % media |
|---|---|---|---|
| < 5.5 ka (dopo) | 22 | **48.8** | 6.2 |
| ≥ 5.5 ka (AHP, fondo carota ~12.9 ka) | 57 | **37.6** | 6.2 |

L’argilla **non** sale nell’umido. Il proxy grezzo sand/silt/clay non è l’end-member fluviale del paper. Zühlsdorff 2007 lo mette sulla **silt carbonate-free** (EM più fine = fango di fiume, early–mid Holocene). Quella spettrometria **non** è nella tabella PANGAEA: è nel paper.

**Specificità:** una torbidite nel canyon può essere fiume **o** crollo di scarpata **o** polvere di piattaforma. Frequenza 3× nell’umido è compatibile col fiume; non lo identifica. L’EM fine è più specifico e non è scaricabile come serie.

## Cosa chiuderebbe (da casa vs Brema)

Da casa, aperto:

1. XRF Si/Al · Fe/Al su GeoB8502-2 ([PANGAEA.134703](https://doi.pangaea.de/10.1594/PANGAEA.134703)) — Wien usa Si/Al per separare torbidite/pelagite. Non è ancora Sr-Nd.
2. Replicare il conteggio torbiditi su 8506/8507 (stessa tabella 738191).

Non da casa:

- Spettri granulometrici EM (Holz 2005 / Zühlsdorff 2007 figure).
- Sr-Nd sulla frazione fine di **Timiris** (Hoggar vs erg). Su 658C è pista A, posto sbagliato.
- Seconda carota con EM + età sulla foce.

## Tesi, detta onesta

La pistola fumante del Tamanrasset **non è una sponda nel DEM**. È fango di fiume nel canyon, datato. Gli archivi pubblici danno il canyon, le carote, le età delle torbiditi. Non danno (ancora) l’end-member unmixed. Argilla grezza, misurata stanotte, **non** conferma il fiume.

Kill-shot remoto: EM fine o Sr-Nd su Timiris, stessa carota, stessa età. Finché manca: premessa “il fiume scorreva” sostenuta; “qui c’era una civiltà” no.
