"""Crea versioni a file unico, interattive e offline, delle due pagine web.

Uso, da vaglio/materiali/uscite/:   python offline.py
Scrive scaricabili/Sotto_la_foresta.html e scaricabili/Vaglio_rapporto.html:
immagini e caratteri incorporati, nessuna risorsa esterna. Si aprono con
qualunque browser, anche senza rete.
"""
from __future__ import annotations

import base64
import re
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "scaricabili"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def data_uri(p: Path) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode()


def inline_fonts(html: str) -> str:
    """Sostituisce il <link> di Google Fonts con @font-face incorporati (solo alfabeti latini)."""
    m = re.search(r'<link rel="stylesheet" href="(https://fonts\.googleapis\.com/[^"]+)">', html)
    if not m:
        return html
    req = urllib.request.Request(m.group(1).replace("&amp;", "&"), headers={"User-Agent": UA})
    css = urllib.request.urlopen(req, timeout=60).read().decode()
    blocks = re.findall(r"/\* (latin(?:-ext)?) \*/\s*(@font-face \{.*?\})", css, flags=re.S)
    out = []
    for _, block in blocks:
        url = re.search(r"url\((https://[^)]+)\)", block).group(1)
        font = base64.b64encode(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60).read()).decode()
        out.append(block.replace(url, "data:font/woff2;base64," + font))
    html = re.sub(r'<link rel="preconnect"[^>]*>\n?', "", html)
    return html.replace(m.group(0), "<style>\n" + "\n".join(out) + "\n</style>")


def build(src: Path, folder: str, dyn: list[tuple[str, str]], dest: Path) -> None:
    html = src.read_text(encoding="utf-8")
    base = src.parent
    files = sorted((base / folder).glob("*.jpg"))
    table = {f"{folder}/{f.name}": data_uri(f) for f in files}
    # attributi src statici: ogni immagine e' salvata una volta sola, nella tabella IMG, e assegnata all'avvio
    html = re.sub(rf'src="({folder}/[^"]+\.jpg)"', lambda m: f'data-src="{m.group(1)}"', html)
    # percorsi costruiti dal codice: passano da una tabella incorporata
    for old, new in dyn:
        assert html.count(old) >= 1, old
        html = html.replace(old, new)
    boot = ("<script>\nconst IMG = " + __import__("json").dumps(table) + ";\n"
            "document.querySelectorAll('img[data-src]').forEach((i) => { i.src = IMG[i.dataset.src]; });\n</script>\n")
    html = html.replace("<script>\n(() => {", boot + "<script>\n(() => {", 1)
    html = inline_fonts(html)
    assert "fonts.googleapis" not in html and ' src="img/' not in html and ' src="figure/' not in html
    dest.write_text("<!doctype html>\n<html lang=\"it\">\n<head>\n<meta charset=\"utf-8\">\n"
                    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
                    + html.replace("</style>", "</style>", 1) + "\n</html>\n", encoding="utf-8")
    print(dest.name, round(dest.stat().st_size / 1e6, 1), "MB")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    build(HERE / "pubblico" / "index.html", "img",
          [("img.src = `img/prova_${k + 1}.jpg`;", "img.src = IMG[`img/prova_${k + 1}.jpg`];")],
          OUT / "Sotto_la_foresta.html")
    build(HERE / "rapporto" / "index.html", "figure",
          [("img.src = `figure/regge_${n}.jpg`;", "img.src = IMG[`figure/regge_${n}.jpg`];")],
          OUT / "Vaglio_rapporto.html")


if __name__ == "__main__":
    main()
