from __future__ import annotations

import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

MAX_DATA_YEAR = datetime.date.today().year - 1  # NASA POWER data lags ~1 year


# NASA POWER wind-surface options (IGBP vegetation classification, types 1-18)
VALID_SURFACES = frozenset([
    "vegtype_1", "vegtype_2", "vegtype_3", "vegtype_4", "vegtype_5",
    "vegtype_6", "vegtype_7", "vegtype_8", "vegtype_9", "vegtype_10",
    "vegtype_11", "vegtype_12", "vegtype_13", "vegtype_14", "vegtype_15",
    "vegtype_16", "vegtype_17", "vegtype_18",
])


class AnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lat: float
    lon: float
    heights: list[int]
    start_year: int
    end_year: int
    wind_surface: str
    project_name: str = ""
    filter_outliers: bool = True

    @field_validator("lat")
    @classmethod
    def validate_lat(cls, v: float) -> float:
        if not (-90 <= v <= 90):
            raise ValueError("纬度必须在 -90 到 90 之间")
        return v

    @field_validator("lon")
    @classmethod
    def validate_lon(cls, v: float) -> float:
        if not (-180 <= v <= 180):
            raise ValueError("经度必须在 -180 到 180 之间")
        return v

    @field_validator("heights")
    @classmethod
    def validate_heights(cls, v: list[int]) -> list[int]:
        if not v:
            raise ValueError("至少选择一个分析高度")
        if len(v) > 5:
            raise ValueError("最多选择 5 个分析高度")
        for h in v:
            if not (10 <= h <= 300):
                raise ValueError(f"分析高度必须在 10–300 m 之间，当前值: {h}")
        return sorted(set(v))

    @field_validator("start_year")
    @classmethod
    def validate_start_year(cls, v: int) -> int:
        if not (1981 <= v <= MAX_DATA_YEAR):
            raise ValueError(f"起始年份必须在 1981–{MAX_DATA_YEAR} 之间")
        return v

    @field_validator("end_year")
    @classmethod
    def validate_end_year(cls, v: int) -> int:
        if not (1981 <= v <= MAX_DATA_YEAR):
            raise ValueError(f"结束年份必须在 1981–{MAX_DATA_YEAR} 之间")
        return v

    @field_validator("wind_surface")
    @classmethod
    def validate_wind_surface(cls, v: str) -> str:
        if v not in VALID_SURFACES:
            raise ValueError(f"无效的地表类型: {v}，允许值: {sorted(VALID_SURFACES)}")
        return v

    def model_post_init(self, __context: object) -> None:
        if self.end_year < self.start_year:
            raise ValueError("结束年份不能早于起始年份")
        years = self.end_year - self.start_year + 1
        if years < 1:
            raise ValueError("分析时段至少需要 1 年")


class ReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    project_name: str = ""
    project_address: str = ""
    report_date: str = ""
    organization: str = ""
    confidentiality: Literal["公开", "内部", "保密", "机密"] = "内部"
    chart_images: dict[str, str] = {}

    @field_validator("task_id")
    @classmethod
    def validate_task_id(cls, v: str) -> str:
        if not v or len(v) > 64:
            raise ValueError("task_id 无效")
        # 只允许字母、数字和连字符
        import re
        if not re.fullmatch(r"[a-zA-Z0-9\-]+", v):
            raise ValueError("task_id 只能包含字母、数字和连字符")
        return v
