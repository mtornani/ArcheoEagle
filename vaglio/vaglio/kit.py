"""Kit per chi scrive i materiali, e cancello per quello che scrive.

Due cose, entrambe pensate per delegare la stesura ad altri (persone o AI)
senza che un numero cambi per strada o che una coordinata scappi:

  export(work)   -> vaglio_lavoro/kit/: numeri.json, figure senza posizione,
                    mappa della sola copertura, copia del pack cieco.
                    Chi scrive usa SOLO questa cartella.
  check(testo)   -> lista di problemi in un materiale pronto a uscire:
                    coordinate, sigle di candidati o transetti, parole che
                    trasformano un candidato in una scoperta.

Il cancello sulle parole e' un'euristica: lascia passare una frase se nega
("non e' una scoperta") o se riferisce l'annuncio di altri. Non sostituisce
una persona che rilegge. Serve a fermare l'errore distratto.
"""
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from . import catalog, known, modern
from . import model as M

MAX_FIGURES = 24

# --- cosa non deve comparire in un materiale che esce ---------------------------------------
LOCATION_PATTERNS = (
    (r"\bV-[0-9a-f]{8}\b", "sigla di un candidato"),
    (r"\b(?:Centro|Norte|North2|South|OutYuc|Chiaps1|ChiapsCampeche)_(?:GLAS|NFI)_l\d+s\d+\b", "sigla di un transetto"),
    (r"(?<![\d.])-?(?:8[6-9]|9[0-4])[.,]\d{3,}", "numero che sembra una longitudine"),
    (r"(?<![\d.,-])(?:1[4-9]|2[0-2])[.,]\d{4,}", "numero che sembra una latitudine"),
    (r"\bopenstreetmap\.org/\?mlat|\bgoogle\.[a-z.]+/maps|\bmaps\.app\.goo\.gl", "collegamento a una mappa"),
)
CLAIM_WORDS = (
    # italiano
    r"scopert[aoie]\b", r"scoprir\w*", r"abbiamo trovato", r"ho trovato", r"sit[oi] nuov[oi]", r"nuov[oi] sit[oi]",
    r"sconosciut[oaie]\b", r"inedit[oaie]\b", r"confermat[oaie]\b", r"citt[aà] perdut[ae]", r"mai vist[oaie]",
    # english
    r"\bdiscover(?:y|ies|ed|s)?\b", r"\bnew(?:ly)? (?:found |identified )?sites?\b", r"\bunknown\b", r"\bunmapped\b",
    r"\bconfirmed\b", r"\blost cit(?:y|ies)\b", r"\bwe (?:have )?found\b", r"\bnever[- ]before[- ]seen\b",
    # espanol
    r"\bdescubri\w*", r"\bhallazgo\w*", r"\bdesconocid[oa]s?\b", r"\bin[eé]dit[oa]s?\b", r"\bconfirmad[oa]s?\b",
    r"ciudad(?:es)? perdida", r"siti[o]s? nuev[oa]s?", r"nuev[oa]s? siti[o]s?",
)
# la frase passa se nega, se e' una domanda aperta, o se riferisce l'annuncio di Miotti
EXCUSES = (r"\bnon\b", r"\bn[eé]\b", r"\bnessun\w*", r"\bsenza\b", r"\bnot\b", r"\bno\b", r"\bnor\b",
           r"\bwithout\b", r"n't\b", r"\bni\b", r"\bsin\b", r"\bnunca\b", r"\bning[uú]n\w*", r"miotti", r"\?\s*$",
           r"\bpresum\w+", r"\bpresume\w*", r"\bse non\b", r"\bunless\b", r"\bwhether\b", r"\bse sia\b")


