import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, Query, Depends, UploadFile, File, Form
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

from model.maintenanceRequestModel import MaintenanceRequest, MaintenanceStatus, MaintenancePriority
from model.userModel import User
from schemas.maintenanceRequestSchemas import (
    MaintenanceRequestCreate,
    MaintenanceRequestUpdate,
    MaintenanceRequestResponse,
    SendToContractorRequest,
    MaintenanceRequestSummary
)
from emailService.maintenanceRequestEmail import (
    send_maintenance_request_to_contractor,
    send_maintenance_request_confirmation_to_admin
)
from config.fileUpload import handle_general_media_upload


async def create_maintenance_request_with_files(
    tenant_name: str = Form(...),
    property_address: str = Form(...),
    issue_title: str = Form(...),
    issue_description: str = Form(...),
    contractor_email: str = Form(...),
    tenant_phone: Optional[str] = Form(None),
    tenant_email: Optional[str] = Form(None),
    property_unit: Optional[str] = Form(None),
    priority: str = Form("medium"),
    contractor_name: Optional[str] = Form(None),
    contractor_phone: Optional[str] = Form(None),
    estimated_cost: Optional[float] = Form(None),
    notes: Optional[str] = Form(None),
    photos: Optional[List[UploadFile]] = File(None),
    admin_user_id: str = None
):
    """Create a new maintenance request with file uploads (admin only)"""
    try:
        print(f"🔧 Creating new maintenance request: {issue_title}")
        
        # Convert admin_user_id to UUID if provided
        admin_uuid = None
        if admin_user_id:
            try:
                admin_uuid = uuid.UUID(admin_user_id)
            except ValueError:
                print(f"⚠️ Invalid admin UUID format: {admin_user_id}")
        
        # Process photos if provided
        photo_data = []
        if photos and len(photos) > 0:
            # Filter out empty files
            valid_photos = [photo for photo in photos if photo.filename and photo.filename.strip()]
            
            if valid_photos:
                print(f"📸 Processing {len(valid_photos)} photos")
                try:
                    upload_result = await handle_general_media_upload(
                        files=valid_photos,
                        upload_type="maintenance",
                        max_files=10,
                        compress_images=True,
                        quality=80,
                        max_width=1200,
                        max_height=1200
                    )
                    
                    if upload_result['success'] and upload_result['processed_files']:
                        photo_data = upload_result['processed_files']
                        print(f"✅ {len(photo_data)} photos processed successfully")
                    else:
                        print(f"⚠️ Photo processing failed: {upload_result.get('errors', [])}")
                        
                except Exception as photo_error:
                    print(f"❌ Photo processing error: {photo_error}")
                    # Continue with maintenance request creation even if photos fail
        
        # Create the maintenance request
        new_request = await MaintenanceRequest.create(
            tenant_name=tenant_name,
            tenant_phone=tenant_phone,
            tenant_email=tenant_email,
            property_address=property_address,
            property_unit=property_unit,
            issue_title=issue_title,
            issue_description=issue_description,
            priority=priority,
            contractor_email=contractor_email,
            contractor_name=contractor_name,
            contractor_phone=contractor_phone,
            photos=photo_data,
            estimated_cost=estimated_cost,
            notes=notes,
            created_by_admin=admin_uuid
        )
        print(f"✅ Maintenance request created with ID: {new_request.id}")
        
        return JSONResponse(
            status_code=HTTP_201_CREATED,
            content={
                "success": True,
                "message": "Maintenance request created successfully",
                "data": {
                    "id": str(new_request.id),
                    "tenant_name": new_request.tenant_name,
                    "tenant_phone": new_request.tenant_phone,
                    "tenant_email": new_request.tenant_email,
                    "property_address": new_request.property_address,
                    "property_unit": new_request.property_unit,
                    "issue_title": new_request.issue_title,
                    "issue_description": new_request.issue_description,
                    "priority": new_request.priority,
                    "contractor_email": new_request.contractor_email,
                    "contractor_name": new_request.contractor_name,
                    "contractor_phone": new_request.contractor_phone,
                    "photos": new_request.photos,
                    "status": new_request.status,
                    "estimated_cost": str(new_request.estimated_cost) if new_request.estimated_cost else None,
                    "notes": new_request.notes,
                    "created_by_admin": str(new_request.created_by_admin) if new_request.created_by_admin else None,
                    "created_at": new_request.created_at.isoformat(),
                    "updated_at": new_request.updated_at.isoformat(),
                    "sent_at": new_request.sent_at.isoformat() if new_request.sent_at else None,
                    "completed_at": new_request.completed_at.isoformat() if new_request.completed_at else None,
                    "photo_count": len(photo_data)
                }
            }
        )
    except Exception as e:
        print(f"❌ Maintenance request creation failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create maintenance request. Please try again later."
        )

