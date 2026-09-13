# Screening bacini confinati — previsione registrata PRIMA di correre

**13 settembre 2026.** Questo blocco e' committato prima di eseguire lo screening. Il git log e' la prova. Se i risultati non lo confermano, resta scritto quello che avevo previsto.

## Cosa corro

`displacement_hazard()` (= `enclosure` x `rim_steep_fraction`) su ogni corridoio in `CORRIDOR_IDS`, con DEM Copernicus GLO-30 reale. Piu' tre depressioni sahariane vere che nel repo **non** ci sono e che sono i soli candidati geometrici plausibili: Qattara, Chott Melrhir, Bodele.

## Previsione

1. **Tutti i corridoi sahariani prendono hazard ~0.** Sono corridoi fluviali a bassa pendenza: `rim_steep_fraction` crolla, e il prodotto con essa. Non e' un fallimento del codice: e' il codice che dice che quei posti non sono Dickson.
2. **Mega-Chad in particolare ~0.** Lago enorme e piatto. La Bama Ridge e' un cordone litorale, gradiente dolce. Il bacino piu' importante del progetto e' il meno adatto a questo meccanismo.
3. **Qattara e' l'unico con orlo ripido** (scarpata nord, ~-133 m sotto il livello del mare).
4. **E Qattara fallisce lo stesso**, ma alla condizione 3, non alla geometria: e' una conca di deflazione eolica iperarida, non ha avuto un corpo d'acqua profondo e permanente nella finestra 15–5 ka. Geometria giusta, acqua mancante.

**Quindi la previsione complessiva e' un NO su tutta la linea.** Se esce un hazard alto da qualche parte, o ho sbagliato la previsione o il codice sta misurando un artefatto del riquadro — e la seconda va esclusa prima di festeggiare.

## Perche' correrlo se prevedo no

Perche' "lo so gia'" non e' una misura, e perche' uno screening che esclude e' un risultato: restringe dove cercare. E perche' se `enclosure` restituisse valori alti su un corridoio fluviale aperto, saprei che la metrica e' rotta — questo e' anche un test del codice, non solo dei bacini.
