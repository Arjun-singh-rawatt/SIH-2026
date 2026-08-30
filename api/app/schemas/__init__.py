"""SIFT Schemas Package."""

from app.schemas.common import (
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
    DatabaseHealthResponse,
    GenericSuccessResponse,
)
from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.schemas.facility import FacilityRead, FacilityCreate, FacilityUpdate, FacilityStats
from app.schemas.barrier import BarrierAssessmentRead, BarrierAssessmentCreate
from app.schemas.action import ActionItemRead, ActionItemCreate, ActionItemUpdate, ActionStatsResponse
from app.schemas.analysis import AnalyzeRequest, ReportAnalysisResult
from app.schemas.review import ReviewSubmitRequest, ReviewQueueSummary
from app.schemas.report import ReportRead, ReportDetail, ReportCreate, ReportUpdate, ReportStats
from app.schemas.dashboard import (
    DashboardOverview,
    DashboardSummary,
    TrendPoint,
    PrecursorDistPoint,
    FacilityRankingPoint,
    ActivityRankingPoint,
    BarrierFailurePoint,
    PriorityAttentionItem,
)
from app.schemas.intelligence import (
    PatternRead,
    PatternOverviewKPIs,
    SimilarReportMatch,
    SimilarReportsResponse,
)
from app.schemas.life_saving_rule import LifeSavingRuleRead, LifeSavingRuleDetail
from app.schemas.vector import VectorRecord, VectorQueryRequest, VectorMatch

__all__ = [
    "ErrorDetail",
    "ErrorResponse",
    "HealthResponse",
    "DatabaseHealthResponse",
    "GenericSuccessResponse",
    "UserRead",
    "UserCreate",
    "UserUpdate",
    "FacilityRead",
    "FacilityCreate",
    "FacilityUpdate",
    "FacilityStats",
    "BarrierAssessmentRead",
    "BarrierAssessmentCreate",
    "ActionItemRead",
    "ActionItemCreate",
    "ActionItemUpdate",
    "ActionStatsResponse",
    "AnalyzeRequest",
    "ReportAnalysisResult",
    "ReviewSubmitRequest",
    "ReviewQueueSummary",
    "ReportRead",
    "ReportDetail",
    "ReportCreate",
    "ReportUpdate",
    "ReportStats",
    "DashboardOverview",
    "DashboardSummary",
    "TrendPoint",
    "PrecursorDistPoint",
    "FacilityRankingPoint",
    "ActivityRankingPoint",
    "BarrierFailurePoint",
    "PriorityAttentionItem",
    "PatternRead",
    "PatternOverviewKPIs",
    "SimilarReportMatch",
    "SimilarReportsResponse",
    "LifeSavingRuleRead",
    "LifeSavingRuleDetail",
    "VectorRecord",
    "VectorQueryRequest",
    "VectorMatch",
]
