"""Fascicolo: un solo file HTML, offline, pensato prima per il telefono.

Dentro ci sono le coordinate: e' il fascicolo LOCALE, non si pubblica.
Accanto viene scritto il pack cieco (niente coordinate, SHA-256) che invece
si puo' condividere, e un GeoJSON locale da aprire in GeoLibre.
"""
from __future__ import annotations

import base64
import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from . import catalog, known

MAX_CARDS = 120  # schede con immagine nel file; il resto sta nel GeoJSON

OUTCOME = {
    "regge_alla_revisione": ("Regge alla revisione", "ok"),
    "incerto": ("Incerto", "mid"),
    "da_rivedere": ("Da rivedere", "new"),
    "scartato": ("Scartato", "no"),
}
KNOWN = {
    "sito_noto_vicino": "Sito noto entro 2 km",
    "rilievo_gia_analizzato": "Rilievo già analizzato da altri: presumi già visto",
    "non_negli_elenchi_consultati": "Non negli elenchi consultati (non vuol dire sconosciuto)",
}

CSS = """
:root{--bg:#f6f4ef;--fg:#1d1b17;--mut:#6b655a;--card:#fff;--line:#ddd7ca;--ok:#1f7a4d;--mid:#a86a00;--new:#3a5fa8;--no:#8a8478;--warn:#9c2b1f}
@media(prefers-color-scheme:dark){:root{--bg:#15140f;--fg:#ece8dd;--mut:#a39d8f;--card:#1f1d17;--line:#35322a;--ok:#5fc48f;--mid:#e0a84a;--new:#8fb0f0;--no:#8a8478;--warn:#f08a7a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:1100px;margin:0 auto;padding:16px}
h1{font-size:1.5rem;margin:.2em 0}h2{font-size:1.15rem;margin:1.6em 0 .5em}
.lead{color:var(--mut);margin:0 0 1em}.warn{border-left:4px solid var(--warn);background:var(--card);padding:10px 12px;margin:12px 0;border-radius:4px}
.nums{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;margin:12px 0}
.num{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px}.num b{display:block;font-size:1.4rem}.num span{color:var(--mut);font-size:.85rem}
.map{background:var(--card);border:1px solid var(--line);border-radius:8px;width:100%;height:auto;touch-action:manipulation}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0;position:sticky;top:0;background:var(--bg);padding:8px 0;z-index:2}
.filters button{min-height:44px;min-width:44px;padding:8px 14px;border-radius:22px;border:1px solid var(--line);background:var(--card);color:var(--fg);font:inherit}
.filters button[aria-pressed=true]{background:var(--fg);color:var(--bg)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
.card:target{outline:3px solid var(--new)}
.imgs{display:grid;grid-template-columns:1fr 1fr}.imgs img{width:100%;height:auto;display:block}
.body{padding:12px}.tag{display:inline-block;padding:2px 10px;border-radius:12px;font-size:.8rem;font-weight:600;border:1px solid currentColor}
.ok{color:var(--ok)}.mid{color:var(--mid)}.new{color:var(--new)}.no{color:var(--no)}
.card h3{margin:.3em 0;font-size:1rem}.plain{margin:.4em 0}.k{color:var(--mut);font-size:.85rem;margin:.3em 0}
details{margin-top:.5em}summary{min-height:44px;display:flex;align-items:center;cursor:pointer;color:var(--mut)}
html,body{overflow-x:hidden}table{border-collapse:collapse;width:100%;font-size:.9rem;table-layout:fixed}td,th{overflow-wrap:anywhere}.card,.num{min-width:0}td,th{text-align:left;padding:4px 6px;border-bottom:1px solid var(--line)}
code{font-size:.85em}footer{color:var(--mut);font-size:.85rem;margin:2em 0}
"""

JS = """
const bs=[...document.querySelectorAll('.filters button')],cs=[...document.querySelectorAll('.card')],ds=[...document.querySelectorAll('.map a')];
bs.forEach(b=>b.onclick=()=>{bs.forEach(x=>x.setAttribute('aria-pressed',x===b));const f=b.dataset.f;
cs.forEach(c=>c.hidden=!(f==='all'||c.dataset.o===f));ds.forEach(d=>d.style.display=(f==='all'||d.dataset.o===f)?'':'none')});
"""


