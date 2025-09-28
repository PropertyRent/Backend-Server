import uuid
from typing import List, Optional
from fastapi import HTTPException, Query, UploadFile, File, Form
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_200_OK,
    HTTP_201_CREATED
)
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.transactions import in_transaction

from model.teamModel import Team
from schemas.teamSchemas import TeamCreate, TeamUpdate, TeamResponse
from config.fileUpload import process_profile_photo


async def add_team_member(team_data: TeamCreate):
    """Create a new team member"""
    try:
        print(f" Creating new team member: {team_data.name}")
        
        # Check if email already exists
        existing_member = await Team.filter(email=team_data.email).first()
        if existing_member:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Create the team member
        new_member = await Team.create(**team_data.dict())
        print(f" Team member created with ID: {new_member.id}")
        
        return JSONResponse(
            status_code=HTTP_201_CREATED,
            content={
                "success": True,
                "message": "Team member created successfully",
                "data": {
                    "id": str(new_member.id),
                    "name": new_member.name,
                    "age": new_member.age,
                    "email": new_member.email,
                    "photo": new_member.photo,
                    "description": new_member.description,
                    "phone": new_member.phone,
                    "position_name": new_member.position_name,
                    "created_at": new_member.created_at.isoformat(),
                    "updated_at": new_member.updated_at.isoformat()
                }
            }
        )
    except HTTPException:
        raise
    except IntegrityError as e:
        print(f" Team member creation failed - integrity error: {e}")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Team member creation failed due to data integrity issues"
        )
    except Exception as e:
        print(f" Team member creation failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create team member"
        )


async def add_team_member_with_photo(
    name: str = Form(...),
    age: int = Form(...),
    email: str = Form(...),
    position_name: str = Form(...),
    description: str = Form(None),
    phone: str = Form(None),
    photo: UploadFile = File(None)
):
    """Create a new team member with photo upload"""
    try:
        print(f" Creating new team member with photo: {name}")
        
        # Check if email already exists
        existing_member = await Team.filter(email=email).first()
        if existing_member:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Process photo if provided
        photo_base64 = None
        if photo:
            photo_base64 = await process_profile_photo(photo)
        
        # Create the team member
        new_member = await Team.create(
            name=name,
            age=age,
            email=email,
            position_name=position_name,
            description=description,
            phone=phone,
            photo=photo_base64
        )
        
        print(f" Team member created with ID: {new_member.id}")
        
        return JSONResponse(
            status_code=HTTP_201_CREATED,
            content={
                "success": True,
                "message": "Team member created successfully",
                "data": {
                    "id": str(new_member.id),
                    "name": new_member.name,
                    "age": new_member.age,
                    "email": new_member.email,
                    "photo": new_member.photo,
                    "description": new_member.description,
                    "phone": new_member.phone,
                    "position_name": new_member.position_name,
                    "created_at": new_member.created_at.isoformat(),
                    "updated_at": new_member.updated_at.isoformat()
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f" Team member creation failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create team member"
        )


async def update_team_member(member_id: str, team_data: TeamUpdate):
    """Update an existing team member"""
    try:
        # Validate UUID
        try:
            member_uuid = uuid.UUID(member_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid team member ID format"
            )
        
        # Check if member exists
        member_obj = await Team.get_or_none(id=member_uuid)
        if not member_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Team member not found"
            )
        
        # Update only provided fields
        update_data = team_data.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Check if email is being updated and if it conflicts
        if 'email' in update_data:
            existing_member = await Team.filter(email=update_data['email']).exclude(id=member_uuid).first()
            if existing_member:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
        
        print(f" Updating team member {member_id} with data: {update_data}")
        
        # Update the member
        await member_obj.update_from_dict(update_data)
        await member_obj.save()
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": "Team member updated successfully",
                "data": {
                    "id": str(member_obj.id),
                    "name": member_obj.name,
                    "age": member_obj.age,
                    "email": member_obj.email,
                    "photo": member_obj.photo,
                    "description": member_obj.description,
                    "phone": member_obj.phone,
                    "position_name": member_obj.position_name,
                    "created_at": member_obj.created_at.isoformat(),
                    "updated_at": member_obj.updated_at.isoformat()
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f" Team member update failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update team member"
        )


async def update_team_member_with_photo(
    member_id: str,
    name: str = Form(None),
    age: int = Form(None),
    email: str = Form(None),
    position_name: str = Form(None),
    description: str = Form(None),
    phone: str = Form(None),
    photo: UploadFile = File(None)
):
    """Update team member with optional photo upload"""
    try:
        # Validate UUID
        try:
            member_uuid = uuid.UUID(member_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid team member ID format"
            )
        
        # Check if member exists
        member_obj = await Team.get_or_none(id=member_uuid)
        if not member_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Team member not found"
            )
        
        # Build update data
        update_data = {}
        if name is not None:
            update_data['name'] = name
        if age is not None:
            update_data['age'] = age
        if email is not None:
            update_data['email'] = email
        if position_name is not None:
            update_data['position_name'] = position_name
        if description is not None:
            update_data['description'] = description
        if phone is not None:
            update_data['phone'] = phone
        
        # Process photo if provided
        if photo:
            photo_base64 = await process_profile_photo(photo)
            update_data['photo'] = photo_base64
        
        if not update_data:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Check email conflict if email is being updated
        if 'email' in update_data:
            existing_member = await Team.filter(email=update_data['email']).exclude(id=member_uuid).first()
            if existing_member:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
        
        # Update the member
        await member_obj.update_from_dict(update_data)
        await member_obj.save()
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": "Team member updated successfully",
                "data": {
                    "id": str(member_obj.id),
                    "name": member_obj.name,
                    "age": member_obj.age,
                    "email": member_obj.email,
                    "photo": member_obj.photo,
                    "description": member_obj.description,
                    "phone": member_obj.phone,
                    "position_name": member_obj.position_name,
                    "created_at": member_obj.created_at.isoformat(),
                    "updated_at": member_obj.updated_at.isoformat()
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f" Team member update failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update team member"
        )


