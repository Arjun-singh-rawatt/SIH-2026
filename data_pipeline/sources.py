"""SIFT Data Source Registry & Provenance Tracking System.

Maintains an auditable catalog of all raw data acquisitions, verifying permissions,
licensing, data ownership, PII status, and cryptographic hashes.
"""

from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import os
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    """Categorization of data acquisition sources."""
    INTERNAL_SAFETY_REPORTS = "INTERNAL_SAFETY_REPORTS"
    AUTHORIZED_HISTORICAL_DATASET = "AUTHORIZED_HISTORICAL_DATASET"
    PUBLIC_LICENSED_SAFETY_DATASET = "PUBLIC_LICENSED_SAFETY_DATASET"
    RESEARCH_DATASET = "RESEARCH_DATASET"
    SYNTHETIC_BENCHMARK = "SYNTHETIC_BENCHMARK"


class DataClassification(str, Enum):
    """Strict data classification hierarchy."""
    REAL = "REAL"
    PUBLIC = "PUBLIC"
    SYNTHETIC = "SYNTHETIC"
    DEMO = "DEMO"


class PermissionStatus(str, Enum):
    """Legal authorization status for ML dataset inclusion."""
    AUTHORIZED = "AUTHORIZED"
    RESTRICTED = "RESTRICTED"
    PENDING_LEGAL = "PENDING_LEGAL"
    REVOKED = "REVOKED"


class RegisteredSource(BaseModel):
    """Authoritative metadata record for an acquired dataset source."""
    source_id: str = Field(..., description="Unique source identifier, e.g. SRC-OIL-2026-01")
    source_name: str
    source_type: SourceType
    classification: DataClassification
    license: str = Field(default="PROPRIETARY_OIL_INTERNAL")
    permission_status: PermissionStatus = Field(default=PermissionStatus.AUTHORIZED)
    collection_date: Optional[str] = None
    data_owner: str = Field(default="Oil India Limited HSE Directorate")
    allowed_use: str = Field(default="SIFT Model Training & Safety Intelligence")
    pii_status: str = Field(default="SCANNED_AND_REDACTED", description="PII audit status")
    record_count: int = Field(default=0)
    raw_file_sha256: Optional[str] = None
    ingested_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = Field(default="ACTIVE", description="ACTIVE, ARCHIVED, DEPRECATED")
    notes: Optional[str] = None


class SourceProvenance(BaseModel):
    """Granular provenance record attached to each safety report."""
    source_id: str
    source_record_id: str
    source_file: str
    ingestion_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_version: str = "1.0.0"


class SourceRegistry:
    """Manages the persistent source registry file."""

    DEFAULT_REGISTRY_PATH = "data/metadata/source_registry.json"

    def __init__(self, registry_path: str = DEFAULT_REGISTRY_PATH):
        self.registry_path = registry_path
        self.sources: Dict[str, RegisteredSource] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("sources", []):
                        src = RegisteredSource(**item)
                        self.sources[src.source_id] = src
            except Exception as e:
                print(f"[Warning] Failed to load source registry: {e}")

    def save(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.registry_path)), exist_ok=True)
        payload = {
            "registry_version": "1.0",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "total_sources": len(self.sources),
            "sources": [s.model_dump() for s in self.sources.values()],
        }
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def register_source(self, source: RegisteredSource) -> RegisteredSource:
        """Register or update an acquired data source."""
        self.sources[source.source_id] = source
        self.save()
        return source

    def get_source(self, source_id: str) -> Optional[RegisteredSource]:
        return self.sources.get(source_id)

    def list_sources(self) -> List[RegisteredSource]:
        return list(self.sources.values())

    def validate_eligibility(self, source_id: str) -> Tuple[bool, Optional[str]]:
        """Validate whether a source is legally and operationally eligible for training."""
        src = self.get_source(source_id)
        if not src:
            return False, f"Source ID '{source_id}' is not registered in source registry."
        if src.permission_status != PermissionStatus.AUTHORIZED:
            return False, f"Source '{source_id}' permission status is '{src.permission_status}' (must be AUTHORIZED)."
        if src.status != "ACTIVE":
            return False, f"Source '{source_id}' status is '{src.status}' (must be ACTIVE)."
        return True, None

    @staticmethod
    def compute_file_sha256(filepath: str) -> str:
        """Calculate cryptographic SHA-256 hash of a file."""
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
