from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from ..authService.auth_service import validate_token

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
):
    """
    Dependency that checks for JWT token in cookies or Authorization header.
    Equivalent to Express checkForAuthenticationCookie.js
    """
    token = None

 
    if "token" in request.cookies:
        token = request.cookies.get("token")

    if not token and credentials:
        if credentials.scheme.lower() == "bearer":
            token = credentials.credentials

    if not token:
        raise HTTPException(status_code=401, detail="No token found. Please login.")

    user_payload = validate_token(token)
    if not user_payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    return user_payload
