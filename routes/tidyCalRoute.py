from fastapi import APIRouter, Depends, Request, Query
from typing import Optional

from controller.tidyCalController import (
    create_booking_page_for_property,
    get_property_booking_pages,
    get_booking_page_embed_code,
    handle_tidycal_webhook,
    get_tidycal_integration_status,
    get_booking_analytics
)
from schemas.tidyCalSchemas import (
    TidyCalBookingPageCreate,
    TidyCalBookingPageUpdate,
    TidyCalWebhookEvent
)
from authMiddleware.authMiddleware import check_for_authentication_cookie
from authMiddleware.roleMiddleware import require_admin

router = APIRouter(tags=["TidyCal Integration"])

# === ADMIN ROUTES - TidyCal Management ===

@router.post("/admin/tidycal/booking-pages",
    summary="[ADMIN] Create TidyCal booking page for property",
    description="Create a new TidyCal booking page for a specific property",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def create_property_booking_page(
    property_id: str = Query(..., description="Property ID to create booking page for"),
    booking_page_data: TidyCalBookingPageCreate = ...
):
    """
    Create a TidyCal booking page for a specific property.
    
    - **property_id**: UUID of the property
    - **booking_page_data**: Booking page configuration
    
    This creates both a TidyCal booking page and stores the configuration locally.
    """
    return await create_booking_page_for_property(property_id, booking_page_data)

@router.get("/admin/tidycal/booking-pages",
    summary="[ADMIN] Get all TidyCal booking pages",
    description="Get all TidyCal booking pages with optional property filtering",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def get_all_booking_pages(
    property_id: Optional[str] = Query(None, description="Filter by property ID")
):
    """
    Get all TidyCal booking pages with optional property filtering.
    
    - **property_id**: Optional property ID to filter by
    
    Returns all booking pages with property details and statistics.
    """
    return await get_property_booking_pages(property_id)

@router.get("/admin/tidycal/booking-pages/{booking_page_id}/embed",
    summary="[ADMIN] Get booking page embed code",
    description="Get embed code for a specific booking page",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def get_booking_page_embed(
    booking_page_id: str,
    width: Optional[str] = Query("100%", description="Iframe width"),
    height: Optional[str] = Query("600px", description="Iframe height")
):
    """
    Get embed code for a specific booking page.
    
    - **booking_page_id**: UUID of the booking page
    - **width**: Iframe width (default: 100%)
    - **height**: Iframe height (default: 600px)
    
    Returns iframe embed code and styling options.
    """
    return await get_booking_page_embed_code(booking_page_id, width, height)

@router.get("/admin/tidycal/status",
    summary="[ADMIN] Get TidyCal integration status",
    description="Get TidyCal integration status and statistics",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def get_integration_status():
    """
    Get TidyCal integration status and statistics.
    
    Returns configuration status, total booking pages, and booking statistics.
    """
    return await get_tidycal_integration_status()

@router.get("/admin/tidycal/analytics",
    summary="[ADMIN] Get booking analytics",
    description="Get booking analytics and statistics",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def get_booking_analytics_data(
    booking_page_id: Optional[str] = Query(None, description="Filter by booking page ID")
):
    """
    Get booking analytics and statistics.
    
    - **booking_page_id**: Optional booking page ID to filter by
    
    Returns detailed analytics including booking trends, popular times, and status breakdowns.
    """
    return await get_booking_analytics(booking_page_id)

# === PUBLIC ROUTES - Frontend Integration ===

@router.get("/tidycal/booking-pages/{property_id}/embed",
    summary="[PUBLIC] Get property booking page embed",
    description="Get TidyCal booking page embed code for a property"
)
async def get_property_booking_embed(
    property_id: str,
    width: Optional[str] = Query("100%", description="Iframe width"),
    height: Optional[str] = Query("600px", description="Iframe height")
):
    """
    Get TidyCal booking page embed code for a specific property.
    
    - **property_id**: UUID of the property
    - **width**: Iframe width (default: 100%)
    - **height**: Iframe height (default: 600px)
    
    Returns embed code for frontend integration.
    """
    # Get booking page for property
    booking_pages = await get_property_booking_pages(property_id)
    
    if not booking_pages.get("success") or not booking_pages["data"]["booking_pages"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No booking page found for this property")
    
    booking_page = booking_pages["data"]["booking_pages"][0]
    booking_page_id = booking_page["id"]
    
    return await get_booking_page_embed_code(booking_page_id, width, height)

@router.get("/tidycal/properties/{property_id}/booking-url",
    summary="[PUBLIC] Get property booking URL",
    description="Get direct TidyCal booking URL for a property"
)
async def get_property_booking_url(property_id: str):
    """
    Get direct TidyCal booking URL for a property.
    
    - **property_id**: UUID of the property
    
    Returns direct booking URL for external linking.
    """
    booking_pages = await get_property_booking_pages(property_id)
    
    if not booking_pages.get("success") or not booking_pages["data"]["booking_pages"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No booking page found for this property")
    
    booking_page = booking_pages["data"]["booking_pages"][0]
    
    return {
        "success": True,
        "data": {
            "property_id": property_id,
            "property_title": booking_page["property_title"],
            "booking_url": booking_page["booking_url"],
            "page_name": booking_page["page_name"],
            "duration_minutes": booking_page["duration_minutes"]
        }
    }

# === WEBHOOK ENDPOINTS ===

@router.post("/tidycal/webhook",
    summary="[WEBHOOK] TidyCal webhook endpoint",
    description="Webhook endpoint to receive TidyCal events"
)
async def tidycal_webhook_handler(request: Request):
    """
    Webhook endpoint to receive TidyCal events.
    
    This endpoint processes booking events from TidyCal including:
    - booking.created
    - booking.cancelled
    - booking.completed
    - booking.rescheduled
    
    Automatically synchronizes bookings with local database.
    """
    try:
        webhook_data = await request.json()
        return await handle_tidycal_webhook(request, webhook_data)
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Invalid webhook data: {str(e)}")

# === INTEGRATION HELPER ENDPOINTS ===

@router.get("/tidycal/integration-guide",
    summary="[PUBLIC] Get TidyCal integration guide",
    description="Get step-by-step integration guide for frontend developers"
)
async def get_integration_guide():
    """
    Get comprehensive integration guide for frontend developers.
    
    Returns step-by-step instructions for integrating TidyCal booking widgets.
    """
    return {
        "success": True,
        "data": {
            "integration_guide": {
                "overview": "TidyCal integration allows seamless property viewing scheduling",
                "setup_steps": [
                    {
                        "step": 1,
                        "title": "Admin Setup",
                        "description": "Admin creates booking pages for properties via admin panel",
                        "endpoint": "POST /api/admin/tidycal/booking-pages"
                    },
                    {
                        "step": 2,
                        "title": "Get Embed Code", 
                        "description": "Frontend fetches embed code for property",
                        "endpoint": "GET /api/tidycal/booking-pages/{property_id}/embed"
                    },
                    {
                        "step": 3,
                        "title": "Display Widget",
                        "description": "Embed TidyCal widget in property details page",
                        "implementation": "Insert returned iframe code in property page"
                    },
                    {
                        "step": 4,
                        "title": "Handle Bookings",
                        "description": "Bookings are automatically synchronized via webhooks",
                        "note": "No additional frontend action required"
                    }
                ],
                "frontend_examples": {
                    "react": {
                        "component": "TidyCalBookingWidget",
                        "props": ["propertyId", "width", "height"],
                        "example_usage": "const { data } = await fetch(`/api/tidycal/booking-pages/${propertyId}/embed`); return <div dangerouslySetInnerHTML={{ __html: data.embed_code }} />;"
                    },
                    "html": {
                        "approach": "Direct iframe embedding",
                        "example": "<iframe src='booking_url' width='100%' height='600px'></iframe>"
                    }
                },
                "webhook_setup": {
                    "url": "https://your-domain.com/api/tidycal/webhook",
                    "events": ["booking.created", "booking.cancelled", "booking.completed", "booking.rescheduled"],
                    "security": "Webhook signature verification implemented"
                }
            }
        }
    }