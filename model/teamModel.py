import uuid
from tortoise import fields, models


class Team(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=255, null=False)
    age = fields.IntField(null=False)
    email = fields.CharField(max_length=255, unique=True, index=True)
    photo = fields.TextField(null=True)  # Base64 encoded image
    description = fields.TextField(null=True)
    phone = fields.CharField(max_length=20, null=True)
    position_name = fields.CharField(max_length=255, null=False)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "teams"

    def __str__(self):
        return f"{self.name} - {self.position_name}"