async def delete_team_member(member_id: str):
    """Delete a team member"""
    try:
        # Validate UUID
        try:
            member_uuid = uuid.UUID(member_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid team member ID format"
            )
        
        # Check if member exists
        member_obj = await Team.get_or_none(id=member_uuid)
        if not member_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Team member not found"
            )
        
        print(f" Deleting team member: {member_obj.name}")
        
        # Delete member
        async with in_transaction():
            await member_obj.delete()
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": "Team member deleted successfully"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f" Team member deletion failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete team member"
        )


async def get_all_team_members(
    limit: int = Query(10, ge=1, le=100, description="Number of team members to return"),
    offset: int = Query(0, ge=0, description="Number of team members to skip"),
    position: Optional[str] = Query(None, description="Filter by position"),
    search: Optional[str] = Query(None, description="Search by name or email")
):
    """Get all team members with optional filtering and pagination"""
    try:
        print(f" Fetching team members with filters: position={position}, search={search}")
        
        # Build query
        query = Team.all()
        
        # Apply filters
        if position:
            query = query.filter(position_name__icontains=position)
        if search:
            query = query.filter(name__icontains=search) | query.filter(email__icontains=search)
        
        # Get total count
        total = await query.count()
        
        # Apply pagination
        team_members = await query.offset(offset).limit(limit).order_by('name')
        
        # Format response
        member_list = []
        for member in team_members:
            member_list.append({
                "id": str(member.id),
                "name": member.name,
                "age": member.age,
                "email": member.email,
                "photo": member.photo,
                "description": member.description,
                "phone": member.phone,
                "position_name": member.position_name,
                "created_at": member.created_at.isoformat(),
                "updated_at": member.updated_at.isoformat()
            })
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "data": {
                    "team_members": member_list,
                    "pagination": {
                        "total": total,
                        "limit": limit,
                        "offset": offset,
                        "has_next": offset + limit < total,
                        "has_prev": offset > 0
                    }
                }
            }
        )
    except Exception as e:
        print(f" Failed to fetch team members: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch team members"
        )


async def get_team_member_by_id(member_id: str):
    """Get a single team member by ID"""
    try:
        # Validate UUID
        try:
            member_uuid = uuid.UUID(member_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid team member ID format"
            )
        
        # Fetch team member
        member_obj = await Team.get_or_none(id=member_uuid)
        if not member_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Team member not found"
            )
        
        print(f" Fetched team member: {member_obj.name}")
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "data": {
                    "id": str(member_obj.id),
                    "name": member_obj.name,
                    "age": member_obj.age,
                    "email": member_obj.email,
                    "photo": member_obj.photo,
                    "description": member_obj.description,
                    "phone": member_obj.phone,
                    "position_name": member_obj.position_name,
                    "created_at": member_obj.created_at.isoformat(),
                    "updated_at": member_obj.updated_at.isoformat()
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f" Failed to fetch team member: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch team member"
        )