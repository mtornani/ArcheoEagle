# Prompt per Gemini Deep Research

Progettato il 13/9/2026. **Principio: chiedere falsificatori, non conferme.** Un agente di ricerca lasciato libero trova sempre materiale a sostegno della tesi che gli hai messo davanti. Questo prompt gli chiede l'opposto, e definisce cosa accettiamo come risposta.

Copia da qui in giù.

---

## RUOLO

Sei un ricercatore forense in paleoclimatologia, geomorfologia e archeologia costiera. Il tuo compito **non** è sostenere un'ipotesi: è cercare i dati che la **ucciderebbero**. Se dopo ricerca approfondita un dato non esiste, dirlo esplicitamente è un risultato di pieno valore — spesso il più utile.

## CONTESTO (fermo, non da rimettere in discussione)

Un progetto indipendente cerca prove oggettive e falsificabili su un possibile referente geografico dietro il racconto di Atlantide. Non cerca una città, non cerca anelli concentrici, non cerca l'Atlantico. Ipotesi di lavoro: paleoidrologia sahariana e paesaggi costieri sommersi, ~15.000–5.000 anni fa.

Conclusioni già raggiunte e **già documentate** — non ripetermele, servono solo perché tu sappia cosa NON cercare:

- Nessun deposito transatlantico è mai stato collegato a frane delle Canarie. Sahara Slide (~600 km³) giudicato non tsunamigenico: pendio dolce, rottura retrogressiva.
- Il cratere Hiawatha (Groenlandia) è stato ridatato nel 2022 a ~58 milioni di anni. Non è un candidato Younger Dryas.
- L'anomalia di platino GISP2 a ~12.890 anni (Petaev 2013; Moore 2017) è nota e accettata come misura.
- Nanodiamanti e microsferule magnetiche dell'ipotesi d'impatto Younger Dryas non hanno superato la replica indipendente (Surovell 2009; Daulton 2010, 2017).
- Dickson Fjord 2023 (Svennevig et al., Science 2024) è noto in ogni dettaglio.

## COSA NON ACCETTO

- **Fonti divulgative come prova**: YouTube, blog, documentari, siti di divulgazione, Wikipedia. Puoi usarli per orientarti, mai per sostenere un'affermazione.
- **Letteratura secondaria su Hancock o Carlson.** Se un dato è reale esiste un lavoro primario: cita quello. Se non esiste, dimmi che non esiste.
- **Parafrasi al posto dei numeri.** "Un rapido innalzamento" non è un dato. "8,2 ± 1,4 m in 160 anni" lo è.
- **Sostituzioni.** Se cerco X e trovi Y che gli somiglia, non spacciarmi Y per X. Dimmi: "X non trovato; il più vicino è Y, che differisce per…".
- **Riempitivo.** Meglio due domande con risposta solida e tre "non trovato" che cinque risposte annacquate.

## PER OGNI DATO CHE RIPORTI, OBBLIGATORI

