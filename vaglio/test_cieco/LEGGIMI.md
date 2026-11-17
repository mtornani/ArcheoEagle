Il test interno su Kiuic è chiuso (17 novembre 2026): sostituito da Vaglio–Chactún, che termina con la verifica di un archeologo.

# Test cieco con Britton: cosa fare, in ordine

Per Mirko. I documenti per Britton sono in inglese (`PREREGISTRATION.md`, `KEY_HOLDER_GUIDE.md`);
questa pagina dice cosa fare tu.

## 1. Sigilla il deposito, prima di scrivergli

Sul tuo PC, dove c'è la scansione completa:

```powershell
cd D:\AI\ArcheoEagle
git pull
cd vaglio
python -m unittest discover -s tests      # deve dire OK
python -m vaglio deposito
```

Il comando stampa un'impronta SHA-256 e il numero di righe (devono essere 11.916). Copia impronta,
righe, transetti e data nella tabella di `test_cieco/DEPOSIT.md`, poi:

```powershell
git add test_cieco/DEPOSIT.md
git commit -m "Test cieco: sigillo del deposito"
git push
```

Quel commit è il sigillo: da lì nessuno, nemmeno tu, può cambiare l'elenco senza che si veda.
Il file `vaglio_lavoro\deposito\deposito.csv` ha le coordinate: **non va nel repository, non va allegato
alla prima email.**

## 2. Scrivigli

Una sola email, con una sola richiesta. Bozza qui sotto: la qualifica e la firma sono tue, il resto puoi
accorciarlo ma non gonfiarlo. Se il repository è privato, allega la cartella `test_cieco` zippata
**senza** il CSV, invece dei link.

> **Subject:** Blind test of an independent re-analysis of your reprocessed G-LiHT transects
>
> Dear Dr Britton,
>
> I am Mirko Tornani, an independent researcher, not an archaeologist. With AI assistants (Claude, GPT)
> I built Vaglio, a small open tool that flags structure-shaped relief in your reprocessed G-LiHT
> transects and measures its own errors. On the Chactún annotations it recovers 76% of 942 held-out
> structures.
>
> Your catalogue is the only independent key for these data, so I would like to ask one thing: would you
> be willing to score Vaglio's output against it, blind? Everything is fixed in advance in a
> pre-registration, the deposit is sealed with a public SHA-256, and a standard-library Python script
> does the scoring in under a minute. You would receive our list privately and return only aggregate
> numbers; your catalogue never leaves your hands. A failed result will be published as well.
>
> Pre-registration and scorer: [link to vaglio/test_cieco in the repository]
>
> Thank you for your time, and for making the reprocessed data public.
>
> Mirko Tornani
> [contatti]

## 3. Se accetta

- Mandagli **in privato** `deposito.csv` (email o trasferimento file), più l'impronta di `DEPOSIT.md`.
- Lui sceglie l'area e le esclusioni prima di lanciare lo script, e ti rimanda `results.json`.
- Tu pubblichi l'esito nel rapporto, qualunque sia, con parole concordate con lui.

## 4. Se non risponde o rifiuta

Non si cambia niente del test. Si può proporre lo stesso pacchetto a un altro custode con un catalogo
indipendente di questi transetti (per esempio il gruppo di Estrada-Belli), aggiungendo una nota datata in
fondo a `PREREGISTRATION.md` prima del punteggio.

## Cosa non fare

- Non lanciare `score.py` tu con un catalogo qualsiasi per «vedere come va»: il test vale solo se la
  chiave la tiene un altro.
- Non rifare la scansione o cambiare parametri dopo il sigillo: sarebbe un nuovo deposito (v2).
- Non promettere coordinate a nessuno oltre al custode della chiave.