def _b64(p: Path, mime: str = "image/jpeg", side: int = 320) -> str:
    """Immagine ridotta e incorporata: il fascicolo resta un file solo e leggero."""
    import io

    from PIL import Image

    if not p.exists():
        return ""
    buf = io.BytesIO()
    Image.open(p).resize((side, side), Image.LANCZOS).save(buf, "JPEG", quality=72)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def _plain(c: Dict[str, Any]) -> str:
    bits = [f"{c['n_objects']} rilievi vicini" if c["n_objects"] > 1 else "un rilievo isolato",
            f"per {c['area_m2']:.0f} m² in tutto", f"il più alto sporge di circa {max(0, c['max_height_m']):.1f} m"]
    if c.get("extent_m"):
        bits.append(f"distribuiti su {c['extent_m']:.0f} m")
    return ", ".join(bits) + "."


def _svg_map(transects: List[Dict[str, Any]], cands: List[Dict[str, Any]], scanned: set) -> str:
    w0, s0, e0, n0 = -93.6, 15.6, -86.4, 21.8
    W, H = 720, 620
    X = lambda lon: (lon - w0) / (e0 - w0) * W
    Y = lambda lat: (n0 - lat) / (n0 - s0) * H
    parts = [f'<svg class="map" viewBox="0 0 {W} {H}" role="img" aria-label="Transetti scansionati e candidati">']
    for t in transects:   # ingombro del transetto (rettangolo che lo contiene), non la sua traccia esatta
        w, s, e, n = t["bbox"]
        done = t["id"] in scanned
        parts.append(f'<rect x="{X(w):.1f}" y="{Y(n):.1f}" width="{max(1.5, X(e) - X(w)):.1f}" height="{max(1.5, Y(s) - Y(n)):.1f}" '
                     f'fill="{"var(--fg)" if done else "var(--mut)"}" fill-opacity="{.35 if done else .12}"/>')
    for c in cands:
        cls = OUTCOME[c["outcome"]][1]
        parts.append(f'<a href="#{c["id"]}" data-o="{c["outcome"]}"><circle cx="{X(c["lon"]):.1f}" cy="{Y(c["lat"]):.1f}" r="5" class="{cls}" fill="currentColor" fill-opacity=".8"><title>{c["id"]}</title></circle></a>')
    parts.append("</svg>")
    return "".join(parts)


def collect(work: Path) -> Dict[str, Any]:
    from . import learn
    from .__main__ import load_scans

    scans = load_scans(work)
    rank = learn.load(work)
    cands = [dict(c, survey=s["survey"]) for s in scans for c in s["candidates"]]
    for c in cands:
        c["priority"] = learn.priority(c, rank) if rank else None
    cands.sort(key=lambda c: -(c["priority"] if rank else c["score"]))
    return_order = {"regge_alla_revisione": 0, "incerto": 1, "da_rivedere": 2, "scartato": 3}
    results = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((work / "review" / "results").glob("*.json"))] \
        if (work / "review" / "results").exists() else []
    votes = {k: v for r in results for k, v in r["candidates"].items()}
    reviewers = {f"{k}": v for r in results for k, v in r["reviewers"].items()}
    sites = known.load_sites(work / "known")
    for c in cands:
        v = votes.get(c["id"])
        c["outcome"] = v["outcome"] if v else "da_rivedere"
        c["votes"] = v["all_votes"] if v else []
        c["known"] = known.status(c, sites, c["survey"])
    cands.sort(key=lambda c: return_order[c["outcome"]])   # stabile: prima cio' che regge, poi per priorita'
    return {"scans": scans, "cands": cands, "reviewers": reviewers, "n_sites": len(sites), "rank": rank}


