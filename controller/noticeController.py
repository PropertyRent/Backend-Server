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

from model.noticeModel import Notice
from schemas.noticeSchemas import NoticeCreate, NoticeUpdate, NoticeResponse
from config.fileUpload import process_document_to_base64


async def add_notice(notice_data: NoticeCreate):
    """Create a new notice"""
    try:
        print(f" Creating new notice: {notice_data.title}")
        
        # Create the notice
        new_notice = await Notice.create(**notice_data.dict())
        print(f" Notice created with ID: {new_notice.id}")
        
        return JSONResponse(
            status_code=HTTP_201_CREATED,
            content={
                "success": True,
                "message": "Notice created successfully",
                "data": {
                    "id": str(new_notice.id),
                    "title": new_notice.title,
                    "description": new_notice.description,
                    "notice_file": new_notice.notice_file,
                    "file_type": new_notice.file_type,
                    "original_filename": new_notice.original_filename,
                    "created_at": new_notice.created_at.isoformat(),
                    "updated_at": new_notice.updated_at.isoformat()
                }
            }
        )
    except IntegrityError as e:
        print(f" Notice creation failed - integrity error: {e}")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Notice creation failed due to data integrity issues"
        )
    except Exception as e:
        print(f" Notice creation failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create notice"
        )


async def update_notice(notice_id: str, notice_data: NoticeUpdate):
    """Update an existing notice"""
    try:
        # Validate UUID
        try:
            notice_uuid = uuid.UUID(notice_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid notice ID format"
            )
        
        # Check if notice exists
        notice_obj = await Notice.get_or_none(id=notice_uuid)
        if not notice_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Notice not found"
            )
        
        # Update only provided fields
        update_data = notice_data.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        print(f" Updating notice {notice_id} with data: {list(update_data.keys())}")
        
        # Update the notice
        await notice_obj.update_from_dict(update_data)
        await notice_obj.save()
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": "Notice updated successfully",
                "data": {
                    "id": str(notice_obj.id),
                    "title": notice_obj.title,
                    "description": notice_obj.description,
                    "notice_file": notice_obj.notice_file,
                    "file_type": notice_obj.file_type,
                    "original_filename": notice_obj.original_filename,
                    "created_at": notice_obj.created_at.isoformat(),
                    "updated_at": notice_obj.updated_at.isoformat()
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f" Notice update failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notice"
        )


async def delete_notice(notice_id: str):
    """Delete a notice"""
    try:
        # Validate UUID
        try:
            notice_uuid = uuid.UUID(notice_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid notice ID format"
            )
        
        # Check if notice exists
        notice_obj = await Notice.get_or_none(id=notice_uuid)
        if not notice_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Notice not found"
            )
        
        print(f" Deleting notice: {notice_obj.title}")
        
        # Delete notice
        async with in_transaction():
            await notice_obj.delete()
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": "Notice deleted successfully"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f" Notice deletion failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete notice"
        )


async def get_all_notices(
    limit: int = Query(10, ge=1, le=100, description="Number of notices to return"),
    offset: int = Query(0, ge=0, description="Number of notices to skip"),
    search: Optional[str] = Query(None, description="Search by title or description")
):
    """Get all notices with optional filtering and pagination"""
    try:
        print(f" Fetching notices with search: {search}")
        
        # Build query
        query = Notice.all()
        
        # Apply search filter
        if search:
            query = query.filter(title__icontains=search) | query.filter(description__icontains=search)
        
        # Get total count
        total = await query.count()
        
        # Apply pagination and order by creation date (newest first)
        notices = await query.offset(offset).limit(limit).order_by('-created_at')
        
        # Format response
        notice_list = []
        for notice in notices:
            notice_list.append({
                "id": str(notice.id),
                "title": notice.title,
                "description": notice.description,
                "notice_file": notice.notice_file,
                "file_type": notice.file_type,
                "original_filename": notice.original_filename,
                "created_at": notice.created_at.isoformat(),
                "updated_at": notice.updated_at.isoformat()
            })
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "data": {
                    "notices": notice_list,
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
        print(f" Failed to fetch notices: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notices"
        )


async def get_notice_by_id(notice_id: str):
    """Get a single notice by ID"""
    try:
        # Validate UUID
        try:
            notice_uuid = uuid.UUID(notice_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid notice ID format"
            )
        
        # Fetch notice
        notice_obj = await Notice.get_or_none(id=notice_uuid)
        if not notice_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Notice not found"
            )
        
        print(f" Fetched notice: {notice_obj.title}")
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "data": {
                    "id": str(notice_obj.id),
                    "title": notice_obj.title,
                    "description": notice_obj.description,
                    "notice_file": notice_obj.notice_file,
                    "file_type": notice_obj.file_type,
                    "original_filename": notice_obj.original_filename,
                    "created_at": notice_obj.created_at.isoformat(),
                    "updated_at": notice_obj.updated_at.isoformat()
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f" Failed to fetch notice: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notice"
        )


# === UNIFIED NOTICE HANDLER ===

