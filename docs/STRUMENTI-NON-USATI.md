# Strumenti valutati e scartati, con il motivo

Elenco di cio' che sembra ovvio provare e non lo e'. Serve a non rifarlo.

## LiDAR — strumento sbagliato, e per il Sahara non esiste

Il LiDAR archeologico (Maya, Angkor, Caracol) funziona perche' **penetra la
chioma della foresta**: e' tutto li' il suo vantaggio. Nel Sahara **non c'e'
chioma** — il suolo e' gia' nudo e il DEM lo vede direttamente.

Copertura LiDAR aerea del Sahara: praticamente nulla. Si vola per progetti
specifici, quasi sempre in paesi ricchi e su siti boscosi.

Da satellite esiste **ICESat-2**, lidar a conteggio di fotoni, aperto. Ma e' uno
strumento **a profilo**: da' tracce lineari distanti chilometri, non un raster.
Precisione verticale ottima (~10 cm), utile per validare quote — inutilizzabile
per cercare strutture.

**Conclusione: non e' una lacuna del progetto, e' una proprieta' del terreno.**

## ALOS PALSAR banda L — provato, esito negativo

Debito saldato: l'accesso era stato verificato il primo giorno e mai usato.

Finestra 1°x1° sul corridoio Tamanrasset (lon -17.5..-16.5, lat 20.5..21.5),
mosaico 2010, HH. Vedi `palsar-tamanrasset.png`.

**Cosa si vede:** il contatto netto fra sabbia (scura, liscia, gamma0 mediano
-19.4 dB) e roccia o ghiaia (chiara, ruvida). Il regime speculare della sabbia
asciutta c'e', ed e' quello in cui i canali sepolti dovrebbero staccarsi.

**Cosa NON si vede: nessun paleocanale sepolto.**

**E l'osservazione che vale piu' del risultato:** le linee piu' nette
dell'immagine sono le **cuciture del mosaico** — bordi rettilinei di scena, non
geologia. Un rilevatore automatico di lineamenti ci si sarebbe buttato sopra.
E' il nono modo diverso in cui questo progetto ha rischiato un falso positivo.

Limite del metodo, non solo del sito: le scoperte classiche di paleocanali al
radar (Bir Safsaf, Ghoneim & El-Baz) sono nel Sahara **orientale**, dove la
coltre sabbiosa e' sottile. Gli erg mauritani sono molto piu' spessi,
verosimilmente oltre la penetrazione della banda L (1-2 m).

## Metalli meteorici (iridio, platino) — evento sbagliato

Vedi `PISTA-A-carbone.md` e il registro. In sintesi: il caso del Dryas recente
e' di **platino**, non di iridio, con rapporto Pt/Ir **non condritico** — un
problema di specificita', non un dettaglio. E soprattutto il Dryas e'
12.9-11.7 ka, mentre l'anomalia nostra sta a 5.5-8.8 ka: **evento sbagliato di
oltre quattromila anni**. Nessun dato Pt/Ir esiste per questo margine.

## Isotopi del ferro — tracciante sbagliato

Per la domanda "da dove viene questa polvere" i traccianti consolidati sono
**Nd, Sr, Pb**, non il Fe. La libreria delle sorgenti dei suoli nordafricani
(Guinoiseau et al. 2022) esiste ed e' aperta. **Ancora da usare.**

## 230Th — ridondante

Un rapporto fra due componenti dello stesso campione e' gia' immune a
sedimentazione, focalizzazione, diluizione e densita'. Il Th agirebbe su effetti
che nel rapporto si cancellano da soli.

## Cosa del catastrofismo e' DENTRO questo progetto

Va detto, perche' e' piu' di quanto sembri:

- **Impulso di scioglimento 1A** — 14-18 m in <=340 anni: e' nel modulo
  `shelf.py`, e produce la previsione delle due fasce di profondita' privilegiate
- **Movimenti di massa come killer** — l'intera Pista B e' stata riscritta
  partendo da Vajont e dal Nepal 2026: un bacino che si riempie NON uccide
- **Piene da rilascio a valle** — meccanismo 3 in `basin.py`, con lo sfioratore
- **Arretramento orizzontale spettacolare** — 175 m di costa persi ogni anno su
  piattaforma piatta: il criterio della memoria

Cio' che resta fuori, e perche': l'**ipotesi di impatto del Dryas** (contestata,
e comunque evento sbagliato per la nostra finestra), e tutto cio' che non ha una
firma fisica misurabile — geometria sacra, civilta' avanzata perduta, precessione
come prova. Non per pregiudizio: perche' non superano le cinque colonne di
`BERSAGLIO.md`.
