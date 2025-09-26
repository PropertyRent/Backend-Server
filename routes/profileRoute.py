from fastapi import APIRouter, Depends, UploadFile, File
from controller.userController import (
    handle_get_profile,
)

router = APIRouter(prefix="/user", tags=["User"])

router.get("/profile")(handle_get_profile)
