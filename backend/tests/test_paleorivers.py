import unittest

from core.hydro.paleorivers import corridor_bbox, load_network, nodes_in_aoi, rivers_in_aoi


class PaleoriversTest(unittest.TestCase):
    def test_network_loads(self):
        net = load_network()
        self.assertGreaterEqual(len(net["features"]), 6)

    def test_tamanrasset_corridor_has_nodes(self):
        # Hoggar-to-Atlantic schematic crosses this box
        bbox = [-8.0, 19.5, -2.0, 22.5]
        nodes = nodes_in_aoi(bbox)
        self.assertTrue(nodes, "expected hydrologic nodes on Tamanrasset")
        basins = {n["basin"] for n in nodes}
        self.assertIn("atlantic_west", basins)

    def test_empty_ocean_has_no_nodes(self):
        bbox = [-40.0, 0.0, -30.0, 5.0]
        self.assertEqual(nodes_in_aoi(bbox), [])

    def test_rivers_filter(self):
        rivers = rivers_in_aoi([13.0, 12.0, 17.0, 16.0])
        kinds = {f["properties"]["kind"] for f in rivers["features"]}
        self.assertIn("paleolake", kinds)

    def test_walk_tamanrasset_bbox_has_nodes(self):
        bbox = corridor_bbox("tamanrasset")
        self.assertEqual(len(bbox), 4)
        self.assertTrue(nodes_in_aoi(bbox))

    def test_unknown_corridor_raises(self):
        with self.assertRaises(ValueError):
            corridor_bbox("atlantis_icon")


if __name__ == "__main__":
    unittest.main()
