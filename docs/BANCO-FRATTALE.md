# Banco di taratura frattale — previsione registrata PRIMA di correre

**14 settembre 2026.** Committato prima dell'esecuzione.

## Cosa provo

Il rilevatore dice "gradino", non "sponda": faglia, fronte montuoso e bordo di duna danno la stessa firma. Serve un discriminante di **forma**. Ipotesi: una costa costruita dalle onde ha una rugosità caratteristica, misurabile come dimensione frattale col compasso di Richardson, `L(r) ~ r^(1−D)`.

Undici paleosponde **datate** dal round Gemini, ciascuna con quota dichiarata e coordinate. Per ognuna: scarico il tile, medio a 120 m, traccio l'isolinea alla quota dichiarata, misuro D. **E misuro D anche a quote di controllo** prese a caso nello stesso tile, dove nessuno dichiara una sponda.

## Due test in uno

1. **Verifica delle fonti.** Le undici quote vengono da Gemini e **non sono verificate**. Il DEM dirà se a quella quota c'è davvero un gradino. Un sito che non lo mostra è un'affermazione che cade — e il round Gemini ha già sbagliato 2 volte su 8.
2. **Taratura.** Sulle sponde che superano il test 1, D diventa una distribuzione di riferimento.

## Previsione

**A.** D delle sponde datate sta in una banda stretta, **fra 1,05 e 1,25**.
**B.** D delle sponde è **sistematicamente più bassa** di D alle quote di controllo nello stesso tile: una costa è più liscia del contorno di un versante qualunque.
**C.** Almeno **7 delle 11** mostrano un gradino sopra soglia alla quota dichiarata.

Se **B** non regge, D non discrimina e l'idea muore lì — il controllo negativo è la parte che conta, non la banda.

## Il modo più probabile in cui fallisce

Che D misuri **la risoluzione del DEM e la lunghezza del contorno**, non la geomorfologia: contorni corti danno poche scale utili e stime instabili (nel pilota tre casi su cinque avevano solo 3 scale). Se D correla con la lunghezza del contorno più che col tipo di sito, è un artefatto e va detto.

**Controllo dichiarato adesso:** riporto D contro il numero di punti del contorno. Se la correlazione è forte, il risultato non vale.
