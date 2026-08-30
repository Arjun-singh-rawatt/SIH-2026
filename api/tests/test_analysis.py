"""AI Analysis endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analyze_energy_isolation(client: AsyncClient):
    payload = {
        "report_text": "Technician loosened bolts on 35 bar compressor manifold without proper isolation or LOTO.",
        "report_type": "Near Miss",
        "facility_id": "FAC-DUL-01",
        "location": "Compressor Manifold",
        "activity": "Maintenance",
    }
    response = await client.post("/api/v1/reports/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sif_potential"] in ["HIGH", "CRITICAL"]
    assert data["precursor_category"] == "Energy Isolation"
    assert data["life_saving_rule"] == "Energy Isolation"
    assert "isolation" in data["evidence_phrase"].lower()
    assert data["confidence"] > 90.0
    assert data["urgency_score"] >= 85


@pytest.mark.asyncio
async def test_analyze_confined_space(client: AsyncClient):
    payload = {
        "report_text": "Cleaners entered separator V-102 manway without atmospheric gas testing; rim monitor alarmed at 42 ppm H2S.",
        "report_type": "Unsafe Act",
        "facility_id": "FAC-DUL-01",
    }
    response = await client.post("/api/v1/reports/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sif_potential"] == "CRITICAL"
    assert data["precursor_category"] == "Confined Space"
    assert data["life_saving_rule"] == "Confined Space Entry"
    assert data["urgency_score"] >= 95


@pytest.mark.asyncio
async def test_analyze_invalid_empty_text(client: AsyncClient):
    payload = {
        "report_text": "   ",
    }
    response = await client.post("/api/v1/reports/analyze", json=payload)
    assert response.status_code == 422 or response.status_code == 400
