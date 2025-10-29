"""Tenant data models for Next Action Tracker."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class TenantBase(BaseModel):
    """Base tenant model with common fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Tenant organization name")


class TenantCreate(TenantBase):
    """Model for creating a new tenant."""
    pass


class TenantUpdate(BaseModel):
    """Model for updating tenant information."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated tenant name")


class Tenant(TenantBase):
    """Complete tenant model with all fields."""
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True