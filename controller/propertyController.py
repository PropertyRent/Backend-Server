import uuid
from typing import List, Optional
from fastapi import HTTPException, Query
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

from model.propertyModel import Property
from model.propertyMediaModel import PropertyMedia
from schemas.propertySchemas import PropertyCreate, PropertyUpdate, PropertyOut
from schemas.propertyMediaSchemas import PropertyMediaCreate, PropertyMediaUpdate, PropertyMediaResponse


async def add_property(property_data: PropertyCreate):
    """Create a new property"""
    try:
        print(f" Creating new property: {property_data.title}")
        
        # Create the property
        new_property = await Property.create(**property_data.dict())
        print(f" Property created with ID: {new_property.id}")
        
        # Fetch the property with media
        property_with_media = await Property.get(id=new_property.id).prefetch_related('media')
        
        return JSONResponse(
            status_code=HTTP_201_CREATED,
            content={
                "success": True,
                "message": "Property created successfully",
                "data": {
                    "id": str(property_with_media.id),
                    "title": property_with_media.title,
                    "description": property_with_media.description,
                    "property_type": property_with_media.property_type,
                    "status": property_with_media.status,
                    "furnishing": property_with_media.furnishing,
                    "area_sqft": float(property_with_media.area_sqft) if property_with_media.area_sqft else None,
                    "bedrooms": property_with_media.bedrooms,
                    "bathrooms": property_with_media.bathrooms,
                    "floors": property_with_media.floors,
                    "utilities": property_with_media.utilities,
                    "lease_term": property_with_media.lease_term,
                    "application_fee": float(property_with_media.application_fee) if property_with_media.application_fee else None,
                    "amenities": property_with_media.amenities,
                    "pet_policy": property_with_media.pet_policy,
                    "appliances_included": property_with_media.appliances_included,
                    "property_management_contact": property_with_media.property_management_contact,
                    "website": property_with_media.website,
                    "price": float(property_with_media.price),
                    "deposit": float(property_with_media.deposit) if property_with_media.deposit else None,
                    "address": property_with_media.address,
                    "city": property_with_media.city,
                    "state": property_with_media.state,
                    "pincode": property_with_media.pincode,
                    "latitude": float(property_with_media.latitude) if property_with_media.latitude else None,
                    "longitude": float(property_with_media.longitude) if property_with_media.longitude else None,
                    "available_from": property_with_media.available_from.isoformat() if property_with_media.available_from else None,
                    "created_at": property_with_media.created_at.isoformat(),
                    "updated_at": property_with_media.updated_at.isoformat(),
                    "media": [
                        {
                            "id": str(media.id),
                            "media_type": media.media_type,
                            "url": media.url,
                            "is_cover": media.is_cover,
                            "created_at": media.created_at.isoformat(),
                            "updated_at": media.updated_at.isoformat()
                        }
                        for media in property_with_media.media
                    ]
                }
            }
        )
    except IntegrityError as e:
        print(f" Property creation failed - integrity error: {e}")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Property creation failed due to data integrity issues"
        )
    except Exception as e:
        print(f" Property creation failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create property"
        )


async def update_property(property_id: str, property_data: PropertyUpdate):
    """Update an existing property"""
    try:
        # Validate UUID
        try:
            property_uuid = uuid.UUID(property_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid property ID format"
            )
        
        # Check if property exists
        property_obj = await Property.get_or_none(id=property_uuid)
        if not property_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        # Update only provided fields
        update_data = property_data.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        print(f" Updating property {property_id} with data: {update_data}")
        
        # Update the property
        await property_obj.update_from_dict(update_data)
        await property_obj.save()
        
        # Fetch updated property with media
        updated_property = await Property.get(id=property_uuid).prefetch_related('media')
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": "Property updated successfully",
                "data": {
                    "id": str(updated_property.id),
                    "title": updated_property.title,
                    "description": updated_property.description,
                    "property_type": updated_property.property_type,
                    "status": updated_property.status,
                    "furnishing": updated_property.furnishing,
                    "area_sqft": float(updated_property.area_sqft) if updated_property.area_sqft else None,
                    "bedrooms": updated_property.bedrooms,
                    "bathrooms": updated_property.bathrooms,
                    "floors": updated_property.floors,
                    "utilities": updated_property.utilities,
                    "lease_term": updated_property.lease_term,
                    "application_fee": float(updated_property.application_fee) if updated_property.application_fee else None,
                    "amenities": updated_property.amenities,
                    "pet_policy": updated_property.pet_policy,
                    "appliances_included": updated_property.appliances_included,
                    "property_management_contact": updated_property.property_management_contact,
                    "website": updated_property.website,
                    "price": float(updated_property.price),
                    "deposit": float(updated_property.deposit) if updated_property.deposit else None,
                    "address": updated_property.address,
                    "city": updated_property.city,
                    "state": updated_property.state,
                    "pincode": updated_property.pincode,
                    "latitude": float(updated_property.latitude) if updated_property.latitude else None,
                    "longitude": float(updated_property.longitude) if updated_property.longitude else None,
                    "available_from": updated_property.available_from.isoformat() if updated_property.available_from else None,
                    "created_at": updated_property.created_at.isoformat(),
                    "updated_at": updated_property.updated_at.isoformat(),
                    "media": [
                        {
                            "id": str(media.id),
                            "media_type": media.media_type,
                            "url": media.url,
                            "is_cover": media.is_cover,
                            "created_at": media.created_at.isoformat(),
                            "updated_at": media.updated_at.isoformat()
                        }
                        for media in updated_property.media
                    ]
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f" Property update failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update property"
        )


async def delete_property(property_id: str):
    """Delete a property and all its associated media"""
    try:
        # Validate UUID
        try:
            property_uuid = uuid.UUID(property_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid property ID format"
            )
        
        # Check if property exists
        property_obj = await Property.get_or_none(id=property_uuid)
        if not property_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        print(f" Deleting property: {property_obj.title}")
        
        # Delete property (media will be deleted due to CASCADE)
        async with in_transaction():
            await property_obj.delete()
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": "Property deleted successfully"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f" Property deletion failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete property"
        )


