from typing import List, Optional
from decimal import Decimal
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from schemas.propertyMediaSchemas import PropertyMediaResponse 

class PropertyBase(BaseModel):
    title: str
    description: Optional[str] = None
    property_type: str
    status: str
    furnishing: Optional[str] = None
    area_sqft: Optional[Decimal] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    floors: Optional[int] = None

    utilities: Optional[List[str]] = None
    lease_term: Optional[str] = None
    application_fee: Optional[Decimal] = None

    amenities: Optional[List[str]] = None
    pet_policy: Optional[str] = None
    appliances_included: Optional[List[str]] = None

    property_management_contact: Optional[str] = None
    website: Optional[str] = None

    price: Decimal
    deposit: Optional[Decimal] = None

    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None

    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    available_from: Optional[datetime] = None


class PropertyCreate(PropertyBase):
    """Schema for creating a property"""
    pass


class PropertyUpdate(BaseModel):
    """Schema for updating property details"""
    title: Optional[str] = None
    description: Optional[str] = None
    property_type: Optional[str] = None
    status: Optional[str] = None
    furnishing: Optional[str] = None
    area_sqft: Optional[Decimal] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    floors: Optional[int] = None

    utilities: Optional[List[str]] = None
    lease_term: Optional[str] = None
    application_fee: Optional[Decimal] = None

    amenities: Optional[List[str]] = None
    pet_policy: Optional[str] = None
    appliances_included: Optional[List[str]] = None

    property_management_contact: Optional[str] = None
    website: Optional[str] = None

    price: Optional[Decimal] = None
    deposit: Optional[Decimal] = None

    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None

    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    available_from: Optional[datetime] = None


class PropertyOut(PropertyBase):
    """Schema for sending property response with media"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    media: List[PropertyMediaResponse] = []   

    class Config:
        from_attributes = True
