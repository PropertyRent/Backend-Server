import uuid
from enum import Enum
from tortoise import fields, models
from datetime import datetime

class MeetingStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ScheduleMeeting(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    full_name = fields.CharField(max_length=255, null=False)
    email = fields.CharField(max_length=255, null=False)
    phone = fields.CharField(max_length=20, null=False)
    
    meeting_date = fields.DateField(null=False)
    meeting_time = fields.TimeField(null=False)
    
    # Relationship with Property
    property = fields.ForeignKeyField("models.Property", related_name="scheduled_meetings", on_delete=fields.CASCADE)
    
    # Relationship with User (optional - if user is logged in)
    user = fields.ForeignKeyField("models.User", related_name="scheduled_meetings", null=True, on_delete=fields.CASCADE)
    
    # Meeting details
    message = fields.TextField(null=True)
    status = fields.CharEnumField(MeetingStatus, default=MeetingStatus.PENDING)
    
    # Admin fields
    admin_notes = fields.TextField(null=True)
    admin_reply = fields.TextField(null=True, default=None)  # Admin reply message to user
    admin_reply_date = fields.DatetimeField(null=True, default=None)  # When admin replied
    approved_by = fields.ForeignKeyField("models.User", related_name="approved_meetings", null=True, on_delete=fields.SET_NULL)
    approved_at = fields.DatetimeField(null=True)
    completed_at = fields.DatetimeField(null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "schedule_meetings"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Meeting: {self.full_name} - {self.meeting_date} {self.meeting_time}"