1. **Citazione primaria** — autori, anno, rivista, **DOI**.
2. **Numeri con unità e incertezza**, come compaiono nel lavoro.
3. **Tipo**: misura diretta / modello / compilazione / revisione. Distinzione non negoziabile.
4. **Base cronologica**: quale metodo di datazione, calibrato o no, con che errore.
5. **Stato della replica**: confermato indipendentemente, contestato, mai ritentato.
6. **Accessibilità del dato**: esiste un archivio pubblico (PANGAEA, NOAA Paleoclimatology, Zenodo, repository dell'editore)? Accessione o URL. **Scaricabile senza registrazione, sì o no.** Questo campo mi serve quanto il dato.

## LE CINQUE DOMANDE

Trattale come indagini separate. Ordine di priorità decrescente.

### 1. Il livello del mare al Younger Dryas — cerca di smentirmi

Ho concluso, da una curva schematica, che il Younger Dryas (12.900–11.700 anni fa) è **il tratto più lento dell'intera deglaciazione**: ~7,5 m in 1.200 anni. Voglio sapere se è vero contro i dati primari.

**Cerca specificamente un record di livello del mare che mostri un innalzamento rapido, di scala metrica, DENTRO la finestra 12.900–12.500 anni fa.** Coralli, microatolli, sequenze di mangrovie, sedimenti costieri — con datazione U-Th o radiocarbonio calibrato.

Accetto come risposta valida: "nessun record mostra un salto in quella finestra; ecco i record che coprono la finestra e cosa mostrano invece."

Copri anche, separatamente: **MWP1B** (~11.300 anni). Esiste davvero? Barbados sì e Tahiti no — qual è lo stato attuale del dibattito, e quanti metri in quanti anni nelle stime più recenti?

### 2. Depositi di run-up dentro bacini confinati

Cerco un test falsificabile per il meccanismo Dickson: una frana in un bacino chiuso genera un'onda che l'acqua non può disperdere, e questa deposita sedimento **sopra il piano d'acqua**.

**Cerca depositi di run-up o di tsunami identificati in bacini confinati o semi-chiusi** — fiordi, laghi, golfi stretti, mari interni — **datati fra 15.000 e 5.000 anni fa**.

Per ognuno: quota del deposito sopra il livello d'acqua contemporaneo, spessore, criteri usati per chiamarlo run-up e non tempesta o piena, meccanismo attribuito.

Interessa anche il **catalogo dei negativi**: bacini dove il deposito è stato cercato e **non** trovato. Nella letteratura questi quasi non si pubblicano; se ne trovi anche solo due o tre, dimmelo.

### 3. Bacini confinati abitati, fuori dal Sahara

Ho fatto lo screening del Sahara: nessun bacino ha la geometria giusta. Qattara a 27 m/pixel dà pendenza dell'orlo zero; l'Hoggar ha 1.955 m di rilievo e comunque zero sull'orlo delle sue conche. **Il Sahara ha montagne, non ha catini a pareti ripide.** Serve guardare altrove.

**Elenca i bacini confinati del mondo che soddisfano TUTTE queste condizioni:**

- chiuso o quasi chiuso (fiordo, lago profondo, mare interno, golfo stretto);
- **pareti ripide** — almeno un tratto di sponda oltre ~17° (pendenza 0,30), con il numero se pubblicato;
- riva **abitata o abitabile** fra 15.000 e 5.000 anni fa, con evidenza archeologica o paleoambientale;
- presenza documentata di **frane, crolli di parete o instabilità di versante** sulla sponda.

Per ognuno voglio: nome, coordinate approssimate, profondità e larghezza, la citazione dell'evidenza archeologica, la citazione dell'evidenza di instabilità.

Non ti serve un candidato "buono": mi serve **la lista completa**, quelli deboli inclusi, perché lo scopo è chiudere lo spazio di ricerca, non trovare il vincitore.

### 4. Paleosponde datate — mi serve un banco di taratura

Ho un rilevatore automatico di paleosponde su DEM che ha **fallito otto volte** su un bersaglio noto (Bama Ridge, sponda del Mega-Chad). Sospetto che il problema sia avere **un solo caso di controllo**.

**Cerca paleosponde lacustri e marine con quota misurata e data indipendente**, ovunque nel mondo, priorità a quelle su terreno arido dove il DEM le vede ancora.

Per ognuna: quota s.l.m. con incertezza, estensione, metodo di datazione (OSL, radiocarbonio, cosmogenici) con errore, coordinate o riquadro.

Mi serve **quantità**: dieci sponde datate valgono più di una descritta bene. Con dieci posso misurare quante volte il rilevatore sbaglia; con una no.

### 5. Carbone e cere fogliari appaiati nella stessa carota

Un'anomalia di carbone al largo della Mauritania (carota GeoB7920-2) si è rivelata un cambio della **sorgente della polvere**, dimostrato dagli isotopi Sr-Nd della vicina ODP 658C. Per riaprire la questione servirebbe replicarla altrove.

**Cerca carote marine o lacustri che misurino, sullo stesso materiale, sia il carbone (microcharcoal) sia le cere fogliari (n-alcani, C29/C31), nella finestra 15.000–5.000 anni fa.**

Priorità al margine dell'Africa nord-occidentale, ma accetto qualsiasi area.

Dimmi anche, separatamente: esiste letteratura pubblicata sulla **granulometria** di GeoB7920-2 stessa?

## FORMATO DELLA RISPOSTA

Una sezione per domanda, nell'ordine. Dentro ciascuna:

1. **Esito in una riga**: TROVATO / PARZIALE / NON TROVATO.
2. **I dati**, in tabella dove sono più di due, con tutti i sei campi obbligatori.
3. **Cosa non sono riuscito a stabilire** — esplicito.
4. **Contraddizioni fra fonti**, se ce ne sono. Non appianarle: mostrale.

Chiudi con una sezione **"Se avessi altro tempo"**: le tre piste che hai visto aprirsi e non hai potuto seguire.

## AVVERTENZA FINALE

Se in qualche punto ti accorgi che una mia premessa nel contesto qui sopra è sbagliata — cronologia, attribuzione, un lavoro ritirato o superato — **dillo subito e in evidenza**. Una premessa sbagliata corretta vale più di tutte e cinque le risposte.
