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

---

# Risultato — e una correzione a quello che ho affermato stamattina

## Prima: un bug mio, trovato e corretto

Il primo giro dava 1 sito su 12 sopra soglia. Ma le quote migliori erano numeri storti — 317,85 / 323,55 / 1361,99 — perché la mia griglia di sweep partiva da `zmin+2` e **non campionava mai le quote dichiarate**. Sul tile della Bama passava per 317,85 invece di 320,0, e il punteggio crolla da +4,42 a +1,30 in due metri. Difetto dello script, non del rilevatore. Rilanciato con griglia **ancorata alla quota dichiarata**.

## Previsione C — falsificata, e fa male

*"Almeno 7 delle 11 mostrano un gradino sopra soglia alla quota dichiarata."*

| sito | miglior punteggio | a quota | scarto dalla dichiarata |
|---|---|---|---|
| **Bama tile 11,13 (il mio)** | **+4,42** | 320,0 | **0,0** |
| **Turkana SHS** | **+2,11** | 427 | −18 |
| Bodélé | +1,65 | 247 | +22 |
| Sunstone Knoll | +1,19 | 1362 | −36 |
| Bonneville | +0,89 | 1506 | −46 |
| Lake Surprise | +0,76 | 1420 | −50 |
| Sehoo / Lahontan | +0,67 | 1277 | −60 |
| Turkana MHS | +0,56 | 479 | +22 |
| Goz Kerki | +0,47 | 295 | −32 |
| Bama Ridge (posizione Gemini) | +0,34 | 383 | +54 |
| Lisan | +0,33 | −184 | −20 |
| Provo | +0,19 | 1420 | −30 |

**Due su dodici sopra soglia. E una sola alla quota dichiarata: il tile su cui il rilevatore è stato sviluppato.**

La riga che chiude il discorso è **Bonneville: +0,89**. È la paleosponda più studiata del pianeta, una banchina erosiva enorme, visibile dallo spazio. Il mio rilevatore non la vede — a nessuna quota entro ±60 m.

## La correzione

Stamattina ho scritto, in un commit e in `STATO.md`: *"il controllo positivo passa"*, *"il fallimento centrale del progetto è risolto"*.

**Era troppo.** Quello che passa è il rilevatore **sul tile su cui è stato costruito**. Su undici sponde datate indipendenti non passa. Questo non è un controllo positivo superato: è **sovradattamento a un esempio**, ed è precisamente ciò che un banco di taratura serve a smascherare.

Il risultato di stamattina resta vero in ciò che dice — a scala 30 m il cordone è invisibile, a 120 m compare — ma non autorizza la conclusione che ne ho tratto. **Trovare il bersaglio su cui hai tarato non è generalizzare.**

## Previsione B — l'unica cosa che sopravvive, e va presa piano

*"D della sponda più bassa di D alle quote di controllo nello stesso tile."*

| | |
|---|---|
| più liscia delle quote di controllo | **7 su 10** |
| differenza media | **−0,072** |
| t appaiato | **−2,30** (df 9; serve \|t\|>2,26 per p<0,05) |
| correlazione con la lunghezza del contorno | +0,402 (sotto la soglia 0,5 dichiarata) |

Nella direzione prevista, appena oltre la significatività, con il controllo artefatto superato **di misura**.

E c'è una cosa che merita attenzione: **D discrimina dove `step_score` fallisce.** Bonneville non è un gradino rilevabile (+0,89) ma la sua isolinea è nettamente più liscia delle quote di controllo (1,137 contro 1,296). Stessa cosa per Lisan (1,160 contro 1,362) e Provo (1,141 contro 1,358).

Se questo regge, **la forma è la strada e la pendenza no.**

**Ma non lo dichiaro un risultato.** n=10, t al pelo, tre previsioni corse senza correzione per confronti multipli dichiarata in anticipo, e una correlazione con la lunghezza che è bassa ma non nulla. È un'ipotesi che ha superato il suo primo test, non una scoperta.

## Previsione A — regge

D delle sponde: min 1,029, mediana 1,177, max 1,283. **7 su 10 nella banda 1,05–1,25** prevista.

## Cosa serve adesso

1. **Più sponde datate.** Dieci sono poche per una soglia. Le 11 di Gemini sono un inizio, e vanno **verificate una per una** sulle fonti primarie: `Bama Ridge (posizione Gemini)` dà +0,34 e il mio tile a 30 km di distanza dà +4,42 — almeno una delle sue coordinate è sbagliata.
2. **Un controllo negativo vero**: D su gradini che sono certamente *non* sponde — scarpate di faglia note, fronti di duna noti. Le "quote di controllo" a caso sono un null, non un negativo mirato.
3. **Smettere di usare `step_score` come se generalizzasse.** Finché non passa su sponde che non ha mai visto, vale per un tile.
