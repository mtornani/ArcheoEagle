#!/usr/bin/env python3
"""Genera immagini colorate, dati e anteprima Open Graph del rapporto pubblico.

Usa solo dati già nel repository (pack cieco, catalogo dei transetti, basemap,
riquadri di controllo di Chactún). Non legge vaglio_lavoro/ e non scrive coordinate
di candidati.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from matplotlib import colormaps
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
CONTROLS = ROOT / "vaglio" / "vaglio" / "data" / "controls"
PACK = ROOT / "vaglio" / "pack_cieco.json"
TRANSECTS = ROOT / "vaglio" / "vaglio" / "data" / "transects.json"
BASEMAP = ROOT / "vaglio" / "vaglio" / "data" / "basemap.json"
SITES = ROOT / "vaglio" / "vaglio" / "data" / "known_sites.csv"

# Riquadri di controllo scelti a vista tra quelli pubblici (Kokalj et al. 2023).
# Sono esempi di come si vede una struttura annotata, non i candidati dello Yucatán.
STRUCTURE_CONTROLS = [
    ("pos_1870_c.jpg", "it-long", "en-long"),
    ("pos_1992_c.jpg", "it-iso", "en-iso"),
    ("pos_2060_c.jpg", "it-plat", "en-plat"),
    ("pos_1812_c.jpg", "it-group", "en-group"),
    ("pos_1962_c.jpg", "it-rect", "en-rect"),
    ("pos_2016_c.jpg", "it-comp", "en-comp"),
    ("pos_1786_c.jpg", "it-group2", "en-group2"),
    ("pos_1851_c.jpg", "it-clust", "en-clust"),
    ("pos_2031_c.jpg", "it-plat2", "en-plat2"),
    ("pos_1767_c.jpg", "it-bodies", "en-bodies"),
]
EMPTY_CONTROLS = [
    "neg_1828_3.jpg",
    "neg_1825_3.jpg",
    "neg_1859_3.jpg",
    "neg_1861_3.jpg",
]

ZONES = {
    "Centro": "Centro: penisola centrale, tra Hopelchén, Peto e Xpujil",
    "South": "South: Campeche interno, tra Hopelchén, Escárcega e Xpujil",
    "Norte": "Norte: nord-ovest, tra Mérida e Campeche",
    "North2": "North2: nord-est, tra Valladolid e Tizimín",
    "OutYuc": "OutYuc: fascia orientale, tra Valladolid e Cancún",
    "Chiaps1": "Chiaps1: Chiapas orientale, tra Comitán e il confine col Guatemala",
    "ChiapsCampeche": "ChiapsCampeche: tra Tenosique ed Escárcega",
}

# Chactún, sito pubblicato (Wikidata Q13518345), già in known_sites.csv
CHACTUN = {"name": "Chactún", "lat": 18.455, "lon": -89.50806, "source": "Wikidata Q13518345"}


def colorize(im: Image.Image, cmap_name: str = "viridis") -> Image.Image:
    """Sky-view in scala di grigi -> rampa viridis (strutture chiare).

    Nei riquadri di controllo le costruzioni appaiono scure (basso sky-view).
    Si inverte il valore, si stira il contrasto e si applica viridis, tenendo
    l'ombreggiatura originale come hillshade.
    """
    gray = im.convert("L")
    a = np.asarray(gray, dtype=np.float32)
    blur = np.asarray(
        gray.resize((gray.width // 2, gray.height // 2), Image.BILINEAR).resize(gray.size, Image.BILINEAR),
        dtype=np.float32,
    )
    mix = 0.65 * blur + 0.35 * a
    elev = 255.0 - mix
    lo, hi = np.percentile(elev, (3, 97))
    t = np.clip((elev - lo) / max(1e-6, hi - lo), 0, 1)
    rgb = colormaps[cmap_name](t)[..., :3]
    shade = 0.40 + 0.60 * (a / 255.0)
    out = np.clip(rgb * shade[..., None] * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGB")


def legend(path: Path, width: int = 640, height: int = 72) -> None:
    cmap = colormaps["viridis"]
    arr = np.zeros((height, width, 3), dtype=np.uint8)
    for x in range(width):
        arr[:, x] = (np.array(cmap(x / (width - 1))[:3]) * 255).astype(np.uint8)
    # darken slightly like the shade blend
    arr = (arr * 0.85).astype(np.uint8)
    img = Image.fromarray(arr, "RGB")
    img.save(path, "PNG")


def reviewed() -> list[dict]:
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    out = []
    for c in pack["candidates"]:
        if c["outcome"] == "da_rivedere":
            continue
        out.append({
            "label": c["label"],
            "outcome": c["outcome"],
            "score": c["score"],
            "n_objects": c["n_objects"],
            "area_m2": c["area_m2"],
            "max_height_m": c["max_height_m"],
            "extent_m": c.get("extent_m"),
            "mean_prob": c["mean_prob"],
            "votes": c["votes"],
            "known": c["known"]["label"],
            "survey": c["survey"],
        })
    order = {"regge_alla_revisione": 0, "incerto": 1, "scartato": 2}
    out.sort(key=lambda c: (order[c["outcome"]], c["label"]))
    return out, pack["hash"], pack["timestamp"]


def coverage() -> dict:
    cat = json.loads(TRANSECTS.read_text(encoding="utf-8"))
    bm = json.loads(BASEMAP.read_text(encoding="utf-8"))
    zones: dict[str, dict] = {}
    strips = []
    for t in cat["transects"]:
        z = t["id"].split("_")[0]
        w, s, e, n = t["bbox"]
        # Non includiamo l'id del transetto (sigla vietata nei materiali).
        strips.append({"zone": z, "bbox": [round(w, 5), round(s, 5), round(e, 5), round(n, 5)]})
        rec = zones.setdefault(z, {"n": 0, "km2": 0.0, "bbox": [180, 90, -180, -90]})
        rec["n"] += 1
        rec["km2"] += t["area_km2"]
        rec["bbox"][0] = min(rec["bbox"][0], w)
        rec["bbox"][1] = min(rec["bbox"][1], s)
        rec["bbox"][2] = max(rec["bbox"][2], e)
        rec["bbox"][3] = max(rec["bbox"][3], n)
    for z, rec in zones.items():
        rec["km2"] = round(rec["km2"], 1)
        rec["label"] = ZONES.get(z, z)
        rec["bbox"] = [round(x, 4) for x in rec["bbox"]]
    return {
        "source_transects": cat.get("source"),
        "source_map": bm.get("source"),
        "zones": zones,
        "strips": strips,
        "coast": bm["coast"],
        "borders": bm["borders"],
        "states": bm["states"],
        "places": [{"name": n, "lat": lat, "lon": lon} for n, lat, lon in bm["places"]],
        "chactun": CHACTUN,
        "n_transects": len(cat["transects"]),
        "km2": round(sum(t["area_km2"] for t in cat["transects"]), 1),
    }


def og_image(chip: Image.Image, cov: dict, dest: Path) -> None:
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), "#1b1630")
    # left panel: colorized chip
    chip = chip.resize((560, 560), Image.LANCZOS)
    img.paste(chip, (20, 35))
    draw = ImageDraw.Draw(img)
    # right text block
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except OSError:
        font_title = font = font_sm = ImageFont.load_default()
    x = 600
    draw.text((x, 50), "Vaglio", font=font_title, fill="#fde725")
    draw.text((x, 110), "Ri-analisi con errori misurati", font=font, fill="#f3f0e7")
    draw.text((x, 148), "del LiDAR pubblico G-LiHT", font=font, fill="#f3f0e7")
    draw.text((x, 186), "sullo Yucatán", font=font, fill="#f3f0e7")
    draw.rectangle((x, 240, 1160, 242), fill="#5e4fa2")
    lines = [
        "11.916  complessi candidati",
        "1.272,7 km²  ·  456 transetti",
        "15  reggono alla revisione",
        "25  restano incerti",
        "0  scartati",
    ]
    y = 260
    for line in lines:
        draw.text((x, y), line, font=font, fill="#e8e4d8")
        y += 40
    draw.text((x, 500), "Ogni candidato si presume già noto.", font=font_sm, fill="#c8c2b2")
    draw.text((x, 532), "Posizioni omesse. Chactún, riquadro di controllo.", font=font_sm, fill="#a39d8f")
    draw.text((x, 580), "Kokalj et al. 2023, CC BY 4.0  ·  viridis", font=font_sm, fill="#7a7468")
    img.save(dest, "JPEG", quality=90, optimize=True)


def main() -> None:
    img_dir = OUT / "img" / "controls"
    img_dir.mkdir(parents=True, exist_ok=True)
    (OUT / "data").mkdir(parents=True, exist_ok=True)
    (OUT / "img").mkdir(parents=True, exist_ok=True)

    manifest = []
    first_chip = None
    for fname, cap_it, cap_en in STRUCTURE_CONTROLS:
        src = CONTROLS / fname
        im = colorize(Image.open(src))
        dest = img_dir / fname
        im.resize((480, 480), Image.LANCZOS).save(dest, "JPEG", quality=86, optimize=True)
        if first_chip is None:
            first_chip = im
        manifest.append({"file": f"img/controls/{fname}", "kind": "struttura", "src": fname})
    for fname in EMPTY_CONTROLS:
        src = CONTROLS / fname
        im = colorize(Image.open(src))
        dest = img_dir / fname
        im.resize((480, 480), Image.LANCZOS).save(dest, "JPEG", quality=86, optimize=True)
        manifest.append({"file": f"img/controls/{fname}", "kind": "vuoto", "src": fname})

    legend(OUT / "img" / "legend-viridis.png")

    revs, pack_hash, pack_ts = reviewed()
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    outcomes = {}
    for c in pack["candidates"]:
        outcomes[c["outcome"]] = outcomes.get(c["outcome"], 0) + 1
    known = {}
    for c in pack["candidates"]:
        k = c["known"]["label"]
        known[k] = known.get(k, 0) + 1

    cov = coverage()
    data = {
        "pack_hash": pack_hash,
        "pack_timestamp": pack_ts,
        "n_candidates": len(pack["candidates"]),
        "outcomes": outcomes,
        "known": known,
        "reviewed": revs,
        "controls": manifest,
        "colormap": "viridis, inverted sky-view + hillshade from the original tile",
        "controls_source": "Kokalj et al. 2023, Sci Data 10:558, CC BY 4.0. Tiles already in vaglio/vaglio/data/controls/.",
    }
    (OUT / "data" / "report.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "data" / "coverage.json").write_text(json.dumps(cov, ensure_ascii=False), encoding="utf-8")

    # JS payloads so the site works without a fetch (file:// or Pages)
    js = (
        "/* Generated by build_assets.py. Public repo data only, no candidate coordinates. */\n"
        f"window.VAGLIO_REPORT = {json.dumps(data, ensure_ascii=False)};\n"
        f"window.VAGLIO_COVERAGE = {json.dumps(cov, ensure_ascii=False)};\n"
    )
    (OUT / "js" / "data.js").write_text(js, encoding="utf-8")

    og_image(first_chip, cov, OUT / "img" / "og.jpg")
    print("wrote assets:", len(manifest), "tiles,", len(revs), "reviewed cards")


if __name__ == "__main__":
    sys.exit(main() or 0)
