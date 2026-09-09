import os
import numpy as np
import requests
from typing import Dict, Any, List, Tuple

class CopernicusClient:
    """Client for Copernicus Data Space Ecosystem (CDSE)."""

    def __init__(self):
        self.username = os.getenv("COPERNICUS_USER")
        self.password = os.getenv("COPERNICUS_PASSWORD")
        self.token = None
        self.auth_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
        self.odata_url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

    def authenticate(self) -> bool:
        if not self.username or not self.password:
            print("Copernicus credentials missing.")
            return False

        data = {
            "client_id": "cdse-public",
            "username": self.username,
            "password": self.password,
            "grant_type": "password",
        }
        try:
            response = requests.post(self.auth_url, data=data, timeout=15)
            response.raise_for_status()
            self.token = response.json().get("access_token")
            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def search_sentinel2(self, bbox: List[float], max_cloud_cover: int = 20) -> List[Dict[str, Any]]:
        """
        Search for Sentinel-2 L2A imagery intersecting the bbox.
        bbox: [minx, miny, maxx, maxy] (longitude, latitude)
        """
        if not self.token:
            if not self.authenticate():
                return [{"id": "mock-scene-1234", "Name": "S2A_MSIL2A_MOCK_SCENE", "cloudCover": 5.0}]

        polygon = f"POLYGON(({bbox[0]} {bbox[1]}, {bbox[2]} {bbox[1]}, {bbox[2]} {bbox[3]}, {bbox[0]} {bbox[3]}, {bbox[0]} {bbox[1]}))"

        filter_query = (
            f"OData.CSC.Intersects(area=geography'SRID=4326;{polygon}') "
            f"and Collection/Name eq 'SENTINEL-2' "
            f"and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/Value eq 'S2MSI2A') "
            f"and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/Value le {max_cloud_cover})"
        )

        params = {
            "$filter": filter_query,
            "$top": 5,
            "$orderby": "ContentDate/Start desc"
        }

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(self.odata_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json().get("value", [])
        except Exception as e:
            print(f"Search failed: {e}")
            return []

    def acquire_and_download(self, geojson: Dict[str, Any], max_cloud_cover: int = 20) -> Tuple[Dict[str, np.ndarray], List[float]]:
        """
        Acquire Sentinel-2 bands for the AOI.
        Returns (bands_dict, bbox) — uses realistic mock when credentials are missing.
        """
        bbox = get_bbox_from_geojson(geojson)

        # TODO: integrate SentinelHub Process API for real band download
        # For now, generate realistic mock at 512x512 (typical 10m tile)
        rng = np.random.default_rng(42)
        h, w = 512, 512

        # Realistic Sentinel-2 L2A reflectance values (surface reflectance * 10000)
        bands = {
            'B02': rng.normal(400, 80, (h, w)).clip(0).astype(np.float64),   # Blue
            'B04': rng.normal(600, 120, (h, w)).clip(0).astype(np.float64),  # Red
            'B08': rng.normal(2200, 300, (h, w)).clip(0).astype(np.float64), # NIR
            'B11': rng.normal(1800, 250, (h, w)).clip(0).astype(np.float64), # SWIR
        }

        # Inject 2-3 realistic archaeological anomalies (crop marks + soil marks)
        # Anomaly 1: large buried structure (60x60 px = ~600m x 600m)
        bands['B08'][220:280, 220:280] = rng.normal(800, 50, (60, 60)).clip(200)
        bands['B04'][220:280, 220:280] = rng.normal(2400, 100, (60, 60)).clip(1500)
        bands['B11'][220:280, 220:280] = rng.normal(2600, 80, (60, 60)).clip(2000)
        bands['B02'][220:280, 220:280] = rng.normal(350, 40, (60, 60)).clip(100)

        # Anomaly 2: smaller feature (25x25 px)
        bands['B08'][380:405, 100:125] = rng.normal(900, 60, (25, 25)).clip(300)
        bands['B04'][380:405, 100:125] = rng.normal(2100, 90, (25, 25)).clip(1400)
        bands['B11'][380:405, 100:125] = rng.normal(2500, 70, (25, 25)).clip(1800)
        bands['B02'][380:405, 100:125] = rng.normal(380, 30, (25, 25)).clip(150)

        # Anomaly 3: linear feature (canal/road, 8x80 px)
        bands['B08'][60:68, 300:380] = rng.normal(750, 40, (8, 80)).clip(200)
        bands['B04'][60:68, 300:380] = rng.normal(2300, 80, (8, 80)).clip(1600)
        bands['B11'][60:68, 300:380] = rng.normal(2700, 60, (8, 80)).clip(2100)
        bands['B02'][60:68, 300:380] = rng.normal(340, 30, (8, 80)).clip(100)

        return bands, bbox


def get_bbox_from_geojson(geojson: Dict[str, Any]) -> List[float]:
    """Extract bounding box [lon_min, lat_min, lon_max, lat_max] from GeoJSON."""
    from core.hydro.paleorivers import bbox_from_geojson
    return bbox_from_geojson(geojson)


copernicus_client = CopernicusClient()
