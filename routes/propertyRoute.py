from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, Request
from typing import Optional, List, Union
from controller.propertyController import (
    handle_create_property,
    handle_update_property,
    handle_delete_property,
    handle_get_all_properties,
    handle_get_property_by_id
)
from authMiddleware.authMiddleware import check_for_authentication_cookie
from authMiddleware.roleMiddleware import require_admin

router = APIRouter(tags=["Properties"])


@router.post("/admin/properties/add", 
    summary="[ADMIN] Create property with optional media",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def create_property_with_media(
    request: Request,
    # Property fields (all optional except title, property_type, status, price)
    title: str = Form(...),
    property_type: str = Form(...),  # apartment, house, studio, etc.
    status: str = Form(...),  # available, rented, maintenance
    price: float = Form(...),
    
    # Optional property details
    description: Optional[str] = Form(None),
    furnishing: Optional[str] = Form(None),
    area_sqft: Optional[float] = Form(None),
    bedrooms: Optional[int] = Form(None),
    bathrooms: Optional[int] = Form(None),
    floors: Optional[int] = Form(None),
    lease_term: Optional[str] = Form(None),
    application_fee: Optional[float] = Form(None),
    pet_policy: Optional[str] = Form(None),
    property_management_contact: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    deposit: Optional[float] = Form(None),
    
    # Location fields
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    pincode: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    
    # JSON fields (will be parsed from comma-separated strings)
    utilities: Optional[str] = Form(None),  # "electricity,water,gas"
    amenities: Optional[str] = Form(None),  # "pool,gym,parking"
    appliances_included: Optional[str] = Form(None),  # "refrigerator,microwave,washer"
    
    # Optional media files - same as working test route
    media_files: List[UploadFile] = File(default=[])
):
    # Debug request details
    print(f"🔍 REQUEST DEBUG: Content-Type = {request.headers.get('content-type', 'NOT SET')}")
    print(f"🔍 REQUEST DEBUG: Method = {request.method}")
    print(f"🔍 REQUEST DEBUG: Content-Length = {request.headers.get('content-length', 'NOT SET')}")
    
    # Try to get raw form data for debugging (this is advanced debugging)
    try:
        form_data = await request.form()
        print(f"🔍 FORM DEBUG: Form keys = {list(form_data.keys())}")
        for key in form_data.keys():
            value = form_data[key]
            if hasattr(value, 'filename'):
                print(f"🔍 FORM DEBUG: {key} = FILE: {value.filename}")
            else:
                print(f"🔍 FORM DEBUG: {key} = {type(value)}: {str(value)[:100]}")
    except Exception as form_error:
        print(f"🔍 FORM DEBUG ERROR: {form_error}")
    
    # Ensure media_files is a list (should already be due to default=[])
    if media_files is None:
        media_files = []
    
    # Debug at route level
    print(f"🔍 ROUTE DEBUG: media_files received = {media_files}")
    print(f"🔍 ROUTE DEBUG: media_files type = {type(media_files)}")
    print(f"🔍 ROUTE DEBUG: len(media_files) = {len(media_files)}")
    if media_files and len(media_files) > 0:
        for i, mf in enumerate(media_files):
            print(f"🔍 ROUTE DEBUG: File {i}: {mf.filename if hasattr(mf, 'filename') else 'NO_FILENAME'} - Size: {getattr(mf, 'size', 'unknown')}")
    else:
        print("🔍 ROUTE DEBUG: No files received or empty list")
    
    return await handle_create_property(
        title=title,
        property_type=property_type,
        status=status,
        price=price,
        description=description,
        furnishing=furnishing,
        area_sqft=area_sqft,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        floors=floors,
        lease_term=lease_term,
        application_fee=application_fee,
        pet_policy=pet_policy,
        property_management_contact=property_management_contact,
        website=website,
        deposit=deposit,
        address=address,
        city=city,
        state=state,
        pincode=pincode,
        latitude=latitude,
        longitude=longitude,
        utilities=utilities,
        amenities=amenities,
        appliances_included=appliances_included,
        media_files=media_files
    )

@router.put("/admin/properties/{property_id}",
    summary="[ADMIN] Update property with optional media",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def update_property_with_media(
    property_id: str,
    
    # All fields optional for updates
    title: Optional[str] = Form(None),
    property_type: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    furnishing: Optional[str] = Form(None),
    area_sqft: Optional[float] = Form(None),
    bedrooms: Optional[int] = Form(None),
    bathrooms: Optional[int] = Form(None),
    floors: Optional[int] = Form(None),
    lease_term: Optional[str] = Form(None),
    application_fee: Optional[float] = Form(None),
    pet_policy: Optional[str] = Form(None),
    property_management_contact: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    deposit: Optional[float] = Form(None),
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    pincode: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    utilities: Optional[str] = Form(None),
    amenities: Optional[str] = Form(None),
    appliances_included: Optional[str] = Form(None),
    
    # Optional media operations
    media_files: List[UploadFile] = File(default=[]),  # Add new media
    remove_media_ids: Optional[str] = Form(None),  # "id1,id2,id3" - comma separated IDs to remove
    set_cover_media_id: Optional[str] = Form(None)  # Set specific media as cover image
):
    return await handle_update_property(
        property_id=property_id,
        title=title,
        property_type=property_type,
        status=status,
        price=price,
        description=description,
        furnishing=furnishing,
        area_sqft=area_sqft,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        floors=floors,
        lease_term=lease_term,
        application_fee=application_fee,
        pet_policy=pet_policy,
        property_management_contact=property_management_contact,
        website=website,
        deposit=deposit,
        address=address,
        city=city,
        state=state,
        pincode=pincode,
        latitude=latitude,
        longitude=longitude,
        utilities=utilities,
        amenities=amenities,
        appliances_included=appliances_included,
        media_files=media_files,
        remove_media_ids=remove_media_ids,
        set_cover_media_id=set_cover_media_id
    )

@router.delete("/admin/properties/{property_id}",
    summary="[ADMIN] Delete property",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def delete_property(property_id: str):
    return await handle_delete_property(property_id)

@router.get("/admin/properties",
    summary="[ADMIN] Get all properties with advanced filtering",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def admin_get_all_properties(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    property_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    bedrooms: Optional[int] = Query(None),
    furnishing: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    sort_order: Optional[str] = Query("desc")
):
    return await handle_get_all_properties(
        page=page,
        limit=limit,
        search=search,
        property_type=property_type,
        status=status,
        city=city,
        min_price=min_price,
        max_price=max_price,
        bedrooms=bedrooms,
        furnishing=furnishing,
        sort_by=sort_by,
        sort_order=sort_order,
        admin_view=True
    )

@router.get("/admin/properties/{property_id}",
    summary="[ADMIN] Get property by ID with full details",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def admin_get_property_by_id(property_id: str):
    return await handle_get_property_by_id(property_id, admin_view=True)

# === USER PROPERTY ROUTES (Public/Read-only) ===
# Users can only view available properties

@router.get("/properties",
    summary="[PUBLIC] Get available properties for users"
)
async def get_available_properties(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),  # Lower limit for public users
    search: Optional[str] = Query(None),
    property_type: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    bedrooms: Optional[int] = Query(None),
    furnishing: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    sort_order: Optional[str] = Query("desc")
):
    return await handle_get_all_properties(
        page=page,
        limit=limit,
        search=search,
        property_type=property_type,
        status="available",  # Force to only show available properties
        city=city,
        min_price=min_price,
        max_price=max_price,
        bedrooms=bedrooms,
        furnishing=furnishing,
        sort_by=sort_by,
        sort_order=sort_order,
        admin_view=False
    )

@router.get("/properties/{property_id}",
    summary="[PUBLIC] Get single property details for users"
)
async def get_property_details(property_id: str):
    return await handle_get_property_by_id(property_id, admin_view=False)


@router.post("/test-media-upload",
    summary="[TEST] Test media file upload functionality"
)
async def test_media_upload(
    files: List[UploadFile] = File(...)
):
    """Test endpoint to verify media file upload is working"""
    try:
        from config.fileUpload import handle_general_media_upload
        
        print(f"🧪 TEST ROUTE: Received {len(files)} files")
        for i, file in enumerate(files):
            print(f"🧪 TEST ROUTE: File {i}: {file.filename} - Content-Type: {file.content_type}")
        
        # Process files using our general upload function
        result = await handle_general_media_upload(
            files=files,
            upload_type="property",
            max_files=10,
            compress_images=True,
            quality=85
        )
        
        return {
            "success": True,
            "message": f"Successfully processed {result['file_count']} files",
            "data": {
                "processed_files": len(result['processed_files']),
                "file_count": result['file_count'],
                "errors": result['errors'],
                "file_info": result['file_info']
            }
        }
        
    except Exception as e:
        print(f"🧪 TEST ROUTE ERROR: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Test upload failed"
        }


@router.post("/simple-file-test")
async def simple_file_test(
    files: List[UploadFile] = File(default=[])
):
    """Simplest possible file upload test - no auth, no processing"""
    print(f"🔥 SIMPLE TEST: Received {len(files)} files")
    
    file_details = []
    for i, file in enumerate(files):
        print(f"🔥 SIMPLE TEST: File {i}: {file.filename}")
        file_details.append({
            "index": i,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": getattr(file, 'size', 'unknown')
        })
    
    return {
        "success": True,
        "files_received": len(files),
        "file_details": file_details
    }