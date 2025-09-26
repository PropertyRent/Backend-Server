import uuid
from sqlalchemy import Column, String, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import DateTime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=True)
    profile_photo = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    role = Column(
        Enum("user", "admin", "admin+", "superadmin", name="user_roles"),
        default="user",
        nullable=False,
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User {self.email}>"
