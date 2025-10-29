"""Base models and utilities for Next Action Tracker."""

from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Any, Dict


class TimestampMixin(BaseModel):
    """Mixin for models with timestamp fields."""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BaseResponse(BaseModel):
    """Base response model for API responses."""
    success: bool = True
    message: str = "Operation completed successfully"


class ErrorResponse(BaseModel):
    """Error response model for API errors."""
    success: bool = False
    message: str
    error_code: str
    details: Dict[str, Any] = Field(default_factory=dict)


def ensure_timezone_aware(dt: datetime) -> datetime:
    """Ensure datetime is timezone-aware (UTC if naive)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt