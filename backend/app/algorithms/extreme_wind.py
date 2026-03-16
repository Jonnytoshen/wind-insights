from __future__ import annotations

import numpy as np
from scipy.stats import gumbel_r


def compute_extreme_wind(
    annual_max_series: np.ndarray,
    years: list[int],
    return_periods: tuple[int, ...] = (50, 100),
) -> dict:
    """
    Fit a Gumbel Type I (GEV) distribution to annual maximum wind speeds
    and compute extreme wind speeds for given return periods.

    Parameters
    ----------
    annual_max_series : 1-D array of annual maximum wind speeds (m/s)
    years             : corresponding year labels
    return_periods    : return period(s) in years (default 50, 100)

    Returns
    -------
    dict with keys: v50, v100, sample_years, annual_max_years, annual_max_values

    Raises
    ------
    ValueError if sample size < 10.
    """
    n = len(annual_max_series)
    if n < 10:
        raise ValueError(
            f"极端风速分析需要至少 10 年数据，当前仅有 {n} 年，"
            "结果将不具备统计可靠性。"
        )

    # Gumbel Type I: F(x) = exp(-exp(-(x-mu)/beta))
    loc, scale = gumbel_r.fit(annual_max_series)

    result: dict = {
        "sample_years": n,
        "annual_max_years": [int(y) for y in years],
        "annual_max_values": annual_max_series.tolist(),
    }

    for T in return_periods:
        # Quantile: x_T = loc - scale * ln(-ln(1 - 1/T))
        vt = float(gumbel_r.ppf(1 - 1 / T, loc=loc, scale=scale))
        result[f"v{T}"] = round(vt, 2)

    return result
