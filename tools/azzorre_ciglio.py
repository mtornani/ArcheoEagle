"""Ciglio della piattaforma insulare delle Azzorre (triangolazione/AZZORRE-TERRAZZE.md).
Uso: python azzorre_ciglio.py <cartella con est.tif centro.tif ovest.tif> <out.json>
Dato: EMODnet Bathymetry WCS, coverage emodnet:mean, passo 0.00104167 gradi. Metodo: PREREG-AZZORRE.md."""
import json, sys
import numpy as np, rasterio
from scipy import ndimage

UNITS = {  # nome: (riquadro, lat, lon di un punto a terra)
    "Santa Maria": ("est", 36.97, -25.10), "Sao Miguel": ("est", 37.78, -25.50),
    "Terceira": ("centro", 38.72, -27.20), "Graciosa": ("centro", 39.05, -28.00),
    "Sao Jorge": ("centro", 38.65, -28.05), "Pico": ("centro", 38.47, -28.30), "Faial": ("centro", 38.58, -28.70),
    "Flores": ("ovest", 39.45, -31.20), "Corvo": ("ovest", 39.70, -31.10),
}
PUBLISHED = [(-50, -40), (-80, -70), (-90, -85), (-110, -100), (-140, -120)]  # Santa Maria, Ricchi et al. 2018
CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)


def slope_deg(z, T, lat_mid):
    dy = abs(T.e) * 111194.9
    dx = T.a * 111194.9 * np.cos(np.radians(lat_mid))
    gy, gx = np.gradient(z, dy, dx)
    return np.degrees(np.arctan(np.hypot(gx, gy)))


def analyse(z, T, lat, lon):
    c, r = ~T * (lon, lat); r, c = int(r), int(c)
    lab, _ = ndimage.label(z >= -400, structure=CROSS)
    comp = lab == lab[r, c]
    land = comp & (z > 0)
    sl = slope_deg(z, T, lat)
    cell_km2 = (abs(T.e) * 111.1949) * (T.a * 111.1949 * np.cos(np.radians(lat)))
    edges = np.arange(0, -401, -10)
    rows = []
    for a, b in zip(edges[:-1], edges[1:]):
        m = comp & (z < a) & (z >= b)
        rows.append({"top": int(a), "bot": int(b), "area_km2": round(float(m.sum() * cell_km2), 2),
                     "slope_med": round(float(np.median(sl[m])), 2) if m.sum() >= 20 else None})
    ref = [x["slope_med"] for x in rows if -80 <= x["bot"] and x["top"] <= -20 and x["slope_med"] is not None]
    brk = None
    if ref:
        thr = 2 * float(np.median(ref))
        for i in range(2, len(rows) - 2):
            s = [rows[j]["slope_med"] for j in (i, i + 1, i + 2)]
            if all(v is not None and v > thr for v in s):
                brk = rows[i]["top"]; break
    return {"land_km2": round(float(land.sum() * cell_km2), 1), "shelf_ref_slope": round(float(np.median(ref)), 2) if ref else None,
            "break_m": brk, "bins": rows, "_comp": comp, "_lab": int(lab[r, c])}


def main(folder, out):
    res, seen = {}, {}
    for name, (box, lat, lon) in UNITS.items():
        ds = rasterio.open(f"{folder}/{box}.tif"); z = ds.read(1).astype(np.float32)
        a = analyse(z, ds.transform, lat, lon)
        key = (box, a.pop("_lab")); a.pop("_comp")
        if key in seen:      # stessa componente connessa di un'isola gia' vista: unita' unica
            res[seen[key] + "-" + name] = res.pop(seen[key]); seen[key] = seen[key] + "-" + name; continue
        seen[key] = name; res[name] = a
    sm = res.get("Santa Maria")
    if sm:
        cand = sorted([b for b in sm["bins"] if b["top"] <= -30 and b["bot"] >= -150], key=lambda b: -b["area_km2"])[:3]
        hit = sum(any(lo - 5 <= (b["top"] + b["bot"]) / 2 <= hi + 5 for lo, hi in PUBLISHED) for b in cand)
        sm["control_top3_bins"] = [[b["top"], b["bot"]] for b in cand]; sm["control_hits"] = hit
    json.dump(res, open(out, "w"), indent=1)
    for k, v in res.items():
        print(f"{k:14s} terra {v['land_km2']:7.1f} km2  pend. piattaforma {v['shelf_ref_slope']}  ciglio {v['break_m']}")
    if sm: print("controllo Santa Maria: classi", sm["control_top3_bins"], "centrate:", sm["control_hits"], "/3")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
