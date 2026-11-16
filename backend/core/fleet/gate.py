"""Cancello della flotta: decide se una segnalazione merita una seconda verifica.

Gli agenti esploratori (scout) non scrivono "anomalie": propongono segnalazioni.
Questa funzione, deterministica e senza rete, e' l'unico modo di entrare in coda.

Perche' esiste: piu' agenti x piu' banche dati = piu' falsi positivi. Un massimo
interno esiste sempre (docs/CALIBRAZIONE.md, otto tentativi). Quindi:

- senza controllo positivo passato  -> NON_CALIBRATO (rumore indistinguibile)
- senza null, o p * n_tested > ALPHA -> SOTTO_IL_CASO (esito onesto, pubblico)
- testo / letteratura                -> COLONNA (mai in coda da solo)
- VERIFICA_APPROFONDITA solo se un agente DIVERSO, con una sorgente DIVERSA,
  ha provato a uccidere la segnalazione e non c'e' riuscito.

Nessun esito di questo file significa "trovato".
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple

ALPHA = 0.05  # dopo correzione per confronti multipli (Bonferroni: p * n_tested)

TIPI = {
    "hydro", "rs", "terrain", "radar", "literature", "plato_text",  # CLAUDE.md §5
    "seismic", "sealevel", "core", "dating",                        # §12
}
TIPI_TESTO = {"literature", "plato_text"}  # colonna, non stampo

# Trappole note (docs/MONDO-12KA.md). Non si "fixano": si rifiutano.
TRAPPOLE = ("richat", "bimini", "yonaguni", "gunung padang")
VIETATE = ("atlantide found", "atlantis found", "scoperta confermata",
           "sponda individuata", "sembra un anello")

# Campi che restano sul device. Mai nel pack cieco.
LOCALI = {"where", "lon", "lat", "bbox", "place", "river_name"}

RESPINTO = "RESPINTO"
NON_CALIBRATO = "NON_CALIBRATO"
SOTTO_IL_CASO = "SOTTO_IL_CASO"
COLONNA = "COLONNA"
SECONDA_VERIFICA = "SECONDA_VERIFICA"
VERIFICA_APPROFONDITA = "VERIFICA_APPROFONDITA"
FAIL = "FAIL"

VERDETTI = {"sopravvive", "ucciso", "aperto"}


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def flag_id(flag: Dict[str, Any]) -> str:
    """Id stabile dal contenuto: stessa segnalazione, stesso id (dedup)."""
    core = {k: v for k, v in flag.items() if k not in ("id", "grade", "reasons")}
    return hashlib.sha256(_canonical(core).encode("utf-8")).hexdigest()[:12]


def _text(x: Any) -> str:
    return x.strip() if isinstance(x, str) else ""


def triage(flag: Dict[str, Any], sources: Dict[str, Dict[str, Any]]) -> Tuple[str, List[str]]:
    """Ritorna (esito, motivi). `sources` = registro indicizzato per id."""
    why: List[str] = []

    # --- 1. Completezza (CLAUDE.md §5: una riga e' prova solo con tutti i campi)
    for k in ("agent", "claim", "source_ref", "can_say", "cannot_say", "kill_shot"):
        if not _text(flag.get(k)):
            why.append(f"campo mancante: {k}")
    if flag.get("tipo") not in TIPI:
        why.append(f"tipo non valido: {flag.get('tipo')!r}")
    measure = flag.get("measure") or {}
    if not isinstance(measure.get("value"), (int, float)) or not _text(measure.get("unit")):
        why.append("misura mancante: measure.value numerico + measure.unit")

    blob = _canonical(flag).lower()
    for w in VIETATE:
        if w in blob:
            why.append(f"stringa vietata: {w!r}")
    for t in TRAPPOLE:
        if t in blob:
            why.append(f"trappola: {t}")

    src = sources.get(flag.get("source_id") or "")
    if src is None:
        why.append(f"sorgente non in registro: {flag.get('source_id')!r}")
    elif src.get("status") == "dead":
        why.append(f"sorgente morta: {src['id']}")
    elif src.get("role", "detector") != "detector":
        # geologia, faglie, magnetico, moderno, cataloghi: servono a uccidere, non a segnalare
        why.append(f"sorgente {src['id']} ha ruolo {src['role']}: non e' un rilevatore")

    # Metodo v1 #1 e #3: l'area viene dai dati, il mito si guarda dopo.
    if flag.get("tipo") not in TIPI_TESTO and flag.get("myth_blind") is not True:
        why.append("myth_blind non dichiarato: il candidato deve venire dal dato, non dal mito")

    if why:
        return RESPINTO, why

    # --- 2. Testo: colonna + / - / N/A, non segnalazione
    if flag["tipo"] in TIPI_TESTO:
        return COLONNA, ["testo e letteratura sono colonna: non entrano in coda da soli"]

    # --- 3. Lo strumento sa riconoscere un caso noto?
    control = flag.get("control") or {}
    if not _text(control.get("name")) or control.get("passed") is not True:
        return NON_CALIBRATO, [
            "controllo positivo assente o fallito: un punteggio alto e' rumore "
            "che non sappiamo distinguere"
        ]
    if src.get("status") != "ok":
        return NON_CALIBRATO, [f"sorgente {src['id']} non verificata dal vivo (status={src.get('status')})"]

    # --- 4. Sopra il caso, contando quante cose hai guardato
    null = flag.get("null") or {}
    p, n = null.get("p"), null.get("n_tested")
    if not _text(null.get("description")) or not isinstance(p, (int, float)) \
            or not isinstance(n, int) or n < 1 or not (0 <= p <= 1):
        return SOTTO_IL_CASO, ["null assente o incompleto (description, p, n_tested): senza null non c'e' anomalia"]
    if p * n > ALPHA:
        return SOTTO_IL_CASO, [f"p*n_tested = {p * n:.3g} > {ALPHA}: niente sopra il caso"]

    return SECONDA_VERIFICA, [f"p*n_tested = {p * n:.3g} <= {ALPHA}, controllo '{control['name']}' passato"]


def apply_review(flag: Dict[str, Any], review: Dict[str, Any],
                 sources: Dict[str, Dict[str, Any]]) -> Tuple[Optional[str], List[str]]:
    """Seconda verifica. Ritorna (nuovo esito | None se la revisione non vale, motivi)."""
    if flag.get("grade") not in (SECONDA_VERIFICA, VERIFICA_APPROFONDITA):
        return None, [f"si rivede solo cio' che e' in coda (esito attuale: {flag.get('grade')})"]
    if review.get("verdict") not in VERDETTI:
        return None, [f"verdetto non valido: {review.get('verdict')!r}"]
    if not _text(review.get("reviewer")) or not _text(review.get("reason")):
        return None, ["revisione senza reviewer o senza motivo"]
    # Operatore != peer
    if review["reviewer"] == flag.get("agent"):
        return None, ["chi segnala non si rivede da solo"]

    if review["verdict"] == "ucciso":
        return FAIL, [review["reason"]]
    if review["verdict"] == "aperto":
        return SECONDA_VERIFICA, [review["reason"]]

    # "sopravvive" vale solo con un dato indipendente, verificato dal vivo
    ind = sources.get(review.get("independent_source_id") or "")
    if ind is None or ind.get("status") != "ok":
        return SECONDA_VERIFICA, ["sopravvive senza sorgente indipendente verificata: resta aperto"]
    if ind["id"] == flag.get("source_id"):
        return SECONDA_VERIFICA, ["stessa sorgente della segnalazione: non e' indipendente, resta aperto"]
    return VERIFICA_APPROFONDITA, [review["reason"]]


def blind_view(flag: Dict[str, Any]) -> Dict[str, Any]:
    """Riga pubblicabile: niente coordinate, niente toponimi locali."""
    return {k: v for k, v in flag.items() if k not in LOCALI}


def make_blind_pack(flags: List[Dict[str, Any]], timestamp: str) -> Dict[str, Any]:
    """Stesso schema di ledger/blind.py: hash = priorita', non prova."""
    rows = [blind_view(f) for f in flags]
    payload = {"algorithm": "sha256", "flags": rows, "timestamp": timestamp}
    return {**payload, "hash": hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()}
