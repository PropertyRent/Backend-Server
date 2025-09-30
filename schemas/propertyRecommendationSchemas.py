from typing import Optional, List
from uuid import UUID
from datetime import datetime, date
from pydantic import BaseModel, EmailStr


class RecommendationBase(BaseModel):
    user_email: EmailStr
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    preferred_location: Optional[str] = None
    bedrooms_required: Optional[int] = None
    bathrooms_required: Optional[int] = None
    property_type_preference: Optional[str] = None
    move_in_date: Optional[date] = None


class RecommendationCreate(RecommendationBase):
    """Schema for creating a property recommendation"""
    screening_id: Optional[UUID] = None
    recommended_properties: Optional[List[dict]] = []
    match_score: Optional[float] = 0.0
    match_criteria: Optional[dict] = {}


class RecommendationUpdate(BaseModel):
    """Schema for updating a recommendation"""
    status: Optional[str] = None
    user_response: Optional[str] = None
    admin_reviewed: Optional[bool] = None
    admin_notes: Optional[str] = None
    priority_level: Optional[str] = None


class PropertyMatch(BaseModel):
    """Schema for individual property matches"""
    property_id: UUID
    property_title: str
    property_type: str
    price: float
    location: str
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    match_score: float
    match_reasons: List[str]


class RecommendationResponse(RecommendationBase):
    """Schema for recommendation response"""
    id: UUID
    screening_id: Optional[UUID] = None
    recommended_properties: List[dict]
    match_score: float
    match_criteria: dict
    status: str
    email_sent: bool
    email_sent_at: Optional[datetime] = None
    user_response: Optional[str] = None
    user_responded_at: Optional[datetime] = None
    admin_reviewed: bool
    admin_notes: Optional[str] = None
    priority_level: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True