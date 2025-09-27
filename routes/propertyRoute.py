from fastapi import APIRouter, Query
from typing import Optional
from controller.propertyController import (
    add_property,
    update_property,
    delete_property,
    get_all_properties,
    get_property_by_id,
    delete_property_media
)
from controller.propertyMediaController import (
    add_property_media,
    update_property_media,
    get_property_media,
    upload_property_media_file
)

router = APIRouter(tags=["Properties"])

# Property CRUD operations
router.post("/properties", summary="Create a new property")(add_property)

router.put("/properties/{property_id}", summary="Update a property")(update_property)

router.delete("/properties/{property_id}", summary="Delete a property")(delete_property)

router.get("/properties", summary="Get all properties with filtering and pagination")(get_all_properties)

router.get("/properties/{property_id}", summary="Get a property by ID")(get_property_by_id)

# Property Media operations
router.post("/properties/media", summary="Add media to a property")(add_property_media)

router.post("/properties/media/upload", summary="Upload media file to a property")(upload_property_media_file)

router.put("/properties/media/{media_id}", summary="Update property media")(update_property_media)

router.get("/properties/{property_id}/media", summary="Get all media for a property")(get_property_media)

router.delete("/properties/media/{media_id}", summary="Delete property media")(delete_property_media)