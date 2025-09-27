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