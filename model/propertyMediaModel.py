import uuid
from enum import Enum
from tortoise import fields, models


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"


class PropertyMedia(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    property = fields.ForeignKeyField(
        "models.Property", related_name="media", on_delete=fields.CASCADE
    )
    media_type = fields.CharEnumField(MediaType)
    url = fields.TextField()  # Long text field for base64 storage (no length limit)
    is_cover = fields.BooleanField(default=False)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "property_media"

    def __str__(self):
        return f"{self.media_type} - {self.url}"
