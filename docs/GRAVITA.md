# Gravità — dove manca massa, e perché quasi mai serve

**13 settembre 2026.** Domanda: *esistono archivi pubblici di anomalie gravitazionali planetarie — troppa massa in un punto, o troppo poca?* Sì, esistono, sono gratuiti e li ho verificati vivi. La risposta utile però non è "dove sono": è **cosa possono e non possono risolvere**, perché la differenza fra le due cose è un fattore 90.

## La trappola, prima di tutto

Scorrere una mappa gravimetrica globale in cerca di "punti strani" è **anomalia prima, spiegazione dopo**. È il metodo con cui hanno risolto Dickson (videro un segnale inspiegato, cercarono la causa) e ha funzionato perché *avevano un segnale*. È anche, parola per parola, il metodo che `PISTA-C-confinamento.md` dice di non copiare, e la pareidolia vietata da CLAUDE.md §3.

Il campo gravitazionale terrestre è **pieno** di anomalie. Sono geologia: radici crostali, bacini sedimentari, intrusioni, subduzione. Un occhio che cerca il bersaglio ne trova uno ovunque.

**Regola operativa: la gravità entra come colonna su candidati già scelti dalla geometria, oppure come kill-shot. Mai come ricerca.**

## L'aritmetica che decide tutto

La risoluzione di un modello a armoniche sferiche di grado N è la semi-lunghezza d'onda: 20.015 km / N. Grado massimo pubblicamente disponibile, verificato sul catalogo ICGEM il 13/9/2026: **2190**.

| modello | grado | risoluzione |
|---|---|---|
| EGM2008 / SGG-UGM-2 | 2190 | **9,1 km** |
| XGM2019e_2159 | 2159 | 9,3 km |
| GOCE da solo | ~300 | 67 km |
| GRACE-FO mensile | ~96 | 208 km |

Per **vedere** un oggetto ne serve almeno il doppio della risoluzione (~18 km).

| oggetto | dimensione | esito |
|---|---|---|
| insediamento sommerso | 0,1 km | **invisibile** (180x troppo piccolo) |
| nicchia di frana tipo Dickson | 2 km | **invisibile** |
| bacino sedimentario | 20 km | visibile |
| struttura crostale | 100 km | visibile bene |

**La gravità non vede archeologia. Non vede nemmeno la frana.** Chi dice il contrario sta vendendo qualcosa.

## GGMplus: 200 metri che non sono quello che sembrano

Esiste GGMplus (Hirt et al., Curtin University, `ddfe.curtin.edu.au/gravitymodels/GGMplus/`, **vivo, http 200**), che copre le terre emerse fino a ±60° di latitudine — Sahara compreso — a **200 m nominali**. Sembra la soluzione a tutto.

Non lo è, e la ragione va scritta in grande: **le lunghezze d'onda corte di GGMplus non sono misurate. Sono modellate in avanti dalla topografia** (SRTM), assumendo una densità costante per la roccia.

Usarlo per "trovare strutture sepolte" significa quindi cercare, in un campo derivato dal DEM, una cosa che nel DEM non c'è. È **circolare**: alla scala fine restituisce il terreno che gli hai dato in pasto. È esattamente lo stesso peccato del DEM sintetico con la valle piantata, vietato da CLAUDE.md §0 — solo travestito meglio, perché stavolta il dato sintetico ha un nome accademico e una citazione.

Legale usarlo come contesto regionale. Vietato usarlo come rivelatore di massa sepolta.

## GRACE: misura la cosa giusta, nel secolo sbagliato

GRACE/GRACE-FO è l'unico che misura davvero *variazione* di massa — "adesso qui ce n'è meno di prima". Bellissimo, e serve a falde acquifere e calotte glaciali. Risoluzione ~200 km e serie che parte dal **2002**.

Per un evento di 12.000 anni fa non c'è niente da fare: lo strumento misura la derivata nel tempo, e del tempo che ci interessa non ha nemmeno un campione.

## L'unica cosa che la gravità farebbe per noi

Non trovare. **Pesare il riempimento di un bacino.**

Sedimento lacustre ha densità bassa; il basamento no. Un bacino riempito da sedimento dà un **minimo di Bouguer**, e la profondità di quel minimo è proporzionale allo spessore del riempimento. Su un bacino ≥20 km funziona, ed è informazione che il DEM **non contiene**: il DEM vede la superficie di oggi, la gravità vede quanto materiale c'è sotto.

Uso legittimo, con un ruolo preciso in questo progetto:

1. **Colonna** su un bacino già selezionato: quanto è stato bacino, per quanto tempo.
2. **Correzione a Merian**: `seiche.py` calcola il periodo dalla profondità d'acqua. Se un bacino ha 300 m di sedimento sopra il fondo roccioso, la profondità antica era maggiore e il periodo era **più corto** di quello che calcoliamo oggi dal DEM.
3. **Kill-shot** su affermazioni di strutture sepolte **grandi** (≥18 km): lì la gravità decide. Sotto quella soglia il suo silenzio non è prova di assenza, ed è scorretto citarlo come tale.

## Archivi verificati il 13/9/2026

| fonte | stato | cosa |
|---|---|---|
| ICGEM (`icgem.gfz-potsdam.de`, `icgem.gfz.de`) | **200** | catalogo modelli, coefficienti .gfc, servizio griglie. `harmonica.load_icgem_gdf` legge il formato |
| NOAA/NGDC gravity | **200** | dati marini e griglie |
| GGMplus (Curtin) | **200** | 200 m, ±60°, **corto sintetico dalla topografia** |
| BGI WGM2012 | **404** | indirizzo cambiato, non trovato |

## Stato

**Non scaricata, e la scelta è motivata.** Non abbiamo un bacino candidato: lo screening (`SCREENING-BACINI.md`) li ha azzerati tutti. Scaricare un campo gravimetrico globale senza un candidato su cui appoggiarlo sarebbe precisamente la caccia all'anomalia che il primo paragrafo vieta.

Quando un candidato ci sarà — un bacino ≥20 km, confinato, con orlo ripido, con riva abitabile nella finestra — la gravità è la seconda colonna da aggiungere, e questo file dice già come farlo e cosa non affermare.
