"""CLI della flotta. Uso (da backend/):

    python -m core.fleet sources              # registro banche dati
    python -m core.fleet probe [--write]      # sonda dal vivo, aggiorna status
    python -m core.fleet submit flag.json     # uno scout propone (anche '-' = stdin)
    python -m core.fleet review review.json   # lo scettico rivede
    python -m core.fleet report [--blind]     # cosa arriva all'umano

La coda sta in data/fleet/runs/queue.jsonl: ha coordinate, resta sul device
(gitignored). `report --blind` e' la sola vista condivisibile.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from . import gate

ROOT = Path(__file__).resolve().parents[3]
SOURCES = ROOT / "data" / "fleet" / "sources.json"
QUEUE = ROOT / "data" / "fleet" / "runs" / "queue.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_sources(path: Path = SOURCES) -> Dict[str, Dict[str, Any]]:
    return {s["id"]: s for s in json.loads(path.read_text(encoding="utf-8"))["sources"]}


def load_queue(path: Path = QUEUE) -> Dict[str, Dict[str, Any]]:
    """Rigioca il log append-only: l'ultimo evento per id vince."""
    flags: Dict[str, Dict[str, Any]] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                f = json.loads(line)
                flags[f["id"]] = f
    return flags


def _append(flag: Dict[str, Any], path: Path = QUEUE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(flag, ensure_ascii=False, sort_keys=True) + "\n")


def _read_json(arg: str) -> Any:
    raw = sys.stdin.read() if arg == "-" else Path(arg).read_text(encoding="utf-8")
    return json.loads(raw)


def submit(flag: Dict[str, Any], queue: Path = QUEUE, sources: Path = SOURCES) -> Dict[str, Any]:
    flag = dict(flag)
    flag["id"] = gate.flag_id(flag)
    flag["grade"], flag["reasons"] = gate.triage(flag, load_sources(sources))
    flag["submitted"] = _now()
    flag.setdefault("reviews", [])
    _append(flag, queue)  # anche RESPINTO e SOTTO_IL_CASO: i FAIL sono pubblici
    return flag


def review(rev: Dict[str, Any], queue: Path = QUEUE, sources: Path = SOURCES) -> Dict[str, Any]:
    flags = load_queue(queue)
    flag = flags.get(rev.get("flag_id") or "")
    if flag is None:
        raise SystemExit(f"segnalazione non in coda: {rev.get('flag_id')!r}")
    grade, why = gate.apply_review(flag, rev, load_sources(sources))
    if grade is None:
        raise SystemExit("revisione rifiutata: " + "; ".join(why))
    flag["grade"], flag["reasons"] = grade, why
    flag["reviews"] = flag.get("reviews", []) + [{**rev, "at": _now()}]
    _append(flag, queue)
    return flag


def probe(write: bool) -> List[Dict[str, Any]]:
    doc = json.loads(SOURCES.read_text(encoding="utf-8"))
    for s in doc["sources"]:
        if s["status"] == "dead" or not s.get("probe"):
            continue
        req = urllib.request.Request(s["probe"], headers={"Range": "bytes=0-2000", "User-Agent": "fleet-probe"})
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                code = r.status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception as e:  # timeout, DNS, TLS: la sorgente non e' verificata, punto
            code = type(e).__name__
        s["last_probe"] = code
        # 'key' e 'manual' restano tali anche se la home risponde: il dato non si scarica da solo
        if s["status"] in ("ok", "unverified"):
            s["status"] = "ok" if code in (200, 206) else "unverified"
        s["checked"] = _now()[:10]
        print(f"{s['status']:<11} {code!s:<14} {s['id']}")
    if write:
        SOURCES.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return doc["sources"]


ORDER = [gate.VERIFICA_APPROFONDITA, gate.SECONDA_VERIFICA, gate.NON_CALIBRATO,
         gate.SOTTO_IL_CASO, gate.FAIL, gate.COLONNA, gate.RESPINTO]


def report(blind: bool) -> None:
    flags = list(load_queue().values())
    if blind:
        keep = [f for f in flags if f["grade"] != gate.RESPINTO]
        print(json.dumps(gate.make_blind_pack(keep, _now()), ensure_ascii=False, indent=2))
        return
    print("Coda flotta — segnalazioni da verificare, non scoperte.")
    print(" ".join(f"{g}={sum(f['grade'] == g for f in flags)}" for g in ORDER))
    for g in ORDER:
        for f in (f for f in flags if f["grade"] == g):
            print(f"\n[{g}] {f['id']}  {f.get('agent')} · {f.get('tipo')} · {f.get('source_id')}")
            print(f"  claim:     {f.get('claim')}")
            print(f"  perche':   {'; '.join(f['reasons'])}")
            print(f"  kill-shot: {f.get('kill_shot')}")
            for r in f.get("reviews", []):
                print(f"  revisione: {r['reviewer']} -> {r['verdict']}: {r['reason']}")
    if not any(f["grade"] in ORDER[:2] for f in flags):
        print("\nNiente sopra il caso. E' un esito, non un guasto.")


def main() -> None:
    ap = argparse.ArgumentParser(prog="python -m core.fleet")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("sources")
    sub.add_parser("probe").add_argument("--write", action="store_true")
    sub.add_parser("submit").add_argument("file")
    sub.add_parser("review").add_argument("file")
    sub.add_parser("report").add_argument("--blind", action="store_true")
    a = ap.parse_args()

    if a.cmd == "sources":
        for s in load_sources().values():
            print(f"{s['status']:<11} {s['domain']:<10} {s['id']:<17} {s['name']}")
    elif a.cmd == "probe":
        probe(a.write)
    elif a.cmd == "submit":
        data = _read_json(a.file)
        for flag in (data if isinstance(data, list) else [data]):
            f = submit(flag)
            print(f"{f['id']} {f['grade']}: {'; '.join(f['reasons'])}")
    elif a.cmd == "review":
        f = review(_read_json(a.file))
        print(f"{f['id']} {f['grade']}: {'; '.join(f['reasons'])}")
    elif a.cmd == "report":
        report(a.blind)


if __name__ == "__main__":
    main()
