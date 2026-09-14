# Pista C — il confinamento

**Aperta il 13 settembre 2026.** Innesco: Dickson Fjord, Groenlandia, 16 settembre 2023.

**Non e' la Pista B riaperta.** Pista B chiedeva: *una frana sul margine mauritano ha mandato uno tsunami attraverso l'Atlantico?* Risposta: no, e resta no. Pista C chiede un'altra cosa: *qual e' la classe di eventi capace di generare il concetto, ovunque sia successa?* Geografia diversa, meccanismo diverso, test diverso. Se qualcuno usa questa pista per rimettere in piedi la Mauritania, sta barando.

---

## Il fatto

25 milioni di m3 di roccia e ghiaccio nel Dickson Fjord. Run-up ~200 m. L'acqua resta chiusa fra due pareti e oscilla, periodo ~92 s, per **nove giorni**: 10,88 mHz su tutta la rete sismica globale (Svennevig et al., *Science*, 2024).

Il confronto che conta:

| | volume | esito |
|---|---|---|
| Sahara Slide | ~600.000 milioni di m3 | giudicato **non** tsunamigenico |
| Dickson Fjord | ~25 milioni di m3 (**24.000x meno**) | run-up 200 m, 9 giorni di segnale |

`collapse_source_potential()` diceva gia' che il criterio e' la pendenza, non il volume. Dickson lo conferma con un fattore 24.000. Ma aggiunge la variabile che nel codice non c'era: **dove finisce l'energia**. Su pendio aperto l'onda irradia e si diluisce. In un bacino chiuso si riflette, si somma, e torna. Non un'onda: un'onda ogni 90 secondi per giorni.

## Cosa e' stato scritto

`backend/core/marine/seiche.py` — `merian_period`, `greens_amplification`, `confinement`, `basin_axes_m`, `seiche_profile`, `displacement_hazard`, `dickson_control`. 22 test in `backend/tests/test_seiche.py`.

**Il controllo positivo passa: 86,2 s previsti contro 92 s osservati, scarto 6%.**

E' il **primo controllo positivo del progetto che passa**. Otto rilevatori di sponda hanno fallito sulla Bama Ridge (`CALIBRAZIONE.md`). Questo ritrova un numero pubblicato. La differenza non e' bravura: e' che qui il bersaglio e' un **numero** (un periodo), la' era una **forma dentro una scena** (un cordone fra migliaia di frammenti di isolinea). Le statistiche d'insieme sanno fare la prima cosa e non la seconda.

`displacement_hazard` non contiene il volume nella firma, ed e' voluto — c'e' un test che lo verifica.

## Il limite, che e' definitivo

| | |
|---|---|
| **Misurabile** | La geometria. Confinamento, assi, profondita' -> periodo atteso. Restringimento e basso fondale -> amplificazione. Da DEM/batimetria che gia' scarichiamo. |
| **NON misurabile** | Il segnale. **Nessun proxy geologico registra un'oscillazione di 90 secondi di 12.000 anni fa.** Quei 9 giorni esistono solo perche' c'e' una rete broadband globale dal ~1990. Per il passato remoto il segnale non e' debole: e' **assente**. |
| **Preservato** | Il deposito di run-up: sedimento portato **sopra il piano d'acqua**. Nessun processo di riva normale mette sedimento lacustre a 100 m di quota. E' l'unico test falsificabile del meccanismo. |

Quindi la risposta secca alla domanda "e' questo il nostro proxy globale?" e' **meta' si'**. Il meccanismo si', il segnale no. Cercare la firma sismica di una seiche antica e' cercare una cosa che non e' mai stata scritta da nessuna parte.

## Metodo: l'inversione che NON dobbiamo copiare

Dickson e' stato risolto **anomalia prima, spiegazione dopo**: qualcuno ha visto un segnale inspiegato (lo chiamarono USO, *unidentified seismic object*) e ha cercato la causa. Ha funzionato benissimo — perche' avevano un segnale.

Noi non ce l'abbiamo. Copiare quel metodo senza quel segnale significa partire da una forma nel deserto e cercarle una causa: e' esattamente la pareidolia vietata da CLAUDE.md §3. La disciplina resta **previsione prima, dato dopo**.

## Il costo concettuale

Se il concetto nasce da una **classe** di eventi e non da un evento, il bersaglio si allarga invece di restringersi. Ogni bacino chiuso con pareti ripide e gente sulla riva e' un biglietto della lotteria. Non c'e' piu' un luogo: ce ne sono N.