async def get_all_properties(
    limit: int = Query(10, ge=1, le=100, description="Number of properties to return"),
    offset: int = Query(0, ge=0, description="Number of properties to skip"),
    city: Optional[str] = Query(None, description="Filter by city"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    bedrooms: Optional[int] = Query(None, ge=0, description="Filter by number of bedrooms")
):
    """Get all properties with optional filtering and pagination"""
    try:
        print(f" Fetching properties with filters: city={city}, type={property_type}, status={status}")
        
        # Build query
        query = Property.all()
        
        # Apply filters
        if city:
            query = query.filter(city__icontains=city)
        if property_type:
            query = query.filter(property_type__icontains=property_type)
        if status:
            query = query.filter(status__icontains=status)
        if min_price is not None:
            query = query.filter(price__gte=min_price)
        if max_price is not None:
            query = query.filter(price__lte=max_price)
        if bedrooms is not None:
            query = query.filter(bedrooms=bedrooms)
        
        # Get total count
        total = await query.count()
        
        # Apply pagination and fetch with media
        properties = await query.prefetch_related('media').offset(offset).limit(limit)
        
        # Format response
        property_list = []
        for prop in properties:
            property_list.append({
                "id": str(prop.id),
                "title": prop.title,
                "description": prop.description,
                "property_type": prop.property_type,
                "status": prop.status,
                "furnishing": prop.furnishing,
                "area_sqft": float(prop.area_sqft) if prop.area_sqft else None,
                "bedrooms": prop.bedrooms,
                "bathrooms": prop.bathrooms,
                "floors": prop.floors,
                "utilities": prop.utilities,
                "lease_term": prop.lease_term,
                "application_fee": float(prop.application_fee) if prop.application_fee else None,
                "amenities": prop.amenities,
                "pet_policy": prop.pet_policy,
                "appliances_included": prop.appliances_included,
                "property_management_contact": prop.property_management_contact,
                "website": prop.website,
                "price": float(prop.price),
                "deposit": float(prop.deposit) if prop.deposit else None,
                "address": prop.address,
                "city": prop.city,
                "state": prop.state,
                "pincode": prop.pincode,
                "latitude": float(prop.latitude) if prop.latitude else None,
                "longitude": float(prop.longitude) if prop.longitude else None,
                "available_from": prop.available_from.isoformat() if prop.available_from else None,
                "created_at": prop.created_at.isoformat(),
                "updated_at": prop.updated_at.isoformat(),
                "media": [
                    {
                        "id": str(media.id),
                        "media_type": media.media_type,
                        "url": media.url,
                        "is_cover": media.is_cover,
                        "created_at": media.created_at.isoformat(),
                        "updated_at": media.updated_at.isoformat()
                    }
                    for media in prop.media
                ]
            })
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "data": {
                    "properties": property_list,
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
        print(f" Failed to fetch properties: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch properties"
        )


async def get_property_by_id(property_id: str):
    """Get a single property by ID"""
    try:
        # Validate UUID
        try:
            property_uuid = uuid.UUID(property_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid property ID format"
            )
        
        # Fetch property with media
        property_obj = await Property.get_or_none(id=property_uuid).prefetch_related('media')
        if not property_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        print(f" Fetched property: {property_obj.title}")
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "data": {
                    "id": str(property_obj.id),
                    "title": property_obj.title,
                    "description": property_obj.description,
                    "property_type": property_obj.property_type,
                    "status": property_obj.status,
                    "furnishing": property_obj.furnishing,
                    "area_sqft": float(property_obj.area_sqft) if property_obj.area_sqft else None,
                    "bedrooms": property_obj.bedrooms,
                    "bathrooms": property_obj.bathrooms,
                    "floors": property_obj.floors,
                    "utilities": property_obj.utilities,
                    "lease_term": property_obj.lease_term,
                    "application_fee": float(property_obj.application_fee) if property_obj.application_fee else None,
                    "amenities": property_obj.amenities,
                    "pet_policy": property_obj.pet_policy,
                    "appliances_included": property_obj.appliances_included,
                    "property_management_contact": property_obj.property_management_contact,
                    "website": property_obj.website,
                    "price": float(property_obj.price),
                    "deposit": float(property_obj.deposit) if property_obj.deposit else None,
                    "address": property_obj.address,
                    "city": property_obj.city,
                    "state": property_obj.state,
                    "pincode": property_obj.pincode,
                    "latitude": float(property_obj.latitude) if property_obj.latitude else None,
                    "longitude": float(property_obj.longitude) if property_obj.longitude else None,
                    "available_from": property_obj.available_from.isoformat() if property_obj.available_from else None,
                    "created_at": property_obj.created_at.isoformat(),
                    "updated_at": property_obj.updated_at.isoformat(),
                    "media": [
                        {
                            "id": str(media.id),
                            "media_type": media.media_type,
                            "url": media.url,
                            "is_cover": media.is_cover,
                            "created_at": media.created_at.isoformat(),
                            "updated_at": media.updated_at.isoformat()
                        }
                        for media in property_obj.media
                    ]
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f" Failed to fetch property: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch property"
        )


async def delete_property_media(media_id: str):
    """Delete a specific property media item"""
    try:
        # Validate UUID
        try:
            media_uuid = uuid.UUID(media_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid media ID format"
            )
        
        # Check if media exists
        media_obj = await PropertyMedia.get_or_none(id=media_uuid)
        if not media_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Property media not found"
            )
        
        print(f" Deleting property media: {media_obj.url}")
        
        # Delete media
        await media_obj.delete()
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": "Property media deleted successfully"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f" Media deletion failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete property media"
        )


# === NEW INTEGRATED PROPERTY + MEDIA HANDLERS ===

from fastapi import UploadFile
from config.fileUpload import process_property_media, handle_general_media_upload
import json

def parse_comma_separated_list(value: Optional[str]) -> Optional[List[str]]:
    """Parse comma-separated string into list"""
    if not value or not value.strip():
        return None
    return [item.strip() for item in value.split(',') if item.strip()]

