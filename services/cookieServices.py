from fastapi import Response
from datetime import timedelta


def set_token_cookie(response: Response, token: str, middleware_token: str):
    """
    Set HttpOnly and non-HttpOnly cookies for authentication.
    Equivalent to your setTokenCookie.js
    """
    max_age = 60 * 60 * 24 * 30  # 30 days in seconds

    # Secure, HttpOnly cookie for main token
    response.set_cookie(
        key="token",
        value=token,
        max_age=max_age,
        httponly=True,
        secure=False,   # change to True in production (HTTPS)
        samesite="lax",
        path="/",
    )

    # Non-HttpOnly cookie for middleware usage
    response.set_cookie(
        key="token_middleware",
        value=middleware_token,
        max_age=max_age,
        httponly=False,
        secure=False,   # change to True in production (HTTPS)
        samesite="lax",
        path="/",
    )


def clear_token_cookie(response: Response):
    """
    Clear authentication cookies.
    Equivalent to your clearTokenCookie.js
    """
    response.delete_cookie(
        key="token",
        path="/",
        samesite="none",   # matches your Node.js config
        httponly=True
    )

    response.delete_cookie(
        key="token_middleware",
        path="/",
        samesite="lax",
        httponly=False
    )