async def handle_create_notice(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    notice_file: Optional[UploadFile] = File(None)
):
    """Create notice with optional file upload (unified route)"""
    try:
        print(f"📢 Creating new notice: {title}")
        
        async with in_transaction():
            # Process file if provided
            file_base64 = None
            file_type = None
            original_filename = None
            
            if notice_file and notice_file.filename:
                print(f"📄 Processing notice file: {notice_file.filename}")
                
                try:
                    # Use document processing function
                    file_base64 = await process_document_to_base64(notice_file)
                    file_type = notice_file.content_type
                    original_filename = notice_file.filename
                    print("✅ Notice file processed successfully")
                    
                except Exception as file_error:
                    print(f"❌ Notice file processing error: {file_error}")
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST,
                        detail=f"File processing failed: {str(file_error)}"
                    )
            
            # Create the notice
            new_notice = await Notice.create(
                title=title,
                description=description,
                notice_file=file_base64,
                file_type=file_type,
                original_filename=original_filename
            )
            
            print(f"✅ Notice created with ID: {new_notice.id}")
        
        return {
            "success": True,
            "message": "Notice created successfully",
            "data": {
                "id": str(new_notice.id),
                "title": new_notice.title,
                "description": new_notice.description,
                "notice_file": new_notice.notice_file,
                "file_type": new_notice.file_type,
                "original_filename": new_notice.original_filename,
                "created_at": new_notice.created_at.isoformat(),
                "updated_at": new_notice.updated_at.isoformat(),
                "has_file": bool(file_base64)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Notice creation failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create notice: {str(e)}"
        )


async def handle_update_notice(
    notice_id: str,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    notice_file: Optional[UploadFile] = File(None)
):
    """Update notice with optional file upload (unified route)"""
    try:
        print(f"📢 Updating notice: {notice_id}")
        
        # Validate UUID
        try:
            notice_uuid = uuid.UUID(notice_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid notice ID format"
            )
        
        # Check if notice exists
        notice_obj = await Notice.get_or_none(id=notice_uuid)
        if not notice_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Notice not found"
            )
        
        async with in_transaction():
            # Build update data
            update_data = {}
            
            # Add basic fields if provided
            if title is not None:
                update_data['title'] = title
            if description is not None:
                update_data['description'] = description
            
            # Process file if provided
            file_updated = False
            if notice_file and notice_file.filename:
                print(f"📄 Processing new notice file: {notice_file.filename}")
                
                try:
                    # Use document processing function
                    file_base64 = await process_document_to_base64(notice_file)
                    update_data['notice_file'] = file_base64
                    update_data['file_type'] = notice_file.content_type
                    update_data['original_filename'] = notice_file.filename
                    file_updated = True
                    print("✅ New notice file processed successfully")
                    
                except Exception as file_error:
                    print(f"❌ Notice file processing error: {file_error}")
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST,
                        detail=f"File processing failed: {str(file_error)}"
                    )
            
            # Update notice if there's data to update
            if update_data:
                print(f"📝 Updating fields: {list(update_data.keys())}")
                await Notice.filter(id=notice_uuid).update(**update_data)
                print("✅ Notice fields updated")
            else:
                print("ℹ️ No fields to update")
        
        # Get updated notice
        updated_notice = await Notice.get(id=notice_uuid)
        
        # Create summary message
        operations = []
        if update_data:
            field_count = len([k for k in update_data.keys() if k not in ['notice_file', 'file_type', 'original_filename']])
            if field_count > 0:
                operations.append(f"updated {field_count} fields")
        if file_updated:
            operations.append("updated file")
        
        operation_summary = ", ".join(operations) if operations else "no changes made"
        
        return {
            "success": True,
            "message": f"Notice updated successfully: {operation_summary}",
            "data": {
                "id": str(updated_notice.id),
                "title": updated_notice.title,
                "description": updated_notice.description,
                "notice_file": updated_notice.notice_file,
                "file_type": updated_notice.file_type,
                "original_filename": updated_notice.original_filename,
                "created_at": updated_notice.created_at.isoformat(),
                "updated_at": updated_notice.updated_at.isoformat(),
                "operations_performed": {
                    "fields_updated": len([k for k in update_data.keys() if k not in ['notice_file', 'file_type', 'original_filename']]) if update_data else 0,
                    "file_updated": file_updated
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Notice update failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notice: {str(e)}"
        )


async def get_active_notices(
    limit: int = 10,
    offset: int = 0,
    search: Optional[str] = None
):
    """Get all active notices with optional filtering and pagination"""
    try:
        print(f"📢 Getting active notices - limit: {limit}, offset: {offset}, search: {search}")
        
        # Build query for active notices
        query = Notice.filter(is_active=True)
        
        # Add search filter if provided
        if search:
            query = query.filter(
                title__icontains=search
            ).union(
                Notice.filter(is_active=True, description__icontains=search)
            )
        
        # Get total count for pagination
        total = await query.count()
        
        # Get notices with pagination, ordered by creation date (newest first)
        notices = await query.order_by('-created_at').offset(offset).limit(limit)
        
        # Format notices data
        notices_data = []
        for notice in notices:
            notice_data = {
                "id": str(notice.id),
                "title": notice.title,
                "description": notice.description,
                "notice_file": notice.notice_file,
                "file_type": notice.file_type,
                "original_filename": notice.original_filename,
                "is_active": notice.is_active,
                "created_at": notice.created_at.isoformat(),
                "updated_at": notice.updated_at.isoformat()
            }
            notices_data.append(notice_data)
        
        print(f"✅ Found {len(notices_data)} active notices out of {total} total active")
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": f"Active notices retrieved successfully",
                "data": {
                    "notices": notices_data,
                    "pagination": {
                        "total": total,
                        "limit": limit,
                        "offset": offset,
                        "returned": len(notices_data)
                    }
                }
            }
        )
        
    except Exception as e:
        print(f"❌ Failed to get active notices: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve active notices: {str(e)}"
        )