"""Soglie e sfioratori. Il modulo nasce corretto da un dubbio: Vajont e il
Nepal 2026 uccidono per MASSA che si muove, non per acqua che supera un orlo,
e la catastrofe e' lineare e a valle. Qui si testa che la stessa primitiva
serva sia il riempimento sia il rilascio."""
import unittest

import numpy as np

from core.marine.basin import (
    collapse_source_potential,
    largest_depression,
    depression_at,
    hypsometry,
    pour_point,
    priority_flood,
    spillway_path,
)


def _box_basin(n=60, wall=200.0, floor=100.0, notch=118.0, notch_rc=(30, 59)):
    """Scatola a fondo piatto con UNA sola tacca nell'orlo. Non ambigua:
    la fixture del primo tentativo aveva l'orlo tutto alla stessa quota."""
    dem = np.full((n, n), wall)
    dem[5:n - 5, 5:n - 5] = floor
    dem[notch_rc] = notch
    # corridoio dal fondo fino alla tacca, sotto la quota di sfioro
    dem[notch_rc[0], n - 5:n - 1] = floor + 5.0
    return dem


class PourPointTest(unittest.TestCase):
    def test_finds_the_single_notch(self):
        dem = _box_basin()
        b = depression_at(dem, (30, 30))
        self.assertIsNotNone(b)
        self.assertAlmostEqual(b["spill_level"], 118.0, places=6)
        pp = pour_point(dem, b)
        self.assertAlmostEqual(pp["level"], 118.0, places=6)
        self.assertEqual((pp["row"], pp["col"]), (30, 59))

    def test_lower_of_two_notches_wins(self):
        dem = _box_basin()
        dem[10, 59] = 112.0
        dem[10, 55:59] = 105.0
        b = depression_at(dem, (30, 30))
        self.assertAlmostEqual(b["spill_level"], 112.0, places=6)

    def test_seed_not_in_a_depression_returns_none(self):
        """Su un pendio non c'e' conca. Nessuna conca inventata."""
        dem = np.tile(np.linspace(100.0, 200.0, 50), (50, 1))
        self.assertIsNone(depression_at(dem, (25, 25)))

    def test_seed_outside_the_grid_returns_none(self):
        self.assertIsNone(depression_at(_box_basin(), (999, 999)))


class TruncationTest(unittest.TestCase):
    """Una conca che tocca il bordo della finestra puo' avere una soglia falsa,
    prodotta dal ritaglio. Va dichiarato, non nascosto — e' lo stesso errore che
    in CALIBRAZIONE.md aveva prodotto un falso positivo."""

    def test_basin_touching_the_edge_is_flagged(self):
        dem = np.full((40, 40), 200.0)
        dem[:, 5:35] = 100.0     # valle che esce da sopra e da sotto
        b = depression_at(dem, (20, 20))
        if b is not None:
            self.assertTrue(b["truncated"])
            self.assertIn("artefatto", b["warning"])

    def test_enclosed_basin_is_not_flagged(self):
        b = depression_at(_box_basin(), (30, 30))
        self.assertFalse(b["truncated"])
        self.assertIsNone(b["warning"])


class SpillwayTest(unittest.TestCase):
    """Meccanismo 3: il bacino si svuota e la distruzione e' A VALLE. Il
    modello originale, che guardava solo il riempimento, non la vedeva."""

    def test_path_goes_downhill_and_leaves_the_basin(self):
        n = 60
        dem = _box_basin(n=n)
        # versante esterno che scende verso destra oltre l'orlo
        for c in range(n - 1, n - 12, -1):
            dem[28:33, c] = 118.0 - (n - 1 - c) * 3.0
        path = spillway_path(dem, (30, 59))
        self.assertGreater(len(path), 3)
        quote = [dem[r, c] for r, c in path]
        self.assertTrue(all(b <= a + 1e-9 for a, b in zip(quote, quote[1:])),
                        "il percorso deve solo scendere")

    def test_flat_terrain_gives_no_path(self):
        dem = np.full((20, 20), 50.0)
        self.assertEqual(len(spillway_path(dem, (10, 10))), 1)


class HypsometryTest(unittest.TestCase):
    """L'integrale di bacino: area e volume in funzione della quota."""

    def test_volume_grows_with_level(self):
        dem = _box_basin()
        b = depression_at(dem, (30, 30))
        curva = hypsometry(dem, b["mask"], [100.0, 105.0, 110.0, 115.0])
        vols = [c["volume"] for c in curva]
        self.assertTrue(all(x < y for x, y in zip(vols, vols[1:])))

    def test_below_the_floor_there_is_no_water(self):
        dem = _box_basin()
        b = depression_at(dem, (30, 30))
        c = hypsometry(dem, b["mask"], [90.0])[0]
        self.assertEqual(c["area_cells"], 0)
        self.assertEqual(c["volume"], 0.0)


