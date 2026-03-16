from __future__ import annotations

import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse

from app.config import TASK_TIMEOUT_SECONDS
from app.core.cache import analysis_cache
from app.core.task_manager import task_manager
from app.core.validators import build_cache_key, snap_to_merra2_grid
from app.models.request import AnalysisRequest
from app.models.response import StartAnalysisResponse
from app.services.nasa_power import fetch_wind_data, NASAPowerError
from app.services.analysis_engine import run_full_analysis

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analysis", tags=["analysis"])


async def _run_analysis_task(task_id: str, req: AnalysisRequest) -> None:
    """Background task: fetch data, run algorithms, store result."""
    import time

    task_manager.update_task(task_id, status="running", progress=5, message="开始获取风速数据...")

    try:
        # Check cache first
        cache_key = build_cache_key(req.lat, req.lon, req.heights, req.start_year, req.end_year, req.wind_surface)
        cached = analysis_cache.get(*cache_key)
        if cached is not None:
            task_manager.update_task(
                task_id, status="success", progress=100, message="分析完成（缓存命中）", result=cached
            )
            return

        def fetch_progress(done: int, total: int, msg: str) -> None:
            pct = 5 + int(done / total * 50)
            task_manager.update_task(task_id, progress=pct, message=msg, current_step="数据获取")

        raw_data = await fetch_wind_data(
            lat=req.lat,
            lon=req.lon,
            heights=req.heights,
            start_year=req.start_year,
            end_year=req.end_year,
            wind_surface=req.wind_surface,
            progress_callback=fetch_progress,
        )

        task_manager.update_task(task_id, progress=60, message="正在运行风资源分析算法...", current_step="算法计算")

        def algo_progress(step: int, total: int, msg: str) -> None:
            pct = 60 + int(step / total * 35)
            task_manager.update_task(task_id, progress=pct, message=msg, current_step="算法计算")

        analysis_output = run_full_analysis(
            raw_data=raw_data,
            heights=req.heights,
            filter_outliers=req.filter_outliers,
            progress=algo_progress,
        )

        grid_lat, grid_lon = snap_to_merra2_grid(req.lat, req.lon)
        result = {
            "task_id": task_id,
            "analysis_heights": req.heights,
            "location": {
                "lat": req.lat,
                "lng": req.lon,
                "grid_lat": grid_lat,
                "grid_lng": grid_lon,
            },
            "params": {
                "start_year": req.start_year,
                "end_year": req.end_year,
                "wind_surface": req.wind_surface,
                "project_name": req.project_name,
            },
            **analysis_output,
        }

        analysis_cache.set(result, *cache_key)
        task_manager.update_task(
            task_id, status="success", progress=100, message="分析完成", result=result
        )

    except NASAPowerError as exc:
        logger.error("NASA API 失败 task=%s: %s", task_id, exc)
        task_manager.update_task(task_id, status="error", message=str(exc))
    except Exception as exc:
        logger.exception("分析任务异常 task=%s", task_id)
        task_manager.update_task(task_id, status="error", message=f"内部错误: {type(exc).__name__}")


@router.post("/start", response_model=StartAnalysisResponse, status_code=202)
async def start_analysis(req: AnalysisRequest, background_tasks: BackgroundTasks):
    task = task_manager.create_task()
    background_tasks.add_task(_run_analysis_task, task.task_id, req)
    return StartAnalysisResponse(task_id=task.task_id)


@router.get("/{task_id}/progress")
async def stream_progress(task_id: str):
    task = task_manager.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")

    async def event_generator() -> AsyncGenerator[str, None]:
        yield f"data: {json.dumps(task.to_progress_dict())}\n\n"
        while True:
            try:
                msg = await asyncio.wait_for(task.queue.get(), timeout=15.0)
                yield f"data: {json.dumps(msg)}\n\n"
                if msg.get("status") in ("success", "error"):
                    break
            except asyncio.TimeoutError:
                yield ": heartbeat\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.get("/{task_id}/result")
async def get_result(task_id: str):
    task = task_manager.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    if task.status in ("pending", "running"):
        raise HTTPException(status_code=409, detail="任务仍在进行中，请稍后再试")
    if task.status == "error":
        raise HTTPException(status_code=500, detail=task.message)
    if task.result is None:
        raise HTTPException(status_code=500, detail="任务结果为空")
    return task.result
