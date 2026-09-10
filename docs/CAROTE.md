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
