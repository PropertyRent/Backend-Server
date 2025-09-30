from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, Request
from typing import Optional, List, Union
from controller.propertyController import (
    handle_create_property,
    handle_update_property,
    handle_delete_property,
    handle_get_properties_admin,
    handle_get_properties_public,
    handle_get_property_by_id,
    handle_get_property_cover_image,
    handle_get_all_property_cover_images,
    get_property_stats,
    get_recent_properties
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
    # Debug media files in update route
    print(f"🔄 UPDATE ROUTE DEBUG: media_files received = {media_files}")
    print(f"🔄 UPDATE ROUTE DEBUG: media_files type = {type(media_files)}")
    print(f"🔄 UPDATE ROUTE DEBUG: len(media_files) = {len(media_files)}")
    if media_files and len(media_files) > 0:
        for i, mf in enumerate(media_files):
            print(f"🔄 UPDATE ROUTE DEBUG: File {i}: {mf.filename if hasattr(mf, 'filename') else 'NO_FILENAME'} - Size: {getattr(mf, 'size', 'unknown')}")
    else:
        print("🔄 UPDATE ROUTE DEBUG: No files received or empty list")
    
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



# === PROPERTY VIEWING ROUTES (Public Access) ===
# No authentication required - accessible to everyone including admins

@router.get("/properties",
    summary="Get all properties with comprehensive filtering"
)
async def get_all_properties(
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of properties per page"),
    
    # Text search - searches in title, description, property_type, city
    keyword: Optional[str] = Query(None, description="Search keyword in title, description, type, city"),
    
    # Property characteristics
    property_type: Optional[str] = Query(None, description="Property type (apartment, house, studio, etc.)"),
    city: Optional[str] = Query(None, description="City name"),
    state: Optional[str] = Query(None, description="State name"),
    furnishing: Optional[str] = Query(None, description="Furnishing type (furnished, unfurnished, semi-furnished)"),
    
    # Price filtering
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    
    # Room specifications
    bedrooms: Optional[int] = Query(None, ge=0, description="Number of bedrooms"),
    bathrooms: Optional[int] = Query(None, ge=0, description="Number of bathrooms"),
    # Pet policy
    pets_allowed: Optional[bool] = Query(None, description="Filter by pet-friendly properties"),
    
    # Move-in date filtering
    available_from_date: Optional[str] = Query(None, description="Available from date (YYYY-MM-DD)"),
    
    # Property status (all users can filter by status)
    status: Optional[str] = Query(None, description="Property status (available, rented, maintenance)")
):
    """
    Get all properties with comprehensive filtering and search capabilities.
    
    **Search Options:**
    - **keyword**: Searches in title, description, property_type, and city
    - **Single filters**: property_type, city, bedrooms, bathrooms, etc.
    - **Price Range**: min_price and max_price for budget filtering
    - **Combination filters**: Use multiple parameters together
    
    **Examples:**
    - `/properties?keyword=apartment&city=mumbai` - Search apartments in Mumbai
    - `/properties?min_price=10000&max_price=25000&bedrooms=2` - 2BHK under ₹25k
    - `/properties?min_price=15000` - Properties above ₹15,000
    - `/properties?max_price=30000` - Properties under ₹30,000
    - `/properties?pets_allowed=true&furnishing=furnished` - Pet-friendly furnished properties
    """
    # Use the public function which can handle all properties
    # Admin users can access this same endpoint to see all properties
    return await handle_get_properties_public(
        page=page,
        limit=limit,
        keyword=keyword,
        property_type=property_type,
        city=city,
        state=state,
        furnishing=furnishing,
        min_price=min_price,
        max_price=max_price,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        pets_allowed=pets_allowed,
        available_from_date=available_from_date,
        status=status
    )

@router.get("/properties/{property_id}",
    summary="Get property details by ID"
)
async def get_property_by_id(property_id: str):
    # Public access - no authentication required
    # Set is_admin=True to allow viewing all properties (not just available ones)
    # This ensures admins and public users can see the same properties
    return await handle_get_property_by_id(property_id, is_admin=True)

# === PROPERTY COVER IMAGE ROUTES (Public Access) ===
# Get cover images for properties - no authentication required

@router.get("/properties/{property_id}/cover-image",
    summary="Get cover image for a specific property (Public Access)"
)
async def get_property_cover_image(property_id: str):
    """
    Get the cover image for a specific property.
    Returns the media file where is_cover=True, or the first available image as fallback.
    """
    return await handle_get_property_cover_image(property_id)

@router.get("/properties/cover-images/all",
    summary="Get all property cover images (Public Access)"
)
async def get_all_property_cover_images():
    """
    Get cover images for all properties.
    Returns all media files where is_cover=True across all properties.
    """
    return await handle_get_all_property_cover_images()


@router.get("/admin/properties/stats",
    summary="[ADMIN] Get property statistics for dashboard",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def get_admin_property_stats():
    """
    Get comprehensive property statistics for admin dashboard:
    - Total properties count
    - Available properties count  
    - Rented properties count
    - Maintenance properties count
    - Occupancy rate percentage
    """
    return await get_property_stats()


@router.get("/admin/properties/recent",
    summary="[ADMIN] Get recent properties",
    dependencies=[Depends(check_for_authentication_cookie), Depends(require_admin)]
)
async def get_admin_recent_properties(limit: int = Query(3, ge=1, le=10, description="Number of recent properties to fetch")):
    """
    Get recently created properties for admin dashboard.
    Returns properties ordered by creation date (newest first).
    Includes comprehensive property details and all associated media files.
    """
    return await get_recent_properties(limit)