def check(text: str) -> List[str]:
    """Problemi trovati in un materiale. Lista vuota = puo' uscire (dopo che una persona l'ha riletto)."""
    problems: List[str] = []
    for k, line in enumerate(text.splitlines(), 1):
        for pat, what in LOCATION_PATTERNS:
            m = re.search(pat, line)
            if m:
                problems.append(f"riga {k}: {what}: «{m.group(0)}»")
    # le parole si giudicano per frase: la negazione sta nella stessa frase o non vale
    plain = re.sub(r"<[^>]+>", " ", text)
    for sent in re.split(r"(?<=[.!?:;])\s+|\n{2,}|\n(?=\s*[-*|#>])", plain):
        low = sent.lower()
        hits = [m.group(0) for w in CLAIM_WORDS for m in [re.search(w, low)] if m]
        if hits and not any(re.search(x, low) for x in EXCUSES):
            problems.append(f"parola da scoperta senza negazione ({', '.join(sorted(set(hits)))}): «{' '.join(sent.split())[:160]}»")
    return problems


# --- il kit ---------------------------------------------------------------------------------
def numbers(work: Path) -> Dict[str, Any]:
    """Tutti i numeri che un materiale puo' citare, calcolati dalla cartella di lavoro. Nessuna posizione."""
    from . import report

    d = report.collect(work)
    cands, scans = d["cands"], d["scans"]
    zones = sorted({report.zone(s["transect"]) for s in scans})
    pack_file = work / "pack_cieco.json"
    pack = json.loads(pack_file.read_text(encoding="utf-8")) if pack_file.exists() else None
    land = [c["land"]["label"] for c in cands if c.get("land")]
    rank = d["rank"]
    return {
        "generato": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "scansione": {"transetti": len(scans), "transetti_in_catalogo": len(catalog.transects()),
                      "km2": round(sum(s["km2"] for s in scans), 1), "rilievi_sopra_soglia": sum(s["n_objects"] for s in scans),
                      "complessi_candidati": len(cands)},
        "esiti": {o: sum(c["outcome"] == o for c in cands) for o in report.OUTCOME},
        "per_zona": [{"zona": z, "km2": round(sum(s["km2"] for s in scans if report.zone(s["transect"]) == z), 1),
                      "candidati": sum(c["zone"] == z for c in cands),
                      "reggono": sum(c["zone"] == z and c["outcome"] == "regge_alla_revisione" for c in cands),
                      "incerti": sum(c["zone"] == z and c["outcome"] == "incerto" for c in cands)} for z in zones],
        "revisori": {k: {f: v.get(f) for f in ("sensitivity", "specificity", "n_pos", "n_neg", "can_confirm", "can_discard")}
                     for k, v in d["reviewers"].items()},
        "gia_noto": {lab: sum(c["known"]["label"] == lab for c in cands) for lab in report.KNOWN},
        "uso_del_suolo_oggi": {lab: land.count(lab) for lab in sorted(set(land))} if land else None,
        "ordine_appreso": {k: rank[k] for k in ("n", "n_kept", "auc_loo")} if rank else None,
        "rilevatore_test_chactun": M.TEST_RESULT,
        "pack_cieco": {"hash": pack["hash"], "timestamp": pack["timestamp"], "candidati": len(pack["candidates"])} if pack else None,
        "lavori_precedenti_sullo_stesso_rilievo": known.PRIOR_WORK.get("G-LiHT Yucatan 2013", []),
        "fonti": {"lidar": catalog.load()["source"], "addestramento": "Kokalj et al. 2023, Sci Data 10:558, doi:10.6084/m9.figshare.22202395, CC BY 4.0",
                  "uso_del_suolo": modern.SOURCE, "mappa": "Natural Earth 1:10m, pubblico dominio"},
    }


def _pair(work: Path, cid: str) -> Any:
    """Riquadro del revisore accanto al riquadro colorato (rosso sporge, blu affonda). 120 m di lato ciascuno."""
    from PIL import Image

    a, b = work / "chips" / f"{cid}.jpg", work / "context" / f"{cid}.jpg"
    if not (a.exists() and b.exists()):
        return None
    im = Image.new("RGB", (960, 480))
    im.paste(Image.open(a).convert("RGB").resize((480, 480)), (0, 0))
    im.paste(Image.open(b).convert("RGB").resize((480, 480)), (480, 0))
    return im


