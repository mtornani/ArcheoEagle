# Carote: librerie pubbliche, e il primo riscontro indipendente della tesi Sahara

## Le librerie, verificate una per una

| risorsa | stato | accesso |
|---|---|---|
| **PANGAEA** | **funziona** | API di ricerca aperta + pacchetto `pangaeapy`. ~400.000 dataset georeferiti, nato proprio da un archivio di carote |
| **SESAR / geosamples.org** | attivo (200) | ha ripreso in carico l'indice campioni |
| **IMLGS (NOAA)** | **DISMESSO dal 5 maggio 2025** | non usarlo. Copriva 228.785 carote; l'eredita' e' passata a SESAR |
| GMRT | funziona | batimetria per bbox, GeoTIFF, senza chiave |

Verificato il 10 set 2026 da questa sessione, non letto da una pagina.

```python
from pangaeapy import PanDataSet
ds = PanDataSet("10.1594/PANGAEA.738191")   # turbiditi, Canyon di Capo Timiris
ds.data      # dataframe
ds.params    # metadati dei parametri: leggere SEMPRE l'unita'
```

Nota metodologica pagata subito: in quel dataset la colonna si chiama
`Duration`, ma i metadati dichiarano **unita' `ka`** e i valori crescono con la
profondita' nel sedimento. E' un'**eta'**, non una durata. Non indovinare mai il
significato di una colonna dal nome.

## La domanda che si voleva chiudere

*Esiste una frana sul margine NW africano datata nella finestra del periodo
umido africano (14.5-5.5 ka), vicino alla paleofoce del Tamanrasset?*

**Si': il Mauritania Slide Complex e' datato 10.5-10.9 cal ka BP.** Stile di
rottura retrogressivo — lo stesso stile per cui il Sahara Slide e' ritenuto
**non** tsunamigenico. Quindi la data e' perfetta, il meccanismo probabilmente no.

## Il risultato che non cercavamo, e che vale di piu'

Il Canyon di Capo Timiris **e' la paleofoce del Tamanrasset**, il corridoio
principale di questo progetto. Wien et al. 2006 hanno pubblicato 41 turbiditi
datate in quattro carote GeoB, aperte e scaricabili:

| periodo | durata | eventi | frequenza |
|---|---|---|---|
| periodo umido africano, 14.5-5.5 ka | 9.000 anni | **16** | 1 ogni 562 anni |
| dopo il disseccamento, 5.5-0 ka | 5.500 anni | **3** | 1 ogni 1.833 anni |

**Rapporto 3.3x.** La frequenza dei flussi torbiditici nel canyon crolla quando
il Sahara si secca.

**Questo e' il primo riscontro indipendente e quantitativo della premessa del
progetto.** Fino a ieri il Tamanrasset era un LineString copiato da un paper —
grado `schematic`, e la spec lo dice a chiare lettere. Adesso c'e' una misura
fatta da altri, con datazioni, che dice che quel fiume portava davvero sedimento
all'oceano proprio nella finestra giusta, e che ha smesso quando doveva.

## Cosa NON dimostra

Le turbiditi in un canyon alimentato da un fiume sono in larga parte **di
apporto fluviale**, non da frana. Un'alta frequenza durante il periodo umido
significa **che il fiume scorreva** — che e' esattamente cio' che ci si aspetta,
e **non** e' prova di catastrofe.

Due eventi cadono vicino all'eta' del Mauritania Slide Complex:

| carota | evento | eta' | posizione | profondita' |
|---|---|---|---|---|
| GeoB8502-2 | T 1 | 10.1 ka | 19.220 N, 18.934 W | -2956 m |
| GeoB8509-2 | T 7 | 10.4 ka | 19.451 N, 18.089 W | -2585 m |

E' **suggestivo, non probante**: a quelle eta' un torbidite puo' essere
benissimo fluviale. Separare le due origini richiede la granulometria e la
composizione strato per strato, che sta nelle altre tabelle dello stesso lavoro.

## Cosa cambia per il progetto

1. Il corridoio Tamanrasset guadagna un riscontro esterno. Non promuove il
   geojson da `schematic` a `survey` — il tracciato resta disegnato — ma la
   **premessa** che quel sistema fluviale fosse attivo nella finestra giusta ora
   ha una misura dietro, fatta da terzi.
