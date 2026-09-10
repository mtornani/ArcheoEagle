"""A shore is a line that can leave a tile. Polar-sort cannot say that."""
import unittest

import numpy as np

from core.hydro.lineament import (
    join_count,
    polar_sort_contour,
    relief_across,
    summarize,
)
from core.hydro.measure import shoreline_from_dem


def _eastward_ramp(n, z0, z1):
    return np.tile(np.linspace(z0, z1, n), (n, 1))


class PolarSortFraudTest(unittest.TestCase):
    def test_polar_sort_closes_an_open_shore(self):
        n = 41
        dem = _eastward_ramp(n, 200.0, 400.0)
        bbox = [14.0, 13.0, 15.0, 14.0]
        polar = polar_sort_contour(dem, bbox, 320.0)
        traced = shoreline_from_dem(dem, bbox, 320.0)
        self.assertTrue(polar)
        self.assertTrue(traced)
        self.assertEqual(polar[0][0], polar[0][-1])
        line = max(traced, key=len)
        self.assertNotEqual(line[0], line[-1])


class CrossTileJoinTest(unittest.TestCase):
    def _plane(self, bbox, n=41):
        """320 m is the diagonal that crosses lon=15 at lat=13.5."""
        lon0, lat0, lon1, lat1 = bbox
        yy, xx = np.mgrid[0:n, 0:n]
        lon = lon0 + xx / (n - 1) * (lon1 - lon0)
        lat = lat1 - yy / (n - 1) * (lat1 - lat0)
        return 320.0 + 200.0 * (lon - 15.0) + 200.0 * (lat - 13.5)

    def test_shared_meridian_contour_joins(self):
        west_bbox = [14.0, 13.0, 15.0, 14.0]
        east_bbox = [15.0, 13.0, 16.0, 14.0]
        a = shoreline_from_dem(self._plane(west_bbox), west_bbox, 320.0)
        b = shoreline_from_dem(self._plane(east_bbox), east_bbox, 320.0)
        self.assertTrue(a, "west tile must carry the diagonal to the east edge")
        self.assertTrue(b, "east tile must carry the diagonal from the west edge")
        self.assertGreaterEqual(join_count(a, west_bbox, b, east_bbox), 1)

    def test_two_bowls_do_not_join(self):
        n = 41
        yy, xx = np.mgrid[0:n, 0:n]
        bowl = 200.0 + ((xx - 20.0) ** 2 + (yy - 20.0) ** 2) * 0.4
        west_bbox = [14.0, 13.0, 15.0, 14.0]
        east_bbox = [15.0, 13.0, 16.0, 14.0]
        a = shoreline_from_dem(bowl, west_bbox, 320.0)
        b = shoreline_from_dem(bowl, east_bbox, 320.0)
        self.assertEqual(join_count(a, west_bbox, b, east_bbox), 0)

    def test_summarize_marks_open_edge_line(self):
        n = 41
        dem = _eastward_ramp(n, 200.0, 400.0)
        bbox = [14.0, 13.0, 15.0, 14.0]
        lines = shoreline_from_dem(dem, bbox, 320.0)
        s = summarize(lines, bbox)
        self.assertGreaterEqual(s["n_open"], 1)
        self.assertGreaterEqual(s["n_with_edge"], 1)
        self.assertFalse(s["longest_closed"])
        self.assertGreater(s["longest_km"], 50.0)


class ReliefAcrossTest(unittest.TestCase):
    def test_bench_has_a_drop_ramp_does_not(self):
        n = 81
        x = np.arange(n) / (n - 1)
        bench = np.tile(np.where(x < 0.5, 300.0, 340.0), (n, 1))
        ramp = np.tile(np.linspace(300.0, 340.0, n), (n, 1))
        bbox = [14.0, 13.0, 15.0, 14.0]
        bench_line = max(shoreline_from_dem(bench, bbox, 320.0), key=len)
        ramp_line = max(shoreline_from_dem(ramp, bbox, 320.0), key=len)
        b = relief_across(bench, bbox, bench_line)
        r = relief_across(ramp, bbox, ramp_line)
        self.assertIsNotNone(b["drop_m"])
        self.assertIsNotNone(r["drop_m"])
        self.assertGreater(b["drop_m"], 20.0)
        self.assertLess(r["drop_m"], 10.0)


if __name__ == "__main__":
    unittest.main()
