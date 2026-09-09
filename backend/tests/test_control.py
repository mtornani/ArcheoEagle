"""Prima di misurare una sponda ignota, lo strumento deve dimostrare due cose:
che vede un gradino quando c'e', e che NON lo vede quando non c'e'.
Il secondo test e' il piu' importante."""
import unittest

import numpy as np

from core.hydro.control import (
    BAMA_RIDGE,
    CONTROL_TILE,
    STEP_SCORE_THRESHOLD,
    level_stats,
    step_profile,
    step_score,
)


def _bench_dem(n=400, seed=20260909):
    """Piana bassa in leggera pendenza, gradino stretto e ripido, piana alta.
    E' la forma di una sponda: due superfici quasi piane separate da un salto.
    Niente rampa perfetta: il terreno vero non e' mai un piano esatto, e una
    rampa esatta non ha dispersione da cui ricavare un riferimento."""
    rng = np.random.default_rng(seed)
    x = np.arange(n, dtype=np.float64) / n
    prof = np.where(
        x < 0.46, 300.0 + 15.0 * (x / 0.46),                  # piana bassa 300->315
        np.where(x < 0.54, 315.0 + 10.0 * ((x - 0.46) / 0.08),  # gradino 315->325
                 325.0 + 15.0 * ((x - 0.54) / 0.46)))          # piana alta 325->340
    return np.tile(prof, (n, 1)) + rng.normal(0.0, 0.15, (n, n))


def _uniform_ramp_dem(n=400, low=300.0, high=340.0, noise=0.0, seed=1):
    """Pendenza costante: nessuna quota e' speciale. Questo e' il null."""
    dem = np.tile(np.linspace(low, high, n), (n, 1))
    if noise:
        dem = dem + np.random.default_rng(seed).normal(0.0, noise, (n, n))
    return dem


class StepDetectionTest(unittest.TestCase):
    def test_finds_the_step_it_was_given(self):
        dem = _bench_dem()
        res = step_score(dem, 320.0)
        self.assertIsNotNone(res["step_score"])
        self.assertGreaterEqual(res["step_score"], STEP_SCORE_THRESHOLD)
        self.assertTrue(res["is_step"])

    def test_plateau_level_is_not_a_step(self):
        """Sulla piana, alla stessa quota di un bordo, non c'e' gradino."""
        dem = _bench_dem()
        res = step_score(dem, 305.0)
        self.assertIsNotNone(res["step_score"])
        self.assertLess(res["step_score"], STEP_SCORE_THRESHOLD)


class NullTest(unittest.TestCase):
    """Il test che impedisce di ripetere il difetto di rho: un punteggio a
    percentile mette sempre qualcosa al primo posto, anche nel rumore puro."""

    def test_perfect_ramp_refuses_to_score_instead_of_guessing(self):
        """Rampa esatta: ogni quota da' una banda identica alle vicine, non c'e'
        niente da cui ricavare un riferimento. La risposta onesta e' None con la
        ragione, non un numero tirato a caso."""
        dem = _uniform_ramp_dem()
        res = step_score(dem, 320.0)
        self.assertIsNone(res["step_score"])
        self.assertIn("dispersione", res["reason"])

    def test_noisy_ramp_has_no_step_at_any_level(self):
        """Con del rumore il punteggio si calcola davvero — e deve restare
        basso a ogni quota: su pendenza costante non ci sono gradini."""
        dem = _uniform_ramp_dem(noise=0.3, seed=20260909)
        scored = 0
        for lvl in (308.0, 314.0, 320.0, 326.0, 332.0):
            res = step_score(dem, lvl)
            if res["step_score"] is None:
                continue
            scored += 1
            self.assertLess(
                res["step_score"], STEP_SCORE_THRESHOLD,
                f"gradino inventato a {lvl} m su una rampa a pendenza costante",
            )
        self.assertGreaterEqual(scored, 3, "il null non ha valutato niente: test vuoto")