2. Esiste una via dati per le prove che contano davvero. Il meccanismo 2
   (massa che sposta l'acqua) lascia firma **stratigrafica**, non geometrica:
   nessun DEM lo vedra' mai, ma PANGAEA si'.
3. La prossima domanda e' netta e chiudibile: **fra le 16 turbiditi del periodo
   umido, ce n'e' una con firma da frana invece che da fiume?** Si risponde con
   le tabelle di granulometria dello stesso dataset. Non e' stata ancora fatta.

Fonti: Wien, Holz, Kölling, Schulz (2006), doi:10.1594/PANGAEA.738191 —
Georgiopoulou et al. 2010, Sahara Slide — Mauritania Slide Complex,
10.5-10.9 cal ka BP — Skonieczny et al. 2015, paleofiume Tamanrasset.

---

# Proxy: il principio, e la trappola

Non si cerca il meteorite: si cerca l'iridio. Alvarez trovo' l'anomalia di
iridio nel **1980**; il cratere di Chicxulub fu identificato nel **1990-91**.
Il proxy non ha seguito la scoperta: **l'ha predetta**.

E' il criterio che separa l'unico risultato di questo progetto dagli otto
fallimenti. Tutto cio' che ha fallito era **rilevazione diretta** (trova la
sponda nel DEM). Tutto cio' che ha funzionato era **proxy**: le turbiditi a
60 km al largo e 3 km di profondita' ci hanno detto che il Tamanrasset
scorreva, senza mai vedere il fiume.

## Cosa rende valido un proxy (e perche' l'iridio lo era)

1. **Necessita'** — il meccanismo *deve* produrre la traccia, non "puo'". Un
   impattore condritico deposita iridio per forza.
2. **Specificita'** — poche altre cause la producono a quella scala. L'iridio
   e' raro nella crosta, abbondante nelle condriti. L'obiezione del vulcanismo
   del Deccan era seria e **andava risposta**, non ignorata.
3. **Conservazione** — la traccia sopravvive in un contesto databile.
4. **Riproducibilita'** — Gubbio, poi Stevns Klint, poi decine di sezioni.
5. **Predizione quantitativa** — la quantita' di iridio dava la dimensione
   dell'impattore, che dava la dimensione del cratere, che poi fu trovato.

Il quinto e' il discriminante: **un buon proxy predice qualcosa che non hai
ancora guardato.** Senza quello, non e' scienza da proxy, e' racconto a
posteriori.

## La misura fatta, e perche' NON dimostra niente

Carbone in GeoB7920-2 (20.75 N, 18.58 W, -2278 m; Dupont & Schefuss 2017),
26 campioni datati, concentrazione col metodo del marcatore esotico:

| periodo | n | mediana |
|---|---|---|
| periodo umido 14.5-5.5 ka | 15 | **5.295** |
| dopo il disseccamento <5.5 ka | 11 | **2.406** |

**2.2x**, con picco a 6.0-6.5 ka e crollo netto alla terminazione. Concorda
con le turbiditi (3.3x): due proxy indipendenti, processi diversi, stessa
transizione alla stessa data.

**E non e' prova di presenza umana.** Il carbone in queste carote arriva dal
continente **per via eolica**: piu' vegetazione (Sahara verde) = piu' biomassa
da bruciare = piu' carbone. Il clima da solo spiega tutto il segnale.

Fallisce il criterio 2, **specificita'**. E' esattamente l'obiezione del Deccan,
in versione sahariana. Un proxy che conferma la tua storia non vale niente
finche' non escludi che la spieghi anche l'alternativa noiosa.

## Il test che lo renderebbe specifico

**Disaccoppiamento.** Il fuoco normalizzato alla biomassa: se il carbone per
unita' di vegetazione **sale** quando la vegetazione scende, non e' il clima.
Il normalizzatore c'e' gia': il polline nelle carote gemelle dello stesso
lavoro (GeoB7929-2 ha carbonati, lipidi, polline, spore e carbone insieme).

Non e' stato fatto. E' la prossima domanda chiudibile con dati gia' pubblici.

## Il riorientamento che il principio impone

I proxy della presenza umana **non stanno nel sito**. Si accumulano nel
**deposito** dove il sedimento converge — canyon, conoide, bacino. Un canyon
sottomarino e' un **integratore naturale**: raccoglie il segnale di tutto il
bacino idrografico a monte.

Quindi non serve trovare l'insediamento. Serve **leggere il registratore**. E
il registratore e' gia' carotato, gia' datato, gia' pubblico.

E' lo stesso motivo per cui l'integrale batteva le statistiche locali: non
perche' l'integrale sia furbo, ma perche' concentra un segnale che localmente
e' sotto il rumore.

## Il test di disaccoppiamento: eseguito

Stessa carota GeoB7920-2, carbone (877696) diviso polline totale (877704),
entrambi calibrati col metodo del marcatore esotico. **Previsione registrata
prima di guardare:** se il carbone e' solo clima, carbone e polline vanno
insieme e il rapporto resta piatto.

| periodo | n | carbone | polline | **carbone/polline** |
|---|---|---|---|---|
| periodo umido 14.5-5.5 ka | 15 | 5.295 | 510 | **9.80** |
| dopo il disseccamento | 11 | 2.406 | 591 | **3.26** |

