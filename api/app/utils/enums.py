"""Domain Enums for SIFT Backend."""

from enum import Enum


class StrEnum(str, Enum):
    """String Enum base for clean JSON serialization."""
    def __str__(self) -> str:
        return self.value


class ReportType(StrEnum):
    UNSAFE_ACT = "Unsafe Act"
    UNSAFE_CONDITION = "Unsafe Condition"
    NEAR_MISS = "Near Miss"
    INCIDENT = "Incident"


class SIFPotential(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NON_SIF = "NON-SIF"


class SIFPrecursor(StrEnum):
    YES = "YES"
    NO = "NO"
    POTENTIAL = "POTENTIAL"


class ReviewStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    MODIFIED = "MODIFIED"
    NEEDS_CORRECTION = "NEEDS_CORRECTION"
    ESCALATED = "ESCALATED"


class BarrierStatus(StrEnum):
    FAILED = "FAILED"
    WEAK = "WEAK"
    EFFECTIVE = "EFFECTIVE"
    UNKNOWN = "UNKNOWN"


class ActionStatus(StrEnum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    OVERDUE = "Overdue"


class ActionPriority(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class UserRole(StrEnum):
    HSE_MANAGER = "HSE Manager"
    SAFETY_OFFICER = "Safety Officer"
    LEAD_INVESTIGATOR = "Lead Investigator"
    DRILLING_SUPERVISOR = "Drilling Supervisor"
    PROCESS_SAFETY = "Process Safety Specialist"
    PIPELINE_ENGINEER = "Pipeline Engineer"
    ADMINISTRATOR = "Administrator"


class LifeSavingRuleCategory(StrEnum):
    ENERGY_ISOLATION = "Energy Isolation"
    CONFINED_SPACE = "Confined Space"
    LINE_OF_FIRE = "Line of Fire"
    HOT_WORK = "Hot Work"
    WORKING_AT_HEIGHT = "Working at Height"
    LIFTING_OPERATIONS = "Lifting Operations"
    DRIVING_SAFETY = "Driving & Journey Management"
    BYPASSING_SAFEGUARDS = "Bypassing Safety Controls"
    TOXIC_GAS_EXPOSURE = "Toxic Gas & Chemical Exposure"
    PROCESS_SAFETY = "Process Safety"
