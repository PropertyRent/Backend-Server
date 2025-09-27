from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from model.propertyMediaModel import MediaType


class PropertyMediaBase(BaseModel):
    media_type: MediaType
    url: str
    is_cover: bool = False


class PropertyMediaCreate(PropertyMediaBase):
    """Schema for creating property media"""
    property_id: UUID


class PropertyMediaUpdate(BaseModel):
    """Schema for updating property media"""
    media_type: Optional[MediaType] = None
    url: Optional[str] = None
    is_cover: Optional[bool] = None


class PropertyMediaResponse(PropertyMediaBase):
    """Schema for property media response"""
    id: UUID
    property_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True