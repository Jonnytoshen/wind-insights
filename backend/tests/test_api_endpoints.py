from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# /api/analysis/start
# ---------------------------------------------------------------------------

VALID_PAYLOAD = {
    "lat": 40.0,
    "lon": 110.0,
    "heights": [100],
    "start_year": 2015,
    "end_year": 2020,
    "wind_surface": "vegtype_1",
    "project_name": "测试项目",
    "filter_outliers": True,
}


class TestStartAnalysis:
    def test_valid_request_returns_202(self):
        with patch("app.routers.analysis._run_analysis_task", new=AsyncMock()):
            resp = client.post("/api/analysis/start", json=VALID_PAYLOAD)
        assert resp.status_code == 202
        data = resp.json()
        assert "task_id" in data

    def test_lat_out_of_range_returns_422(self):
        payload = {**VALID_PAYLOAD, "lat": 95.0}
        resp = client.post("/api/analysis/start", json=payload)
        assert resp.status_code == 422

    def test_lon_out_of_range_returns_422(self):
        payload = {**VALID_PAYLOAD, "lon": 200.0}
        resp = client.post("/api/analysis/start", json=payload)
        assert resp.status_code == 422

    def test_invalid_wind_surface_returns_422(self):
        payload = {**VALID_PAYLOAD, "wind_surface": "invalid_surface"}
        resp = client.post("/api/analysis/start", json=payload)
        assert resp.status_code == 422

    def test_height_out_of_range_returns_422(self):
        payload = {**VALID_PAYLOAD, "heights": [5]}
        resp = client.post("/api/analysis/start", json=payload)
        assert resp.status_code == 422

    def test_end_year_before_start_year_returns_422(self):
        payload = {**VALID_PAYLOAD, "start_year": 2020, "end_year": 2015}
        resp = client.post("/api/analysis/start", json=payload)
        assert resp.status_code == 422

    def test_extra_fields_rejected_422(self):
        payload = {**VALID_PAYLOAD, "injected_field": "malicious"}
        resp = client.post("/api/analysis/start", json=payload)
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# /api/analysis/{task_id}/result
# ---------------------------------------------------------------------------

class TestGetResult:
    def _create_task(self) -> str:
        from app.core.task_manager import task_manager
        task = task_manager.create_task()
        return task.task_id

    def test_nonexistent_task_returns_404(self):
        resp = client.get("/api/analysis/nonexistent-task-id/result")
        assert resp.status_code == 404

    def test_pending_task_returns_409(self):
        task_id = self._create_task()
        resp = client.get(f"/api/analysis/{task_id}/result")
        assert resp.status_code == 409

    def test_success_task_returns_result(self):
        from app.core.task_manager import task_manager
        task = task_manager.create_task()
        task_manager.update_task(task.task_id, status="success", result={"task_id": task.task_id})
        resp = client.get(f"/api/analysis/{task.task_id}/result")
        assert resp.status_code == 200
        assert resp.json()["task_id"] == task.task_id

    def test_error_task_returns_500(self):
        from app.core.task_manager import task_manager
        task = task_manager.create_task()
        task_manager.update_task(task.task_id, status="error", message="模拟错误")
        resp = client.get(f"/api/analysis/{task.task_id}/result")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# /api/report/generate
# ---------------------------------------------------------------------------

class TestGenerateReport:
    def test_nonexistent_task_returns_404(self):
        payload = {
            "task_id": "nonexistent-task-id",
            "project_name": "测试",
            "project_address": "",
            "report_date": "2026-03-16",
            "organization": "",
            "confidentiality": "内部",
            "chart_images": {},
        }
        resp = client.post("/api/report/generate", json=payload)
        assert resp.status_code == 404

    def test_invalid_task_id_format_returns_422(self):
        payload = {
            "task_id": "../../etc/passwd",
            "project_name": "",
            "project_address": "",
            "report_date": "",
            "organization": "",
            "confidentiality": "内部",
            "chart_images": {},
        }
        resp = client.post("/api/report/generate", json=payload)
        assert resp.status_code == 422