async def handle_create_property(
    title: str,
    property_type: str,
    status: str,
    price: float,
    description: Optional[str] = None,
    furnishing: Optional[str] = None,
    area_sqft: Optional[float] = None,
    bedrooms: Optional[int] = None,
    bathrooms: Optional[int] = None,
    floors: Optional[int] = None,
    lease_term: Optional[str] = None,
    application_fee: Optional[float] = None,
    pet_policy: Optional[str] = None,
    property_management_contact: Optional[str] = None,
    website: Optional[str] = None,
    deposit: Optional[float] = None,
    address: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    pincode: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    utilities: Optional[str] = None,
    amenities: Optional[str] = None,
    appliances_included: Optional[str] = None,
    media_files: Optional[List[UploadFile]] = None
):
    """Create property with optional media files"""
    try:
        print(f"🏠 Creating new property: {title}")
        
        # Parse JSON fields from comma-separated strings
        utilities_list = parse_comma_separated_list(utilities)
        amenities_list = parse_comma_separated_list(amenities)
        appliances_list = parse_comma_separated_list(appliances_included)
        
        # Create property data
        property_data = {
            "title": title,
            "property_type": property_type,
            "status": status,
            "price": price,
            "description": description,
            "furnishing": furnishing,
            "area_sqft": area_sqft,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "floors": floors,
            "lease_term": lease_term,
            "application_fee": application_fee,
            "pet_policy": pet_policy,
            "property_management_contact": property_management_contact,
            "website": website,
            "deposit": deposit,
            "address": address,
            "city": city,
            "state": state,
            "pincode": pincode,
            "latitude": latitude,
            "longitude": longitude,
            "utilities": utilities_list,
            "amenities": amenities_list,
            "appliances_included": appliances_list
        }
        
        # Remove None values
        property_data = {k: v for k, v in property_data.items() if v is not None}
        
        async with in_transaction():
            # Create the property
            new_property = await Property.create(**property_data)
            print(f"✅ Property created with ID: {new_property.id}")
            
            media_results = []
            
            # Debug media files
            print(f"🔍 Debug: media_files = {media_files}")
            print(f"🔍 Debug: media_files type = {type(media_files)}")
            if media_files:
                print(f"🔍 Debug: len(media_files) = {len(media_files)}")
                for i, mf in enumerate(media_files):
                    print(f"🔍 Debug: media_file[{i}] = {mf}, filename = {getattr(mf, 'filename', 'NO_FILENAME')}")
            
            # Process media files using general upload function
            if media_files and len(media_files) > 0:
                print(f"📸 Processing {len(media_files)} media files using general upload function...")
                
                try:
                    # Use the new general media upload function
                    upload_result = await handle_general_media_upload(
                        files=media_files,
                        upload_type="property",
                        max_files=20,
                        compress_images=True,
                        quality=85,
                        max_width=1920,
                        max_height=1080
                    )
                    
                    if upload_result['success'] and upload_result['processed_files']:
                        print(f"📸 Successfully processed {upload_result['file_count']} files")
                        
                        # Create database records for each processed file
                        for i, (base64_url, file_info) in enumerate(zip(upload_result['processed_files'], upload_result['file_info'])):
                            try:
                                media_record = await PropertyMedia.create(
                                    property=new_property,
                                    media_type=file_info.get('media_type', 'image'),
                                    url=base64_url,
                                    is_cover=(i == 0)  # First image is cover by default
                                )
                                
                                media_results.append({
                                    "id": str(media_record.id),
                                    "media_type": media_record.media_type,
                                    "url": media_record.url,
                                    "is_cover": media_record.is_cover,
                                    "created_at": media_record.created_at.isoformat(),
                                    "updated_at": media_record.updated_at.isoformat(),
                                    "original_filename": file_info.get('original_filename'),
                                    "file_size_mb": file_info.get('size_mb')
                                })
                                
                                print(f"✅ Database record created for file {i+1}")
                                
                            except Exception as db_error:
                                print(f"❌ Failed to create database record for file {i+1}: {db_error}")
                    
                    # Log any errors from processing
                    if upload_result['errors']:
                        print(f"⚠️ Some files had errors: {upload_result['errors']}")
                    
                    print(f"✅ Final result: {len(media_results)} media files successfully added to property")
                    
                except Exception as upload_error:
                    print(f"❌ Media upload processing failed: {upload_error}")
                    # Continue with property creation even if media fails
        
        # Return complete property data
        return {
            "success": True,
            "message": f"Property created successfully with {len(media_results)} media files",
            "data": {
                "id": str(new_property.id),
                "title": new_property.title,
                "description": new_property.description,
                "property_type": new_property.property_type,
                "status": new_property.status,
                "furnishing": new_property.furnishing,
                "area_sqft": float(new_property.area_sqft) if new_property.area_sqft else None,
                "bedrooms": new_property.bedrooms,
                "bathrooms": new_property.bathrooms,
                "floors": new_property.floors,
                "utilities": new_property.utilities,
                "amenities": new_property.amenities,
                "appliances_included": new_property.appliances_included,
                "lease_term": new_property.lease_term,
                "application_fee": float(new_property.application_fee) if new_property.application_fee else None,
                "pet_policy": new_property.pet_policy,
                "property_management_contact": new_property.property_management_contact,
                "website": new_property.website,
                "price": float(new_property.price),
                "deposit": float(new_property.deposit) if new_property.deposit else None,
                "address": new_property.address,
                "city": new_property.city,
                "state": new_property.state,
                "pincode": new_property.pincode,
                "latitude": float(new_property.latitude) if new_property.latitude else None,
                "longitude": float(new_property.longitude) if new_property.longitude else None,
                "available_from": new_property.available_from.isoformat() if new_property.available_from else None,
                "created_at": new_property.created_at.isoformat(),
                "updated_at": new_property.updated_at.isoformat(),
                "media": media_results,
                "media_count": len(media_results)
            }
        }
        
    except Exception as e:
        print(f"❌ Property creation failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create property: {str(e)}"
        )


