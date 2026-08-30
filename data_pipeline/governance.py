"""SIFT Data Governance, PII Detection & Leakage Prevention.

Provides automated scanning for personally identifiable information (PII),
governance compliance verification, label leakage checks, and post-event feature isolation.
"""

from enum import Enum
import re
from typing import Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field


class PIIStatus(str, Enum):
    """PII compliance status for a dataset record."""
    CLEAN = "CLEAN"
    FLAGGED = "FLAGGED"
    REDACTED = "REDACTED"


class PIIMatch(BaseModel):
    """Details of a single detected PII element."""
    pii_type: str = Field(..., description="Type of PII (EMAIL, PHONE, EMPLOYEE_ID, IP_ADDRESS, NAME)")
    matched_text: str = Field(..., description="The sensitive text snippet detected")
    start_offset: int = Field(..., description="Character start offset in scanned text")
    end_offset: int = Field(..., description="Character end offset in scanned text")
    replacement: str = Field(..., description="Standardized redaction placeholder")


class PIIResult(BaseModel):
    """Result of PII inspection on a text narrative."""
    status: PIIStatus = Field(default=PIIStatus.CLEAN)
    flags: List[PIIMatch] = Field(default_factory=list)
    sanitized_text: str = Field(..., description="Text with PII redacted if redaction was applied")
    is_clean: bool = Field(default=True)


class GovernanceReport(BaseModel):
    """Record-level governance and leakage audit report."""
    record_id: str
    pii_status: PIIStatus
    pii_matches_count: int
    pii_types_detected: List[str] = Field(default_factory=list)
    label_leakage_detected: bool = Field(default=False)
    leakage_reasons: List[str] = Field(default_factory=list)
    passed_governance: bool = Field(default=True)


class PIIDetector:
    """Configurable, rule-based PII detector tailored for industrial HSE safety reports."""
    
    # Pre-compiled regular expressions
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
    
    # Indian & international phone formats: e.g. +91 94350 12841, 09435012841, +91-94350-12841, 0374-2800123
    PHONE_PATTERN = re.compile(
        r'(?:\+91[\s-]?)?(?:\(?\d{2,5}\)?[\s-]?)?\d{5,10}\b'
    )
    
    # Employee / User / Contractor IDs: USR-001, EMP-12345, OIL-8921, CONT-441
    EMPLOYEE_ID_PATTERN = re.compile(
        r'\b(?:USR|EMP|OIL|CONT|STAFF|BADGE)[-_]?\d{3,7}\b',
        re.IGNORECASE
    )
    
    # IPv4 Addresses
    IP_PATTERN = re.compile(
        r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    )
    
    # Honorific Personal Names: e.g. "Mr. Sharma", "Shri Bhaben Saikia", "Er. Devajit Neog", "Dr. Phukan"
    HONORIFIC_NAME_PATTERN = re.compile(
        r'\b(?:Mr\.|Mrs\.|Ms\.|Shri|Smt\.|Er\.|Dr\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b'
    )

    def __init__(
        self,
        custom_employee_ids: Optional[Set[str]] = None,
        custom_names: Optional[Set[str]] = None,
    ):
        self.custom_employee_ids = custom_employee_ids or set()
        self.custom_names = custom_names or set()

    def scan(self, text: str, redact: bool = False) -> PIIResult:
        """Scan text for sensitive PII and optionally redact matches.
        
        Args:
            text: Input safety narrative text.
            redact: If True, replaces sensitive spans with placeholders.
            
        Returns:
            PIIResult with status, detected matches, and sanitized text.
        """
        if not text:
            return PIIResult(status=PIIStatus.CLEAN, flags=[], sanitized_text="", is_clean=True)
            
        matches: List[PIIMatch] = []
        
        # 1. Emails
        for m in self.EMAIL_PATTERN.finditer(text):
            matches.append(PIIMatch(
                pii_type="EMAIL",
                matched_text=m.group(0),
                start_offset=m.start(),
                end_offset=m.end(),
                replacement="[EMAIL_REDACTED]"
            ))
            
        # 2. Employee IDs
        for m in self.EMPLOYEE_ID_PATTERN.finditer(text):
            matches.append(PIIMatch(
                pii_type="EMPLOYEE_ID",
                matched_text=m.group(0),
                start_offset=m.start(),
                end_offset=m.end(),
                replacement="[ID_REDACTED]"
            ))
            
        # 3. Known custom employee IDs
        for emp_id in self.custom_employee_ids:
            pos = 0
            while True:
                idx = text.find(emp_id, pos)
                if idx == -1:
                    break
                # Check not already captured
                if not any(m.start_offset == idx and m.end_offset == idx + len(emp_id) for m in matches):
                    matches.append(PIIMatch(
                        pii_type="EMPLOYEE_ID",
                        matched_text=emp_id,
                        start_offset=idx,
                        end_offset=idx + len(emp_id),
                        replacement="[ID_REDACTED]"
                    ))
                pos = idx + len(emp_id)

        # 4. Known custom names
        for name in self.custom_names:
            pos = 0
            while True:
                idx = text.find(name, pos)
                if idx == -1:
                    break
                if not any(m.start_offset == idx and m.end_offset == idx + len(name) for m in matches):
                    matches.append(PIIMatch(
                        pii_type="NAME",
                        matched_text=name,
                        start_offset=idx,
                        end_offset=idx + len(name),
                        replacement="[NAME_REDACTED]"
                    ))
                pos = idx + len(name)

        # 5. Honorific Names
        for m in self.HONORIFIC_NAME_PATTERN.finditer(text):
            matches.append(PIIMatch(
                pii_type="NAME",
                matched_text=m.group(0),
                start_offset=m.start(),
                end_offset=m.end(),
                replacement="[NAME_REDACTED]"
            ))

        # 6. IPv4 Addresses
        for m in self.IP_PATTERN.finditer(text):
            matches.append(PIIMatch(
                pii_type="IP_ADDRESS",
                matched_text=m.group(0),
                start_offset=m.start(),
                end_offset=m.end(),
                replacement="[IP_REDACTED]"
            ))

        # 7. Phone Numbers (filter out false positives like pressures "35 bar", measurements "120 mm", years "2026")
        for m in self.PHONE_PATTERN.finditer(text):
            val = m.group(0).strip()
            # Require at least 7 digits to avoid short numerical values
            digits = re.sub(r'\D', '', val)
            if len(digits) >= 8:
                # Ensure it wasn't already covered by an employee ID or IP match
                if not any(m.start() >= match.start_offset and m.end() <= match.end_offset for match in matches):
                    matches.append(PIIMatch(
                        pii_type="PHONE",
                        matched_text=val,
                        start_offset=m.start(),
                        end_offset=m.end(),
                        replacement="[PHONE_REDACTED]"
                    ))

        # Sort matches by start_offset descending to allow clean in-place replacement
        matches.sort(key=lambda x: x.start_offset, reverse=True)

        # Build sanitized text if redaction is requested
        sanitized = text
        if redact and matches:
            for match in matches:
                sanitized = sanitized[:match.start_offset] + match.replacement + sanitized[match.end_offset:]
            status = PIIStatus.REDACTED
        elif matches:
            status = PIIStatus.FLAGGED
        else:
            status = PIIStatus.CLEAN

        # Sort matches back to ascending order for presentation
        matches.sort(key=lambda x: x.start_offset)
        
        return PIIResult(
            status=status,
            flags=matches,
            sanitized_text=sanitized,
            is_clean=len(matches) == 0,
        )


