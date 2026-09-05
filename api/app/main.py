"""Main FastAPI Application Entrypoint for SIFT."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.errors import SIFTException
from app.db.base import Base
from app.db.session import engine
import app.db.models  # Register all models
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.api.v1.router import api_router
from app.api.v1.endpoints import health


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown event management."""
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.APP_ENV}]")

    # If using local SQLite, automatically create all tables on startup
    if "sqlite" in settings.DATABASE_URL:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Initialized local SQLite database schema.")

    # Initialize MongoDB Connection
    await connect_to_mongo()

    yield

    logger.info("Shutting down SIFT Backend.")
    await engine.dispose()
    await close_mongo_connection()


def create_application() -> FastAPI:
    """FastAPI Application Factory."""
    application = FastAPI(
        title=settings.APP_NAME,
        description=(
            "AI-Assisted Safety Intelligence & Fatality-Risk Tracking Backend for Oil India Limited (OIL). "
            "Analyzes Unsafe Acts, Unsafe Conditions, Near Misses, and Incident reports to classify SIF potential, "
            "map IOGP Life-Saving Rules, diagnose failed safety barriers, and prioritize CAPA actions."
        ),
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # 1. CORS Configuration
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Exception Handlers
    @application.exception_handler(SIFTException)
    async def sift_exception_handler(request: Request, exc: SIFTException):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "The request payload failed schema validation.",
                    "details": exc.errors(),
                }
            },
        )

    @application.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled server exception on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected server error occurred. Please contact the HSE platform administrator.",
                }
            },
        )

    # 3. Mount Routers
    application.include_router(health.router)
    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = create_application()
