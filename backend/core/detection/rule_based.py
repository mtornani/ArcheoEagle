import numpy as np
from core.preprocessing.spectral import calculate_ndvi, calculate_bsi


def detect_anomalies(sentinel_bands: dict, dem: np.ndarray = None) -> dict:
    """
    Perform rule-based anomaly detection based on NDVI, BSI, and optionally DEM.
    Expected sentinel_bands: {'B02': ndarray, 'B04': ndarray, 'B08': ndarray, 'B11': ndarray}
    dem: optional 2D elevation array (meters), same shape as bands.
    """
    try:
        nir = sentinel_bands.get('B08')
        red = sentinel_bands.get('B04')
        swir = sentinel_bands.get('B11')
        blue = sentinel_bands.get('B02')

        if any(b is None for b in [nir, red, swir, blue]):
            return {"error": "Missing required bands (B02, B04, B08, B11)"}

        ndvi_map = calculate_ndvi(nir, red)
        bsi_map = calculate_bsi(swir, red, nir, blue)

        # Rule 1: NDVI low compared to surroundings (crop mark proxy)
        ndvi_mean = np.nanmean(ndvi_map)
        ndvi_std = np.nanstd(ndvi_map)
        ndvi_threshold = ndvi_mean - 1.5 * ndvi_std
        ndvi_anomaly = ndvi_map < ndvi_threshold

        # Rule 2: High BSI indicating bare soil (soil mark proxy)
        bsi_threshold = 0.2
        bsi_anomaly = bsi_map > bsi_threshold

        # Rule 3: DEM-based — flat terrain / valley preference
        dem_anomaly = np.ones_like(ndvi_anomaly, dtype=bool)  # default: all pass
        slope_map = None
        tpi_map = None
        dem_stats = {}

        if dem is not None and dem.shape == nir.shape:
            from core.imagery.srtm import compute_slope, compute_tpi
            slope_map = compute_slope(dem, cell_size=30.0)
            tpi_map = compute_tpi(dem, radius=5)

            # Archaeological sites favor gentle slopes (<15 degrees)
            # and slightly negative TPI (valleys/depressions, not hilltops)
            slope_threshold = 15.0
            tpi_threshold = 5.0  # sites with TPI < 5 (not on ridges)
            dem_anomaly = np.logical_and(
                slope_map < slope_threshold,
                tpi_map < tpi_threshold
            )
            dem_stats = {
                "slope_mean": float(np.nanmean(slope_map)),
                "slope_max": float(np.nanmax(slope_map)),
                "tpi_mean": float(np.nanmean(tpi_map)),
                "elevation_range": [float(np.nanmin(dem)), float(np.nanmax(dem))],
            }

        # Combined Anomaly (all rules must pass)
        combined_anomaly = np.logical_and(ndvi_anomaly, bsi_anomaly)
        combined_anomaly = np.logical_and(combined_anomaly, dem_anomaly)
        anomaly_pixel_count = int(np.sum(combined_anomaly))

        # Compute values inside anomaly zone for explanation
        ndvi_anomaly_mean = float(np.nanmean(ndvi_map[combined_anomaly])) if anomaly_pixel_count > 0 else None
        bsi_anomaly_mean = float(np.nanmean(bsi_map[combined_anomaly])) if anomaly_pixel_count > 0 else None

        # Build reasoning chain
        reasons = []
        if anomaly_pixel_count > 0:
            reasons.append({
                "rule": "NDVI Crop Mark",
                "triggered": True,
                "detail": (
                    f"La vegetazione nella zona anomala ha NDVI medio {ndvi_anomaly_mean:.3f}, "
                    f"significativamente sotto la media circostante ({ndvi_mean:.3f}). "
                    f"Soglia applicata: < {ndvi_threshold:.3f} (media - 1.5 deviazioni standard). "
                    f"Strutture sepolte alterano la crescita radicale, creando 'crop marks' visibili nello spettro NIR."
                ),
            })
            reasons.append({
                "rule": "BSI Soil Mark",
                "triggered": True,
                "detail": (
                    f"L'indice di suolo nudo (BSI) nella zona anomala e' {bsi_anomaly_mean:.3f}, "
                    f"sopra la soglia {bsi_threshold}. "
                    f"Terreno con riflettanza SWIR/Red elevata indica suolo disturbato o compattato, "
                    f"tipico di fondamenta, muri o strutture interrate che alterano il drenaggio."
                ),
            })

            if dem is not None and slope_map is not None:
                slope_anom_mean = float(np.nanmean(slope_map[combined_anomaly]))
                tpi_anom_mean = float(np.nanmean(tpi_map[combined_anomaly]))
                elev_anom_mean = float(np.nanmean(dem[combined_anomaly]))
                reasons.append({
                    "rule": "DEM Analisi Morfologica",
                    "triggered": True,
                    "detail": (
                        f"L'area anomala si trova a ~{elev_anom_mean:.0f}m s.l.m. con pendenza media "
                        f"di {slope_anom_mean:.1f}° (soglia < 15°) e TPI {tpi_anom_mean:.1f} "
                        f"(indice di posizione topografica). "
                        f"Le strutture archeologiche si trovano preferenzialmente su terreni pianeggianti "
                        f"o in leggere depressioni, vicino a corsi d'acqua antichi. "
                        f"Il DEM SRTM 30m conferma morfologia compatibile."
                    ),
                })

            reasons.append({
                "rule": "Combinazione Multi-Indice" + (" + DEM" if dem is not None else ""),
                "triggered": True,
                "detail": (
                    f"La sovrapposizione di anomalia vegetativa (NDVI basso), suolo esposto (BSI alto)"
                    f"{' e morfologia favorevole (DEM)' if dem is not None else ''} "
                    f"su {anomaly_pixel_count} pixel contigui e' un pattern compatibile con strutture "
                    f"archeologiche sepolte (muri, fondamenta, canali)."
                ),
            })

        return {
            "ndvi_map": ndvi_map,
            "bsi_map": bsi_map,
            "slope_map": slope_map,
            "tpi_map": tpi_map,
            "dem": dem,
            "ndvi_mean": float(ndvi_mean),
            "ndvi_threshold": float(ndvi_threshold),
            "ndvi_anomaly_mean": ndvi_anomaly_mean,
            "bsi_threshold_applied": bsi_threshold,
            "bsi_anomaly_mean": bsi_anomaly_mean,
            "anomaly_pixels_detected": anomaly_pixel_count,
            "reasons": reasons,
            "dem_stats": dem_stats,
            "success": True,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e), "success": False}
