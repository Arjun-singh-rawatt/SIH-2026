"""CAPA Action Items CRUD tests."""

from datetime import datetime, timezone, timedelta
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_action_lifecycle(client: AsyncClient):
    # 1. Create a report
    rep_res = await client.post(
        "/api/v1/reports",
        json={
            "reporter_id": "USR-001",
            "facility_id": "FAC-DUL-01",
            "location": "Header Area",
            "raw_report_text": "Valve was unbolted under pressure without isolation.",
            "report_type": "Near Miss",
            "activity": "Maintenance",
        },
    )
    rep_id = rep_res.json()["report_id"]

    # 2. Create action item
    due_date = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    create_act_res = await client.post(
        "/api/v1/actions",
        json={
            "report_id": rep_id,
            "assigned_to": "USR-001",
            "facility_id": "FAC-DUL-01",
            "action_type": "LOTO Audit",
            "description": "Execute positive zero energy audit.",
            "priority": "CRITICAL",
            "due_date": due_date,
        },
    )
    assert create_act_res.status_code == 201
    act_data = create_act_res.json()
    act_id = act_data["action_id"]
    assert act_data["status"] == "Open"
    assert act_data["report_id"] == rep_id

    # 3. Update status to Completed
    patch_res = await client.patch(
        f"/api/v1/actions/{act_id}",
        json={"status": "Completed"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "Completed"
    assert patch_res.json()["completed_at"] is not None

    # 4. Check action stats
    stats_res = await client.get("/api/v1/actions/stats")
    assert stats_res.status_code == 200
    assert stats_res.json()["completed"] >= 1
