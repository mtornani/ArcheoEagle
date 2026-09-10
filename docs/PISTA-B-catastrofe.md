# Pista B — La catastrofe

**Non ha niente a che vedere con la Pista A.** Questa e' veloce (minuti-ore),
riguarda masse in movimento e onde, e vive o muore su depositi, non su proxy
lenti.

## Lo stato in una riga

**Sostanzialmente chiusa.** Tre linee indipendenti dicono che sul margine NW
africano non c'e' stato un maremoto da frana grande nell'Olocene.

## Come e' nata

L'ipotesi iniziale era: bacino con soglia, scavalcato, che si riempie in fretta.
Vajont e il Nepal 2026 l'hanno corretta prima che scrivessi il rilevatore
sbagliato: in entrambi i casi reali il killer e' una **massa solida**, non acqua
che supera un orlo, e la catastrofe e' **lineare e a valle**.

E il colpo e' piu' duro: **un bacino che si riempie non uccide.** Anche il Mar
Nero "catastrofico" sale ~15 cm al giorno — una cosa da cui ci si allontana
camminando. Sposta, non seppellisce: niente corpi, niente abbandono improvviso,
quindi **ne' memoria traumatica ne' giacimento in posto**.

Tre meccanismi, e l'ipotesi iniziale copriva il meno interessante:

| | meccanismo | uccide? | conserva? | firma |
|---|---|---|---|---|
| 1 | riempimento per sfioro | no, sposta | male | geometria: conca + soglia |
| 2 | massa che sposta l'acqua (Vajont, Storegga) | si', in minuti | benissimo | **stratigrafia** |
| 3 | rilascio a valle (Nepal 2026, GLOF) | si', in minuti | bene | detrito, scavo di valle |

## Perche' e' chiusa

| linea | esito |
|---|---|
| **Sahara Slide** (~600 km3, runout 900 km) | ritenuto **non tsunamigenico**: pendio dolce, accelerazione bassa, rottura retrogressiva |
| **Mauritania Slide Complex** (10.5-10.9 cal ka BP, dentro la finestra!) | **retrogressivo**, lo stesso stile non tsunamigenico |
| **deposito transatlantico** sulla sponda opposta | **cercato e non trovato**: nessun deposito sul bordo del bacino atlantico e' mai stato collegato alle grandi frane delle Canarie. I massi delle Bahamas sono attribuiti a **tempeste**; i depositi caraibici documentati hanno sorgenti **locali** (Great Bahama Bank) |

E combacia con la fisica: uno tsunami da frana ha **sorgente compatta e decade
come 1/r**. Storegga devasto' Doggerland a 700 km; attraverso 5.000 km di
Atlantico un'onda da frana arriva piccola.

**Il volume non e' il criterio.** Lo sono pendenza, coerenza e accelerazione.
Una massa enorme che scivola piano non sposta acqua in modo impulsivo.

## Il valore dell'esito negativo

L'assenza del deposito lontano **e' informativa** — stesso ragionamento
dell'iridio mancante nel caso del Dryas recente. **Pone un tetto** a quanto
grande possa essere stato un maremoto da frana olocenico su quel margine.

## Cosa la riaprirebbe

Il catalogo dei depositi di tsunami caraibici e' **datato** (Engel et al. 2016 e
successivi). Se ne comparisse uno a **10.5-10.9 ka** con firma di campo lontano,
sarebbe il collegamento col Mauritania Slide Complex. **Oggi non c'e'.**

Il codice geometrico che resta utile: `backend/core/marine/basin.py` — punto di
sfioro (serve meccanismo 1 e 3), percorso dello sfioratore, ipsometria,
potenziale di sorgente di frana. Con il limite dichiarato: **il meccanismo 2,
il piu' promettente, non ha firma geometrica.** Sta nella stratigrafia, e
nessun DEM lo vedra' mai.
