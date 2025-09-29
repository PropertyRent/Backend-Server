from fastapi import APIRouter, Depends, Request, Query
from typing import Optional

from controller.scheduleMeetingController import (
    handle_schedule_meeting,
    handle_get_user_meetings,
    handle_get_all_meetings_admin,
    handle_update_meeting_status,
    handle_get_meeting_by_id,
    handle_delete_meeting,
    handle_get_meeting_stats,
    handle_cancel_meeting
)
from schemas.scheduleMeetingSchemas import (
    ScheduleMeetingCreate,
    ScheduleMeetingUpdate
)
from authMiddleware.authMiddleware import check_for_authentication_cookie
from authMiddleware.roleMiddleware import require_admin

router = APIRouter(tags=["Schedule Meetings"])

# Public/User routes
@router.post("/meetings/schedule", 
    summary="Schedule a meeting for property viewing",
    description="Allow users (logged in or guest) to schedule a meeting to view a property"
)
async def schedule_meeting(request: Request, meeting_data: ScheduleMeetingCreate):
    """Schedule a meeting for property viewing"""
    return await handle_schedule_meeting(request, meeting_data)

@router.get("/user/meetings",
    summary="Get user's scheduled meetings",
    description="Get all meetings scheduled by the current logged-in user",
    dependencies=[Depends(check_for_authentication_cookie)]
)
async def get_user_meetings(
    request: Request,
    status: Optional[str] = Query(None, description="Filter by meeting status (pending, approved, rejected, completed, cancelled)")
):
    """Get meetings for the current user"""
    return await handle_get_user_meetings(request, status)

@router.put("/user/meetings/{meeting_id}/cancel",
    summary="Cancel user's meeting",
    description="Allow user to cancel their own meeting",
    dependencies=[Depends(check_for_authentication_cookie)]
)
async def cancel_user_meeting(request: Request, meeting_id: str):
    """Cancel user's own meeting"""
    return await handle_cancel_meeting(request, meeting_id)

@router.get("/meetings/{meeting_id}",
    summary="Get meeting details",
    description="Get detailed information about a specific meeting"
)
async def get_meeting_by_id(meeting_id: str):
    """Get meeting details by ID"""
    return await handle_get_meeting_by_id(meeting_id)

# Admin routes
@router.get("/admin/meetings",
    summary="[ADMIN] Get all meetings",
    description="Get all meetings for admin review and management",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def get_all_meetings_admin(
    status: Optional[str] = Query(None, description="Filter by meeting status"),
    property_id: Optional[str] = Query(None, description="Filter by property ID")
):
    """Get all meetings for admin"""
    return await handle_get_all_meetings_admin(status, property_id)

@router.put("/admin/meetings/{meeting_id}",
    summary="[ADMIN] Update meeting status",
    description="Update meeting status, add admin notes, approve/reject meetings",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def update_meeting_status(request: Request, meeting_id: str, update_data: ScheduleMeetingUpdate):
    """Update meeting status (admin only)"""
    return await handle_update_meeting_status(request, meeting_id, update_data)

@router.delete("/admin/meetings/{meeting_id}",
    summary="[ADMIN] Delete meeting",
    description="Delete a meeting request",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def delete_meeting(meeting_id: str):
    """Delete meeting (admin only)"""
    return await handle_delete_meeting(meeting_id)

@router.get("/admin/meetings/stats",
    summary="[ADMIN] Get meeting statistics",
    description="Get meeting statistics for admin dashboard",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def get_meeting_stats():
    """Get meeting statistics"""
    return await handle_get_meeting_stats()

# Specific admin actions
@router.put("/admin/meetings/{meeting_id}/approve",
    summary="[ADMIN] Approve meeting",
    description="Approve a pending meeting request",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def approve_meeting(request: Request, meeting_id: str, admin_notes: Optional[str] = None):
    """Approve a meeting"""
    update_data = ScheduleMeetingUpdate(status="approved", admin_notes=admin_notes)
    return await handle_update_meeting_status(request, meeting_id, update_data)

@router.put("/admin/meetings/{meeting_id}/reject",
    summary="[ADMIN] Reject meeting",
    description="Reject a pending meeting request",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def reject_meeting(request: Request, meeting_id: str, admin_notes: Optional[str] = None):
    """Reject a meeting"""
    update_data = ScheduleMeetingUpdate(status="rejected", admin_notes=admin_notes)
    return await handle_update_meeting_status(request, meeting_id, update_data)

@router.put("/admin/meetings/{meeting_id}/complete",
    summary="[ADMIN] Mark meeting as completed",
    description="Mark a meeting as completed after it has taken place",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def complete_meeting(request: Request, meeting_id: str, admin_notes: Optional[str] = None):
    """Mark meeting as completed"""
    update_data = ScheduleMeetingUpdate(status="completed", admin_notes=admin_notes)
    return await handle_update_meeting_status(request, meeting_id, update_data)