"""Human-in-the-loop review workflow tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_review_queue_and_preserve_ai_predictions(client: AsyncClient):
    # 1. Create a report
    create_res = await client.post(
        "/api/v1/reports",
        json={
            "reporter_id": "USR-001",
            "facility_id": "FAC-DUL-01",
            "location": "Header Area",
            "raw_report_text": "Valve was unbolted while line was still pressurized with natural gas without isolation.",
            "report_type": "Near Miss",
            "activity": "Maintenance",
        },
    )
    rep_id = create_res.json()["report_id"]
    original_ai_sif = create_res.json()["ai_sif_potential"]

    # 2. Check in review queue
    queue_res = await client.get("/api/v1/reviews/queue?tab=PENDING")
    assert queue_res.status_code == 200
    assert any(r["report_id"] == rep_id for r in queue_res.json()["items"])

    # 3. Human modifier reclassifies to MEDIUM with notes
    review_res = await client.post(
        f"/api/v1/reports/{rep_id}/review",
        json={
            "action": "MODIFY",
            "reviewer_id": "USR-001",
            "reviewer_notes": "Reclassified after verifying downstream secondary check valve was active.",
            "final_sif_potential": "MEDIUM",
            "final_life_saving_rule": "Energy Isolation",
        },
    )
    assert review_res.status_code == 200
    rev_data = review_res.json()

    # Verify AI prediction is intact
    assert rev_data["ai_sif_potential"] == original_ai_sif
    # Verify Human final is set
    assert rev_data["final_sif_potential"] == "MEDIUM"
    assert rev_data["sif_potential"] == "MEDIUM"
    assert rev_data["review_status"] == "MODIFIED"
    assert rev_data["reviewer_notes"] is not None
