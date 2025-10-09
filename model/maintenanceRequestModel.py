from tortoise.models import Model
from tortoise import fields
from enum import Enum


class MaintenanceStatus(str, Enum):
    PENDING = "pending"
    SENT_TO_CONTRACTOR = "sent_to_contractor"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MaintenancePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class MaintenanceRequest(Model):
    """Model for maintenance requests sent to contractors"""
    
    id = fields.UUIDField(pk=True)
    
    # Tenant Information
    tenant_name = fields.CharField(max_length=100)
    tenant_phone = fields.CharField(max_length=20, null=True)
    tenant_email = fields.CharField(max_length=255, null=True)
    
    # Property Information
    property_address = fields.TextField()
    property_unit = fields.CharField(max_length=50, null=True)
    
    # Maintenance Details
    issue_title = fields.CharField(max_length=200)
    issue_description = fields.TextField()
    priority = fields.CharEnumField(MaintenancePriority, default=MaintenancePriority.MEDIUM)
    
    # Contractor Information
    contractor_email = fields.CharField(max_length=255)
    contractor_name = fields.CharField(max_length=100, null=True)
    contractor_phone = fields.CharField(max_length=20, null=True)
    
    # Photos/Attachments
    photos = fields.JSONField(default=list)  # List of base64 encoded images
    
    # Status and Metadata
    status = fields.CharEnumField(MaintenanceStatus, default=MaintenanceStatus.PENDING)
    estimated_cost = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    notes = fields.TextField(null=True)
    
    # Admin who created the request
    created_by_admin = fields.UUIDField(null=True)  # Reference to admin user
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    sent_at = fields.DatetimeField(null=True)  # When it was sent to contractor
    completed_at = fields.DatetimeField(null=True)
    
    class Meta:
        table = "maintenance_requests"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Maintenance Request: {self.issue_title} - {self.tenant_name}"