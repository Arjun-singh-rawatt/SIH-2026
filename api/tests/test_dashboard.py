"""Executive dashboard analytics tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_overview(client: AsyncClient):
    # Ingest a sample report
    await client.post(
        "/api/v1/reports",
        json={
            "reporter_id": "USR-001",
            "facility_id": "FAC-DUL-01",
            "location": "Header Area",
            "raw_report_text": "Valve was unbolted while line was still pressurized with 35 bar natural gas.",
            "report_type": "Near Miss",
            "activity": "Maintenance",
        },
    )

    res = await client.get("/api/v1/dashboard/overview")
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    assert data["summary"]["total_reports"] >= 1
    assert "sif_reports" in data["summary"]
    assert "sif_density" in data["summary"]
    assert "trend" in data
    assert "facility_ranking" in data
    assert "activity_ranking" in data
    assert "barrier_failures" in data
