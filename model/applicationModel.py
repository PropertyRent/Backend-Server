import uuid
from enum import Enum
from tortoise import fields, models
from datetime import datetime

class ApplicationStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"

class RentalApplication(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    
    # Property Reference
    property = fields.ForeignKeyField("models.Property", related_name="applications", null=True, on_delete=fields.SET_NULL)
    
    # Status and tracking
    status = fields.CharEnumField(ApplicationStatus, default=ApplicationStatus.PENDING)
    admin_reply = fields.TextField(null=True)
    admin_reply_date = fields.DatetimeField(null=True)
    replied_by = fields.ForeignKeyField("models.User", related_name="replied_applications", null=True, on_delete=fields.SET_NULL)
    
    # Personal Information
    full_name = fields.CharField(max_length=255, null=True)
    email = fields.CharField(max_length=255, null=True)
    phone_number = fields.CharField(max_length=20, null=True)
    date_of_birth = fields.DateField(null=True)
    social_security_number = fields.CharField(max_length=500, null=True)  # Encrypted field - needs longer length
    drivers_license_number = fields.CharField(max_length=500, null=True)  # Encrypted field - needs longer length
    
    # Emergency Contact
    emergency_contact_name = fields.CharField(max_length=255, null=True)
    emergency_contact_relationship = fields.CharField(max_length=100, null=True)
    emergency_contact_phone = fields.CharField(max_length=20, null=True)
    
    # Current Address
    current_street_address = fields.TextField(null=True)
    current_city = fields.CharField(max_length=100, null=True)
    current_state = fields.CharField(max_length=50, null=True)
    current_zip = fields.CharField(max_length=10, null=True)
    current_move_in_date = fields.DateField(null=True)
    current_monthly_rent = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    current_reason_for_leaving = fields.TextField(null=True)
    
    # Previous Address
    previous_street_address = fields.TextField(null=True)
    previous_city = fields.CharField(max_length=100, null=True)
    previous_state = fields.CharField(max_length=50, null=True)
    previous_zip = fields.CharField(max_length=10, null=True)
    previous_move_in_date = fields.DateField(null=True)
    previous_move_out_date = fields.DateField(null=True)
    previous_monthly_rent = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    previous_reason_for_leaving = fields.TextField(null=True)
    
    # Landlord Contact
    landlord_name = fields.CharField(max_length=255, null=True)
    landlord_phone = fields.CharField(max_length=20, null=True)
    landlord_email = fields.CharField(max_length=255, null=True)
    
    # Employment Information
    employer_company_name = fields.CharField(max_length=255, null=True)
    employer_job_title = fields.CharField(max_length=100, null=True)
    employer_supervisor_name = fields.CharField(max_length=255, null=True)
    employment_start_date = fields.DateField(null=True)
    monthly_income = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    # Additional Income (JSON field to store array)
    additional_income_sources = fields.JSONField(null=True)
    
    # Bank Information
    bank_name = fields.CharField(max_length=500, null=True)  # Encrypted field - needs longer length
    account_type = fields.CharField(max_length=500, null=True)  # Encrypted field - needs longer length
    routing_number = fields.CharField(max_length=500, null=True)  # Encrypted field - needs longer length
    account_number = fields.CharField(max_length=500, null=True)  # Encrypted field - needs longer length
    
    # Background Check Consent
    background_check_consent = fields.BooleanField(default=False)
    ever_convicted_felony = fields.BooleanField(default=False)
    criminal_history_details = fields.TextField(null=True)
    ever_evicted = fields.BooleanField(default=False)
    eviction_history_details = fields.TextField(null=True)
    
    # References (JSON fields to store arrays)
    personal_references = fields.JSONField(null=True)
    professional_references = fields.JSONField(null=True)
    
    # Pets (JSON field to store array)
    pets = fields.JSONField(null=True)
    
    # Vehicles (JSON field to store array)
    vehicles = fields.JSONField(null=True)
    
    # Additional Applicants (JSON field to store array)
    additional_applicants = fields.JSONField(null=True)
    
    # Electronic Signature
    electronic_signature_name = fields.CharField(max_length=500, null=True)  # Encrypted field - needs longer length
    electronic_signature_date = fields.DateField(null=True)
    
    # Terms Acknowledgment
    agree_to_lease_terms = fields.BooleanField(default=False)
    consent_to_background_credit_checks = fields.BooleanField(default=False)
    understand_rental_policies = fields.BooleanField(default=False)
    
    # Lease and Payment
    lease_reviewed = fields.BooleanField(default=False)
    lease_signed = fields.BooleanField(default=False)
    security_deposit_amount = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    security_deposit_payment_method = fields.CharField(max_length=500, null=True)  # Encrypted field - needs longer length
    first_month_rent_amount = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    first_month_rent_payment_method = fields.CharField(max_length=500, null=True)  # Encrypted field - needs longer length
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "rental_applications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Application {self.id} - {self.full_name or 'No Name'} ({self.status})"