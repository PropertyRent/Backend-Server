from fastapi import Response
from datetime import timedelta


def set_token_cookie(response: Response, token: str ):
    """
    Set HttpOnly and non-HttpOnly cookies for authentication.
    Equivalent to your setTokenCookie.js
    """
    max_age = 60 * 60 * 24 * 30  

    # Set HttpOnly token (existing)
    response.set_cookie(
        # domain=".pixbit.me",
        key="token",
        value=token,
        max_age=max_age,
        httponly=True,
        secure=True,  
        samesite="none",
        path="/",
    )

    # Set non-HttpOnly token for JavaScript access
    response.set_cookie(
        # domain=".pixbit.me",
        key="token_middleware",
        value=token,
        max_age=max_age,
        httponly=False,  # Accessible by JavaScript
        secure=True,  
        samesite="none",
        path="/",
    )

    
def clear_token_cookie(response: Response):
    """
    Clear authentication cookies.
    Equivalent to your clearTokenCookie.js
    """
    # Clear HttpOnly token
    response.delete_cookie(
        # domain=".pixbit.me",
        key="token",
        path="/",
        samesite="none",   
        httponly=True
    )
    
    # Clear non-HttpOnly token
    response.delete_cookie(
        # domain=".pixbit.me",
        key="token_middleware",
        path="/",
        samesite="none",   
        httponly=False
    )