"""
Layer rendering: converts numpy arrays to base64 PNG for Leaflet ImageOverlay.
"""
import io
import base64
import numpy as np
from PIL import Image


def array_to_colormap_png(data: np.ndarray, cmap: str = "viridis",
                           vmin: float = None, vmax: float = None,
                           alpha: float = 0.7) -> str:
    """
    Convert a 2D numpy array to a base64-encoded RGBA PNG using a colormap.
    Returns: base64 string ready for data:image/png;base64,... URI.
    """
    arr = data.copy().astype(np.float64)

    # Handle NaN
    nan_mask = np.isnan(arr)
    if vmin is None:
        vmin = float(np.nanmin(arr))
    if vmax is None:
        vmax = float(np.nanmax(arr))

    # Normalize to 0-1
    if vmax - vmin > 0:
        arr = (arr - vmin) / (vmax - vmin)
    else:
        arr = np.zeros_like(arr)
    arr = np.clip(arr, 0, 1)

    # Apply colormap
    rgba = _apply_colormap(arr, cmap, alpha)

    # Transparent where NaN
    rgba[nan_mask, 3] = 0

    img = Image.fromarray(rgba, 'RGBA')
    buf = io.BytesIO()
    img.save(buf, format='PNG', optimize=True)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def _apply_colormap(normalized: np.ndarray, cmap: str, alpha: float) -> np.ndarray:
    """Apply a colormap to normalized [0,1] data. Returns RGBA uint8 array."""
    h, w = normalized.shape
    rgba = np.zeros((h, w, 4), dtype=np.uint8)

    colormaps = {
        "ndvi": [  # Red → Yellow → Green
            (0.0, (180, 30, 30)),
            (0.3, (220, 160, 40)),
            (0.5, (200, 200, 60)),
            (0.7, (80, 180, 60)),
            (1.0, (20, 120, 40)),
        ],
        "bsi": [  # Blue → White → Brown
            (0.0, (30, 60, 150)),
            (0.3, (100, 140, 200)),
            (0.5, (220, 220, 220)),
            (0.7, (180, 140, 80)),
            (1.0, (140, 80, 20)),
        ],
        "dem": [  # Green → Yellow → Brown → White (topographic)
            (0.0, (40, 120, 60)),
            (0.2, (80, 160, 60)),
            (0.4, (200, 200, 80)),
            (0.6, (180, 140, 60)),
            (0.8, (140, 100, 60)),
            (1.0, (240, 240, 240)),
        ],
        "slope": [  # White → Orange → Red
            (0.0, (240, 240, 240)),
            (0.3, (255, 200, 100)),
            (0.6, (240, 120, 40)),
            (1.0, (180, 30, 30)),
        ],
        "viridis": [  # Approximate viridis
            (0.0, (68, 1, 84)),
            (0.25, (59, 82, 139)),
            (0.5, (33, 145, 140)),
            (0.75, (94, 201, 98)),
            (1.0, (253, 231, 37)),
        ],
    }

    stops = colormaps.get(cmap, colormaps["viridis"])

    for y in range(h):
        for x in range(w):
            v = normalized[y, x]
            # Find surrounding stops
            for i in range(len(stops) - 1):
                if v <= stops[i + 1][0]:
                    t = (v - stops[i][0]) / (stops[i + 1][0] - stops[i][0]) if stops[i + 1][0] != stops[i][0] else 0
                    c0 = stops[i][1]
                    c1 = stops[i + 1][1]
                    r = int(c0[0] + (c1[0] - c0[0]) * t)
                    g = int(c0[1] + (c1[1] - c0[1]) * t)
                    b = int(c0[2] + (c1[2] - c0[2]) * t)
                    rgba[y, x] = [r, g, b, int(alpha * 255)]
                    break

    return rgba


def array_to_colormap_png_fast(data: np.ndarray, cmap: str = "viridis",
                                vmin: float = None, vmax: float = None,
                                alpha: float = 0.7) -> str:
    """
    Fast vectorized version using lookup table (256 entries).
    """
    arr = data.copy().astype(np.float64)
    nan_mask = np.isnan(arr)

    if vmin is None:
        vmin = float(np.nanmin(arr))
    if vmax is None:
        vmax = float(np.nanmax(arr))

    if vmax - vmin > 0:
        arr = (arr - vmin) / (vmax - vmin)
    else:
        arr = np.zeros_like(arr)
    arr = np.clip(arr, 0, 1)

    # Build 256-entry LUT
    lut = _build_lut(cmap, alpha)

    # Map to indices
    indices = (arr * 255).astype(np.uint8)
    rgba = lut[indices]

    # Transparent NaN
    rgba[nan_mask, 3] = 0

    img = Image.fromarray(rgba, 'RGBA')
    buf = io.BytesIO()
    img.save(buf, format='PNG', optimize=True)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def _build_lut(cmap: str, alpha: float) -> np.ndarray:
    """Build a 256x4 RGBA lookup table for the given colormap."""
    colormaps = {
        "ndvi": [(0.0, (180, 30, 30)), (0.3, (220, 160, 40)), (0.5, (200, 200, 60)),
                 (0.7, (80, 180, 60)), (1.0, (20, 120, 40))],
        "bsi": [(0.0, (30, 60, 150)), (0.3, (100, 140, 200)), (0.5, (220, 220, 220)),
                (0.7, (180, 140, 80)), (1.0, (140, 80, 20))],
        "dem": [(0.0, (40, 120, 60)), (0.2, (80, 160, 60)), (0.4, (200, 200, 80)),
                (0.6, (180, 140, 60)), (0.8, (140, 100, 60)), (1.0, (240, 240, 240))],
        "slope": [(0.0, (240, 240, 240)), (0.3, (255, 200, 100)),
                  (0.6, (240, 120, 40)), (1.0, (180, 30, 30))],
        "viridis": [(0.0, (68, 1, 84)), (0.25, (59, 82, 139)), (0.5, (33, 145, 140)),
                    (0.75, (94, 201, 98)), (1.0, (253, 231, 37))],
    }
    stops = colormaps.get(cmap, colormaps["viridis"])
    lut = np.zeros((256, 4), dtype=np.uint8)

    for i in range(256):
        v = i / 255.0
        for j in range(len(stops) - 1):
            if v <= stops[j + 1][0]:
                t = (v - stops[j][0]) / (stops[j + 1][0] - stops[j][0]) if stops[j + 1][0] != stops[j][0] else 0
                c0 = stops[j][1]
                c1 = stops[j + 1][1]
                lut[i] = [
                    int(c0[0] + (c1[0] - c0[0]) * t),
                    int(c0[1] + (c1[1] - c0[1]) * t),
                    int(c0[2] + (c1[2] - c0[2]) * t),
                    int(alpha * 255)
                ]
                break

    return lut
