from __future__ import annotations

import os


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ORIGINS: list[str] = os.environ.get(
    "CORS_ORIGINS", "http://localhost,http://localhost:5173"
).split(",")

# ---------------------------------------------------------------------------
# Task management
# ---------------------------------------------------------------------------
TASK_TIMEOUT_SECONDS: int = int(os.environ.get("TASK_TIMEOUT_SECONDS", "300"))

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------
CACHE_TTL_SECONDS: int = int(os.environ.get("CACHE_TTL_SECONDS", "1800"))

# ---------------------------------------------------------------------------
# NASA POWER API
# ---------------------------------------------------------------------------
NASA_POWER_BASE_URL: str = "https://power.larc.nasa.gov/api/temporal/hourly/point"
NASA_MAX_CONNECTIONS: int = 10
NASA_MAX_KEEPALIVE: int = 5
NASA_RETRY_MAX: int = 3
