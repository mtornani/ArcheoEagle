# Azzorre — la tesi di Carlson nel ledger

**20 settembre 2026.** Innesco: Mirko segnala la spedizione di Randall Carlson alle Azzorre e un episodio del Julian Dorey Podcast in cui cita depositi e carotaggi. `CLAUDE.md` §2.3: Carlson è una **lente, non un oracolo** — entra nel ledger come tesi, con fonte, e può prendere un `−`. Ma lo prende **dopo** essere stato letto.

## Cosa NON sono riuscito a verificare, e va detto prima

**Non ho potuto leggere cosa Carlson afferma davvero.** La descrizione YouTube non è accessibile da qui, la pagina dell'evento su randallcarlson.com dà **404**. So che la spedizione c'è stata (**4–16 novembre 2025**, due settimane, «Azores: Search for Atlantis Tour») e che esiste un episodio intitolato *"Atlantis Mystery – Evidence Revealed Pt6: Landslides / Echoes in Azores"*.

Quindi **non attribuisco a Carlson nessuna affermazione specifica**. Quello che ho fatto è andare alla letteratura primaria sul tema che il titolo nomina, e misurare cosa i numeri permettono. Se qualcuno mi porta la trascrizione, il confronto si fa sul dettaglio.

## Quello che c'è di vero, e non è poco

Le Azzorre **non sono** il Richat: non è una trappola da pareidolia, è un posto con geologia reale e pertinente.

- **Frane sottomarine documentate** sui fianchi delle isole centrali (Chang et al. 2021, *G-cubed*).
- **Carote di gravità con torbiditi** originate da frane di versante; alcune torbiditi vulcanoclastiche contengono carbonati di piattaforma, cioè materiale portato giù dalla piattaforma poco profonda.
- **Treni di onde di sedimento** su cinque isole, circa due volte più frequenti sui versanti nord che sud.
- **Le piattaforme insulari si sono formate durante l'ultimo massimo glaciale**: c'è davvero terra annegata lì attorno.

Le torbiditi da frana in bacino sono esattamente il **kill-shot sostitutivo** che `PISTA-C-confinamento.md` cercava quando l'ho parcheggiata. Le Azzorre non sono un bacino confinato, ma il tipo di deposito è quello che si conserva.

## Il conto che decide, e sta tutto in una riga

Il mio `shelf.py` dice dall'inizio che l'unica via per far coincidere *terra abitabile* e *monumenti* è la **subsidenza tettonica**. Le Azzorre ce l'hanno, misurata. Ma con **due numeri pubblicati che differiscono di ~24 volte**:

| | tasso | cos'è |
|---|---|---|
| GPS, breve termine | **5,7–7,2 mm/a** | deformazione vulcanica/magmatica attuale |
| Geologico, lungo termine | **≤ 0,3 mm/a** | dalla profondità del ciglio di piattaforma su edifici di età nota |

Fonte: Quartau et al. 2015 (*G-cubed*), con **Commento** di Marques et al. 2016 e **Replica**: è contestato in letteratura, non è una verità assestata.

**Un punto che oggi sta a −30 m — il limite "niente monumenti" — quando è stato terra l'ultima volta?**

| tasso | emerso fino a | guadagno |
|---|---|---|
| nessuna subsidenza | 9,1 ka | — |
| **0,3 mm/a (max geologico)** | **8,8 ka** | **+300 anni** |
| 0,6 mm/a | 8,5 ka | +600 anni |
| **7,2 mm/a (GPS)** | **4,0 ka** | **+5.100 anni** |

**Al tasso geologico la subsidenza non apre la finestra. Al tasso GPS la spalanca** — porta un sito a −30 m dentro l'epoca di Pavlopetri e Atlit-Yam, cioè paesi veri.

Tutta la questione «alle Azzorre poteva esserci un sito sommerso» si riduce a **quale dei due numeri si usa**. E il tasso GPS misura un respiro magmatico di oggi: **applicarlo a dodicimila anni è l'errore, non la scoperta.**

## Verdetto per il ledger

| claim | esito |
|---|---|
| Alle Azzorre ci sono frane sottomarine e torbiditi in carota | **`+`** — misurato, pubblicato |
| Le piattaforme insulari sono annegate dal LGM | **`+`** — c'è terra annegata |
| La subsidenza apre la finestra per un insediamento sommerso | **`−` al tasso geologico**, `+` solo usando il GPS fuori dal suo dominio |
| Le Azzorre sono Atlantide | **N/A** — non è una domanda che questo strumento pone |

**Kill-shot, preciso:** una datazione indipendente di subsidenza sostenuta ≥1 mm/a per il tardo Quaternario su un'isola azzorriana — da terrazzi marini datati, non da GPS. Se esiste, il mio `−` cade e le Azzorre diventano il primo posto dove la finestra cronologica si apre davvero.

**Cosa non si può dire:** che l'assenza di quella datazione provi che non c'è niente. Prova che, con i numeri pubblicati oggi, la profondità e l'età non si incontrano.

## Cosa cambia nel codice

`shelf.py` ora calcola la subsidenza invece di nominarla: `depth_was_land_kyr(z, tasso)` e `deepest_ever_land_m(tasso)`, più `AZORES_SUBSIDENCE` con i due tassi e il flag `contested`. 6 test bloccano il conto. Suite 123/123.

