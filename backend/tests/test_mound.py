"""Banco tumuli (CLAUDE.md §13). Offline. Il DEM qui e' una FIXTURE di test:
serve a verificare l'aritmetica, non a sostenere un claim."""
import unittest

import numpy as np

from core.anthro import mound


def scene(with_mounds: bool, seed: int = 0):
    rng = np.random.default_rng(seed)
    n = 1200
    yy, xx = np.mgrid[0:n, 0:n]
    dem = 400 + 0.01 * xx + rng.normal(0, 0.4, (n, n))  # piano inclinato + rumore
    sites = []
    bbox = [40.0, 36.0, 40.0 + n / 3600, 36.0 + n / 3600]
    for k in range(60):
        r, c = rng.integers(40, n - 40, 2)
        lon = bbox[0] + (c + 0.5) / n * (bbox[2] - bbox[0])
        lat = bbox[3] - (r + 0.5) / n * (bbox[3] - bbox[1])
        tall = k % 2 == 0
        if with_mounds and tall:
            dem += 12 * np.exp(-((yy - r) ** 2 + (xx - c) ** 2) / (2 * 4.0 ** 2))
        sites.append((lon, lat, 12.0 if tall else float("nan")))
    return dem, bbox, sites


def run(dem, bbox, sites):
    s = mound.cell_scores(mound.residual_relief(dem))
    return mound.evaluate(s, mound.label_cells(s.shape, bbox, sites))


class MoundBenchTest(unittest.TestCase):
    def test_finds_mounds_it_was_given_and_not_flat_sites(self):
        out = run(*scene(True))
        self.assertTrue(out["passed"])
        self.assertGreater(out["recall_tall"], 0.9)
        self.assertLess(out["recall_low"], 0.05)

    def test_no_relief_means_no_pass(self):
        # stessi "siti" in catalogo, nessun tumulo nel terreno: deve fallire
        out = run(*scene(False))
        self.assertFalse(out["passed"])
        self.assertLess(out["recall_tall"], 0.1)

    def test_false_alarm_rate_is_what_was_declared(self):
        dem, bbox, sites = scene(True)
        s = mound.cell_scores(mound.residual_relief(dem))
        lab = mound.label_cells(s.shape, bbox, sites)
        out = mound.evaluate(s, lab)
        self.assertAlmostEqual(out["false_alarms"] / out["n_empty"], mound.FPR, delta=0.002)

    def test_refuses_to_score_with_too_few_cases(self):
        dem, bbox, sites = scene(True)
        self.assertIsNone(run(dem, bbox, sites[:6])["passed"])

    def test_v2_same_bump_scores_lower_on_rough_ground(self):
        dem, bbox, sites = scene(True)
        rough = dem + np.random.default_rng(1).normal(0, 6.0, dem.shape)
        z_flat = mound.cell_scores_v2(mound.residual_relief(dem))
        z_rough = mound.cell_scores_v2(mound.residual_relief(rough))
        lab = mound.label_cells(z_flat.shape, bbox, sites)
        self.assertGreater(np.median(z_flat[lab["tall"]]), 2 * np.median(z_rough[lab["tall"]]))
        self.assertTrue(mound.evaluate(z_flat, lab, "flat", mound.PASS_RECALL_TALL_V2)["passed"])

    def test_regional_slope_is_not_a_mound(self):
        dem, _, _ = scene(False)
        self.assertLess(np.abs(mound.residual_relief(dem)).max(), 5.0)


if __name__ == "__main__":
    unittest.main()
