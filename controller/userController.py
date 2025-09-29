import os
import uuid
import bcrypt
from fastapi.responses import JSONResponse
import jwt
from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File, Form, Request
from starlette.status import HTTP_400_BAD_REQUEST
from tortoise.exceptions import DoesNotExist
from model.userModel import User
from schemas.userSchemas import UserCreate, UserLogin, ResetPasswordSchema, UserUpdate
from services.authServices import create_token, validate_token
from services.cookieServices import set_token_cookie
from services.cookieServices import clear_token_cookie
from config.fileUpload import process_profile_photo
from authMiddleware.authMiddleware import check_for_authentication_cookie
from emailService.authEmail import (
    send_forget_password_email,
    send_verification_email,
    send_password_reset_success_email,
    send_congrats_email,
    send_update_profile_email,
)

router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


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

async def get_current_user(user_data: dict = Depends(check_for_authentication_cookie)) -> User:
    """Get current user from authentication middleware"""
    try:
        user_id = user_data.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        user = await User.get(id=uuid.UUID(user_id))
        return user
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


async def handle_get_profile(current_user: User = Depends(get_current_user)):
    try:
        user_dict = current_user.__dict__.copy()
        user_dict.pop("password", None) 
        
        # Convert datetime objects to ISO format strings
        if 'created_at' in user_dict and user_dict['created_at']:
            user_dict['created_at'] = user_dict['created_at'].isoformat()
        if 'updated_at' in user_dict and user_dict['updated_at']:
            user_dict['updated_at'] = user_dict['updated_at'].isoformat()
        
        # Convert UUID to string
        if 'id' in user_dict:
            user_dict['id'] = str(user_dict['id'])
        
        # Add photo metadata for frontend convenience
        photo_info = {
            "has_photo": bool(user_dict.get('profile_photo')),
            "photo_size": len(user_dict.get('profile_photo', '')) if user_dict.get('profile_photo') else 0
        }
        
        # If photo exists, extract some metadata
        if photo_info["has_photo"]:
            photo_data = user_dict['profile_photo']
            if photo_data.startswith('data:image/'):
                # Extract MIME type from data URL
                mime_part = photo_data.split(';')[0].split(':')[1]
                photo_info["mime_type"] = mime_part
                photo_info["format"] = mime_part.split('/')[-1].upper()
                
                # Calculate approximate original size (base64 is ~37% larger)
                base64_size = len(photo_data.split(',')[1]) if ',' in photo_data else 0
                original_size_bytes = base64_size * 0.75
                photo_info["estimated_size_kb"] = round(original_size_bytes / 1024, 1)
            
        return {
            "success": True, 
            "user": user_dict,
            "photo_info": photo_info
        }
    except Exception as error:
        print(f"❌ Profile fetch error: {error}")
        raise HTTPException(status_code=500, detail="Failed to fetch profile")


async def handle_update_profile(
    full_name: str = Form(None),
    phone: str = Form(None),
    profile_photo: UploadFile = File(None),
    current_user: User = Depends(get_current_user)
):
    """Update user profile with optional photo upload"""
    try:
        print(f"📝 Updating profile for user: {current_user.email}")
        
        update_data = {}
        
        # Update text fields if provided
        if full_name is not None and full_name.strip():
            update_data['full_name'] = full_name.strip()
            print(f"📝 Updating full_name: {full_name}")
            
        if phone is not None and phone.strip():
            update_data['phone'] = phone.strip()
            print(f"📝 Updating phone: {phone}")
        
        # Process profile photo if uploaded
        if profile_photo and profile_photo.filename:
            print(f"📷 Processing profile photo: {profile_photo.filename}")
            print(f"📷 File size: {profile_photo.size if hasattr(profile_photo, 'size') else 'unknown'}")
            
            try:
                # Check if file has content
                file_content = await profile_photo.read()
                if not file_content:
                    raise HTTPException(status_code=400, detail="Empty file uploaded")
                
                # Reset file pointer
                await profile_photo.seek(0)
                
                # Process image to base64
                print("📷 Converting image to base64...")
                base64_image = await process_profile_photo(profile_photo)
                update_data['profile_photo'] = base64_image
                print("✅ Profile photo processed successfully")
                
            except HTTPException as e:
                print(f"❌ Photo processing HTTPException: {e.detail}")
                raise e
            except Exception as e:
                print(f"❌ Photo processing Exception: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Photo processing failed: {str(e)}")
        
        # Update user if there's data to update
        if update_data:
            print(f"💾 Saving updates: {list(update_data.keys())}")
            
            # Check if profile_photo data is too large before saving
            if 'profile_photo' in update_data:
                photo_size = len(update_data['profile_photo'])
                photo_size_mb = photo_size / (1024 * 1024)
                print(f"📊 Profile photo base64 size: {photo_size} chars ({photo_size_mb:.2f}MB)")
                
                # Warn about very large images
                if photo_size > 1_000_000:  # 1M characters ≈ 750KB image
                    print(f"⚠️  Large base64 string: {photo_size_mb:.2f}MB")
            
            try:
                # Update user fields
                for key, value in update_data.items():
                    setattr(current_user, key, value)
                
                await current_user.save()
                
            except Exception as db_error:
                error_msg = str(db_error)
                print(f"❌ Database save error: {error_msg}")
                
                # Handle specific database errors
                if "value too long" in error_msg and "character varying(255)" in error_msg:
                    raise HTTPException(
                        status_code=400,
                        detail="Profile photo is too large. Database column needs to be updated to TEXT type. Please contact admin."
                    )
                elif "value too long" in error_msg:
                    raise HTTPException(
                        status_code=400,
                        detail="Profile photo file is too large. Please use a smaller image."
                    )
                else:
                    raise HTTPException(status_code=500, detail=f"Database error: {error_msg}")
            
            print(f"✅ Profile updated successfully for user: {current_user.email}")
            
            # Prepare response data
            user_dict = {
                "id": str(current_user.id),
                "email": current_user.email,
                "full_name": current_user.full_name,
                "phone": current_user.phone,
                "profile_photo": current_user.profile_photo,
                "role": current_user.role,
                "is_verified": current_user.is_verified,
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
                "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None
            }
            
            return {
                "success": True,
                "message": f"Profile updated successfully! Updated: {', '.join(list(update_data.keys()))}",
                "updated_fields": list(update_data.keys()),
                "user": user_dict
            }
        else:
            return {
                "success": False,
                "message": "No data provided for update. You can update any combination of: full_name, phone, profile_photo (all are optional)."
            }
            
    except HTTPException:
        raise
    except Exception as error:
        print(f"❌ Profile update failed: {error}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Failed to update profile"
        )