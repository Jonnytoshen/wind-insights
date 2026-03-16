from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app.algorithms.turbulence import compute_turbulence


def _make_df(n: int = 8760, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    index = pd.date_range("2015-01-01", periods=n, freq="h")
    ws = rng.weibull(2.0, n) * 8.0 + 0.5  # strictly positive
    return pd.DataFrame({"ws_100m": ws}, index=index)


class TestComputeTurbulence:
    def test_returns_expected_keys(self):
        df = _make_df()
        result = compute_turbulence(df, "ws_100m")
        assert "annual_mean_ti" in result
        assert "ti15" in result
        assert "wind_speed_bins" in result
        assert "ti_mean_by_bin" in result
        assert "ti_std_by_bin" in result

    def test_bins_and_means_same_length(self):
        df = _make_df()
        result = compute_turbulence(df, "ws_100m")
        assert len(result["wind_speed_bins"]) == len(result["ti_mean_by_bin"])
        assert len(result["wind_speed_bins"]) == len(result["ti_std_by_bin"])

    def test_annual_mean_ti_positive(self):
        df = _make_df()
        result = compute_turbulence(df, "ws_100m")
        assert result["annual_mean_ti"] >= 0.0

    def test_ti_values_bounded(self):
        df = _make_df()
        result = compute_turbulence(df, "ws_100m")
        for ti in result["ti_mean_by_bin"]:
            assert 0.0 <= ti <= 1.0, f"TI 值超出范围: {ti}"

    def test_empty_dataframe_does_not_crash(self):
        df = pd.DataFrame({"ws_100m": pd.Series([], dtype=float)})
        result = compute_turbulence(df, "ws_100m")
        assert result["annual_mean_ti"] == 0.0
        assert result["wind_speed_bins"] == []

    def test_all_nan_does_not_crash(self):
        index = pd.date_range("2015-01-01", periods=100, freq="h")
        df = pd.DataFrame({"ws_100m": [float("nan")] * 100}, index=index)
        result = compute_turbulence(df, "ws_100m")
        assert result["annual_mean_ti"] == 0.0
