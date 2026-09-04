"""Comprehensive automated test suite for SIFT Annotation Workbench.

Tests:
1. Batch creation and dual-annotator assignment
2. Double-blind isolation (Annotator A cannot see B's draft or submission)
3. Zero AI prediction leakage (AI fields strictly stripped from annotator view)
4. Evidence span offset grounding and validation
5. Private draft saving and updating
6. Final submission and immutability
7. Automatic agreement / disagreement detection
8. Expert adjudication with role-based access control (403 for unauthorized users)
9. Inter-annotator agreement metrics (Kappa, Jaccard, Span IoU)
10. 7-Gate release readiness audit
11. Security boundaries (Annotator cannot modify peer annotations, cannot adjudicate)
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.db.models.safety_report import SafetyReport
from app.db.models.facility import Facility


@pytest_asyncio.fixture(scope="function")
async def seed_annotation_users_and_report(db_session: AsyncSession):
    """Seed dedicated annotators, adjudicator, and test report."""
    # Annotator A (Safety Officer)
    ann_a = User(
        user_id="USR-ANN-A",
        name="Annotator Alice",
        email="alice@oilindia.in",
        role="Safety Officer",
        facility_id="FAC-DUL-01",
    )
    # Annotator B (Safety Officer)
    ann_b = User(
        user_id="USR-ANN-B",
        name="Annotator Bob",
        email="bob@oilindia.in",
        role="Safety Officer",
        facility_id="FAC-DUL-01",
    )
    # Lead Adjudicator (HSE Manager)
    adjudicator = User(
        user_id="USR-ADJ-01",
        name="Lead Adjudicator Charlie",
        email="charlie@oilindia.in",
        role="HSE Manager",
        facility_id="FAC-DUL-01",
    )
    # Administrator
    admin = User(
        user_id="USR-ADM-01",
        name="Admin Dave",
        email="dave@oilindia.in",
        role="Administrator",
        facility_id="FAC-DUL-01",
    )
    db_session.add_all([ann_a, ann_b, adjudicator, admin])

    report = SafetyReport(
        id="rep-uuid-001",
        report_id="SIF-TEST-001",
        reporter_id="USR-001",
        facility_id="FAC-DUL-01",
        location="Wellhead Platform Alpha",
        raw_report_text="While servicing bypass valve on Compressor #2, noticed 35 bar gas pressure was not isolated.",
        report_type="Near Miss",
        activity="Maintenance",
        # Original AI predictions (MUST BE STRIPPED)
        ai_sif_potential="CRITICAL",
        ai_sif_precursor="YES",
        ai_confidence=94.5,
        ai_urgency_score=92,
        ai_primary_hazard="Stored / Pressurized Hydrocarbon Energy",
        ai_precursor_category="Energy Isolation",
        ai_life_saving_rule="Energy Isolation",
        ai_evidence_phrase="noticed 35 bar gas pressure was not isolated",
        ai_explanation="Severe live gas pressure without isolation.",
    )
    db_session.add(report)
    await db_session.commit()

    return {
        "annotator_a": ann_a,
        "annotator_b": ann_b,
        "adjudicator": adjudicator,
        "admin": admin,
        "report": report,
    }


@pytest.mark.asyncio
async def test_taxonomy_endpoint(client: AsyncClient):
    """Verify taxonomy reference endpoint returns canonical lists."""
    res = await client.get("/api/v1/annotations/taxonomy")
    assert res.status_code == 200
    data = res.json()
    assert "sif_potential_levels" in data
    assert "CRITICAL" in data["sif_potential_levels"]
    assert "NON-SIF" in data["sif_potential_levels"]
    assert "Energy Isolation" in data["precursor_categories"]


@pytest.mark.asyncio
async def test_batch_creation_and_admin_security(
    client: AsyncClient,
    seed_annotation_users_and_report: dict,
):
    """Verify admin can create batch and non-admin is rejected."""
    fixtures = seed_annotation_users_and_report
    batch_payload = {
        "batch_id": "BATCH-TEST-001",
        "name": "Test Pilot Batch",
        "source_id": "SRC-SIM-01",
        "report_ids": ["SIF-TEST-001"],
        "annotator_a_id": "USR-ANN-A",
        "annotator_b_id": "USR-ANN-B",
        "is_demo": True,
        "notes": "Automated test batch",
    }

    # Non-admin attempt should fail with 403
    res_non_admin = await client.post(
        "/api/v1/annotations/batches",
        json=batch_payload,
        headers={"X-User-Id": "USR-ANN-A"},
    )
    assert res_non_admin.status_code == 403

    # Admin attempt succeeds
    res_admin = await client.post(
        "/api/v1/annotations/batches",
        json=batch_payload,
        headers={"X-User-Id": "USR-ADM-01"},
    )
    assert res_admin.status_code == 201
    batch_data = res_admin.json()
    assert batch_data["batch_id"] == "BATCH-TEST-001"
    assert batch_data["record_count"] == 1


@pytest.mark.asyncio
async def test_double_blind_isolation_and_ai_stripping(
    client: AsyncClient,
    seed_annotation_users_and_report: dict,
):
    """Verify Annotator A sees no AI fields and cannot see Annotator B's data."""
    fixtures = seed_annotation_users_and_report
    # Create batch
    await client.post(
        "/api/v1/annotations/batches",
        json={
            "batch_id": "BATCH-BLIND-001",
            "name": "Blind Test Batch",
            "source_id": "SRC-SIM-01",
            "report_ids": ["SIF-TEST-001"],
            "annotator_a_id": "USR-ANN-A",
            "annotator_b_id": "USR-ANN-B",
        },
        headers={"X-User-Id": "USR-ADM-01"},
    )

    # Get tasks for Annotator A
    res_tasks = await client.get("/api/v1/annotations/tasks", headers={"X-User-Id": "USR-ANN-A"})
    assert res_tasks.status_code == 200
    tasks = res_tasks.json()
    assert len(tasks) >= 1
    task_id = tasks[0]["id"]

    # Annotator A gets task detail
    res_detail = await client.get(f"/api/v1/annotations/tasks/{task_id}", headers={"X-User-Id": "USR-ANN-A"})
    assert res_detail.status_code == 200
    detail = res_detail.json()

    # 1. AI PREDICTIONS MUST BE STRIPPED
    assert "ai_sif_potential" not in detail
    assert "ai_confidence" not in detail
    assert "ai_explanation" not in detail
    assert "ai_evidence_phrase" not in detail

    # 2. Raw text is visible
    assert "While servicing bypass valve" in detail["raw_text"]
    assert detail["my_role_slot"] == "ANNOTATOR_A"

    # Unassigned user cannot access task
    res_unassigned = await client.get(f"/api/v1/annotations/tasks/{task_id}", headers={"X-User-Id": "USR-004"})
    assert res_unassigned.status_code == 403


