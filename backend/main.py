from collections import defaultdict, deque
from time import monotonic
from fastapi import FastAPI, HTTPException
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database.database import Base, engine, SessionLocal
from app.api.repository import router as repository_router
from app.api.auth import router as auth_router
from app.ai.llm import GeminiServiceError
from app.models.indexing_job import IndexingJob
from app.core.config import settings
import app.models.vector_embedding  # noqa: F401
import app.models.embedding_rate_reservation  # noqa: F401

PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/auth/login", "/auth/register", "/"}

if engine.dialect.name == "postgresql":
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

Base.metadata.create_all(bind=engine)

# redirect_slashes=False prevents FastAPI from 307-redirecting /repositories → /repositories/
# which strips the Authorization header on browsers.
app = FastAPI(title="CodePilot AI", redirect_slashes=False)
_requests: dict[str, deque[float]] = defaultdict(deque)


@app.exception_handler(GeminiServiceError)
async def gemini_error_handler(_: Request, error: GeminiServiceError):
    return JSONResponse(
        status_code=502,
        content={"detail": "The AI service could not complete this request. Please try again."},
    )

# -----------------------------
# CORS — must be added FIRST so it wraps everything
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_and_rate_limit(request: Request, call_next):
    """Small dependency-free protection layer for local and single-instance deployments."""
    # Normalize path for public-path check (strip trailing slash for consistency)
    path = request.url.path.rstrip("/") or "/"
    if path not in PUBLIC_PATHS:
        client = request.client.host if request.client else "unknown"
        now = monotonic()
        bucket = _requests[client]
        while bucket and now - bucket[0] >= 60:
            bucket.popleft()
        if len(bucket) >= settings.MAX_REQUESTS_PER_MINUTE:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Please try again shortly."})
        bucket.append(now)
        if settings.API_KEY and request.method not in {"GET", "HEAD", "OPTIONS"}:
            if request.headers.get("X-API-Key") != settings.API_KEY:
                return JSONResponse(status_code=401, content={"detail": "A valid API key is required."})
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self'"
    )
    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=(), camera=()"
    )
    return response

# -----------------------------
# Routes
# -----------------------------
app.include_router(repository_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {
        "message": "CodePilot AI Backend"
    }


@app.get("/health")
def health():
    """Deep health check — verifies DB connectivity."""
    db_status = "ok"
    http_status = 200
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception:
        db_status = "error"
        http_status = 503

    payload = {
        "status": "ok" if db_status == "ok" else "degraded",
        "db": db_status,
        "environment": settings.ENVIRONMENT,
    }
    return JSONResponse(content=payload, status_code=http_status)
