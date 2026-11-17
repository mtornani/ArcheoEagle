"""Vaglio — dal LiDAR pubblico a un fascicolo di candidati, con gli errori misurati.

    python -m vaglio catalogo
    python -m vaglio scansiona --transetti South_GLAS_l3s459      # oppure --tutti, oppure --dtm mio.tif
    python -m vaglio pacco --top 60                               # immagini anonime + controlli piantati
    python -m vaglio esiti pacco-1 claude=r1.json grok=r2.json    # pesa i revisori, conta i voti
    python -m vaglio impara                                       # le revisioni riordinano la coda
    python -m vaglio moderno                                      # cosa c'e' oggi sopra ogni candidato (uso del suolo)
    python -m vaglio verifica pack_cieco.json                     # controlla un pack ricevuto: hash e nessuna coordinata
    python -m vaglio deposito                                     # test cieco: elenco sigillato + impronta da pubblicare
    python -m vaglio kit                                          # numeri e figure senza posizioni, per chi scrive i materiali
    python -m vaglio controlla rapporto.md                        # un testo pronto a uscire: niente coordinate, niente "scoperta"
    python -m vaglio dossier                                      # HTML offline + pack cieco

Tutto finisce in ./vaglio_lavoro (coordinate comprese: resta sul tuo dispositivo).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List

from . import catalog, known, review, scan
from . import model as M

SURVEY = "G-LiHT Yucatan 2013"
# Soglie di priorita' (non di verita'): cosa vale la pena far guardare a un revisore.
MIN_OBJECTS, MIN_AREA_M2 = 2, 100.0
SOLO_AREA_M2, SOLO_HEIGHT_M = 150.0, 0.75


def _is_candidate(c: Dict[str, Any]) -> bool:
    return (c["n_objects"] >= MIN_OBJECTS and c["area_m2"] >= MIN_AREA_M2) or \
           (c["area_m2"] >= SOLO_AREA_M2 and c["max_height_m"] >= SOLO_HEIGHT_M)


def _scan_one(work: Path, name: str, dtm: Path, epsg: int | None, km2: float | None, m: Dict[str, Any]) -> Dict[str, Any]:
    import numpy as np
    import rasterio
    from PIL import Image
    from pyproj import Transformer

    t0 = time.time()
    objs = scan.scan_dtm(dtm, m["clf"], name)
    clusters = scan.cluster(objs)
    with rasterio.open(dtm) as src:
        crs = src.crs
        if km2 is None:
            km2 = round(src.width * src.height * src.res[0] * src.res[1] / 1e6, 2)
    tr = Transformer.from_crs(crs if epsg is None else epsg, 4326, always_xy=True)
    cands = []
    for c in filter(_is_candidate, clusters):
        c["id"] = "V-" + hashlib.sha1(f"{name}:{c['x']}:{c['y']}".encode()).hexdigest()[:8]
        c["transect"] = name
        c["lon"], c["lat"] = (round(v, 6) for v in tr.transform(c["x"], c["y"]))
        b, valid, lrm = scan.chip_bands(dtm, c["x"], c["y"])
        c["valid_frac"] = round(float(valid.mean()), 2)
        (work / "chips").mkdir(parents=True, exist_ok=True)
        (work / "context").mkdir(parents=True, exist_ok=True)
        g = scan.render_gray(b, valid)
        g.save(work / "chips" / f"{c['id']}.jpg", quality=85)
        # contesto per il fascicolo: stesso riquadro, rosso dove sporge, blu dove affonda
        a = np.asarray(g, dtype=np.float32)
        r = np.asarray(Image.fromarray(np.clip(lrm, -3, 3)).resize(g.size, Image.BILINEAR))
        rgb = np.stack([a + 60 * np.clip(r, 0, 3), a - 15 * np.abs(r), a + 60 * np.clip(-r, 0, 3)], -1)
        Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).save(work / "context" / f"{c['id']}.jpg", quality=72)
        cands.append(c)
    out = {"transect": name, "survey": SURVEY if epsg else "DTM fornito", "km2": km2,
           "n_objects": len(objs), "n_clusters": len(clusters), "seconds": round(time.time() - t0, 1),
           "hi": M.HI, "lo": M.LO, "candidates": cands}
    (work / "scan").mkdir(parents=True, exist_ok=True)
    (work / "scan" / f"{name}.json").write_text(json.dumps(out), encoding="utf-8")
    return out


def load_scans(work: Path) -> List[Dict[str, Any]]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted((work / "scan").glob("*.json"))]


def main() -> None:
    ap = argparse.ArgumentParser(prog="python -m vaglio", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lavoro", default="vaglio_lavoro", help="cartella di lavoro (locale, con coordinate)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("catalogo")
    s = sub.add_parser("scansiona")
    s.add_argument("--transetti", help="id separati da virgola")
    s.add_argument("--tutti", action="store_true")
    s.add_argument("--dtm", help="un tuo GeoTIFF di terreno nudo, in metri")
    s.add_argument("--limite", type=int, default=0)
    s.add_argument("--parte", default="", help="K/N: fai solo la K-esima di N parti (per lavorare in parallelo)")
    s.add_argument("--tieni-dtm", action="store_true", help="non cancellare i DTM scaricati")
    p = sub.add_parser("pacco")
    p.add_argument("--top", type=int, default=60)
    p.add_argument("--nome", default="")
    p.add_argument("--controlli", type=int, default=30)
    p.add_argument("--seme", type=int, default=0)
    p.add_argument("--ordine", choices=("auto", "punteggio", "appreso"), default="auto",
                   help="come scegliere 'i piu' alti': punteggio grezzo, ordine appreso dalle revisioni, o auto (appreso se c'e')")
    p.add_argument("--misto", action="store_true",
                   help="meta' dai punteggi piu' alti, meta' a caso dal resto: misura il rilevatore su tutta la scala, non solo in cima")
    e = sub.add_parser("esiti")
    e.add_argument("nome")
    e.add_argument("risposte", nargs="+", help="revisore=file.json")
    sub.add_parser("impara")
    sub.add_parser("moderno")
    sub.add_parser("dossier")
    sub.add_parser("kit")
    sub.add_parser("deposito")
    k = sub.add_parser("controlla")
    k.add_argument("file", nargs="+", help="testi pronti a uscire (md, html, txt)")
    v = sub.add_parser("verifica")
    v.add_argument("pack", nargs="?", default="", help="pack cieco da controllare (default: quello della cartella di lavoro)")
    a = ap.parse_args()
    work = Path(a.lavoro)

    if a.cmd == "catalogo":
        ts = catalog.transects()
        print(f"{len(ts)} transetti, {sum(t['area_km2'] for t in ts):.0f} km2, {sum(t['dtm_mb'] for t in ts) / 1e3:.1f} GB — {catalog.load()['source']}")
        done = {s["transect"] for s in load_scans(work)} if (work / "scan").exists() else set()
        print(f"scansionati qui: {len(done)}")
        return

    if a.cmd == "scansiona":
        import joblib

        m = joblib.load(M.MODEL_PATH)
        if a.dtm:
            r = _scan_one(work, Path(a.dtm).stem, Path(a.dtm), None, None, m)
            print(f"{r['transect']}: {r['n_objects']} oggetti, {len(r['candidates'])} candidati, {r['seconds']} s")
            return
        ts = catalog.transects()
        if a.transetti:
            want = set(a.transetti.split(","))
            ts = [t for t in ts if t["id"] in want]
        elif not a.tutti:
            raise SystemExit("indica --transetti, --tutti oppure --dtm")
        done = {p.stem for p in (work / "scan").glob("*.json")} if (work / "scan").exists() else set()
        ts = [t for t in ts if t["id"] not in done]
        if a.parte:
            k, n = (int(v) for v in a.parte.split("/"))
            ts = [t for i, t in enumerate(catalog.transects()) if i % n == k - 1 and t in ts]
        if a.limite:
            ts = ts[: a.limite]
        for k, t in enumerate(ts, 1):
            try:
                dtm = catalog.fetch_dtm(t, work / "dtm")
                r = _scan_one(work, t["id"], dtm, t["epsg"], t["area_km2"], m)
                print(f"[{k}/{len(ts)}] {t['id']}: {r['km2']} km2, {r['n_objects']} oggetti, {len(r['candidates'])} candidati, {r['seconds']} s", flush=True)
            except Exception as ex:  # un transetto rotto non ferma la scansione; resta scritto che e' fallito
                print(f"[{k}/{len(ts)}] {t['id']}: FALLITO {type(ex).__name__}: {ex}", flush=True)
                continue
            if not a.tieni_dtm:
                dtm.unlink(missing_ok=True)
        return

    if a.cmd == "pacco":
        from . import learn

        rank = None if a.ordine == "punteggio" else learn.load(work)
        if a.ordine == "appreso" and not rank:
            raise SystemExit("nessun ordine appreso: prima `python -m vaglio impara`")
        cands = sorted((c for s in load_scans(work) for c in s["candidates"]),
                       key=lambda c: -(learn.priority(c, rank) if rank else c["score"]))
        seen = {v["ref"] for kf in (work / "review" / "keys").glob("*.json") for v in json.loads(kf.read_text()).values()} \
            if (work / "review" / "keys").exists() else set()
        cands = [c for c in cands if c["id"] not in seen]
        if a.misto:
            import random

            rest = cands[a.top // 2:]
            cands = cands[: a.top // 2] + random.Random(a.seme).sample(rest, min(len(rest), a.top - a.top // 2))
        else:
            cands = cands[: a.top]
        # numero libero dopo il piu' alto mai usato (anche fra gli annullati): un pacco rivisto non si sovrascrive
        used = [int(m.group(1)) for p_ in (work / "review").rglob("*pacco-*")
                for m in [re.search(r"pacco-(\d+)", p_.name)] if m] if (work / "review").exists() else []
        name = a.nome or f"pacco-{max(used, default=0) + 1}"
        if (work / "review" / "keys" / f"{name}.json").exists():
            raise SystemExit(f"{name} esiste gia': scegli un altro --nome")
        print(json.dumps(review.make_pack(cands, work / "chips", work / "review", name, a.controlli, a.seme), ensure_ascii=False))
        return

    if a.cmd == "esiti":
        key = json.loads((work / "review" / "keys" / f"{a.nome}.json").read_text())
        by = {}
        for spec in a.risposte:
            who, _, f = spec.partition("=")
            by[who] = json.loads(Path(f).read_text(encoding="utf-8"))
        res = review.ingest(key, by)
        (work / "review" / "results").mkdir(parents=True, exist_ok=True)
        (work / "review" / "results" / f"{a.nome}.json").write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
        for who, g in res["reviewers"].items():
            print(who, g)
        outc = [c["outcome"] for c in res["candidates"].values()]
        print({o: outc.count(o) for o in sorted(set(outc))})
        return

    if a.cmd == "impara":
        from . import learn

        reviewed = {k: v for f in sorted((work / "review" / "results").glob("*.json"))
                    for k, v in json.loads(f.read_text(encoding="utf-8"))["candidates"].items()}
        m = learn.fit([c for s_ in load_scans(work) for c in s_["candidates"]], reviewed)
        (work / "review" / "ordine.json").write_text(json.dumps(m), encoding="utf-8")
        print(json.dumps({k: m[k] for k in m if k not in ("mu", "sd")}, ensure_ascii=False))
        return

    if a.cmd == "moderno":
        from . import modern

        cands = [c for s_ in load_scans(work) for c in s_["candidates"]]
        land = modern.land_use(cands, work / "worldcover")
        (work / "moderno.json").write_text(json.dumps(land), encoding="utf-8")
        labels = [v_["label"] for v_ in land.values()]
        print(json.dumps({"candidati": len(land), **{k: labels.count(k) for k in sorted(set(labels))},
                          "fonte": modern.SOURCE}, ensure_ascii=False))
        return

    if a.cmd == "verifica":
        from . import report

        path = Path(a.pack) if a.pack else work / "pack_cieco.json"
        pack = json.loads(path.read_text(encoding="utf-8"))
        problems = report.verify_pack(pack)
        print(f"{path}: {len(pack.get('candidates') or [])} candidati, firmato {pack.get('timestamp')}")
        print("\n".join(problems) if problems else "a posto: l'hash corrisponde e nessun campo localizza")
        raise SystemExit(1 if problems else 0)

    if a.cmd == "deposito":
        from . import deposit

        m = deposit.write(work)
        print(json.dumps(m, ensure_ascii=False, indent=1))
        print("Pubblica l'impronta sha256 (commit in vaglio/test_cieco/DEPOSITO.md) PRIMA di mandare il CSV.")
        return

    if a.cmd == "kit":
        from . import kit

        print(json.dumps(kit.export(work), ensure_ascii=False))
        return

    if a.cmd == "controlla":
        from . import kit

        bad = 0
        for f in a.file:
            problems = kit.check(Path(f).read_text(encoding="utf-8", errors="replace"))
            print(f"{f}: " + ("a posto" if not problems else f"{len(problems)} problemi"))
            for line in problems:
                print("  -", line)
            bad += bool(problems)
        raise SystemExit(1 if bad else 0)

    if a.cmd == "dossier":
        from . import report

        print(json.dumps(report.build(work), ensure_ascii=False))


if __name__ == "__main__":
    main()
