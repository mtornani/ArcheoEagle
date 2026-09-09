"""Route-level smoke tests. A handler with an undefined name is a 500 in
production that unittest never sees unless something calls it directly."""
import unittest

from api.routes.analysis import hydro_network


class NetworkRouteTest(unittest.TestCase):
    def test_hydro_network_returns_the_schematic_feature_collection(self):
        # Regression: hydro_network() called load_network() without
        # importing it — a NameError on every /api/v1/analysis/network
        # request, invisible to a test suite that never calls the route.
        net = hydro_network()
        self.assertEqual(net["type"], "FeatureCollection")
        self.assertGreaterEqual(len(net["features"]), 6)


if __name__ == "__main__":
    unittest.main()
