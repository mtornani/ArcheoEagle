# Isostasia sul Mega-Chad — previsione registrata PRIMA di correre

**14 settembre 2026.** Committato prima dell'esecuzione. Il git log è la prova. Previsione cieca: non conosco il risultato.

## L'ipotesi, con un segno

Un lago carica la crosta. Quando si svuota, la crosta **rimbalza**, e rimbalza **di più dove il carico era maggiore** — cioè al centro profondo del bacino, non ai margini.

Conseguenza geometrica: una sponda che al momento della formazione era **orizzontale** oggi non lo è più. È **inarcata a cupola**: più alta verso il centro del bacino, più bassa ai margini.

Non è speculazione: è il caso di scuola del Lago Bonneville, dove la stessa linea di riva sta a 1552 m ai margini non deformati e fino a **1628 m** al centro — **71 m di inarcamento**.

## Perché il Mega-Chad è il candidato giusto

Se è successo, spiega **tre cose insieme** che finora ho trattato come separate:

1. **1 tile su 12 ha un gradino a 320 m.** Se la sponda è inarcata, a 320 m la becchi solo dove la deformazione è vicina a zero. Altrove sta a un'altra quota.
2. **320 contro 329 m** (mio DEM contro Armitage 2015): due misure giuste in due posti diversi della stessa superficie piegata.
3. Il modello "un livello unico per 500 km di sponda" sarebbe **sbagliato in linea di principio**, non impreciso.

## Previsione, falsificabile

Per ogni tile attorno al bacino cerco la quota del **miglior gradino** (sweep 300–340 m, punteggio del rilevatore validato), poi metto quella quota contro la **distanza dal centro del bacino** (il punto più basso del fondo, misurato sul DEM, non assunto).

**Prevedo una pendenza NEGATIVA: la quota del gradino cala allontanandosi dal centro.**

- Se esce **negativa e coerente** → rimbalzo idro-isostatico, e il modello a livello unico va buttato.
- Se esce **piatta** → nessun rimbalzo rilevabile, e l'1-su-12 va spiegato con la conservazione a tratti.
- Se esce **positiva** → l'ipotesi è morta nel segno, che è il modo più netto di morire.

## Il modo più probabile in cui questo non funziona

**I gradini rilevati saranno troppo pochi.** Ieri, a quota fissa, uno su dodici. Se lo sweep ne trova tre o quattro in tutto, non c'è niente da regredire e la risposta onesta è "non misurabile con questo campione", non una retta tirata su quattro punti.

Soglia dichiarata adesso: **sotto 6 tile con gradino non regredisco nulla.**

## Nota di metodo — perché non uso un livello unico nello sweep

È il punto sollevato da Mirko: stiamo misurando come si misura π con un poligono. Cercare la sponda a 320 m ovunque è fissare il numero di lati. Lasciare che ogni tile dica **a quale quota ha il suo gradino** è lasciare che sia la misura a parlare — e solo dopo si guarda se quelle quote stanno su una superficie sensata.

---

# Risultato — stesso giorno, dopo l'esecuzione

80 tile spazzati, 21 quote ciascuno (300–340 m, passo 2 m), scala 120 m, media d'area. Centro del bacino **misurato** sul DEM, non assunto: **17,5N 17,5E a 156,5 m** — la depressione del Bodélé.

## Il filtro, prima dei numeri

| | tile |
|---|---|
| analizzati | 80 |
| con un punteggio | 64 |
| sopra soglia (≥2,0) | 8 |
| **e con picco INTERNO allo sweep** | **7** |

Il picco interno non è pignoleria: un massimo che cade a 300,0 o 340,0 significa che il punteggio è monotono fino al bordo della finestra, cioè che non c'è nessun gradino — solo una tendenza tagliata. Otto tile su otto sarebbero diventati sette.

## La previsione è confermata nel segno e falsificata nella sostanza

| | |
|---|---|
| pendenza | **−2,56 m / 100 km** |
| intercetta | 338,4 m |
| R² | 0,344 |

