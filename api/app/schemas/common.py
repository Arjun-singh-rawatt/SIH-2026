"""Common response and error schemas."""

from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error description")
    details: Optional[Any] = Field(default=None, description="Optional diagnostic details")


class ErrorResponse(BaseModel):
    error: ErrorDetail


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    environment: str = "development"


class DatabaseHealthResponse(BaseModel):
    status: str = "ok"
    database: str = "connected"
    latency_ms: float = 0.0


class GenericSuccessResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