## Nota di metodo

Il verso del conto l'ho sbagliato **due volte** prima di scriverlo giusto (*«è stato terra per QUALCHE istante»* richiede il minimo, non il massimo). Il commento è rimasto nel codice. Un risultato che dipende da un segno va guardato due volte.

---

# Aggiornamento 20/9 sera — il sito, e la tesi del micro-continente

## Il sito non contiene dati

`kosmogoniauniversity.com` dà **404 sulla radice** (esistono solo sottopagine come `/terms`); `kosmogonia.university` è un **dominio parcheggiato** (`window.location.href="/lander"`). Kosmogonia è una piattaforma di iscrizione lanciata nel 2026, e i contenuti stanno dietro `skool.com/kosmogonia`. **Non è una fonte di dati geologici**, è un portale di corsi.

## Correzione importante sulla cronologia

Gli episodi sulle Azzorre **sono del 2019, non della spedizione 2025**:

| ep | data | claim |
|---|---|---|
| #009 | 10 dic 2019 | Richat |
| **#008** | 4 dic 2019 | frane recenti dalle **Canarie**, da sonar e batimetria |
| **#007** | 7 nov 2019 | **«micro-continente granitico» sotto il medio Atlantico, esposto negli ultimi ~20.000 anni** |
| #006 | 22 ott 2019 | Younger Dryas, carote di ghiaccio |
| #005 | 22 ott 2019 | eustasia e isostasia |

Quindi il materiale della spedizione di novembre 2025 sta altrove — nell'episodio di Julian Dorey che **non sono riuscito a leggere**. Quello che valuto qui è la tesi del 2019, che è la sua versione più forte e più specifica.

L'ep #008 sulle Canarie è **già nel ledger con un `−`**: `PISTA-B-catastrofe.md` — nessun deposito transatlantico è mai stato collegato a frane delle Canarie.

## La tesi del micro-continente, spezzata in clausole

Come vuole §3: ogni clausola si testa da sola, e N/A è legale.

**Clausola 1 — «esiste materiale granitico/continentale nel medio Atlantico».** **`+`, VERO.** Zirconi **paleozoici (~330 Ma) e proterozoici (~1600 Ma)** perforati da gabbri presso la zona di frattura di Kane, pubblicati su *Nature* (1998). Non è folklore, è una misura.

**Clausola 2 — «è un micro-continente».** **Contestata.** La letteratura spiega quegli zirconi come **litosfera continentale delaminata**, riciclata attraverso celle di circolazione nel mantello poco profondo e riportata all'asse della dorsale. Il Plateau delle Azzorre è interpretato come **plateau oceanico** da interazione pennacchio–dorsale con magmatismo dal Miocene. Materiale continentale presente ≠ continente sommerso.

**Clausola 3 — «esposto negli ultimi ~20.000 anni».** **`−`, e di due-tre ordini di grandezza.**

Livello del mare a 20 ka: **−125,3 m**. Perché un punto che oggi sta a *z* fosse terra emersa allora, serve un tasso di subsidenza di almeno:

| profondità oggi | tasso richiesto | vs geologico (0,3) | vs GPS (7,2) |
|---|---|---|---|
| −130 m (minimo glaciale) | 0,2 mm/a | **1×** | 0,03× |
| −500 m (scarpata insulare) | 18,7 mm/a | 62× | 2,6× |
| −1000 m (base edificio) | 43,7 mm/a | **146×** | 6,1× |
| −2000 m (Plateau Azzorre) | 93,7 mm/a | **312×** | 13× |
| −3500 m (asse dorsale, zona Kane) | 168,7 mm/a | **562×** | 23× |

E la controprova inversa: **col tasso GPS sostenuto per 20.000 anni** — che è già un abuso, misura un respiro magmatico di oggi — si sprofonda di 144 m, e la cosa più profonda che sarebbe stata emersa sta a **−269 m**.

I zirconi vengono da **migliaia di metri** di profondità. Non c'è nessun tasso pubblicato, né onesto né generoso, che li porti all'aria 20.000 anni fa.

**E il punto che rende il verdetto solido: non dipende da quale numero scegli.** Fallisce col tasso geologico e fallisce col tasso GPS. Un `−` che regge su entrambi gli estremi della controversia non è una scelta di campo.

## Verdetto aggiornato

| clausola | esito |
|---|---|
| materiale granitico nel medio Atlantico | **`+`** — misurato, *Nature* 1998 |
| è un micro-continente | **contestata** — la letteratura dice litosfera riciclata; plateau oceanico |
| esposto negli ultimi 20.000 anni | **`−`** — servono 146–562× il tasso geologico |
| frane recenti dalle Canarie | già `−` in Pista B |

**Il modo corretto di dirlo:** Carlson ha ragione sul fatto che lì sotto c'è roba continentale, e non è una cosa da poco — è una misura pubblicata su *Nature* che molti scettici ignorano. Ha torto sul quando è stata all'aria, e ha torto di un fattore fra 146 e 562.

**Cosa non posso dire:** cosa sostenga *oggi*, dopo la spedizione del 2025. Quella è la sola cosa che manca, ed è la sola per cui mi serve la trascrizione.
