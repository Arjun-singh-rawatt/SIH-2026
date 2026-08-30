"""Vector Storage and Embedding schemas."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class VectorRecord(BaseModel):
    id: str
    values: List[float]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VectorQueryRequest(BaseModel):
    vector: Optional[List[float]] = None
    text: Optional[str] = None
    top_k: int = 5
    filter: Optional[Dict[str, Any]] = None


class VectorMatch(BaseModel):
    id: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
