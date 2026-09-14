# Gemini Deep Research — round 1, valutato

**14 settembre 2026.** Report integrale in `gemini-round-1-integrale.txt` (4.206 parole). Qui cosa ho verificato e cosa ne resta.

Il prompt chiedeva falsificatori. È tornato un documento che conferma quasi tutto e aggiunge una correzione che mi aiuta. **Questo è di per sé un motivo di sospetto**, non di soddisfazione: ho verificato le tre affermazioni verificabili da qui prima di accettarne una.

---

## Verifica 1 — Bama Ridge a 329 ± 2 m: **CONTRADDETTA dal mio DEM**

Gemini (via Armitage et al. 2015, PNAS) dà la Bama Ridge a **329 ± 2 m**. Il repo usa `MEGA_CHAD_HIGHSTAND_M = 320.0`.

Tre transetti N-S indipendenti sul tile 11N/13E, Copernicus GLO-30 a piena risoluzione:

| transetto | gradino a | da → a | cresta locale |
|---|---|---|---|
| 13,35°E | 11,705°N | 322 → 331 m | 330,9 m |
| 13,50°E | 11,614°N | 319 → 326 m | 332,4 m |
| 13,65°E | 11,546°N | 319 → 326 m | 332,2 m |

Il gradino **migra verso sud all'aumentare della longitudine**: cordone arcuato coerente, non rumore.

Poi ho lasciato decidere al rilevatore del repo (Bama contro tile di controllo):

| livello | Bama | controllo |
|---|---|---|
| **320 m** | **+4,42 ✓** | −0,71 |
| 322 m | +3,80 ✓ | −1,05 |
| 329 m | −0,80 | −0,78 |

