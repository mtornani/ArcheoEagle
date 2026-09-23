"""A shore is a line that can leave a tile. Polar-sort cannot say that."""
import unittest

import numpy as np

from core.hydro.lineament import (
    join_count,
    local_drop_along,
    polar_sort_contour,
    relief_across,
    split_by_local_relief,
    split_lines_by_relief,
    split_longest_by_relief,
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



class LocalReliefSplitTest(unittest.TestCase):
    """Spezzare dove Δz locale crolla. Isolinea ≠ ridge. Offline only."""

    BBOX = [14.0, 13.0, 15.0, 14.0]

    def _dem_ridge_plus_flat(self, n=121):
        """Sharp N-S step in the north half; flat ~320 m basin in the south."""
        lon0, lat0, lon1, lat1 = self.BBOX
        yy, xx = np.mgrid[0:n, 0:n]
        lon = lon0 + xx / (n - 1) * (lon1 - lon0)
        lat = lat1 - yy / (n - 1) * (lat1 - lat0)
        # north (lat > 13.5): west 300 / east 340 with step at 14.5
        north = np.where(lon < 14.5, 300.0, 340.0)
        # south: flat basin at the contour level (tiny noise so |Δz|~0)
        south = np.full_like(north, 320.0)
        return np.where(lat > 13.5, north, south)

    def _polyline_ridge_then_meander(self):
        """N-S along the step, then E-W wiggles on the flat basin (same level)."""
        line = []
        # high-drop: along lon=14.5 from lat 13.95 → 13.52
        for lat in np.linspace(13.95, 13.52, 80):
            line.append((14.5, float(lat)))
        # low-drop meanders on the flat south
        for i, lon in enumerate(np.linspace(14.5, 14.85, 40)):
            lat = 13.45 - 0.02 * ((i % 6) - 3)  # wiggle
            line.append((float(lon), float(lat)))
        for i, lon in enumerate(np.linspace(14.85, 14.2, 40)):
            lat = 13.35 - 0.02 * ((i % 6) - 3)
            line.append((float(lon), float(lat)))
        return line

    def test_split_keeps_ridge_drops_meanders(self):
        dem = self._dem_ridge_plus_flat()
        line = self._polyline_ridge_then_meander()
        drops = local_drop_along(dem, self.BBOX, line, sample_every_n=2)
        self.assertGreater(len(drops), 10)
        # early samples (ridge) high; late samples (meander) low
        early = [d for i, d in drops if i < 60]
        late = [d for i, d in drops if i > 90]
        self.assertTrue(early and late)
        self.assertGreater(sum(early) / len(early), 20.0)
        self.assertLess(sum(late) / len(late), 5.0)

        segs = split_by_local_relief(
            dem, self.BBOX, line,
            min_drop_m=15.0,
            min_seg_km=5.0,
            sample_every_n=2,
        )
        self.assertGreaterEqual(len(segs), 1)
        # kept segments are high-drop; meander run must not dominate
        for s in segs:
            self.assertGreaterEqual(s["drop_mean_m"], 15.0)
            self.assertEqual(s["grade"], "dem-contour")
            self.assertEqual(s["label"], "candidate ridge segment")
            self.assertNotIn("sponda", s["label"].lower())
            self.assertNotIn("shore found", s["label"].lower())
        # longest kept should sit on the northern ridge stretch
        best = max(segs, key=lambda s: s["length_km"])
        mid_lat = (best["line"][0][1] + best["line"][-1][1]) / 2.0
        self.assertGreater(mid_lat, 13.5)

    def test_constant_ramp_no_false_ridge_segments(self):
        n = 81
        ramp = np.tile(np.linspace(300.0, 340.0, n), (n, 1))
        lines = shoreline_from_dem(ramp, self.BBOX, 320.0)
        self.assertTrue(lines)
        report = split_longest_by_relief(
            ramp, self.BBOX, lines,
            min_drop_m=15.0,
            min_seg_km=5.0,
            sample_every_n=3,
        )
        self.assertEqual(report["n_segments"], 0)
        self.assertEqual(report["lengths_km"], [])
        self.assertEqual(report["grade"], "dem-contour")
        self.assertIn("sponda individuata", report["non_puoi_dire"])

    def test_split_lines_helper_and_report_fields(self):
        dem = self._dem_ridge_plus_flat()
        line = self._polyline_ridge_then_meander()
        all_segs = split_lines_by_relief(
            dem, self.BBOX, [line],
            min_drop_m=15.0, min_seg_km=5.0, sample_every_n=2,
        )
        self.assertGreaterEqual(len(all_segs), 1)
        report = split_longest_by_relief(
            dem, self.BBOX, [line],
            min_drop_m=15.0, min_seg_km=5.0, sample_every_n=2,
        )
        self.assertEqual(report["n_segments"], len(all_segs))
        self.assertEqual(len(report["lengths_km"]), report["n_segments"])
        self.assertEqual(len(report["drops_m"]), report["n_segments"])
        self.assertGreater(report["source_longest_km"], 0.0)

if __name__ == "__main__":
    unittest.main()