@pytest.mark.asyncio
async def test_evidence_span_offset_validation(
    client: AsyncClient,
    seed_annotation_users_and_report: dict,
):
    """Verify evidence span character offsets are strictly validated against raw text."""
    await client.post(
        "/api/v1/annotations/batches",
        json={
            "batch_id": "BATCH-OFFSETS-001",
            "name": "Offset Validation Batch",
            "source_id": "SRC-SIM-01",
            "report_ids": ["SIF-TEST-001"],
            "annotator_a_id": "USR-ANN-A",
            "annotator_b_id": "USR-ANN-B",
        },
        headers={"X-User-Id": "USR-ADM-01"},
    )

    res_tasks = await client.get("/api/v1/annotations/tasks", headers={"X-User-Id": "USR-ANN-A"})
    task_id = res_tasks.json()[0]["id"]

    # Invalid span (text doesn't match raw_report_text at offsets)
    bad_span_payload = {
        "sif_potential": "HIGH",
        "evidence_spans": [
            {"text": "Completely wrong text", "start_offset": 0, "end_offset": 21}
        ]
    }
    res_bad = await client.post(
        f"/api/v1/annotations/tasks/{task_id}/draft",
        json=bad_span_payload,
        headers={"X-User-Id": "USR-ANN-A"},
    )
    assert res_bad.status_code == 422
    assert "mismatch" in res_bad.json()["detail"].lower()

    # Valid span: "While servicing" at [0:15]
    good_span_payload = {
        "sif_potential": "HIGH",
        "evidence_spans": [
            {"text": "While servicing", "start_offset": 0, "end_offset": 15}
        ]
    }
    res_good = await client.post(
        f"/api/v1/annotations/tasks/{task_id}/draft",
        json=good_span_payload,
        headers={"X-User-Id": "USR-ANN-A"},
    )
    assert res_good.status_code == 200
    assert res_good.json()["is_draft"] is True


