"""Tentativo 11 — integrale di bacino del Mega-Chad (docs/CALIBRAZIONE.md, "direzioni non provate" n.1).

Non cerca una sponda dentro un tile. Chiede al DEM una cosa sola, alla scala giusta:
a che quota la conca del Ciad tracima, da dove, e quanta acqua tiene a quel punto.

Uso:
    python tentativo11_bacino.py <cartella_tile_GLO90> <cartella_output>

I tile sono Copernicus GLO-90 (COG pubblici su S3, nessuna key):
    https://copernicus-dem-90m.s3.amazonaws.com/Copernicus_DSM_COG_30_N{lat}_00_E{lon}_00_DEM/...

Previsione e kill-shot: PREREG-T11.md, scritto e hashato PRIMA di aprire i tile.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage
from skimage.morphology import reconstruction

LAT0, LAT1 = 6, 21      # bbox fissato in pre-registrazione
LON0, LON1 = 8, 23
BLOCK = 4               # 3" -> 12"
PER_TILE = 1200 // BLOCK
EARTH_R_KM = 6371.0088
CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)   # 4-vicini, come core/marine/basin.py
FULL = np.ones((3, 3), bool)                                # 8-vicini, solo per sensibilita'

MAYO_KEBBI = (9.9, 15.0)          # bersaglio P2 (lat, lon)
BODELE_BOX = (16.0, 18.0, 17.0, 19.5)   # lat0, lat1, lon0, lon1: dove cercare il seme


def build_mosaic(tile_dir: Path, how: str) -> np.ndarray:
    """Mosaico a 12". how = 'mean' | 'min'. Riga 0 = nord."""
    nlat, nlon = LAT1 - LAT0, LON1 - LON0
    out = np.full((nlat * PER_TILE, nlon * PER_TILE), np.nan, np.float32)
    for lat in range(LAT0, LAT1):
        for lon in range(LON0, LON1):
            name = f"Copernicus_DSM_COG_30_N{lat:02d}_00_E{lon:03d}_00_DEM.tif"
            with rasterio.open(tile_dir / name) as ds:
                a = ds.read(1).astype(np.float32)
            if a.shape != (1200, 1200):
                raise ValueError(f"{name}: forma inattesa {a.shape}")
            b = a.reshape(PER_TILE, BLOCK, PER_TILE, BLOCK)
            agg = b.mean(axis=(1, 3)) if how == "mean" else b.min(axis=(1, 3))
            r = (LAT1 - 1 - lat) * PER_TILE
            c = (lon - LON0) * PER_TILE
            out[r:r + PER_TILE, c:c + PER_TILE] = agg
    if np.isnan(out).any():
        raise ValueError("buchi nel mosaico")
    return out


def rc_to_latlon(r: float, c: float, shape) -> tuple[float, float]:
    h, w = shape
    return LAT1 - (r + 0.5) * (LAT1 - LAT0) / h, LON0 + (c + 0.5) * (LON1 - LON0) / w


def cell_area_km2(shape) -> np.ndarray:
    """Area sferica per riga: un pixel a 20 N e' il 6% piu' stretto che all'equatore."""
    h, w = shape
    dlat = np.radians((LAT1 - LAT0) / h)
    dlon = np.radians((LON1 - LON0) / w)
    lat = np.radians(LAT1 - (np.arange(h) + 0.5) * (LAT1 - LAT0) / h)
    return (EARTH_R_KM ** 2 * dlat * dlon * np.cos(lat)).astype(np.float64)


