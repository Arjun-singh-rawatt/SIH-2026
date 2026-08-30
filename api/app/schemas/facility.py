"""Facility Pydantic schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class FacilityBase(BaseModel):
    facility_id: str = Field(..., description="Unique Facility Code (e.g. FAC-DUL-01)")
    name: str = Field(..., description="Full Facility Name")
    short_name: str = Field(..., description="Short Display Name")
    region: str = Field(..., description="Operational Basin/Region")
    type: str = Field(..., description="Facility Classification")
    location_description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    active_personnel: int = Field(default=0, ge=0)
    manager: Optional[str] = None
    active: bool = True


class FacilityCreate(FacilityBase):
    pass


class FacilityUpdate(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    region: Optional[str] = None
    type: Optional[str] = None
    location_description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    active_personnel: Optional[int] = None
    manager: Optional[str] = None
    active: Optional[bool] = None


class FacilityRead(FacilityBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class FacilityStats(BaseModel):
    facility_id: str
    facility_name: str
    short_name: str
    region: str
    type: str
    active_personnel: int
    risk_level: str
    total_reports: int
    sif_reports: int
    sif_density: float  # percentage
    high_urgency_count: int
    open_actions: int
    top_precursor: str
    top_activity: str
    primary_hazard: str
    manager: Optional[str] = None