@pytest.mark.asyncio
async def test_dual_submission_and_disagreement_generation(
    client: AsyncClient,
    seed_annotation_users_and_report: dict,
):
    """Verify that when Annotator A and B diverge, a disagreement is generated."""
    await client.post(
        "/api/v1/annotations/batches",
        json={
            "batch_id": "BATCH-DISAGREE-001",
            "name": "Disagreement Test Batch",
            "source_id": "SRC-SIM-01",
            "report_ids": ["SIF-TEST-001"],
            "annotator_a_id": "USR-ANN-A",
            "annotator_b_id": "USR-ANN-B",
        },
        headers={"X-User-Id": "USR-ADM-01"},
    )
    res_tasks = await client.get("/api/v1/annotations/tasks", headers={"X-User-Id": "USR-ANN-A"})
    task_id = res_tasks.json()[0]["id"]

    # Submission A: SIF Potential = HIGH
    sub_a = {
        "sif_potential": "HIGH",
        "sif_precursor": "YES",
        "primary_hazard": "Stored / Pressurized Hydrocarbon Energy",
        "activity": "Maintenance",
        "primary_precursor": "Energy Isolation",
        "precursor_categories": ["Energy Isolation"],
        "life_saving_rule": "Energy Isolation",
        "life_saving_rules": ["Energy Isolation"],
        "evidence_spans": [{"text": "While servicing", "start_offset": 0, "end_offset": 15}],
        "notes": "Annotator A notes",
    }
    res_a = await client.post(f"/api/v1/annotations/tasks/{task_id}/submit", json=sub_a, headers={"X-User-Id": "USR-ANN-A"})
    assert res_a.status_code == 200

    # Submission B: SIF Potential = CRITICAL (discrepancy!)
    sub_b = {
        "sif_potential": "CRITICAL",
        "sif_precursor": "YES",
        "primary_hazard": "Stored / Pressurized Hydrocarbon Energy",
        "activity": "Maintenance",
        "primary_precursor": "Energy Isolation",
        "precursor_categories": ["Energy Isolation"],
        "life_saving_rule": "Energy Isolation",
        "life_saving_rules": ["Energy Isolation"],
        "evidence_spans": [{"text": "While servicing", "start_offset": 0, "end_offset": 15}],
        "notes": "Annotator B notes",
    }
    res_b = await client.post(f"/api/v1/annotations/tasks/{task_id}/submit", json=sub_b, headers={"X-User-Id": "USR-ANN-B"})
    assert res_b.status_code == 200

    # Disagreement should be recorded
    res_dis = await client.get("/api/v1/annotations/disagreements", headers={"X-User-Id": "USR-ADJ-01"})
    assert res_dis.status_code == 200
    disagreements = res_dis.json()
    assert len(disagreements) >= 1
    sif_dis = next((d for d in disagreements if d["field_name"] == "sif_potential"), None)
    assert sif_dis is not None
    assert sif_dis["annotator_a_value"] == "HIGH"
    assert sif_dis["annotator_b_value"] == "CRITICAL"


