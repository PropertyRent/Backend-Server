import uuid
from enum import Enum
from tortoise import fields, models


class ContactStatus(str, Enum):
    PENDING = "pending"
    REPLIED = "replied"
    RESOLVED = "resolved"


class ContactUs(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    full_name = fields.CharField(max_length=255, null=False)
    email = fields.CharField(max_length=255, null=False)
    message = fields.TextField(null=False)
    phone = fields.CharField(max_length=20, null=True)
    status = fields.CharEnumField(ContactStatus, default=ContactStatus.PENDING)
    admin_reply = fields.TextField(null=True)
    admin_reply_date = fields.DatetimeField(null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "contact_us"

    def __str__(self):
        return f"{self.full_name} - {self.email}"