"""IOGP Life-Saving Rules endpoints."""

from typing import List
from fastapi import APIRouter, Depends
from app.api.deps import get_life_saving_rule_service
from app.services.life_saving_rule_service import LifeSavingRuleService
from app.schemas.life_saving_rule import LifeSavingRuleRead, LifeSavingRuleDetail

router = APIRouter(prefix="/life-saving-rules", tags=["Life-Saving Rules"])


@router.get(
    "",
    response_model=List[LifeSavingRuleRead],
    summary="List IOGP Life-Saving Rules",
)
async def list_life_saving_rules(
    service: LifeSavingRuleService = Depends(get_life_saving_rule_service),
) -> List[LifeSavingRuleRead]:
    """Retrieve standardized Life-Saving Rules with dynamically calculated failure counts & SIF densities."""
    return await service.list_rules()


@router.get(
    "/{rule_id}",
    response_model=LifeSavingRuleDetail,
    summary="Get Life-Saving Rule Details & Associated Reports",
)
async def get_life_saving_rule(
    rule_id: str,
    service: LifeSavingRuleService = Depends(get_life_saving_rule_service),
) -> LifeSavingRuleDetail:
    """Retrieve complete standard specification and recently mapped field observations."""
    return await service.get_rule_by_id(rule_id)
