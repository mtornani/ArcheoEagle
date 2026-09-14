# Mega-Chad misurato — la casella §9 chiusa

**14 settembre 2026.** Casella aperta dal primo giorno di `CLAUDE.md` §9:

> Mega-Chad: se il contour 320 m esiste, `grade=dem-contour` e i nodi non sono i vertici del geojson.

Non era mai stata chiusa **perché il rilevatore non funzionava**. Chiusa oggi, e il risultato non è quello che speravo — è più interessante.

## Tre difetti che si nascondevano a vicenda

**1. Il tracciatore di isolinee era finto.** `shoreline_from_dem` raccoglieva i punti di attraversamento e li ordinava **per angolo attorno al centroide**, poi chiudeva l'anello. Presuppone un anello chiuso e convesso: su un segmento di sponda dentro un tile produce un poligono a stella senza rapporto con la geometria. Era un disegno, non una misura — proprio ciò che §2b vieta. Sostituito con marching squares.

**2. I tile pagati finivano nell'angolo sbagliato.** La bbox del Mega-Chad chiede **156 tile**, il tetto per richiesta è 12, e venivano presi in ordine di griglia: tutti nell'angolo sud-ovest, oltre 100 km dalla sponda attesa. Si misurava terreno a caso e lo si chiamava `dem-contour`. Ora sono ordinati per vicinanza al tracciato schematico.

**3. Un'isolinea non è una sponda.** A 320 m su un bacino enorme e piatto la quota viene attraversata dappertutto: **1136 polilinee** al primo giro pulito. Aggiunto il filtro a gradino: prima di accettare le isolinee di un tile si chiede al rilevatore — quello validato sul controllo positivo — se a quella quota il terreno si comporta da cordone.

Il difetto 1 rendeva invisibili il 2 e il 3. Si sono coperti a vicenda per settimane.

## Il risultato

| tile | score | gradino | isolinee |
|---|---|---|---|
| 16N14E | −0,76 | no | 475 |
| 12N18E | +0,57 | no | 6 |
| 11N16E | +0,41 | no | 135 |
| 13N18E | +0,45 | no | 28 |
| 12N11E | +0,96 | no | 70 |
| 11N12E | +0,97 | no | 1 |
| **13N11E** | **+3,32** | **sì** | **419** |
| 14N11E | −1,08 | no | 2 |
| 16N16E, 13N10E, 15N11E, 16N12E | — | indeciso | 0 |

**Un tile su dodici.** 15 nodi accettati, tutti dal settore 13,1–13,6 N / 11,3–11,8 E.

**`vs_schematic_km`: minimo 34,8 — mediana 82,8 — massimo 115,6.** Zero nodi entro 25 km dal disegno, due entro 50.

## Le due cose che questo dice davvero

**Il disegno sbaglia di ~83 km.** Non è un dettaglio di tracciato: è la distanza fra dove la letteratura schematica mette la sponda e dove il DEM trova un gradino a quella quota. Era esattamente il numero per cui `vs_schematic_km` esiste.

**E il disegno sbaglia anche su dove guardare.** Il tile della Bama Ridge — 11N13E, dove il controllo positivo passa, dove c'è un cordone datato OSL, dove il gradino è misurato su tre transetti indipendenti — è **23° su 156** per vicinanza al tracciato schematico. Fuori dai dodici che ci possiamo permettere. *Il solo posto in cui sappiamo che c'è una sponda vera non è dove il disegno dice di cercarla.*

## L'ipotesi che ne esce, da testare

Che a 320 m il gradino ci sia in un tile su dodici può voler dire due cose, e non so quale:

1. la sponda si conserva solo a tratti (dune, erosione, sepoltura);
2. **un livello unico per una sponda di oltre 500 km è il modello sbagliato.**

La seconda ha un appoggio serio dalla ricerca del 14/9: nel Great Basin il rimbalzo isostatico deforma **la stessa linea di riva fino a 71 m** fra centro e margine del bacino. Un paleolago grande come il Mega-Chad carica la crosta e la deforma quando si svuota. Se è successo, cercare 320 m ovunque è come cercare una riga dritta su un foglio piegato — e spiegherebbe insieme l'1-su-12 e il disaccordo 320 vs 329 m con Armitage 2015.

**Non l'ho testata.** Richiede un modello di deformazione idro-isostatica del bacino, che è un altro mestiere. Registrata qui come la prima domanda del prossimo giro.

## Stato della casella

- [x] il contour a 320 m esiste ed è tracciato davvero (marching squares, non un anello inventato)
- [x] `grade=dem-contour`
- [x] i nodi non sono i vertici del geojson: vengono dal DEM
- [x] `vs_schematic_km` calcolato: mediana 82,8 km
- [x] copertura dichiarata: 12/156 tile, 4 indecisi, troncamento riportato

**Quello che NON si può dire:** che sia la sponda del Mega-Chad. È un gradino misurato a 320 m in un settore, coerente con una sponda, in un bacino dove undici tile su dodici a quella quota non mostrano niente.
