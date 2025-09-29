from fastapi import APIRouter, Depends, UploadFile, File, Form, Request
from authMiddleware.authMiddleware import check_for_authentication_cookie
from controller.userController import (
    handle_get_profile,
    handle_update_profile,
)

router = APIRouter(tags=["User"])

# Profile routes without additional dependencies since main.py handles it
router.get("/profile", summary="Get current user profile")(handle_get_profile)
router.put("/profile", summary="Update user profile with optional photo")(handle_update_profile)
