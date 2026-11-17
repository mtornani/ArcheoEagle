"""Costruisce index.html della pagina per il pubblico ("Sotto la foresta").

Uso, da vaglio/:
    python materiali/uscite/pubblico/build.py

Inserisce la mappa della sola copertura, la galleria dei 15 candidati e le risposte
della prova. Controlla che i numeri scritti nel testo tornino col pack cieco.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VAGLIO = HERE.parents[2]
sys.path.insert(0, str(VAGLIO))

from vaglio import catalog, report  # noqa: E402


def main() -> None:
    pack = json.loads((VAGLIO / "pack_cieco.json").read_text(encoding="utf-8"))
    c = pack["candidates"]
    checks = {"11.916": len(c) == 11916, "15": sum(x["outcome"] == "regge_alla_revisione" for x in c) == 15,
              "40": sum(x["outcome"] != "da_rivedere" for x in c) == 40,
              "1.273 km²": round(sum(t["area_km2"] for t in catalog.transects())) == 1273,
              "456": len(catalog.transects()) == 456}
    bad = [k for k, ok in checks.items() if not ok]
    if bad:
        raise SystemExit(f"numeri del testo che non tornano col pack: {bad}")

    ids = {t["id"] for t in catalog.transects()}
    svg = report._svg_map(catalog.transects(), [], ids)
    svg = (svg.replace("var(--fg)", "var(--ink)").replace("var(--mut)", "var(--ink-2)").replace("var(--line)", "var(--rule)")
              .replace("var(--card)", "var(--panel)").replace('fill-opacity=".28"', 'fill-opacity=".85"')
              .replace('font-size="12"', 'font-size="16"')
              .replace('aria-label="Mappa dei candidati"', 'aria-label="Le 456 strisce sorvolate dalla NASA sulla penisola dello Yucatán"'))
    rail = "".join(
        f'<li><button type="button" class="flip" aria-pressed="false" aria-label="Punto {i} di 15: tocca per la vista a colori">'
        f'<img src="img/c{i:02d}_grigio.jpg" width="480" height="480" loading="lazy" alt="Punto {i}: rilievi visti dal laser, quadrato di 120 metri.">'
        f'<img class="col" src="img/c{i:02d}_colore.jpg" width="480" height="480" loading="lazy" alt="">'
        f'<span class="n">{i:02d}</span></button></li>' for i in range(1, 16))
    answers = json.loads((HERE / "risposte.json").read_text(encoding="utf-8"))

    s = (HERE / "template.html").read_text(encoding="utf-8")
    for k, v in {"<!--COVER-->": svg, "<!--RAIL-->": rail, "/*ANSWERS*/[]": json.dumps(answers)}.items():
        if k not in s:
            raise SystemExit(f"segnaposto mancante: {k}")
        s = s.replace(k, v)
    (HERE / "index.html").write_text(s, encoding="utf-8")
    print(f"index.html: {len(s) // 1024} KB · prova: {sum(answers)} edifici su {len(answers)}")


if __name__ == "__main__":
    main()
