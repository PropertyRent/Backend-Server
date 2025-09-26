import os
import uuid
import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from dbConnection.dbConfig import get_db
from model.userModel.userModel import User
from schemas.userSchemas import UserCreate, UserLogin, ResetPasswordSchema
from emailService.authEmail import (
    send_forget_password_email,
    send_verification_email,
    send_password_reset_success_email,
    send_congrats_email,
)

router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


def create_token(user: User, expires_in: int = 60 * 60):
    payload = {"id": str(user.id)}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


@router.post("/signup")
async def handle_signup(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User already exists")

    hashed_password = bcrypt.hashpw(user_data.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    new_user = User(
        email=user_data.email,
        password=hashed_password,
        full_name=user_data.full_name,
        role="user",
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    verify_token = create_token(new_user, expires_in=1800)  # 30m
    verify_url = f"{FRONTEND_URL}/verify-email/{verify_token}"

    await send_verification_email(new_user.email, verify_url)

    return {
        "success": True,
        "verifyUrl": verify_url,
        "message": "User registered. Please check your email to verify your account.",
        "user": {"id": str(new_user.id), "email": new_user.email},
    }


@router.get("/verify-email/{token}")
async def handle_verify_email(token: str, db: AsyncSession = Depends(get_db)):
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = decoded.get("id")

        result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid token")

        if getattr(user, "is_verified", False):
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User already verified")

        user.is_verified = True
        await db.commit()

        await send_congrats_email(user.email)
        return {"success": True, "message": "Email verified successfully"}

    except Exception:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid or expired token")


@router.post("/resend-verification")
async def handle_resend_verification(data: dict, db: AsyncSession = Depends(get_db)):
    email = data.get("email")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User not found")
    if getattr(user, "is_verified", False):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User already verified")

    verify_token = create_token(user, expires_in=1800)
    verify_url = f"{FRONTEND_URL}/verify-email/{verify_token}"

    await send_verification_email(user.email, verify_url)

    return {"success": True, "verifyUrl": verify_url, "message": "Verification email resent"}


@router.post("/login")
async def handle_login(
    response: Response, user_data: UserLogin, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid credentials")

    if not getattr(user, "is_verified", False):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Please verify your email first")

    if not user.password:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="User registered with Google, use Google login or reset password",
        )

    if not bcrypt.checkpw(user_data.password.encode("utf-8"), user.password.encode("utf-8")):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid password")

    token = create_token(user)
    response.set_cookie(key="token", value=token, httponly=True)

    return {"success": True, "message": "Login successful", "token": token, "user": {"id": str(user.id), "email": user.email}}


@router.post("/logout")
async def handle_logout(response: Response):
    response.delete_cookie("token")
    return {"success": True, "message": "Logged out successfully"}


@router.post("/forgot-password")
async def handle_forgot_password(data: dict, db: AsyncSession = Depends(get_db)):
    email = data.get("email")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User not found")

    reset_token = create_token(user, expires_in=900)  # 15m
    reset_url = f"{FRONTEND_URL}/reset-password/{reset_token}"

    await send_forget_password_email(user.email, reset_url)

    return {"success": True, "message": "Password reset email sent", "resetUrl": reset_url}


@router.post("/reset-password/{reset_token}")
async def handle_reset_password(reset_token: str, data: ResetPasswordSchema, db: AsyncSession = Depends(get_db)):
    try:
        decoded = jwt.decode(reset_token, JWT_SECRET, algorithms=["HS256"])
        user_id = decoded.get("id")

        result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User not found")

        hashed_password = bcrypt.hashpw(data.new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user.password = hashed_password
        await db.commit()

        await send_password_reset_success_email(user.email)

        return {"success": True, "message": "Password reset successfully"}

    except Exception:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
