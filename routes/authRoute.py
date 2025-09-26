from fastapi import APIRouter
from controller.userController import userAuthController as auth

router = APIRouter(prefix="/auth", tags=["Auth"])

router.post("/signup")(auth.handle_signup)
router.post("/login")(auth.handle_login)
router.post("/logout")(auth.handle_logout)

router.post("/forgot-password")(auth.handle_forgot_password)
router.post("/reset-password/{reset_token}")(auth.handle_reset_password)

router.get("/verify-email/{token}")(auth.handle_verify_email)
router.post("/resend-verification")(auth.handle_resend_verification)
