"""
SRTM 30m DEM Client for Archaeo-Sentinel.
Fetches elevation data from OpenTopography API or generates realistic synthetic DEM.
"""
import os
import numpy as np
import requests
from typing import List, Tuple, Optional


class SRTMClient:
    """Fetches SRTM 30m DEM tiles for a given bounding box."""

    def __init__(self):
        self.api_key = os.getenv("OPENTOPOGRAPHY_API_KEY", "")
        self.base_url = "https://portal.opentopography.org/API/globaldem"

    def fetch_dem(self, bbox: List[float], target_shape: Tuple[int, int] = (512, 512)) -> Optional[np.ndarray]:
        """
        Fetch real SRTM 30m DEM for bbox [lon_min, lat_min, lon_max, lat_max].
        Returns None if the API key is missing or the request fails.
        Does not invent terrain. A fake valley is not evidence.
        """
        return self._fetch_real(bbox, target_shape)

    def _fetch_real(self, bbox: List[float], target_shape: Tuple[int, int]) -> Optional[np.ndarray]:
        """Try OpenTopography SRTM GL1 (30m) API."""
        if not self.api_key:
            print("[WARN] OPENTOPOGRAPHY_API_KEY assente -> nessun DEM. Non inventiamo il terreno.")
            return None

        try:
            params = {
                "demtype": "SRTMGL1",
                "south": bbox[1],
                "north": bbox[3],
                "west": bbox[0],
                "east": bbox[2],
                "outputFormat": "AAIGrid",
                "API_Key": self.api_key,
            }
            resp = requests.get(self.base_url, params=params, timeout=30)
            resp.raise_for_status()

            # Parse AAIGrid (ASCII raster)
            lines = resp.text.strip().split("\n")
            header = {}
            data_start = 0
            for i, line in enumerate(lines):
                parts = line.strip().split()
                if len(parts) == 2 and parts[0].lower() in (
                    "ncols", "nrows", "xllcorner", "yllcorner", "cellsize", "nodata_value"
                ):
                    header[parts[0].lower()] = float(parts[1])
                    data_start = i + 1
                else:
                    break

            rows = []
            for line in lines[data_start:]:
                vals = [float(v) for v in line.strip().split()]
                if vals:
                    rows.append(vals)

            dem = np.array(rows, dtype=np.float64)

            # Handle NODATA
            nodata = header.get("nodata_value", -9999)
            dem[dem == nodata] = np.nan

            # Resize to target shape
            if dem.shape != target_shape:
                from PIL import Image
                img = Image.fromarray(dem)
                img = img.resize((target_shape[1], target_shape[0]), Image.BILINEAR)
                dem = np.array(img, dtype=np.float64)

            print(f"[OK] DEM SRTM 30m reale caricato: {dem.shape}, range [{np.nanmin(dem):.0f} - {np.nanmax(dem):.0f}]m")
            return dem

        except Exception as e:
            print(f"[WARN] OpenTopography API fallita: {e} -> DEM sintetico")
            return None

    def _generate_synthetic(self, bbox: List[float], shape: Tuple[int, int]) -> np.ndarray:
        """
        Generate realistic synthetic DEM based on region coordinates.
        Uses multiple frequency noise to simulate terrain.
        """
        h, w = shape
        rng = np.random.default_rng(int(abs(bbox[0] * 1000 + bbox[1] * 100)))

        # Base elevation from latitude (higher toward mountains)
        lat_center = (bbox[1] + bbox[3]) / 2
        lon_center = (bbox[0] + bbox[2]) / 2

        # Regional base elevation heuristic (Mediterranean/Middle East)
        base_elevation = 150 + abs(lat_center - 35) * 30 + abs(lon_center - 35) * 10

        # Multi-frequency terrain
        y = np.linspace(0, 1, h)
        x = np.linspace(0, 1, w)
        xx, yy = np.meshgrid(x, y)

        # Large-scale terrain (hills)
        terrain = np.sin(xx * 3.5 + 0.7) * np.cos(yy * 2.8 + 1.2) * 80
        # Medium-scale ridges
        terrain += np.sin(xx * 8 + yy * 6) * 25
        # Fine-scale noise
        terrain += rng.normal(0, 8, shape)

        dem = base_elevation + terrain

        dem = np.clip(dem, 0, 4000).astype(np.float64)
        print(f"[DEM] Sintetico generato: {shape}, range [{dem.min():.0f} - {dem.max():.0f}]m")
        return dem


def compute_slope(dem: np.ndarray, cell_size: float = 30.0) -> np.ndarray:
    """
    Compute slope in degrees from DEM.
    cell_size: pixel resolution in meters (SRTM 30m = 30.0)
    """
    dy, dx = np.gradient(dem, cell_size)
    slope_rad = np.arctan(np.sqrt(dx ** 2 + dy ** 2))
    return np.degrees(slope_rad)


def compute_aspect(dem: np.ndarray, cell_size: float = 30.0) -> np.ndarray:
    """Compute aspect (compass direction of slope) in degrees."""
    dy, dx = np.gradient(dem, cell_size)
    aspect = np.degrees(np.arctan2(-dy, dx))
    aspect = (aspect + 360) % 360
    return aspect


def compute_tpi(dem: np.ndarray, radius: int = 5) -> np.ndarray:
    """
    Topographic Position Index: difference between cell elevation and mean of neighbors.
    Negative = valley/depression, Positive = ridge/hilltop.
    """
    try:
        from scipy.ndimage import uniform_filter
        mean_elev = uniform_filter(dem, size=radius * 2 + 1, mode='nearest')
    except ImportError:
        from numpy.lib.stride_tricks import sliding_window_view
        k = radius * 2 + 1
        pad = np.pad(dem, radius, mode='edge')
        mean_elev = sliding_window_view(pad, (k, k)).mean(axis=(-1, -2))
    return dem - mean_elev


srtm_client = SRTMClient()
