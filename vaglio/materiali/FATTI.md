# Vaglio — scheda dei fatti

Aggiornata il 16 nov 2026. È l'unica fonte dei fatti per chi scrive rapporti, lettere o presentazioni.
Regola: **un numero o un'affermazione che non sta qui, o in `kit/numeri.json`, non si scrive.**
Se questa scheda e `kit/numeri.json` danno conteggi diversi, vale `numeri.json` (è più recente);
per l'interpretazione vale questa scheda.

Ogni fatto ha un grado:

- **misurato** — c'è un numero, un file e un modo di rifarlo;
- **riferito** — lo dice una fonte esterna, citata; non l'abbiamo verificato noi;
- **non noto** — non lo sappiamo, e va detto così.

---

## 1. Che cos'è

Vaglio è un programma che legge rilievi LiDAR pubblici, segnala i punti in cui il terreno nudo ha
la forma di una costruzione, li fa rivedere al buio e scrive un fascicolo. Gira su un portatile,
senza chiavi e senza scheda grafica. Codice pubblico: repository `mtornani/ArcheoEagle`, cartella `vaglio/`.

Non è stato scritto da archeologi. Ricerca condotta da assistenti AI (Claude per metodo, codice e
misure; GPT per il completamento della scansione) con la supervisione di Mirko Tornani.

## 2. Da dove nasce (riferito)

A novembre 2026 Pietro Miotti, ricercatore di Google, ha pubblicato un progetto personale: 48 agenti
AI hanno guardato circa 1.200 km² di LiDAR NASA sullo Yucatán e hanno segnalato un sito maya che
l'istituto messicano INAH non aveva nel registro. L'archeologa Sarah Parcak ha fatto notare che il
sito era già pubblicato in un lavoro del 2025 guidato da Francisco Estrada-Belli (Tulane). L'11
novembre Miotti ha riconosciuto che gli agenti l'avevano «riscoperto».

Fonti: pietromiotti.com/latest/maya-site/ · futurism.com/artificial-intelligence/ai-found-ancient-maya-site-not

Come parlarne: Miotti ha fatto per primo una cosa che funziona, e ha corretto in pubblico. Vaglio
riprende il suo metodo e aggiunge le misure che lì non c'erano. Non lo si deride e non lo si usa
come bersaglio.

## 3. I dati

| Fatto | Grado |
|---|---|
| LiDAR aereo NASA G-LiHT, campagna AMIGA-Carb, aprile–maggio 2013, laser Riegl VQ-480 a circa 335 m dal suolo | riferito (scheda OpenTopography) |
| Riprocessato nel 2026 da Benjamin Jay Britton (University of Cincinnati): punti a terra riclassificati da capo, modelli del terreno a 33 cm | riferito (scheda OpenTopography) |
| 456 transetti (222 a ovest, 234 a est), 1.272,7 km² in tutto | misurato (`vaglio/vaglio/data/transects.json`) |
| Pubblici, senza chiave: doi:10.5069/G9Z899N1 e doi:10.5069/G9TH8JX9. Licenza di pubblico dominio (PDDL) secondo la raccolta dell'autore su Scholar@UC | riferito |
| Sono gli stessi transetti del lavoro di Miotti e, in un insieme più ampio, di Estrada-Belli et al. 2025 | riferito |

I transetti sono strisce larghe circa 400 m e lunghe in mediana 7,6 km (al massimo 9,4): campionano la
penisola, non la coprono. 1.273 km² sono meno dell'1% della penisola.

## 4. Il rilevatore