def export(work: Path) -> Dict[str, Any]:
    """Scrive vaglio_lavoro/kit/. Tutto cio' che contiene si puo' dare a chi scrive e a chi legge."""
    from PIL import Image

    from . import report, review

    out = work / "kit"
    fig = out / "figure"
    if fig.exists():
        shutil.rmtree(fig)
    fig.mkdir(parents=True)
    d = report.collect(work)
    nums = numbers(work)
    (out / "numeri.json").write_text(json.dumps(nums, ensure_ascii=False, indent=1), encoding="utf-8")

    written: Dict[str, int] = {}
    sheet: List[Any] = []
    groups = (("regge", [c for c in d["cands"] if c["outcome"] == "regge_alla_revisione"]),
              ("incerto", [c for c in d["cands"] if c["outcome"] == "incerto"
                           and sum(v["verdict"] in review.NO for v in c["votes"]) >= 2][:6]))
    for name, group in groups:
        n = 0
        for c in group[:MAX_FIGURES]:
            im = _pair(work, c["id"])
            if im is None:
                continue
            n += 1
            im.save(fig / f"{name}_{n:02d}.jpg", quality=85)       # il nome e' un numero d'ordine: niente sigla
            if name == "regge" and len(sheet) < 12:
                sheet.append(im.crop((0, 0, 480, 480)).resize((320, 320)))
        written[name] = n
    for kind in ("pos", "neg"):
        for n, src in enumerate(sorted(review.CONTROLS.glob(f"{kind}_*.jpg"))[:4], 1):
            shutil.copyfile(src, fig / f"controllo_{'struttura' if kind == 'pos' else 'vuoto'}_{n:02d}.jpg")
    if sheet:
        cols = 4
        im = Image.new("RGB", (320 * cols, 320 * ((len(sheet) + cols - 1) // cols)), "white")
        for k, s in enumerate(sheet):
            im.paste(s, ((k % cols) * 320, (k // cols) * 320))
        im.save(fig / "tavola_reggono.jpg", quality=85)
    scanned = {s["transect"] for s in d["scans"]}
    svg = report._svg_map(catalog.transects(), [], scanned)          # copertura: NESSUN candidato sulla mappa
    (fig / "copertura.svg").write_text(svg.replace('class="map"', 'xmlns="http://www.w3.org/2000/svg"')
                                       .replace("var(--fg)", "#1d1b17").replace("var(--mut)", "#6b655a")
                                       .replace("var(--line)", "#ddd7ca").replace("var(--card)", "#ffffff"), encoding="utf-8")
    if (work / "pack_cieco.json").exists():
        shutil.copyfile(work / "pack_cieco.json", out / "pack_cieco.json")
    (out / "LEGGIMI.txt").write_text(
        "Kit Vaglio per chi scrive rapporti e materiali.\n"
        "Tutto cio' che sta in questa cartella si puo' condividere: non contiene coordinate,\n"
        "sigle di candidati o di transetti. Tutto cio' che sta FUORI da questa cartella\n"
        "(dossier.html, candidati.csv, candidati.geojson, scan/, chips/, review/keys/) NO.\n\n"
        "numeri.json            ogni numero citabile. Un numero che non e' qui non si scrive.\n"
        "figure/regge_NN.jpg    candidati che reggono alla revisione: a sinistra cio' che vede il revisore,\n"
        "                       a destra lo stesso riquadro colorato (rosso sporge, blu affonda). Lato 120 m.\n"
        "figure/incerto_NN.jpg  candidati che almeno due revisori hanno giudicato non costruiti.\n"
        "figure/controllo_*.jpg riquadri di controllo a risposta nota (Chactun, Kokalj et al. 2023, CC BY 4.0).\n"
        "figure/tavola_reggono.jpg  dodici candidati che reggono, in una tavola.\n"
        "figure/copertura.svg   dove e' passato il LiDAR. Nessun candidato sulla mappa, apposta.\n"
        "pack_cieco.json        elenco completo senza posizioni, con SHA-256.\n\n"
        "Regole di scrittura: vaglio/materiali/ISTRUZIONI.md nel repository.\n"
        "Prima di far uscire un testo: python -m vaglio controlla <file>\n", encoding="utf-8")
    return {"kit": str(out), "figure": written, "candidati": nums["scansione"]["complessi_candidati"]}
