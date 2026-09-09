# Cercare terra abitata oggi sommersa — metodo e criteri

Non "trovare Atlantide". Questo cerca **paesaggi annegati ad alta probabilita'
di insediamento e conservazione**, cioe' decide dove valga la pena mandare un
sonar o un carotaggio. L'esito normale e onesto e' "niente sopra il caso".

## 0. Il vincolo che decide cosa si puo' trovare

| profondita' | annegata | cosa poteva esserci |
|---|---|---|
| -30 / -130 m | 20.000-7.000 anni fa | caccia-raccolta, primo neolitico. **Niente monumenti** |
| 0 / -20 m | < 7.000 anni fa | citta' vere: Pavlopetri, Eracleion, Baia |

L'architettura monumentale compare quando il mare si era gia' fermato. "Citta'
monumentale a -100 m" e' un'impossibilita' cronologica, non un bersaglio
difficile.

**L'unica finestra in cui le due si sovrappongono e' la subsidenza tettonica**:
coste scese piu' di quanto spieghi il solo eustatismo. E' li' che l'unica
"acropoli sommersa" fisicamente possibile puo' stare — ed e' li' che le si
trova davvero.

## 1. Criteri di OCCUPAZIONE — dove vivevano

1. **Residenza costiera.** Quanto a lungo il punto e' rimasto entro pochi km
   dalla riva. E' un integrale sulla curva del livello del mare, con la fascia
   verticale fissata dalla pendenza locale. Piattaforma piattissima: la riva
   sfreccia via, residenza breve. Pendio ripido: residenza lunga ma terreno
   inabitabile. **L'ottimo e' intermedio, e la tensione e' voluta.**
   → `coastal_residence_kyr()`
2. **Acqua dolce.** Paleovalli fluviali, confluenze, foci, lagune, sorgenti
   carsiche. E' il predittore singolo piu' forte di densita' insediativa.
   Atlit-Yam sta su una sorgente; i siti della Florida sulle risorgive.
   → da estrarre come reticolo di drenaggio dalla batimetria. **Non implementato.**
3. **Riparo.** Baie e concavita' della paleocosta, fetch basso. Non promontori
   esposti. → **Non implementato.**
4. **Pendenza abitabile.** Penalizzazione quadratica oltre il 5%.
   → `SLOPE_MAX`

## 2. Criteri di CONSERVAZIONE — dove sopravvive

5. **Velocita' di annegamento.** La risacca distrugge. Se il mare attraversa
   quella quota in fretta, il sito si conserva. Il meltwater pulse 1A
   (~14.6-14.2 ka, ~16 m) rende una fascia di profondita' privilegiata.
   → `rapid_drowning_ratio()`
6. **Tempo nella risacca.** Poco e' meglio. → `surf_exposure_kyr()`
7. **Seppellimento rapido con sedimento fine, anossia.** Conserva gli organici.
   → serve una griglia di spessore sedimentario. **Non implementato.**
8. **Assenza di scavo da correnti di marea.** → **Non implementato.**

## 3. Criteri di SCOPRIBILITA' — cosa si puo' vedere da casa

9. **Paleosuperficie vicina al fondale attuale.** Sotto 60 m di fango non si
   trova niente, per quanto sia ben conservato.
10. **Copertura dati.** GMRT da' una bbox in GeoTIFF senza chiave (verificato).

## 4. L'algoritmo

```
punteggio_grezzo = residenza_costiera x rapidita_annegamento x penalita_pendenza
```

E poi la parte che conta davvero:

1. **Il punteggio grezzo non significa niente da solo.** Va letto come
   percentile contro un null di punti casuali della stessa piattaforma.
   Un massimo interno esiste sempre — otto tentativi in `CALIBRAZIONE.md`
   l'hanno imparato a caro prezzo.
2. **Il null va condizionato sulla profondita'** (vedi §5).
3. **Controllo positivo** su siti gia' pubblicati. Se il metodo non li ritrova,
   non trovera' niente di nuovo. Vietato tararlo su di loro.