**320 m resta.** La costante non si tocca. Probabile riconciliazione: 329 m è la **cresta** del cordone (costruita dalle onde, sopra il piano d'acqua), 320 m è il **piede**, che è dove la sponda si traccia. Due numeri per due cose diverse.

Se avessi accettato la correzione perché suonava autorevole, avrei introdotto una regressione. **È il motivo per cui si verifica.**

## Verifica 2 — granulometria di GeoB7920-2: **Gemini ha ragione sul fatto, torto sull'accesso**

Avevo dichiarato la granulometria di GeoB7920-2 *"fuori portata da casa, richiede misure nuove su materiale in archivio a Brema"*. **Era sbagliato**: Tjallingii et al. (2008, EPSL) l'ha misurata e pubblicata — N=315, modello a 3 end-member (EM1 57,8 µm eolico grossolano; EM2 34,6 µm eolico fine; EM3 4,9 µm emipelagico), 88% di varianza spiegata. La misura **esiste**.

Ma l'affermazione *"dati granulometrici primari su PANGAEA, download senza registrazione: SÌ"* **non regge alla verifica**:

- `PANGAEA.705111` scarica (313 righe) ma contiene `Depth sed`, `Age`, **`Humidity index`** — **nessuna colonna granulometrica**;
- `PANGAEA.811709` e `761033` sono **collezioni**; la ricerca PANGAEA per "GeoB7920-2 grain size" dà **un solo risultato**, la collezione stessa, e i metadati non nominano granulometria né end-member.

**Ma c'è un guadagno vero, ed è immediato.** L'*humidity index* di Tjallingii **è** la quantità derivata dalla granulometria — il rapporto fra componente emipelagica ed eolica. 313 punti, pubblici, scaricati stasera. Non è la distribuzione grezza, ma è il segnale che volevo.

## Verifica 3 — citazione Bard et al. 2010: **incoerente**

Gemini scrive *"Bard et al. (2010), Geology, DOI: 10.1130/G30867.1"* per il tasso YD di 5,6 ± 0,4 mm/anno. Ma la sua stessa bibliografia (voce 5) rimanda a `Bard10Science_SI.pdf`, cioè **Science**, non Geology, e `10.1130/...` è un prefisso Geology. **Rivista e DOI non possono essere entrambi giusti.** Non ho verificato quale sia corretto: la usi solo dopo averlo fatto.

---

## Cosa accetto, e cosa cambia

### MWP1B ridimensionato — rafforza la mia conclusione

Il gradino di ~15 m a Barbados (Abdul et al. 2016) sarebbe un **artefatto da clasti di *Acropora palmata* ex-situ franati a valle** e rideposti sopra superfici più antiche. Le revisioni (Tahiti IODP 310, Grande Barriera IODP 325 — Webster et al. 2025) danno **7,7–10,2 m a 23–30 mm/anno**, non 15 m a >40.

Se regge, l'obiezione che avevo scritto contro me stesso in `YOUNGER-DRYAS.md` si indebolisce ancora: non c'è nessun impulso catastrofico a 11,3 ka da spiegare. **L'anello 2 resta `−`, e più solido di prima.**

### Il tasso YD: accordo indipendente

Gemini/letteratura: **5,6 ± 0,4 mm/anno**. La mia curva schematica: **6,2 mm/anno**. Concordano entro l'incertezza. La curva semplificata di `shelf.py` regge.

### Il colpo che fa male: Pista C potrebbe non essere testabile

Il "catalogo dei negativi" della domanda 2 è la cosa più preziosa del report, e va contro di me:

> Nei bacini lacustri confinati perialpini, i depositi di run-up sopra la linea di riva **non sono stati trovati o sono privi di continuità stratigrafica**. Il riflusso d'onda e l'erosione meteorica rimuovono la sabbia oltre riva **entro pochi decenni**, preservando solo la torbidite sul fondo.

E nel "non è stato possibile stabilire": **nessun deposito da run-up in un bacino lacustre chiuso ed endoreico, 15–5 ka, preservato in ambiente subaereo.** Zero casi al mondo.

`PISTA-C-confinamento.md` dice che il deposito di run-up sopra il piano d'acqua è **l'unico test falsificabile** del meccanismo. Se in un bacino chiuso quel deposito non si conserva, **il mio unico kill-shot non è eseguibile lì**. Non è che la pista è morta: è che il test che le avevo assegnato non vale nel contesto che mi serve. Va sostituito con la **torbidite sul fondo**, che si conserva — e che è stratigrafia da carota, non geometria da DEM.

### Materiale utile accettato con riserva (da verificare uno per uno)

- **Quattro bacini confinati abitati**: Mar Morto (31,5N 35,5E), Bonneville (40,5N 112,5W), Turkana (3,5N 36,0E), Storfjorden/Tafjorden (62,3N 7,0E). Sono candidati plausibili — rift e fiordi, cioè dove le pareti ripide stanno davvero.
- **Undici paleosponde datate** con quota, incertezza, metodo e coordinate: Bama, Goz Kerki, Bodélé, Bonneville, Provo, Sunstone Knoll, Sehoo/Lahontan, Lake Surprise, Turkana MHS e SHS, Lisan. **È il banco di taratura che avevo chiesto**, e supera le dieci.
- Avvertenza loro, seria: nel Great Basin il rimbalzo isostatico deforma la stessa linea di riva **fino a 71 m** fra centro e margine del bacino. Un banco di taratura che ignori la GIA misura la deformazione, non l'errore del rilevatore.

## Bilancio

| affermazione | esito |
|---|---|
| Bama a 329 m | **contraddetta** dalla mia misura; 320 m resta |
| Granulometria GeoB7920-2 esiste | **accettata** — mia dichiarazione di impossibilità era sbagliata |
| ...ed è su PANGAEA senza registrazione | **non verificata**: è l'indice di umidità, non la granulometria |
| Citazione Bard 2010 | **incoerente** (rivista vs DOI) |
| MWP1B ridimensionato a 7,7–10,2 m | accettata con riserva, **rafforza** l'anello 2 |
| Tasso YD 5,6 ± 0,4 mm/anno | **accordo** con la mia curva (6,2) |
| Run-up non conservato in bacini chiusi | **accettata, e mi danneggia** — il kill-shot di Pista C va sostituito |
| 11 paleosponde datate | accettate come lista da verificare; è il banco che serviva |

Due su otto verificate contro il dato: una contraddetta, una parziale. **Il tasso di errore non è trascurabile, e il documento va usato come indice bibliografico da controllare, mai come fonte.**
