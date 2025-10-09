from fastapi import APIRouter, Query, UploadFile, File, Form, Depends
from typing import Optional
from controller.noticeController import (
    handle_create_notice,
    handle_update_notice,
    delete_notice,
    get_all_notices,
    get_notice_by_id,
    get_active_notices,
    download_notice_file,
    toggle_notice_active,
    set_notice_active,
    debug_notice_file
)
from authMiddleware.authMiddleware import check_for_authentication_cookie
from authMiddleware.roleMiddleware import require_admin

router = APIRouter(tags=["Notices"])


# === UNIFIED NOTICE CRUD OPERATIONS ===
# Single routes that handle both JSON data and file uploads

@router.post("/admin/notices", 
    summary="[ADMIN] Create notice with optional file upload",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def create_notice(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    notice_file: Optional[UploadFile] = File(None)
):
    """
    Create a new notice with all details and optional file upload.
    
    - **title**: Notice title (required)
    - **description**: Notice description or content (optional)
    - **notice_file**: Notice attachment file - supports PDF, DOCX, DOC, and image files (optional)
    
    This unified route handles both basic notice data and optional file upload in a single request.
    Supported file formats: PDF, DOCX, DOC, JPG, JPEG, PNG, GIF, WEBP
    """
    return await handle_create_notice(
        title=title,
        description=description,
        notice_file=notice_file
    )


@router.put("/admin/notices/{notice_id}",
    summary="[ADMIN] Update notice with optional file upload",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def update_notice(
    notice_id: str,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    notice_file: Optional[UploadFile] = File(None)
):
    """
    Update an existing notice with optional fields and file upload.
    
    - **notice_id**: UUID of the notice to update
    - **title**: Updated notice title (optional)
    - **description**: Updated notice description or content (optional)
    - **notice_file**: New notice attachment file - supports PDF, DOCX, DOC, and image files (optional)
    
    This unified route handles both basic notice data updates and optional file upload in a single request.
    Only provided fields will be updated.
    Supported file formats: PDF, DOCX, DOC, JPG, JPEG, PNG, GIF, WEBP
    """
    return await handle_update_notice(
        notice_id=notice_id,
        title=title,
        description=description,
        notice_file=notice_file
    )


# === NOTICE MANAGEMENT OPERATIONS ===

@router.delete("/admin/notices/{notice_id}", 
    summary="[ADMIN] Delete a notice",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def delete_notice_route(notice_id: str):
    """Delete a notice by ID"""
    return await delete_notice(notice_id)


@router.get("/admin/notices", 
    summary="[ADMIN] Get all notices with filtering and pagination",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def get_all_notices_route(
    limit: int = Query(10, ge=1, le=100, description="Number of notices to return"),
    offset: int = Query(0, ge=0, description="Number of notices to skip"),
    search: Optional[str] = Query(None, description="Search by title or description")
):
    """
    Get all notices with optional filtering and pagination.
    
    - **limit**: Number of notices to return (1-100, default: 10)
    - **offset**: Number of notices to skip for pagination (default: 0)
    - **search**: Search term to filter notices by title or description (optional)
    
    Returns notices ordered by creation date (newest first).
    """
    return await get_all_notices(
        limit=limit,
        offset=offset,
        search=search
    )


@router.get("/admin/notices/{notice_id}", 
    summary="[ADMIN] Get a notice by ID",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def get_notice_by_id_route(notice_id: str):
    """
    Get a single notice by ID.
    
    **ADMIN ONLY** - Requires authentication and admin role.
    
    - **notice_id**: UUID of the notice to retrieve
    
    Returns complete notice details including file attachment if present.
    """
    return await get_notice_by_id(notice_id)


@router.patch("/admin/notices/{notice_id}/toggle-active", 
    summary="[ADMIN] Toggle notice active status",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def toggle_notice_active_status(notice_id: str):
    """
    Toggle the active status of a notice (true to false or false to true).
    
    **ADMIN ONLY** - Requires authentication and admin role.
    
    - **notice_id**: UUID of the notice to toggle
    
    This will automatically switch:
    - Active notice (is_active=true) → Inactive (is_active=false)
    - Inactive notice (is_active=false) → Active (is_active=true)
    
    Returns the updated notice with new status.
    """
    return await toggle_notice_active(notice_id)


@router.put("/admin/notices/{notice_id}/set-active", 
    summary="[ADMIN] Set notice active status",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def set_notice_active_status(notice_id: str, is_active: bool = Form(...)):
    """
    Set the active status of a notice to a specific value.
    
    **ADMIN ONLY** - Requires authentication and admin role.
    
    - **notice_id**: UUID of the notice to update
    - **is_active**: Set to true to make notice active, false to make inactive
    
    Returns the updated notice with new status.
    """
    return await set_notice_active(notice_id, is_active)


# === PUBLIC NOTICE ROUTES ===

@router.get("/public/notices/active", 
    summary="[PUBLIC] Get active notices only"
)
async def get_active_notices_route(
    limit: int = Query(10, ge=1, le=100, description="Number of active notices to return"),
    offset: int = Query(0, ge=0, description="Number of notices to skip"),
    search: Optional[str] = Query(None, description="Search by title or description")
):
    """
    Get active notices with optional filtering and pagination.
    
    **PUBLIC ROUTE** - No authentication required.
    
    - **limit**: Number of active notices to return (1-100, default: 10)
    - **offset**: Number of notices to skip for pagination (default: 0)
    - **search**: Search term to filter notices by title or description (optional)
    
    Returns only notices that are marked as active, ordered by creation date (newest first).
    """
    return await get_active_notices(
        limit=limit,
        offset=offset,
        search=search
    )


# === FILE DOWNLOAD ROUTES ===

@router.get("/notices/{notice_id}/download",
    summary="[PUBLIC] Download notice file",
    description="Download attached file from a notice. Accessible to both admin and public users."
)
async def download_notice_file_public(notice_id: str):
    """
    Download the file attached to a specific notice.
    
    - **notice_id**: UUID of the notice
    
    Returns the file with proper headers for download. Supports PDF, DOCX, DOC, and image files.
    """
    return await download_notice_file(notice_id)


@router.get("/admin/notices/{notice_id}/download",
    summary="[ADMIN] Download notice file",
    description="Admin endpoint to download attached file from any notice.",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def download_notice_file_admin(notice_id: str):
    """
    Admin endpoint to download the file attached to a specific notice.
    
    - **notice_id**: UUID of the notice
    
    Returns the file with proper headers for download. Supports PDF, DOCX, DOC, and image files.
    """
    return await download_notice_file(notice_id)