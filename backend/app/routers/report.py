from __future__ import annotations

import asyncio
import logging
import urllib.parse
from functools import partial

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.task_manager import task_manager
from app.models.request import ReportRequest
from app.services.pdf_generator import generate_pdf, PdfGenerationError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/report", tags=["report"])


@router.post("/generate")
async def generate_report(req: ReportRequest):
    task = task_manager.get_task(req.task_id)
    if task is None or task.result is None:
        raise HTTPException(status_code=404, detail="任务不存在或结果已过期")
    if task.status != "success":
        raise HTTPException(status_code=409, detail="任务尚未完成")

    try:
        # Run WeasyPrint in a thread-pool executor to avoid blocking the
        # async event loop (CJK font loading can take 30-60 s on cold start).
        loop = asyncio.get_event_loop()
        fn = partial(
            generate_pdf,
            analysis_result=task.result,
            report_config={
                "project_name": req.project_name,
                "project_address": req.project_address,
                "report_date": req.report_date,
                "organization": req.organization,
                "confidentiality": req.confidentiality,
            },
            chart_images=req.chart_images,
        )
        pdf_bytes = await loop.run_in_executor(None, fn)
    except PdfGenerationError as exc:
        logger.error("PDF 生成失败 task=%s: %s", req.task_id, exc)
        raise HTTPException(status_code=500, detail=f"PDF 生成失败: {exc}")

    project = req.project_name or "wind-insights"
    filename = urllib.parse.quote(f"{project}-风资源分析报告.pdf")

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename}",
            "Content-Length": str(len(pdf_bytes)),
        },
    )
