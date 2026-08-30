"""Pattern Intelligence & Semantic Similarity tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_patterns_and_similarity(client: AsyncClient):
    # Ingest multiple sample observations
    await client.post(
        "/api/v1/reports",
        json={
            "reporter_id": "USR-001",
            "facility_id": "FAC-DUL-01",
            "location": "Compressor Skid",
            "raw_report_text": "Pressure gauge needle vibrating; valve removed under 35 bar pressure without isolation.",
            "report_type": "Near Miss",
            "activity": "Maintenance",
        },
    )
    await client.post(
        "/api/v1/reports",
        json={
            "reporter_id": "USR-001",
            "facility_id": "FAC-DUL-01",
            "location": "Compressor Manifold #2",
            "raw_report_text": "Flange loosened while line was still pressurized with 30 bar gas without LOTO verification.",
            "report_type": "Near Miss",
            "activity": "Maintenance",
        },
    )

    # 1. List patterns
    pats_res = await client.get("/api/v1/intelligence/patterns")
    assert pats_res.status_code == 200
    patterns = pats_res.json()
    assert len(patterns) >= 1
    assert any("Energy Isolation" in p["category"] for p in patterns)

    # 2. Get pattern KPIs
    kpi_res = await client.get("/api/v1/intelligence/overview")
    assert kpi_res.status_code == 200
    assert kpi_res.json()["total_patterns"] >= 1

    # 3. Query similar reports
    sim_res = await client.post(
        "/api/v1/intelligence/similar-reports",
        json={"query_text": "Unbolting valve on pressurized 35 bar gas line without isolation"},
    )
    assert sim_res.status_code == 200
    assert sim_res.json()["total_matches"] >= 1
