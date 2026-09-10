"""The mouth is a canyon. Chemistry of T1 must not look like a glacial sand dump."""
import unittest

from core.cores.timiris import ahp_events, load_turbidites, load_xrf, sial_windows


class TimirisArchiveTest(unittest.TestCase):
    def test_t1_is_the_only_ahp_bed_on_the_levee(self):
        beds = load_turbidites(core="GeoB8502-2")
        ahp = [b for b in beds if 5.5 <= b["age_ka"] <= 14.5]
        self.assertEqual(len(ahp), 1)
        self.assertEqual(ahp[0]["event"], "T1")
        self.assertAlmostEqual(ahp[0]["age_ka"], 10.1)

    def test_canyon_channel_is_busy_in_the_humid_window(self):
        # Intra-canyon GeoB8509-2: river/canyon was switching on, not a single dump.
        self.assertGreaterEqual(ahp_events("GeoB8509-2"), 10)

    def test_t1_is_a_si_pulse_not_a_pleistocene_sand_cannon(self):
        w = sial_windows(load_xrf())
        # There is a pulse: T1 > the pelagite sitting on top of it.
        self.assertGreater(w["t1_ahp_10ka"]["sial"], w["pelagite_above"]["sial"])
        # Glacial canyon fill hits Si/Al ~8-10. T1's peak does not.
        self.assertGreater(w["pleistocene_bombs"]["sial_max"], 7.0)
        self.assertLess(w["t1_ahp_10ka"]["sial_max"], w["pleistocene_bombs"]["sial_max"])


if __name__ == "__main__":
    unittest.main()
