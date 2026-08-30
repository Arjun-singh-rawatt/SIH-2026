"""Tests for SIFT PII Detection, Governance Compliance, and Label Leakage Prevention."""

from data_pipeline.governance import PIIDetector, GovernanceChecker, PIIStatus


def test_pii_detector_flags_email_and_phone():
    """Verify detection of emails, employee IDs, and phone numbers in safety text."""
    detector = PIIDetector()
    text = "Report filed by USR-004 (rituraj.gogoi@oilindia.in) after contacting safety desk at +91 94355 67120."
    
    res = detector.scan(text, redact=False)
    assert res.is_clean is False
    assert res.status == PIIStatus.FLAGGED
    
    pii_types = {m.pii_type for m in res.flags}
    assert "EMAIL" in pii_types
    assert "EMPLOYEE_ID" in pii_types
    assert "PHONE" in pii_types


def test_pii_detector_redaction():
    """Verify that redaction masks replace sensitive tokens while preserving report structure."""
    detector = PIIDetector()
    text = "Operator USR-002 noticed oil leak. Email priyanka.barua@oilindia.in for details."
    
    res = detector.scan(text, redact=True)
    assert res.status == PIIStatus.REDACTED
    assert "[ID_REDACTED]" in res.sanitized_text
    assert "[EMAIL_REDACTED]" in res.sanitized_text
    assert "USR-002" not in res.sanitized_text
    assert "priyanka.barua@oilindia.in" not in res.sanitized_text


def test_governance_checker_flags_label_leakage():
    """Verify that prospective target label strings in narrative trigger leakage alerts."""
    checker = GovernanceChecker()
    leaked_narrative = "The investigation concluded: SIF POTENTIAL: CRITICAL due to unisolated gas line."
    
    rep = checker.audit_record("REC-001", leaked_narrative, context_dict={"activity": "Maintenance"})
    assert rep.label_leakage_detected is True
    assert rep.passed_governance is False
    assert len(rep.leakage_reasons) > 0


def test_governance_checker_flags_post_event_context_leakage():
    """Verify that post-incident investigation fields in context container trigger governance failure."""
    checker = GovernanceChecker()
    clean_text = "Flange bolts unbolted without isolation certificate."
    leaked_context = {"activity": "Maintenance", "reviewer_notes": "Adjudicated as critical"}
    
    rep = checker.audit_record("REC-002", clean_text, context_dict=leaked_context)
    assert rep.label_leakage_detected is True
    assert rep.passed_governance is False
