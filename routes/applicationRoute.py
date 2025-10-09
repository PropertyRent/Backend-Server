from fastapi import APIRouter, Depends, Request, Query
from typing import Optional

from controller.applicationController import (
    handle_submit_application,
    handle_get_all_applications,
    handle_get_application_by_id,
    handle_admin_reply_to_application,
    handle_update_application_status,
    handle_delete_application
)
from schemas.applicationSchemas import (
    RentalApplicationCreate,
    AdminReplySchema,
    ApplicationStatusEnum
)
from authMiddleware.authMiddleware import check_for_authentication_cookie
from authMiddleware.roleMiddleware import require_admin
from model.applicationModel import ApplicationStatus

router = APIRouter(tags=["Rental Applications"])

# === PUBLIC ROUTES - No login required ===

@router.post("/applications/submit", 
    summary="[PUBLIC] Submit rental application",
    description="Allow users to submit rental application without login required"
)
async def submit_application(application_data: RentalApplicationCreate):
    """Submit a rental application - No login required"""
    return await handle_submit_application(application_data)

# === ADMIN ROUTES - Authentication + Admin Role Required ===

@router.get("/admin/applications",
    summary="[ADMIN] Get all rental applications",
    description="Get all applications for admin review and management",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def get_all_applications_admin(
    status: Optional[str] = Query(None, description="Filter by application status"),
    search: Optional[str] = Query(None, description="Search by name, email, or application ID")
):
    """1) Admin get all applications submitted by users"""
    return await handle_get_all_applications(status, search)

@router.get("/admin/applications/{application_id}",
    summary="[ADMIN] Get application by ID",
    description="Get detailed information about a specific application",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def get_application_by_id_admin(application_id: str):
    """2) Admin get application by id"""
    return await handle_get_application_by_id(application_id)

@router.post("/admin/applications/{application_id}/reply",
    summary="[ADMIN] Reply to application",
    description="Admin reply to application with optional status update and user receives email",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def reply_to_application(request: Request, application_id: str, reply_data: AdminReplySchema):
    """3) Admin reply to application then user receives email"""
    return await handle_admin_reply_to_application(request, application_id, reply_data)

@router.put("/admin/applications/{application_id}/status/reviewed",
    summary="[ADMIN] Mark application as reviewed",
    description="Admin marks application as reviewed",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def mark_application_reviewed(request: Request, application_id: str):
    """4a) Admin marks application as reviewed"""
    return await handle_update_application_status(request, application_id, ApplicationStatus.REVIEWED)

@router.put("/admin/applications/{application_id}/status/approved",
    summary="[ADMIN] Approve application",
    description="Admin approves application",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def approve_application(request: Request, application_id: str):
    """4b) Admin approves application"""
    return await handle_update_application_status(request, application_id, ApplicationStatus.APPROVED)

@router.put("/admin/applications/{application_id}/status/rejected",
    summary="[ADMIN] Reject application",
    description="Admin rejects application", 
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def reject_application(request: Request, application_id: str):
    """4c) Admin rejects application"""
    return await handle_update_application_status(request, application_id, ApplicationStatus.REJECTED)

@router.put("/admin/applications/{application_id}/status/completed",
    summary="[ADMIN] Mark application as completed",
    description="Admin marks application as completed",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def complete_application(request: Request, application_id: str):
    """4d) Admin marks application as completed"""
    return await handle_update_application_status(request, application_id, ApplicationStatus.COMPLETED)

@router.delete("/admin/applications/{application_id}",
    summary="[ADMIN] Delete application",
    description="Admin can permanently delete an application",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def delete_application(request: Request, application_id: str):
    """5) Admin can delete application permanently"""
    return await handle_delete_application(request, application_id)