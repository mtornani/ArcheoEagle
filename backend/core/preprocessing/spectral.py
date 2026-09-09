import numpy as np

def calculate_ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
    """
    Calculate Normalized Difference Vegetation Index (NDVI).
    NDVI = (NIR - RED) / (NIR + RED)
    """
    denominator = nir + red
    np.seterr(invalid='ignore', divide='ignore')
    ndvi = np.where(denominator == 0, 0, (nir - red) / denominator)
    return ndvi

def calculate_bsi(swir: np.ndarray, red: np.ndarray, nir: np.ndarray, blue: np.ndarray) -> np.ndarray:
    """
    Calculate Bare Soil Index (BSI).
    BSI = ((SWIR + RED) - (NIR + BLUE)) / ((SWIR + RED) + (NIR + BLUE))
    """
    term1 = swir + red
    term2 = nir + blue
    denominator = term1 + term2
    np.seterr(invalid='ignore', divide='ignore')
    bsi = np.where(denominator == 0, 0, (term1 - term2) / denominator)
    return bsi
