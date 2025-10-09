from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File, Form
from typing import Optional, List
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from controller.maintenanceRequestController import (
    create_maintenance_request,
    create_maintenance_request_with_files,
    get_all_maintenance_requests,
    get_maintenance_request_by_id,
    update_maintenance_request,
    send_maintenance_request_to_contractor_endpoint,
    delete_maintenance_request,
    get_maintenance_requests_by_status
)
from schemas.maintenanceRequestSchemas import (
    MaintenanceRequestCreate,
    MaintenanceRequestUpdate,
    SendToContractorRequest
)
from model.maintenanceRequestModel import MaintenanceStatus, MaintenancePriority
from authMiddleware.authMiddleware import check_for_authentication_cookie
from authMiddleware.roleMiddleware import require_admin


router = APIRouter( tags=["Maintenance Requests"])

@router.post("/maintenance-requests", status_code=HTTP_201_CREATED,dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)])
async def create_new_maintenance_request(
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
    photos: Optional[List[UploadFile]] = File(default=None),
    
):
    """
    Create a new maintenance request with photo uploads (Admin only)
    
    This endpoint allows administrators to create maintenance requests that can be sent to contractors.
    Supports uploading multiple photos of the maintenance issue.
    
    **Required fields:**
    - **tenant_name**: Name of the tenant reporting the issue
    - **property_address**: Full address of the property
    - **issue_title**: Brief title describing the maintenance issue
    - **issue_description**: Detailed description of the issue
    - **contractor_email**: Email address of the contractor to handle this request
    
    **Optional fields:**
    - **tenant_phone**: Tenant's contact phone number
    - **tenant_email**: Tenant's email address
    - **property_unit**: Specific unit number (for multi-unit properties)
    - **priority**: Issue priority (low, medium, high, urgent) - defaults to medium
    - **contractor_name**: Name of the contractor
    - **contractor_phone**: Contractor's phone number
    - **photos**: Multiple image files showing the maintenance issue
    - **estimated_cost**: Estimated cost for the maintenance work
    - **notes**: Additional notes or instructions
    
    **Photo Upload:**
    - Supports JPEG, PNG, GIF, WebP formats
    - Maximum 10 photos per request
    - Images are automatically compressed and resized
    - Files are converted to base64 for storage
    """
    
    admin_user_id = None  
    return await create_maintenance_request_with_files(
        tenant_name=tenant_name,
        property_address=property_address,
        issue_title=issue_title,
        issue_description=issue_description,
        contractor_email=contractor_email,
        tenant_phone=tenant_phone,
        tenant_email=tenant_email,
        property_unit=property_unit,
        priority=priority,
        contractor_name=contractor_name,
        contractor_phone=contractor_phone,
        estimated_cost=estimated_cost,
        notes=notes,
        photos=photos,
        admin_user_id=admin_user_id
    )


@router.post("/maintenance-requests/json", status_code=HTTP_201_CREATED,dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)])
async def create_new_maintenance_request_json(
    request_data: MaintenanceRequestCreate,
  
):
    """
    Create a new maintenance request via JSON (Admin only)
    
    Alternative endpoint for creating maintenance requests without file uploads.
    Use this when photos are already uploaded elsewhere or not needed.
    """
    
    admin_user_id = None 
    return await create_maintenance_request(request_data, admin_user_id)


@router.get("/maintenance-requests", status_code=HTTP_200_OK,dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)])
async def get_maintenance_requests(
    limit: int = Query(20, ge=1, le=100, description="Number of requests to return"),
    offset: int = Query(0, ge=0, description="Number of requests to skip"),
    status: Optional[MaintenanceStatus] = Query(None, description="Filter by status"),
    priority: Optional[MaintenancePriority] = Query(None, description="Filter by priority"),
    search: Optional[str] = Query(None, description="Search by tenant name, property address, or issue title"),
):
    """
    Get all maintenance requests with optional filters (Admin only)
    
    This endpoint returns a paginated list of maintenance requests with optional filtering.
    
    **Query Parameters:**
    - **limit**: Maximum number of requests to return (1-100, default: 20)
    - **offset**: Number of requests to skip for pagination (default: 0)
    - **status**: Filter by request status (pending, sent_to_contractor, in_progress, completed, cancelled)
    - **priority**: Filter by priority (low, medium, high, urgent)
    - **search**: Search text to match against tenant name, property address, or issue title
    
    **Returns:**
    - List of maintenance requests with pagination metadata
    - Each request includes summary information for list display
    """
    return await get_all_maintenance_requests(limit, offset, status, priority, search)


