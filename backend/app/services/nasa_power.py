from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx
import pandas as pd

from app.config import NASA_POWER_BASE_URL, NASA_POWER_ENDPOINT, NASA_MAX_CONNECTIONS
from app.core.validators import snap_to_merra2_grid

logger = logging.getLogger(__name__)

# NASA POWER API 单次请求最多 366 天，因此按年分段请求
_MAX_RETRIES = 3


class NASAPowerError(Exception):
    pass


async def _fetch_year(
    client: httpx.AsyncClient,
    lat: float,
    lon: float,
    height: int,
    year: int,
    wind_surface: str,
    semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    """Fetch a single year of wind data for one height level with exponential backoff retry."""
    # Wind direction: ≤50 m → WD10M, >50 m → WD50M (API limitation)
    wd_param = "WD10M" if height <= 50 else "WD50M"
    # Request WS50M as the base parameter; when wind-elevation is set the API
    # automatically returns a 'WSC' key containing the adjusted custom-height speed.
    ws_param = "WS50M"

    # Explicit param dict – never pass user input directly (SSRF/injection protection)
    params: dict[str, Any] = {
        "latitude": lat,
        "longitude": lon,
        "wind-elevation": height,
        "wind-surface": wind_surface,
        "start": f"{year}0101",
        "end": f"{year}1231",
        "parameters": f"{ws_param},{wd_param}",
        "community": "RE",
        "time-standard": "UTC",
        "format": "JSON",
    }

    for attempt in range(_MAX_RETRIES):
        async with semaphore:
            try:
                response = await client.get(
                    NASA_POWER_ENDPOINT,
                    params=params,
                    timeout=60.0,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code in (429, 503) and attempt < _MAX_RETRIES - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise NASAPowerError(
                    f"NASA POWER API HTTP {exc.response.status_code} for height={height}m year={year}"
                ) from exc
            except (httpx.RequestError, httpx.TimeoutException) as exc:
                if attempt < _MAX_RETRIES - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise NASAPowerError(
                    f"NASA POWER API 请求失败 height={height}m year={year}: {exc}"
                ) from exc

    raise NASAPowerError(f"NASA POWER API 超过最大重试次数 height={height}m year={year}")


def _parse_year_response(data: dict[str, Any], height: int) -> pd.DataFrame:
    """Extract hourly wind speed and direction from a single-year API response."""
    props = data.get("properties", {})
    parameters = props.get("parameter", {})

    # The API returns the custom-height adjusted wind speed under key 'WSC'
    # regardless of the requested height. 'WS50M' is the unadjusted base.
    ws_key = "WSC"
    wd_key = "WD10M" if height <= 50 else "WD50M"

    ws_data = parameters.get(ws_key) or parameters.get("WS50M", {})
    wd_data = parameters.get(wd_key, {})

    if not ws_data:
        available = list(parameters.keys())
        raise NASAPowerError(
            f"API 响应中未找到高度 {height}m 的风速数据。"
            f"可用参数键: {available}"
        )

    timestamps = list(ws_data.keys())
    ws_values = [float(v) if v != -999.0 else float("nan") for v in ws_data.values()]
    wd_values = [float(v) if v != -999.0 else float("nan") for v in wd_data.values()] if wd_data else [float("nan")] * len(timestamps)

    df = pd.DataFrame({
        "timestamp": pd.to_datetime(timestamps, format="%Y%m%d%H"),
        f"ws_{height}m": ws_values,
        f"wd_{height}m": wd_values,
    })
    return df.set_index("timestamp")


async def fetch_wind_data(
    lat: float,
    lon: float,
    heights: list[int],
    start_year: int,
    end_year: int,
    wind_surface: str,
    progress_callback: Any = None,
) -> dict[int, pd.DataFrame]:
    """
    Fetch MERRA-2 hourly wind data for all heights and years concurrently.

    Returns a dict mapping height (int) → pd.DataFrame indexed by timestamp.
    The callback signature: progress_callback(completed: int, total: int, message: str)
    """
    grid_lat, grid_lon = snap_to_merra2_grid(lat, lon)
    years = list(range(start_year, end_year + 1))
    tasks_total = len(heights) * len(years)
    tasks_done = 0

    limits = httpx.Limits(max_connections=NASA_MAX_CONNECTIONS, max_keepalive_connections=5)
    semaphore = asyncio.Semaphore(NASA_MAX_CONNECTIONS)

    async with httpx.AsyncClient(base_url=NASA_POWER_BASE_URL, limits=limits) as client:
        # Build all fetch coroutines
        fetch_jobs: list[tuple[int, int, asyncio.Task]] = []
        for h in heights:
            for y in years:
                task = asyncio.create_task(
                    _fetch_year(client, grid_lat, grid_lon, h, y, wind_surface, semaphore)
                )
                fetch_jobs.append((h, y, task))

        # Gather with progress
        results_by_height: dict[int, list[pd.DataFrame]] = {h: [] for h in heights}
        errors: list[str] = []

        for h, y, task in fetch_jobs:
            try:
                year_data = await task
                df = _parse_year_response(year_data, h)
                results_by_height[h].append(df)
            except NASAPowerError as exc:
                errors.append(str(exc))
                logger.warning("跳过 height=%dm year=%d: %s", h, y, exc)

            tasks_done += 1
            if progress_callback:
                progress_callback(
                    tasks_done,
                    tasks_total,
                    f"已获取 {tasks_done}/{tasks_total} 个数据段 (height={h}m, year={y})",
                )

    if errors and tasks_done == 0:
        raise NASAPowerError(f"所有 NASA POWER API 请求均失败。第一个错误: {errors[0]}")

    # Concatenate years for each height
    combined: dict[int, pd.DataFrame] = {}
    for h in heights:
        frames = results_by_height[h]
        if frames:
            combined[h] = pd.concat(frames).sort_index()

    return combined