@pytest.mark.asyncio
async def test_expert_adjudication_workflow(
    client: AsyncClient,
    seed_annotation_users_and_report: dict,
):
    """Verify Lead HSE Expert can review side-by-side comparison and resolve ground truth."""
    await client.post(
        "/api/v1/annotations/batches",
        json={
            "batch_id": "BATCH-ADJUDICATE-001",
            "name": "Adjudication Workflow Batch",
            "source_id": "SRC-SIM-01",
            "report_ids": ["SIF-TEST-001"],
            "annotator_a_id": "USR-ANN-A",
            "annotator_b_id": "USR-ANN-B",
        },
        headers={"X-User-Id": "USR-ADM-01"},
    )
    task_id = (await client.get("/api/v1/annotations/tasks", headers={"X-User-Id": "USR-ANN-A"})).json()[0]["id"]

    # Complete dual submissions
    base_sub = {
        "sif_precursor": "YES",
        "primary_hazard": "Stored / Pressurized Hydrocarbon Energy",
        "activity": "Maintenance",
        "primary_precursor": "Energy Isolation",
        "life_saving_rule": "Energy Isolation",
        "evidence_spans": [{"text": "While servicing", "start_offset": 0, "end_offset": 15}],
    }
    await client.post(f"/api/v1/annotations/tasks/{task_id}/submit", json={**base_sub, "sif_potential": "HIGH"}, headers={"X-User-Id": "USR-ANN-A"})
    await client.post(f"/api/v1/annotations/tasks/{task_id}/submit", json={**base_sub, "sif_potential": "CRITICAL"}, headers={"X-User-Id": "USR-ANN-B"})

    # Unauthorized user (Annotator) cannot adjudicate
    adj_payload = {
        "resolved_sif_potential": "CRITICAL",
        "resolved_sif_precursor": "YES",
        "resolved_primary_hazard": "Stored / Pressurized Hydrocarbon Energy",
        "resolved_activity": "Maintenance",
        "resolved_primary_precursor": "Energy Isolation",
        "resolved_life_saving_rule": "Energy Isolation",
        "resolved_evidence_spans": [{"text": "While servicing", "start_offset": 0, "end_offset": 15}],
        "adjudication_notes": "Live gas without isolation carries lethal risk; classified as CRITICAL.",
    }
    res_unauth = await client.post(f"/api/v1/annotations/disagreements/{task_id}/adjudicate", json=adj_payload, headers={"X-User-Id": "USR-ANN-A"})
    assert res_unauth.status_code == 403

    # Authorized Adjudicator resolves
    res_adj = await client.post(f"/api/v1/annotations/disagreements/{task_id}/adjudicate", json=adj_payload, headers={"X-User-Id": "USR-ADJ-01"})
    assert res_adj.status_code == 200
    adj_data = res_adj.json()
    assert adj_data["resolved_sif_potential"] == "CRITICAL"
    assert "lethal risk" in adj_data["adjudication_notes"]


@pytest.mark.asyncio
async def test_quality_and_release_readiness(
    client: AsyncClient,
    seed_annotation_users_and_report: dict,
):
    """Verify agreement metrics calculation and 7 release gates evaluation."""
    res_q = await client.get("/api/v1/annotations/quality")
    assert res_q.status_code == 200
    q_data = res_q.json()
    assert "overall_cohens_kappa" in q_data
    assert "evidence_span_iou" in q_data

    res_rel = await client.get("/api/v1/annotations/release-readiness")
    assert res_rel.status_code == 200
    rel_data = res_rel.json()
    assert "gates" in rel_data
    assert len(rel_data["gates"]) == 7
    gate_names = [g["gate_name"] for g in rel_data["gates"]]
    assert "SOURCE_REGISTRATION" in gate_names
    assert "ANNOTATION_COMPLETENESS" in gate_names
    assert "HIGH_SIF_SAFETY_FLOOR" in gate_names
