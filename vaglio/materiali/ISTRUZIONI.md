# Vaglio — istruzioni per produrre rapporti e materiali

Per chi scrive: un assistente AI o una persona. Scritte il 16 nov 2026 da chi ha fatto la ricerca.
Chi scrive **non** fa ricerca, **non** cambia i numeri, **non** contatta nessuno: trasforma fatti già
misurati in testi che un esperto può leggere senza trovarci una parola di troppo.

Questo documento contiene, come esempi da evitare, le parole vietate: non è un materiale che esce e
non passa dal cancello. Tutto ciò che produci, sì.

---

## 1. Cosa ricevi, e cosa no

Ricevi tre cose. Non te ne servono altre.

| Cosa | Dove | A cosa serve |
|---|---|---|
| Scheda dei fatti | `vaglio/materiali/FATTI.md` | ogni affermazione e il suo grado (misurato, riferito, non noto) |
| Queste istruzioni | `vaglio/materiali/ISTRUZIONI.md` | cosa produrre e come |
| Il kit | cartella `kit/` (te la passa l'operatore, di solito come zip) | `numeri.json`, le figure, il pack cieco |

Non ricevi, e se li vedi non li apri e non li citi: `dossier.html`, `candidati.csv`,
`candidati.geojson`, le cartelle `scan/`, `chips/`, `context/`, `review/keys/`. Contengono posizioni
o le chiavi della revisione. Il modo più sicuro è che l'operatore ti dia **solo** lo zip del kit.

### Preparazione, a cura di chi ha la cartella di lavoro (non di chi scrive)

```powershell
cd D:\AI\ArcheoEagle
git pull                                  # servono i comandi nuovi: moderno, kit, controlla, verifica
cd vaglio
python -m unittest discover -s tests      # deve dire OK
python -m vaglio catalogo                 # deve dire: scansionati qui: 456
python -m vaglio moderno                  # uso del suolo di oggi; scarica una volta alcune centinaia di MB
python -m vaglio dossier                  # rigenera fascicolo e pack cieco con la nuova colonna
python -m vaglio verifica                 # deve dire: a posto
python -m vaglio kit                      # scrive vaglio_lavoro\kit\
Compress-Archive -Path vaglio_lavoro\kit -DestinationPath $HOME\Downloads\vaglio_kit.zip
```

Dopo `dossier` il pack cieco cambia (ha una colonna in più) e quindi cambia la sua firma. La firma da
citare è quella che sta in `kit/numeri.json` alla voce `pack_cieco`, non quella scritta in FATTI.md.

---

## 2. Le regole

### 2.1 Numeri

1. Ogni numero viene da `kit/numeri.json` o da `FATTI.md`. Lo copi cifra per cifra.
2. Sotto i 100 casi scrivi i conteggi, non le percentuali: «12 su 20», mai «il 60%».
3. Non fai calcoli nuovi che producano un numero nuovo: niente proiezioni, niente «quindi circa
   2.000 siti». L'unica operazione ammessa è la somma di voci dello stesso elenco.
4. Ogni numero porta accanto il suo limite, nella stessa frase o in quella dopo.
5. Con ogni materiale consegni una **tabella di riscontro**: ogni numero del testo, e la voce di
   `numeri.json` o la sezione di `FATTI.md` da cui viene.

### 2.2 Parole

Le traduzioni sono fisse: non le ritraduci a senso.

| Concetto | Italiano | English | Español | Mai |
|---|---|---|---|---|
| l'unità di conto | complesso candidato | candidate complex | complejo candidato | sito, site, sitio |
| cosa vede il rilevatore | rilievo a forma di costruzione | structure-shaped relief | relieve con forma de construcción | edificio maya, Maya building |
| esito migliore | regge alla revisione | holds up under blind review | se sostiene en la revisión a ciegas | confermato, confirmed, confirmado |
| esito intermedio | incerto | uncertain | incierto | falso, rejected, descartado |
| non ancora visto | da rivedere | not yet reviewed | sin revisar | |
| rapporto col già noto | si presume già noto | presumed already known | se presume ya conocido | nuovo, sconosciuto, unknown, unmapped, inédito |
| cosa fa Vaglio su questi dati | riproduce, ri-analizza | re-analyses, reproduces | reanaliza, reproduce | scopre, discovers, descubre |
| chi rivede | revisore (agente AI) | reviewer (AI agent) | revisor (agente de IA) | esperto, expert |

Forme, non funzioni. Nelle didascalie e nel testo descrivi quello che si vede: «tumulo», «piattaforma»,
«rilievi allungati a lati dritti», «corpi disposti attorno a uno spazio piano». Non scrivi mai
«piramide», «tempio», «palazzo», «piazza cerimoniale», «città», né l'equivalente in altre lingue:
la funzione la stabilisce un archeologo, sul posto.

Niente aggettivi da annuncio: straordinario, rivoluzionario, incredibile, senza precedenti,
breakthrough, groundbreaking, stunning, asombroso.

### 2.3 Frasi obbligatorie

Vanno riportate **così come sono**. S1, S2 e S5 in ogni materiale. S3 e S4 in ogni materiale che
parla della revisione o mostra figure.

**S1 — già analizzato da altri**

- IT: «Questo rilievo è già stato analizzato da altri gruppi (Estrada-Belli et al. 2025; Britton 2026, con un catalogo di 57.181 strutture non ancora pubblico). Ogni candidato si presume già noto finché un confronto non mostra il contrario.»
- EN: "This lidar survey has already been analysed by other teams (Estrada-Belli et al. 2025; Britton 2026, with a catalogue of 57,181 structures that is not yet public). Every candidate is presumed already known unless a comparison shows otherwise."
- ES: «Este levantamiento lidar ya ha sido analizado por otros equipos (Estrada-Belli et al. 2025; Britton 2026, con un catálogo de 57.181 estructuras aún no público). Todo candidato se presume ya conocido mientras una comparación no muestre lo contrario.»

**S2 — nessuna verifica sul campo**

- IT: «Nessun candidato è stato verificato sul campo. Non si afferma nulla sull'età, sulla cultura o sulla funzione di alcun candidato.»
- EN: "No candidate has been verified in the field. No claim is made about the age, culture or function of any candidate."
- ES: «Ningún candidato ha sido verificado en campo. No se afirma nada sobre la edad, la cultura o la función de ningún candidato.»

**S3 — quanto valgono i revisori**

- IT: «La revisione è stata fatta da agenti AI dello stesso modello. Sui riquadri di controllo hanno riconosciuto 3–4 edifici noti su 10 e non hanno indicato come struttura nessuno dei 10 riquadri vuoti. Per questo il loro giudizio vale per confermare, non per scartare.»
- EN: "The review was carried out by AI agents of the same model. On control tiles they recognised 3–4 of 10 known buildings and flagged none of the 10 empty tiles as a structure. Their judgement is therefore used to confirm, not to rule out."
- ES: «La revisión fue realizada por agentes de IA del mismo modelo. En los recuadros de control reconocieron 3–4 de 10 edificios conocidos y no señalaron como estructura ninguno de los 10 recuadros vacíos. Por eso su juicio sirve para sostener un candidato, no para excluirlo.»

Se `numeri.json` elenca revisori diversi da D, E, F, la S3 va aggiornata dall'operatore, non da te.

**S4 — posizioni**

- IT: «Le posizioni dei candidati non sono in questo documento, per non esporre i luoghi al saccheggio.»
- EN: "Candidate locations are not included in this document, to avoid exposing the places to looting."
- ES: «Las ubicaciones de los candidatos no figuran en este documento, para no exponer los lugares al saqueo.»

**S5 — chi ha fatto il lavoro**

- IT: «Analisi e testi prodotti da assistenti AI (Claude, GPT) con la supervisione di Mirko Tornani, [qualifica: la scrive l'operatore].»
- EN: "Analysis and text were produced by AI assistants (Claude, GPT) under the supervision of Mirko Tornani, [role: to be filled in by the operator]."
- ES: «El análisis y los textos fueron producidos por asistentes de IA (Claude, GPT) bajo la supervisión de Mirko Tornani, [función: la completa el operador].»

Lasci la parentesi quadra com'è: la riempie l'operatore.

### 2.4 Cosa non entra mai

- Coordinate, in qualunque forma. Sigle di candidati (`V-…`) o di transetti. Collegamenti a mappe.
- Una posizione più fine del blocco di volo. I blocchi sono sette e i loro nomi stanno in
  `numeri.json` alla voce `per_zona`: quello è il massimo dettaglio.
- Una mappa con i candidati sopra. L'unica mappa ammessa è `figure/copertura.svg`.
- Una classifica dei «migliori» o dei «più promettenti». Il punteggio decide cosa guardare prima,
  non è una probabilità, e non si mostra come tale.
- Proiezioni dal campione dei 40 agli 11.916.
- Il confronto fra i 24.265 rilievi di Vaglio e le 57.181 strutture di Britton come se fosse una
  percentuale.
- Qualunque affermazione su età, cultura, funzione, importanza.
- Confronti con altri metodi che non abbiamo misurato.
- Indirizzi email, telefoni o affiliazioni che non stanno in §4: non li inventi e non li cerchi.

### 2.5 Figure

Solo quelle di `kit/figure/`. Non le ritagli, non ci disegni frecce o cerchi, non le ricolori.

| File | Cosa mostra | Didascalia (IT; per EN ed ES traduci parola per parola) |
|---|---|---|
| `tavola_reggono.jpg` | fino a dodici candidati che reggono | «Candidati che reggono alla revisione. Ogni riquadro ha 120 m di lato e mostra il terreno nudo ricavato dal LiDAR (NASA G-LiHT 2013, riprocessato da B. J. Britton 2026). Posizioni omesse.» |
| `regge_NN.jpg` | un candidato che regge, due viste | «A sinistra il riquadro come lo vede il revisore; a destra lo stesso riquadro con il rilievo in colore (rosso sporge, blu affonda). Lato 120 m. Posizione omessa.» |
| `incerto_NN.jpg` | un candidato che i revisori hanno giudicato non costruito | «Candidato rimasto incerto: almeno due revisori lo hanno giudicato naturale, moderno o un difetto del dato. Resta incerto perché questi revisori non possono scartare.» |
| `controllo_struttura_NN.jpg`, `controllo_vuoto_NN.jpg` | riquadri di controllo a risposta nota | «Riquadro di controllo (Chactún; Kokalj et al. 2023, CC BY 4.0), mescolato ai candidati senza che il revisore lo sappia.» |
| `copertura.svg` | dove è passato il LiDAR | «Transetti scansionati. I candidati non sono riportati sulla mappa, per scelta.» |

### 2.6 Tono

Frasi brevi, una cosa per frase. Prima il fatto, poi il suo limite. Si concede ciò che è vero prima
di rispondere a un'obiezione. Nessuna urgenza, nessuna lusinga, nessun «come sapete». Chi legge è
più competente di chi scrive, e lo sa.

### 2.7 Non si spedisce niente

Produci file. Li spedisce l'operatore, uno alla volta, quando decide lui.

---

## 3. I materiali

Si producono in quest'ordine. M1 in italiano è il testo madre: gli altri ne derivano e non possono
dire niente che M1 non dica. I file vanno in `vaglio/materiali/uscite/`.

### M1 — Rapporto tecnico

`rapporto-tecnico.it.md`, poi `rapporto-tecnico.en.md`. Per chi è del mestiere e vuole capire in
dieci minuti se il lavoro è serio. Da 2.000 a 3.000 parole. Sezioni, in quest'ordine e con questi titoli:

1. **In breve** (al massimo 120 parole). Cosa è stato fatto in una frase. Tre misure: il rilevatore
   sul test, i revisori sui controlli, l'esito sui 40 rivisti. La domanda che facciamo. Poi S1.
2. **Perché** (circa 100 parole). Il caso Miotti come in FATTI §2, con rispetto.
3. **Dati.** La tabella di FATTI §3 e le due righe sui transetti.
4. **Metodo.** Cinque passi numerati, da due a quattro frasi ciascuno: visualizzazioni del terreno;
   rilevatore; complessi; revisione al buio con controlli; confronto col già noto e con l'uso del suolo.
5. **Misure.** Tre tabelle: test del rilevatore (FATTI §4, con i tre limiti scritti sotto);
   revisori sui controlli (uno per riga, da `numeri.json` → `revisori`); il campione dei 40 (FATTI §6,
   con i cinque punti «come leggere» riportati per intero). Poi S3.
6. **La scansione.** Conteggi di `numeri.json` → `scansione` ed `esiti`; tabella per blocco da
   `per_zona`; se c'è, `uso_del_suolo_oggi` con i limiti di FATTI §8.
7. **Cosa non ha funzionato.** I quattro punti di FATTI §9, tutti.
8. **Cosa non sappiamo.** I cinque punti di FATTI §10, tutti e per intero, più la frase finale. Poi S2.
9. **Cosa chiediamo.** Tre richieste, da §4 di queste istruzioni: il confronto col catalogo; un
   revisore umano su un pacco al buio; un parere sul metodo.
10. **Riproducibilità.** Comandi, identificativi dei dati, firma del pack cieco, come verificarlo.
11. **Posizioni, crediti, dichiarazione.** S4, i crediti di FATTI §12, S5.

Figure: `tavola_reggono.jpg` dopo la sezione 1; un controllo con struttura e uno vuoto nella 5; due
`incerto_` nella 5; `copertura.svg` nella 6.

### M2 — Scheda di una pagina

`scheda.en.md`, `scheda.es.md`, `scheda.it.md`. È ciò che si allega a una prima lettera. Al massimo
300 parole e una figura (`tavola_reggono.jpg`). Struttura fissa:

- Titolo neutro. Usa questo: «Vaglio: una ri-analisi con errori misurati del LiDAR pubblico G-LiHT
  sullo Yucatán» / "Vaglio: an error-measured re-analysis of public G-LiHT lidar over the Yucatán" /
  «Vaglio: un reanálisis con errores medidos del lidar público G-LiHT sobre Yucatán».
- Tre punti: cosa abbiamo misurato (un numero ciascuno, col suo limite).
- Un paragrafo: cosa non sappiamo.
- Una riga: cosa chiediamo.
- S1, S2, S5. Poi la riga dei contatti, che riempie l'operatore.

### M3 — Lettere di primo contatto

Una per destinatario: `lettera-britton.en.md`, `lettera-kokalj-sprajc.en.md`,
`lettera-estrada-belli.en.md`, `lettera-miotti.en.md`. Corpo di al massimo 180 parole. Struttura fissa:

1. Chi scrive e S5, nelle prime due frasi. Chi legge deve sapere subito che c'è di mezzo un'AI.
2. Una frase su cosa è stato fatto, con un solo numero.
3. Perché si scrive proprio a lui o a lei (da §4).
4. **Una** richiesta, piccola, a cui si risponde in dieci minuti (da §4).
5. Cosa è allegato (la scheda M2) e cosa si può mandare su richiesta (pack cieco, tavole di figure).
6. Grazie. Firma e contatti: li mette l'operatore.

Oggetto: descrittivo, senza punti esclamativi. Esempio: "Independent re-analysis of your reprocessed
G-LiHT transects — a comparison request". Nelle lettere S1 e S2 si possono fondere in una frase sola,
purché restino tutte e due le informazioni.

### M4 — Domande e obiezioni

`domande-e-obiezioni.it.md`, poi `.en.md`. Serve all'operatore per non farsi trovare impreparato.
Undici obiezioni, risposta di al massimo 90 parole ciascuna. Ogni risposta **comincia concedendo ciò
che è vero**.

| Obiezione | La sostanza della risposta |
|---|---|
| «È già tutto noto.» | Probabilmente sì, ed è scritto in testa a ogni documento. Per questo chiediamo il confronto. |
| «Un classificatore per pixel è un giocattolo.» | I contorni sono grossolani (IoU 0,566). Serve a dire dove guardare. È misurato su etichette di archeologi mai viste, e gira su un portatile. |
| «Gli agenti AI inventano.» | Per questo sono misurati con controlli nascosti: perdono 6–7 edifici noti su 10 e non hanno sbagliato nessuno dei 10 vuoti. Quindi confermano e basta. Tre agenti dello stesso modello non sono tre pareri indipendenti. |
| «Tarato su Chactún, altrove non vale.» | Non lo sappiamo. I 40 rivisti vengono da un blocco solo. È il prossimo test, scritto prima. |
| «Venti controlli sono pochi.» | Sì. Ogni pacco ne aggiunge venti. |
| «Avete cambiato le regole in corsa.» | Due volte, entrambe dichiarate: un giro annullato per un difetto dei controlli, e la regola «conferma ma non scarta». Il criterio del rilevatore era scritto prima e non è cambiato. |
| «Perché non pubblicate le posizioni?» | Per il saccheggio. E va detto che dati e codice sono pubblici: è una scelta di condotta, non un segreto. |
| «Il LiDAR del 2013 sotto la chioma è rado.» | Sì. Le case basse possono mancare: i candidati pendono verso i rilievi più grandi. |
| «E strade, argini, cave?» | C'è un controllo sull'uso del suolo di oggi (FATTI §8). Vede le strade asfaltate, non le piste nel bosco. |
| «Chi siete?» | S5, senza abbellimenti. |
| «Cosa volete da me?» | La richiesta di §4 per quel destinatario, e nient'altro. |

### M5 — Presentazione per non addetti

`presentazione.it.md`: otto diapositive. Per ognuna un titolo di al massimo otto parole, al massimo
40 parole di testo, una figura. Scaletta fissa:

1. Cosa abbiamo fatto, e cosa no (S1 abbreviata a una riga, S2).
2. Il caso che ci ha messo in moto (FATTI §2).
3. I dati: strisce di LiDAR pubblico (`copertura.svg`).
4. Come lavora: cinque passi.
5. Quanto sbaglia il rilevatore.
6. Quanto sbagliano i revisori (due controlli come figura).
7. Cosa è uscito (`tavola_reggono.jpg`).
8. Cosa non sappiamo e cosa chiediamo. S5.

### M6 — Nota di riproducibilità

`riproducibilita.en.md`, una pagina. Requisiti (`vaglio/requirements.txt`), i comandi di
`vaglio/README.md` nell'ordine in cui vanno dati, cosa ci si aspetta di leggere a ogni passo,
identificativi dei dati (FATTI §3 e §12), i due commit della pre-registrazione (FATTI §4), la firma
del pack cieco e il comando per verificarla, i tempi (31 GB da scaricare; circa quattro ore su
quattro core).

---

## 4. A chi, e cosa chiedere

Affiliazioni come lette in fonti pubbliche il 16 nov 2026: **l'operatore le verifica** sulle pagine
degli istituti prima di spedire, e lì trova i contatti. Una lettera alla volta, in quest'ordine;
si aspetta la risposta prima della successiva.

| # | Chi | Perché lui | L'unica richiesta | Cosa si offre |
|---|---|---|---|---|
| 1 | Benjamin Jay Britton, University of Cincinnati. Autore del riprocessamento e del catalogo di 57.181 strutture | È l'unico che può dire quanti candidati sono già noti | Se è disposto a dire quale parte di un piccolo campione dei nostri candidati sta già nel suo catalogo | Un controllo indipendente del suo catalogo, fatto con un altro metodo |
| 2 | Žiga Kokalj e Ivan Šprajc, ZRC SAZU (Lubiana). Autori delle annotazioni di Chactún | Rilevatore e controlli vengono dai loro dati | Se l'uso che abbiamo fatto della loro divisione di test è una prova corretta; e se gli edifici che i revisori AI non riconoscono (tumuli consumati, senza lati dritti) sono del tipo che solo il campo decide | Il risultato sui revisori, che riguarda i loro dati |
| 3 | Francisco Estrada-Belli, Tulane University. Ha guidato l'analisi del 2025 sullo stesso LiDAR | Conosce questo LiDAR e questo terreno | Se lui o un collaboratore rivedrebbe un pacco al buio di 60 riquadri (circa venti minuti) | Sapere quanto un occhio esperto e gli agenti AI concordano |
| 4 | Pietro Miotti | Ha fatto per primo lo stesso lavoro, con agenti di modelli diversi | Se farebbe rivedere un nostro pacco al buio ai suoi agenti | Il protocollo con i controlli nascosti, che al suo progetto mancava |
| — | INAH (Messico) | È l'autorità competente | **Niente, per ora.** Ci si rivolge all'INAH solo dopo il parere di un archeologo e insieme a lui: una segnalazione fatta da soli verrebbe letta come un annuncio | — |

Perché la richiesta 3 conta più delle altre: un revisore umano esperto, misurato sugli stessi
controlli, è l'unico modo per avere qualcuno che possa anche **scartare**.

Sulle posizioni: se il confronto col catalogo le richiede, decide l'operatore, caso per caso, e solo
verso un ricercatore con nome e istituto. Chi scrive non le promette in nessuna lettera: scrive che
«il modo di fare il confronto si concorda».

Con giornalisti e pubblico generico: solo M5 e la scheda in italiano, e solo dopo che almeno un
esperto ha risposto.

---

## 5. Controlli prima di consegnare

Un materiale è finito quando tutte e cinque le righe sono vere.

1. `python -m vaglio controlla <file>` dice «a posto» (esce con codice 0). Cerca coordinate, sigle e
   parole da annuncio non negate. È un'euristica: non vede tutto.
2. La tabella di riscontro copre ogni numero del testo.
3. Le frasi obbligatorie previste per quel materiale ci sono, identiche.
4. Un **secondo** assistente, diverso da chi ha scritto, ha fatto la lettura scettica (prompt in §6)
   e i suoi rilievi sono stati corretti o motivati uno per uno.
5. L'operatore l'ha letto dall'inizio alla fine.

---

## 6. Prompt pronti

### Per chi scrive (incollare, poi aggiungere il materiale richiesto)

```
Devi scrivere un materiale del progetto Vaglio. Non fai ricerca e non cambi i fatti.

Hai tre fonti e solo quelle: FATTI.md, ISTRUZIONI.md, e la cartella kit/ (numeri.json, figure/,
pack_cieco.json). Leggile per intero prima di scrivere una riga.

Regole che non si discutono:
1. Ogni numero viene da kit/numeri.json o da FATTI.md, copiato cifra per cifra. Sotto i 100 casi
   scrivi conteggi («12 su 20»), non percentuali. Nessuna proiezione.
2. Usi le parole della tabella di ISTRUZIONI §2.2 e mai quelle della colonna «Mai».
3. Riporti identiche le frasi obbligatorie di ISTRUZIONI §2.3 previste per questo materiale.
4. Niente coordinate, sigle di candidati o transetti, mappe con candidati, classifiche dei «migliori»,
   affermazioni su età, cultura o funzione. Descrivi forme, non funzioni.
5. Usi solo le figure di kit/figure/, con le didascalie di ISTRUZIONI §2.5.
6. Non inventi contatti e non spedisci niente.

Consegna due file: il materiale, e una tabella di riscontro con ogni numero del testo e la voce di
numeri.json o la sezione di FATTI.md da cui viene. Se un fatto che ti serve non c'è nelle fonti,
non lo scrivi: lo elenchi in fondo sotto «Mi manca».

Materiale da produrre: [M1 … M6, lingua], secondo ISTRUZIONI §3.
```

### Per la lettura scettica (a un assistente diverso)

```
Sei un revisore scettico. Ti do un materiale del progetto Vaglio, FATTI.md e ISTRUZIONI.md.
Non riscrivi il testo. Cerchi, riga per riga:
1. numeri che non stanno in FATTI.md o in numeri.json, o che sono stati arrotondati o ricalcolati;
2. frasi che un lettore frettoloso leggerebbe come l'annuncio di qualcosa di nuovo;
3. limiti di FATTI §4, §6 e §10 che mancano accanto al numero a cui si riferiscono;
4. parole di funzione (piramide, tempio, palazzo, città) o aggettivi da annuncio;
5. qualunque indicazione di posizione più fine del blocco di volo;
6. frasi obbligatorie mancanti o modificate.
Rispondi con una tabella: riga, problema, correzione proposta. Se non trovi niente in una categoria,
scrivilo. Non lodare il testo.
```

---

## 7. Se qualcuno risponde

- Chiede il pack cieco o le figure: l'operatore manda `kit/pack_cieco.json` e le tavole di `kit/figure/`.
- Chiede le posizioni: decide l'operatore (§4). Di norma si propone prima il contrario, cioè che sia
  l'esperto a dire quanti candidati di un campione riconosce.
- Segnala un errore: lo si corregge nei fatti e nei materiali, e lo si scrive in `FATTI.md` §9.
  In questo progetto gli errori si pubblicano.
- Accetta di rivedere un pacco: `vaglio/RIPRESA.md` dice come si prepara e come si pesano le risposte.
