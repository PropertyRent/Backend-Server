from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr
from model.contactModel import ContactStatus


class ContactUsCreate(BaseModel):
    """Schema for creating a contact us message"""
    full_name: str
    email: EmailStr
    message: str
    phone: Optional[str] = None


class ContactUsUpdate(BaseModel):
    """Schema for updating contact us status (admin only)"""
    status: Optional[ContactStatus] = None
    admin_reply: Optional[str] = None


class ContactUsResponse(BaseModel):
    """Schema for contact us response"""
    id: UUID
    full_name: str
    email: str
    message: str
    phone: Optional[str] = None
    status: ContactStatus
    admin_reply: Optional[str] = None
    admin_reply_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminReply(BaseModel):
    """Schema for admin reply to contact us message"""
    message: str