async def create_maintenance_request(request_data: MaintenanceRequestCreate, admin_user_id: str = None):
    """Create a new maintenance request (admin only)"""
    try:
        print(f"🔧 Creating new maintenance request: {request_data.issue_title}")
        
        # Convert admin_user_id to UUID if provided
        admin_uuid = None
        if admin_user_id:
            try:
                admin_uuid = uuid.UUID(admin_user_id)
            except ValueError:
                print(f"⚠️ Invalid admin UUID format: {admin_user_id}")
        
        # Create the maintenance request
        new_request = await MaintenanceRequest.create(
            **request_data.dict(),
            created_by_admin=admin_uuid
        )
        print(f"✅ Maintenance request created with ID: {new_request.id}")
        
        return JSONResponse(
            status_code=HTTP_201_CREATED,
            content={
                "success": True,
                "message": "Maintenance request created successfully",
                "data": {
                    "id": str(new_request.id),
                    "tenant_name": new_request.tenant_name,
                    "tenant_phone": new_request.tenant_phone,
                    "tenant_email": new_request.tenant_email,
                    "property_address": new_request.property_address,
                    "property_unit": new_request.property_unit,
                    "issue_title": new_request.issue_title,
                    "issue_description": new_request.issue_description,
                    "priority": new_request.priority,
                    "contractor_email": new_request.contractor_email,
                    "contractor_name": new_request.contractor_name,
                    "contractor_phone": new_request.contractor_phone,
                    "photos": new_request.photos,
                    "status": new_request.status,
                    "estimated_cost": str(new_request.estimated_cost) if new_request.estimated_cost else None,
                    "notes": new_request.notes,
                    "created_by_admin": str(new_request.created_by_admin) if new_request.created_by_admin else None,
                    "created_at": new_request.created_at.isoformat(),
                    "updated_at": new_request.updated_at.isoformat(),
                    "sent_at": new_request.sent_at.isoformat() if new_request.sent_at else None,
                    "completed_at": new_request.completed_at.isoformat() if new_request.completed_at else None
                }
            }
        )
    except Exception as e:
        print(f"❌ Maintenance request creation failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create maintenance request. Please try again later."
        )


