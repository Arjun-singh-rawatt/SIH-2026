"""FastAPI Dependency Injection helpers."""

from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.repositories.report_repo import ReportRepository
from app.db.repositories.facility_repo import FacilityRepository
from app.db.repositories.action_repo import ActionRepository
from app.db.repositories.user_repo import UserRepository
from app.db.repositories.barrier_repo import BarrierRepository
from app.db.repositories.pattern_repo import PatternRepository
from app.ai import get_ai_provider, AIProvider
from app.vector import get_vector_store, get_embedding_provider, VectorStore, EmbeddingProvider
from app.services.analysis_service import AnalysisService
from app.services.report_service import ReportService
from app.services.mongo_report_service import MongoReportService
from app.core.config import settings
from app.services.review_service import ReviewService
from app.services.dashboard_service import DashboardService
from app.services.facility_service import FacilityService
from app.services.action_service import ActionService
from app.services.intelligence_service import IntelligenceService
from app.services.life_saving_rule_service import LifeSavingRuleService
from app.services.user_service import UserService

# Database session dependency
DBSession = Annotated[AsyncSession, Depends(get_db)]

# Repositories
def get_report_repo(db: DBSession) -> ReportRepository:
    return ReportRepository(db)

def get_facility_repo(db: DBSession) -> FacilityRepository:
    return FacilityRepository(db)

def get_action_repo(db: DBSession) -> ActionRepository:
    return ActionRepository(db)

def get_user_repo(db: DBSession) -> UserRepository:
    return UserRepository(db)

def get_barrier_repo(db: DBSession) -> BarrierRepository:
    return BarrierRepository(db)

def get_pattern_repo(db: DBSession) -> PatternRepository:
    return PatternRepository(db)

# Services
def get_analysis_service(
    ai_provider: Annotated[AIProvider, Depends(get_ai_provider)] = None,
) -> AnalysisService:
    return AnalysisService(ai_provider or get_ai_provider())

def get_report_service(
    report_repo: Annotated[ReportRepository, Depends(get_report_repo)],
    facility_repo: Annotated[FacilityRepository, Depends(get_facility_repo)],
    analysis_service: Annotated[AnalysisService, Depends(get_analysis_service)],
) -> ReportService:
    if settings.REPORT_STORAGE.lower() == "mongodb":
        return MongoReportService(analysis_service)  # type: ignore[return-value]
    return ReportService(
        report_repo=report_repo,
        facility_repo=facility_repo,
        analysis_service=analysis_service,
        vector_store=get_vector_store(),
        embedding_provider=get_embedding_provider(),
    )

def get_review_service(
    report_repo: Annotated[ReportRepository, Depends(get_report_repo)],
    report_service: Annotated[ReportService, Depends(get_report_service)],
) -> ReviewService:
    return ReviewService(report_repo=report_repo, report_service=report_service)

def get_dashboard_service(
    report_repo: Annotated[ReportRepository, Depends(get_report_repo)],
    facility_repo: Annotated[FacilityRepository, Depends(get_facility_repo)],
    action_repo: Annotated[ActionRepository, Depends(get_action_repo)],
) -> DashboardService:
    return DashboardService(
        report_repo=report_repo,
        facility_repo=facility_repo,
        action_repo=action_repo,
    )

def get_facility_service(
    facility_repo: Annotated[FacilityRepository, Depends(get_facility_repo)],
) -> FacilityService:
    return FacilityService(facility_repo=facility_repo)

def get_action_service(
    action_repo: Annotated[ActionRepository, Depends(get_action_repo)],
    report_repo: Annotated[ReportRepository, Depends(get_report_repo)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    facility_repo: Annotated[FacilityRepository, Depends(get_facility_repo)],
) -> ActionService:
    return ActionService(
        action_repo=action_repo,
        report_repo=report_repo,
        user_repo=user_repo,
        facility_repo=facility_repo,
    )

def get_intelligence_service(
    pattern_repo: Annotated[PatternRepository, Depends(get_pattern_repo)],
    report_repo: Annotated[ReportRepository, Depends(get_report_repo)],
) -> IntelligenceService:
    return IntelligenceService(
        pattern_repo=pattern_repo,
        report_repo=report_repo,
        vector_store=get_vector_store(),
        embedding_provider=get_embedding_provider(),
    )

def get_life_saving_rule_service(
    report_repo: Annotated[ReportRepository, Depends(get_report_repo)],
) -> LifeSavingRuleService:
    return LifeSavingRuleService(report_repo=report_repo)

def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> UserService:
    return UserService(user_repo=user_repo)

from app.db.repositories.annotation_repo import AnnotationRepository
from app.services.annotation_service import AnnotationService
from fastapi import Header
from app.db.models.user import User
from typing import Optional

def get_annotation_repo(db: DBSession) -> AnnotationRepository:
    return AnnotationRepository(db)

def get_annotation_service(
    annotation_repo: Annotated[AnnotationRepository, Depends(get_annotation_repo)],
    report_repo: Annotated[ReportRepository, Depends(get_report_repo)],
) -> AnnotationService:
    return AnnotationService(annotation_repo=annotation_repo, report_repo=report_repo)

async def get_current_user(
    x_user_id: Annotated[Optional[str], Header(alias="X-User-Id")] = None,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)] = None,
) -> User:
    """Resolve active user identity from X-User-Id header (Development identity mechanism)."""
    user_id = x_user_id or "USR-001"
    user = await user_repo.get_by_user_id(user_id)
    if not user:
        if x_user_id:
            return User(
                user_id=x_user_id,
                name=f"User {x_user_id}",
                email=f"{x_user_id.lower()}@oilindia.in",
                role="Observer",
            )
        users = await user_repo.get_all()
        if users:
            return users[0]
        return User(
            user_id=user_id,
            name="Alok Sharma",
            email="alok.sharma@oilindia.in",
            role="HSE Manager",
        )
    return user
