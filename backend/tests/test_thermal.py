"""Subsidenza termica: l'orologio che Heezen non aveva nel 1969."""
import unittest

from core.marine.thermal import (
    SEEWARTE_CHAIN, implied_rate_mm_yr, planation_age_range_ma,
    plate_depth_m, subsidence_rate_m_per_myr, verdict_vs_claim,
)

SUMMIT = -268.0          # vetta dell'Atlantis Seamount, misurata su GMRT
SEA_LEVEL_12KA = -65.0


class PlateModelTest(unittest.TestCase):
    def test_young_crust_is_shallow_old_crust_is_deep(self):
        self.assertLess(plate_depth_m(5.0), plate_depth_m(80.0))

    def test_subsidence_slows_down_with_age(self):
        # E' il cuore dell'argomento: una piastra vecchia non si muove quasi.
        self.assertGreater(subsidence_rate_m_per_myr(20.0), subsidence_rate_m_per_myr(85.0))

    def test_the_two_models_agree_on_young_crust_and_differ_on_old(self):
        giovane = abs(plate_depth_m(10.0, "gdh1") - plate_depth_m(10.0, "ps77"))
        vecchia = abs(plate_depth_m(100.0, "gdh1") - plate_depth_m(100.0, "ps77"))
        self.assertLess(giovane, vecchia)

    def test_old_plate_subsidence_is_far_too_slow_for_archaeology(self):
        # A 85 Ma: pochi metri per milione di anni. Mille volte troppo lento
        # per spiegare 268 m in tempi umani.
        self.assertLess(subsidence_rate_m_per_myr(85.0), 15.0)


class ImpliedRateTest(unittest.TestCase):
    def test_older_planation_means_slower_rate(self):
        self.assertLess(implied_rate_mm_yr(SUMMIT, 26.0), implied_rate_mm_yr(SUMMIT, 10.0))

    def test_the_implied_rate_is_hundredths_of_a_millimetre(self):
        for age in SEEWARTE_CHAIN["volcanism_ma"]:
            r = implied_rate_mm_yr(SUMMIT, age)
            self.assertLess(r, 0.05)
            self.assertGreater(r, 0.005)

    def test_zero_or_negative_age_is_refused(self):
        with self.assertRaises(ValueError):
            implied_rate_mm_yr(SUMMIT, 0.0)


class HeezenVerdictTest(unittest.TestCase):
    def test_the_twelve_thousand_year_claim_is_off_by_a_factor_of_hundreds(self):
        v = verdict_vs_claim(SUMMIT, 12.0, SEA_LEVEL_12KA)
        self.assertEqual(v["verdict"], "falsificato")
        lo, hi = v["overstatement_factor"]
        self.assertGreater(lo, 500)
        self.assertGreater(hi, 1000)

    def test_the_required_rate_is_about_17_mm_per_year(self):
        v = verdict_vs_claim(SUMMIT, 12.0, SEA_LEVEL_12KA)
        self.assertAlmostEqual(v["rate_required_mm_yr"], 16.9, delta=0.5)

    def test_the_planation_window_matches_the_chain_volcanism(self):
        self.assertEqual(planation_age_range_ma(SUMMIT), (10.0, 26.0))

    def test_the_verdict_refuses_to_deny_the_observation(self):
        # Il punto che separa questo da una liquidazione: l'isola c'e' stata.
        v = verdict_vs_claim(SUMMIT, 12.0, SEA_LEVEL_12KA)
        self.assertIn("lo e' stato", v["cannot_say"])


if __name__ == "__main__":
    unittest.main()
