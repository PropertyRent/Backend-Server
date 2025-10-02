from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import date, time, datetime
from enum import Enum

class MeetingStatusEnum(str, Enum):
    PENDING = "pending"
    REPLIED = "replied"
    APPROVED = "approved"  
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ScheduleMeetingCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    meeting_date: date
    meeting_time: time
    property_id: str
    message: Optional[str] = None

    @validator('meeting_date')
    def validate_meeting_date(cls, v):
        if v < date.today():
            raise ValueError('Meeting date cannot be in the past')
        return v

    @validator('full_name')
    def validate_full_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters long')
        return v.strip()

    @validator('phone')
    def validate_phone(cls, v):
        # Remove any spaces, dashes, or parentheses
        cleaned_phone = ''.join(filter(str.isdigit, v))
        if len(cleaned_phone) < 10:
            raise ValueError('Phone number must be at least 10 digits')
        return v

class ScheduleMeetingUpdate(BaseModel):
    status: Optional[MeetingStatusEnum] = None
    admin_message: Optional[str] = None  # Single admin message field
    meeting_date: Optional[date] = None
    meeting_time: Optional[time] = None

class AdminReplySchema(BaseModel):
    """Schema for admin reply to meeting"""
    message: str
    action: Optional[MeetingStatusEnum] = None  # approve or reject (optional)

class ScheduleMeetingResponse(BaseModel):
    id: str
    full_name: str
    email: str
    phone: str
    meeting_date: date
    meeting_time: time
    property_id: str
    user_id: Optional[str] = None
    message: Optional[str] = None
    status: str
    admin_message: Optional[str] = None
    admin_reply_date: Optional[datetime] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ScheduleMeetingWithProperty(BaseModel):
    id: str
    full_name: str
    email: str
    phone: str
    meeting_date: date
    meeting_time: time
    message: Optional[str] = None
    status: str
    admin_message: Optional[str] = None
    admin_reply_date: Optional[datetime] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    property: dict  # Property details
    user: Optional[dict] = None  # User details if available

    class Config:
        from_attributes = True

class MeetingStatsResponse(BaseModel):
    total_meetings: int
    pending_meetings: int
    approved_meetings: int
    completed_meetings: int
    rejected_meetings: int
    cancelled_meetings: int