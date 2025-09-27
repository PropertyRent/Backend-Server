from fastapi import APIRouter, Depends, UploadFile, File, Form
from controller.userController import (
    handle_get_profile,
    handle_update_profile,
    handle_upload_profile_photo,
)

router = APIRouter(prefix="/user", tags=["User"])

router.get("/profile")(handle_get_profile)
router.put("/profile", summary="Update user profile with optional photo")(handle_update_profile)
router.post("/profile/photo", summary="Upload/update profile photo only")(handle_upload_profile_photo)
