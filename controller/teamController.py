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
from tortoise.expressions import Q

from model.teamModel import Team
from schemas.teamSchemas import TeamCreate, TeamUpdate, TeamResponse
from config.fileUpload import process_profile_photo
from config.fileUpload import handle_general_media_upload


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
            # Use Q objects for OR condition
            query = query.filter(Q(name__icontains=search) | Q(email__icontains=search))
        
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




async def handle_create_team_member(
    name: str = Form(...),
    age: int = Form(...),
    email: str = Form(...),
    position_name: str = Form(...),
    description: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None)
):
    """Create team member with optional photo upload (unified route)"""
    try:
        print(f"👥 Creating new team member: {name}")
        
        # Check if email already exists
        existing_member = await Team.filter(email=email).first()
        if existing_member:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        async with in_transaction():
            # Process photo if provided using general upload function
            photo_base64 = None
            if photo and photo.filename:
                print(f"📸 Processing photo for team member: {photo.filename}")
                
                try:
                    # Use general media upload function for consistency
                    upload_result = await handle_general_media_upload(
                        files=[photo],
                        upload_type="profile",
                        max_files=1,
                        compress_images=True,
                        quality=85,
                        max_width=800,
                        max_height=800
                    )
                    
                    if upload_result['success'] and upload_result['processed_files']:
                        photo_base64 = upload_result['processed_files'][0]
                        print("✅ Photo processed successfully")
                    else:
                        print(f"⚠️ Photo processing failed: {upload_result.get('errors', [])}")
                        
                except Exception as photo_error:
                    print(f"❌ Photo processing error: {photo_error}")
                    # Continue with team member creation even if photo fails
            
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
            
            print(f"✅ Team member created with ID: {new_member.id}")
        
        return {
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
                "updated_at": new_member.updated_at.isoformat(),
                "has_photo": bool(photo_base64)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Team member creation failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create team member: {str(e)}"
        )


async def handle_update_team_member(
    member_id: str,
    name: Optional[str] = Form(None),
    age: Optional[int] = Form(None),
    email: Optional[str] = Form(None),
    position_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None)
):
    """Update team member with optional photo upload (unified route)"""
    try:
        print(f"👥 Updating team member: {member_id}")
        
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
        
        async with in_transaction():
            # Build update data
            update_data = {}
            
            # Add basic fields if provided
            field_mapping = {
                "name": name,
                "age": age,
                "email": email,
                "position_name": position_name,
                "description": description,
                "phone": phone
            }
            
            for field_name, field_value in field_mapping.items():
                if field_value is not None:
                    update_data[field_name] = field_value
            
            # Check email conflict if email is being updated
            if 'email' in update_data:
                existing_member = await Team.filter(email=update_data['email']).exclude(id=member_uuid).first()
                if existing_member:
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST,
                        detail="Email already exists"
                    )
            
            # Process photo if provided
            photo_updated = False
            if photo and photo.filename:
                print(f"📸 Processing new photo for team member: {photo.filename}")
                
                try:
                    # Use general media upload function for consistency
                    upload_result = await handle_general_media_upload(
                        files=[photo],
                        upload_type="profile",
                        max_files=1,
                        compress_images=True,
                        quality=85,
                        max_width=800,
                        max_height=800
                    )
                    
                    if upload_result['success'] and upload_result['processed_files']:
                        update_data['photo'] = upload_result['processed_files'][0]
                        photo_updated = True
                        print("✅ New photo processed successfully")
                    else:
                        print(f"⚠️ Photo processing failed: {upload_result.get('errors', [])}")
                        
                except Exception as photo_error:
                    print(f"❌ Photo processing error: {photo_error}")
                    # Continue with update even if photo fails
            
            # Update member if there's data to update
            if update_data:
                print(f"📝 Updating fields: {list(update_data.keys())}")
                await Team.filter(id=member_uuid).update(**update_data)
                print("✅ Team member fields updated")
            else:
                print("ℹ️ No fields to update")
        
        # Get updated member
        updated_member = await Team.get(id=member_uuid)
        
        # Create summary message
        operations = []
        if update_data:
            field_count = len([k for k in update_data.keys() if k != 'photo'])
            if field_count > 0:
                operations.append(f"updated {field_count} fields")
        if photo_updated:
            operations.append("updated photo")
        
        operation_summary = ", ".join(operations) if operations else "no changes made"
        
        return {
            "success": True,
            "message": f"Team member updated successfully: {operation_summary}",
            "data": {
                "id": str(updated_member.id),
                "name": updated_member.name,
                "age": updated_member.age,
                "email": updated_member.email,
                "photo": updated_member.photo,
                "description": updated_member.description,
                "phone": updated_member.phone,
                "position_name": updated_member.position_name,
                "created_at": updated_member.created_at.isoformat(),
                "updated_at": updated_member.updated_at.isoformat(),
                "operations_performed": {
                    "fields_updated": len([k for k in update_data.keys() if k != 'photo']) if update_data else 0,
                    "photo_updated": photo_updated
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Team member update failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update team member: {str(e)}"
        )