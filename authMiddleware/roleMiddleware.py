from fastapi import Depends, HTTPException, status
from typing import List, Dict
from .authMiddleware import check_for_authentication_cookie


def authorize_roles(roles: List[str]):
    """
    Dependency factory to restrict routes to specific roles.
    Equivalent to Express authorizeRoles.js
    """
    
    async def role_checker(current_user: Dict = Depends(check_for_authentication_cookie)):
        if current_user.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized Access! You are not authorized to access this resource.",
            )
        return current_user  
    return role_checker


# Convenience function for admin-only routes
def require_admin():
    """Convenience function for admin-only routes"""
    return authorize_roles(["admin"])