**Il disaccoppiamento c'e', ed e' netto: 3x.** Il carbone e' massimo (10.188 a
6.3 ka) proprio quando il polline e' minimo. E il polline e' 4 volte piu'
abbondante a 10.5-11 ka — la fase piu' umida — che nella fase 8-6 ka.

**E quasi certamente non e' presenza umana.** Il picco del rapporto cade a
6-8 ka, cioe' nella fase **terminale e in via di disseccamento** del periodo
umido. Ed e' esattamente cio' che l'ecologia del fuoco prevede: **il fuoco e'
massimo a umidita' intermedia** — abbastanza biomassa da bruciare, abbastanza
secca da prendere fuoco. Un paesaggio che si sta seccando ma e' ancora vegetato
brucia piu' sia di uno umido sia di un deserto.

Altre alternative da escludere prima di qualunque affermazione:
- **trasporto, non produzione.** A 200+ km dalla costa carbone e polline
  arrivano col vento, e hanno proprieta' aerodinamiche diverse. Un cambio di
  circolazione (monsone contro alisei) cambia il rapporto senza che cambino ne'
  il fuoco ne' le persone. E' l'obiezione piu' seria.
- **spostamento dell'area sorgente.** Durante il periodo umido la fascia
  vegetata si sposta a nord: il polline a 20.75 N nel 10 ka viene da un'altra
  regione che nel 5 ka.
- diluizione e conservazione differenziale.

## La predizione quantitativa che chiude o apre il caso

Se il picco del rapporto e' l'effetto di umidita' intermedia, allora **il
rapporto deve essere prevedibile dalla curva di umidita'**. Il proxy idrologico
sta nella stessa collezione: i **lipidi** (doi:10.1594/PANGAEA.877702), dove il
deuterio delle cere fogliari e' una misura diretta di umidita'.

- rapporto che segue l'umidita' -> clima, caso chiuso, e lo si dice.
- rapporto che se ne discosta -> resta qualcosa da spiegare.

Non e' stato fatto. E' il criterio 5 (predizione quantitativa) applicato per
davvero, ed e' l'unica cosa che distingue questo da un racconto a posteriori.

---

# Proxy culturali: esistono, e sono rigorosi

L'esempio dell'ambra baltica non e' inventato: e' metodo reale. L'ambra baltica
si riconosce chimicamente (succinite, spettroscopia infrarossa) e la sua
comparsa e scomparsa nei corredi mediterranei traccia una rete di scambio.

Famiglie mature, tutte basate sulla **provenienza**:

| proxy | cosa traccia | come |
|---|---|---|
| **ossidiana** | la rete di scambio, sorgente per sorgente | ogni vulcano ha un'impronta di elementi in traccia (XRF, attivazione neutronica) |
| **isotopi del piombo** | rame, argento, lingotti | firma della miniera |
| **stagno** | il problema classico dell'eta' del bronzo | isotopi su lingotti da relitti |
| **petrografia ceramica** | zone di produzione | impasti e inclusi |
| **stronzio/ossigeno nei denti** | mobilita' del singolo individuo | dove e' cresciuto contro dove e' sepolto |
| **DNA antico** | movimento e sostituzione di popolazioni | |
| **date al radiocarbonio sommate** | **demografia** | densita' di date come proxy di popolazione |

## La trappola, che e' la stessa di sempre

"L'ambra smette di arrivare, quindi la popolazione che la esportava e'
sparita" fallisce la **specificita'**. Alternative, tutte da escludere:

- sono crollati gli **intermediari**, non la sorgente
- e' cambiata la **rotta**
- e' crollata la **domanda**, non l'offerta
- e' comparso un **sostituto**
- e' cambiato l'**uso rituale**: l'ambra non smette di arrivare, smette di
  essere sepolta
- **bias di scavo**: abbiamo scavato meno siti di quel periodo
- la "lacuna" e' un artefatto della **risoluzione cronologica**

Il discriminante e' spaziale e testabile: **un crollo della sorgente uccide la
rete tutta insieme; un'interruzione di rotta la spegne progressivamente
dall'estremita' piu' lontana verso l'interno.** Gradiente contro simultaneita'.
E' il criterio 5 applicato alle reti di scambio.

## Quello utilizzabile qui e ora

**Le date al radiocarbonio come proxy demografico** ("dates as data"): la somma
delle probabilita' delle date archeologiche di una regione approssima
l'andamento della popolazione. Per il Sahara del periodo umido esiste materiale
vero — Gobero, Takarkori, Nabta Playa, e alcune fra le ceramiche piu' antiche
del mondo.

**E fa una previsione verificabile per il nostro problema:** se una popolazione
costiera si e' ritirata verso l'interno mentre il mare avanzava, la densita' di
date **nell'entroterra deve salire** proprio in quella finestra.

