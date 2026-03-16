from __future__ import annotations

import numpy as np
import pandas as pd


def select_representative_year(
    df: pd.DataFrame,
    ws_col: str,
) -> dict:
    """
    Select the most representative year: the year whose 12 monthly mean wind
    speeds are closest (L2 distance) to the long-term monthly mean.

    Parameters
    ----------
    df     : DataFrame with DatetimeIndex and a wind speed column
    ws_col : name of the wind speed column

    Returns
    -------
    dict with keys:
        representative_year, bias_from_long_term,
        long_term_monthly_mean, rep_year_monthly_mean
    """
    ws = df[ws_col].dropna()
    if ws.empty:
        raise ValueError("风速数据为空，无法计算代表年")

    years = sorted(ws.index.year.unique())
    if len(years) < 1:
        raise ValueError("数据不足 1 年")

    monthly_group = ws.groupby([ws.index.year, ws.index.month]).mean()

    # Long-term monthly mean (all years)
    lt_monthly = ws.groupby(ws.index.month).mean()
    lt_arr = lt_monthly.reindex(range(1, 13)).values  # shape (12,)

    best_year: int = years[0]
    best_dist = float("inf")
    year_monthly_means: dict[int, np.ndarray] = {}

    for y in years:
        yr_data = [monthly_group.get((y, m), np.nan) for m in range(1, 13)]
        yr_arr = np.array(yr_data, dtype=float)
        year_monthly_means[y] = yr_arr
        # Use only months where both lt and year data are available
        valid = ~np.isnan(yr_arr) & ~np.isnan(lt_arr)
        if valid.sum() < 6:
            continue
        dist = float(np.sqrt(np.sum((yr_arr[valid] - lt_arr[valid]) ** 2)))
        if dist < best_dist:
            best_dist = dist
            best_year = y

    rep_arr = year_monthly_means[best_year]
    annual_lt_mean = float(np.nanmean(lt_arr))
    annual_rep_mean = float(np.nanmean(rep_arr))
    bias = round(annual_rep_mean - annual_lt_mean, 4)

    return {
        "representative_year": int(best_year),
        "bias_from_long_term": bias,
        "long_term_monthly_mean": [
            round(float(v), 4) if not np.isnan(v) else None for v in lt_arr
        ],
        "rep_year_monthly_mean": [
            round(float(v), 4) if not np.isnan(v) else None for v in rep_arr
        ],
    }