| Fatto | Grado |
|---|---|
| Addestrato sulle annotazioni di Chactún (Kokalj, Džeroski, Šprajc et al. 2023, *Scientific Data* 10:558; CC BY 4.0): 2.094 riquadri di 240 m con edifici e piattaforme delineati da archeologi | riferito (il dataset) |
| Di quelle annotazioni, il 22,4% degli edifici e il 24,2% delle piattaforme è stato verificato sul campo dagli autori | riferito (l'articolo) |
| Divisione addestramento/test: quella degli autori del dataset. Test su 329 riquadri mai usati prima | misurato |
| Criterio di successo scritto e committato prima di guardare il test: ritrovare almeno il 70% delle strutture annotate, con almeno il 70% di segnalazioni corrette | misurato (commit `1028de8`, poi emendamento `b592a1e`, entrambi prima del test) |
| **Esito, eseguito una volta: su 942 strutture annotate ne ritrova il 76,4%; delle 677 segnalazioni l'83,0% cade su una struttura annotata. Criterio superato** | misurato (`vaglio/vaglio/model.py`) |
| Sovrapposizione dei contorni (IoU) 0,566: i contorni sono grossolani. Serve a dire dove guardare, non a disegnare piante | misurato |

Limiti da dire sempre insieme al numero:

- Ogni riquadro di Chactún contiene almeno una struttura. La precisione dell'83% vale in terreno
  **denso di rovine**. In terreno vuoto, carsico o coltivato non è stata misurata da questo test.
- Chactún è stato rilevato con un altro strumento, a densità di punti più alta. Quanto il rilevatore
  perda passando ai dati NASA del 2013 **non è noto**.
- Il modello è un classificatore per pixel a gradient boosting, non una rete profonda. È scelto perché
  è piccolo, trasparente e gira su qualunque computer. Non citare confronti con altri metodi: non li
  abbiamo misurati.

## 5. La scansione

| Fatto | Grado |
|---|---|
| Scansionati 456 transetti su 456, 1.272,7 km² | misurato |
| 11.916 «complessi candidati»: gruppi di rilievi a forma di costruzione distanti fra loro meno di 60 m | misurato (`vaglio/pack_cieco.json`) |
| Dentro quei complessi ci sono 24.265 rilievi singoli | misurato |
| 7.328 complessi (61%) sono fatti di un solo rilievo; 845 ne hanno almeno 5; 214 almeno 10 | misurato |
| Area mediana di un complesso 1.018 m²; il rilievo più alto sporge in mediana di 1,4 m | misurato |
| I primi 51 transetti sono stati scansionati e controllati da Claude; gli altri 405 sono stati completati sul computer dell'operatore da un altro assistente. Di quelli Claude ha verificato l'elenco finale (firma integra, nessuna posizione, coerenza con i primi 51), **non** ha rifatto la scansione | misurato / dichiarazione di provenienza |

Un «complesso candidato» **non è un sito**. È un punto dove il rilevatore ha visto una forma.

## 6. La revisione al buio

Come funziona: i candidati vengono mostrati come riquadri di 120 m, senza nome né posizione, mescolati
a riquadri di controllo di cui la risposta è nota (presi dai riquadri di test di Chactún). Chi rivede
non sa quali sono i controlli.

| Fatto | Grado |
|---|---|
| Primo giro **annullato**: i controlli positivi erano tagliati sul bordo del riquadro e i revisori, correttamente, vedevano terreno vuoto. Il difetto era nel controllo | misurato |
| Secondo giro: 40 candidati + 20 controlli, tre revisori (agenti AI Claude, indipendenti fra loro) | misurato |
| Sui 10 controlli con struttura i tre revisori ne hanno riconosciuti 4, 3 e 4 | misurato |
| Sui 10 controlli vuoti nessuno dei tre ha mai detto «struttura» (i 10 riquadri sono gli stessi per tutti) | misurato |
| I tre revisori concordano fra loro sul 90–97% dei candidati | misurato |
| Esito sui 40: **15 reggono alla revisione** (almeno due revisori dicono «struttura»), 25 restano incerti, 0 scartati | misurato |
| Regola adottata dopo aver visto questi numeri, e dichiarata come tale: un revisore che non sbaglia i vuoti può **confermare**; solo un revisore che riconosce almeno il 70% delle strutture note può **scartare**. Questi agenti possono confermare, non scartare | misurato / scelta a posteriori |

Come leggere il campione dei 40, senza gonfiarlo:

- È stato estratto quando erano scansionati solo i primi 40 transetti circa, **tutti in un solo blocco**
  («Centro»): 20 col punteggio più alto in quel momento, 20 a caso fra gli altri.
- Dei 20 col punteggio più alto reggono 12. Dei 20 a caso reggono 3.
- Nella scansione completa quei «20 più alti» non sono più i più alti: stanno fra la 13ª e la 433ª
  posizione su 11.916. **Dei primi 100 candidati della scansione completa ne sono stati rivisti 3.**
  I 20 presi a caso stanno fra la 1.844ª e la 11.858ª.
- Tre revisori dello stesso modello che concordano non sono tre conferme indipendenti.
- Gli agenti riconoscono gli edifici a lati netti e non i tumuli consumati. Quindi «15 reggono» è
  una stima per difetto di quanti, fra quei 40, sono costruiti; e «25 incerti» **non** vuol dire
  25 falsi.

## 7. Già noto

| Fatto | Grado |
|---|---|
| Su questi stessi transetti riprocessati esiste un catalogo di 57.181 strutture maya (Britton 2026). Non è pubblico | riferito (scheda OpenTopography) |
| Lo stesso rilievo è stato analizzato da Estrada-Belli et al. 2025 e da Britton et al. 2026 (*J Archaeol Method Theory* 33:15) | riferito |
| **Nessun candidato è stato confrontato con il catalogo di Britton né con il registro INAH** | misurato (non l'abbiamo fatto) |
| 249 candidati stanno entro 2 km da uno dei 229 siti elencati su Wikidata; gli altri 11.667 sono marcati «rilievo già analizzato: presumi già noto» | misurato |

Conseguenza, da scrivere in ogni materiale: su questi dati Vaglio **riproduce** un'analisi già
fatta da altri, con un metodo diverso e con gli errori misurati. Quanti candidati siano già nel
catalogo di Britton **non è noto**; la presunzione è «quasi tutti».

I 24.265 rilievi di Vaglio e le 57.181 strutture di Britton **non sono confrontabili**: definizioni,
soglie di area e metodi diversi. Non presentare il rapporto fra i due numeri come una percentuale di
ritrovamento.

## 8. Moderno

| Fatto | Grado |
|---|---|
| Per ogni candidato si può leggere l'uso del suolo di oggi (ESA WorldCover 2021, 10 m, CC BY 4.0) nel riquadro di 120 m | misurato (`python -m vaglio moderno`) |
| Sui 1.548 candidati dei primi 51 transetti, 11 hanno almeno il 5% di «costruito». Guardati uno per uno (non al buio): sono tutti e 11 strade asfaltate con le loro scarpate | misurato, controllo a vista di Claude |
| Lo stesso conto sulla scansione completa | **non noto** finché non gira `moderno` sul computer dell'operatore: poi sta in `numeri.json` |

Limiti: il LiDAR è del 2013, la carta del 2021. Una pista sterrata nel bosco non risulta «costruito».
Un abitato moderno sta spesso sopra un sito antico: «costruito oggi» non vuol dire «non antico».

## 9. Cose provate che non hanno funzionato

Vanno dette: fanno parte del risultato.

- Prima di Vaglio, un rilevatore di tumuli sul modello del terreno gratuito a 30 m (alto Khabur, Siria,
  14.324 siti noti di Menze e Ur 2012 come controllo) ha **fallito due volte** un test pre-registrato:
  ritrovava dal 6 al 24% dei tumuli alti, e scansionando al buio da 86 a 98 allarmi su 100 non erano
  tumuli a catalogo. È il motivo per cui Vaglio lavora solo dove c'è LiDAR ad alta risoluzione.
- Il primo giro di revisione è stato annullato (sezione 6).
- La misura di «ortogonalità dei bordi», aggiunta per abbassare in classifica il carsismo naturale, non
  pesa nel predire cosa i revisori confermano, una volta contate altezza e probabilità (33 casi, un
  solo blocco: indizio, non conclusione).
- Un «ordine appreso» dalle 40 revisioni separa bene tenuti e non tenuti sui 33 casi utilizzabili
  (0,99 su 1 lasciandone fuori uno alla volta), ma il numero è gonfiato dal modo in cui è fatto il
  campione, e applicato alla scansione completa spinge in cima i rilievi più alti, cioè anche colline
  naturali. **Non è adottato** finché non supera una prova scritta prima (`vaglio/RIPRESA.md`).

## 10. Quello che non sappiamo

1. Quanti degli 11.916 candidati sono costruzioni. Il campione rivisto viene da un solo blocco e non
   si estende agli altri sei. **Non estrapolare** «12 su 20» o «3 su 20» a 11.916.
2. Quanti sono già nel catalogo di Britton o nel registro INAH.
3. Età, cultura, funzione di qualunque candidato.
4. Quanto il rilevatore perde su questi dati rispetto a Chactún.
5. Quanto valgono i candidati fuori dal blocco «Centro» (Chiapas montuoso, nord coltivato e abitato).

Nessun candidato è stato visto sul campo.

## 11. Posizioni

Le posizioni dei candidati esistono solo nella cartella locale `vaglio_lavoro/` dell'operatore e non
sono in nessun materiale. Motivo: una mappa pubblica di rovine non scavate serve ai saccheggiatori.

Onestà sul limite: dati e codice sono pubblici, quindi chiunque rifaccia la scansione riottiene lo
stesso elenco. La riservatezza è una scelta di condotta, non un segreto tecnico.

L'elenco senza posizioni è pubblico: `vaglio/pack_cieco.json`, 11.916 candidati, firmato il
2026-11-16T17:27:11+00:00, SHA-256
`3b94f3d294788a987b0497188484cbdac15c81159ac9c35f3dc6522c8a7a4ba0`.
Chiunque lo controlla con `python -m vaglio verifica pack_cieco.json`.

## 12. Crediti da riportare

- LiDAR: NASA G-LiHT (AMIGA-Carb, 2013); riprocessamento B. J. Britton (2026), distribuito da
  OpenTopography, doi:10.5069/G9Z899N1 e doi:10.5069/G9TH8JX9.
- Addestramento e controlli: Kokalj, Ž., Džeroski, S., Šprajc, I. et al. (2023). Machine learning-ready
  remote sensing data for Maya archaeology. *Scientific Data* 10, 558. Dati: doi:10.6084/m9.figshare.22202395, CC BY 4.0.
- Uso del suolo: ESA WorldCover 10 m 2021 v200, CC BY 4.0.
- Mappa di sfondo: Natural Earth, pubblico dominio. Siti noti: Wikidata, CC0.