async def handle_update_property(
    property_id: str,
    title: Optional[str] = None,
    property_type: Optional[str] = None,
    status: Optional[str] = None,
    price: Optional[float] = None,
    description: Optional[str] = None,
    furnishing: Optional[str] = None,
    area_sqft: Optional[float] = None,
    bedrooms: Optional[int] = None,
    bathrooms: Optional[int] = None,
    floors: Optional[int] = None,
    lease_term: Optional[str] = None,
    application_fee: Optional[float] = None,
    pet_policy: Optional[str] = None,
    property_management_contact: Optional[str] = None,
    website: Optional[str] = None,
    deposit: Optional[float] = None,
    address: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    pincode: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    utilities: Optional[str] = None,
    amenities: Optional[str] = None,
    appliances_included: Optional[str] = None,
    media_files: Optional[List[UploadFile]] = None,
    set_cover_media_id: Optional[str] = None,
    remove_media_ids: Optional[str] = None  # Comma-separated media IDs to remove
):
    """Update property with optional media operations"""
    try:
        print(f"🏠 Updating property: {property_id}")
        
        # Check if property exists
        property_obj = await Property.filter(id=property_id).first()
        if not property_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        async with in_transaction():
            # Prepare update data
            update_data = {}
            
            # Parse comma-separated list fields
            if utilities is not None:
                update_data["utilities"] = parse_comma_separated_list(utilities)
            if amenities is not None:
                update_data["amenities"] = parse_comma_separated_list(amenities)
            if appliances_included is not None:
                update_data["appliances_included"] = parse_comma_separated_list(appliances_included)
            
            # Add basic fields if provided
            field_mapping = {
                "title": title,
                "property_type": property_type,
                "status": status,
                "price": price,
                "description": description,
                "furnishing": furnishing,
                "area_sqft": area_sqft,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "floors": floors,
                "lease_term": lease_term,
                "application_fee": application_fee,
                "pet_policy": pet_policy,
                "property_management_contact": property_management_contact,
                "website": website,
                "deposit": deposit,
                "address": address,
                "city": city,
                "state": state,
                "pincode": pincode,
                "latitude": latitude,
                "longitude": longitude
            }
            
            for field_name, field_value in field_mapping.items():
                if field_value is not None:
                    update_data[field_name] = field_value
            
            # Update property if there's data to update
            if update_data:
                print(f"📝 Updating fields: {list(update_data.keys())}")
                await Property.filter(id=property_id).update(**update_data)
                print("✅ Property basic fields updated")
            
            # Handle media removal
            media_removed_count = 0
            if remove_media_ids and remove_media_ids.strip():
                remove_ids = [id.strip() for id in remove_media_ids.split(',') if id.strip()]
                print(f"🗑️ Removing media IDs: {remove_ids}")
                
                for media_id in remove_ids:
                    try:
                        deleted_count = await PropertyMedia.filter(
                            id=media_id, 
                            property_id=property_id
                        ).delete()
                        if deleted_count > 0:
                            media_removed_count += 1
                            print(f"✅ Removed media {media_id}")
                        else:
                            print(f"⚠️ Media {media_id} not found or doesn't belong to this property")
                    except Exception as e:
                        print(f"❌ Failed to remove media {media_id}: {e}")
            
            # Handle cover image setting
            if set_cover_media_id and set_cover_media_id.strip():
                print(f"🎯 Setting cover image: {set_cover_media_id}")
                
                # Remove cover from all existing media
                await PropertyMedia.filter(property_id=property_id).update(is_cover=False)
                
                # Set new cover
                cover_updated = await PropertyMedia.filter(
                    id=set_cover_media_id, 
                    property_id=property_id
                ).update(is_cover=True)
                
                if cover_updated > 0:
                    print("✅ Cover image updated")
                else:
                    print("⚠️ Cover media not found or doesn't belong to this property")
            
            # Handle new media files using general upload function (same as create)
            media_added_count = 0
            new_media_results = []
            if media_files and len(media_files) > 0:
                print(f"📸 Adding {len(media_files)} new media files using general upload function...")
                
                try:
                    # Use the same general media upload function as create
                    upload_result = await handle_general_media_upload(
                        files=media_files,
                        upload_type="property",
                        max_files=20,
                        compress_images=True,
                        quality=85,
                        max_width=1920,
                        max_height=1080
                    )
                    
                    if upload_result['success'] and upload_result['processed_files']:
                        print(f"📸 Successfully processed {upload_result['file_count']} files for update")
                        
                        # Create database records for each processed file
                        for i, (base64_url, file_info) in enumerate(zip(upload_result['processed_files'], upload_result['file_info'])):
                            try:
                                media_record = await PropertyMedia.create(
                                    property=property_obj,
                                    media_type=file_info.get('media_type', 'image'),
                                    url=base64_url,
                                    is_cover=False  # Don't auto-set as cover for updates
                                )
                                
                                new_media_results.append({
                                    "id": str(media_record.id),
                                    "media_type": media_record.media_type,
                                    "url": media_record.url,
                                    "is_cover": media_record.is_cover,
                                    "created_at": media_record.created_at.isoformat(),
                                    "updated_at": media_record.updated_at.isoformat(),
                                    "original_filename": file_info.get('original_filename'),
                                    "file_size_mb": file_info.get('size_mb')
                                })
                                
                                media_added_count += 1
                                print(f"✅ Database record created for update file {i+1}")
                                
                            except Exception as db_error:
                                print(f"❌ Failed to create database record for update file {i+1}: {db_error}")
                    
                    # Log any errors from processing
                    if upload_result['errors']:
                        print(f"⚠️ Some update files had errors: {upload_result['errors']}")
                    
                    print(f"✅ Final update result: {media_added_count} media files successfully added to property")
                    
                except Exception as upload_error:
                    print(f"❌ Media upload processing failed during update: {upload_error}")
                    # Continue with property update even if media fails
        
        # Get updated property with current media
        # Fix: Use get_or_none to handle potential duplicates gracefully
        updated_property = await Property.filter(id=property_id).first()
        if not updated_property:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Property not found after update"
            )
        current_media = await PropertyMedia.filter(property_id=property_id).all()
        
        # Format current media data
        current_media_data = []
        for media in current_media:
            current_media_data.append({
                "id": str(media.id),
                "media_type": media.media_type,
                "url": media.url,
                "is_cover": media.is_cover,
                "created_at": media.created_at.isoformat(),
                "updated_at": media.updated_at.isoformat()
            })
        
        # Create summary message
        operations = []
        if update_data:
            operations.append(f"updated {len(update_data)} fields")
        if media_added_count > 0:
            operations.append(f"added {media_added_count} media files")
        if media_removed_count > 0:
            operations.append(f"removed {media_removed_count} media files")
        if set_cover_media_id:
            operations.append("updated cover image")
        
        operation_summary = ", ".join(operations) if operations else "no changes made"
        
        return {
            "success": True,
            "message": f"Property updated successfully: {operation_summary}",
            "data": {
                "id": str(updated_property.id),
                "title": updated_property.title,
                "description": updated_property.description,
                "property_type": updated_property.property_type,
                "status": updated_property.status,
                "furnishing": updated_property.furnishing,
                "area_sqft": float(updated_property.area_sqft) if updated_property.area_sqft else None,
                "bedrooms": updated_property.bedrooms,
                "bathrooms": updated_property.bathrooms,
                "floors": updated_property.floors,
                "utilities": updated_property.utilities,
                "amenities": updated_property.amenities,
                "appliances_included": updated_property.appliances_included,
                "lease_term": updated_property.lease_term,
                "application_fee": float(updated_property.application_fee) if updated_property.application_fee else None,
                "pet_policy": updated_property.pet_policy,
                "property_management_contact": updated_property.property_management_contact,
                "website": updated_property.website,
                "price": float(updated_property.price),
                "deposit": float(updated_property.deposit) if updated_property.deposit else None,
                "address": updated_property.address,
                "city": updated_property.city,
                "state": updated_property.state,
                "pincode": updated_property.pincode,
                "latitude": float(updated_property.latitude) if updated_property.latitude else None,
                "longitude": float(updated_property.longitude) if updated_property.longitude else None,
                "available_from": updated_property.available_from.isoformat() if updated_property.available_from else None,
                "created_at": updated_property.created_at.isoformat(),
                "updated_at": updated_property.updated_at.isoformat(),
                "media": current_media_data,
                "media_count": len(current_media_data),
                "operations_performed": {
                    "fields_updated": len(update_data),
                    "media_added": media_added_count,
                    "media_removed": media_removed_count,
                    "cover_updated": bool(set_cover_media_id)
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Property update failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update property: {str(e)}"
        )


async def handle_delete_property(property_id: str):
    """Delete property and all its media"""
    try:
        print(f"🗑️ Deleting property: {property_id}")
        
        # Check if property exists
        property_obj = await Property.get_or_none(id=property_id)
        if not property_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        async with in_transaction():
            # Delete all media first
            media_count = await PropertyMedia.filter(property_id=property_id).count()
            await PropertyMedia.filter(property_id=property_id).delete()
            print(f"🗑️ Deleted {media_count} media records")
            
            # Delete the property
            await Property.filter(id=property_id).delete()
            print("✅ Property deleted successfully")
        
        return {
            "success": True,
            "message": f"Property and {media_count} associated media files deleted successfully",
            "data": {
                "deleted_property_id": property_id,
                "deleted_media_count": media_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Property deletion failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete property: {str(e)}"
        )


async def handle_get_properties_admin(
    page: int = 1,
    limit: int = 10,
    keyword: Optional[str] = None,
    property_type: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    furnishing: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    bedrooms: Optional[int] = None,
    bathrooms: Optional[int] = None,
    pets_allowed: Optional[bool] = None,
    available_from_date: Optional[str] = None,
    status: Optional[str] = None
):
    """Get all properties for admin with comprehensive filtering (admin can see all statuses)"""
    try:
        print(f"👑 Admin fetching properties - Page {page}, Limit {limit}")
        print(f"🔍 Filters: keyword={keyword}, type={property_type}, city={city}, status={status}")
        
        # Base query - admin can see all properties regardless of status
        query = Property.all()
        
        # === TEXT SEARCH (keyword) ===
        if keyword and keyword.strip():
            search_term = keyword.strip()
            print(f"🔍 Searching for keyword: '{search_term}'")
            
            # Search in multiple fields: title, description, property_type, city
            title_matches = await Property.filter(title__icontains=search_term).values_list('id', flat=True)
            desc_matches = await Property.filter(description__icontains=search_term).values_list('id', flat=True)
            type_matches = await Property.filter(property_type__icontains=search_term).values_list('id', flat=True)
            city_matches = await Property.filter(city__icontains=search_term).values_list('id', flat=True)
            
            # Combine all matching IDs (OR operation)
            all_matching_ids = set(title_matches) | set(desc_matches) | set(type_matches) | set(city_matches)
            
            if all_matching_ids:
                query = query.filter(id__in=list(all_matching_ids))
            else:
                # No matches found, return empty result
                return JSONResponse(
                    status_code=HTTP_200_OK,
                    content={
                        "success": True,
                        "message": f"No properties found matching keyword '{search_term}'",
                        "data": {
                            "properties": [],
                            "pagination": {
                                "total_count": 0,
                                "page": page,
                                "limit": limit,
                                "total_pages": 0
                            }
                        }
                    }
                )
        
        # === PROPERTY CHARACTERISTICS ===
        if property_type:
            query = query.filter(property_type__icontains=property_type)
        
        if city:
            query = query.filter(city__icontains=city)
        
        if state:
            query = query.filter(state__icontains=state)
        
        if furnishing:
            query = query.filter(furnishing__icontains=furnishing)
        
        if status:
            query = query.filter(status=status)
            print(f"🔍 Filter: status = {status}")
        
        # === PRICE FILTERING (Min/Max only) ===
        if min_price is not None:
            query = query.filter(price__gte=min_price)
        
        if max_price is not None:
            query = query.filter(price__lte=max_price)
        
        # === ROOM SPECIFICATIONS (Exact count only) ===
        if bedrooms is not None:
            query = query.filter(bedrooms=bedrooms)
        
        if bathrooms is not None:
            query = query.filter(bathrooms=bathrooms)
        
        # === PET POLICY FILTERING ===
        if pets_allowed is not None:
            if pets_allowed:
                # Search for pet-friendly keywords in pet_policy
                pet_friendly_ids = await Property.filter(
                    pet_policy__icontains="allowed"
                ).values_list('id', flat=True)
                
                pet_friendly_ids2 = await Property.filter(
                    pet_policy__icontains="yes"
                ).values_list('id', flat=True)
                
                pet_friendly_ids3 = await Property.filter(
                    pet_policy__icontains="welcome"
                ).values_list('id', flat=True)
                
                all_pet_friendly = set(pet_friendly_ids) | set(pet_friendly_ids2) | set(pet_friendly_ids3)
                
                if all_pet_friendly:
                    query = query.filter(id__in=list(all_pet_friendly))
                else:
                    # No pet-friendly properties found
                    query = query.filter(id=-1)
            else:
                # Filter out pet-friendly properties
                not_pet_friendly_ids = await Property.filter(
                    pet_policy__icontains="not allowed"
                ).values_list('id', flat=True)
                
                not_pet_friendly_ids2 = await Property.filter(
                    pet_policy__icontains="no pets"
                ).values_list('id', flat=True)
                
                all_not_pet_friendly = set(not_pet_friendly_ids) | set(not_pet_friendly_ids2)
                
                if all_not_pet_friendly:
                    query = query.filter(id__in=list(all_not_pet_friendly))
        
        # === MOVE-IN DATE FILTERING ===
        if available_from_date:
            try:
                from datetime import datetime
                move_in_date = datetime.strptime(available_from_date, "%Y-%m-%d")
                query = query.filter(available_from__lte=move_in_date)
            except ValueError:
                print(f"⚠️ Invalid date format: {available_from_date}")
                pass
        
        # Get total count before pagination
        total_count = await query.count()
        
        # Apply pagination and get results with media
        offset = (page - 1) * limit
        properties = await query.offset(offset).limit(limit).prefetch_related('media').all()
        
        # Format the results
        properties_data = []
        for property_obj in properties:
            # Get media for this property
            media_data = []
            for media in property_obj.media:
                media_data.append({
                    "id": str(media.id),
                    "media_type": media.media_type,
                    "url": media.url,
                    "is_cover": media.is_cover,
                    "created_at": media.created_at.isoformat(),
                    "updated_at": media.updated_at.isoformat()
                })
            
            # Sort media - cover first, then by creation date
            media_data.sort(key=lambda x: (not x["is_cover"], x["created_at"]))
            
            properties_data.append({
                "id": str(property_obj.id),
                "title": property_obj.title,
                "description": property_obj.description,
                "property_type": property_obj.property_type,
                "status": property_obj.status,
                "furnishing": property_obj.furnishing,
                "area_sqft": float(property_obj.area_sqft) if property_obj.area_sqft else None,
                "bedrooms": property_obj.bedrooms,
                "bathrooms": property_obj.bathrooms,
                "floors": property_obj.floors,
                "utilities": property_obj.utilities,
                "amenities": property_obj.amenities,
                "appliances_included": property_obj.appliances_included,
                "lease_term": property_obj.lease_term,
                "application_fee": float(property_obj.application_fee) if property_obj.application_fee else None,
                "pet_policy": property_obj.pet_policy,
                "property_management_contact": property_obj.property_management_contact,
                "website": property_obj.website,
                "price": float(property_obj.price),
                "deposit": float(property_obj.deposit) if property_obj.deposit else None,
                "address": property_obj.address,
                "city": property_obj.city,
                "state": property_obj.state,
                "pincode": property_obj.pincode,
                "latitude": float(property_obj.latitude) if property_obj.latitude else None,
                "longitude": float(property_obj.longitude) if property_obj.longitude else None,
                "available_from": property_obj.available_from.isoformat() if property_obj.available_from else None,
                "created_at": property_obj.created_at.isoformat(),
                "updated_at": property_obj.updated_at.isoformat(),
                "media": media_data,
                "media_count": len(media_data)
            })
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit  # Ceiling division
        
        print(f"✅ Found {len(properties)} properties (Total: {total_count})")
        
        # Build filter summary for response
        active_filters = {}
        if keyword:
            active_filters["keyword"] = keyword
        if property_type:
            active_filters["property_type"] = property_type
        if city:
            active_filters["city"] = city
        if state:
            active_filters["state"] = state
        if status:
            active_filters["status"] = status
        if min_price or max_price:
            active_filters["price_range"] = f"₹{min_price or 0} - ₹{max_price or 'unlimited'}"
        if bedrooms:
            active_filters["bedrooms"] = f"exactly {bedrooms}"
        if bathrooms:
            active_filters["bathrooms"] = f"exactly {bathrooms}"
        if pets_allowed is not None:
            active_filters["pets"] = "allowed" if pets_allowed else "not allowed"
        if available_from_date:
            active_filters["available_from"] = available_from_date
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": f"[ADMIN] Found {total_count} properties" + (f" matching your filters" if active_filters else ""),
                "data": {
                    "properties": properties_data,
                    "pagination": {
                        "current_page": page,
                        "per_page": limit,
                        "total_count": total_count,
                        "total_pages": total_pages,
                        "has_next": page < total_pages,
                        "has_prev": page > 1,
                        "showing": f"{min(offset + 1, total_count)}-{min(offset + limit, total_count)} of {total_count}"
                    },
                    "filters_applied": active_filters,
                    "filter_count": len(active_filters)
                }
            }
        )
        
    except Exception as e:
        print(f"❌ Failed to fetch properties: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch properties: {str(e)}"
        )


async def handle_get_properties_public(
    page: int = 1,
    limit: int = 10,
    keyword: Optional[str] = None,
    property_type: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    furnishing: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    bedrooms: Optional[int] = None,
    bathrooms: Optional[int] = None,
    pets_allowed: Optional[bool] = None,
    available_from_date: Optional[str] = None,
    status: Optional[str] = None
):
    """Get available properties for public/users with comprehensive filtering"""
    try:
        print(f"👥 Public fetching properties - Page {page}, Limit {limit}")
        print(f"🔍 Filters: keyword={keyword}, type={property_type}, city={city}, price={min_price}-{max_price}")
        
        # Base query - default to available properties unless status is specified
        if status:
            query = Property.filter(status=status)
        else:
            query = Property.filter()
        
        # === TEXT SEARCH (keyword) ===
        if keyword and keyword.strip():
            search_term = keyword.strip()
            print(f"🔍 Searching for keyword: '{search_term}'")
            
            # Search in multiple fields: title, description, property_type, city
            title_matches = await Property.filter(title__icontains=search_term).values_list('id', flat=True)
            desc_matches = await Property.filter(description__icontains=search_term).values_list('id', flat=True)
            type_matches = await Property.filter(property_type__icontains=search_term).values_list('id', flat=True)
            city_matches = await Property.filter(city__icontains=search_term).values_list('id', flat=True)
            
            # Combine all matching IDs (OR operation)
            all_matching_ids = set(title_matches) | set(desc_matches) | set(type_matches) | set(city_matches)
            
            if all_matching_ids:
                query = query.filter(id__in=list(all_matching_ids))
            else:
                # No matches found, return empty result
                return JSONResponse(
                    status_code=HTTP_200_OK,
                    content={
                        "success": True,
                        "message": f"No properties found matching keyword '{search_term}'",
                        "data": {
                            "properties": [],
                            "pagination": {
                                "total_count": 0,
                                "page": page,
                                "limit": limit,
                                "total_pages": 0
                            }
                        }
                    }
                )
        
        # === PROPERTY CHARACTERISTICS ===
        if property_type:
            query = query.filter(property_type__icontains=property_type)
        
        if city:
            query = query.filter(city__icontains=city)
        
        if state:
            query = query.filter(state__icontains=state)
        
        if furnishing:
            query = query.filter(furnishing__icontains=furnishing)
        
        # === PRICE FILTERING ===
        if min_price is not None:
            query = query.filter(price__gte=min_price)
        
        if max_price is not None:
            query = query.filter(price__lte=max_price)
        
        # === ROOM SPECIFICATIONS (Exact count only) ===
        if bedrooms is not None:
            query = query.filter(bedrooms=bedrooms)
        
        if bathrooms is not None:
            query = query.filter(bathrooms=bathrooms)
        
        # === PET POLICY FILTERING ===
        if pets_allowed is not None:
            if pets_allowed:
                # Search for pet-friendly keywords in pet_policy
                pet_friendly_ids = await Property.filter(
                    pet_policy__icontains="allowed"
                ).values_list('id', flat=True)
                
                pet_friendly_ids2 = await Property.filter(
                    pet_policy__icontains="yes"
                ).values_list('id', flat=True)
                
                pet_friendly_ids3 = await Property.filter(
                    pet_policy__icontains="welcome"
                ).values_list('id', flat=True)
                
                all_pet_friendly = set(pet_friendly_ids) | set(pet_friendly_ids2) | set(pet_friendly_ids3)
                
                if all_pet_friendly:
                    query = query.filter(id__in=list(all_pet_friendly))
                else:
                    # No pet-friendly properties found
                    query = query.filter(id=-1)
            else:
                # Filter out pet-friendly properties
                not_pet_friendly_ids = await Property.filter(
                    pet_policy__icontains="not allowed"
                ).values_list('id', flat=True)
                
                not_pet_friendly_ids2 = await Property.filter(
                    pet_policy__icontains="no pets"
                ).values_list('id', flat=True)
                
                all_not_pet_friendly = set(not_pet_friendly_ids) | set(not_pet_friendly_ids2)
                
                if all_not_pet_friendly:
                    query = query.filter(id__in=list(all_not_pet_friendly))
        
        # === MOVE-IN DATE FILTERING ===
        if available_from_date:
            try:
                from datetime import datetime
                move_in_date = datetime.strptime(available_from_date, "%Y-%m-%d")
                query = query.filter(available_from__lte=move_in_date)
            except ValueError:
                print(f"⚠️ Invalid date format: {available_from_date}")
                pass
        
        # Get total count and results
        total_count = await query.count()
        offset = (page - 1) * limit
        properties = await query.offset(offset).limit(limit).prefetch_related('media').all()
        
        # Format results (same as admin but we can hide sensitive info if needed)
        properties_data = []
        for property_obj in properties:
            media_data = []
            for media in property_obj.media:
                media_data.append({
                    "id": str(media.id),
                    "media_type": media.media_type,
                    "url": media.url,
                    "is_cover": media.is_cover
                })
            
            media_data.sort(key=lambda x: (not x["is_cover"], x["created_at"] if "created_at" in x else ""))
            
            properties_data.append({
                "id": str(property_obj.id),
                "title": property_obj.title,
                "description": property_obj.description,
                "property_type": property_obj.property_type,
                "status": property_obj.status,
                "furnishing": property_obj.furnishing,
                "area_sqft": float(property_obj.area_sqft) if property_obj.area_sqft else None,
                "bedrooms": property_obj.bedrooms,
                "bathrooms": property_obj.bathrooms,
                "floors": property_obj.floors,
                "utilities": property_obj.utilities,
                "amenities": property_obj.amenities,
                "appliances_included": property_obj.appliances_included,
                "lease_term": property_obj.lease_term,
                "application_fee": float(property_obj.application_fee) if property_obj.application_fee else None,
                "pet_policy": property_obj.pet_policy,
                "property_management_contact": property_obj.property_management_contact,
                "website": property_obj.website,
                "price": float(property_obj.price),
                "deposit": float(property_obj.deposit) if property_obj.deposit else None,
                "address": property_obj.address,
                "city": property_obj.city,
                "state": property_obj.state,
                "pincode": property_obj.pincode,
                "latitude": float(property_obj.latitude) if property_obj.latitude else None,
                "longitude": float(property_obj.longitude) if property_obj.longitude else None,
                "available_from": property_obj.available_from.isoformat() if property_obj.available_from else None,
                "media": media_data,
                "media_count": len(media_data)
            })
        
        total_pages = (total_count + limit - 1) // limit
        
        print(f"✅ Found {len(properties)} properties (Total: {total_count})")
        
        # Build filter summary for response
        active_filters = {}
        if keyword:
            active_filters["keyword"] = keyword
        if property_type:
            active_filters["property_type"] = property_type
        if city:
            active_filters["city"] = city
        if state:
            active_filters["state"] = state
        if min_price or max_price:
            active_filters["price_range"] = f"₹{min_price or 0} - ₹{max_price or 'unlimited'}"
        if bedrooms:
            active_filters["bedrooms"] = f"exactly {bedrooms}"
        if bathrooms:
            active_filters["bathrooms"] = f"exactly {bathrooms}"
        if pets_allowed is not None:
            active_filters["pets"] = "allowed" if pets_allowed else "not allowed"
        if available_from_date:
            active_filters["available_from"] = available_from_date
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": f"Found {total_count} properties" + (f" matching your filters" if active_filters else ""),
                "data": {
                    "properties": properties_data,
                    "pagination": {
                        "current_page": page,
                        "per_page": limit,
                        "total_count": total_count,
                        "total_pages": total_pages,
                        "has_next": page < total_pages,
                        "has_prev": page > 1,
                        "showing": f"{min(offset + 1, total_count)}-{min(offset + limit, total_count)} of {total_count}"
                    },
                    "filters_applied": active_filters,
                    "filter_count": len(active_filters)
                }
            }
        )
        
    except Exception as e:
        print(f"❌ Failed to fetch public properties: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch properties: {str(e)}"
        )