def blind_pack(cands: List[Dict[str, Any]], ts: str) -> Dict[str, Any]:
    drop = {"lon", "lat", "x", "y", "transect", "id"}
    rows = []
    for k, c in enumerate(cands, 1):
        r = {key: val for key, val in c.items() if key not in drop}
        r["label"] = f"C{k:03d}"
        r["known"] = {"label": c["known"]["label"]}  # niente nome del sito vicino: localizzerebbe
        r["votes"] = [{"verdict": v["verdict"], "reviewer": v["reviewer"]} for v in c["votes"]]
        rows.append(r)
    payload = {"algorithm": "sha256", "candidates": rows, "timestamp": ts}
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return {**payload, "hash": hashlib.sha256(blob.encode()).hexdigest(),
            "note": "Niente coordinate. Hash = priorita', non prova."}


def build(work: Path) -> Dict[str, Any]:
    d = collect(work)
    cands, scans = d["cands"], d["scans"]
    ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    km2 = sum(s["km2"] for s in scans)
    n_obj = sum(s["n_objects"] for s in scans)
    counts = {o: sum(c["outcome"] == o for c in cands) for o in OUTCOME}
    cal = [r for r in d["reviewers"].values() if r.get("can_confirm")]
    e = html.escape

    cards = []
    for rank, c in enumerate(cands[:MAX_CARDS], 1):
        lab, cls = OUTCOME[c["outcome"]]
        near = c["known"]["nearest"]
        votes = "".join(f"<tr><td>{e(v['reviewer'])}</td><td>{e(v['verdict'])}</td><td>{e(str(v.get('note') or ''))}</td></tr>" for v in c["votes"])
        cards.append(f"""<article class="card" id="{c['id']}" data-o="{c['outcome']}">
<div class="imgs"><img loading="lazy" alt="Riquadro 120 m, terreno nudo" src="{_b64(work / 'chips' / (c['id'] + '.jpg'), 'image/jpeg')}">
<img loading="lazy" alt="Stesso riquadro: rosso sporge, blu affonda" src="{_b64(work / 'context' / (c['id'] + '.jpg'), 'image/jpeg')}"></div>
<div class="body"><span class="tag {cls}">{lab}</span>
<h3>#{rank} · {c['id']}</h3>
<p class="plain">{e(_plain(c))}</p>
<p class="k">{e(KNOWN[c['known']['label']])}{f" — più vicino: {e(near['name'])}, {near['km']} km ({e(near['source'])})" if near else ""}</p>
<details><summary>Misure, voti, cosa lo smentirebbe</summary>
<table><tr><th>punteggio d'ordine</th><td>{c['score']}</td></tr><tr><th>probabilità media</th><td>{c['mean_prob']}</td></tr>
<tr><th>ortogonalità dei bordi (0–1)</th><td>{c.get('ortho', '—')}</td></tr><tr><th>dato valido nel riquadro</th><td>{int(100 * c.get('valid_frac', 1))}%</td></tr>
<tr><th>transetto</th><td>{e(c['transect'])}</td></tr><tr><th>lat, lon (locale)</th><td>{c['lat']}, {c['lon']}</td></tr></table>
{f"<table><tr><th>revisore</th><th>verdetto</th><th>nota</th></tr>{votes}</table>" if votes else "<p class='k'>Nessun revisore l'ha ancora visto.</p>"}
<p class="k"><b>Cosa posso dire:</b> qui il terreno ha la forma che gli archeologi hanno annotato come struttura a Chactún.<br>
<b>Cosa non posso dire:</b> che sia antico, che sia maya, che sia nuovo.<br>
<b>Lo smentirebbe:</b> un secondo rilievo senza il rilievo; una foto recente con un edificio o un campo; un sopralluogo (serve permesso INAH).</p>
</details></div></article>""")

    rev_rows = "".join(
        f"<tr><td>{e(k)}</td><td>{r.get('sensitivity', '—')}</td><td>{r.get('specificity', '—')}</td><td>{r.get('n_pos', 0) + r.get('n_neg', 0)}</td><td>{'conferma' if r.get('can_confirm') else '—'} · {'scarta' if r.get('can_discard') else 'non scarta'}</td></tr>"
        for k, r in d["reviewers"].items())
    prior = "".join(f"<li>{e(p)}</li>" for p in known.PRIOR_WORK.get("G-LiHT Yucatan 2013", []))
    page = f"""<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vaglio — fascicolo locale</title><style>{CSS}</style></head><body><main>
<h1>Vaglio — fascicolo locale</h1>
<p class="lead">Candidati da verificare su LiDAR pubblico. Non è un elenco di scoperte. Generato {ts}.</p>
<div class="warn"><b>Questo file contiene coordinate: resta sul tuo dispositivo.</b> Da condividere c'è solo <code>pack_cieco.json</code>.
Una mappa pubblica di rovine non scavate è una mappa per i saccheggiatori.</div>
<div class="nums">
<div class="num"><b>{km2:.0f} km²</b><span>scansionati ({len(scans)} transetti)</span></div>
<div class="num"><b>{n_obj}</b><span>rilievi sopra soglia</span></div>
<div class="num"><b>{len(cands)}</b><span>complessi candidati</span></div>
<div class="num"><b>{counts['regge_alla_revisione']}</b><span>reggono alla revisione</span></div>
<div class="num"><b>{counts['scartato']}</b><span>scartati dai revisori</span></div>
<div class="num"><b>{len(cal)}/{len(d['reviewers'])}</b><span>revisori che possono confermare</span></div>
</div>
<h2>Già guardato da altri</h2>
<p>Questo rilievo è già stato analizzato. Ogni candidato si presume già visto finché non si dimostra il contrario.</p><ul>{prior}</ul>
<p class="k">Elenchi di siti noti consultati: {d['n_sites']} siti. «Non nel registro» non vuol dire «sconosciuto».</p>
<h2>Mappa</h2>{_svg_map(catalog.transects(), cands[:MAX_CARDS], {s['transect'] for s in scans})}
<p class="k">Rettangoli marcati: transetti scansionati. Tenui: ancora da fare. Tocca un punto per la scheda (solo i primi candidati hanno una scheda).</p>
<h2>Revisori</h2>
{f"<table><tr><th>revisore</th><th>trova le strutture note</th><th>scarta i vuoti noti</th><th>controlli</th><th>il suo voto vale per</th></tr>{rev_rows}</table><p class='k'>Un revisore che non trova almeno il 70% delle strutture note non può scartare: il suo «naturale» non prova niente. Chi scarta almeno il 70% dei vuoti noti può confermare.</p>" if rev_rows else "<p>Nessuna revisione ancora. <code>python -m vaglio pacco</code> prepara le immagini.</p>"}
<h2>Candidati</h2>
<p class="k">{f"Ordine appreso da {d['rank']['n']} candidati già rivisti (capacità di separare tenuti e scartati, misurata lasciandone fuori uno alla volta: {d['rank']['auc_loo']} su 1; 0,5 = a caso)." if d['rank'] else "Ordine: punteggio di priorità (area, altezza, lati dritti). Non è una probabilità."}</p>
<div class="filters"><button data-f="all" aria-pressed="true">Tutti {len(cands)}</button>{"".join(f'<button data-f="{o}" aria-pressed="false">{OUTCOME[o][0]} {n}</button>' for o, n in counts.items())}</div>
<div class="cards">{"".join(cards)}</div>
<footer>Rilevatore tarato su Chactún (Kokalj et al. 2023, CC BY 4.0). LiDAR: NASA G-LiHT 2013, riprocessato da B. J. Britton (2026), OpenTopography, pubblico dominio.
{f"Mostrate le prime {MAX_CARDS} schede di {len(cands)}; tutte stanno in candidati.geojson." if len(cands) > MAX_CARDS else ""}</footer>
</main><script>{JS}</script></body></html>"""
    (work / "dossier.html").write_text(page, encoding="utf-8")
    geo = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [c["lon"], c["lat"]]},
         "properties": {k: c[k] for k in ("id", "outcome", "score", "n_objects", "area_m2", "max_height_m", "transect")}} for c in cands]}
    (work / "candidati.geojson").write_text(json.dumps(geo), encoding="utf-8")
    (work / "pack_cieco.json").write_text(json.dumps(blind_pack(cands, ts), ensure_ascii=False, indent=1), encoding="utf-8")
    return {"dossier": str(work / "dossier.html"), "candidates": len(cands), "km2": round(km2, 1), **counts}
