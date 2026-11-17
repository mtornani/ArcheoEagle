# Vaglio

Dal LiDAR pubblico a un fascicolo di candidati archeologici, **con gli errori misurati**.

Funziona da casa, su un portatile, senza chiavi e senza GPU. Non trova città perdute:
mette in fila i punti dove il terreno ha la forma di una costruzione, dice quanto
sbaglia nel farlo, e ti ricorda chi ha già guardato lì prima di te.

## Perché esiste

A novembre 2026 un ricercatore ha fatto guardare a 48 agenti AI 1.200 km² di LiDAR
NASA sullo Yucatán e ha annunciato un sito maya «non mappato». Era già pubblicato
(Estrada-Belli et al. 2025). Il metodo funzionava; mancavano tre cose:

| Mancava | Vaglio |
|---|---|
| Quanto sbaglia il rilevatore | Misurato su 329 riquadri annotati da archeologi, mai visti in addestramento, con criteri scritti prima |
| Quanto sbagliano gli agenti | Ogni pacco di revisione contiene controlli piantati a risposta nota; chi li sbaglia non vota |
| Chi l'aveva già trovato | Ogni candidato su un rilievo già studiato si presume già visto; «non nel registro» ≠ «sconosciuto» |

## Cosa è stato misurato (16 nov 2026)

| Misura | Esito |
|---|---|
| Rilevatore su 329 riquadri di Chactún mai visti (942 strutture annotate) | ritrova il 76%; l'83% di ciò che segnala è una struttura annotata. Criterio (≥70% entrambe) scritto prima: **passa** |
| Revisori (3 agenti, secondo giro) sui controlli piantati | riconoscono il 30–40% degli edifici noti, scartano 10 vuoti su 10, accordo fra loro 90–97% |
| Conseguenza | un revisore così può **confermare** ma non **scartare**: il suo «naturale» non prova niente |
| Yucatán, primi 44 transetti (137 km² su 1.273) | 1.149 complessi candidati; rivisti 40 |
| Yucatán, scansione completa (456 transetti; 1.272,7 km²) | 11.916 complessi candidati; 15 reggono, 25 incerti, 11.876 da rivedere, 0 scartati |
| Dei 20 col punteggio più alto **in quel momento** (primi 40 transetti, un solo blocco) | 12 reggono alla revisione |
| Dei 20 presi a caso dal resto | 3 reggono alla revisione |
| Nella scansione completa, dei primi 100 candidati per punteggio | ne sono stati rivisti 3: il resto è da fare |
| Uso del suolo di oggi, sui 1.548 candidati dei primi 51 transetti | 11 sotto «costruito»: a vista, tutte strade asfaltate |

La scansione completa è stata chiusa il 16 nov 2026. Il pack cieco verificabile e senza
coordinate è versionato in `pack_cieco.json`; il dossier con coordinate resta locale.

Il primo giro di revisione è stato annullato: i controlli positivi erano tagliati sul bordo del
riquadro e i revisori, giustamente, vedevano terreno vuoto. Il difetto era nel controllo.
Nessun candidato è stato confrontato con il catalogo Britton 2026, che non è pubblico.

## Uso

```bash
pip install -r requirements.txt
python -m vaglio catalogo                                   # 456 transetti, 1.273 km², 31 GB
python -m vaglio scansiona --transetti South_GLAS_l3s459    # 1-2 minuti a transetto
python -m vaglio scansiona --tutti                          # tutto lo Yucatán (~4 ore su 4 core con --parte 1/4 … 4/4); riprende da dove si era fermato
python -m vaglio scansiona --dtm mio_rilievo.tif            # un tuo DTM di terreno nudo, in metri
python -m vaglio pacco --top 60                             # immagini anonime + controlli piantati
python -m vaglio esiti pacco-1 claude=a.json grok=b.json    # pesa i revisori, conta i voti
python -m vaglio impara                                     # (quando ci sono abbastanza tenuti e scartati) riordina la coda
python -m vaglio moderno                                    # cosa c'è oggi sopra ogni candidato (ESA WorldCover)
python -m vaglio dossier                                    # dossier.html + pack_cieco.json + candidati.csv + candidati.geojson
python -m vaglio verifica pack_cieco.json                   # controlla un pack ricevuto: firma e nessuna posizione
python -m vaglio kit                                        # numeri e figure senza posizioni, per chi scrive i materiali
python -m vaglio controlla testo.md                         # un testo pronto a uscire: niente coordinate, niente annunci
```

