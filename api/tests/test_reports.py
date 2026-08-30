"""Safety Reports CRUD and filtering tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_get_report(client: AsyncClient):
    payload = {
        "reporter_id": "USR-001",
        "facility_id": "FAC-DUL-01",
        "location": "Header Manifold #3",
        "raw_report_text": "Technician removed discharge valve under 35 bar pressure without positive LOTO isolation.",
        "report_type": "Near Miss",
        "activity": "Maintenance",
    }
    create_res = await client.post("/api/v1/reports", json=payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["report_id"].startswith("SIF-")
    assert created_data["sif_potential"] in ["HIGH", "CRITICAL"]
    assert created_data["life_saving_rule"] == "Energy Isolation"
    assert created_data["review_status"] == "PENDING"
    assert len(created_data["barrier_assessments"]) >= 1

    # Fetch report by report_id
    rep_id = created_data["report_id"]
    get_res = await client.get(f"/api/v1/reports/{rep_id}")
    assert get_res.status_code == 200
    assert get_res.json()["report_id"] == rep_id


@pytest.mark.asyncio
async def test_list_and_filter_reports(client: AsyncClient):
    # Create 2 reports
    await client.post(
        "/api/v1/reports",
        json={
            "reporter_id": "USR-001",
            "facility_id": "FAC-DUL-01",
            "location": "Vessel V-101",
            "raw_report_text": "Confined space entry into vessel without multi-gas test; 40 ppm H2S detected.",
            "report_type": "Unsafe Act",
            "activity": "Vessel Cleaning",
        },
    )
    await client.post(
        "/api/v1/reports",
        json={
            "reporter_id": "USR-001",
            "facility_id": "FAC-DUL-01",
            "location": "Rig NHK-42",
            "raw_report_text": "Auxiliary wire rope snapped under 3.2 ton load; roughnecks were in line of fire.",
            "report_type": "Near Miss",
            "activity": "Drilling",
        },
    )

    # Filter by report_type
    res = await client.get("/api/v1/reports?report_type=Unsafe Act")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert all(r["report_type"] == "Unsafe Act" for r in data["items"])

    # Search
    search_res = await client.get("/api/v1/reports?search=snapped")
    assert search_res.status_code == 200
    assert search_res.json()["total"] >= 1
