#!/usr/bin/env python3
"""Blind-test scorer for Vaglio (see PREREGISTRATION.md). Run by the key holder.

Standard library only (Python 3.8+). pyproj is needed only if the catalogue is in
projected coordinates (pass --catalog-epsg).

    python score.py --deposit deposito.csv --expected-sha256 <hash from DEPOSIT.md> \
                    --catalog my_catalogue.geojson --footprints footprints.geojson \
                    [--transects test_transects.txt] [--exclude excluded.txt] \
                    [--catalog-epsg 32616] --out results.json

Inputs
  deposit     the sealed CSV received privately from the Vaglio operator.
  catalogue   the key: CSV with lon,lat (or x,y + --catalog-epsg) and an optional id
              column, or GeoJSON with Point / Polygon / MultiPolygon features
              (polygons are reduced to their centroid).
  footprints  transect boundary polygons (WGS84), shipped next to this script.
  transects   optional: one transect id per line = the evaluation area. Default: all.
  exclude     optional: transect ids excluded by the key holder, declared before scoring.

Nothing is sent anywhere. The output JSON contains only aggregate numbers plus the
deposit_ids and catalogue ids that did not match, for the key holder's own inspection.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import sys
from collections import defaultdict
from datetime import datetime, timezone

# ---- pre-registered constants (PREREGISTRATION.md, section 5). Do not edit. ----
N_NULL = 200            # repetitions of each null model
N_BOOT = 2000           # bootstrap resamples of complexes
JITTER_MIN_M, JITTER_MAX_M = 150.0, 300.0
SEED = 20261117
PASS = {"P1_precision_min": 0.60, "P2_margin_over_jitter_min": 0.20, "P3_coverage_min": 0.30}

M_PER_DEG_LAT = 110_574.0


def m_per_deg_lon(lat: float) -> float:
    return 111_320.0 * math.cos(math.radians(lat))


# ------------------------------------------------------------------------- geometry
def point_in_ring(x: float, y: float, ring) -> bool:
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-300) + xi:
            inside = not inside
        j = i
    return inside


class Footprint:
    def __init__(self, ring):
        self.ring = ring
        xs, ys = [p[0] for p in ring], [p[1] for p in ring]
        self.bbox = (min(xs), min(ys), max(xs), max(ys))

    def contains(self, lon: float, lat: float) -> bool:
        w, s, e, n = self.bbox
        return w <= lon <= e and s <= lat <= n and point_in_ring(lon, lat, self.ring)

    def random_point(self, rng: random.Random):
        w, s, e, n = self.bbox
        for _ in range(10_000):
            lon, lat = rng.uniform(w, e), rng.uniform(s, n)
            if point_in_ring(lon, lat, self.ring):
                return lon, lat
        raise RuntimeError("could not sample inside footprint")


def centroid(geom):
    t = geom["type"]
    if t == "Point":
        return geom["coordinates"][:2]
    rings = [geom["coordinates"][0]] if t == "Polygon" else [p[0] for p in geom["coordinates"]] if t == "MultiPolygon" else None
    if rings is None:
        raise ValueError(f"unsupported geometry {t}")
    a = cx = cy = 0.0
    for ring in rings:
        for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
            f = x1 * y2 - x2 * y1
            a += f; cx += (x1 + x2) * f; cy += (y1 + y2) * f
    if abs(a) < 1e-18:
        pts = [p for r in rings for p in r]
        return [sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)]
    return [cx / (3 * a), cy / (3 * a)]


class Grid:
    """Spatial hash in metres around a reference latitude: fast 'anything within r' queries."""
    def __init__(self, pts, cell_m: float, lat0: float):
        self.kx, self.ky, self.cell = m_per_deg_lon(lat0), M_PER_DEG_LAT, cell_m
        self.cells = defaultdict(list)
        for i, (lon, lat) in enumerate(pts):
            self.cells[self.key(lon, lat)].append((lon * self.kx, lat * self.ky, i))

    def key(self, lon, lat):
        return (int(lon * self.kx // self.cell), int(lat * self.ky // self.cell))

    def within(self, lon, lat, r):
        x, y = lon * self.kx, lat * self.ky
        cx, cy = self.key(lon, lat)
        n = int(r // self.cell) + 1
        hits = []
        for dx in range(-n, n + 1):
            for dy in range(-n, n + 1):
                for px, py, i in self.cells.get((cx + dx, cy + dy), ()):
                    if (px - x) ** 2 + (py - y) ** 2 <= r * r:
                        hits.append(i)
        return hits


# ------------------------------------------------------------------------- loading
def load_deposit(path, expected):
    blob = open(path, "rb").read()
    digest = hashlib.sha256(blob).hexdigest()
    if expected and digest != expected.lower():
        sys.exit(f"STOP: deposit SHA-256 is {digest}, the pre-registered one is {expected}. The file was changed or is not the deposited one.")
    rows = list(csv.DictReader(blob.decode("utf-8").splitlines()))
    for r in rows:
        r["lon"], r["lat"], r["radius_m"] = float(r["lon"]), float(r["lat"]), float(r["radius_m"])
    return rows, digest


def load_catalog(path, epsg):
    pts, ids = [], []
    if path.lower().endswith((".geojson", ".json")):
        gj = json.load(open(path, encoding="utf-8"))
        for k, f in enumerate(gj["features"]):
            if not f.get("geometry"):
                continue
            pts.append(centroid(f["geometry"]))
            props = f.get("properties") or {}
            ids.append(str(props.get("id", props.get("ID", k))))
    else:
        with open(path, encoding="utf-8-sig") as fh:
            rd = csv.DictReader(fh)
            cols = {c.lower(): c for c in rd.fieldnames}
            xk = cols.get("lon") or cols.get("longitude") or cols.get("x")
            yk = cols.get("lat") or cols.get("latitude") or cols.get("y")
            ik = cols.get("id")
            if not (xk and yk):
                sys.exit("catalogue CSV needs lon,lat or x,y columns")
            for k, r in enumerate(rd):
                pts.append([float(r[xk]), float(r[yk])])
                ids.append(str(r[ik]) if ik else str(k))
    if epsg:
        from pyproj import Transformer
        tr = Transformer.from_crs(int(epsg), 4326, always_xy=True)
        pts = [list(tr.transform(x, y)) for x, y in pts]
    bad = [p for p in pts if not (-180 <= p[0] <= 180 and -90 <= p[1] <= 90)]
    if bad:
        sys.exit("catalogue coordinates are not lon/lat: pass --catalog-epsg with the catalogue's EPSG code")
    return pts, ids


def read_list(path):
    if not path:
        return None
    return {line.strip() for line in open(path, encoding="utf-8") if line.strip() and not line.startswith("#")}


# ------------------------------------------------------------------------- scoring
def precision(points, radii, grid):
    return [1 if grid.within(lon, lat, r) else 0 for (lon, lat), r in zip(points, radii)]


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 4), round(c + h, 4))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deposit", required=True)
    ap.add_argument("--expected-sha256", default="")
    ap.add_argument("--catalog", required=True)
    ap.add_argument("--catalog-epsg", default="")
    ap.add_argument("--footprints", required=True)
    ap.add_argument("--transects", default="")
    ap.add_argument("--exclude", default="")
    ap.add_argument("--out", default="results.json")
    a = ap.parse_args()
    if not a.expected_sha256:
        print("WARNING: --expected-sha256 not given; the deposit is not checked against the pre-registered fingerprint.", file=sys.stderr)

    deposit, digest = load_deposit(a.deposit, a.expected_sha256)
    cat_pts, cat_ids = load_catalog(a.catalog, a.catalog_epsg)
    fp = {f["properties"]["transect"]: Footprint(f["geometry"]["coordinates"][0]) for f in json.load(open(a.footprints))["features"]}
    area = read_list(a.transects) or set(fp)
    excluded = read_list(a.exclude) or set()
    unknown = (area | excluded) - set(fp)
    if unknown:
        sys.exit(f"unknown transect ids: {sorted(unknown)[:5]}")
    area -= excluded

    # evaluation area: inside the chosen footprints only, for both sides
    dep = [r for r in deposit if r["transect"] in area and fp[r["transect"]].contains(r["lon"], r["lat"])]
    dropped_dep = sum(1 for r in deposit if r["transect"] in area) - len(dep)
    cat_in, cat_tr = [], []
    for (lon, lat), cid in zip(cat_pts, cat_ids):
        t = next((t for t in area if fp[t].contains(lon, lat)), None)
        if t:
            cat_in.append(((lon, lat), cid)); cat_tr.append(t)
    if not dep or not cat_in:
        sys.exit(f"nothing to score: {len(dep)} deposit rows and {len(cat_in)} catalogue points in the evaluation area")

    lat0 = sum(r["lat"] for r in dep) / len(dep)
    cgrid = Grid([p for p, _ in cat_in], 100.0, lat0)
    dpts, drad = [(r["lon"], r["lat"]) for r in dep], [r["radius_m"] for r in dep]
    hit = precision(dpts, drad, cgrid)

    # coverage: catalogue points within the radius of at least one complex
    rmax = max(drad)
    dgrid = Grid(dpts, 100.0, lat0)
    covered = []
    for (lon, lat), _ in cat_in:
        cand = dgrid.within(lon, lat, rmax)
        kx, ky = m_per_deg_lon(lat0), M_PER_DEG_LAT
        covered.append(1 if any(((dpts[i][0] - lon) * kx) ** 2 + ((dpts[i][1] - lat) * ky) ** 2 <= drad[i] ** 2 for i in cand) else 0)

    rng = random.Random(SEED)
    # null 1: same number of complexes per transect, same radii, uniform inside the footprint
    # null 2: each complex moved 150-300 m in a random direction, kept inside its own footprint
    def null(kind):
        vals = []
        for _ in range(N_NULL):
            pts = []
            for r in dep:
                f = fp[r["transect"]]
                if kind == "uniform":
                    pts.append(f.random_point(rng)); continue
                for _ in range(500):
                    d, th = rng.uniform(JITTER_MIN_M, JITTER_MAX_M), rng.uniform(0, 2 * math.pi)
                    lon = r["lon"] + d * math.cos(th) / m_per_deg_lon(r["lat"])
                    lat = r["lat"] + d * math.sin(th) / M_PER_DEG_LAT
                    if f.contains(lon, lat):
                        pts.append((lon, lat)); break
                else:
                    pts.append(f.random_point(rng))
            vals.append(sum(precision(pts, drad, cgrid)) / len(pts))
        vals.sort()
        return {"mean": round(sum(vals) / len(vals), 4), "p2.5": round(vals[int(0.025 * len(vals))], 4), "p97.5": round(vals[int(0.975 * len(vals)) - 1], 4)}

    nulls = {"uniform": null("uniform"), "jitter_150_300m": null("jitter")}
    boots = sorted(sum(hit[rng.randrange(len(hit))] for _ in hit) / len(hit) for _ in range(N_BOOT))
    prec = sum(hit) / len(hit)
    cov = sum(covered) / len(covered)
    ci = (round(boots[int(0.025 * N_BOOT)], 4), round(boots[int(0.975 * N_BOOT) - 1], 4))

    p1 = prec >= PASS["P1_precision_min"]
    p2 = (prec - nulls["jitter_150_300m"]["mean"] >= PASS["P2_margin_over_jitter_min"]) and ci[0] > nulls["jitter_150_300m"]["p97.5"]
    p3 = cov >= PASS["P3_coverage_min"]

    def group(key):
        g = defaultdict(lambda: [0, 0])
        for r, h in zip(dep, hit):
            g[key(r)][0] += h; g[key(r)][1] += 1
        return {k: {"complexes": n, "with_catalogue_structure": h, "precision": round(h / n, 4), "ci95": wilson(h, n)} for k, (h, n) in sorted(g.items())}

    res = {
        "scored_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "deposit_sha256": digest, "deposit_checked_against_preregistration": bool(a.expected_sha256),
        "evaluation_area": {"transects": len(area), "excluded_by_key_holder": sorted(excluded),
                            "deposit_complexes": len(dep), "deposit_rows_outside_footprint_dropped": dropped_dep,
                            "catalogue_points": len(cat_in)},
        "precision": {"value": round(prec, 4), "ci95_bootstrap": ci, "complexes_with_catalogue_structure": sum(hit)},
        "coverage": {"value": round(cov, 4), "ci95": wilson(sum(covered), len(covered)), "catalogue_points_covered": sum(covered)},
        "nulls_precision": nulls,
        "by_review_outcome": group(lambda r: r["outcome"]),
        "by_flight_block": group(lambda r: r["transect"].split("_")[0]),
        "pre_registered_criteria": PASS,
        "verdict": {"P1": p1, "P2": p2, "P3": p3, "PASS": p1 and p2 and p3},
        "for_key_holder_only": {
            "unmatched_deposit_ids": [r["deposit_id"] for r, h in zip(dep, hit) if not h],
            "uncovered_catalogue_ids": [cid for (_, cid), c in zip(cat_in, covered) if not c],
        },
    }
    json.dump(res, open(a.out, "w", encoding="utf-8"), indent=1)
    v = res["verdict"]
    print(f"area: {len(area)} transects · {len(dep)} complexes · {len(cat_in)} catalogue points")
    print(f"precision {prec:.3f} (95% {ci[0]:.3f}-{ci[1]:.3f}) · jitter null {nulls['jitter_150_300m']['mean']:.3f} · uniform null {nulls['uniform']['mean']:.3f}")
    print(f"coverage {cov:.3f}")
    print(f"P1 {'pass' if v['P1'] else 'FAIL'} · P2 {'pass' if v['P2'] else 'FAIL'} · P3 {'pass' if v['P3'] else 'FAIL'} -> {'PASS' if v['PASS'] else 'FAIL'}")
    print(f"written {a.out}. Share the whole file except 'for_key_holder_only' if you prefer.")


if __name__ == "__main__":
    main()
