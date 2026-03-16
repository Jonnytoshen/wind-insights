from __future__ import annotations


def snap_to_merra2_grid(lat: float, lon: float) -> tuple[float, float]:
    """Round coordinates to the nearest MERRA-2 grid point (0.5° lat × 0.625° lon)."""
    grid_lat = round(lat / 0.5) * 0.5
    grid_lon = round(lon / 0.625) * 0.625
    return grid_lat, grid_lon


def build_cache_key(
    lat: float,
    lon: float,
    heights: list[int],
    start_year: int,
    end_year: int,
    wind_surface: str,
) -> tuple:
    """Build a deterministic cache key using grid-snapped coordinates."""
    grid_lat, grid_lon = snap_to_merra2_grid(lat, lon)
    return (grid_lat, grid_lon, tuple(sorted(heights)), start_year, end_year, wind_surface)
