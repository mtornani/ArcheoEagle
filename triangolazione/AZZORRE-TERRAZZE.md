# Azzorre — il ciglio della piattaforma insulare. 9 novembre 2026.

Tesi nel ledger (Randall Carlson): l'altopiano delle Azzorre e' sprofondato a fine glaciazione (~11.6 ka).
Previsione, metodo e kill-shot: `PREREG-AZZORRE.md` (SHA-256 in `PREREG-AZZORRE.sha256`), scritti prima di scaricare le isole.
Dato: EMODnet Bathymetry, ~115 m. Codice: `tools/azzorre_ciglio.py`. Numeri: `dati/azzorre_ciglio.json`.

## Risultato

| unita' | ciglio (m) | sprofondamento netto implicato (ciglio - 130) |
|---|---|---|
| Corvo | -100 | nessuno |
| Santa Maria | -130 | 0 |
| Sao Miguel | -150 | ~20 m |
| Pico-Faial | -160 | ~30 m |
| Sao Jorge | -170 | ~40 m |
| Flores | -170 | ~40 m |
| Graciosa | -250 | ~120 m |
| Terceira | -330 | ~200 m |

Mediana del ciglio: **-165 m** -> sprofondamento netto mediano ~35 m. Alla tesi ne servono ~1000.

| | esito |
|---|---|
| C1 controllo: ciglio di Santa Maria in [-90, -170] | PASSA (-130) |
| C2 controllo debole: classi di area massima nelle bande pubblicate | 3 su 3 (per caso riesce 1 volta su 2: non decide) |
| P1: ciglio in [-80, -180] per almeno 6 unita' su 8 | PASSA, al limite (6 su 8) |
| P2: nessun ciglio oltre -300 m | **FALLISCE** (Terceira -330) |

## Lettura, con la regola fissata prima
Mediana < 100 m => la riga "Azzorre sprofondate a 11.6 ka" prende **-**.
P2 e' fallita e resta agli atti: Terceira e Graciosa hanno il ciglio piu' profondo del previsto.
Anche nel caso peggiore (Terceira, 200 m) manca un fattore 5 rispetto a quanto serve.

Nota a posteriori, NON valida come prova: su Terceira e Graciosa la pendenza resta bassa (2-4 gradi) fino a
-200 m e oltre, quindi la soglia "2 volte" scatta tardi. Possibili cause: dorsali vulcaniche sottomarine dentro la
componente connessa, subsidenza locale vera, o regola inadatta a piattaforme larghe. La regola NON e' stata ritoccata.

## Limiti
- Piattaforme poligeniche; ciglio ritoccato da lave e sedimenti; 115 m non risolve terrazze strette.
- Limita il movimento NETTO dall'ultimo stazionamento basso, non oscillazioni che si annullano.
- Classi di 10 m: la precisione sul ciglio e' +-10 m nel migliore dei casi.

## Ledger Carlson (lente, non oracolo — CLAUDE.md §2.3)

| tesi | esito | perche' |
|---|---|---|
| Megainondazioni di fine glaciazione (Scablands) | + | misurate, letteratura consolidata |
| Azzorre sprofondate a 11.6 ka | - | questo test; Santa Maria in sollevamento (Ramalho et al. 2017); altopiano di 10-4 Ma (Storch et al. 2020) |
| Impatto a 12.9 ka | N/A | contestata (Holliday et al. 2023 contro; Sweatman et al. 2024 replica); non decidibile da casa |
| Civilta' glaciale sulle Azzorre | - | prima traccia umana proposta 700-850 d.C. (Raposeiro et al. 2021, contestata) |
| Metodo: acqua prima, forma dopo la misura | + | e' quello che ha fatto passare il tentativo 11 |
