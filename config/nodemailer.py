import os
import ssl
from pydantic import EmailStr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from dotenv import load_dotenv

load_dotenv()  # Load .env

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

async def send_email(to_email: EmailStr, subject: str, html_content: str):
    """
    Async email sender using Gmail SMTP (similar to nodemailer.createTransport).
    """

    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        raise ValueError("ADMIN_EMAIL or ADMIN_PASSWORD not configured in environment")

    # Build the email
    msg = MIMEMultipart("alternative")
    msg["From"] = ADMIN_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(html_content, "html"))

    # Send email
    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=True,
            username=ADMIN_EMAIL,
            password=ADMIN_PASSWORD,
            timeout=30,
        )
        return True
    except Exception as e:
        print(f"❌ Email send failed: {e}")
        return False
