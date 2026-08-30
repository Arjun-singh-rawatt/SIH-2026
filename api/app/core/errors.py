"""Standardized application exceptions and error models."""

from typing import Any, Optional
from fastapi import HTTPException, status


class SIFTException(HTTPException):
    """Base SIFT API Exception."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail={"error": {"code": code, "message": message, "details": details}},
        )


class EntityNotFoundException(SIFTException):
    def __init__(self, entity_name: str, identifier: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code=f"{entity_name.upper()}_NOT_FOUND",
            message=f"{entity_name} with identifier '{identifier}' was not found.",
        )


class ReportNotFoundException(EntityNotFoundException):
    def __init__(self, report_id: Any):
        super().__init__("REPORT", report_id)


class FacilityNotFoundException(EntityNotFoundException):
    def __init__(self, facility_id: Any):
        super().__init__("FACILITY", facility_id)


class UserNotFoundException(EntityNotFoundException):
    def __init__(self, user_id: Any):
        super().__init__("USER", user_id)


class ActionNotFoundException(EntityNotFoundException):
    def __init__(self, action_id: Any):
        super().__init__("ACTION", action_id)


class PatternNotFoundException(EntityNotFoundException):
    def __init__(self, pattern_id: Any):
        super().__init__("PATTERN", pattern_id)


class LifeSavingRuleNotFoundException(EntityNotFoundException):
    def __init__(self, rule_id: Any):
        super().__init__("LIFE_SAVING_RULE", rule_id)


class InvalidReportException(SIFTException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_REPORT",
            message=message,
        )


class AIProviderException(SIFTException):
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="AI_PROVIDER_ERROR",
            message=message,
            details=details,
        )


class VectorStoreException(SIFTException):
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="VECTOR_STORE_ERROR",
            message=message,
            details=details,
        )
