import os
import uuid
import bcrypt
from fastapi.responses import JSONResponse
import jwt
from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File, Form
from starlette.status import HTTP_400_BAD_REQUEST
from tortoise.exceptions import DoesNotExist
from model.userModel import User
from schemas.userSchemas import UserCreate, UserLogin, ResetPasswordSchema, UserUpdate
from services.authServices import create_token
from services.cookieServices import set_token_cookie
from services.cookieServices import clear_token_cookie
from config.fileUpload import process_profile_photo
from emailService.authEmail import (
    send_forget_password_email,
    send_verification_email,
    send_password_reset_success_email,
    send_congrats_email,
    send_update_profile_email,
)

router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


async def handle_signup(user_data: UserCreate):
    print(" Handling user signup...")
    existing_user = await User.filter(email=user_data.email).first()
    print(f"Existing user check: {existing_user}")
    if existing_user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User already exists, Please login")
    print("Creating new user...")
    hashed_password = bcrypt.hashpw(user_data.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    new_user = await User.create(
        email=user_data.email,
        password=hashed_password,
        full_name=user_data.full_name,
        role="user",
    )
    print(f"New user created: {new_user}")

    verify_token = create_token(new_user, expires_in=1800)  # 30 min
    verify_url = f"{FRONTEND_URL}/verify-email/{verify_token}"
    await send_verification_email(new_user.email, verify_url)

    return {
        "success": True,
        "verifyUrl": verify_url,
        "message": "User registered. Please check your email to verify your account.",
        "user": {"id": str(new_user.id), "email": new_user.email, "full_name": new_user.full_name},
    }


async def handle_verify_email(token: str):
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = decoded.get("id")
        user = await User.get(id=uuid.UUID(user_id))

        if user.is_verified:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User already verified")

        user.is_verified = True
        await user.save()
        await send_congrats_email(user.email)
        return {"success": True, "message": "Email verified successfully"}

    except (jwt.ExpiredSignatureError, jwt.DecodeError, DoesNotExist):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid or expired token")



async def handle_resend_verification(data: dict):
    email = data.get("email")
    user = await User.filter(email=email).first()
    if not user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User not found")
    if user.is_verified:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User already verified")

    verify_token = create_token(user, expires_in=1800)
    verify_url = f"{FRONTEND_URL}/verify-email/{verify_token}"
    await send_verification_email(user.email, verify_url)
    return {"success": True, "verifyUrl": verify_url, "message": "Verification email resent"}



async def handle_login(response: Response, user_data: UserLogin):
    user = await User.filter(email=user_data.email).first()
    if not user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid credentials")

    if not user.is_verified:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Please verify your email first")

    if not user.password:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="User registered with Google, use Google login or reset password",
        )

    if not bcrypt.checkpw(user_data.password.encode("utf-8"), user.password.encode("utf-8")):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid password")

    token = create_token(user)

    set_token_cookie(response, token)

    return JSONResponse(
        content={
            "success": True,
            "message": "Login successful",
            "token": token,
            "user": {"id": str(user.id), "email": user.email},
        },
        headers=response.headers  
    )



async def handle_logout(response: Response):
    clear_token_cookie(response)
    return {"success": True, "message": "Logged out successfully"}



async def handle_forgot_password(data: dict):
    email = data.get("email")
    user = await User.filter(email=email).first()
    if not user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User not found")

    reset_token = create_token(user, expires_in=900)  # 15 min
    reset_url = f"{FRONTEND_URL}/reset-password/{reset_token}"
    await send_forget_password_email(user.email, reset_url)
    return {"success": True, "message": "Password reset email sent", "resetUrl": reset_url}


async def handle_reset_password(reset_token: str, data: ResetPasswordSchema):
    try:
        decoded = jwt.decode(reset_token, JWT_SECRET, algorithms=["HS256"])
        user_id = decoded.get("id")
        user = await User.get(id=uuid.UUID(user_id))

        hashed_password = bcrypt.hashpw(data.new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user.password = hashed_password
        await user.save()
        await send_password_reset_success_email(user.email)
        return {"success": True, "message": "Password reset successfully"}

    except (jwt.ExpiredSignatureError, jwt.DecodeError, DoesNotExist):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

async def get_current_user(user_id: str):
    try:
        user = await User.get(id=user_id)
        return user
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")


async def handle_get_profile(current_user: User = Depends(get_current_user)):
    try:
        user_dict = current_user.__dict__.copy()
        user_dict.pop("password", None) 
        return {"success": True, "user": user_dict}
    except Exception as error:
        return {
            "success": False,
            "message": "Server error",
            "error": str(error)
        }


async def handle_update_profile(
    full_name: str = Form(None),
    phone: str = Form(None),
    profile_photo: UploadFile = File(None),
    current_user: User = Depends(get_current_user)
):
    """Update user profile with optional photo upload"""
    try:
        print(f" Updating profile for user: {current_user.email}")
        
        update_data = {}
        
        # Update text fields if provided
        if full_name is not None:
            update_data['full_name'] = full_name
            
        if phone is not None:
            update_data['phone'] = phone
        
        # Process profile photo if uploaded
        if profile_photo:
            print(f" Processing profile photo: {profile_photo.filename}")
            try:
                # Process image to base64
                base64_image = await process_profile_photo(profile_photo)
                update_data['profile_photo'] = base64_image
                print(" Profile photo processed successfully")
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Photo processing failed: {str(e)}")
        
        # Update user if there's data to update
        if update_data:
            await current_user.update_from_dict(update_data)
            await current_user.save()
            
            # Send confirmation email
            await send_update_profile_email(current_user.email)
            
            print(f" Profile updated successfully for user: {current_user.email}")
            
            # Return updated user data (without password)
            updated_user = await User.get(id=current_user.id)
            user_dict = updated_user.__dict__.copy()
            user_dict.pop("password", None)
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Profile updated successfully",
                    "user": {
                        "id": str(user_dict["id"]),
                        "email": user_dict["email"],
                        "full_name": user_dict["full_name"],
                        "phone": user_dict["phone"],
                        "profile_photo": user_dict["profile_photo"],
                        "role": user_dict["role"],
                        "is_verified": user_dict["is_verified"],
                        "created_at": user_dict["created_at"].isoformat(),
                        "updated_at": user_dict["updated_at"].isoformat()
                    }
                }
            )
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "No data provided for update"
                }
            )
            
    except HTTPException:
        raise
    except Exception as error:
        print(f" Profile update failed: {error}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update profile"
        )


async def handle_upload_profile_photo(
    profile_photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload/update profile photo only"""
    try:
        print(f" Uploading profile photo for user: {current_user.email}")
        
        # Process image to base64
        base64_image = await process_profile_photo(profile_photo)
        
        # Update user profile photo
        current_user.profile_photo = base64_image
        await current_user.save()
        
        print(" Profile photo uploaded successfully")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Profile photo updated successfully",
                "profile_photo": base64_image
            }
        )
        
    except HTTPException:
        raise
    except Exception as error:
        print(f" Profile photo upload failed: {error}")
        raise HTTPException(
            status_code=500,
            detail="Failed to upload profile photo"
        )