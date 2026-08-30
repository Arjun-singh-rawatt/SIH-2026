"""Master API v1 Router aggregator."""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    reports,
    analysis,
    reviews,
    dashboard,
    intelligence,
    life_saving_rules,
    facilities,
    actions,
    users,
)

api_router = APIRouter()

# Health endpoints at root and sub-router
api_router.include_router(reports.router)
api_router.include_router(analysis.router)
api_router.include_router(reviews.router)
api_router.include_router(dashboard.router)
api_router.include_router(intelligence.router)
api_router.include_router(life_saving_rules.router)
api_router.include_router(facilities.router)
api_router.include_router(actions.router)
api_router.include_router(users.router)
