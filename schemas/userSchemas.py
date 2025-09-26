from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    full_name: str | None
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ResetPasswordSchema(BaseModel):
    new_password: str
