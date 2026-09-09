# Calibrazione — lo strumento non e' ancora tarato

**Stato al 9 settembre 2026: il controllo positivo FALLISCE.**
ArcheoEagle sa disegnare l'isolinea a quota 320 m. Non ha ancora dimostrato di
saper distinguere una sponda vera da una quota qualunque. Finche' questo file
dice "fallito", il tool non puo' affermare di aver individuato una sponda: puo'
solo dire che ha disegnato un'isolinea.

## Perche' serve un controllo positivo

Un'isolinea esiste a **qualunque** quota. Che il codice ne produca una a 320 m
non dimostra niente. L'unico modo di sapere se lo strumento funziona e' dargli
da trovare una sponda che gli archeologi hanno gia' trovato.

**Bama Ridge** (Borno, Nigeria) — paleosponda del Mega-Chad, mappata, creste
documentate a **320 / 335 / 338 m**, datazione OSL **6.1±0.54 – 9.6±0.7 ka**.
Sta nel tile Copernicus GLO-30 lat 11–12 / lon 13–14.

Controllo negativo: tile lat 15–16 / lon 18–19 (Chad interno). Ha terreno che
attraversa i 320 m, nessuna sponda mappata li'.

Se lo strumento trova il gradino sul primo e non sul secondo, e' tarato.

## Cosa e' stato provato, e come e' andato

### Tentativo 1 — istogramma delle quote (SCARTATO)

"Pochi pixel a quota z" doveva indicare un gradino. Sul tile di Bama: 3.4% dei
pixel a 320 m contro 9.1% attesi. Sembrava funzionare.

Poi i controlli, e il test si e' smontato:

| tile | esito a 320 m |
|---|---|
| N11E013 Bama | 3.4% — minimo |
| N13E016 fondo lago | 0.0% |
| N21E010 Tenere | 0.0% — **ma il terreno li' parte da 468 m**: controllo nullo |
| N15E018 Chad interno | 10.8% — nessun minimo |

**Difetto:** "pochi pixel" non distingue *gradino ripido* da *terreno che a
quella quota quasi non arriva*. Confrontare tile diversi confonde inoltre il
segnale con la topografia regionale. Va confrontato **dentro lo stesso tile**.

### Tentativo 2 — min(occupazione, pendenza) (BOCCIATO DAL CONTROLLO)

Auto-controllato dentro il tile, punteggio in unita' di MAD (non percentile:
un percentile mette sempre qualcosa al primo posto, anche nel rumore puro).

| | step_score | occupancy_z | slope_z |
|---|---|---|---|
| Bama (documentata) | **1.56** | 1.56 | **10.92** |
| Controllo | −1.44 | −0.80 | −1.44 |

Soglia 2.0 → **fallito**. Diagnosi: la pendenza separa benissimo, l'occupazione
no, e il minimo viene trascinato giu' dalla statistica debole.

Verificato che il segnale di pendenza non siano le montagne (le Mandara Hills,
fino a 1337 m, stanno nel quadrante SE del tile):

| finestra | slope_z a 320 m |
|---|---|
| tile intero | 10.92 |
| meta' nord, **senza** montagne | 9.92 |
| solo quadrante montuoso | 2.45 |
| controllo | −1.44 |

Il segnale sopravvive togliendo le montagne. Non sono loro.

### Tentativo 3 — min(pendenza, continuita' laterale) (ANCORA FALLITO)

Sostituita l'occupazione con la continuita' (una sponda e' una linea lunga, uno
scarpato casuale e' una macchia). **La soglia non e' stata toccata.**

| | step_score | slope_z | elongation_z |
|---|---|---|---|
| Bama | **−0.76** | 10.92 | −0.76 |
| Controllo | −1.44 | −1.44 | 0.29 |

**Anche questa statistica e' confondibile:** misurata come span²/area della
componente connessa piu' grande, una macchia enorme che attraversa il tile
prende un punteggio alto quanto una linea sottile. I valori grezzi non sono
piatti (5–42 tra 310 e 335 m), quindi la statistica misura *qualcosa* — ma non
la cosa giusta. Il −0.76 su Bama **non e' una smentita della cresta**: e' una
statistica non valida.

## Dove siamo

Una sola statistica separa in modo netto: la **pendenza**, +9.9σ sul Bama
(senza montagne) contro −1.4σ sul controllo. Ma un test a statistica singola e'
esattamente il difetto denunciato per ρ: senza una seconda condizione, un
valore estremo puo' essere spurio.

**Le modifiche allo strumento si fermano qui.** Cambiare la seconda statistica
una terza volta finche' Bama passa e' il barare che questo modulo esiste per
impedire. Due tentativi sono gia' il limite.

## Regole che restano

1. La soglia `STEP_SCORE_THRESHOLD = 2.0` **non si muove** per far passare un
   caso. Si cambia lo strumento, mai il bersaglio.
2. Finche' il verdetto e' "fallito", nessuna schermata e nessun export puo'
   dire "sponda individuata". Isolinea disegnata, si.
3. Un gradino non e' una sponda nemmeno quando il test passera': faglia, fronte
   montuoso e bordo di duna danno la stessa firma. Il salto lo fa la
   letteratura o il campo.

## Prossimo passo onesto

Le statistiche su maschera raster sono il problema: lavorano su un'area, mentre
una sponda e' una **linea**. Serve tracciare davvero l'isolinea come polilinea
(non l'ordinamento per angolo attorno al centroide che usa oggi
`shoreline_from_dem`, che presuppone un anello chiuso) e misurarne lunghezza,
curvatura e coerenza di quota. E' un pezzo di lavoro a se', da decidere prima
di farlo.

## Come rieseguirlo

```python
from core.hydro.control import run_positive_control
run_positive_control(320.0)   # scarica 2 tile Copernicus, ~70 MB
```

I test unitari (`backend/tests/test_control.py`) non toccano la rete: verificano
che lo strumento veda un gradino sintetico e — piu' importante — che **non** ne
veda uno su una rampa a pendenza costante.
