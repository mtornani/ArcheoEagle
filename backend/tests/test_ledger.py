import unittest

from core.ledger.hypotheses import VERDICT_CONTRADICT, VERDICT_NA, build_ledger, plato_tests


class PlatoTest(unittest.TestCase):
    def test_missing_rings_is_na_not_contradict(self):
        tests = plato_tests(-10.0, 20.5, circularity=0.2)
        rings = next(t for t in tests if t["id"] == "concentric_rings")
        self.assertEqual(rings["verdict"], VERDICT_NA)
        self.assertNotEqual(rings["verdict"], VERDICT_CONTRADICT)

    def test_west_of_gibraltar_supports_pillars(self):
        tests = plato_tests(-12.0, 20.0)
        pillars = next(t for t in tests if t["id"] == "beyond_pillars")
        self.assertEqual(pillars["verdict"], "support")

    def test_east_of_gibraltar_is_na(self):
        tests = plato_tests(8.0, 23.0)
        pillars = next(t for t in tests if t["id"] == "beyond_pillars")
        self.assertEqual(pillars["verdict"], VERDICT_NA)

    def test_circularity_can_support_without_being_required(self):
        tests = plato_tests(-10.0, 20.5, circularity=0.9)
        rings = next(t for t in tests if t["id"] == "concentric_rings")
        self.assertEqual(rings["verdict"], "support")


class LedgerTest(unittest.TestCase):
    def test_hydro_outranks_orphan_spectral(self):
        hydro = [{
            "lon": -5.0, "lat": 20.8, "node_type": "confluence",
            "hydro_score": 0.92, "basin": "atlantic_west",
            "river_id": "tamanrasset", "river_name": "Tamanrasset",
        }]
        spectral = [{
            "geometry": {"type": "Point", "coordinates": [20.0, 25.0]},
            "properties": {"score": 0.88, "label": "blob", "eccentricity": 0.2},
        }]
        rows = build_ledger(hydro, spectral)
        self.assertGreaterEqual(len(rows), 2)
        self.assertEqual(rows[0]["label"], "A")
        self.assertEqual(rows[0]["node_type"], "confluence")
        self.assertLess(rows[0]["residual"], rows[-1]["residual"])


if __name__ == "__main__":
    unittest.main()
