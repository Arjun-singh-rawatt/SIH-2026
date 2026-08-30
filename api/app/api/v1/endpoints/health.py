"""Health check endpoints."""

import time
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import get_db
from app.schemas.common import HealthResponse, DatabaseHealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="Service Health Check")
async def health_check() -> HealthResponse:
    """Returns basic liveness state of the SIFT FastAPI application."""
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
    )


@router.get("/health/db", response_model=DatabaseHealthResponse, summary="Database Connectivity Check")
async def database_health_check(db: AsyncSession = Depends(get_db)) -> DatabaseHealthResponse:
    """Verifies active connectivity and measures latency to the database engine."""
    start = time.perf_counter()
    await db.execute(text("SELECT 1"))
    latency = round((time.perf_counter() - start) * 1000, 2)

    return DatabaseHealthResponse(
        status="ok",
        database="connected",
        latency_ms=latency,
    )