I file locali finiscono in `./vaglio_lavoro/`. **Contiene coordinate: resta sul tuo dispositivo.**
Da condividere c'è solo `pack_cieco.json` (niente coordinate, SHA-256); il pack della scansione
completa è pubblicato in `./pack_cieco.json`.

Per scrivere rapporti, lettere e presentazioni: `materiali/FATTI.md` (i fatti e il loro grado) e
`materiali/ISTRUZIONI.md` (cosa produrre, per chi, con quali parole).
Scheda web mobile in italiano, inglese e spagnolo: `materiali/uscite/scheda-trilingue.html`.
Rapporto web completo in italiano e inglese: `materiali/uscite/rapporto/index.html`, rigenerabile con
`python materiali/uscite/rapporto/build.py` (si ferma se i numeri del testo non tornano col pack cieco).
Pagina per il pubblico, da condividere anche su WhatsApp: `materiali/uscite/pubblico/index.html`
(«Sotto la foresta»), rigenerabile con `python materiali/uscite/pubblico/build.py`.
PDF scaricabili delle due pagine in `materiali/uscite/pdf/`; si rigenerano con `node esporta_pdf.js`
da `materiali/uscite/` (serve Playwright).

## Come funziona

1. **Rilievo.** Dal DTM calcola sky-view factor, apertura positiva e pendenza con gli stessi
   parametri di Kokalj et al. 2023 (`relief.py`). Solo numpy.
2. **Rilevatore.** Un classificatore a gradient boosting, per pixel, su contesto locale a più
   scale (`model.py`). Addestrato su Chactún. Piccolo, trasparente, gira su CPU.
3. **Complessi.** Rilievi entro 60 m diventano un complesso: è l'unità che si rivede (`scan.py`).
4. **Revisione al buio.** I candidati vengono mescolati a controlli noti e mostrati senza nome
   né posizione a più revisori — agenti Claude Code (`vaglio-revisore`), Grok, ChatGPT, persone.
   Serve una cartella di immagini e una rubrica; torna un JSON (`review.py`).
5. **Già noto.** Confronto con elenchi di siti e con la lista di chi ha già analizzato il rilievo
   (`known.py`). Aggiungi i tuoi elenchi come CSV `name,lat,lon,source` in `vaglio_lavoro/known/`.
6. **Fascicolo.** Un file HTML offline, pensato per il telefono (`report.py`).

## Esiti possibili di un candidato

`da_rivedere` · `incerto` · `scartato` · `regge_alla_revisione`. Nessuno significa «trovato».
Quello che regge alla revisione è una forma che almeno due revisori, affidabili nel dire
«struttura», riconoscono come costruita. Che sia antica, e che sia nuova, lo dice solo un sopralluogo autorizzato.

## Cosa non fa

- Non vede sotto una chioma che il LiDAR non ha attraversato: dove mancano punti a terra, il DTM è inventato dall'interpolazione.
- Non distingue antico da moderno con certezza. Un argine o una cava hanno lati dritti.
- Non sostituisce il catalogo di chi quei dati li ha prodotti. Sullo Yucatán esiste un catalogo di 57.181 strutture (Britton 2026) non pubblico: un candidato di Vaglio lì è quasi certamente già dentro.
- Non pubblica coordinate.

## Dati e licenze

- LiDAR: NASA G-LiHT 2013 (AMIGA-Carb), riprocessato da B. J. Britton (2026), OpenTopography,
  doi:10.5069/G9Z899N1 e doi:10.5069/G9TH8JX9, PDDL.
- Addestramento e controlli: Kokalj, Džeroski, Šprajc et al. 2023, *Sci Data* 10:558,
  doi:10.6084/m9.figshare.22202395, CC BY 4.0. I riquadri in `vaglio/data/controls/` derivano da lì.
- Siti noti forniti: Wikidata (CC0).

## Test

```bash
python -m unittest discover -s tests
```
