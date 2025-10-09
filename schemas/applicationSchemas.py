from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum

class ApplicationStatusEnum(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"

# Nested schemas for complex data structures
class EmergencyContactSchema(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None
    phone_number: Optional[str] = None

class AddressSchema(BaseModel):
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    move_in_date: Optional[date] = None
    monthly_rent: Optional[float] = None
    reason_for_leaving: Optional[str] = None

class PreviousAddressSchema(AddressSchema):
    move_out_date: Optional[date] = None

class LandlordContactSchema(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None

class CurrentEmployerSchema(BaseModel):
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    supervisor_name: Optional[str] = None
    employment_start_date: Optional[date] = None
    monthly_income: Optional[float] = None

class IncomeSourceSchema(BaseModel):
    source: Optional[str] = None
    amount: Optional[float] = None

class BankAccountSchema(BaseModel):
    bank_name: Optional[str] = None
    account_type: Optional[str] = None
    routing_number: Optional[str] = None
    account_number: Optional[str] = None

class CriminalHistorySchema(BaseModel):
    ever_convicted_felony: Optional[bool] = False
    details: Optional[str] = None

class EvictionHistorySchema(BaseModel):
    ever_evicted: Optional[bool] = False
    details: Optional[str] = None

class PersonalReferenceSchema(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None

class ProfessionalReferenceSchema(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None

class PetSchema(BaseModel):
    has_pet: Optional[bool] = False
    type: Optional[str] = None
    breed: Optional[str] = None
    weight: Optional[str] = None
    age: Optional[str] = None

class VehicleSchema(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[str] = None
    color: Optional[str] = None
    license_plate_number: Optional[str] = None

class AdditionalApplicantSchema(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None
    employment_status: Optional[str] = None
    monthly_income: Optional[float] = None

class ElectronicSignatureSchema(BaseModel):
    full_name: Optional[str] = None
    signature_date: Optional[date] = None

class TermsAcknowledgmentSchema(BaseModel):
    agree_to_lease_terms: Optional[bool] = False
    consent_to_background_credit_checks: Optional[bool] = False
    understand_rental_policies: Optional[bool] = False

class LeaseAgreementSchema(BaseModel):
    reviewed: Optional[bool] = False
    signed: Optional[bool] = False

class PaymentSchema(BaseModel):
    amount_due: Optional[float] = None
    payment_method: Optional[str] = None

# Main application schemas
class PersonalInformationSchema(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    social_security_number: Optional[str] = None
    drivers_license_number: Optional[str] = None
    emergency_contact: Optional[EmergencyContactSchema] = None

class ResidentialHistorySchema(BaseModel):
    current_address: Optional[AddressSchema] = None
    previous_address: Optional[PreviousAddressSchema] = None
    landlord_contact: Optional[LandlordContactSchema] = None

class EmploymentIncomeSchema(BaseModel):
    current_employer: Optional[CurrentEmployerSchema] = None
    additional_income_sources: Optional[List[IncomeSourceSchema]] = None
    bank_account_information: Optional[BankAccountSchema] = None

class CreditBackgroundCheckSchema(BaseModel):
    consent: Optional[bool] = False
    criminal_history: Optional[CriminalHistorySchema] = None
    eviction_history: Optional[EvictionHistorySchema] = None

class ReferencesSchema(BaseModel):
    personal_references: Optional[List[PersonalReferenceSchema]] = None
    professional_references: Optional[List[ProfessionalReferenceSchema]] = None

class AdditionalInformationSchema(BaseModel):
    pets: Optional[List[PetSchema]] = None
    vehicles: Optional[List[VehicleSchema]] = None
    additional_applicants: Optional[List[AdditionalApplicantSchema]] = None

class SignatureAcknowledgmentSchema(BaseModel):
    electronic_signature: Optional[ElectronicSignatureSchema] = None
    terms_acknowledgment: Optional[TermsAcknowledgmentSchema] = None

class LeaseSigningPaymentSchema(BaseModel):
    lease_agreement: Optional[LeaseAgreementSchema] = None
    security_deposit_payment: Optional[PaymentSchema] = None
    first_month_rent: Optional[PaymentSchema] = None

class RentalApplicationCreate(BaseModel):
    property_id: Optional[str] = None  # Property UUID as string
    personal_information: Optional[PersonalInformationSchema] = None
    residential_history: Optional[ResidentialHistorySchema] = None
    employment_income: Optional[EmploymentIncomeSchema] = None
    credit_background_check: Optional[CreditBackgroundCheckSchema] = None
    references: Optional[ReferencesSchema] = None
    additional_information: Optional[AdditionalInformationSchema] = None
    signature_acknowledgment: Optional[SignatureAcknowledgmentSchema] = None
    lease_signing_payment: Optional[LeaseSigningPaymentSchema] = None

class RentalApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatusEnum] = None
    admin_reply: Optional[str] = None

class AdminReplySchema(BaseModel):
    reply: str
    status: Optional[ApplicationStatusEnum] = None

class RentalApplicationResponse(BaseModel):
    id: str
    status: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    admin_reply: Optional[str] = None
    admin_reply_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Property information
    property_id: Optional[str] = None
    property_details: Optional[Dict[str, Any]] = None
    
    # All the detailed fields for complete response
    personal_information: Optional[Dict[str, Any]] = None
    residential_history: Optional[Dict[str, Any]] = None
    employment_income: Optional[Dict[str, Any]] = None
    credit_background_check: Optional[Dict[str, Any]] = None
    references: Optional[Dict[str, Any]] = None
    additional_information: Optional[Dict[str, Any]] = None
    signature_acknowledgment: Optional[Dict[str, Any]] = None
    lease_signing_payment: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True