"""SIFT Root API Smoke Test.

Validates that the FastAPI application initializes correctly, all router routes
are registered, OpenAPI schema generates without error, and key endpoints exist.
"""

import pytest
from app.main import app


def test_openapi_schema_generation():
    """Verify OpenAPI 3.x schema generation succeeds without schema validation errors."""
    openapi_schema = app.openapi()
    assert "SIFT" in openapi_schema["info"]["title"]
    
    paths = openapi_schema["paths"]
    # Core health endpoints
    assert "/health" in paths
    assert "/health/db" in paths
    
    # Core domain endpoints
    assert "/api/v1/reports" in paths
    assert "/api/v1/dashboard/overview" in paths
    assert "/api/v1/facilities" in paths
    assert "/api/v1/actions" in paths
    assert "/api/v1/intelligence/overview" in paths
    assert "/api/v1/life-saving-rules" in paths
