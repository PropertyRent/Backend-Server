import os
import ssl
from pydantic import EmailStr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from dotenv import load_dotenv

load_dotenv()  # Load .env

# Email configuration
SMTP_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER", os.getenv("ADMIN_EMAIL"))
EMAIL_PASS = os.getenv("EMAIL_PASS", os.getenv("ADMIN_PASSWORD"))
EMAIL_FROM = os.getenv("EMAIL_FROM", EMAIL_USER)

async def send_email(to_email: EmailStr, subject: str, html_content: str):
    """
    Async email sender using Gmail SMTP with improved error handling.
    """

    if not EMAIL_USER or not EMAIL_PASS:
        print(" Email configuration error: EMAIL_USER or EMAIL_PASS not set")
        raise ValueError("Email credentials not configured in environment")

    print(f" Attempting to send email to: {to_email}")
    print(f" Using SMTP: {SMTP_HOST}:{SMTP_PORT}")
    print(f" From: {EMAIL_FROM}")

    # Build the email
    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(html_content, "html"))

    # Send email with better error handling
    try:
        print(f" Connecting to SMTP server...")
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=True,
            username=EMAIL_USER,
            password=EMAIL_PASS,
            timeout=30,
        )
        print(f" Email sent successfully to: {to_email}")
        return True
    except aiosmtplib.SMTPAuthenticationError as e:
        print(f" SMTP Authentication failed: {e}")
        print(" Make sure you're using an App Password, not your regular Gmail password")
        print(" Generate App Password at: https://myaccount.google.com/apppasswords")
        return False
    except aiosmtplib.SMTPException as e:
        print(f" SMTP Error: {e}")
        return False
    except Exception as e:
        print(f" Email send failed: {e}")
        return False