async def handle_get_property_details(property_id: str, is_admin: bool = False):
    """Get single property details"""
    try:
        print(f"🏠 Getting property details: {property_id} (admin: {is_admin})")
        
        # Build query
        if is_admin:
            # Admin can see all properties
            property_obj = await Property.get_or_none(id=property_id).prefetch_related('media')
        else:
            # Users can only see available properties
            property_obj = await Property.get_or_none(
                id=property_id, 
                status="available"
            ).prefetch_related('media')
        
        if not property_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Property not found or not available"
            )
        
        # Get media data
        media_data = []
        for media in property_obj.media:
            media_item = {
                "id": str(media.id),
                "media_type": media.media_type,
                "url": media.url,
                "is_cover": media.is_cover
            }
            
            # Add timestamps for admin
            if is_admin:
                media_item.update({
                    "created_at": media.created_at.isoformat(),
                    "updated_at": media.updated_at.isoformat()
                })
            
            media_data.append(media_item)
        
        # Sort media - cover first
        media_data.sort(key=lambda x: (not x["is_cover"]))
        
        # Build response data
        property_data = {
            "id": str(property_obj.id),
            "title": property_obj.title,
            "description": property_obj.description,
            "property_type": property_obj.property_type,
            "status": property_obj.status,
            "furnishing": property_obj.furnishing,
            "area_sqft": float(property_obj.area_sqft) if property_obj.area_sqft else None,
            "bedrooms": property_obj.bedrooms,
            "bathrooms": property_obj.bathrooms,
            "floors": property_obj.floors,
            "utilities": property_obj.utilities,
            "amenities": property_obj.amenities,
            "appliances_included": property_obj.appliances_included,
            "lease_term": property_obj.lease_term,
            "application_fee": float(property_obj.application_fee) if property_obj.application_fee else None,
            "pet_policy": property_obj.pet_policy,
            "property_management_contact": property_obj.property_management_contact,
            "website": property_obj.website,
            "price": float(property_obj.price),
            "deposit": float(property_obj.deposit) if property_obj.deposit else None,
            "address": property_obj.address,
            "city": property_obj.city,
            "state": property_obj.state,
            "pincode": property_obj.pincode,
            "latitude": float(property_obj.latitude) if property_obj.latitude else None,
            "longitude": float(property_obj.longitude) if property_obj.longitude else None,
            "available_from": property_obj.available_from.isoformat() if property_obj.available_from else None,
            "media": media_data,
            "media_count": len(media_data)
        }
        
        # Add admin-only fields
        if is_admin:
            property_data.update({
                "created_at": property_obj.created_at.isoformat(),
                "updated_at": property_obj.updated_at.isoformat()
            })
        
        print("✅ Property details retrieved successfully")
        
        return {
            "success": True,
            "message": "Property details retrieved successfully",
            "data": property_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to get property details: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get property details: {str(e)}"
        )


