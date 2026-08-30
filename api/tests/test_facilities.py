"""Facilities endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_facilities_and_stats(client: AsyncClient):
    res = await client.get("/api/v1/facilities")
    assert res.status_code == 200
    facilities = res.json()
    assert len(facilities) >= 1
    fac_id = facilities[0]["facility_id"]

    # Check facility stats
    stats_res = await client.get(f"/api/v1/facilities/{fac_id}/stats")
    assert stats_res.status_code == 200
    stats_data = stats_res.json()
    assert stats_data["facility_id"] == fac_id
    assert "sif_density" in stats_data
    assert "high_urgency_count" in stats_data
    assert "top_precursor" in stats_data
