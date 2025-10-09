import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
JWT_ALGORITHM = "HS256"


def create_token(user: dict, expires_in: int = 30):
    """
    Create a JWT token with full payload (id, email, role).
    Default expiration = 30 days
    """
    try:
        if not JWT_SECRET:
            raise ValueError("JWT_SECRET is missing in environment variables")

        payload = {
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
            "exp": datetime.utcnow() + timedelta(days=expires_in),
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    except Exception as e:
        print(" Error creating token:", str(e))
        return None



def validate_token(token: str):
    """
    Validate and decode a JWT token.
    Returns decoded payload if valid, otherwise None.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        print(" Token expired")
        return None
    except jwt.InvalidTokenError as e:
        print(" Invalid token:", str(e))
        return None