class GovernanceChecker:
    """Audits safety dataset records for governance compliance, label leakage, and post-event isolation."""

    LEAKAGE_TARGET_LABELS = {
        "CRITICAL SIF",
        "HIGH SIF",
        "MEDIUM SIF",
        "LOW SIF",
        "NON-SIF",
        "SIF POTENTIAL: CRITICAL",
        "SIF POTENTIAL: HIGH",
        "FINAL CLASSIFICATION",
        "REVIEWER NOTES:",
        "ADJUDICATION NOTES:",
    }

    def __init__(self, pii_detector: Optional[PIIDetector] = None):
        self.pii_detector = pii_detector or PIIDetector()

    def audit_record(
        self,
        record_id: str,
        raw_text: str,
        context_dict: Optional[Dict[str, any]] = None,
    ) -> GovernanceReport:
        """Audit a record for PII and input feature label leakage.
        
        Args:
            record_id: Unique record ID.
            raw_text: Input narrative text.
            context_dict: Dictionary of context fields.
            
        Returns:
            GovernanceReport detailing compliance and leakage flags.
        """
        pii_res = self.pii_detector.scan(raw_text, redact=False)
        
        leakage_detected = False
        leakage_reasons: List[str] = []
        
        # Check raw text for explicit target label leakage strings
        upper_text = raw_text.upper()
        for label_indicator in self.LEAKAGE_TARGET_LABELS:
            if label_indicator in upper_text:
                leakage_detected = True
                leakage_reasons.append(
                    f"Narrative contains prospective target label indicator: '{label_indicator}'"
                )
                
        # Check context fields for post-event leakage
        if context_dict:
            for k, v in context_dict.items():
                k_lower = k.lower()
                if any(bad in k_lower for bad in ["reviewer", "adjudicat", "final_sif", "ai_sif", "investigation_findings"]):
                    leakage_detected = True
                    leakage_reasons.append(
                        f"Context container includes post-event or target label field: '{k}'"
                    )

        passed = pii_res.is_clean and not leakage_detected
        
        detected_types = list({m.pii_type for m in pii_res.flags})
        
        return GovernanceReport(
            record_id=record_id,
            pii_status=pii_res.status,
            pii_matches_count=len(pii_res.flags),
            pii_types_detected=detected_types,
            label_leakage_detected=leakage_detected,
            leakage_reasons=leakage_reasons,
            passed_governance=passed,
        )
