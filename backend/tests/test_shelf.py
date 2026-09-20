"""Piattaforma annegata. Il test piu' importante e' il null: su una piattaforma
uniforme il punteggio deve variare SOLO con la profondita' — che e' per
costruzione, non una scoperta."""
import unittest

import numpy as np

from core.marine.shelf import (
    deepest_ever_land_m,
    depth_was_land_kyr,
    AZORES_SUBSIDENCE,
    MWP1A,
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


class YoungerDryasTest(unittest.TestCase):
    """La catena 'impatto -> collasso della calotta -> diluvio' fa una
    previsione quantitativa: al Younger Dryas (12,9 ka) il livello del mare
    deve accelerare. Questi test bloccano cio' che la curva dice davvero, cosi'
    la conclusione non puo' essere spostata cambiando i dati in silenzio."""

    def _rate_mm_yr(self, kyr_from, kyr_to):
        gain = sea_level_at(kyr_to) - sea_level_at(kyr_from)
        return gain / ((kyr_from - kyr_to) * 1000.0) * 1000.0

    def test_younger_dryas_is_a_pause_not_a_flood(self):
        # 12,9 -> 11,7 ka: ~7,5 m in 1200 anni.
        yd = self._rate_mm_yr(12.9, 11.7)
        self.assertLess(yd, 8.0)

    def test_mwp1a_is_an_order_of_magnitude_faster_than_the_whole_yd(self):
        yd = self._rate_mm_yr(12.9, 11.7)
        mwp = MWP1A["rise_m"] / ((MWP1A["start_kyr"] - MWP1A["end_kyr"]) * 1000.0) * 1000.0
        self.assertGreater(mwp / yd, 5.0)

    def test_the_pulse_comes_before_the_impact_window_not_after(self):
        # MWP1A parte 1750 anni PRIMA dell'inizio del Younger Dryas: non puo'
        # esserne la conseguenza. L'ordine temporale da solo rompe la catena.
        self.assertGreater(MWP1A["start_kyr"], 12.9)
        self.assertGreater((MWP1A["start_kyr"] - 12.9) * 1000.0, 1000.0)

    def test_yd_is_the_slowest_stretch_of_the_deglaciation(self):
        # Fra 18 e 7 ka (deglaciazione vera), nessun intervallo di pari durata
        # sale piu' piano di quello che contiene l'inizio del YD.
        yd = self._rate_mm_yr(13.0, 12.0)
        others = [self._rate_mm_yr(a, a - 1.0) for a in
                  (18.0, 17.0, 16.0, 15.0, 14.0, 12.0, 11.0, 10.0, 9.0, 8.0)]
        self.assertLessEqual(yd, min(others))


class SubsidenceTest(unittest.TestCase):
    """Le Azzorre: due tassi di subsidenza pubblicati che differiscono ~24x.
    Quale si usa decide se un sito sommerso poteva esistere. Questi test
    bloccano il conto, non l'opinione."""

    def test_zero_subsidence_is_the_pure_eustatic_case(self):
        a = depth_was_land_kyr(-30.0, 0.0)
        self.assertIsNotNone(a)
        self.assertAlmostEqual(a, 9.1, delta=0.3)

    def test_geological_rate_buys_almost_nothing(self):
        # 0,3 mm/a e' il MASSIMO di lungo termine per le Azzorre.
        base = depth_was_land_kyr(-30.0, 0.0)
        geo = depth_was_land_kyr(-30.0, AZORES_SUBSIDENCE["geological_long_term_max_mm_yr"])
        self.assertLess(base - geo, 0.6)          # meno di 600 anni guadagnati

    def test_gps_rate_would_open_the_window_by_millennia(self):
        # Il tasso GPS sposta -30 m dentro l'epoca dei paesi veri. E' il motivo
        # per cui estrapolarlo a 12.000 anni e' l'errore da non fare.
        base = depth_was_land_kyr(-30.0, 0.0)
        gps = depth_was_land_kyr(-30.0, AZORES_SUBSIDENCE["gps_short_term_mm_yr"][1])
        self.assertGreater(base - gps, 4.0)       # oltre 4.000 anni guadagnati

    def test_the_two_published_rates_differ_by_more_than_an_order(self):
        gps = AZORES_SUBSIDENCE["gps_short_term_mm_yr"][1]
        geo = AZORES_SUBSIDENCE["geological_long_term_max_mm_yr"]
        self.assertGreater(gps / geo, 20.0)
        self.assertTrue(AZORES_SUBSIDENCE["contested"])

    def test_subsidence_deepens_the_ever_land_limit(self):
        self.assertLess(deepest_ever_land_m(0.6), deepest_ever_land_m(0.0))

    def test_a_point_above_sea_level_is_land_now(self):
        self.assertEqual(depth_was_land_kyr(5.0, 0.0), 0.0)


class MidAtlanticExposureTest(unittest.TestCase):
    """Tesi (Kosmographia Ep007, nov 2019): un 'micro-continente granitico'
    sotto il medio Atlantico sarebbe stato esposto negli ultimi ~20.000 anni.
    La parte granitica e' reale (zirconi 330 e 1600 Ma, Nature 1998). La parte
    sull'esposizione si pesa qui, e non regge di due-tre ordini di grandezza."""

    def _rate_needed_mm_yr(self, z_now_m, kyr=20.0):
        """Tasso di subsidenza minimo perche' z_now fosse emerso kyr fa."""
        return ((sea_level_at(kyr) - z_now_m) / (kyr * 1000.0)) * 1000.0

    def test_the_glacial_lowstand_needs_no_subsidence(self):
        # -130 m e' gia' spiegato dall'eustasia: nessuna tettonica richiesta.
        self.assertLess(self._rate_needed_mm_yr(-130.0), 1.0)

    def test_the_ridge_axis_needs_hundreds_of_times_the_geological_rate(self):
        # I zirconi vengono da gabbri presso la zona di frattura di Kane,
        # a migliaia di metri di profondita'.
        need = self._rate_needed_mm_yr(-3500.0)
        geo = AZORES_SUBSIDENCE["geological_long_term_max_mm_yr"]
        self.assertGreater(need / geo, 500.0)

    def test_even_the_gps_rate_cannot_reach_plateau_depths(self):
        # Il tasso GPS estrapolato a 20.000 anni - gia' un abuso - arriva a
        # circa -270 m. Il Plateau delle Azzorre sta a migliaia di metri.
        gps = AZORES_SUBSIDENCE["gps_short_term_mm_yr"][1]
        deepest = deepest_ever_land_m(gps)
        self.assertGreater(deepest, -300.0)
        self.assertLess(deepest, -200.0)

    def test_the_claim_fails_on_every_published_rate(self):
        # Non dipende da quale numero scegli: fallisce con entrambi.
        need = self._rate_needed_mm_yr(-2000.0)
        for rate in (AZORES_SUBSIDENCE["geological_long_term_max_mm_yr"],
                     *AZORES_SUBSIDENCE["gps_short_term_mm_yr"]):
            self.assertGreater(need / rate, 10.0)
