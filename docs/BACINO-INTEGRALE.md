# Tentativo 11 — integrale di bacino. Il controllo positivo PASSA (alla scala del bacino).

9 novembre 2026. Chiude la "direzione non provata n.1" di `CALIBRAZIONE.md`.
Previsione e kill-shot: `docs/t11/PREREG-T11.md`, SHA-256 in `docs/t11/PREREG-T11.sha256`, scritti prima di aprire i tile.

## Cosa e' stato fatto
- 225 tile Copernicus GLO-90 (lat 6..21 N, lon 8..23 E), aggregati a 12" (media e minimo).
- Priority-flood dal bordo (ricostruzione morfologica, stesso risultato di `core/marine/basin.py`, in C).
- Seme: cella piu' bassa del Bodele. Area sferica per cella.
- Soglia rifatta a 1" (GLO-30) nella finestra 9..11 N, 14..16 E.
- Codice: `tools/tentativo11_bacino.py`, `tools/tentativo11_soglia30.py`. Numeri: `docs/t11/t11_report.json`, `docs/t11/t11_sill30.json`.

## Risultato

| | previsto | misurato | esito |
|---|---|---|---|
| P1 quota di sfioro | 315–335 m | 324.18 m (media, 4-vicini) · 323.66–324.18 nelle 4 varianti · 324.21–324.38 a 1" | PASSA |
| P2 pour point | <= 100 km da 9.9 N 15.0 E | 10.28 N 15.30 E, 53 km (spartiacque Logone–Mayo Kebbi) | PASSA |
| P3 area a sfioro | 300–400 mila km2 | 344.315 km2 (344.3–350.0 mila nelle varianti) | PASSA |
| P4 bordo vs Bama Ridge | <= 10 km | Bama 0.5 km, Maiduguri 0.0 km | PASSA |
| truncated | false | false in tutte le varianti | valido |

Volume ~14.300 km3, profondita' massima 162 m.
Tasso di base per P4: il 3.4% del bbox sta entro 10 km dal bordo calcolato. Controlli: N'Djamena 89 km, Kano 341 km.
Letteratura: sponda 325 +/- 5 m e ~340.000 km2 (Leblanc et al. 2006); soglia Mayo Kebbi 325 m (Mémin et al. 2020).

## Correzione dichiarata
`pour_point` come "cella piu' bassa dell'orlo" pareggia con ogni cella di riva a quota = sfioro
(visto sul run `min`: punto messo a 485 km). Sostituito con "cella dell'orlo che ha un vicino che drena
sotto lo sfioro". La quota di sfioro non cambia. Lo stesso difetto e' in `core/marine/basin.pour_point`: da correggere li'.

## Cosa si puo' dire / non dire
- SI: alla scala del bacino lo strumento ritrova quota, area, sbocco e posizione di una sponda datata da terzi.
- NO: "sponda individuata" su un tile. I rilevatori per-tile (tentativi 1–10) restano FALLITI. Regola 2 invariata.
- Indipendenza: il 325 di Leblanc viene da un DEM (SRTM30). Qui cambiano dato e codice, non il principio.
  L'indipendenza vera e' P4 (OSL sul Bama, mai usato nel calcolo).
- Topografia moderna, DSM (chioma). Non data niente.
- La posizione esatta della cella di soglia a 1" non e' robusta (spartiacque piatto): si dichiara la zona, non il pixel.

## Cosa sblocca
Tentativo 8 (sponda deformata): ora esiste una maschera di sponda indipendente dai tile.
Prossimo: quota del gradino a stazioni lungo il bordo calcolato, contro il rimbalzo idro-isostatico di Mémin et al. 2020.
Previsione da registrare prima.

## Nota per STATO.md / FOCE-TAMANRASSET.md
La frase "frequenza 3x nell'umido compatibile col fiume" va ritirata. Sul CSV del repo (GeoB8509-2):
14.6–12.9 ka 6 eventi (3.5/ka) · 12.9–11.7 ka 5 (4.2/ka) · 11.7–5.5 ka 4 (0.65/ka) · 5.5–0 ka 3 (0.55/ka).
Olocene umido vs arido: indistinguibili (binomiale esatto p = 1.0). Il grappolo e' la deglaciazione:
Wien et al. 2006 lo legano alla risalita rapida del mare, Henrich et al. 2010 a sabbie eoliche rimobilizzate.
Resta in piedi solo l'end-member fine di Zuehlsdorff 2007 (non scaricabile come serie).
