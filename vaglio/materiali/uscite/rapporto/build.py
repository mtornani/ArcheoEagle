"""Costruisce index.html del rapporto da template.html e dal pack cieco pubblico.

Uso, da vaglio/:
    python materiali/uscite/rapporto/build.py

Legge solo file senza posizioni: vaglio/pack_cieco.json, il catalogo dei transetti
(ingombri, per la mappa di copertura) e figure/info.json (misure delle figure,
scritte da chi ha la cartella di lavoro). I numeri del testo sono scritti a mano
nel template e vanno ricontrollati contro FATTI.md e numeri.json a ogni rigenerazione:
questo script verifica quelli che puo' ricalcolare e si ferma se non tornano.
"""
from __future__ import annotations

import html
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VAGLIO = HERE.parents[2]
sys.path.insert(0, str(VAGLIO))

from vaglio import catalog, report  # noqa: E402


def fmt(n: float, lang: str, dec: int = 0) -> str:
    s = f"{n:,.{dec}f}"
    return s.replace(",", " ").replace(".", ",").replace(" ", ".") if lang == "it" else s


def main() -> None:
    pack = json.loads((VAGLIO / "pack_cieco.json").read_text(encoding="utf-8"))
    cands = pack["candidates"]
    info = json.loads((HERE / "figure" / "info.json").read_text(encoding="utf-8"))
    n = len(cands)

    # --- controlli: i numeri del template che si possono ricalcolare devono tornare
    outcomes = {o: sum(c["outcome"] == o for c in cands) for o in ("regge_alla_revisione", "incerto", "da_rivedere")}
    reliefs = sum(c["n_objects"] for c in cands)
    land = {k: sum((c.get("land") or {}).get("label") == k for c in cands)
            for k in ("costruito oggi", "coltivato oggi", "nessun uso moderno evidente")}
    near = sum(c["known"]["label"] == "sito_noto_vicino" for c in cands)
    km2 = sum(t["area_km2"] for t in catalog.transects())
    expect = {"candidati": (n, 11916), "regge": (outcomes["regge_alla_revisione"], 15), "incerti": (outcomes["incerto"], 25),
              "da_rivedere": (outcomes["da_rivedere"], 11876), "rilievi": (reliefs, 24265), "costruito": (land["costruito oggi"], 150),
              "coltivato": (land["coltivato oggi"], 34), "nessun_uso": (land["nessun uso moderno evidente"], 11732),
              "vicino_noto": (near, 249), "km2": (round(km2, 1), 1272.7), "figure_regge": (len(info["regge"]), 15)}
    bad = {k: v for k, v in expect.items() if v[0] != v[1]}
    if bad:
        raise SystemExit(f"i numeri scritti nel template non tornano col pack: {bad}. Aggiorna il testo, poi rigenera.")
    if pack["hash"] not in (HERE / "template.html").read_text(encoding="utf-8"):
        raise SystemExit("l'impronta del pack nel template non e' quella del pack attuale")

    # --- classifica per punteggio: dove cadono i rivisti, e da quale estrazione vengono
    order = sorted(range(n), key=lambda i: -cands[i]["score"])
    rank = {i: r + 1 for r, i in enumerate(order)}
    reviewed = sorted((rank[i], "regge" if cands[i]["outcome"] == "regge_alla_revisione" else "incerto")
                      for i in range(n) if cands[i]["outcome"] != "da_rivedere")
    top_cut = sorted(r for r, _ in reviewed)[19]            # i 20 piu' alti al momento del pacco restano i 20 piu' alti fra i 40
    rank_data = [[r, o, "top" if r <= top_cut else "rnd"] for r, o in reviewed]

    bins = [("1 rilievo", "1 relief", lambda k: k == 1), ("2", "2", lambda k: k == 2), ("3–4", "3–4", lambda k: 3 <= k <= 4),
            ("5–9", "5–9", lambda k: 5 <= k <= 9), ("10 o più", "10 or more", lambda k: k >= 10)]
    size = [[a, b, sum(f(c["n_objects"]) for c in cands)] for a, b, f in bins]
    if round(100 * size[0][2] / n) != 61:
        raise SystemExit("la quota di rilievi isolati non e' piu' 61%: aggiorna la didascalia")

    def rank_table(lang: str) -> str:
        head = ("Posizione", "Estrazione", "Esito") if lang == "it" else ("Rank", "Drawn as", "Outcome")
        g = {"top": ("20 più alti allora", "Top 20 at the time"), "rnd": ("20 a caso", "Random 20")}
        o = {"regge": ("regge alla revisione", "holds up under blind review"), "incerto": ("incerto", "uncertain")}
        k = 0 if lang == "it" else 1
        rows = "".join(f'<tr><td class="n">{fmt(r, lang)}</td><td>{g[gr][k]}</td><td>{o[oc][k]}</td></tr>' for r, oc, gr in rank_data)
        return f'<table><thead><tr><th class="n">{head[0]}</th><th>{head[1]}</th><th>{head[2]}</th></tr></thead><tbody>{rows}</tbody></table>'

    def size_table(lang: str) -> str:
        head = ("Rilievi per complesso", "Complessi") if lang == "it" else ("Reliefs per complex", "Complexes")
        k = 0 if lang == "it" else 1
        rows = "".join(f'<tr><th scope="row">{d[k]}</th><td class="n">{fmt(d[2], lang)}</td></tr>' for d in size)
        return f'<table><thead><tr><th>{head[0]}</th><th class="n">{head[1]}</th></tr></thead><tbody>{rows}</tbody></table>'

    def host(kind: str, lang: str) -> str:
        labels = {"rank": ("Posizione nella classifica per punteggio dei 40 candidati rivisti, su 11.916.",
                           "Score rank of the 40 reviewed candidates, out of 11,916."),
                  "size": ("Complessi candidati per numero di rilievi.", "Candidate complexes by number of reliefs.")}
        return (f'<div class="chart-host" data-chart="{kind}" data-it-label="{html.escape(labels[kind][0])}" '
                f'data-en-label="{html.escape(labels[kind][1])}"></div>')

    def gallery(lang: str) -> str:
        items = []
        for i, d in enumerate(info["regge"]):
            rel = (f"{d['n']} rilievi" if d["n"] > 1 else "1 rilievo") if lang == "it" else (f"{d['n']} reliefs" if d["n"] > 1 else "1 relief")
            alt = (f"Candidato {i + 1}: {rel}, {fmt(d['area'], 'it')} m²" if lang == "it" else f"Candidate {i + 1}: {rel}, {fmt(d['area'], 'en')} m²")
            items.append(f'<li><button type="button" data-i="{i}"><img src="figure/regge_{i + 1:02d}.jpg" width="960" height="480" '
                         f'loading="lazy" alt="{html.escape(alt)}"><span>{i + 1:02d} · {rel}</span></button></li>')
        return f'<ul class="gallery">{"".join(items)}</ul>'

    # --- mappa di copertura: tutti i transetti, nessun candidato
    ids = {t["id"] for t in catalog.transects()}
    svg = report._svg_map(catalog.transects(), [], ids)
    svg = (svg.replace("var(--fg)", "var(--ink)").replace("var(--mut)", "var(--ink-2)").replace("var(--line)", "var(--rule)")
              .replace("var(--card)", "var(--panel)").replace('fill-opacity=".28"', 'fill-opacity=".7"')
              .replace('font-size="12"', 'font-size="15"').replace('aria-label="Mappa dei candidati"', 'aria-label="Transetti LiDAR scansionati sulla penisola dello Yucatán"'))

    s = (HERE / "template.html").read_text(encoding="utf-8")
    subs = {"<!--COVER-->": svg, "<!--RANK_IT-->": host("rank", "it"), "<!--RANK_EN-->": host("rank", "en"),
            "<!--SIZE_IT-->": host("size", "it"), "<!--SIZE_EN-->": host("size", "en"),
            "<!--RANKTABLE_IT-->": rank_table("it"), "<!--RANKTABLE_EN-->": rank_table("en"),
            "<!--SIZETABLE_IT-->": size_table("it"), "<!--SIZETABLE_EN-->": size_table("en"),
            "<!--GALLERY_IT-->": gallery("it"), "<!--GALLERY_EN-->": gallery("en"),
            "/*INFO*/null": json.dumps(info, ensure_ascii=False),
            "/*DATA*/null": json.dumps({"n": n, "rank": rank_data, "size": size}, ensure_ascii=False)}
    for k, v in subs.items():
        if k not in s:
            raise SystemExit(f"segnaposto mancante nel template: {k}")
        s = s.replace(k, v)
    (HERE / "index.html").write_text(s, encoding="utf-8")
    print(f"index.html: {len(s) // 1024} KB · {n} candidati · rivisti {len(rank_data)} · pack {pack['hash'][:12]}")


if __name__ == "__main__":
    main()
