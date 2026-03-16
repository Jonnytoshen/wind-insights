from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import config

app = FastAPI(
    title="Wind Insights API",
    version="1.0.0",
    description="NASA POWER proxy & wind resource analysis engine",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global exception handlers
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "内部服务器错误，请稍后重试", "code": "INTERNAL_ERROR"},
    )


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Routers — imported lazily to avoid circular imports
# ---------------------------------------------------------------------------
from app.routers import analysis, report  # noqa: E402

app.include_router(analysis.router)
app.include_router(report.router)
