from __future__ import annotations

import numpy as np


def fit_power_law_shear(
    heights: list[int],
    mean_speeds: list[float],
) -> dict:
    """
    Fit a wind shear power law: v(h) = v_ref * (h / h_ref) ^ alpha

    Uses log-linear regression: ln(v) = alpha * ln(h) + const

    Parameters
    ----------
    heights     : list of measurement heights in metres (≥2 heights required)
    mean_speeds : corresponding long-term mean wind speeds (m/s)

    Returns
    -------
    dict with keys: alpha, r2, heights, mean_speeds, fitted_speeds
    """
    if len(heights) < 2:
        raise ValueError("风切变分析至少需要 2 个高度的数据")

    h_arr = np.array(heights, dtype=float)
    v_arr = np.array(mean_speeds, dtype=float)

    # Filter zero/negative speeds
    valid = v_arr > 0
    if valid.sum() < 2:
        raise ValueError("有效（>0 m/s）高度数据不足 2 个，无法拟合风切变")

    ln_h = np.log(h_arr[valid])
    ln_v = np.log(v_arr[valid])

    # Least-squares: ln_v = alpha * ln_h + c
    A = np.vstack([ln_h, np.ones_like(ln_h)]).T
    result = np.linalg.lstsq(A, ln_v, rcond=None)
    alpha, c = result[0]

    # R²
    ln_v_pred = alpha * ln_h + c
    ss_res = float(np.sum((ln_v - ln_v_pred) ** 2))
    ss_tot = float(np.sum((ln_v - ln_v.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0

    # Fitted speeds at all heights (not just valid)
    fitted_speeds = (np.exp(c) * (h_arr ** alpha)).tolist()

    return {
        "alpha": round(float(alpha), 4),
        "r2": round(r2, 4),
        "heights": [int(h) for h in heights],
        "mean_speeds": [round(float(v), 4) for v in mean_speeds],
        "fitted_speeds": [round(float(v), 4) for v in fitted_speeds],
    }
