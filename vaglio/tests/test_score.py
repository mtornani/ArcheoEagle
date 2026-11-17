"""Test del punteggio del test cieco (test_cieco/score.py). Dati sintetici, nessuna rete."""
import csv
import hashlib
import json
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCORE = Path(__file__).resolve().parents[1] / "test_cieco" / "score.py"


def world(d: Path, catalogue: str):
    """Due transetti quadrati di ~1 km; 120 complessi; un catalogo costruito secondo `catalogue`."""
    rng = random.Random(1)
    fps, dep = [], []
    for t, (lon0, lat0) in {"Centro_GLAS_l0s001": (-89.50, 18.50), "South_NFI_l0s002": (-89.40, 18.60)}.items():
        ring = [[lon0, lat0], [lon0 + 0.0095, lat0], [lon0 + 0.0095, lat0 + 0.009], [lon0, lat0 + 0.009], [lon0, lat0]]
        fps.append({"type": "Feature", "properties": {"transect": t}, "geometry": {"type": "Polygon", "coordinates": [ring]}})
        for _ in range(60):
            dep.append((t, lon0 + rng.uniform(0.001, 0.0085), lat0 + rng.uniform(0.001, 0.008)))
    (d / "fp.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": fps}))
    with open(d / "dep.csv", "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["deposit_id", "transect", "lon", "lat", "radius_m", "extent_m", "area_m2", "n_objects", "max_height_m", "outcome"])
        for k, (t, lon, lat) in enumerate(dep, 1):
            w.writerow([f"D{k:05d}", t, f"{lon:.6f}", f"{lat:.6f}", 35.0, 30, 700, 3, 1.5, "regge_alla_revisione" if k <= 10 else "da_rivedere"])
    cat = []
    if catalogue == "matching":                     # 3 su 4 complessi hanno una struttura entro ~10 m, piu' strutture che noi non vediamo
        for k, (t, lon, lat) in enumerate(dep):
            if k % 4:
                cat.append((lon + rng.uniform(-8e-5, 8e-5), lat + rng.uniform(-8e-5, 8e-5)))
        for t, lon, lat in dep[:40]:
            cat.append((lon + 0.0012, lat))           # circa 125 m piu' in la': non coperte
    else:                                             # strutture messe a caso: nessun legame coi complessi
        for _ in range(150):
            t = rng.choice(fps)["geometry"]["coordinates"][0]
            cat.append((rng.uniform(t[0][0], t[1][0]), rng.uniform(t[0][1], t[2][1])))
    with open(d / "cat.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["id", "lon", "lat"])
        for k, (lon, lat) in enumerate(cat):
            w.writerow([f"S{k}", lon, lat])
    return hashlib.sha256((d / "dep.csv").read_bytes()).hexdigest()


def run(d: Path, digest: str):
    p = subprocess.run([sys.executable, str(SCORE), "--deposit", str(d / "dep.csv"), "--expected-sha256", digest,
                        "--catalog", str(d / "cat.csv"), "--footprints", str(d / "fp.geojson"), "--out", str(d / "res.json")],
                       capture_output=True, text=True)
    return p, (json.loads((d / "res.json").read_text()) if (d / "res.json").exists() else None)


class ScoreTest(unittest.TestCase):
    def test_a_catalogue_that_matches_passes_and_beats_the_nulls(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t); p, r = run(d, world(d, "matching"))
            self.assertEqual(p.returncode, 0, p.stderr)
            # 0,75 per costruzione, di piu' per le coincidenze fra vicini: e' quello che il confronto con lo spostamento misura
            self.assertGreaterEqual(r["precision"]["value"], 0.75)
            self.assertLess(r["precision"]["value"], 0.95)
            self.assertLess(r["nulls_precision"]["jitter_150_300m"]["mean"], 0.5)
            self.assertTrue(r["verdict"]["PASS"])
            self.assertEqual(r["evaluation_area"]["deposit_complexes"], 120)
            self.assertIn("regge_alla_revisione", r["by_review_outcome"])

    def test_a_random_catalogue_fails_because_it_does_not_beat_the_null(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t); p, r = run(d, world(d, "random"))
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertFalse(r["verdict"]["P2"])
            self.assertFalse(r["verdict"]["PASS"])

    def test_a_deposit_changed_after_sealing_is_refused(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t); digest = world(d, "matching")
            with open(d / "dep.csv", "a") as fh:
                fh.write("D99999,Centro_GLAS_l0s001,-89.495,18.505,35,30,700,3,1.5,da_rivedere\n")
            p, r = run(d, digest)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("SHA-256", p.stdout + p.stderr)
            self.assertIsNone(r)

    def test_output_never_contains_coordinates(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t); run(d, world(d, "matching"))
            blob = (d / "res.json").read_text()
            self.assertNotIn("-89.", blob)
            self.assertNotIn('"lat"', blob)


if __name__ == "__main__":
    unittest.main()
