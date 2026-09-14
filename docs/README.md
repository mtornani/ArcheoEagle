# Indice — parti da qui

Sedici documenti sono troppi per orientarsi. Questo è **l'unico punto d'ingresso**. Ordine di lettura: `CLAUDE.md` §0 (ordini permanenti, vincono su tutto), poi questa pagina, poi solo il file che ti serve.

## In una riga

Strumento forense per restringere **da casa** dove cercare un referente reale dietro il racconto di Atlantide. In cinque giorni ha prodotto **quattro "no" misurati e un "sì"**: il rilevatore di sponde, che ora funziona.

## Stato delle indagini

| pista | stato | cosa l'ha decisa |
|---|---|---|
| **A — carbone** | **chiusa** | Sr-Nd su ODP 658C: l'anomalia era un cambio di sorgente della polvere |
| **B — catastrofe** | **chiusa** | nessun deposito transatlantico; l'assenza mette un tetto alla taglia |
| **C — confinamento** | **parcheggiata** | il suo unico kill-shot non esiste nei bacini chiusi; il sostituto è da carota, non da casa |
| **Younger Dryas** | **anello del diluvio `−`** | il YD è il tratto più lento della deglaciazione, e MWP1A lo precede di 1750 anni |

## Il risultato che conta

**Il controllo positivo passa.** `CALIBRAZIONE.md` documentava otto rilevatori falliti sulla Bama Ridge e concludeva che il bersaglio fosse invisibile. Era un **errore di scala**: il rilevatore girava a 30 m nativi su un cordone di 8 m disteso su 1 km. A ~120 m di media d'area compare, con controllo negativo pulito.

Spiega anche perché l'hillshade lo trovava a occhio in un secondo: guardare un'immagine la rimpicciolisce — l'occhio faceva la media che il codice non faceva.

## Mappa dei file

**Leggi prima questi**

| file | cosa c'è |
|---|---|
| `../CLAUDE.md` | la spec. §0 vince su qualunque task |
| `STATO.md` | diario datato, il più recente in cima |
| `BERSAGLIO.md` | cosa stiamo cercando davvero, e la rubrica dei proxy |
| `CALIBRAZIONE.md` | gli otto rilevatori falliti e la diagnosi |

**Indagini**

| file | cosa c'è |
|---|---|
| `PISTA-A-carbone.md` | anomalia del carbone, chiusa |
| `PISTA-B-catastrofe.md` | frane e tsunami, chiusa |
| `PISTA-C-confinamento.md` | Dickson, seiche, confinamento — parcheggiata |
| `YOUNGER-DRYAS.md` | impatto cometario valutato nel ledger |
| `SCREENING-BACINI.md` | il Sahara non ha catini a pareti ripide |

**Metodo e strumenti**

| file | cosa c'è |
|---|---|
| `AUDIT-PARAMETRI.md` | i bug ricorrenti: metrica, scala, soglie. **Da rifare a ogni modulo nuovo** |
| `GRAVITA.md` | archivi verificati, e perché 9,1 km di risoluzione non bastano |
| `STRUMENTI-NON-USATI.md` | LiDAR, PALSAR e altri: valutati e scartati, con motivo |
| `CAROTE.md` | fonti verificate vive, con accessioni |
| `METODO-PIATTAFORMA.md` | criteri per le piattaforme sommerse |
| `GEOLIBRE.md` | il GIS. Non forkarlo |

**Round esterni**

| file | cosa c'è |
|---|---|
| `PROMPT-DEEP-RESEARCH.md` | il prompt: chiedi falsificatori, non conferme |
| `GEMINI-ROUND-1.md` | round 1 valutato: 2 affermazioni su 8 non hanno retto |
| `gemini-round-1-integrale.txt` | il report grezzo |

## Le tre regole che costano di più se le ignori

1. **Non riaprire A o B raccontandole meglio.** Servono misure nuove, e sono in archivio a Brema.
2. **Non usare la gravità come ricerca**, e non usare GGMplus per massa sepolta: le sue lunghezze corte sono modellate dalla topografia, quindi è circolare.
3. **Un modulo nuovo che tocca un DEM dichiara tre cose**: se converte i pixel in metri, a quale scala analizza, se le sue soglie sono adimensionali. Vedi `AUDIT-PARAMETRI.md`.

## Avvio

```bash
cd backend && python -m unittest discover -s tests -v   # deve restare verde
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```
