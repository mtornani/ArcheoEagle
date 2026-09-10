"""Piattaforma annegata. Il test piu' importante e' il null: su una piattaforma
uniforme il punteggio deve variare SOLO con la profondita' — che e' per
costruzione, non una scoperta."""
import unittest

import numpy as np

from core.marine.shelf import (
    KNOWN_SUBMERGED_SITES,
    SLOPE_MAX,
    coastal_residence_kyr,
    drowning_age_kyr,
    percentile_vs_null,
    raw_score,
    rapid_drowning_ratio,
    sea_level_at,
    shelf_cell,
    surf_exposure_kyr,
)


class SeaLevelTest(unittest.TestCase):
    def test_lowstand_and_present(self):
        self.assertLess(sea_level_at(21.0), -120.0)
        self.assertAlmostEqual(sea_level_at(0.0), 0.0, places=6)

    def test_monotone_rise_since_lgm(self):
        ts = np.arange(0.0, 20.0, 0.25)
        lv = np.array([sea_level_at(t) for t in ts])
        self.assertTrue(np.all(np.diff(lv) <= 1e-9), "il livello deve calare andando indietro")

    def test_meltwater_pulse_is_in_the_curve(self):
        """Fra 14.6 e 14.2 ka il mare sale di ~16 m: e' l'impulso 1A, ed e' la
        ragione fisica per cui certe profondita' sono privilegiate."""
        salto = sea_level_at(14.2) - sea_level_at(14.6)
        self.assertGreater(salto, 12.0)


class DrowningAgeTest(unittest.TestCase):
    def test_shallow_drowned_later_than_deep(self):
        self.assertLess(drowning_age_kyr(-10.0), drowning_age_kyr(-100.0))

    def test_land_above_sea_has_no_drowning_age(self):
        self.assertIsNone(drowning_age_kyr(5.0))

    def test_below_glacial_lowstand_never_was_land(self):
        self.assertIsNone(drowning_age_kyr(-200.0))

    def test_known_sites_drowned_after_their_occupation(self):
        """Coerenza elementare: un sito non puo' essere annegato prima di
        essere stato abitato. Se scatta, o le coordinate o la curva sono
        sbagliate (o il sito e' sceso per subsidenza, non per eustatismo)."""
        for s in KNOWN_SUBMERGED_SITES:
            eta = drowning_age_kyr(s["depth_m"])
            self.assertIsNotNone(eta, s["name"])
            self.assertLess(eta, s["age_kyr"] + 3.0, s["name"])


class PreservationTest(unittest.TestCase):
    def test_fast_drowning_beats_slow(self):
        """-88 m fu attraversata durante l'impulso; -5 m ha avuto il mare
        addosso per millenni."""
        self.assertGreater(rapid_drowning_ratio(-88.0), rapid_drowning_ratio(-5.0))

    def test_surf_time_is_long_where_sea_level_stalled(self):
        self.assertGreater(surf_exposure_kyr(-5.0), surf_exposure_kyr(-88.0))

    def test_steep_slope_is_penalised(self):
        piano = raw_score(shelf_cell(-60.0, 0.002))
        ripido = raw_score(shelf_cell(-60.0, 0.5))
        self.assertGreater(piano, ripido * 5)


class NullTest(unittest.TestCase):
    """Un massimo interno esiste sempre: e' la lezione di docs/CALIBRAZIONE.md."""

    def test_percentile_refuses_to_answer_on_too_few_samples(self):
        self.assertIsNone(percentile_vs_null(10.0, [1.0, 2.0, 3.0]))

    def test_percentile_works_with_enough_samples(self):
        null = list(np.linspace(0.0, 10.0, 100))
        self.assertGreater(percentile_vs_null(9.0, null), 85.0)
        self.assertLess(percentile_vs_null(1.0, null), 15.0)

    def test_uniform_shelf_has_no_special_place_at_fixed_depth(self):
        """A profondita' e pendenza uguali, ogni punto della piattaforma ha lo
        stesso punteggio. Il modello NON inventa un posto speciale: la
        variazione viene solo da profondita' e pendenza, che sono input."""
        punteggi = [raw_score(shelf_cell(-50.0, 0.003)) for _ in range(20)]
        self.assertEqual(len(set(round(p, 9) for p in punteggi)), 1)


