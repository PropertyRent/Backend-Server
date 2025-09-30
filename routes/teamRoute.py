from fastapi import APIRouter, Query, UploadFile, File, Form
from typing import Optional
from controller.teamController import (
    handle_create_team_member,
    handle_update_team_member,
    delete_team_member,
    get_all_team_members,
    get_team_member_by_id
)

router = APIRouter(tags=["Team"])


# === UNIFIED TEAM CRUD OPERATIONS ===
# Single routes that handle both JSON data and file uploads

@router.post("/team", 
    summary="Create team member with optional photo upload"
)
async def create_team_member(
    name: str = Form(...),
    age: int = Form(...),
    email: str = Form(...),
    position_name: str = Form(...),
    description: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None)
):
    """
    Create a new team member with all details and optional photo upload.
    
    - **name**: Team member's full name (required)
    - **age**: Team member's age (required)
    - **email**: Team member's email address (required, must be unique)
    - **position_name**: Job position/title (required)
    - **description**: Brief description or bio (optional)
    - **phone**: Contact phone number (optional)
    - **photo**: Profile photo file (optional)
    
    This unified route handles both basic team member data and optional photo upload in a single request.
    """
    return await handle_create_team_member(
        name=name,
        age=age,
        email=email,
        position_name=position_name,
        description=description,
        phone=phone,
        photo=photo
    )


@router.put("/team/{member_id}",
    summary="Update team member with optional photo upload"
)
async def update_team_member(
    member_id: str,
    name: Optional[str] = Form(None),
    age: Optional[int] = Form(None),
    email: Optional[str] = Form(None),
    position_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None)
):
    """
    Update an existing team member with optional fields and photo upload.
    
    - **member_id**: UUID of the team member to update
    - **name**: Updated full name (optional)
    - **age**: Updated age (optional)
    - **email**: Updated email address (optional, must be unique)
    - **position_name**: Updated job position/title (optional)
    - **description**: Updated description or bio (optional)
    - **phone**: Updated contact phone number (optional)
    - **photo**: New profile photo file (optional)
    
    This unified route handles both basic team member data updates and optional photo upload in a single request.
    Only provided fields will be updated.
    """
    return await handle_update_team_member(
        member_id=member_id,
        name=name,
        age=age,
        email=email,
        position_name=position_name,
        description=description,
        phone=phone,
        photo=photo
    )


# === TEAM MANAGEMENT OPERATIONS ===

@router.delete("/team/{member_id}", 
    summary="Delete a team member"
)
async def delete_team_member_route(member_id: str):
    """Delete a team member by ID"""
    return await delete_team_member(member_id)


@router.get("/team", 
    summary="Get all team members with filtering and pagination"
)
async def get_all_team_members_route(
    limit: int = Query(10, ge=1, le=100, description="Number of team members to return"),
    offset: int = Query(0, ge=0, description="Number of team members to skip"),
    position: Optional[str] = Query(None, description="Filter by position"),
    search: Optional[str] = Query(None, description="Search by name or email")
):
    """Get all team members with optional filtering and pagination"""
    return await get_all_team_members(
        limit=limit,
        offset=offset,
        position=position,
        search=search
    )


@router.get("/team/{member_id}", 
    summary="Get a team member by ID"
)
async def get_team_member_by_id_route(member_id: str):
    """Get a single team member by ID"""
    return await get_team_member_by_id(member_id)