Il guadagno e' che N e' **finito ed enumerabile**. Lo screening ha quattro condizioni, tutte necessarie:

1. bacino confinato (`enclosure` alta) — da DEM/batimetria
2. orlo ripido (`collapse_source_potential`) — da DEM
3. riva abitabile nella finestra 15–5 ka — da `shelf.py` (vincolo cronologico gia' scritto)
4. **deposito di run-up sopra il piano d'acqua** — stratigrafia, l'unico test vero

Le prime tre sono uno screen da fare da casa. La quarta e' il giudizio, e non e' geometria.

## Una previsione tentata e messa da parte

Se il concetto nasce da questa classe, i miti di *terra persa per sempre in un giorno, con superstiti* dovrebbero addensarsi su bacini confinati a pareti ripide, mentre i miti di piena fluviale dovrebbero stare sulle pianure alluvionali. Contrasto reale, non soddisfatto dall'ipotesi nulla.

**Non la corro.** I cataloghi di miti di diluvio sono contaminati da bias di raccolta e dalla diffusione della Genesi in epoca missionaria: separare il segnale dal contatto e' un lavoro da folklorista, non da DEM. Registrata qui perche' e' una previsione onesta, e perche' l'ultima volta che ne ho costruita una male (demografia al radiocarbonio, `19218ac`) l'ipotesi nulla la soddisfaceva da sola.

## Stato

Aperta come **strumento**, non come caccia. Nessun bacino candidato e' stato ancora valutato. Il punteggio geometrico e' una predisposizione, mai un evento: dice dove andare a cercare uno strato.

---

# PARCHEGGIATA — 14 settembre 2026

**Non chiusa: parcheggiata, e con una ragione precisa.** Il meccanismo regge. Il controllo positivo (Merian, 86,2 s previsti contro 92 osservati) passa ancora. Ma **il test che le avevo assegnato non è eseguibile nel contesto che mi serve**, e una pista senza test è uno strumento, non un'indagine.

## Cosa l'ha fermata

Sopra, in questo stesso file, avevo scritto che il deposito di run-up sopra il piano d'acqua è **l'unico test falsificabile** del meccanismo. La ricerca bibliografica del 14/9 (`GEMINI-ROUND-1.md`, domanda 2) riporta:

> Nei bacini lacustri confinati perialpini i depositi di run-up sopra la linea di riva **non sono stati trovati o sono privi di continuità stratigrafica**. Il riflusso d'onda e l'erosione meteorica rimuovono la sabbia oltre riva **entro pochi decenni**, preservando solo la torbidite sul fondo.

E, esplicitamente: **nessun caso al mondo** di deposito da run-up subaereo in un bacino lacustre chiuso ed endoreico, 15–5 ka, conservato sopra riva.

Il mio kill-shot non è difficile. In un bacino chiuso **non esiste**.

## Perché non lo sostituisco e basta

Il sostituto naturale c'è ed è la **torbidite sul fondo del bacino**, che invece si conserva bene. Ma è **stratigrafia da carota**, non geometria da DEM: esce dalla capacità "da casa" che è il vincolo fondante del progetto (CLAUDE.md §1). Tenerla aperta fingendo che sia testabile da qui sarebbe coprire un buco, cioè la prima cosa vietata da §0.

## Il verdetto dello screening, che resta valido

`SCREENING-BACINI.md`: **nessun bacino sahariano ha la geometria di Dickson.** Qattara a 27 m/pixel dà orlo zero; l'Hoggar ha 1955 m di rilievo e comunque orlo zero. Il Sahara ha montagne, non catini a pareti ripide. Questo risultato non dipende dal kill-shot mancante ed è un restringimento vero.

## Cosa resta utile, e cosa serve per riaprirla

Restano in repo e funzionano: `seiche.py` (Merian, Green, confinamento, `displacement_hazard`) e i 22 test. Servono se un giorno arriva un bacino candidato.

**Condizione di riapertura, una sola:** accesso a dati di carotaggio — proprio o pubblicato — di un bacino confinato con riva abitabile 15–5 ka, in cui cercare una **torbidite da spostamento di massa** databile. Finché non c'è, questa pista non si tocca.

I quattro candidati che la ricerca ha portato (Mar Morto, Bonneville, Turkana, Storfjorden) sono il posto da cui ripartire — non per camminarli col DEM, ma per cercare se qualcuno li ha già carotati.
