"""Revisione visiva al buio, con controlli piantati.

Il punto debole di chi fa "48 agenti guardano le immagini": nessuno sa quanto
sbagliano. Qui ogni pacco mescola ai candidati dei riquadri di CONTROLLO di cui
la risposta e' nota (Chactun, annotati da archeologi, mai usati per addestrare).
Chi rivede non sa quali sono. Un revisore che sbaglia i controlli non vota.

I controlli positivi sono CENTRATI su un edificio annotato di almeno 100 m2,
come i candidati sono centrati sul loro rilievo. Il primo giro (16 nov 2026)
usava quadranti fissi: meta' delle strutture finiva tagliata sul bordo e tre
revisori su tre, correttamente, vedevano "piano vuoto". Controllo sbagliato,
non revisore sbagliato: giro annullato e rifatto.

EMENDAMENTO (16 nov 2026, dopo il secondo giro, dichiarato post-hoc).
Secondo giro, controlli centrati, tre agenti nuovi: riconoscono il 30-40% degli
edifici annotati (quelli a lati netti; i tumuli erosi no) e scartano 10 vuoti su
10. Accordo fra loro 90-97%. Non si ritoccano i controlli finche' "passano".
Si prende atto che l'errore e' asimmetrico e lo si tratta come tale:
  - chi scarta bene i vuoti (specificita' >= MIN_SPEC) puo' CONFERMARE;
  - chi trova le strutture note (sensibilita' >= MIN_SENS) puo' SCARTARE.
Un revisore prudente dice il vero quando dice "struttura"; il suo "naturale"
non prova niente. Limite: 10 controlli negativi per pacco sono pochi.

Il revisore puo' essere un agente Claude Code, Grok, ChatGPT o una persona:
riceve una cartella di immagini e una rubrica, restituisce un JSON.
"""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict, List

VERDICTS = ("struttura", "naturale", "moderno", "artefatto", "incerto")
MIN_SENS = 0.70      # puo' SCARTARE solo chi sui controlli trova almeno il 70% delle strutture
MIN_SPEC = 0.70      # puo' CONFERMARE solo chi scarta almeno il 70% dei riquadri vuoti
MIN_CONTROLS = 10    # e ne ha visti abbastanza per dirlo
CONTROLS = Path(__file__).resolve().parent / "data" / "controls"

RUBRICA = """# Rubrica di revisione — Vaglio

Ogni immagine e' un riquadro di 120 x 120 m di terreno nudo (LiDAR, vegetazione
rimossa). Chiaro = piano e aperto. Scuro = pendio, bordo, incavo.
Alcune immagini sono controlli di cui la risposta e' nota. Non sai quali.

Per ogni immagine scegli UN verdetto:

- `struttura`  — rilievo costruito antico: tumulo o piattaforma a pianta
  rettangolare o quadrata, lati dritti, angoli; piu' corpi allineati o attorno
  a uno spazio piano (corte, piazza); gradoni.
- `naturale`   — collina o cresta carsica dai bordi irregolari, dolina (incavo
  tondo), affioramento, alveo, versante. Forme senza angoli e senza allineamenti.
- `moderno`    — strada o pista (linea lunga e regolare), campo arato (righe
  parallele), argine, fosso, edificio recente, cava.
- `artefatto`  — difetto del dato: bordo del rilievo, cucitura, facce
  triangolari piatte dove mancano punti a terra, righe di scansione.
- `incerto`    — non si distingue. E' una risposta legittima: usala.

Regole:
1. Giudica solo quello che vedi. Non sai dove sia il riquadro e non ti serve.
2. Un singolo dosso tondo senza lati dritti NON e' `struttura`.
3. Se la forma regolare e' una sola linea lunga, e' `moderno`, non `struttura`.
4. Nel dubbio fra `struttura` e altro: `incerto`.

Rispondi con un file JSON, una riga per immagine:

    [{"item": "r_0001", "verdict": "naturale", "confidence": 0.8,
      "note": "dolina tonda, nessun lato dritto"}, ...]
"""


