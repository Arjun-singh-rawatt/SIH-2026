"""Action Item Pydantic schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.utils.enums import ActionStatus, ActionPriority


class ActionItemBase(BaseModel):
    report_id: str = Field(..., description="Related Safety Report ID")
    assigned_to: str = Field(..., description="Assignee User ID")
    facility_id: str = Field(..., description="Facility ID")
    action_type: str = Field(..., description="Type/Category of Action")
    description: str = Field(..., description="Action Description & Deliverables")
    priority: str = Field(default=ActionPriority.HIGH.value)
    status: str = Field(default=ActionStatus.OPEN.value)
    due_date: datetime = Field(..., description="Due Date")
    completed_at: Optional[datetime] = None


class ActionItemCreate(BaseModel):
    report_id: str
    report_title: Optional[str] = None
    assigned_to: str
    facility_id: str
    action_type: str
    description: str
    priority: str = ActionPriority.HIGH.value
    due_date: datetime


class ActionItemUpdate(BaseModel):
    action_type: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ActionItemRead(ActionItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    action_id: str
    report_title: Optional[str] = None
    assignee_name: Optional[str] = None
    assignee_role: Optional[str] = None
    facility_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ActionStatsResponse(BaseModel):
    total: int
    open: int
    in_progress: int
    completed: int
    overdue: int
