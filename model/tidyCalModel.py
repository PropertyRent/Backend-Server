import uuid
from tortoise import fields, models
from enum import Enum

class BookingPageStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"

class TidyCalBookingPage(models.Model):
    """
    Model to store TidyCal booking page information for properties
    """
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    
    # Property relationship
    property = fields.ForeignKeyField("models.Property", related_name="booking_pages", on_delete=fields.CASCADE)
    
    # TidyCal booking page details
    tidycal_booking_page_id = fields.CharField(max_length=255, null=True)  # TidyCal's booking page ID
    booking_url = fields.TextField(null=False)  # Direct booking URL
    embed_code = fields.TextField(null=True)   # Iframe embed code
    
    # Page configuration
    page_name = fields.CharField(max_length=255, null=False)
    description = fields.TextField(null=True)
    duration_minutes = fields.IntField(default=60)  # Meeting duration
    buffer_before = fields.IntField(default=15)     # Buffer before meeting
    buffer_after = fields.IntField(default=15)      # Buffer after meeting
    
    # Status and settings
    status = fields.CharEnumField(BookingPageStatus, default=BookingPageStatus.ACTIVE)
    is_public = fields.BooleanField(default=True)   # Whether page is publicly accessible
    
    # Additional settings
    custom_questions = fields.JSONField(null=True)  # Custom questions for booking
    notification_settings = fields.JSONField(null=True)  # Email notification settings
    
    # Tracking
    total_bookings = fields.IntField(default=0)     # Total bookings made
    last_booking_date = fields.DatetimeField(null=True)  # Last booking made
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "tidycal_booking_pages"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"Booking Page: {self.page_name}"


class TidyCalBooking(models.Model):
    """
    Model to store TidyCal booking information synchronized with our system
    """
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    
    # TidyCal booking details
    tidycal_booking_id = fields.CharField(max_length=255, null=False, unique=True)
    booking_page = fields.ForeignKeyField("models.TidyCalBookingPage", related_name="bookings", on_delete=fields.CASCADE)
    
    # Customer information
    customer_name = fields.CharField(max_length=255, null=False)
    customer_email = fields.CharField(max_length=255, null=False)
    customer_phone = fields.CharField(max_length=20, null=True)
    
    # Booking details
    scheduled_date = fields.DateField(null=False)
    scheduled_time = fields.TimeField(null=False)
    duration_minutes = fields.IntField(default=60)
    timezone = fields.CharField(max_length=50, default="UTC")
    
    # Status and metadata
    booking_status = fields.CharField(max_length=50, default="confirmed")  # confirmed, cancelled, completed, no_show
    customer_notes = fields.TextField(null=True)    # Notes from customer
    admin_notes = fields.TextField(null=True)       # Internal admin notes
    
    # Custom field responses
    custom_responses = fields.JSONField(null=True)  # Responses to custom questions
    
    # Integration with existing system
    local_meeting = fields.ForeignKeyField("models.ScheduleMeeting", related_name="tidycal_booking", null=True, on_delete=fields.SET_NULL)
    
    # Tracking
    booking_created_at = fields.DatetimeField(null=False)  # When booking was made in TidyCal
    last_sync_at = fields.DatetimeField(auto_now=True)     # Last time synced with TidyCal
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "tidycal_bookings"
        ordering = ["-scheduled_date", "-scheduled_time"]
    
    def __str__(self):
        return f"Booking: {self.customer_name} - {self.scheduled_date} {self.scheduled_time}"