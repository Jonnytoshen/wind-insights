from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ProgressResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    status: str  # "pending" | "running" | "success" | "error"
    progress: int  # 0–100
    message: str = ""
    current_step: str = ""


class HistogramData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bins: list[float]
    frequencies: list[float]


class WeibullResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    k: float
    c: float
    histogram: HistogramData
    fitted_pdf: list[float]


class WindRoseData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    directions: list[str]
    frequency: list[float]
    speed_bin_freqs: list[list[float]]


class ExtremeWindResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    v50: float
    v100: float
    sample_years: int
    annual_max_years: list[int]
    annual_max_values: list[float]


class RepresentativeYearResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    representative_year: int
    bias_from_long_term: float
    long_term_monthly_mean: list[float]
    rep_year_monthly_mean: list[float]


class BasicStats(BaseModel):
    model_config = ConfigDict(extra="forbid")

    annual_mean_ws: float
    data_valid_rate: float
    outlier_count: int
    monthly_mean_timestamps: list[str]
    monthly_mean_values: list[float]
    dominant_direction: str


class TurbulenceData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    annual_mean_ti: float
    ti15: float | None
    wind_speed_bins: list[float]
    ti_mean_by_bin: list[float]
    ti_std_by_bin: list[float]


class ShearResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alpha: float
    r2: float
    heights: list[int]
    mean_speeds: list[float]
    fitted_speeds: list[float]


class WpdResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    annual_wpd: float
    monthly_wpd: list[float]


class AnalysisResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    analysis_heights: list[int]
    location: dict[str, float]
    params: dict
    basic_stats: dict[str, BasicStats]
    weibull_results: dict[str, WeibullResult]
    wind_rose_data: dict[str, WindRoseData]
    extreme_wind_results: dict[str, ExtremeWindResult]
    representative_year_results: dict[str, RepresentativeYearResult]
    turbulence_data: dict[str, TurbulenceData]
    shear_result: ShearResult | None
    wpd_results: dict[str, WpdResult]


class StartAnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    message: str = "分析任务已启动"


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    detail: str
    code: str