@router.get("/maintenance-requests/status/{status}", status_code=HTTP_200_OK,dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)])
async def get_requests_by_status(
    status: MaintenanceStatus,
):
    """
    Get maintenance requests filtered by status (Admin only)
    
    **Path Parameters:**
    - **status**: The status to filter by (pending, sent_to_contractor, in_progress, completed, cancelled)
    
    **Returns:**
    - List of maintenance requests with the specified status
    - Count of requests found
    """
    return await get_maintenance_requests_by_status(status)


@router.get("/maintenance-requests/{request_id}", status_code=HTTP_200_OK,dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)])
async def get_maintenance_request(
    request_id: str,
):
    """
    Get a single maintenance request by ID (Admin only)
    
    **Path Parameters:**
    - **request_id**: UUID of the maintenance request
    
    **Returns:**
    - Complete maintenance request details including all fields
    - Full tenant, property, contractor information
    - Photos, notes, and status information
    """
    return await get_maintenance_request_by_id(request_id)


@router.put("/maintenance-requests/{request_id}", status_code=HTTP_200_OK,dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)])
async def update_maintenance_request_endpoint(
    request_id: str,
    update_data: MaintenanceRequestUpdate,
):
    """
    Update a maintenance request (Admin only)
    
    **Path Parameters:**
    - **request_id**: UUID of the maintenance request to update
    
    **Request Body:**
    - Any combination of the maintenance request fields to update
    - Only provided fields will be updated (partial updates supported)
    
    **Updatable fields:**
    - Tenant information (name, phone, email)
    - Property information (address, unit)
    - Issue details (title, description, priority)
    - Contractor information (email, name, phone)
    - Status, photos, estimated cost, notes
    """
    return await update_maintenance_request(request_id, update_data)


@router.post("/maintenance-requests/{request_id}/send-to-contractor", status_code=HTTP_200_OK,dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)])
async def send_to_contractor(
    request_id: str,
    send_data: SendToContractorRequest,
    # current_admin = Depends(get_current_admin_user)  # Uncomment when auth is implemented
):
    """
    Send maintenance request to contractor via email (Admin only)
    
    This is the main action that sends the maintenance request details to the contractor.
    
    **Path Parameters:**
    - **request_id**: UUID of the maintenance request to send
    
    **Request Body:**
    - **additional_message**: Optional additional message to include in the email
    - **urgent**: Whether to mark this as urgent (affects email formatting)
    
    **Actions performed:**
    - Sends detailed email to contractor with all maintenance information
    - Updates request status to 'sent_to_contractor'
    - Sets the 'sent_at' timestamp
    - Sends confirmation email to admin
    
    **Email includes:**
    - Tenant contact information
    - Property address and unit details
    - Issue description and priority
    - Photos (if uploaded)
    - Estimated cost and notes
    - Admin contact information for follow-up
    """
    return await send_maintenance_request_to_contractor_endpoint(request_id, send_data)


@router.delete("/maintenance-requests/{request_id}", status_code=HTTP_200_OK,dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)])
async def delete_maintenance_request_endpoint(
    request_id: str,
    # current_admin = Depends(get_current_admin_user)  # Uncomment when auth is implemented
):
    """
    Delete a maintenance request (Admin only)
    
    **Path Parameters:**
    - **request_id**: UUID of the maintenance request to delete
    
    **Warning:**
    - This action is permanent and cannot be undone
    - Consider updating the status to 'cancelled' instead of deleting
    """
    return await delete_maintenance_request(request_id)