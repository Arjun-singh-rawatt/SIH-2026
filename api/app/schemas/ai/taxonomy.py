"""SIFT AI & Data Taxonomy Definitions.

Canonical versioned taxonomy enumerations and validation structures
for dataset creation, annotation, and model inference contracts.
Taxonomy Version: 1.0
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class StrEnum(str, Enum):
    """String Enum for clean serialization and JSON schema generation."""
    def __str__(self) -> str:
        return self.value


# ------------------------------------------------------------------------------
# Core SIF Taxonomies (Version 1.0)
# ------------------------------------------------------------------------------

class SIFPotentialLevel(StrEnum):
    """Canonical SIF Potential Categories.
    
    Represents the potential for Serious Injury or Fatality (consequence severity),
    independent of actual injury outcome.
    """
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NON_SIF = "NON-SIF"


class SIFPrecursorFlag(StrEnum):
    """Canonical SIF Precursor Flag.
    
    Indicates whether a high-energy hazard was present in the absence of a direct,
    functioning safety barrier.
    """
    YES = "YES"
    NO = "NO"
    POTENTIAL = "POTENTIAL"


class PrecursorCategory(StrEnum):
    """Canonical SIF Precursor Categories (Version 1.0)."""
    ENERGY_ISOLATION = "Energy Isolation"
    CONFINED_SPACE = "Confined Space"
    LINE_OF_FIRE = "Line of Fire"
    WORKING_AT_HEIGHT = "Working at Height"
    HOT_WORK = "Hot Work"
    LIFTING_OPERATIONS = "Lifting Operations"
    DRIVING_SAFETY = "Driving & Journey Management"
    BYPASSING_SAFEGUARDS = "Bypassing Safety Controls"
    TOXIC_GAS_EXPOSURE = "Toxic Gas & Chemical Exposure"
    PROCESS_SAFETY = "Process Safety"
    PROCEDURAL_SAFETY = "Procedural Safety"
    OTHER = "Other"


class PrimaryHazardType(StrEnum):
    """Canonical Hazard Taxonomy (Version 1.0)."""
    STORED_HYDROCARBON_PRESSURE = "Stored / Pressurized Hydrocarbon Energy"
    TOXIC_GAS_H2S = "Toxic Gas / Asphyxiation (H2S & O2 Deficiency)"
    DROPPED_OBJECT = "Dropped Heavy Object / Line of Fire"
    FALL_FROM_HEIGHT = "Unprotected Fall from Elevated Height (>2m)"
    HYDROCARBON_IGNITION = "Ignition of Hydrocarbon Vapor Cloud"
    ELECTRICAL_ARC_FLASH = "Electrical Arc Flash & Energized Circuits"
    MECHANICAL_PINCH = "Rotating Machinery & Heavy Mechanical Pinch"
    CHEMICAL_SPLASH = "Corrosive / Hazardous Chemical Splash"
    VEHICLE_COLLISION = "Vehicle Rollover & Heavy Transport Collision"
    EXCAVATION_COLLAPSE = "Trench & Excavation Wall Collapse"
    OPERATIONAL_HAZARD = "Operational Hazard Exposure"
    OTHER = "Other"


class ActivityCategory(StrEnum):
    """Canonical Operational Activity Taxonomy (Version 1.0)."""
    MAINTENANCE = "Maintenance"
    DRILLING_OPERATIONS = "Drilling Operations"
    WELL_INTERVENTION = "Well Intervention"
    LIFTING_RIGGING = "Lifting & Rigging"
    VESSEL_CLEANING = "Vessel Cleaning & Desanding"
    WORKING_AT_HEIGHT = "Working at Height"
    HOT_WORK_WELDING = "Hot Work & Welding"
    PIPELINE_TRANSPORT = "Pipeline Pigging & Transport"
    PLANT_OPERATIONS = "Plant Operations & Header Sampling"
    ELECTRICAL_SERVICING = "Electrical Substation Servicing"
    CIVIL_CONSTRUCTION = "Civil Construction & Excavation"
    OTHER = "Other"


class LifeSavingRuleIdentifier(StrEnum):
    """Canonical IOGP Life-Saving Rules Mapping (Version 1.0)."""
    ENERGY_ISOLATION = "Energy Isolation"
    CONFINED_SPACE = "Confined Space Entry"
    LINE_OF_FIRE = "Line of Fire"
    SAFE_MECHANICAL_LIFTING = "Safe Mechanical Lifting"
    WORKING_AT_HEIGHT = "Working at Height"
    HOT_WORK = "Hot Work & Ignition Control"
    DRIVING_SAFETY = "Safe Driving & Journey Management"
    BYPASSING_SAFETY_CONTROLS = "Bypassing Safety Controls"
    TOXIC_GAS_PROTECTION = "Toxic Gas Protection (H2S)"
    WORK_AUTHORIZATION = "Work Authorization & PTW"


class SafetyBarrierCategory(StrEnum):
    """Canonical Barrier Hierarchy Category."""
    ENGINEERING = "Engineering / Physical Barrier"
    ADMINISTRATIVE = "Administrative / Procedural Barrier"
    BEHAVIORAL_PPE = "Behavioral / Last Line of Defense (PPE)"


class BarrierStatusLevel(StrEnum):
    """Canonical Safety Barrier Integrity Status."""
    FAILED = "FAILED"
    WEAK = "WEAK"
    EFFECTIVE = "EFFECTIVE"
    UNKNOWN = "UNKNOWN"


# ------------------------------------------------------------------------------
# Taxonomy Metadata Models
# ------------------------------------------------------------------------------

class TaxonomyItemDefinition(BaseModel):
    """Metadata definition for a taxonomy item."""
    code: str
    name: str
    description: str
    category: Optional[str] = None
    taxonomy_version: str = Field(default="1.0")
    active: bool = Field(default=True)
