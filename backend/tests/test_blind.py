import unittest

from core.ledger.blind import make_blind_pack, verify_hash


class BlindTest(unittest.TestCase):
    def setUp(self):
        self.rows = [{
            "label": "A",
            "rank": 1,
            "residual": 0.31,
            "hydro_score": 0.92,
            "spectral_score": 0.4,
            "geometry_score": None,
            "node_type": "confluence",
            "basin": "atlantic_west",
            "source": "hydro",
            "lon": -5.12345,
            "lat": 20.88888,
            "river_name": "Tamanrasset",
            "river_id": "tamanrasset",
            "pro": ["nodo"],
            "contro": ["aperto"],
            "kill_shot": "nessuno",
            "plato": [{"id": "beyond_pillars", "verdict": "support", "detail": "secret"}],
        }]

    def test_strips_coordinates_and_river_name(self):
        pack = make_blind_pack(self.rows, timestamp="2026-08-16T12:00:00+00:00")
        blob = str(pack)
        self.assertNotIn("-5.12345", blob)
        self.assertNotIn("20.88888", blob)
        self.assertNotIn("Tamanrasset", blob)
        self.assertNotIn("lon", pack["ranking"][0])
        self.assertEqual(pack["ranking"][0]["label"], "A")

    def test_hash_stable_and_verifiable(self):
        ts = "2026-08-16T12:00:00+00:00"
        a = make_blind_pack(self.rows, timestamp=ts)
        b = make_blind_pack(self.rows, timestamp=ts)
        self.assertEqual(a["hash"], b["hash"])
        self.assertTrue(verify_hash(a))
        self.assertEqual(len(a["hash"]), 64)

    def test_plato_detail_not_leaked(self):
        pack = make_blind_pack(self.rows, timestamp="2026-08-16T12:00:00+00:00")
        self.assertNotIn("secret", str(pack["ranking"]))


if __name__ == "__main__":
    unittest.main()
