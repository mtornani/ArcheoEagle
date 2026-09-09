"""Misura ≠ disegno. DEM finto con valle piantata = frode."""
import unittest

import numpy as np

from core.hydro.measure import (
    MEGA_CHAD_HIGHSTAND_M,
    copernicus_cog_url,
    nodes_from_contour,
    shoreline_from_dem,
    trap_richat,
)
from core.imagery.srtm import srtm_client


class ShorelineMeasureTest(unittest.TestCase):
    def test_bowl_contour_sits_on_the_level(self):
        n = 81
        yy, xx = np.mgrid[0:n, 0:n]
        # center 200 m, rises radially. 320 m is a ring.
        dem = 200.0 + ((xx - 40.0) ** 2 + (yy - 40.0) ** 2) * 0.12
        bbox = [10.0, 12.0, 11.0, 13.0]
        lines = shoreline_from_dem(dem, bbox, level_m=320.0)
        self.assertTrue(lines, "expected a closed 320 m contour")
        nodes = nodes_from_contour(
            lines,
            level_m=320.0,
            node_type="paleolake_shore",
            basin="mega_chad",
            river_id="mega_chad_highstand",
            river_name="Mega-Chad highstand (DEM)",
            step_km=40.0,
        )
        self.assertGreaterEqual(len(nodes), 3)
        for node in nodes:
            self.assertEqual(node["grade"], "dem-contour")
            self.assertEqual(node["source"], "dem-contour")
            self.assertEqual(node["node_type"], "paleolake_shore")
            self.assertGreaterEqual(node["lon"], 10.0)
            self.assertLessEqual(node["lon"], 11.0)

    def test_flat_dem_yields_no_shore(self):
        dem = np.full((20, 20), 280.0)
        lines = shoreline_from_dem(dem, [0, 0, 1, 1], level_m=320.0)
        self.assertEqual(lines, [])

    def test_copernicus_url_is_the_public_cog(self):
        url = copernicus_cog_url(16, 18)
        self.assertIn("Copernicus_DSM_COG_10_N16_00_E018_00_DEM", url)
        self.assertTrue(url.startswith("https://copernicus-dem-30m.s3.amazonaws.com/"))

    def test_west_south_url(self):
        url = copernicus_cog_url(-21, -11)
        self.assertIn("S21_00_W011_00", url)


class HonestDemTest(unittest.TestCase):
    def test_no_key_means_none_not_a_planted_valley(self):
        """Production path must not invent terrain where 'sites typically are'."""
        old = srtm_client.api_key
        srtm_client.api_key = ""
        try:
            dem = srtm_client.fetch_dem([14.0, 12.0, 16.0, 14.0], target_shape=(32, 32))
            self.assertIsNone(dem)
        finally:
            srtm_client.api_key = old


class RichatTrapTest(unittest.TestCase):
    def test_richat_refuses_to_rank(self):
        payload = trap_richat()
        self.assertEqual(payload["method"], "trap")
        self.assertEqual(payload["trap_id"], "richat")
        self.assertEqual(payload["ranking"], [])
        self.assertNotIn("Atlantide found", payload["message"])


class HighstandConstantTest(unittest.TestCase):
    def test_mega_chad_level_is_the_published_bench(self):
        self.assertEqual(MEGA_CHAD_HIGHSTAND_M, 320.0)


if __name__ == "__main__":
    unittest.main()