Stato delle banche dati, verificato: **XRONOS** (xronos.ch) risponde, ma
l'endpoint API non e' stato identificato in questa sessione — segnato come
raggiungibile, non come funzionante. **p3k14c** e' un dataset globale aperto
distribuito su GitHub. Da verificare entrambi prima di usarli.

## Il limite duro

I proxy culturali richiedono **cultura materiale**: siti scavati e reperti
databili. Per una piattaforma annegata e non scavata **non sono disponibili**.
Restano utilizzabili in due modi indiretti:
1. sulla terra **sopravvissuta**, per leggere cosa e' successo a quella perduta;
2. nel **deposito** dove il sedimento converge, che e' il riorientamento gia'
   registrato qui sopra.

## Il test dei lipidi: previsione falsificata, e cosa resta in piedi

**Previsione registrata:** se il rapporto carbone/polline e' l'effetto di
umidita' intermedia, deve avere un massimo a umidita' media e scendere ai due
estremi. Una gobba.

**Falsificata.** Nessuna gobba: piu' umido = piu' alto, monotono
(r = -0.54 con il deuterio delle cere fogliari).

| terzile di umidita' | rapporto mediano |
|---|---|
| piu' umido | 12.2 |
| intermedio | 9.5 |
| piu' secco | 3.6 |

**Ma il denominatore era rotto**, e lo dice una misura indipendente nella stessa
carota: il d13C passa da -22.4 a 11 ka (erba C4) a -26 dopo (legnose C3). Le
erbe producono molto piu' polline delle legnose, quindi il rapporto puo' salire
solo perche' cambia il *tipo* di vegetazione, senza che il fuoco cambi.
Spiegazione noiosa che non avevo previsto.

### Normalizzatore corretto: le cere fogliari

Carbone diviso **n-alcani C29+C31 per grammo di sedimento** — biomassa vegetale
misurata chimicamente, senza il filtro della produzione pollinica.

| periodo | n | mediana |
|---|---|---|
| 12-5.5 ka | 15 | **29** |
| < 5.5 ka | 11 | **9** |

Valori ordinati — periodo umido: 10 14 14 14 23 27 28 29 36 40 55 58 58 104 117
dopo: 2 6 9 9 9 9 10 13 16 16 19. **Mann-Whitney p < 0.001**, e la separazione
non dipende dai tre valori estremi: togliendoli resta.

### Le alternative noiose, una per una

| alternativa | esito |
|---|---|
| fuoco massimo a umidita' intermedia | **falsificata** (nessuna gobba) |
| produzione pollinica che cambia col tipo di vegetazione | **valida, ed e' perche' il polline e' stato scartato** come normalizzatore |
| diagenesi: le cere si degradano, il carbone e' inerte, quindi il rapporto cresce con l'eta' | **non regge**: i campioni piu' vecchi (10.5-11 ka) hanno rapporto 14, piu' basso di molti campioni a 6 ka. Non e' monotono con l'eta' |
| **trasporto: vento diverso porta carbone e cere in proporzione diversa** | **NON TESTATA. E' la spiegazione residua piu' probabile.** |

### Cosa sopravvive, detto con precisione

C'e' un innalzamento statisticamente robusto del carbone per unita' di biomassa
vegetale, **circoscritto alla finestra 5.5-8.8 ka** — la seconda meta' del
periodo umido — basso sia prima (10-11 ka) sia dopo. Nessuna delle tre
spiegazioni climatiche testate lo rende conto.

**E questo NON e' prova di presenza umana.** Non lo e' per due ragioni
indipendenti:

1. Il confondente del **trasporto** e' intatto. A 200+ km dalla costa, carbone
   e cere arrivano col vento e hanno aerodinamica diversa; il regime era
   monsonico durante il periodo umido e ad alisei dopo. Un cambio di
   circolazione muove il rapporto senza toccare il fuoco. **E' la spiegazione
   piu' probabile di quel che resta.**
2. Anche se il trasporto fosse escluso, "piu' fuoco per biomassa" ha altre
   cause prima dell'uomo: regime dei fulmini, struttura del combustibile,
   stagionalita' delle piogge.

### Il test che chiude o apre

Se e' trasporto, il rapporto deve seguire l'**apporto terrigeno** (forza del
vento). Il proxy sta nella stessa collezione: il **carbonato di calcio**
(doi:10.1594/PANGAEA.877688) e' un indicatore inverso di diluizione terrigena.
Piu' a fondo: i record di polvere di deMenocal su ODP 658C.

Segue la polvere -> trasporto, caso chiuso, e lo si dice.
Non la segue -> resta qualcosa da spiegare, e allora vale la pena chiamare
qualcuno che ne sa piu' di noi.

**Non e' stato fatto.** Ed e' il quarto tentativo di spiegazione noiosa: le
prime tre sono cadute, il che aumenta l'interesse ma non cambia lo stato, che
resta **non concluso**.