Segno negativo, come previsto. E non basta.

**Leave-one-out:** il segno sopravvive a ogni cancellazione — sempre negativo. Ma togliendo `16N18E`, l'unico punto vicino al centro (154 km), **R² crolla da 0,344 a 0,075**. Sei dei sette punti stanno fra 630 e 808 km: la retta è ancorata da un punto solo.

**E il colpo che chiude — dispersione a distanza costante:**

| | |
|---|---|
| 6 punti nella fascia 630–808 km | quote 306, 312, 320, 320, 322, 334 m |
| escursione osservata **alla stessa distanza** | **28 m** |
| dislivello previsto dal modello su quella fascia | **4,5 m** |
| **rumore / segnale** | **6,2×** |

Alla stessa distanza dal centro la quota del gradino varia di 28 metri, mentre l'intero effetto radiale previsto ne vale 4,5. **Il modello isostatico radiale non è supportato.**

## Ma non è un nulla: è un'informazione precisa

La variazione c'è ed è grande — 28 m — **solo che non è organizzata radialmente**. Tre spiegazioni, e il mio test non le separa:

1. **I gradini non sono tutti sponde.** Il `non_puoi_dire` del rilevatore lo dice da sempre: *"faglia, fronte montuoso e bordo di duna danno la stessa firma"*. Sta dicendo "gradino", non "sponda".
2. **Stand multipli.** Armitage 2015 dà per la Bama Ridge **tre gruppi OSL** (11,5–10,4 / 9,4–8,1 / 6,6–5,4 ka). Tile diversi possono conservare **sponde diverse** a quote diverse. Non è rumore: è storia.
3. Deformazione reale ma non radiale (il carico di un lago non è un disco).

La 2 è la più economica e la più trascurata. **Il modello "una sponda" era sbagliato prima ancora del modello "un livello".**

## Cosa potrebbe funzionare — la forma, non la quota

Il rilevatore trova gradini e non sa dire quale sia una sponda. Serve un discriminante di **forma**, e la strada è quella del paradosso della costa: una costa costruita dalle onde ha una rugosità caratteristica, diversa da una scarpata di faglia (rettilinea) o da un bordo di duna.

Dimensione frattale col metodo del compasso (Richardson), `L(r) ~ r^(1−D)`:

| caso | D | scale usate |
|---|---|---|
| **11N13E — Bama Ridge, sponda datata OSL** | **1,114** | 5 |
| 13N11E — gradino forte a 320 m | 1,111 | 3 |
| 10N17E — quota anomala 334 m | 1,196 | 3 |
| 10N15E — quota bassa 306 m | 1,268 | 3 |
| 16N18E — vicino al centro | n/d | <3 |

I due gradini a **320 m** hanno D quasi identica alla sponda datata (1,114 contro 1,111). Quelli alle quote anomale sono più **rugosi**. L'ordinamento è quello che l'ipotesi prevede.

**È un pilota, non un test.** Cinque casi, tre con sole tre scale utili, nessuna stima d'incertezza. Chiamarlo risultato sarebbe esattamente l'errore che questo repo esiste per non fare.

**Cosa lo renderebbe un test, ed è già a portata:** le **11 paleosponde datate** che il round Gemini ha portato (Bama, Goz Kerki, Bodélé, Bonneville, Provo, Sunstone Knoll, Sehoo, Lake Surprise, Turkana MHS e SHS, Lisan). Misurare D su undici sponde **note e datate** dà una distribuzione di riferimento. Da lì D smette di essere un'analogia e diventa una soglia: il discriminante che al rilevatore manca.

## Stato

- Modello isostatico radiale: **non supportato**, con numeri.
- `vs_schematic_km`: corretto da punto-vertice a punto-segmento. **Mediana da 82,8 a 46,5 km** — metà del valore di ieri era l'errore del mio righello.
- Discriminante frattale: **pilota promettente, da calibrare sulle 11 sponde datate.** È il prossimo lavoro.
