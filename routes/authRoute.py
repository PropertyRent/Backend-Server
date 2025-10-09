from fastapi import APIRouter
from controller.userController import (
    handle_signup,
    handle_login,
    handle_logout,
    handle_forgot_password,
    handle_reset_password,
    handle_verify_email,
    handle_resend_verification,
)

router = APIRouter(tags=["Auth"])

router.post("/signup")(handle_signup)
router.post("/login")(handle_login)
router.post("/logout")(handle_logout)

router.post("/forgot-password")(handle_forgot_password)
router.post("/reset-password/{reset_token}")(handle_reset_password)

router.get("/verify-email/{token}")(handle_verify_email)
router.post("/resend-verification")(handle_resend_verification)
