from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class NoticeBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_active: Optional[bool] = True


class NoticeCreate(NoticeBase):
    """Schema for creating a notice"""
    notice_file: Optional[str] = None  # Optional base64 file
    file_type: Optional[str] = None
    original_filename: Optional[str] = None


class NoticeUpdate(BaseModel):
    """Schema for updating a notice"""
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    notice_file: Optional[str] = None
    file_type: Optional[str] = None
    original_filename: Optional[str] = None


class NoticeResponse(NoticeBase):
    """Schema for notice response"""
    id: UUID
    notice_file: Optional[str] = None
    file_type: Optional[str] = None
    original_filename: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True