# === COMPATIBILITY ALIASES FOR ROUTES ===
# These provide backward compatibility with existing route imports

async def handle_get_all_properties(
    page: int = 1,
    limit: int = 10,
    property_type: Optional[str] = None,
    status: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    bedrooms: Optional[int] = None,
    bathrooms: Optional[int] = None,
    furnishing: Optional[str] = None,
    search: Optional[str] = None
):
    """Alias for admin get properties - backward compatibility"""
    return await handle_get_properties_admin(
        page=page,
        limit=limit,
        property_type=property_type,
        status=status,
        min_price=min_price,
        max_price=max_price,
        city=city,
        state=state,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        furnishing=furnishing,
        search=search
    )


async def handle_get_property_by_id(property_id: str, is_admin: bool = True):
    """Alias for get property details - backward compatibility"""
    return await handle_get_property_details(property_id=property_id, is_admin=is_admin)


async def handle_get_property_cover_image(property_id: str):
    """Get the cover image for a specific property"""
    try:
        # Validate property_id format
        try:
            property_uuid = uuid.UUID(property_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid property ID format"
            )
        
        # Check if property exists
        try:
            property_obj = await Property.get(id=property_uuid)
        except DoesNotExist:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        # Find cover image for this property
        try:
            cover_media = await PropertyMedia.get(
                property_id=property_uuid,
                is_cover=True
            )
            
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Cover image found",
                    "data": {
                        "id": str(cover_media.id),
                        "property_id": str(cover_media.property_id),
                        "media_type": cover_media.media_type,
                        "url": cover_media.url,
                        "is_cover": cover_media.is_cover,
                        "created_at": cover_media.created_at.isoformat(),
                        "updated_at": cover_media.updated_at.isoformat()
                    }
                }
            )
            
        except DoesNotExist:
            # No cover image found, try to get the first image as fallback
            try:
                first_image = await PropertyMedia.filter(
                    property_id=property_uuid,
                    media_type="image"
                ).first()
                
                if first_image:
                    return JSONResponse(
                        status_code=HTTP_200_OK,
                        content={
                            "success": True,
                            "message": "No cover image set, returning first available image",
                            "data": {
                                "id": str(first_image.id),
                                "property_id": str(first_image.property_id),
                                "media_type": first_image.media_type,
                                "url": first_image.url,
                                "is_cover": first_image.is_cover,
                                "created_at": first_image.created_at.isoformat(),
                                "updated_at": first_image.updated_at.isoformat()
                            }
                        }
                    )
                else:
                    raise HTTPException(
                        status_code=HTTP_404_NOT_FOUND,
                        detail="No images found for this property"
                    )
                    
            except Exception as fallback_error:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND,
                    detail="No cover image or images found for this property"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting property cover image: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get property cover image: {str(e)}"
        )


