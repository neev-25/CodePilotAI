# ── Stage 1: deps ────────────────────────────────────────────────────────────
FROM python:3.12-slim AS deps

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    gosu \
    && rm -rf /var/lib/apt/lists/* \
    # Create a non-root system user for security
    && adduser --system --no-create-home --group appuser

COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

COPY . .
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Volumes for persistent data (database, indexing state, cloned repos)
VOLUME ["/app/index_state", "/app/repositories"]

EXPOSE 8000

# Health check — Docker marks container unhealthy if /health returns non-200
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD-SHELL curl -f "http://localhost:${PORT:-8000}/health" || exit 1

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

CMD ["uvicorn", "main:app"]