class HonestAbsenceTest(unittest.TestCase):
    def test_dry_land_scores_nothing_rather_than_zero_dressed_as_data(self):
        self.assertIsNone(raw_score(shelf_cell(10.0, 0.01)))

    def test_never_emerged_scores_nothing(self):
        self.assertIsNone(raw_score(shelf_cell(-250.0, 0.01)))


class KnownSitesFixtureTest(unittest.TestCase):
    def test_sites_carry_position_depth_age_and_kind(self):
        self.assertGreaterEqual(len(KNOWN_SUBMERGED_SITES), 3)
        for s in KNOWN_SUBMERGED_SITES:
            for k in ("name", "lon", "lat", "depth_m", "age_kyr", "kind"):
                self.assertIn(k, s)
            self.assertLess(s["depth_m"], 0.0)

    def test_catalogue_is_shallow_biased_and_that_is_recorded(self):
        """I siti noti stanno tutti in acqua bassa: si trovano dove i sub
        arrivano, non dove la conservazione e' migliore. Usarli come controllo
        positivo senza condizionare sulla profondita' misura questa distorsione,
        non il metodo."""
        prof = [s["depth_m"] for s in KNOWN_SUBMERGED_SITES]
        self.assertGreater(min(prof), -30.0)


if __name__ == "__main__":
    unittest.main()


class HorizontalRetreatTest(unittest.TestCase):
    """La domanda di Mirko: quanto era 'piu' in la'' la costa? La risposta non
    e' in metri ma in decine di chilometri — e il ritmo di arretramento e' il
    criterio della memoria, distinto da quello della conservazione."""

    def test_never_land_below_the_glacial_lowstand(self):
        from core.marine.shelf import was_ever_land
        self.assertTrue(was_ever_land(-120.0))
        self.assertFalse(was_ever_land(-200.0), "il mare non e' mai sceso a -200 m")
        self.assertFalse(was_ever_land(-300.0))
        self.assertFalse(was_ever_land(5.0), "sopra il livello attuale e' terra, non paleocosta")

    def test_meltwater_pulse_is_faster_than_average_deglaciation(self):
        from core.marine.shelf import MWP1A, vertical_rate_m_per_yr
        impulso = vertical_rate_m_per_yr(MWP1A["start_kyr"], MWP1A["end_kyr"])
        medio = vertical_rate_m_per_yr(20.0, 6.0)
        self.assertGreater(impulso, medio * 3)

    def test_flatter_shelf_loses_coast_faster(self):
        from core.marine.shelf import horizontal_retreat_m_per_yr
        piatta = horizontal_retreat_m_per_yr(0.0002, 0.047)
        ripida = horizontal_retreat_m_per_yr(0.02, 0.047)
        self.assertGreater(piatta, ripida * 50)

    def test_flat_shelf_loses_kilometres_in_a_lifetime(self):
        """Su piattaforma 1:5000 con il ritmo dell'impulso si perdono
        chilometri di costa in una vita: si vede accadere, e si racconta."""
        from core.marine.shelf import witnessed_loss_km
        self.assertGreater(witnessed_loss_km(0.0002, 0.047, 60.0), 10.0)

    def test_zero_gradient_refuses_to_answer(self):
        from core.marine.shelf import horizontal_retreat_m_per_yr, witnessed_loss_km
        self.assertIsNone(horizontal_retreat_m_per_yr(0.0, 0.047))
        self.assertIsNone(witnessed_loss_km(0.0, 0.047))
