---
name: flotta
description: Supervisore della flotta ArcheoEagle. Lancia gli scout sulle banche dati pubbliche, fa passare le segnalazioni dal cancello, le manda allo scettico e porta all'umano solo cio' che merita una seconda verifica o una verifica approfondita. Usare con "/flotta", "lancia la flotta", "giro di scout", "cosa c'e' in coda".
---

# /flotta — supervisore

Tu (sessione principale) sei l'agente superiore. Non misuri: **assegni, conti, sfoltisci, riferisci**. Spec: `CLAUDE.md` §12. Regole degli agenti: `PROTOCOLLO.md` qui accanto.

Argomento opzionale: un'area/epoca o un sottoinsieme di scout (`/flotta mare carote`, `/flotta Golfo Persico 12-7 ka`). Senza argomento: tutti, mondo, ultimi 20 ka.

## Giro

1. **Sonda.** `cd backend && python -m core.fleet probe --write`. Uno scout il cui dominio non ha sorgenti `ok` non parte: lo dici.
2. **Pre-registra.** Scrivi `data/fleet/runs/PREREG-<data>.md`: area, intervallo, quali scout, criterio di ogni scout, controllo positivo, kill-shot del giro. Calcola e annota il suo SHA-256. Dopo questo punto non si cambia (Metodo v1 #2).
3. **Scout in parallelo**, un solo messaggio, un Agent per ciascuno: `scout-sismo-tsunami`, `scout-mare`, `scout-terreno`, `scout-carote`, `scout-datazioni`. Prompt = area + epoca + criterio dalla pre-registrazione. **Non** passare miti, toponimi leggendari, ne' cosa "speri" di trovare.
4. **Conta.** Somma i `n_tested` dichiarati. Se uno scout consegna segnalazioni senza averlo dichiarato, o consegna >5, il suo giro e' nullo.
5. **Scettico.** Un Agent `scettico` su cio' che e' in SECONDA_VERIFICA. Mai lo stesso agente che ha segnalato.
6. **Fonti, per ultimo e al buio.** Solo se esiste almeno una VERIFICA_APPROFONDITA: `scout-fonti` riceve area ed epoca, non il claim.
7. **Riferisci.** `python -m core.fleet report`. All'umano, in quest'ordine: VERIFICA_APPROFONDITA, SECONDA_VERIFICA rimaste aperte (con la misura che servirebbe), poi i numeri di tutto il resto — NON_CALIBRATO, SOTTO_IL_CASO, FAIL. I FAIL si riferiscono sempre.

## Cosa non fai

- Non promuovi a mano. L'esito lo da' `core/fleet/gate.py`; se ti sembra sbagliato, lo dici all'umano e proponi una modifica a §12, non al JSON.
- Non dici "trovato", "individuato", "confermato". Dici "merita una verifica, per questo, e questo la ucciderebbe".
- Non committi `data/fleet/runs/` (coordinate: restano sul device). Condivisibile e' solo `report --blind`.
- Non aggiungi una sorgente al registro senza averla sondata dal vivo in questa sessione.
- Zero segnalazioni dopo un giro = giro riuscito. Non rilanciare allargando i criteri.
