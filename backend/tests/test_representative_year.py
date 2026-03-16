from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app.algorithms.representative_year import select_representative_year


def _make_multiyear_df(start_year: int = 2010, n_years: int = 10, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    periods = n_years * 8760
    index = pd.date_range(f"{start_year}-01-01", periods=periods, freq="h")
    ws = rng.weibull(2.0, periods) * 8.0 + 0.5
    return pd.DataFrame({"ws_100m": ws}, index=index)


class TestSelectRepresentativeYear:
    def test_rep_year_in_data_range(self):
        df = _make_multiyear_df(2010, 10)
        result = select_representative_year(df, "ws_100m")
        years = df.index.year.unique().tolist()
        assert result["representative_year"] in years

    def test_output_keys(self):
        df = _make_multiyear_df(2010, 5)
        result = select_representative_year(df, "ws_100m")
        assert "representative_year" in result
        assert "bias_from_long_term" in result
        assert "long_term_monthly_mean" in result
        assert "rep_year_monthly_mean" in result

    def test_monthly_arrays_length_12(self):
        df = _make_multiyear_df(2010, 5)
        result = select_representative_year(df, "ws_100m")
        assert len(result["long_term_monthly_mean"]) == 12
        assert len(result["rep_year_monthly_mean"]) == 12

    def test_single_year_still_works(self):
        df = _make_multiyear_df(2015, 1)
        result = select_representative_year(df, "ws_100m")
        assert result["representative_year"] == 2015

    def test_empty_series_raises(self):
        df = pd.DataFrame({"ws_100m": pd.Series([], dtype=float)})
        with pytest.raises(ValueError):
            select_representative_year(df, "ws_100m")

    def test_bias_close_to_zero_for_stable_data(self):
        """When all years have identical wind, bias should be ~0."""
        index = pd.date_range("2010-01-01", periods=5 * 8760, freq="h")
        ws = np.full(len(index), 7.0)
        df = pd.DataFrame({"ws_100m": ws}, index=index)
        result = select_representative_year(df, "ws_100m")
        assert abs(result["bias_from_long_term"]) < 0.01