def fill(dem: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Priority-flood dal bordo, via ricostruzione morfologica (stesso risultato, in C)."""
    seed = np.full_like(dem, dem.max())
    seed[0, :], seed[-1, :], seed[:, 0], seed[:, -1] = dem[0, :], dem[-1, :], dem[:, 0], dem[:, -1]
    return reconstruction(seed, dem, method="erosion", footprint=footprint).astype(np.float32)


def haversine_km(a, b) -> float:
    la1, lo1, la2, lo2 = map(np.radians, (a[0], a[1], b[0], b[1]))
    h = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return float(2 * EARTH_R_KM * np.arcsin(np.sqrt(h)))


def measure(dem: np.ndarray, footprint: np.ndarray) -> dict:
    h, w = dem.shape
    filled = fill(dem, footprint)

    # seme: cella piu' bassa nel riquadro del Bodele
    la0, la1, lo0, lo1 = BODELE_BOX
    r0, r1 = int((LAT1 - la1) / (LAT1 - LAT0) * h), int((LAT1 - la0) / (LAT1 - LAT0) * h)
    c0, c1 = int((lo0 - LON0) / (LON1 - LON0) * w), int((lo1 - LON0) / (LON1 - LON0) * w)
    sub = dem[r0:r1, c0:c1]
    sr, sc = np.unravel_index(np.argmin(sub), sub.shape)
    sr, sc = sr + r0, sc + c0
    spill = float(filled[sr, sc])

    # conca: regione connessa al seme, allagata alla quota di sfioro
    wet = (filled == filled[sr, sc]) & (dem < filled[sr, sc])
    lab, _ = ndimage.label(wet, structure=footprint)
    mask = lab == lab[sr, sc]
    truncated = bool(mask[0].any() or mask[-1].any() or mask[:, 0].any() or mask[:, -1].any())

    # pour point: cella dell'orlo alla quota di sfioro CHE HA UN'USCITA (un vicino che drena
    # sotto lo sfioro). La sola "cella piu' bassa dell'orlo" (basin.pour_point) e' ambigua:
    # ogni cella di riva con dem == sfioro pareggia. Visto sul run 'min', corretto e dichiarato.
    rim = ndimage.binary_dilation(mask, structure=footprint) & ~mask
    exits = ndimage.binary_dilation(filled < filled[sr, sc], structure=footprint)
    cand = rim & exits
    if not cand.any():
        cand = rim
    rr, cc = np.nonzero(cand)
    k = int(np.argmin(dem[rr, cc]))
    pp = rc_to_latlon(rr[k], cc[k], dem.shape)

    area_row = cell_area_km2(dem.shape)
    area = float((mask.sum(axis=1) * area_row).sum())
    depth = np.where(mask, spill - dem, 0.0)
    vol = float((depth.sum(axis=1) * area_row).sum() / 1000.0)   # km3

    return {
        "spill_m": round(spill, 2),
        "seed_latlon": [round(v, 3) for v in rc_to_latlon(sr, sc, dem.shape)],
        "seed_z_m": round(float(dem[sr, sc]), 1),
        "pour_point_latlon": [round(v, 3) for v in pp],
        "pour_point_z_m": round(float(dem[rr[k], cc[k]]), 2),
        "pour_point_km_from_mayo_kebbi": round(haversine_km(pp, MAYO_KEBBI), 1),
        "area_km2": round(area),
        "volume_km3": round(vol),
        "max_depth_m": round(float(depth.max()), 1),
        "truncated": truncated,
        "_mask": mask, "_filled": filled,
    }


def hypsometry(dem: np.ndarray, mask: np.ndarray, levels: np.ndarray) -> list[dict]:
    """A(z) e V(z) dentro la conca finale. Geometria, non cronologia."""
    area_row = cell_area_km2(dem.shape)
    out = []
    for z in levels:
        under = mask & (dem < z)
        a = float((under.sum(axis=1) * area_row).sum())
        v = float((np.where(under, z - dem, 0.0).sum(axis=1) * area_row).sum() / 1000.0)
        out.append({"z_m": float(z), "area_km2": round(a), "volume_km3": round(v, 1)})
    return out


def main(tile_dir: str, out_dir: str) -> None:
    tiles, out = Path(tile_dir), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    report: dict = {"dem": "Copernicus GLO-90, aggregato a 12 arcsec",
                    "bbox_lat_lon": [LAT0, LAT1, LON0, LON1], "runs": {}}
    keep = {}
    for how in ("mean", "min"):
        dem = build_mosaic(tiles, how)
        for conn, fp in (("4", CROSS), ("8", FULL)):
            m = measure(dem, fp)
            key = f"{how}_conn{conn}"
            if key == "mean_conn4":
                keep = {"dem": dem, "mask": m["_mask"], "filled": m["_filled"], "spill": m["spill_m"]}
            report["runs"][key] = {k: v for k, v in m.items() if not k.startswith("_")}
            print(key, json.dumps(report["runs"][key]))

    dem, mask, spill = keep["dem"], keep["mask"], keep["spill"]
    levels = np.arange(160.0, np.floor(spill) + 1.0, 1.0)
    levels = np.append(levels, spill)
    report["hypsometry_mean_conn4"] = hypsometry(dem, mask, levels)
    np.savez_compressed(out / "t11_grids.npz", dem=dem, mask=mask, filled=keep["filled"])
    (out / "t11_report.json").write_text(json.dumps(report, indent=1))
    print("scritto", out / "t11_report.json")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
