from fastapi import Depends, HTTPException, status
from typing import List, Dict
from .auth_dependency import get_current_user


def authorize_roles(roles: List[str]):
    """
    Dependency factory to restrict routes to specific roles.
    Equivalent to Express authorizeRoles.js
    """

    async def role_checker(current_user: Dict = Depends(get_current_user)):
        if current_user.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized Access! You are not authorized to access this resource.",
            )
        return current_user  
    return role_checker
