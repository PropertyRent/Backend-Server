import uuid
from typing import List
from fastapi import HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_201_CREATED,
    HTTP_200_OK
)
from tortoise.exceptions import IntegrityError

from model.propertyModel import Property
from model.propertyMediaModel import PropertyMedia
from schemas.propertyMediaSchemas import PropertyMediaCreate, PropertyMediaUpdate
from config.fileUpload import process_property_media


async def add_property_media(media_data: PropertyMediaCreate):
    """Add media to a property"""
    try:
        # Validate property exists
        property_obj = await Property.get_or_none(id=media_data.property_id)
        if not property_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        print(f" Adding media to property: {property_obj.title}")
        
        # If this is a cover image, unset other cover images for this property
        if media_data.is_cover:
            await PropertyMedia.filter(property_id=media_data.property_id, is_cover=True).update(is_cover=False)
        
        # Create media
        media_dict = media_data.dict()
        property_id = media_dict.pop('property_id')  # Remove property_id from dict
        
        new_media = await PropertyMedia.create(
            property_id=property_id,
            **media_dict
        )
        
        return JSONResponse(
            status_code=HTTP_201_CREATED,
            content={
                "success": True,
                "message": "Property media added successfully",
                "data": {
                    "id": str(new_media.id),
                    "property_id": str(new_media.property_id),
                    "media_type": new_media.media_type,
                    "url": new_media.url,
                    "is_cover": new_media.is_cover,
                    "created_at": new_media.created_at.isoformat(),
                    "updated_at": new_media.updated_at.isoformat()
                }
            }
        )
    except HTTPException:
        raise
    except IntegrityError as e:
        print(f" Media creation failed - integrity error: {e}")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Media creation failed due to data integrity issues"
        )
    except Exception as e:
        print(f" Media creation failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add property media"
        )


async def update_property_media(media_id: str, media_data: PropertyMediaUpdate):
    """Update property media"""
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
        
        # Update only provided fields
        update_data = media_data.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # If setting as cover image, unset other cover images for this property
        if update_data.get('is_cover'):
            await PropertyMedia.filter(property_id=media_obj.property_id, is_cover=True).exclude(id=media_uuid).update(is_cover=False)
        
        print(f" Updating media {media_id} with data: {update_data}")
        
        # Update the media
        await media_obj.update_from_dict(update_data)
        await media_obj.save()
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": "Property media updated successfully",
                "data": {
                    "id": str(media_obj.id),
                    "property_id": str(media_obj.property_id),
                    "media_type": media_obj.media_type,
                    "url": media_obj.url,
                    "is_cover": media_obj.is_cover,
                    "created_at": media_obj.created_at.isoformat(),
                    "updated_at": media_obj.updated_at.isoformat()
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f" Media update failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update property media"
        )


async def get_property_media(property_id: str):
    """Get all media for a specific property"""
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
        
        # Get all media for this property
        media_list = await PropertyMedia.filter(property_id=property_uuid).order_by('-is_cover', 'created_at')
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "data": [
                    {
                        "id": str(media.id),
                        "property_id": str(media.property_id),
                        "media_type": media.media_type,
                        "url": media.url,
                        "is_cover": media.is_cover,
                        "created_at": media.created_at.isoformat(),
                        "updated_at": media.updated_at.isoformat()
                    }
                    for media in media_list
                ]
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f" Failed to fetch property media: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch property media"
        )


async def upload_property_media_file(
    property_id: str = Form(...),
    media_type: str = Form(...),  # "image" or "video"
    is_cover: bool = Form(False),
    media_file: UploadFile = File(...)
):
    """Upload property media file and convert to base64"""
    try:
        # Validate UUID
        try:
            property_uuid = uuid.UUID(property_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid property ID format"
            )
        
        # Validate property exists
        property_obj = await Property.get_or_none(id=property_uuid)
        if not property_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        # Validate media type
        if media_type.lower() not in ["image", "video"]:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid media type. Must be 'image' or 'video'"
            )
        
        print(f" Uploading {media_type} for property: {property_obj.title}")
        
        # Process file to base64
        base64_data = await process_property_media(media_file, media_type.lower())
        
        # If this is a cover image, unset other cover images for this property
        if is_cover:
            await PropertyMedia.filter(property_id=property_uuid, is_cover=True).update(is_cover=False)
        
        # Create media record
        new_media = await PropertyMedia.create(
            property_id=property_uuid,
            media_type=media_type.lower(),
            url=base64_data,
            is_cover=is_cover
        )
        
        return JSONResponse(
            status_code=HTTP_201_CREATED,
            content={
                "success": True,
                "message": f"Property {media_type} uploaded successfully",
                "data": {
                    "id": str(new_media.id),
                    "property_id": str(new_media.property_id),
                    "media_type": new_media.media_type,
                    "url": new_media.url[:100] + "..." if len(new_media.url) > 100 else new_media.url,  # Truncate for response
                    "is_cover": new_media.is_cover,
                    "created_at": new_media.created_at.isoformat(),
                    "updated_at": new_media.updated_at.isoformat()
                }
            }
        )
    except HTTPException:
        raise
    except IntegrityError as e:
        print(f" Media upload failed - integrity error: {e}")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Media upload failed due to data integrity issues"
        )
    except Exception as e:
        print(f" Media upload failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload property media"
        )