async def get_all_maintenance_requests(
    limit: int = Query(20, ge=1, le=100, description="Number of requests to return"),
    offset: int = Query(0, ge=0, description="Number of requests to skip"),
    status: Optional[MaintenanceStatus] = Query(None, description="Filter by status"),
    priority: Optional[MaintenancePriority] = Query(None, description="Filter by priority"),
    search: Optional[str] = Query(None, description="Search by tenant name, property address, or issue title")
):
    """Get all maintenance requests with filters (admin only)"""
    try:
        print(f"🔍 Fetching maintenance requests with filters: status={status}, priority={priority}, search={search}")
        
        # Build query
        query = MaintenanceRequest.all()
        
        # Apply filters
        if status:
            query = query.filter(status=status)
        if priority:
            query = query.filter(priority=priority)
        if search:
            query = query.filter(
                tenant_name__icontains=search
            ) | query.filter(
                property_address__icontains=search
            ) | query.filter(
                issue_title__icontains=search
            )
        
        # Get total count
        total = await query.count()
        
        # Apply pagination and ordering (newest first)
        requests = await query.offset(offset).limit(limit).order_by('-created_at')
        
        # Format response
        request_list = []
        for request in requests:
            request_list.append({
                "id": str(request.id),
                "tenant_name": request.tenant_name,
                "property_address": request.property_address,
                "issue_title": request.issue_title,
                "priority": request.priority,
                "status": request.status,
                "contractor_email": request.contractor_email,
                "contractor_name": request.contractor_name,
                "created_at": request.created_at.isoformat(),
                "sent_at": request.sent_at.isoformat() if request.sent_at else None
            })
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "data": {
                    "requests": request_list,
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
        print(f"❌ Failed to fetch maintenance requests: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch maintenance requests"
        )


async def get_maintenance_request_by_id(request_id: str):
    """Get a single maintenance request by ID (admin only)"""
    try:
        # Validate UUID
        try:
            request_uuid = uuid.UUID(request_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid maintenance request ID format"
            )
        
        # Fetch maintenance request
        request_obj = await MaintenanceRequest.get_or_none(id=request_uuid)
        if not request_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Maintenance request not found"
            )
        
        print(f"📋 Fetched maintenance request: {request_obj.issue_title}")
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "data": {
                    "id": str(request_obj.id),
                    "tenant_name": request_obj.tenant_name,
                    "tenant_phone": request_obj.tenant_phone,
                    "tenant_email": request_obj.tenant_email,
                    "property_address": request_obj.property_address,
                    "property_unit": request_obj.property_unit,
                    "issue_title": request_obj.issue_title,
                    "issue_description": request_obj.issue_description,
                    "priority": request_obj.priority,
                    "contractor_email": request_obj.contractor_email,
                    "contractor_name": request_obj.contractor_name,
                    "contractor_phone": request_obj.contractor_phone,
                    "photos": request_obj.photos,
                    "status": request_obj.status,
                    "estimated_cost": str(request_obj.estimated_cost) if request_obj.estimated_cost else None,
                    "notes": request_obj.notes,
                    "created_by_admin": str(request_obj.created_by_admin) if request_obj.created_by_admin else None,
                    "created_at": request_obj.created_at.isoformat(),
                    "updated_at": request_obj.updated_at.isoformat(),
                    "sent_at": request_obj.sent_at.isoformat() if request_obj.sent_at else None,
                    "completed_at": request_obj.completed_at.isoformat() if request_obj.completed_at else None
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to fetch maintenance request: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch maintenance request"
        )


async def update_maintenance_request(request_id: str, update_data: MaintenanceRequestUpdate):
    """Update a maintenance request (admin only)"""
    try:
        # Validate UUID
        try:
            request_uuid = uuid.UUID(request_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid maintenance request ID format"
            )
        
        # Check if request exists
        request_obj = await MaintenanceRequest.get_or_none(id=request_uuid)
        if not request_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Maintenance request not found"
            )
        
        # Update only provided fields
        update_dict = update_data.dict(exclude_unset=True)
        if not update_dict:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        print(f"📝 Updating maintenance request: {request_obj.issue_title}")
        
        # Update the request
        await request_obj.update_from_dict(update_dict)
        await request_obj.save()
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": "Maintenance request updated successfully",
                "data": {
                    "id": str(request_obj.id),
                    "issue_title": request_obj.issue_title,
                    "status": request_obj.status,
                    "priority": request_obj.priority,
                    "updated_at": request_obj.updated_at.isoformat()
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Maintenance request update failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update maintenance request"
        )


