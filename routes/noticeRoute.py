from fastapi import APIRouter, Query, UploadFile, File, Form
from typing import Optional
from controller.noticeController import (
    handle_create_notice,
    handle_update_notice,
    delete_notice,
    get_all_notices,
    get_notice_by_id
)

router = APIRouter(tags=["Notices"])


# === UNIFIED NOTICE CRUD OPERATIONS ===
# Single routes that handle both JSON data and file uploads

@router.post("/notices", 
    summary="Create notice with optional file upload"
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


@router.put("/notices/{notice_id}",
    summary="Update notice with optional file upload"
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

@router.delete("/notices/{notice_id}", 
    summary="Delete a notice"
)
async def delete_notice_route(notice_id: str):
    """Delete a notice by ID"""
    return await delete_notice(notice_id)


@router.get("/notices", 
    summary="Get all notices with filtering and pagination"
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


@router.get("/notices/{notice_id}", 
    summary="Get a notice by ID"
)
async def get_notice_by_id_route(notice_id: str):
    """
    Get a single notice by ID.
    
    - **notice_id**: UUID of the notice to retrieve
    
    Returns complete notice details including file attachment if present.
    """
    return await get_notice_by_id(notice_id)