async def handle_get_all_property_cover_images():
    """Get cover images for all properties"""
    try:
        # Get only 3 properties with their cover images
        cover_images = await PropertyMedia.filter(is_cover=True).prefetch_related('property').limit(3)
        
        if not cover_images:
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "success": True,
                    "message": "No cover images found",
                    "data": [],
                    "total": 0
                }
            )
        
        # Format response
        cover_images_data = []
        for cover_image in cover_images:
            cover_images_data.append({
                "id": str(cover_image.id),
                "property_id": str(cover_image.property_id),
                "property_title": cover_image.property.title if cover_image.property else None,
                "media_type": cover_image.media_type,
                "url": cover_image.url,
                "is_cover": cover_image.is_cover,
                "created_at": cover_image.created_at.isoformat(),
                "updated_at": cover_image.updated_at.isoformat()
            })
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": f"Found {len(cover_images_data)} cover images",
                "data": cover_images_data,
                "total": len(cover_images_data)
            }
        )
        
    except Exception as e:
        print(f"❌ Error getting all property cover images: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get property cover images: {str(e)}"
        )


async def get_property_stats():
    """Get property statistics for admin dashboard"""
    try:
        print("📊 Getting property statistics...")
        
        # Get total property count
        total_properties = await Property.all().count()
        print(f"Total properties: {total_properties}")
        
        # Get available properties count
        available_properties = await Property.filter(status="available").count()
        print(f"Available properties: {available_properties}")
        
        # Get rented properties count
        rented_properties = await Property.filter(status="rented").count()
        print(f"Rented properties: {rented_properties}")
        
        # Get maintenance properties count
        maintenance_properties = await Property.filter(status="maintenance").count()
        print(f"Maintenance properties: {maintenance_properties}")
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": "Property statistics retrieved successfully",
                "data": {
                    "total_properties": total_properties,
                    "available_properties": available_properties,
                    "rented_properties": rented_properties,
                    "maintenance_properties": maintenance_properties,
                    "occupancy_rate": round((rented_properties / total_properties * 100), 2) if total_properties > 0 else 0
                }
            }
        )
        
    except Exception as e:
        print(f"❌ Error getting property statistics: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get property statistics: {str(e)}"
        )


