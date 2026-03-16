from __future__ import annotations

import logging
from typing import Callable

import numpy as np
import pandas as pd

from app.algorithms.weibull import fit_weibull, build_histogram, compute_fitted_pdf
from app.algorithms.extreme_wind import compute_extreme_wind
from app.algorithms.turbulence import compute_turbulence
from app.algorithms.shear import fit_power_law_shear
from app.algorithms.representative_year import select_representative_year

logger = logging.getLogger(__name__)

AIR_DENSITY = 1.225  # kg/m³ standard


def _detect_outliers(ws: pd.Series, sigma: float = 3.0) -> pd.Series:
    """Return boolean mask True where values are outliers (|z| > sigma)."""
    mean = ws.mean()
    std = ws.std(ddof=1)
    if std == 0:
        return pd.Series(False, index=ws.index)
    return ((ws - mean).abs() > sigma * std)


def _compute_basic_stats(df: pd.DataFrame, ws_col: str, wd_col: str, filter_outliers: bool) -> dict:
    raw = df[ws_col].copy()
    total = len(raw)

    outlier_mask = _detect_outliers(raw.dropna()) if filter_outliers else pd.Series(False, index=raw.dropna().index)
    valid = raw.dropna()
    valid_clean = valid[~outlier_mask] if filter_outliers else valid

    annual_mean_ws = round(float(valid_clean.mean()), 4)
    data_valid_rate = round(float(valid_clean.count() / total * 100), 2) if total > 0 else 0.0
    outlier_count = int(outlier_mask.sum())

    # Monthly mean time series
    monthly = valid_clean.resample("ME").mean()
    timestamps = [str(d.strftime("%Y-%m")) for d in monthly.index]
    values = [round(float(v), 4) for v in monthly]

    # Dominant direction
    wd = df[wd_col].dropna()
    if not wd.empty:
        direction_sectors = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                             "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        sector_size = 360 / len(direction_sectors)
        sector_idx = ((wd + sector_size / 2) % 360 / sector_size).astype(int) % len(direction_sectors)
        dominant_idx = int(sector_idx.value_counts().idxmax())
        dominant_direction = direction_sectors[dominant_idx]
    else:
        dominant_direction = "N/A"

    return {
        "annual_mean_ws": annual_mean_ws,
        "data_valid_rate": data_valid_rate,
        "outlier_count": outlier_count,
        "monthly_mean_timestamps": timestamps,
        "monthly_mean_values": values,
        "dominant_direction": dominant_direction,
    }


def _compute_wind_rose(df: pd.DataFrame, ws_col: str, wd_col: str) -> dict:
    ws = df[ws_col].dropna()
    wd = df[wd_col].dropna()
    common = ws.index.intersection(wd.index)
    ws = ws.loc[common]
    wd = wd.loc[common]

    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    n_dirs = len(directions)
    sector_size = 360 / n_dirs
    speed_bins = [0, 3, 6, 9, 12, 9999]

    sector_assignments = ((wd + sector_size / 2) % 360 / sector_size).astype(int) % n_dirs
    total = len(ws)

    frequency = []
    speed_bin_freqs: list[list[float]] = [[] for _ in range(len(speed_bins) - 1)]

    for d_idx in range(n_dirs):
        mask = sector_assignments == d_idx
        sector_ws = ws[mask]
        sector_freq = round(float(len(sector_ws) / total * 100), 2) if total > 0 else 0.0
        frequency.append(sector_freq)

        for b_idx in range(len(speed_bins) - 1):
            lo, hi = speed_bins[b_idx], speed_bins[b_idx + 1]
            bin_freq = round(float(((sector_ws >= lo) & (sector_ws < hi)).sum() / total * 100), 2) if total > 0 else 0.0
            speed_bin_freqs[b_idx].append(bin_freq)

    return {
        "directions": directions,
        "frequency": frequency,
        "speed_bin_freqs": speed_bin_freqs,
    }


def _compute_wpd(ws: pd.Series) -> dict:
    monthly = ws.dropna().resample("ME")
    monthly_wpd = []
    for _name, group in monthly:
        if group.empty:
            monthly_wpd.append(0.0)
        else:
            # WPD = 0.5 * rho * mean(v³) — correct formula
            wpd = 0.5 * AIR_DENSITY * float((group ** 3).mean())
            monthly_wpd.append(round(wpd, 2))

    all_ws = ws.dropna()
    annual_wpd = round(0.5 * AIR_DENSITY * float((all_ws ** 3).mean()), 2) if not all_ws.empty else 0.0

    return {
        "annual_wpd": annual_wpd,
        "monthly_wpd": monthly_wpd,
    }


