# ---- single stage ----
FROM python:3.12-slim

WORKDIR /app

# WeasyPrint system dependencies + CJK fonts
# libgdk-pixbuf2.0-0 was renamed to libgdk-pixbuf-xlib-2.0-0 in Debian trixie
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-xlib-2.0-0 \
    libffi-dev \
    fonts-noto-cjk \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv --no-cache-dir

# Install Python dependencies into .venv
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
