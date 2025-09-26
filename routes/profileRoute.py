from fastapi import APIRouter, Depends, UploadFile, File
from controller.userController import userProfileController as profile

router = APIRouter(prefix="/user", tags=["User"])

router.get("/profile")(profile.handle_get_profile)

@router.patch("/profile")
async def update_profile(
    profilePhoto: UploadFile = File(None),
    result=Depends(profile.handle_update_profile),
):
    return await result(profilePhoto)

router.post("/change-password")(profile.handle_change_password)
