"""Confinamento e seiche. Il test che conta e' il primo: Merian deve ritrovare
i ~92 secondi misurati a Dickson nel 2023. Gli altri difendono i bordi."""
import math
import unittest

import numpy as np

from core.marine.seiche import (
    DICKSON, SAHARA_SLIDE, basin_axes_m, confinement, dickson_control,
    displacement_hazard, greens_amplification, merian_period, seiche_profile,
)


class DicksonControlTest(unittest.TestCase):
    def test_merian_reproduces_the_observed_period(self):
        # Controllo positivo su un caso pubblicato e misurato dal vivo.
        c = dickson_control()
        self.assertTrue(c["passes"], c)
        self.assertLess(abs(c["predicted_period_s"] - 92.0), 20.0)

    def test_the_small_volume_is_the_point(self):
        # 25 Mm3 contro 600.000 Mm3: se questo rapporto cambia, e' cambiato un
        # dato di letteratura e va rimesso a mano, non aggiustato il test.
        self.assertEqual(dickson_control()["volume_ratio_vs_sahara_slide"], 24000)
        self.assertFalse(SAHARA_SLIDE["tsunamigenic"])


class MerianTest(unittest.TestCase):
    def test_open_basin_rings_twice_as_slow_as_closed(self):
        self.assertAlmostEqual(
            merian_period(1000, 100, "open"),
            2 * merian_period(1000, 100, "closed"),
        )

    def test_deeper_water_rings_faster(self):
        # c = sqrt(g h): piu' fondo, onda piu' veloce, periodo piu' corto.
        self.assertLess(merian_period(1000, 400), merian_period(1000, 100))

    def test_matches_the_closed_form(self):
        self.assertAlmostEqual(
            merian_period(2000, 250, "closed"),
            2 * 2000 / math.sqrt(9.81 * 250),
        )

    def test_degenerate_geometry_returns_none_instead_of_a_number(self):
        # Zero o negativo non e' un bacino: niente numero inventato.
        self.assertIsNone(merian_period(0, 100))
        self.assertIsNone(merian_period(1000, 0))
        self.assertIsNone(merian_period(-5, 100))


class GreenTest(unittest.TestCase):
    def test_no_change_no_amplification(self):
        self.assertAlmostEqual(greens_amplification(100, 100, 500, 500), 1.0)

    def test_narrowing_and_shoaling_amplify(self):
        self.assertGreater(greens_amplification(400, 25, 4000, 500), 1.0)

    def test_widening_into_deep_water_damps(self):
        self.assertLess(greens_amplification(25, 400, 500, 4000), 1.0)

    def test_narrowing_beats_shoaling_for_the_same_ratio(self):
        # esponente 1/2 sulla larghezza contro 1/4 sulla profondita'.
        narrow = greens_amplification(100, 100, 1000, 250)
        shoal = greens_amplification(100, 25, 1000, 1000)
        self.assertGreater(narrow, shoal)


def _fjord(rows=20, cols=20):
    """Canale chiuso su tre lati, aperto solo sul bordo destro della griglia."""
    m = np.zeros((rows, cols), bool)
    m[8:12, 4:] = True
    return m


def _open_water(rows=20, cols=20):
    """Acqua che esce da tutti i lati: nessun confinamento."""
    return np.ones((rows, cols), bool)


class ConfinementTest(unittest.TestCase):
    def test_a_closed_lake_is_fully_enclosed(self):
        m = np.zeros((20, 20), bool)
        m[5:15, 5:15] = True
        self.assertAlmostEqual(confinement(m)["enclosure"], 1.0)
        self.assertEqual(confinement(m)["open_cells"], 0.0)

    def test_open_water_has_no_enclosure(self):
        self.assertAlmostEqual(confinement(_open_water())["enclosure"], 0.0)

    def test_a_fjord_sits_between_the_two(self):
        e = confinement(_fjord())["enclosure"]
        self.assertGreater(e, 0.8)   # quasi tutto parete
        self.assertLess(e, 1.0)      # ma la bocca e' aperta

    def test_empty_mask_does_not_divide_by_zero(self):
        self.assertEqual(confinement(np.zeros((5, 5), bool))["enclosure"], 0.0)


class AxesTest(unittest.TestCase):
    def test_short_axis_is_the_across_channel_span(self):
        # 4 righe x 16 colonne a 100 m: il lato corto e' 400 m.
        short, long = basin_axes_m(_fjord(), 100.0, 100.0)
        self.assertAlmostEqual(short, 400.0)
        self.assertAlmostEqual(long, 1600.0)

    def test_anisotropic_pixels_are_honoured(self):
        # Su EPSG:4326 la cella non e' quadrata: 4 righe x 200 m = 800 m,
        # che supera i 16 x 50 m = 800 m dell'altro asse solo a pari merito.
        short, long = basin_axes_m(_fjord(), 50.0, 200.0)
        self.assertAlmostEqual(short, 800.0)
        self.assertAlmostEqual(long, 800.0)

    def test_no_water_no_axes(self):
        self.assertEqual(basin_axes_m(np.zeros((5, 5), bool), 30.0, 30.0), (0.0, 0.0))


class ProfileAndHazardTest(unittest.TestCase):
    def test_transverse_mode_is_faster_than_longitudinal(self):
        p = seiche_profile(_fjord(), depth_m=400.0, px_m=100.0, py_m=100.0)
        self.assertLess(p["transverse_period_s"], p["longitudinal_period_s"])

    def test_hazard_needs_both_factors(self):
        # Orlo ripido su mare aperto: niente. Catino con orlo piatto: niente.
        steep_open = displacement_hazard(_open_water(), 0.9, 400.0, 100.0, 100.0)
        flat_closed = displacement_hazard(_fjord(), 0.0, 400.0, 100.0, 100.0)
        self.assertAlmostEqual(steep_open["hazard"], 0.0)
        self.assertAlmostEqual(flat_closed["hazard"], 0.0)

    def test_steep_and_confined_scores(self):
        h = displacement_hazard(_fjord(), 0.9, 400.0, 100.0, 100.0)
        self.assertGreater(h["hazard"], 0.7)

    def test_volume_is_not_an_input(self):
        # Il punto dottrinale del modulo: nessun volume nella firma.
        import inspect
        params = inspect.signature(displacement_hazard).parameters
        self.assertNotIn("volume", " ".join(params))

    def test_hazard_carries_its_own_disclaimer(self):
        # Un punteggio senza kill-shot e senza "cosa non puoi dire" non e' una
        # riga di prova secondo CLAUDE.md §5.
        h = displacement_hazard(_fjord(), 0.9, 400.0, 100.0, 100.0)
        self.assertTrue(h["kill_shot"])
        self.assertTrue(h["cannot_say"])
        self.assertEqual(h["grade"], "geometry")


if __name__ == "__main__":
    unittest.main()