class HonestAbsenceTest(unittest.TestCase):
    def test_level_outside_the_dem_is_none_not_zero(self):
        dem = _bench_dem()
        res = step_score(dem, 900.0)
        self.assertIsNone(res["step_score"])
        self.assertIn("nessun terreno", res["reason"])

    def test_flat_dem_cannot_discriminate(self):
        dem = np.full((100, 100), 320.0)
        res = step_score(dem, 320.0)
        self.assertIsNone(res["step_score"])

    def test_level_stats_returns_none_where_there_is_no_terrain(self):
        dem = _bench_dem()
        self.assertIsNone(level_stats(dem, 900.0))


class ProfileTest(unittest.TestCase):
    def test_profile_skips_empty_levels_without_faking_them(self):
        dem = _bench_dem()
        prof = step_profile(dem, [300.0, 320.0, 340.0, 900.0])
        self.assertEqual(len(prof), 3)
        self.assertNotIn(900.0, [p.level_m for p in prof])


class PositiveControlFixtureTest(unittest.TestCase):
    def test_bama_is_pinned_to_the_published_levels(self):
        self.assertEqual(BAMA_RIDGE["levels_m"], (320.0, 335.0, 338.0))
        self.assertEqual(BAMA_RIDGE["tile"], (11, 13))
        self.assertEqual(BAMA_RIDGE["grade"], "literature")
        self.assertIn("OSL", BAMA_RIDGE["source"])

    def test_control_tile_is_not_the_bama_tile(self):
        self.assertNotEqual(CONTROL_TILE, BAMA_RIDGE["tile"])


if __name__ == "__main__":
    unittest.main()


class MetricTest(unittest.TestCase):
    """Il DEM sta in gradi, non in metri. Trattare la griglia come euclidea usa
    un righello che si accorcia verso i poli: piccolo dentro un tile, ma rende
    non confrontabili corridoi a latitudini diverse — che e' cio' che il tool fa."""

    def test_pixel_width_shrinks_with_latitude(self):
        from core.hydro.control import pixel_metres
        shape = (100, 100)
        dx_eq, dy = pixel_metres([0.0, 0.0, 1.0, 1.0], shape)
        dx_31, _ = pixel_metres([0.0, 31.0, 1.0, 32.0], shape)
        self.assertAlmostEqual(float(dx_eq.mean()) / dy, 1.0, places=2)
        self.assertLess(float(dx_31.mean()) / dy, 0.87)

    def test_no_bbox_means_pixel_units_declared_not_guessed(self):
        from core.hydro.control import pixel_metres
        self.assertIsNone(pixel_metres(None, (10, 10)))

    def test_slope_is_dimensionless_when_georeferenced(self):
        """Rampa di 40 m su 1 grado all'equatore: la pendenza vera e' ~40/111km."""
        from core.hydro.control import _slope_map
        n = 200
        dem = np.tile(np.linspace(300.0, 340.0, n), (n, 1))
        bbox = [0.0, 0.0, 1.0, 1.0]
        s_geo = float(np.median(_slope_map(dem, bbox)))
        s_px = float(np.median(_slope_map(dem, None)))
        # 40 m distribuiti su n-1 intervalli, pixel largo 1 grado / n
        atteso = (40.0 / (n - 1)) / (111194.9 / n)
        self.assertAlmostEqual(s_geo / atteso, 1.0, places=3)
        self.assertGreater(s_px, s_geo * 100)  # m/pixel: tutt'altra scala

    def test_same_terrain_at_two_latitudes_scores_differently_in_pixels(self):
        """La correzione non e' cosmetica: senza, lo stesso terreno a latitudini
        diverse da' pendenze diverse solo per via del reticolo."""
        from core.hydro.control import _slope_map
        n = 200
        dem = np.tile(np.linspace(300.0, 340.0, n), (n, 1))
        s_low = float(np.median(_slope_map(dem, [0.0, 11.0, 1.0, 12.0])))
        s_high = float(np.median(_slope_map(dem, [0.0, 31.0, 1.0, 32.0])))
        self.assertGreater(s_high / s_low, 1.1)  # ~14% di differenza reale