def run_full_analysis(
    raw_data: dict[int, pd.DataFrame],
    heights: list[int],
    filter_outliers: bool,
    progress: Callable[[int, int, str], None] | None = None,
) -> dict:
    """
    Run all analysis algorithms on the raw wind data.

    Parameters
    ----------
    raw_data        : height → DataFrame(index=DatetimeIndex, ws_{h}m, wd_{h}m)
    heights         : sorted list of analysis heights
    filter_outliers : whether to remove 3σ outliers before computing stats
    progress        : optional callback(step, total_steps, message)

    Returns
    -------
    dict matching the AnalysisResult response model schema
    """
    steps_total = len(heights) * 6 + (1 if len(heights) >= 2 else 0)
    step = 0

    def _progress(msg: str) -> None:
        nonlocal step
        step += 1
        if progress:
            progress(step, steps_total, msg)

    basic_stats: dict[str, dict] = {}
    weibull_results: dict[str, dict] = {}
    wind_rose_data: dict[str, dict] = {}
    extreme_wind_results: dict[str, dict] = {}
    rep_year_results: dict[str, dict] = {}
    turbulence_data: dict[str, dict] = {}
    wpd_results: dict[str, dict] = {}

    for h in heights:
        key = f"{h}m"
        df = raw_data.get(h)
        if df is None or df.empty:
            logger.warning("高度 %dm 无数据，跳过", h)
            continue

        ws_col = f"ws_{h}m"
        wd_col = f"wd_{h}m"
        ws = df[ws_col].dropna()

        # 1. Basic stats
        _progress(f"{key} 基础统计")
        try:
            basic_stats[key] = _compute_basic_stats(df, ws_col, wd_col, filter_outliers)
        except Exception as exc:
            logger.error("基础统计失败 %s: %s", key, exc)

        # 2. Weibull
        _progress(f"{key} Weibull 拟合")
        try:
            ws_arr = ws.values.astype(float)
            k, c = fit_weibull(ws_arr)
            bins, freqs = build_histogram(ws_arr)
            fitted = compute_fitted_pdf(bins, k, c)
            weibull_results[key] = {
                "k": round(k, 4),
                "c": round(c, 4),
                "histogram": {"bins": bins, "frequencies": freqs},
                "fitted_pdf": fitted,
            }
        except Exception as exc:
            logger.error("Weibull 拟合失败 %s: %s", key, exc)

        # 3. Wind rose
        _progress(f"{key} 风向玫瑰图")
        try:
            wind_rose_data[key] = _compute_wind_rose(df, ws_col, wd_col)
        except Exception as exc:
            logger.error("风向玫瑰图失败 %s: %s", key, exc)

        # 4. WPD
        _progress(f"{key} 风功率密度")
        try:
            wpd_results[key] = _compute_wpd(ws)
        except Exception as exc:
            logger.error("WPD 计算失败 %s: %s", key, exc)

        # 5. Extreme wind
        _progress(f"{key} 极端风速")
        try:
            annual_max = ws.resample("YE").max().dropna()
            years_list = [int(d.year) for d in annual_max.index]
            extreme_wind_results[key] = compute_extreme_wind(annual_max.values, years_list)
        except Exception as exc:
            logger.warning("极端风速分析失败 %s: %s", key, exc)
            extreme_wind_results[key] = {"error": str(exc)}

        # 6. Representative year
        _progress(f"{key} 代表年")
        try:
            rep_year_results[key] = select_representative_year(df, ws_col)
        except Exception as exc:
            logger.error("代表年分析失败 %s: %s", key, exc)

        # Turbulence (attached to basic analysis, same step)
        try:
            turbulence_data[key] = compute_turbulence(df, ws_col)
        except Exception as exc:
            logger.error("湍流强度计算失败 %s: %s", key, exc)

    # Shear analysis (requires ≥2 heights)
    shear_result = None
    if len(heights) >= 2:
        _progress("风切变指数拟合")
        try:
            mean_speeds = [
                float(raw_data[h][f"ws_{h}m"].dropna().mean())
                for h in heights
                if h in raw_data and not raw_data[h].empty
            ]
            valid_heights = [
                h for h in heights
                if h in raw_data and not raw_data[h].empty
            ]
            shear_result = fit_power_law_shear(valid_heights, mean_speeds)
        except Exception as exc:
            logger.error("风切变拟合失败: %s", exc)

    return {
        "basic_stats": basic_stats,
        "weibull_results": weibull_results,
        "wind_rose_data": wind_rose_data,
        "extreme_wind_results": extreme_wind_results,
        "representative_year_results": rep_year_results,
        "turbulence_data": turbulence_data,
        "wpd_results": wpd_results,
        "shear_result": shear_result,
    }
