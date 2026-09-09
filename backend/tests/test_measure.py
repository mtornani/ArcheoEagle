"""Misura ≠ disegno. DEM finto con valle piantata = frode."""
import unittest
from unittest.mock import patch

import numpy as np

from core.hydro.measure import (
    MEGA_CHAD_HIGHSTAND_M,
    copernicus_cog_url,
    measure_highstand,
    nodes_from_contour,
    shoreline_from_dem,
    tiles_covering_bbox,
    trap_richat,
)
from core.imagery.srtm import srtm_client


def _bowl_tile(bbox, cx=40.0, cy=40.0, base=200.0, n=81):
    """A synthetic bowl DEM standing in for one fetched Copernicus tile —
    used only to test tiling/merging logic, never shipped to the app."""
    yy, xx = np.mgrid[0:n, 0:n]
    dem = base + ((xx - cx) ** 2 + (yy - cy) ** 2) * 0.12
    return dem, list(bbox), f"mock://{bbox}"


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


class TileGridTest(unittest.TestCase):
    def test_single_degree_bbox_is_one_tile(self):
        self.assertEqual(tiles_covering_bbox([14.0, 12.0, 14.9, 12.9]), [(12, 14)])

    def test_bbox_spanning_two_degrees_is_four_tiles(self):
        tiles = tiles_covering_bbox([14.2, 12.2, 15.3, 13.3])
        self.assertEqual(
            set(tiles), {(12, 14), (12, 15), (13, 14), (13, 15)}
        )

    def test_western_southern_hemisphere_bbox(self):
        tiles = tiles_covering_bbox([-11.5, -21.5, -10.6, -20.6])
        self.assertEqual(set(tiles), {(-22, -12), (-22, -11), (-21, -12), (-21, -11)})


class MultiTileHighstandTest(unittest.TestCase):
    """One 1° tile is a corner of Mega-Chad, not the shore. measure_highstand
    must walk the whole grid touching bbox, merge every tile's contour, and
    report honestly what it covered — not silently substitute a single tile."""

    def test_merges_nodes_from_every_tile_in_bbox(self):
        bbox = [14.0, 12.0, 15.9, 12.9]  # two tiles: (12,14) and (12,15)

        def fake_fetch(lat_s, lon_s, timeout=90):
            tile_bbox = [lon_s, lat_s, lon_s + 1.0, lat_s + 1.0]
            dem, tb, url = _bowl_tile(tile_bbox)
            return dem, tb, url

        with patch("core.hydro.measure.fetch_copernicus_tile", side_effect=fake_fetch):
            result = measure_highstand(bbox, level_m=320.0)

        self.assertTrue(result["nodes"], "expected merged nodes from both tiles")
        self.assertEqual(len(result["dem"]["tiles_used"]), 2)
        self.assertEqual(result["dem"]["tiles_failed"], [])
        self.assertFalse(result["dem"]["truncated"])
        self.assertTrue(result["dem"]["real"])

    def test_a_failed_tile_is_dropped_not_invented(self):
        bbox = [14.0, 12.0, 15.9, 12.9]

        def fake_fetch(lat_s, lon_s, timeout=90):
            if lon_s == 15:
                return None
            tile_bbox = [lon_s, lat_s, lon_s + 1.0, lat_s + 1.0]
            return _bowl_tile(tile_bbox)

        with patch("core.hydro.measure.fetch_copernicus_tile", side_effect=fake_fetch):
            result = measure_highstand(bbox, level_m=320.0)

        self.assertEqual(len(result["dem"]["tiles_used"]), 1)
        self.assertEqual(result["dem"]["tiles_failed"], [[12, 15]])

    def test_all_tiles_failing_is_an_honest_empty_not_a_planted_shore(self):
        bbox = [14.0, 12.0, 15.9, 12.9]
        with patch("core.hydro.measure.fetch_copernicus_tile", return_value=None):
            result = measure_highstand(bbox, level_m=320.0)

        self.assertEqual(result["nodes"], [])
        self.assertFalse(result["dem"]["real"])
        self.assertEqual(result["dem"]["tiles_total"], 2)

    def test_truncation_is_reported_never_hidden(self):
        bbox = [10.0, 10.0, 19.9, 10.9]  # 10 tiles wide

        def fake_fetch(lat_s, lon_s, timeout=90):
            tile_bbox = [lon_s, lat_s, lon_s + 1.0, lat_s + 1.0]
            return _bowl_tile(tile_bbox)

        with patch("core.hydro.measure.fetch_copernicus_tile", side_effect=fake_fetch):
            result = measure_highstand(bbox, level_m=320.0, max_tiles=3)

        self.assertEqual(len(result["dem"]["tiles_used"]), 3)
        self.assertEqual(result["dem"]["tiles_total"], 10)
        self.assertTrue(result["dem"]["truncated"])


if __name__ == "__main__":
    unittest.main()