async def send_maintenance_request_to_contractor_endpoint(request_id: str, send_data: SendToContractorRequest):
    """Send maintenance request to contractor via email"""
    try:
        # Validate UUID
        try:
            request_uuid = uuid.UUID(request_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid maintenance request ID format"
            )
        
        # Check if request exists
        request_obj = await MaintenanceRequest.get_or_none(id=request_uuid)
        if not request_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Maintenance request not found"
            )
        
        print(f"📧 Sending maintenance request to contractor: {request_obj.contractor_email}")
        
        # Prepare data for email
        maintenance_data = {
            "tenant_name": request_obj.tenant_name,
            "tenant_phone": request_obj.tenant_phone,
            "tenant_email": request_obj.tenant_email,
            "property_address": request_obj.property_address,
            "property_unit": request_obj.property_unit,
            "issue_title": request_obj.issue_title,
            "issue_description": request_obj.issue_description,
            "priority": request_obj.priority,
            "contractor_email": request_obj.contractor_email,
            "contractor_name": request_obj.contractor_name,
            "contractor_phone": request_obj.contractor_phone,
            "photos": request_obj.photos,
            "estimated_cost": str(request_obj.estimated_cost) if request_obj.estimated_cost else None,
            "notes": request_obj.notes
        }
        
        # Send email to contractor
        try:
            await send_maintenance_request_to_contractor(
                maintenance_data,
                additional_message=send_data.additional_message
            )
            print("✅ Email sent successfully to contractor")
        except Exception as e:
            print(f"❌ Failed to send email to contractor: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email to contractor"
            )
        
        # Update request status and sent_at timestamp
        request_obj.status = MaintenanceStatus.SENT_TO_CONTRACTOR
        request_obj.sent_at = datetime.now()
        await request_obj.save()
        
        # Send confirmation email to admin (optional)
        # You can get admin email from the current user context or environment
        admin_email = "admin@property-rent.com"  # Replace with actual admin email
        try:
            await send_maintenance_request_confirmation_to_admin(maintenance_data, admin_email)
            print("✅ Confirmation email sent to admin")
        except Exception as e:
            print(f"⚠️ Failed to send confirmation email to admin: {e}")
            # Don't fail the request if admin confirmation fails
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": "Maintenance request sent to contractor successfully",
                "data": {
                    "id": str(request_obj.id),
                    "contractor_email": request_obj.contractor_email,
                    "status": request_obj.status,
                    "sent_at": request_obj.sent_at.isoformat()
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to send maintenance request to contractor: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send maintenance request to contractor"
        )


async def delete_maintenance_request(request_id: str):
    """Delete a maintenance request (admin only)"""
    try:
        # Validate UUID
        try:
            request_uuid = uuid.UUID(request_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid maintenance request ID format"
            )
        
        # Check if request exists
        request_obj = await MaintenanceRequest.get_or_none(id=request_uuid)
        if not request_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Maintenance request not found"
            )
        
        print(f"🗑️ Deleting maintenance request: {request_obj.issue_title}")
        
        # Delete request
        async with in_transaction():
            await request_obj.delete()
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": "Maintenance request deleted successfully"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Maintenance request deletion failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete maintenance request"
        )


async def get_maintenance_requests_by_status(status: MaintenanceStatus):
    """Get maintenance requests filtered by status"""
    try:
        requests = await MaintenanceRequest.filter(status=status).order_by('-created_at')
        
        request_list = []
        for request in requests:
            request_list.append({
                "id": str(request.id),
                "tenant_name": request.tenant_name,
                "property_address": request.property_address,
                "issue_title": request.issue_title,
                "priority": request.priority,
                "contractor_email": request.contractor_email,
                "contractor_name": request.contractor_name,
                "created_at": request.created_at.isoformat(),
                "sent_at": request.sent_at.isoformat() if request.sent_at else None
            })
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "data": {
                    "requests": request_list,
                    "count": len(request_list),
                    "status": status
                }
            }
        )
    except Exception as e:
        print(f"❌ Failed to fetch requests by status: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch maintenance requests by status"
        )