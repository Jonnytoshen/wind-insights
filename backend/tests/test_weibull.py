from __future__ import annotations

import numpy as np
import pytest

from app.algorithms.weibull import (
    fit_weibull,
    build_histogram,
    compute_fitted_pdf,
)


def _synthetic_weibull(k: float, c: float, n: int = 5000, seed: int = 0) -> np.ndarray:
    """Generate samples from a Weibull distribution (scipy convention)."""
    from scipy.stats import weibull_min
    rng = np.random.default_rng(seed)
    return weibull_min.rvs(k, scale=c, size=n, random_state=rng)


class TestFitWeibull:
    def test_known_parameters_within_5_percent(self):
        true_k, true_c = 2.0, 8.0
        data = _synthetic_weibull(true_k, true_c, n=10_000)
        k, c = fit_weibull(data)
        assert abs(k - true_k) / true_k < 0.05, f"k偏差过大: {k}"
        assert abs(c - true_c) / true_c < 0.05, f"c偏差过大: {c}"

    def test_all_zeros_raises(self):
        data = np.zeros(100)
        with pytest.raises(ValueError, match="有效风速"):
            fit_weibull(data)

    def test_negative_values_filtered(self):
        data = _synthetic_weibull(2.0, 7.0, n=500)
        data_with_neg = np.concatenate([data, [-1.0, -5.0]])
        k, c = fit_weibull(data_with_neg)
        assert 1.0 < k < 4.0
        assert 3.0 < c < 12.0

    def test_too_few_samples_raises(self):
        with pytest.raises(ValueError):
            fit_weibull(np.array([1.0, 2.0, 3.0]))

    def test_returns_positive_parameters(self):
        data = _synthetic_weibull(1.5, 6.0, n=200)
        k, c = fit_weibull(data)
        assert k > 0
        assert c > 0


class TestBuildHistogram:
    def test_frequencies_sum_to_100(self):
        data = _synthetic_weibull(2.0, 8.0, n=2000)
        bins, freqs = build_histogram(data)
        assert abs(sum(freqs) - 100.0) < 1.0  # allow rounding

    def test_bins_and_freqs_same_length(self):
        data = _synthetic_weibull(2.0, 8.0, n=500)
        bins, freqs = build_histogram(data)
        assert len(bins) == len(freqs)

    def test_empty_array(self):
        bins, freqs = build_histogram(np.array([]))
        assert all(f == 0.0 for f in freqs)


class TestFittedPdf:
    def test_pdf_nonnegative(self):
        data = _synthetic_weibull(2.0, 8.0, n=1000)
        bins, freqs = build_histogram(data)
        k, c = fit_weibull(data)
        fitted = compute_fitted_pdf(bins, k, c)
        assert all(v >= 0 for v in fitted)

    def test_pdf_same_length_as_bins(self):
        data = _synthetic_weibull(2.0, 8.0, n=1000)
        bins, freqs = build_histogram(data)
        k, c = fit_weibull(data)
        fitted = compute_fitted_pdf(bins, k, c)
        assert len(fitted) == len(bins)
