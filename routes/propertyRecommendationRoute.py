from fastapi import APIRouter, Query, Form
from typing import Optional
from controller.propertyRecommendationController import (
    create_property_recommendation_from_screening,
    get_recommendations_by_email,
    get_recommendation_by_id,
    update_recommendation_status,
    get_all_recommendations_admin,
    send_recommendation_email
)

router = APIRouter(tags=["Property Recommendations"])


# === PROPERTY RECOMMENDATION GENERATION ===

@router.post("/recommendations/generate/{screening_id}",
    summary="Generate property recommendations from screening questionnaire"
)
async def generate_recommendations(screening_id: str):
    """
    Generate automated property recommendations based on screening questionnaire responses.
    
    - **screening_id**: UUID of the completed screening questionnaire
    
    This endpoint analyzes the user's screening responses and finds matching properties based on:
    - Budget requirements
    - Location preferences  
    - Bedroom/bathroom needs
    - Property type preferences
    - Move-in date requirements
    
    Returns a list of recommended properties with match scores and reasons.
    """
    return await create_property_recommendation_from_screening(screening_id)


# === USER RECOMMENDATION ACCESS ===

@router.get("/recommendations/user/{email}",
    summary="Get recommendations by user email"
)
async def get_user_recommendations(email: str):
    """
    Get all property recommendations for a specific user by email.
    
    - **email**: User's email address
    
    Returns all recommendations created for this user, including status and preview of properties.
    """
    return await get_recommendations_by_email(email)


@router.get("/recommendations/{recommendation_id}",
    summary="Get detailed recommendation by ID"
)
async def get_recommendation_details(recommendation_id: str):
    """
    Get detailed information about a specific recommendation.
    
    - **recommendation_id**: UUID of the recommendation
    
    Returns complete recommendation details including all matching properties, criteria, and status.
    """
    return await get_recommendation_by_id(recommendation_id)


# === USER RESPONSE TRACKING ===

@router.put("/recommendations/{recommendation_id}/respond",
    summary="Update user response to recommendation"
)
async def respond_to_recommendation(
    recommendation_id: str,
    response: str = Form(...),  # interested, not_interested, need_more_info
    status: str = Form("viewed")  # viewed, interested, rejected
):
    """
    Record user's response to property recommendations.
    
    - **recommendation_id**: UUID of the recommendation
    - **response**: User's response (interested, not_interested, need_more_info)
    - **status**: Updated status (viewed, interested, rejected)
    
    This tracks user engagement with recommendations for analytics and follow-up.
    """
    return await update_recommendation_status(
        recommendation_id=recommendation_id,
        status=status,
        user_response=response
    )


# === ADMIN RECOMMENDATION MANAGEMENT ===

@router.get("/admin/recommendations",
    summary="[ADMIN] Get all recommendations with filtering"
)
async def get_all_recommendations_for_admin(
    limit: int = Query(20, ge=1, le=100, description="Number of recommendations to return"),
    offset: int = Query(0, ge=0, description="Number of recommendations to skip"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority level")
):
    """
    Get all property recommendations for admin management.
    
    - **limit**: Number of recommendations to return (1-100, default: 20)
    - **offset**: Number of recommendations to skip for pagination (default: 0)
    - **status**: Filter by status (pending, sent, viewed, interested, rejected)
    - **priority**: Filter by priority level (high, normal, low)
    
    Returns paginated list of all recommendations with admin-relevant information.
    """
    return await get_all_recommendations_admin(
        limit=limit,
        offset=offset,
        status=status,
        priority=priority
    )


@router.put("/admin/recommendations/{recommendation_id}/review",
    summary="[ADMIN] Mark recommendation as reviewed"
)
async def mark_recommendation_reviewed(
    recommendation_id: str,
    admin_notes: Optional[str] = Form(None),
    priority_level: str = Form("normal")
):
    """
    Mark a recommendation as reviewed by admin with optional notes.
    
    - **recommendation_id**: UUID of the recommendation
    - **admin_notes**: Optional admin notes about the recommendation
    - **priority_level**: Priority level (high, normal, low)
    
    This helps track which recommendations have been reviewed by staff.
    """
    # This would update admin_reviewed, admin_notes, and priority_level
    # Implementation would be similar to update_recommendation_status
    return await update_recommendation_status(
        recommendation_id=recommendation_id,
        status="reviewed"
    )


# === EMAIL NOTIFICATIONS ===

@router.post("/recommendations/{recommendation_id}/send-email",
    summary="Send property recommendations via email"
)
async def send_recommendation_email_route(recommendation_id: str):
    """
    Send property recommendations to user via email.
    
    - **recommendation_id**: UUID of the recommendation to send
    
    Sends beautifully formatted email with property cards, match scores,
    and response tracking links. Also notifies admin of the sent recommendation.
    """
    return await send_recommendation_email(recommendation_id)