class CollapseSourceTest(unittest.TestCase):
    """Meccanismo 2 (Vajont, Storegga): una massa cade in acqua e la sposta.
    Qui si trova solo la SORGENTE possibile; l'onda e il suo deposito stanno
    nella stratigrafia, e questo modulo non li vede. Limite dichiarato."""

    def test_steep_rim_scores_higher_than_gentle_rim(self):
        n = 40
        acqua = np.zeros((n, n), bool)
        acqua[15:25, 15:25] = True
        dolce = np.zeros((n, n))
        yy, xx = np.mgrid[0:n, 0:n]
        dolce = 0.01 * np.abs(xx - 20)
        ripido = 3.0 * np.abs(xx - 20)
        self.assertGreater(collapse_source_potential(ripido, acqua),
                           collapse_source_potential(dolce, acqua))

    def test_no_water_means_zero_not_a_guess(self):
        self.assertEqual(
            collapse_source_potential(np.zeros((10, 10)), np.zeros((10, 10), bool)), 0.0)


class PriorityFloodTest(unittest.TestCase):
    def test_filled_never_below_terrain(self):
        rng = np.random.default_rng(20260910)
        dem = rng.normal(100.0, 10.0, (40, 40))
        filled = priority_flood(dem)
        self.assertTrue(np.all(filled >= dem - 1e-9))

    def test_monotone_slope_has_no_depressions(self):
        dem = np.tile(np.linspace(100.0, 200.0, 40), (40, 1))
        filled = priority_flood(dem)
        self.assertLess(float(np.max(filled - dem)), 1e-6)


if __name__ == "__main__":
    unittest.main()


class SlopeUnitsTest(unittest.TestCase):
    """Regressione del 13 set 2026: np.gradient da' metri per PIXEL, non m/m.
    Su DEM decimato (pixel ~240 m) qualunque terreno superava steep=0.30 e la
    funzione tornava ~1.0 ovunque. Ha rotto il primo screening dei bacini."""

    def _ramp(self, rise_per_pixel=20.0, n=24):
        # rampa attorno a una conca: 20 m di dislivello per pixel.
        dem = np.zeros((n, n))
        for c in range(n):
            dem[:, c] = abs(c - n // 2) * rise_per_pixel
        acqua = np.zeros((n, n), bool)
        acqua[8:16, 10:14] = True
        return dem, acqua

    def test_metric_pixels_change_the_answer(self):
        dem, acqua = self._ramp()
        # 20 m per pixel: in unita' pixel e' 20 >> 0.30 -> tutto ripido.
        senza = collapse_source_potential(dem, acqua)
        # con pixel da 240 m la pendenza vera e' 20/240 = 0.083 < 0.30.
        con = collapse_source_potential(dem, acqua, px_m=240.0, py_m=240.0)
        self.assertGreater(senza, 0.9)
        self.assertEqual(con, 0.0)

    def test_the_same_terrain_at_finer_pixels_is_steeper(self):
        # Stesso dislivello per pixel, pixel piu' piccolo = pendenza maggiore.
        dem, acqua = self._ramp()
        grosso = collapse_source_potential(dem, acqua, px_m=240.0, py_m=240.0)
        fine = collapse_source_potential(dem, acqua, px_m=30.0, py_m=30.0)
        self.assertGreaterEqual(fine, grosso)
        self.assertGreater(fine, 0.9)   # 20/30 = 0.67 > 0.30


class LargestDepressionTest(unittest.TestCase):
    """Regressione: `filled - dem > 1 m` prendeva migliaia di pozzanghere
    sparse, nessuna a contatto col bordo -> enclosure 1.0 ovunque."""

    def test_picks_one_connected_basin_not_confetti(self):
        dem = np.full((30, 30), 100.0)
        dem[5:9, 5:9] = 60.0        # conca grande
        dem[20:22, 20:22] = 80.0    # conca piccola
        got = largest_depression(dem, min_depth_m=5.0)
        self.assertEqual(got["components"], 2)
        self.assertEqual(got["cells"], 16)          # solo la grande
        self.assertTrue(got["mask"][6, 6])
        self.assertFalse(got["mask"][20, 20])       # la piccola e' esclusa

    def test_flat_terrain_returns_none_not_a_score(self):
        self.assertIsNone(largest_depression(np.full((20, 20), 50.0), 5.0))

    def test_shallow_dips_below_threshold_are_not_basins(self):
        dem = np.full((20, 20), 100.0)
        dem[8:12, 8:12] = 98.0      # solo 2 m
        self.assertIsNone(largest_depression(dem, min_depth_m=5.0))

    def test_reports_depth_and_fill_level(self):
        dem = np.full((20, 20), 100.0)
        dem[8:12, 8:12] = 70.0
        got = largest_depression(dem, 5.0)
        self.assertAlmostEqual(got["max_depth_m"], 30.0)
        self.assertAlmostEqual(got["fill_level_m"], 100.0)