async def get_recent_properties(limit: int = 3):
    """Get recent properties for admin dashboard"""
    try:
        print(f"📋 Getting {limit} recent properties...")
        
        # Get recent properties ordered by created_at descending
        recent_properties = await Property.all().order_by('-created_at').limit(limit).prefetch_related('media')
        
        properties_data = []
        for property_obj in recent_properties:
            # Get all media files for the property
            media_files = []
            cover_image = None
            
            if property_obj.media:
                for media in property_obj.media:
                    media_data = {
                        "id": str(media.id),
                        "media_type": media.media_type.value,  # Convert enum to string
                        "url": media.url,  # This contains the base64 data
                        "is_cover": media.is_cover,
                        "created_at": media.created_at.isoformat() if media.created_at else None,
                        "updated_at": media.updated_at.isoformat() if media.updated_at else None
                    }
                    media_files.append(media_data)
                    
                    # Set cover image for backward compatibility
                    if media.is_cover:
                        cover_image = media.url
            
            property_data = {
                "id": str(property_obj.id),
                "title": property_obj.title,
                "description": property_obj.description,
                "property_type": property_obj.property_type,
                "status": property_obj.status,
                "furnishing": property_obj.furnishing,
                "price": float(property_obj.price),
                "deposit": float(property_obj.deposit) if property_obj.deposit else None,
                "bedrooms": property_obj.bedrooms,
                "bathrooms": property_obj.bathrooms,
                "floors": property_obj.floors,
                "area_sqft": float(property_obj.area_sqft) if property_obj.area_sqft else None,
                "utilities": property_obj.utilities,
                "amenities": property_obj.amenities,
                "appliances_included": property_obj.appliances_included,
                "lease_term": property_obj.lease_term,
                "application_fee": float(property_obj.application_fee) if property_obj.application_fee else None,
                "pet_policy": property_obj.pet_policy,
                "property_management_contact": property_obj.property_management_contact,
                "website": property_obj.website,
                "address": property_obj.address,
                "city": property_obj.city,
                "state": property_obj.state,
                "pincode": property_obj.pincode,
                "latitude": float(property_obj.latitude) if property_obj.latitude else None,
                "longitude": float(property_obj.longitude) if property_obj.longitude else None,
                "available_from": property_obj.available_from.isoformat() if property_obj.available_from else None,
                "created_at": property_obj.created_at.isoformat() if property_obj.created_at else None,
                "updated_at": property_obj.updated_at.isoformat() if property_obj.updated_at else None,
                "cover_image": cover_image,  # For backward compatibility
                "media": media_files,  # All media files
                "media_count": len(media_files)
            }
            properties_data.append(property_data)
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": f"Retrieved {len(properties_data)} recent properties with media",
                "data": properties_data,
                "total": len(properties_data)
            }
        )
        
    except Exception as e:
        print(f"❌ Error getting recent properties: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent properties: {str(e)}"
        )