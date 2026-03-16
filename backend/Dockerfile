# ---- build stage ----
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv
RUN pip install uv --no-cache-dir

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

# ---- runtime stage ----
FROM python:3.12-slim

WORKDIR /app

# WeasyPrint system dependencies + CJK fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