def make_pack(cands: List[Dict[str, Any]], chips: Path, out: Path, name: str,
              n_controls: int = 30, seed: int = 0) -> Dict[str, Any]:
    """Scrive out/<name>/ (immagini anonime + rubrica) e la chiave in out/keys/<name>.json."""
    import shutil

    rng = random.Random(seed)
    ctrl = sorted(CONTROLS.glob("*.jpg"))
    pos = [c for c in ctrl if c.name.startswith("pos_")]
    neg = [c for c in ctrl if c.name.startswith("neg_")]
    picked = rng.sample(pos, min(len(pos), n_controls // 2)) + rng.sample(neg, min(len(neg), n_controls - n_controls // 2))
    items = [("cand", c["id"], chips / f"{c['id']}.jpg") for c in cands if (chips / f"{c['id']}.jpg").exists()]
    items += [("pos" if p.name.startswith("pos_") else "neg", p.stem, p) for p in picked]
    rng.shuffle(items)
    folder = out / name
    folder.mkdir(parents=True, exist_ok=True)
    key = {}
    for k, (kind, ref, src) in enumerate(items, 1):
        item = f"r_{k:04d}"
        shutil.copyfile(src, folder / f"{item}.jpg")
        key[item] = {"kind": kind, "ref": ref}
    (folder / "RUBRICA.md").write_text(RUBRICA, encoding="utf-8")
    (folder / "risposte_modello.json").write_text(
        json.dumps([{"item": i, "verdict": "", "confidence": 0.0, "note": ""} for i in sorted(key)], indent=1), encoding="utf-8")
    (out / "keys").mkdir(exist_ok=True)
    (out / "keys" / f"{name}.json").write_text(json.dumps(key), encoding="utf-8")
    return {"pack": str(folder), "items": len(key), "candidates": sum(v["kind"] == "cand" for v in key.values()),
            "controls": sum(v["kind"] != "cand" for v in key.values())}


def grade_reviewer(key: Dict[str, Dict[str, str]], answers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Quanto vale questo revisore, misurato sui controlli che non sapeva di avere."""
    a = {r["item"]: r.get("verdict") for r in answers}
    pos = [a.get(i) for i, v in key.items() if v["kind"] == "pos" and a.get(i) in VERDICTS]
    neg = [a.get(i) for i, v in key.items() if v["kind"] == "neg" and a.get(i) in VERDICTS]
    out: Dict[str, Any] = {"n_pos": len(pos), "n_neg": len(neg)}
    if len(pos) + len(neg) < MIN_CONTROLS or not pos or not neg:
        return {**out, "calibrated": False, "can_confirm": False, "can_discard": False, "why": "troppo pochi controlli valutati"}
    out["sensitivity"] = round(sum(v == "struttura" for v in pos) / len(pos), 3)
    out["specificity"] = round(sum(v != "struttura" for v in neg) / len(neg), 3)
    out["can_confirm"] = bool(out["specificity"] >= MIN_SPEC)   # il suo "struttura" vale
    out["can_discard"] = bool(out["sensitivity"] >= MIN_SENS)   # il suo "non struttura" vale
    out["calibrated"] = out["can_confirm"] and out["can_discard"]
    return out


NO = ("naturale", "moderno", "artefatto")


def tally(votes: List[Dict[str, Any]], reviewers: Dict[str, Dict[str, Any]]) -> str:
    """Esito di un candidato. Ogni voto conta solo nella direzione in cui chi lo da' e' affidabile. Mai 'trovato'."""
    if not votes:
        return "da_rivedere"
    conf = [v["verdict"] for v in votes if reviewers[v["reviewer"]].get("can_confirm")]
    disc = [v["verdict"] for v in votes if reviewers[v["reviewer"]].get("can_discard")]
    yes = sum(v == "struttura" for v in conf)
    no = sum(v in NO for v in disc)
    if len(conf) >= 2 and yes >= 2 and yes / len(conf) >= 2 / 3:
        return "regge_alla_revisione"
    if len(disc) >= 2 and no >= 2 and no / len(disc) >= 2 / 3:
        return "scartato"
    return "incerto"


def ingest(key: Dict[str, Dict[str, str]], by_reviewer: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Unisce le risposte di piu' revisori. Ritorna {reviewers, candidates}."""
    reviewers = {name: grade_reviewer(key, ans) for name, ans in by_reviewer.items()}
    cands: Dict[str, Dict[str, Any]] = {}
    for name, ans in by_reviewer.items():
        for r in ans:
            k = key.get(r.get("item", ""))
            if not k or k["kind"] != "cand" or r.get("verdict") not in VERDICTS:
                continue
            cands.setdefault(k["ref"], {"all_votes": []})["all_votes"].append(
                {"reviewer": name, "verdict": r["verdict"], "confidence": r.get("confidence"), "note": r.get("note", "")})
    for c in cands.values():
        c["outcome"] = tally(c["all_votes"], reviewers)
    return {"reviewers": reviewers, "candidates": cands}
