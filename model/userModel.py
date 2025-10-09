import uuid
from enum import Enum
from tortoise import fields, models

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    ADMIN_PLUS = "admin+"
    SUPERADMIN = "superadmin"

class User(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    full_name = fields.CharField(max_length=255, null=True)
    email = fields.CharField(max_length=255, unique=True, index=True)
    password = fields.CharField(max_length=255, null=True)
    profile_photo = fields.TextField(null=True)  
    phone = fields.CharField(max_length=20, null=True)

    role = fields.CharEnumField(UserRole, default=UserRole.USER)
    is_verified = fields.BooleanField(default=False)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users" 

    def __str__(self):
        return self.email
