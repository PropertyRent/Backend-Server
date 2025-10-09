from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr


class TeamBase(BaseModel):
    name: str
    age: int
    email: EmailStr
    description: Optional[str] = None
    phone: Optional[str] = None
    position_name: str


class TeamCreate(TeamBase):
    """Schema for creating a team member"""
    photo: Optional[str] = None  # Optional base64 image


class TeamUpdate(BaseModel):
    """Schema for updating team member details"""
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[EmailStr] = None
    photo: Optional[str] = None  # Base64 image
    description: Optional[str] = None
    phone: Optional[str] = None
    position_name: Optional[str] = None


class TeamResponse(TeamBase):
    """Schema for team member response"""
    id: UUID
    photo: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True