4. **Cieco:** chi cerca non e' chi valuta.
5. **Output**: "qui vale la pena un sonar, per questo motivo, e questo lo
   smentirebbe". Mai "trovato".

## 5. Il problema del controllo positivo — distorsione da profondita'

I siti sommersi noti stanno tutti in acqua bassa:

| sito | profondita' | eta' |
|---|---|---|
| Atlit-Yam | -10 m | 9.000 anni |
| Bouldnor Cliff | -11 m | 8.000 anni |
| Pavlopetri | -3.5 m | 3.500 anni |

Si trovano dove i sub arrivano, **non dove la conservazione e' migliore**. Il
catalogo misura lo sforzo di ricerca quanto la realta'.

Conseguenza operativa, non aggirabile: il null va **condizionato sulla
profondita'**. Si chiede "dato che sta a -10 m, questo punto e' speciale?", non
"e' speciale in assoluto" — che risponderebbe soltanto "sta dove si guarda".

Questo separa il modello in due parti con status diverso:

- **Parte verticale** (fascia di profondita' -> velocita' di annegamento):
  **non validabile** sul catalogo distorto.
- **Parte laterale** (a parita' di profondita': acqua dolce, riparo, pendenza,
  sedimento): **validabile**. Ed e' proprio quella non ancora implementata.

## 6. Previsioni falsificabili che il modello gia' produce

Con la sola parte verticale, su pendenza tipica di piattaforma:

| quota | annegata | punteggio grezzo |
|---|---|---|
| -88 m | 14.4 ka | **31.3** (impulso 1A) |
| -20 m | 8.0 ka | **21.8** |
| -120 m | 18.0 ka | 8.4 |
| -60 m | 11.5 ka | 7.6 |
| -5 m | 6.2 ka | 3.2 |

**Previsione:** a parita' di sforzo di ricerca, le fasce ~-85/-90 m e ~-20 m
devono mostrare densita' di siti superiore alle quote adiacenti.

**Come si uccide:** si prende il catalogo dei siti sommersi noti, si corregge
per sforzo (ore di immersione, coperture sonar per fascia di profondita'), e si
guarda l'istogramma. Se le due fasce non emergono, il modello e' sbagliato.
Nessuno ha ancora fatto questo controllo qui.

## 7. Il limite duro, da ripetere in ogni output

La batimetria libera globale ha risoluzione di **centinaia di metri**. Un
villaggio neolitico e' largo **cento**. Da casa **non si trovano siti**: si
trovano **paesaggi** — paleovalli, paleolinee di costa, lagune sepolte.

Questa e' la differenza fra un lavoro onesto e il marketing.

## 8. Dove guarderei, e perche'

Criteri oggettivi, non somiglianza col mito: superficie emersa all'ultimo
massimo glaciale, paleofiumi, allagamento rapido, latitudine abitabile.

1. **Golfo Persico** — era un bacino asciutto con Tigri ed Eufrate dentro,
   allagato nell'Olocene antico, adiacente a dove poco dopo compaiono le prime
   societa' complesse.
2. **Piattaforma di Sunda** — la piu' vasta terra emersa persa al mondo,
   tropicale, abitata.
3. **Mare del Nord (Doggerland)** — gia' dimostrato: serve da controllo.
4. **Piattaforma della Florida** — karst e risorgive, conservazione eccellente.
5. **Coste in subsidenza (Egeo, delta del Nilo, Campania)** — l'unica finestra
   per qualcosa di monumentale.

## 9. Stato

Implementato e testato (17 test, nessuno tocca la rete): curva del livello del
mare, eta' di annegamento, residenza costiera, esposizione alla risacca,
rapidita' di annegamento, punteggio grezzo, percentile contro null, accesso
GMRT.

Non implementato: reticolo di drenaggio annegato, riparo/fetch, spessore
sedimentario, rilevazione della subsidenza. **Sono i criteri laterali, cioe' gli
unici validabili sul catalogo.** Il controllo positivo e' progettato ma non
eseguito, e senza quelli non e' eseguibile in modo significativo.
