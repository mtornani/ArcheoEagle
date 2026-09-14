# Audit dei parametri condivisi — 14 settembre 2026

**Perché esiste.** Due bug sono stati trovati per caso in quattro giorni, e sono la stessa specie: *un parametro trattato bene in un modulo e male o per niente in un altro*.

1. **9 set** — metrica sferica: `control.py` convertiva i pixel in metri, `basin.py` no. Scoperto perché uno screening dava 0,9–1,0 ovunque.
2. **14 set** — scala di analisi: il rilevatore girava a 30 m nativi su un cordone che vive a ~120 m. Scoperto **verificando tutt'altro** (un'affermazione di Gemini sulla quota della Bama Ridge).

Due volte per fortuna è una scommessa, non un metodo. Questa è la tabella, e va rifatta quando si aggiunge un modulo.

## Tabella

| modulo | metrica sferica | scala d'analisi | soglia adimensionale | esito |
|---|---|---|---|---|
| `hydro/control.py` | sì (`pixel_metres`) | **sì** (`coarsen`, `multiscale_step_score`) | — | a posto |
| `hydro/measure.py` | sì (`_coarsen_to_scale`) | **sì** (media d'area a 120 m) | — | a posto, dal 14/9 |
| `marine/basin.py` | sì (`px_m`/`py_m`, dal 13/9) | **no** | `steep=0.30` | **dipendenza dichiarata, non corretta** |
| `marine/shelf.py` | n/a | n/a | `SLOPE_MAX=0.05` | a posto: la pendenza **la riceve**, non la calcola |
| `marine/seiche.py` | sì (`px_m`/`py_m` espliciti) | n/a | — | a posto |

## Il caso aperto: `basin.py`

`collapse_source_potential` misura la pendenza alla risoluzione che riceve, e la soglia 0,30 non lo sa. Un versante dolce e lungo sembra più ripido a 30 m che a 240 m.

**Non l'ho corretto nel codice**, e la ragione è che la conclusione che ne dipende — *il Sahara non ha catini a pareti ripide* — è stata verificata ai due estremi invece che assunta:

| | risoluzione | orlo ripido |
|---|---|---|
| Qattara | 27 m | 0,0 |
| Qattara | 240 m | 0,0 |
| Sognefjord (controllo +) | 118 m | 0,356 |

La conclusione regge a entrambi gli estremi. La dipendenza è ora scritta nel docstring: **chi cambia la risoluzione d'ingresso deve rifare quella verifica, non fidarsi del numero.**

Correggerla davvero significherebbe portare `multiscale_step_score` dentro `basin.py` — lavoro giusto, ma non necessario finché nessuna conclusione ci poggia sopra senza verifica.

## Il caso chiuso male: `shelf.py`

Sembrava un bug (soglia adimensionale, nessuna metrica in metri) ed è invece una **delega dichiarata**: `coastal_residence_kyr` e `shelf_cell` ricevono `slope` come float dal chiamante. La responsabilità è di chi chiama. Nessun chiamante attuale la calcola da un DEM, quindi nessun errore in circolo — ma il primo che lo farà deve usare metrica e scala corrette.

## Regola

Un modulo nuovo che tocca un DEM dichiara, nel docstring di testata, **tre cose**: se converte i pixel in metri, a quale scala analizza, e se le sue soglie sono adimensionali. Se una manca, va scritto perché — come qui sopra per `basin.py`.
