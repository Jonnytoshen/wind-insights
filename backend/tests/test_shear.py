from __future__ import annotations

import pytest

from app.algorithms.shear import fit_power_law_shear


class TestFitPowerLawShear:
    def test_known_alpha_recovered(self):
        """Given synthetic power-law data, alpha should be recovered closely."""
        alpha_true = 0.2
        h_ref = 80.0
        v_ref = 7.0
        heights = [40, 60, 80, 100, 120, 140]
        speeds = [round(v_ref * (h / h_ref) ** alpha_true, 4) for h in heights]
        result = fit_power_law_shear(heights, speeds)
        assert abs(result["alpha"] - alpha_true) < 0.005
        assert result["r2"] > 0.999

    def test_alpha_in_reasonable_range(self):
        heights = [50, 80, 100, 120]
        speeds = [6.5, 7.0, 7.3, 7.6]
        result = fit_power_law_shear(heights, speeds)
        assert 0.01 <= result["alpha"] <= 1.0

    def test_fitted_speeds_correct_count(self):
        heights = [50, 100]
        speeds = [6.0, 7.0]
        result = fit_power_law_shear(heights, speeds)
        assert len(result["fitted_speeds"]) == 2

    def test_single_height_raises(self):
        with pytest.raises(ValueError, match="2 个高度"):
            fit_power_law_shear([100], [7.0])

    def test_all_zero_speeds_raises(self):
        with pytest.raises(ValueError):
            fit_power_law_shear([50, 100], [0.0, 0.0])

    def test_output_keys(self):
        result = fit_power_law_shear([80, 100], [7.0, 7.4])
        assert set(result.keys()) == {"alpha", "r2", "heights", "mean_speeds", "fitted_speeds"}
