from fastapi import Response
from datetime import timedelta


def set_token_cookie(response: Response, token: str):
    """
    Set HttpOnly and non-HttpOnly cookies for authentication.
    Equivalent to your setTokenCookie.js
    """
    max_age = 60 * 60 * 24 * 30  

    response.set_cookie(
        domain=".pixbit.me",
        key="token",
        value=token,
        max_age=max_age,
        httponly=True,
        secure=True,  
        samesite="none",
        path="/",
    )

    
def clear_token_cookie(response: Response):
    """
    Clear authentication cookies.
    Equivalent to your clearTokenCookie.js
    """
    response.delete_cookie(
        domain=".pixbit.me",
        key="token",
        path="/",
        samesite="none",   
        httponly=True
    )