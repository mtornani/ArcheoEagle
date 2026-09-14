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
