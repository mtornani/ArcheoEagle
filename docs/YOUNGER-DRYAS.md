# Impatto cometario sul Younger Dryas — tesi nel ledger

**13 settembre 2026.** Domanda: un impatto sulla calotta artica ~12.900 anni fa, con effetti a catena, puo' essere all'origine del concetto?

CLAUDE.md §2.3: Carlson e Hancock sono **lenti, non oracoli**; ogni loro claim entra nel ledger come tesi, con fonte, e **puo' prendere un `−`**. Questa e' la tesi piu' grossa del lotto e la tratto come tale: non la liquido e non la sposo.

**Avvertenza di metodo, subito.** Non e' un test cieco. La curva del livello del mare era gia' in `shelf.py` dal 9 settembre e la conoscevo. Quindi non registro una previsione: registro un **confronto fra un'affermazione e un dato che il repo aveva gia'**. Dichiarato perche' l'ultima volta che ho scelto una finestra dopo aver visto i numeri (carbone, 5,5–8,8 ka) e' venuta fuori una quasi-tautologia.

---

## La catena, spezzata in anelli testabili

L'ipotesi popolare e' un treno: `impatto -> collasso della calotta -> impulso d'acqua -> coste sommerse -> memoria del diluvio`. Un treno si rompe dove si rompe il primo vagone. Testo gli anelli separatamente.

### Anello 1 — c'e' stato un impatto? Contestato, non chiuso

**A favore, e va detto perche' e' la parte seria:** l'anomalia di **platino** nella carota GISP2 in Groenlandia, a ~12.890 anni (Petaev et al., *PNAS*, 2013), ritrovata poi in una decina di siti nordamericani (Moore et al., *Scientific Reports*, 2017). E' una misura vera, replicata, in un archivio che conserva bene. Non e' folklore.

**Contro:** nanodiamanti e microsferule magnetiche — gli altri marcatori portanti — **non hanno superato la replica indipendente** (Surovell et al. 2009; Daulton et al. 2010, 2017). Sulla cronologia, Meltzer et al. (*PNAS*, 2014) sostengono che solo 3 dei 29 siti rivendicati cadano davvero nella finestra. Critica d'insieme in Holliday et al. (*Earth-Science Reviews*, 2023).

**E il cratere artico, che e' la tua domanda precisa:** il cratere **Hiawatha**, 31 km, sotto il ghiaccio groenlandese (Kjær et al., *Science Advances*, 2018), fu subito il candidato. **Ridatato nel 2022 a ~58 milioni di anni** (Kenny et al., *Science Advances*, Ar-Ar e U-Pb su zircone). E' del Paleocene. **Non c'entra niente col Younger Dryas, ed e' l'unico cratere artico grande che avevamo.**

Non esiste un cratere di eta' YD. I proponenti rispondono: *airburst*, esplosione in atmosfera, che per costruzione non lascia cratere. Puo' essere vero — ma sposta l'ipotesi in un posto dove l'assenza di cratere smette di poterla contraddire. E un'ipotesi che si riformula ogni volta che una previsione fallisce (cratere -> airburst -> airburst multipli) perde il diritto di chiamare "conferma" ogni marcatore che trova.

**Verdetto anello 1: aperto.** L'anomalia di platino prende un `+` come fatto misurato. L'impatto come causa del Younger Dryas resta contestato. Non e' compito nostro chiuderlo.

### Anello 2 — c'e' stato l'impulso d'acqua? NO, e questo lo possiamo misurare

Qui la catena si rompe, e si rompe con numeri che avevamo gia' in casa.

| | livello | durata | tasso |
|---|---|---|---|
| **MWP1A** (14,65–14,31 ka) | +16 m | 340 anni | **47 mm/anno** |
| **Younger Dryas intero** (12,9–11,7 ka) | +7,5 m | 1200 anni | **6,2 mm/anno** |

Tre cose, tutte contro la catena:

1. **Il Younger Dryas non e' un diluvio: e' la pausa.** 7,5 metri in dodici secoli. Il segmento che contiene l'inizio del YD e' il **piu' lento di tutta la deglaciazione** fra 18 e 7 ka. Ed e' fisicamente ovvio, una volta detto: il YD e' un **raffreddamento**. Il ghiaccio riavanza. Il mare rallenta.
2. **Il vero impulso e' 7,5 volte piu' rapido e sta altrove.** MWP1A e' l'evento d'acqua piu' violento del periodo — 16 m in tre secoli — e nessuno gli associa un impatto.
3. **L'ordine temporale, da solo, basta.** MWP1A comincia **1750 anni prima** dell'inizio del Younger Dryas. Non puo' esserne la conseguenza. Un effetto non precede la causa di diciassette secoli.

Bloccato in 4 test (`test_shelf.py::YoungerDryasTest`) perche' la conclusione non si possa spostare cambiando la curva in silenzio.

**Verdetto anello 2: `−`.** Il collasso-diluvio al Younger Dryas non c'e' nel livello del mare.

### Anello 3 — localizza qualcosa? NO, ed e' il problema peggiore

Anche **concedendo l'impatto per intero**, non ci serve a trovare niente. Un evento emisferico non ha indirizzo. E' la diluizione di Pista C portata al massimo: se la causa e' globale, ogni costa del pianeta e' candidata, cioe' nessuna.

Il platino nella carota groenlandese e' un cronometro, non una bussola: dice *quando*, non *dove*. E il *quando* lo sapevamo gia'.

---

## Rubrica dei proxy (BERSAGLIO.md, modello iridio K-Pg)

| criterio | esito |
|---|---|
| necessita' | **no** — il raffreddamento YD si spiega con acqua di fusione e AMOC, senza impatto |
| specificita' | **debole** — il platino non e' esclusivamente da impatto |
| conservazione | **si'** — le carote di ghiaccio conservano benissimo |
| riproducibilita' | **mista** — platino si', nanodiamanti e sferule no |
| previsione quantitativa | **la piu' debole** — l'ipotesi si e' riformulata a ogni previsione fallita |

L'iridio al K-Pg passa tutte e cinque. Per questo e' il modello, e per questo il confronto e' impietoso.

## Verdetto per il ledger

| anello | esito |
|---|---|
| impatto ~12,9 ka | **aperto** — platino `+`, resto contestato. Non nostro da chiudere |
| collasso -> impulso d'acqua | **`−`** — misurato, il YD e' la pausa piu' lenta della deglaciazione |
| localizza un referente | **N/A** — un evento emisferico non ha indirizzo |

**Kill-shot che chiuderebbe l'anello 2 in nostro favore:** un dato di livello del mare, da coralli o da coste, che mostri un salto metrico rapido dentro 12,9–12,5 ka. Se qualcuno lo produce, questo `−` cade. **Finche' non esiste, l'anello resta rotto e la catena non regge.**

## Cosa NON fare

Non riformulare. Se il diluvio non e' al Younger Dryas, la risposta non e' spostare la finestra finche' un diluvio ci cade dentro — sarebbe esattamente l'errore che ho gia' commesso col carbone, e che la sezione **Avvertenza di metodo** qui sopra dichiara.
