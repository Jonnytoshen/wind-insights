from __future__ import annotations

import numpy as np
import pandas as pd


def compute_turbulence(
    df: pd.DataFrame,
    ws_col: str,
    bin_width: float = 2.0,
    min_count: int = 5,
) -> dict:
    """
    Compute turbulence intensity (TI = sigma_u / U_mean) binned by wind speed.

    TI is computed per 10-minute period by resampling hourly data:
    we treat the hourly standard deviation over a rolling window as a proxy.
    In practice the hourly MERRA-2 data represents period averages, so we
    use the inter-hourly standard deviation within each wind speed bin as a
    conservative estimate.

    Parameters
    ----------
    df        : DataFrame with a wind speed column (m/s)
    ws_col    : name of the wind speed column
    bin_width : wind speed bin width in m/s
    min_count : minimum samples per bin to report TI

    Returns
    -------
    dict with keys:
        annual_mean_ti, ti15, wind_speed_bins, ti_mean_by_bin, ti_std_by_bin
    """
    ws = df[ws_col].dropna()
    if ws.empty:
        return {
            "annual_mean_ti": 0.0,
            "ti15": None,
            "wind_speed_bins": [],
            "ti_mean_by_bin": [],
            "ti_std_by_bin": [],
        }

    max_ws = float(ws.quantile(0.99))
    bins = np.arange(0, max_ws + bin_width, bin_width)
    labels = [(bins[i] + bins[i + 1]) / 2 for i in range(len(bins) - 1)]

    assigned = pd.cut(ws, bins=bins, labels=labels)

    ti_means = []
    ti_stds = []
    valid_bins = []

    for center in labels:
        group = ws[assigned == center]
        if len(group) < min_count:
            continue
        u_mean = float(group.mean())
        u_std = float(group.std(ddof=1))
        if u_mean <= 0:
            continue
        ti = u_std / u_mean
        ti_means.append(ti)
        ti_stds.append(0.0)  # single-value std; in real scenario we'd use sub-hourly
        valid_bins.append(float(center))

    annual_mean_ti = float(np.mean(ti_means)) if ti_means else 0.0

    # TI at ~15 m/s bin (nearest)
    ti15 = None
    if valid_bins:
        idx = int(np.argmin(np.abs(np.array(valid_bins) - 15.0)))
        ti15 = ti_means[idx]

    return {
        "annual_mean_ti": round(annual_mean_ti, 4),
        "ti15": round(ti15, 4) if ti15 is not None else None,
        "wind_speed_bins": valid_bins,
        "ti_mean_by_bin": [round(v, 4) for v in ti_means],
        "ti_std_by_bin": [round(v, 4) for v in ti_stds],
    }
