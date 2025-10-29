"""Opportunity data models for Next Action Tracker."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator


class OpportunityBase(BaseModel):
    """Base opportunity model with common fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Opportunity name")
    value: Optional[int] = Field(None, ge=0, description="Opportunity value in cents")
    stage: str = Field(..., min_length=1, max_length=100, description="Current sales stage")
    next_action_at: Optional[datetime] = Field(None, description="When the next action is due")
    next_action_details: Optional[str] = Field(None, max_length=1000, description="Details of the next action")
    
    @validator('next_action_details')
    def validate_next_action_details(cls, v, values):
        """Ensure next_action_details is provided when next_action_at is set."""
        next_action_at = values.get('next_action_at')
        
        if next_action_at is not None and (v is None or v.strip() == ''):
            raise ValueError('next_action_details is required when next_action_at is set')
        
        return v


class OpportunityCreate(OpportunityBase):
    """Model for creating a new opportunity."""
    tenant_id: UUID = Field(..., description="Tenant ID for multi-tenant isolation")


class OpportunityUpdate(BaseModel):
    """Model for updating opportunity next action (completing current action)."""
    new_next_action_at: datetime = Field(..., description="Due date for the new next action")
    new_next_action_details: str = Field(..., min_length=1, max_length=1000, description="Details of the new next action")


class OpportunityPartialUpdate(BaseModel):
    """Model for partial opportunity updates."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    value: Optional[int] = Field(None, ge=0)
    stage: Optional[str] = Field(None, min_length=1, max_length=100)
    next_action_at: Optional[datetime] = None
    next_action_details: Optional[str] = Field(None, max_length=1000)


class Opportunity(OpportunityBase):
    """Complete opportunity model with all fields."""
    id: UUID
    tenant_id: UUID
    last_activity_at: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OpportunityDue(BaseModel):
    """Simplified model for due opportunities dashboard."""
    id: UUID
    name: str
    value: Optional[int]
    stage: str
    next_action_at: datetime
    next_action_details: str
    
    class Config:
        from_attributes = True