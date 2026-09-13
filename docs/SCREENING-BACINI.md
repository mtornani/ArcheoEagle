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

---

# Risultato — stesso giorno, dopo l'esecuzione

## La previsione era sbagliata al primo colpo, e nel modo che avevo scritto

Primo giro: **hazard 0,9–1,0 su tutti e dieci i bersagli**, Bodele compresa. Non era una scoperta, era un metro rotto — e l'avevo previsto come seconda possibilita': *"o ho sbagliato la previsione o il codice sta misurando un artefatto del riquadro"*.

Due bug, uno dei quali vecchio e mio.

**1. Unita' della pendenza (bug preesistente in `collapse_source_potential`).** `np.gradient` su un array grezzo restituisce **metri per indice di pixel**, non m/m. Confrontarlo con `steep=0.30` confronta unita' diverse. Su DEM decimato (pixel ~240 m) qualunque terreno reale supera la soglia, e la funzione tornava ~1,0 ovunque. In `control.py` avevo corretto esattamente questo il 9 settembre (`pixel_metres`, `_slope_map`); `basin.py` non aveva mai ricevuto la correzione. **Due moduli miei che misuravano la pendenza in due unita' diverse per quattro giorni.**

**2. Coriandoli invece di bacini.** `water = filled - dem > 1 m` seleziona migliaia di micro-depressioni sparse (fino a **1674 componenti** su un solo tile). Nessuna tocca il bordo della griglia, quindi `confinement()` le dichiarava tutte perfettamente chiuse: 1,0 ovunque. Misurava la granulosita' del DEM.

Correzioni: `px_m`/`py_m` opzionali in `collapse_source_potential` (pendenza adimensionale), nuova `largest_depression()` che restituisce **una** componente connessa o `None`. 6 test di regressione. Suite 107/107.

## Secondo giro, e il controllo positivo che lo rende leggibile

Zero ovunque non vale niente finche' non dimostri che la pipeline sa dire di si'.

| | pixel | rilievo | pendenza p99 | orlo ripido |
|---|---|---|---|---|
| **Sognefjord, Norvegia (controllo +)** | 118 m | 1913 m | 1,29 | **0,356** |
| Hoggar (montagne vere, Sahara) | 113 m | 1955 m | 0,42 | 0,0 |
| Qattara, **piena risoluzione** | 27 m | 73 m | 0,039 | 0,0 |
| Tamanrasset | 115 m | 101 m | 0,041 | 0,0 |

Screening completo, secondo giro: **hazard 0,0 su tutti i corridoi**; Chott Melrhir 0,015, che e' rumore.

## Cosa e' stabilito

**La previsione era giusta nella sostanza: nessun bacino sahariano ha la geometria di Dickson.** E ora e' una misura con un controllo positivo che passa, non un'opinione.

Le due righe che valgono piu' delle altre:

- **Qattara a 27 m/pixel da' zero.** Non e' la decimazione che spiana una scarpata: alla risoluzione nativa del DEM, non c'e' pendenza.
- **L'Hoggar ha 1955 m di rilievo e orlo a zero.** Il Sahara *ha* montagne. Non ha **catini a pareti ripide**. Sono due cose diverse, e questa e' la distinzione che il meccanismo di Dickson richiede.

Punto 4 della previsione (Qattara esclusa dall'acqua, non dalla geometria): **non verificato, ed e' peggio di cosi'** — Qattara e' esclusa gia' dalla geometria, prima ancora di discutere se avesse acqua.

## Limiti dichiarati

- Un tile 1° per bersaglio, preso al centro del corridoio. La scarpata nord di Qattara e' lunga ~300 km: la mia finestra ne vede un pezzo, con 73 m di rilievo. Non escludo che un tratto sia piu' ripido — escludo che il bacino nel suo insieme sia un fiordo.
- `enclosure` resta 1,0 quasi ovunque anche dopo la correzione, perche' una conca interna non tocca mai il bordo del tile. **A scala di tile la variabile che discrimina e' la pendenza, non il confinamento.** L'enclosure diventa informativa solo su bacini costieri o tagliati dal riquadro.
- Il fiordo di controllo e' Sognefjord, non Dickson: Copernicus GLO-30 sull'Artico alto non e' stato provato. Stessa classe geometrica, sito diverso.
