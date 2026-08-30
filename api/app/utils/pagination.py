"""Pagination models and helper utilities."""

import math
from typing import Generic, List, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    page: int
    page_size: int
    total: int
    pages: int

    @classmethod
    def create(cls, items: List[T], total: int, params: PageParams) -> "PaginatedResponse[T]":
        pages = math.ceil(total / params.page_size) if total > 0 else 1
        return cls(
            items=items,
            page=params.page,
            page_size=params.page_size,
            total=total,
            pages=pages,
        )
