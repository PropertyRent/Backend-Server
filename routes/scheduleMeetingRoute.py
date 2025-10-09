from fastapi import APIRouter, Depends, Request, Query
from typing import Optional

from controller.scheduleMeetingController import (
    handle_schedule_meeting,
    handle_get_all_meetings_admin,
    handle_get_meeting_by_id,
    handle_admin_reply_to_meeting,
    handle_admin_complete_meeting,
    handle_admin_delete_meeting
)
from schemas.scheduleMeetingSchemas import (
    ScheduleMeetingCreate,
    AdminReplySchema
)
from authMiddleware.authMiddleware import check_for_authentication_cookie
from authMiddleware.roleMiddleware import require_admin

router = APIRouter(tags=["Schedule Meetings"])

# === PUBLIC ROUTES - No login required ===
@router.post("/meetings/schedule", 
    summary="[PUBLIC] Schedule a meeting for property viewing",
    description="Allow users (no login required) to schedule a meeting to view a property"
)
async def schedule_meeting(meeting_data: ScheduleMeetingCreate):
    """Schedule a meeting for property viewing - No login required"""
    return await handle_schedule_meeting(None, meeting_data)

# === ADMIN ROUTES - Authentication + Admin Role Required ===

@router.get("/admin/meetings",
    summary="[ADMIN] Get all meetings scheduled by users",
    description="Get all meetings for admin review and management",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def get_all_meetings_admin(
    status: Optional[str] = Query(None, description="Filter by meeting status"),
    property_id: Optional[str] = Query(None, description="Filter by property ID")
):
    """1) Admin get all meetings scheduled by users"""
    return await handle_get_all_meetings_admin(status, property_id)

@router.get("/admin/meetings/{meeting_id}",
    summary="[ADMIN] Get meeting by ID",
    description="Get detailed information about a specific meeting",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def get_meeting_by_id_admin(meeting_id: str):
    """2) Admin get meeting by id"""
    return await handle_get_meeting_by_id(meeting_id)

@router.post("/admin/meetings/{meeting_id}/reply",
    summary="[ADMIN] Reply to meeting request",
    description="Admin gives reply to meeting and user receives email",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def reply_to_meeting(request: Request, meeting_id: str, reply_data: AdminReplySchema):
    """3) Admin give reply to that meeting then user receive mail"""
    return await handle_admin_reply_to_meeting(request, meeting_id, reply_data)


@router.put("/admin/meetings/{meeting_id}/complete",
    summary="[ADMIN] Mark meeting as completed",
    description="Admin marks meeting as completed",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def complete_meeting(request: Request, meeting_id: str):
    """5) Admin marks as completed that meeting"""
    return await handle_admin_complete_meeting(request, meeting_id)

@router.delete("/admin/meetings/{meeting_id}",
    summary="[ADMIN] Delete meeting",
    description="Admin can permanently delete a meeting request",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def delete_meeting(request: Request, meeting_id: str):
    """6) Admin can delete meeting permanently"""
    return await handle_admin_delete_meeting(request, meeting_id)