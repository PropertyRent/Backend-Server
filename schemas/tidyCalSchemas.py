from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import date, time, datetime
from enum import Enum

class BookingPageStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"

class BookingStatusEnum(str, Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"

# TidyCal Booking Page Schemas
class TidyCalBookingPageCreate(BaseModel):
    property_id: str
    page_name: str
    description: Optional[str] = None
    duration_minutes: Optional[int] = 60
    buffer_before: Optional[int] = 15
    buffer_after: Optional[int] = 15
    is_public: Optional[bool] = True
    custom_questions: Optional[List[Dict[str, Any]]] = None
    notification_settings: Optional[Dict[str, Any]] = None

class TidyCalBookingPageUpdate(BaseModel):
    page_name: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    buffer_before: Optional[int] = None
    buffer_after: Optional[int] = None
    status: Optional[BookingPageStatusEnum] = None
    is_public: Optional[bool] = None
    custom_questions: Optional[List[Dict[str, Any]]] = None
    notification_settings: Optional[Dict[str, Any]] = None

class TidyCalBookingPageResponse(BaseModel):
    id: str
    property_id: str
    property_title: Optional[str] = None
    tidycal_booking_page_id: Optional[str] = None
    booking_url: str
    embed_code: Optional[str] = None
    page_name: str
    description: Optional[str] = None
    duration_minutes: int
    buffer_before: int
    buffer_after: int
    status: str
    is_public: bool
    total_bookings: int
    last_booking_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# TidyCal Booking Schemas
class TidyCalBookingCreate(BaseModel):
    booking_page_id: str
    customer_name: str
    customer_email: EmailStr
    customer_phone: Optional[str] = None
    scheduled_date: date
    scheduled_time: time
    duration_minutes: Optional[int] = 60
    timezone: Optional[str] = "UTC"
    customer_notes: Optional[str] = None
    custom_responses: Optional[Dict[str, Any]] = None

class TidyCalBookingUpdate(BaseModel):
    booking_status: Optional[BookingStatusEnum] = None
    admin_notes: Optional[str] = None
    customer_notes: Optional[str] = None

class TidyCalBookingResponse(BaseModel):
    id: str
    tidycal_booking_id: str
    booking_page_id: str
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    scheduled_date: date
    scheduled_time: time
    duration_minutes: int
    timezone: str
    booking_status: str
    customer_notes: Optional[str] = None
    admin_notes: Optional[str] = None
    custom_responses: Optional[Dict[str, Any]] = None
    booking_created_at: datetime
    created_at: datetime
    updated_at: datetime
    
    # Property information
    property_title: Optional[str] = None
    property_address: Optional[str] = None
    
    class Config:
        from_attributes = True

# Webhook Schemas
class TidyCalWebhookEvent(BaseModel):
    event_type: str  # booking.created, booking.cancelled, booking.completed, etc.
    booking_id: str
    booking_page_id: str
    customer: Dict[str, Any]
    booking_details: Dict[str, Any]
    timestamp: datetime

class TidyCalWebhookResponse(BaseModel):
    success: bool
    message: str
    processed_at: datetime

# Integration Response Schemas
class TidyCalIntegrationStatus(BaseModel):
    is_configured: bool
    api_key_present: bool
    webhook_configured: bool
    total_booking_pages: int
    total_bookings: int
    last_sync: Optional[datetime] = None

class BookingPageEmbedResponse(BaseModel):
    booking_url: str
    embed_code: str
    iframe_width: Optional[str] = "100%"
    iframe_height: Optional[str] = "600px"
    custom_styling: Optional[Dict[str, str]] = None

# Property Integration Schemas
class PropertyWithBookingPage(BaseModel):
    property_id: str
    property_title: str
    property_address: str
    property_price: Optional[float] = None
    has_booking_page: bool
    booking_page: Optional[TidyCalBookingPageResponse] = None
    recent_bookings_count: Optional[int] = 0

# Analytics Schemas
class BookingAnalytics(BaseModel):
    total_bookings: int
    confirmed_bookings: int
    cancelled_bookings: int
    completed_bookings: int
    no_show_bookings: int
    most_popular_times: List[Dict[str, Any]]
    booking_trends: Dict[str, int]  # Monthly trends
    average_booking_duration: float
    
class BookingPageAnalytics(BaseModel):
    booking_page_id: str
    page_name: str
    property_title: str
    analytics: BookingAnalytics
    created_at: datetime