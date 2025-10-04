import os
import httpx
from fastapi import APIRouter, HTTPException, Query,Depends
from typing import Optional
from authMiddleware.authMiddleware import check_for_authentication_cookie
from authMiddleware.roleMiddleware import require_admin

router = APIRouter(tags=["TidyCal Proxy"])

# Get TidyCal API key from environment
TIDYCAL_API_KEY = os.getenv("TIDYCAL_API_KEY")
TIDYCAL_BASE_URL = "https://tidycal.com/api"

@router.get("/tidycal/booking-types", dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)])
async def get_tidycal_booking_types(
    page: Optional[int] = Query(1, description="Page number"),
    per_page: Optional[int] = Query(30, description="Number of items per page")
):
    """
    Proxy endpoint to fetch booking types from TidyCal API
    Only accessible by authenticated admin users
    Frontend calls this route which then calls TidyCal API and returns the data
    """

    if not TIDYCAL_API_KEY:
        raise HTTPException(status_code=500, detail="TidyCal API key not configured")
    
    # Prepare headers for TidyCal API
    headers = {
        "Authorization": f"Bearer {TIDYCAL_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Prepare query parameters
    params = {
        "page": page,
        "per_page": per_page
    }
    
    # Build TidyCal API URL
    url = f"{TIDYCAL_BASE_URL}/booking-types"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            # Return the exact response from TidyCal API
            return response.json()
            
    except httpx.HTTPStatusError as e:
        # Handle HTTP errors from TidyCal API
        error_detail = f"TidyCal API error: {e.response.status_code}"
        try:
            error_body = e.response.json()
            if "message" in error_body:
                error_detail += f" - {error_body['message']}"
        except:
            error_detail += f" - {e.response.text}"
        
        raise HTTPException(status_code=e.response.status_code, detail=error_detail)
        
    except httpx.RequestError as e:
        # Handle network/connection errors
        raise HTTPException(status_code=500, detail=f"Failed to connect to TidyCal API: {str(e)}")
    
    except Exception as e:
        # Handle any other errors
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")