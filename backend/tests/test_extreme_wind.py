from __future__ import annotations

import numpy as np
import pytest

from app.algorithms.extreme_wind import compute_extreme_wind


def _gumbel_samples(n: int = 20, seed: int = 42) -> tuple[np.ndarray, list[int]]:
    from scipy.stats import gumbel_r
    rng = np.random.default_rng(seed)
    samples = gumbel_r.rvs(loc=30.0, scale=5.0, size=n, random_state=rng)
    years = list(range(2000, 2000 + n))
    return samples, years


class TestComputeExtremeWind:
    def test_v50_lt_v100(self):
        samples, years = _gumbel_samples(20)
        result = compute_extreme_wind(samples, years)
        assert result["v50"] < result["v100"]

    def test_v50_reasonable_range(self):
        samples, years = _gumbel_samples(20)
        result = compute_extreme_wind(samples, years)
        # With loc=30, scale=5 the V50 should be roughly 30 + 5*ln(50) ≈ 50 m/s
        assert 30.0 < result["v50"] < 80.0

    def test_known_series_v50_accuracy(self):
        """Check that V50 is within 20% of analytical expectation."""
        from scipy.stats import gumbel_r
        loc, scale = 30.0, 5.0
        v50_expected = float(gumbel_r.ppf(1 - 1 / 50, loc=loc, scale=scale))
        samples, years = _gumbel_samples(30)
        result = compute_extreme_wind(samples, years)
        assert abs(result["v50"] - v50_expected) / v50_expected < 0.20

    def test_too_few_years_raises(self):
        samples = np.array([25.0, 28.0, 30.0, 27.0, 29.0])
        years = list(range(2000, 2005))
        with pytest.raises(ValueError, match="10 年"):
            compute_extreme_wind(samples, years)

    def test_output_keys(self):
        samples, years = _gumbel_samples(15)
        result = compute_extreme_wind(samples, years)
        assert "v50" in result
        assert "v100" in result
        assert "sample_years" in result
        assert result["sample_years"] == 15

    def test_annual_max_years_preserved(self):
        samples, years = _gumbel_samples(12)
        result = compute_extreme_wind(samples, years)
        assert result["annual_max_years"] == years
