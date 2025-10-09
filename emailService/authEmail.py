import os
from config.nodemailer import send_email


FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "no-reply@example.com")


async def send_forget_password_email(to_email: str, reset_password_link: str):
    subject = "Reset Your Password - Property-Rent"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: #1a39ffff;">Hello</h2>
        <p>You recently requested to reset your password for your Property-Rent account.</p>
        <p>Please click the button below to reset your password:</p>
        <a href="{reset_password_link}" style="
            display: inline-block;
            padding: 10px 20px;
            margin: 10px 0;
            font-size: 16px;
            color: white;
            background-color: #4733fcff;
            text-decoration: none;
            border-radius: 5px;
        ">Reset Password</a>
        <p>If you didn’t request this, you can safely ignore this email.</p>
        <p style="margin-top: 20px;">Thanks,<br/>The Property-Rent Team</p>
      </div>
    </div>
    """
    return await send_email(to_email, subject, html_content)


async def send_verification_email(to_email: str, verify_url: str):
    subject = "Verify Your Email - Property-Rent"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: #1a39ffff;">Welcome to Property-Rent</h2>
        <p>Thanks for signing up! Please verify your email address to activate your account.</p>
        <p>Click the button below to verify your email:</p>
        <a href="{verify_url}" style="
            display: inline-block;
            padding: 10px 20px;
            margin: 10px 0;
            font-size: 16px;
            color: white;
            background-color: #4733fcff;
            text-decoration: none;
            border-radius: 5px;
        ">Verify Email</a>
        <p>If you didn’t create this account, you can safely ignore this email.</p>
        <p style="margin-top: 20px;">Thanks,<br/>The Property-Rent Team</p>
      </div>
    </div>
    """
    return await send_email(to_email, subject, html_content)


async def send_congrats_email(to_email: str):
    subject = "Email Verified Successfully - Property-Rent"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: #1a39ffff;">Congratulations</h2>
        <p>Your email has been successfully verified.</p>
        <p>You can now log in and start using Property-Rent with full access.</p>
        <a href="{FRONTEND_URL}/login" style="
            display: inline-block;
            padding: 10px 20px;
            margin: 10px 0;
            font-size: 16px;
            color: white;
            background-color: #4733fcff;
            text-decoration: none;
            border-radius: 5px;
        ">Go to Login</a>
        <p style="margin-top: 20px;">Thanks,<br/>The Property-Rent Team</p>
      </div>
    </div>
    """
    return await send_email(to_email, subject, html_content)


async def send_password_reset_success_email(to_email: str):
    subject = "Password Reset Successful - AI-MVP-Local"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: #1a39ffff;">Password Reset Successful</h2>
        <p>Your password has been successfully reset.</p>
        <p>If you did not perform this action, please contact support immediately.</p>
        <a href="{FRONTEND_URL}/login" style="
            display: inline-block;
            padding: 10px 20px;
            margin: 10px 0;
            font-size: 16px;
            color: white;
            background-color: #4733fcff;
            text-decoration: none;
            border-radius: 5px;
        ">Login Now</a>
        <p style="margin-top: 20px;">Stay secure,<br/>The Property-Rent Team</p>
      </div>
    </div>
    """
    return await send_email(to_email, subject, html_content)


async def send_password_change_email(to_email: str):
    subject = "Your Password Was Changed - Property-Rent"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: #1a39ffff;">Password Changed Successfully</h2>
        <p>We wanted to let you know that your password has been successfully updated.</p>
        <p>If you made this change, no further action is required.</p>
        <p style="color: red; font-weight: bold;">If you did not make this change, please reset your password immediately and contact support.</p>
        <p style="margin-top: 20px;">Thanks,<br/>The Property-Rent Team</p>
      </div>
    </div>
    """
    return await send_email(to_email, subject, html_content)


async def send_update_profile_email(to_email: str):
    subject = "Your Profile is successfully Updated - Property-Rent"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
      <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px;">
        <h2 style="color: #1a39ffff;">Profile Updated Successfully</h2>
        <p>We wanted to let you know that your profile has been successfully updated.</p>
        <p>If you made this change, no further action is required.</p>
        <p style="color: red; font-weight: bold;">If you did not make this change, please reset your password immediately and contact support.</p>
        <p style="margin-top: 20px;">Thanks,<br/>The Property-Rent Team</p>
      </div>
    </div>
    """
    return await send_email(to_email, subject, html_content)
