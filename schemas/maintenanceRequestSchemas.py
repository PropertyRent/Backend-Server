from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field
from model.maintenanceRequestModel import MaintenanceStatus, MaintenancePriority


class MaintenanceRequestCreate(BaseModel):
    """Schema for creating a maintenance request"""
    # Tenant Information
    tenant_name: str = Field(..., min_length=1, max_length=100)
    tenant_phone: Optional[str] = Field(None, max_length=20)
    tenant_email: Optional[EmailStr] = None
    
    # Property Information
    property_address: str = Field(..., min_length=1)
    property_unit: Optional[str] = Field(None, max_length=50)
    
    # Maintenance Details
    issue_title: str = Field(..., min_length=1, max_length=200)
    issue_description: str = Field(..., min_length=1)
    priority: MaintenancePriority = MaintenancePriority.MEDIUM
    
    # Contractor Information
    contractor_email: EmailStr
    contractor_name: Optional[str] = Field(None, max_length=100)
    contractor_phone: Optional[str] = Field(None, max_length=20)
    
    # Photos/Attachments
    photos: Optional[List[str]] = []
    
    # Additional Details
    estimated_cost: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None


class MaintenanceRequestUpdate(BaseModel):
    """Schema for updating a maintenance request"""
    # Tenant Information
    tenant_name: Optional[str] = Field(None, min_length=1, max_length=100)
    tenant_phone: Optional[str] = Field(None, max_length=20)
    tenant_email: Optional[EmailStr] = None
    
    # Property Information
    property_address: Optional[str] = Field(None, min_length=1)
    property_unit: Optional[str] = Field(None, max_length=50)
    
    # Maintenance Details
    issue_title: Optional[str] = Field(None, min_length=1, max_length=200)
    issue_description: Optional[str] = Field(None, min_length=1)
    priority: Optional[MaintenancePriority] = None
    
    # Contractor Information
    contractor_email: Optional[EmailStr] = None
    contractor_name: Optional[str] = Field(None, max_length=100)
    contractor_phone: Optional[str] = Field(None, max_length=20)
    
    # Photos/Attachments
    photos: Optional[List[str]] = None
    
    # Status and Additional Details
    status: Optional[MaintenanceStatus] = None
    estimated_cost: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None


class MaintenanceRequestResponse(BaseModel):
    """Schema for maintenance request response"""
    id: UUID
    
    # Tenant Information
    tenant_name: str
    tenant_phone: Optional[str]
    tenant_email: Optional[str]
    
    # Property Information
    property_address: str
    property_unit: Optional[str]
    
    # Maintenance Details
    issue_title: str
    issue_description: str
    priority: MaintenancePriority
    
    # Contractor Information
    contractor_email: str
    contractor_name: Optional[str]
    contractor_phone: Optional[str]
    
    # Photos/Attachments
    photos: List[str]
    
    # Status and Metadata
    status: MaintenanceStatus
    estimated_cost: Optional[Decimal]
    notes: Optional[str]
    created_by_admin: Optional[UUID]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    sent_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class SendToContractorRequest(BaseModel):
    """Schema for sending maintenance request to contractor"""
    additional_message: Optional[str] = None
    urgent: bool = False


class MaintenanceRequestSummary(BaseModel):
    """Schema for maintenance request summary/list view"""
    id: UUID
    tenant_name: str
    property_address: str
    issue_title: str
    priority: MaintenancePriority
    status: MaintenanceStatus
    contractor_email: str
    contractor_name: Optional[str]
    created_at: datetime
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True