import uuid
from tortoise import fields, models


class Notice(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    title = fields.CharField(max_length=255, null=False)
    description = fields.TextField(null=True)
    notice_file = fields.TextField(null=True)  # Base64 encoded file (PDF, image, or DOCX)
    file_type = fields.CharField(max_length=50, null=True)  # Store the original file type
    original_filename = fields.CharField(max_length=255, null=True)  # Store original filename
    is_active = fields.BooleanField(default=False)  # Active status for notices

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "notices"