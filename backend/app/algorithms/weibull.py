from __future__ import annotations

import numpy as np
from scipy.special import gamma
from scipy.optimize import minimize_scalar
from scipy.stats import weibull_min


def fit_weibull(wind_speeds: np.ndarray) -> tuple[float, float]:
    """
    Fit a 2-parameter Weibull distribution to wind speed data using MLE.

    Parameters
    ----------
    wind_speeds : array of positive wind speeds (m/s). Values ≤ 0 are filtered out.

    Returns
    -------
    (k, c) : shape parameter k and scale parameter c (m/s)

    Raises
    ------
    ValueError if there are fewer than 10 valid data points.
    """
    data = wind_speeds[wind_speeds > 0]
    if len(data) < 10:
        raise ValueError(f"有效风速样本量不足，需 ≥10 个，当前: {len(data)}")

    # scipy weibull_min: shape=k, scale=c, loc fixed at 0
    k, _loc, c = weibull_min.fit(data, floc=0)
    return float(k), float(c)


def weibull_pdf(v: np.ndarray, k: float, c: float) -> np.ndarray:
    """Weibull PDF evaluated at v."""
    return (k / c) * (v / c) ** (k - 1) * np.exp(-((v / c) ** k))


def build_histogram(
    wind_speeds: np.ndarray,
    bin_width: float = 1.0,
    max_speed: float = 30.0,
) -> tuple[list[float], list[float]]:
    """
    Build a wind speed frequency histogram (as percentages).

    Returns
    -------
    (bins, frequencies) : bin center values and percentage frequencies
    """
    edges = np.arange(0, max_speed + bin_width, bin_width)
    counts, _ = np.histogram(wind_speeds[wind_speeds >= 0], bins=edges)
    total = counts.sum()
    frequencies = (counts / total * 100).tolist() if total > 0 else [0.0] * len(counts)
    bins = ((edges[:-1] + edges[1:]) / 2).tolist()
    return bins, frequencies


def compute_fitted_pdf(
    bins: list[float],
    k: float,
    c: float,
    bin_width: float = 1.0,
) -> list[float]:
    """Compute Weibull PDF at bin centers, scaled to percentage frequency."""
    v = np.array(bins)
    pdf = weibull_pdf(v, k, c)
    return (pdf * bin_width * 100).tolist()
