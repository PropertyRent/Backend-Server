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
                    "updated_at": notice_obj.updated_at.isoformat(),
                    "is_active": notice_obj.is_active
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
            query = query.filter(Q(title__icontains=search) | Q(description__icontains=search))
        
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
                "is_active": notice.is_active,
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
                    "is_active": notice_obj.is_active,
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
                "is_active": new_notice.is_active,
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
            query = query.filter(Q(title__icontains=search) | Q(description__icontains=search))
        
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


# === NOTICE ACTIVE STATUS MANAGEMENT ===

async def toggle_notice_active(notice_id: str):
    """Toggle the active status of a notice (true to false or false to true)"""
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
        
        # Store old status for logging
        old_status = notice_obj.is_active
        new_status = not old_status
        
        print(f"📢 Toggling notice '{notice_obj.title}' from {old_status} to {new_status}")
        
        # Update the active status
        notice_obj.is_active = new_status
        await notice_obj.save()
        
        status_text = "activated" if new_status else "deactivated"
        visibility = "visible to public" if new_status else "hidden from public"
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": f"Notice {status_text} successfully - now {visibility}",
                "data": {
                    "id": str(notice_obj.id),
                    "title": notice_obj.title,
                    "description": notice_obj.description,
                    "is_active": notice_obj.is_active,
                    "file_type": notice_obj.file_type,
                    "original_filename": notice_obj.original_filename,
                    "created_at": notice_obj.created_at.isoformat(),
                    "updated_at": notice_obj.updated_at.isoformat(),
                    "status_change": {
                        "old_status": old_status,
                        "new_status": new_status,
                        "action": status_text
                    }
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to toggle notice active status: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle notice active status: {str(e)}"
        )


async def set_notice_active(notice_id: str, is_active: bool):
    """Set the active status of a notice to a specific value"""
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
        
        # Store old status for logging
        old_status = notice_obj.is_active
        
        print(f"📢 Setting notice '{notice_obj.title}' active status from {old_status} to {is_active}")
        
        # Check if change is needed
        if old_status == is_active:
            status_text = "active" if is_active else "inactive" 
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": f"Notice is already {status_text} - no change needed",
                    "data": {
                        "id": str(notice_obj.id),
                        "title": notice_obj.title,
                        "description": notice_obj.description,
                        "is_active": notice_obj.is_active,
                        "file_type": notice_obj.file_type,
                        "original_filename": notice_obj.original_filename,
                        "created_at": notice_obj.created_at.isoformat(),
                        "updated_at": notice_obj.updated_at.isoformat(),
                        "status_change": {
                            "old_status": old_status,
                            "new_status": is_active,
                            "action": "no change"
                        }
                    }
                }
            )
        
        # Update the active status
        notice_obj.is_active = is_active
        await notice_obj.save()
        
        status_text = "activated" if is_active else "deactivated"
        visibility = "visible to public" if is_active else "hidden from public"
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": f"Notice {status_text} successfully - now {visibility}",
                "data": {
                    "id": str(notice_obj.id),
                    "title": notice_obj.title,
                    "description": notice_obj.description,
                    "is_active": notice_obj.is_active,
                    "file_type": notice_obj.file_type,
                    "original_filename": notice_obj.original_filename,
                    "created_at": notice_obj.created_at.isoformat(),
                    "updated_at": notice_obj.updated_at.isoformat(),
                    "status_change": {
                        "old_status": old_status,
                        "new_status": is_active,
                        "action": status_text
                    }
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to set notice active status: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set notice active status: {str(e)}"
        )


async def download_notice_file(notice_id: str):
    """Download notice file - Accessible to both admin and public"""
    try:
        import base64
        from fastapi.responses import Response
        
        print(f"📁 Downloading notice file for ID: {notice_id}")
        
        # Get notice
        try:
            notice = await Notice.get(id=uuid.UUID(notice_id))
        except DoesNotExist:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Notice not found"
            )
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid notice ID format"
            )
        
        # Check if notice has a file
        if not notice.notice_file:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="No file attached to this notice"
            )
        
        try:
            # Clean the base64 string (remove data URL prefix if present)
            base64_data = notice.notice_file
            if base64_data.startswith('data:'):
                # Remove data URL prefix like "data:application/pdf;base64," 
                base64_data = base64_data.split(',', 1)[1]
            
            # Remove any whitespace or newlines
            base64_data = base64_data.replace('\n', '').replace('\r', '').replace(' ', '')
            
            print(f"📁 Base64 data length: {len(base64_data)}")
            print(f"📁 First 100 chars of base64: {base64_data[:100]}")
            
            # Decode base64 file data
            file_data = base64.b64decode(base64_data)
            
            # Determine content type based on file type
            content_type_mapping = {
                'pdf': 'application/pdf',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'doc': 'application/msword',
                'txt': 'text/plain'
            }
            
            # Get file extension from original filename or file_type
            file_extension = None
            if notice.original_filename:
                file_extension = notice.original_filename.split('.')[-1].lower()
            elif notice.file_type:
                file_extension = notice.file_type.lower()
            
            content_type = content_type_mapping.get(file_extension, 'application/octet-stream')
            
            # Create filename for download
            if notice.original_filename:
                filename = notice.original_filename
            else:
                # Fallback filename
                filename = f"notice_{notice.id}.{file_extension or 'bin'}"
            
            print(f"📁 File download successful - filename: {filename}, size: {len(file_data)} bytes, type: {content_type}")
            
            # Return file as response with proper headers
            return Response(
                content=file_data,
                media_type=content_type,
                headers={
                    "Content-Disposition": f"attachment; filename=\"{filename}\"",
                    "Content-Length": str(len(file_data)),
                    "Cache-Control": "no-cache"
                }
            )
            
        except Exception as decode_error:
            print(f"❌ File decoding error: {decode_error}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to decode file data. File may be corrupted."
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error downloading notice file: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download notice file: {str(e)}"
        )


async def debug_notice_file(notice_id: str):
    """Debug notice file data - Show file info for troubleshooting"""
    try:
        print(f"🔍 Debugging notice file for ID: {notice_id}")
        
        # Get notice
        try:
            notice = await Notice.get(id=uuid.UUID(notice_id))
        except DoesNotExist:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Notice not found"
            )
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid notice ID format"
            )
        
        # Check if notice has a file
        if not notice.notice_file:
            return {
                "success": False,
                "message": "No file attached to this notice",
                "data": {
                    "notice_id": str(notice.id),
                    "title": notice.title,
                    "has_file": False
                }
            }
        
        file_info = {
            "notice_id": str(notice.id),
            "title": notice.title,
            "has_file": True,
            "original_filename": notice.original_filename,
            "file_type": notice.file_type,
            "base64_length": len(notice.notice_file),
            "starts_with_data_url": notice.notice_file.startswith('data:'),
            "base64_prefix": notice.notice_file[:100] if len(notice.notice_file) > 100 else notice.notice_file
        }
        
        # Try to decode and get file size
        try:
            import base64
            base64_data = notice.notice_file
            if base64_data.startswith('data:'):
                base64_data = base64_data.split(',', 1)[1]
            
            base64_data = base64_data.replace('\n', '').replace('\r', '').replace(' ', '')
            file_data = base64.b64decode(base64_data)
            file_info["decoded_size"] = len(file_data)
            file_info["decode_success"] = True
            
        except Exception as decode_error:
            file_info["decode_success"] = False
            file_info["decode_error"] = str(decode_error)
        
        return {
            "success": True,
            "message": "File debug information",
            "data": file_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error debugging notice file: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to debug notice file: {str(e)}"
        )