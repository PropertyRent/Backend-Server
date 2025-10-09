import os
import uuid
from typing import List, Optional
from fastapi import HTTPException, Request
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from datetime import datetime, date

from model.applicationModel import RentalApplication, ApplicationStatus
from model.userModel import User
from model.propertyModel import Property
from schemas.applicationSchemas import (
    RentalApplicationCreate,
    RentalApplicationUpdate,
    RentalApplicationResponse,
    AdminReplySchema
)
from emailService.applicationEmail import (
    send_application_confirmation,
    send_admin_reply_to_application,
    send_application_status_update,
    notify_admin_new_application
)
from authMiddleware.authMiddleware import check_for_authentication_cookie
from services.encryptionService import encryption_service, SENSITIVE_FIELDS

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@propertyrent.com")

async def format_application_data(application: RentalApplication) -> dict:
    """Format application data for response with decrypted sensitive fields"""
    
    # Personal Information (decrypt sensitive fields)
    personal_info = {
        "full_name": application.full_name,
        "email": application.email,
        "phone_number": application.phone_number,
        "date_of_birth": application.date_of_birth.isoformat() if application.date_of_birth else None,
        "social_security_number": encryption_service.decrypt(application.social_security_number) if application.social_security_number else None,
        "drivers_license_number": encryption_service.decrypt(application.drivers_license_number) if application.drivers_license_number else None,
        "emergency_contact": {
            "name": application.emergency_contact_name,
            "relationship": application.emergency_contact_relationship,
            "phone_number": application.emergency_contact_phone
        }
    }
    
    # Residential History
    residential_history = {
        "current_address": {
            "street_address": application.current_street_address,
            "city": application.current_city,
            "state": application.current_state,
            "zip": application.current_zip,
            "move_in_date": application.current_move_in_date.isoformat() if application.current_move_in_date else None,
            "monthly_rent": float(application.current_monthly_rent) if application.current_monthly_rent else None,
            "reason_for_leaving": application.current_reason_for_leaving
        },
        "previous_address": {
            "street_address": application.previous_street_address,
            "city": application.previous_city,
            "state": application.previous_state,
            "zip": application.previous_zip,
            "move_in_date": application.previous_move_in_date.isoformat() if application.previous_move_in_date else None,
            "move_out_date": application.previous_move_out_date.isoformat() if application.previous_move_out_date else None,
            "monthly_rent": float(application.previous_monthly_rent) if application.previous_monthly_rent else None,
            "reason_for_leaving": application.previous_reason_for_leaving
        },
        "landlord_contact": {
            "name": application.landlord_name,
            "phone_number": application.landlord_phone,
            "email": application.landlord_email
        }
    }
    
    # Employment Income
    employment_income = {
        "current_employer": {
            "company_name": application.employer_company_name,
            "job_title": application.employer_job_title,
            "supervisor_name": application.employer_supervisor_name,
            "employment_start_date": application.employment_start_date.isoformat() if application.employment_start_date else None,
            "monthly_income": float(application.monthly_income) if application.monthly_income else None
        },
        "additional_income_sources": application.additional_income_sources or [],
        "bank_account_information": {
            "bank_name": encryption_service.decrypt(application.bank_name) if application.bank_name else None,
            "account_type": encryption_service.decrypt(application.account_type) if application.account_type else None,
            "routing_number": encryption_service.decrypt(application.routing_number) if application.routing_number else None,
            "account_number": encryption_service.decrypt(application.account_number) if application.account_number else None
        }
    }
    
    # Credit Background Check
    credit_background_check = {
        "consent": application.background_check_consent,
        "criminal_history": {
            "ever_convicted_felony": application.ever_convicted_felony,
            "details": application.criminal_history_details
        },
        "eviction_history": {
            "ever_evicted": application.ever_evicted,
            "details": application.eviction_history_details
        }
    }
    
    # References
    references = {
        "personal_references": application.personal_references or [],
        "professional_references": application.professional_references or []
    }
    
    # Additional Information
    additional_information = {
        "pets": application.pets or [],
        "vehicles": application.vehicles or [],
        "additional_applicants": application.additional_applicants or []
    }
    
    # Signature Acknowledgment (decrypt sensitive fields)
    signature_acknowledgment = {
        "electronic_signature": {
            "full_name": encryption_service.decrypt(application.electronic_signature_name) if application.electronic_signature_name else None,
            "date": application.electronic_signature_date.isoformat() if application.electronic_signature_date else None
        },
        "terms_acknowledgment": {
            "agree_to_lease_terms": application.agree_to_lease_terms,
            "consent_to_background_credit_checks": application.consent_to_background_credit_checks,
            "understand_rental_policies": application.understand_rental_policies
        }
    }
    
    # Lease Signing Payment
    lease_signing_payment = {
        "lease_agreement": {
            "reviewed": application.lease_reviewed,
            "signed": application.lease_signed
        },
        "security_deposit_payment": {
            "amount_due": float(application.security_deposit_amount) if application.security_deposit_amount else None,
            "payment_method": encryption_service.decrypt(application.security_deposit_payment_method) if application.security_deposit_payment_method else None
        },
        "first_month_rent": {
            "amount_due": float(application.first_month_rent_amount) if application.first_month_rent_amount else None,
            "payment_method": encryption_service.decrypt(application.first_month_rent_payment_method) if application.first_month_rent_payment_method else None
        }
    }
    
    # Property details if property is linked
    property_details = None
    if application.property_id:
        try:
            property_instance = await Property.get(id=application.property_id)
            property_details = {
                "id": str(property_instance.id),
                "title": property_instance.title,
                "description": property_instance.description,
                "property_type": property_instance.property_type,
                "status": property_instance.status,
                "furnishing": property_instance.furnishing,
                "area_sqft": float(property_instance.area_sqft) if property_instance.area_sqft else None,
                "bedrooms": property_instance.bedrooms,
                "bathrooms": property_instance.bathrooms,
                "floors": property_instance.floors,
                "utilities": property_instance.utilities,
                "lease_term": property_instance.lease_term,
                "application_fee": float(property_instance.application_fee) if property_instance.application_fee else None,
                "amenities": property_instance.amenities,
                "pet_policy": property_instance.pet_policy,
                "appliances_included": property_instance.appliances_included,
                "property_management_contact": property_instance.property_management_contact,
                "website": property_instance.website,
                "price": float(property_instance.price) if property_instance.price else None,
                "deposit": float(property_instance.deposit) if property_instance.deposit else None,
                "address": property_instance.address,
                "city": property_instance.city,
                "state": property_instance.state,
                "pincode": property_instance.pincode,
                "latitude": float(property_instance.latitude) if property_instance.latitude else None,
                "longitude": float(property_instance.longitude) if property_instance.longitude else None,
                "available_from": property_instance.available_from.isoformat() if property_instance.available_from else None,
                "created_at": property_instance.created_at.isoformat(),
                "updated_at": property_instance.updated_at.isoformat()
            }
        except DoesNotExist:
            property_details = {"error": "Property not found or may have been deleted"}

    return {
        "id": str(application.id),
        "status": application.status.value,
        "admin_reply": application.admin_reply,
        "admin_reply_date": application.admin_reply_date.isoformat() if application.admin_reply_date else None,
        "created_at": application.created_at.isoformat(),
        "updated_at": application.updated_at.isoformat(),
        "property_id": str(application.property_id) if application.property_id else None,
        "property_details": property_details,
        "personal_information": personal_info,
        "residential_history": residential_history,
        "employment_income": employment_income,
        "credit_background_check": credit_background_check,
        "references": references,
        "additional_information": additional_information,
        "signature_acknowledgment": signature_acknowledgment,
        "lease_signing_payment": lease_signing_payment
    }

async def handle_submit_application(application_data: RentalApplicationCreate):
    """Handle rental application submission - No login required"""
    try:
        # Extract data from nested structure
        personal_info = application_data.personal_information or {}
        residential_history = application_data.residential_history or {}
        employment_income = application_data.employment_income or {}
        credit_background = application_data.credit_background_check or {}
        references = application_data.references or {}
        additional_info = application_data.additional_information or {}
        signature_ack = application_data.signature_acknowledgment or {}
        lease_payment = application_data.lease_signing_payment or {}
        
        # Validate property_id if provided
        property_instance = None
        if application_data.property_id:
            try:
                property_instance = await Property.get(id=uuid.UUID(application_data.property_id))
            except DoesNotExist:
                raise HTTPException(status_code=404, detail=f"Property with ID {application_data.property_id} not found")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid property ID format")

        # Create application record
        application = await RentalApplication.create(
            # Property reference
            property_id=uuid.UUID(application_data.property_id) if application_data.property_id else None,
            
            # Personal Information (encrypt sensitive fields)
            full_name=personal_info.full_name if personal_info else None,
            email=personal_info.email if personal_info else None,
            phone_number=personal_info.phone_number if personal_info else None,
            date_of_birth=personal_info.date_of_birth if personal_info else None,
            social_security_number=encryption_service.encrypt(personal_info.social_security_number) if personal_info and personal_info.social_security_number else None,
            drivers_license_number=encryption_service.encrypt(personal_info.drivers_license_number) if personal_info and personal_info.drivers_license_number else None,
            
            # Emergency Contact
            emergency_contact_name=personal_info.emergency_contact.name if personal_info and personal_info.emergency_contact else None,
            emergency_contact_relationship=personal_info.emergency_contact.relationship if personal_info and personal_info.emergency_contact else None,
            emergency_contact_phone=personal_info.emergency_contact.phone_number if personal_info and personal_info.emergency_contact else None,
            
            # Current Address
            current_street_address=residential_history.current_address.street_address if residential_history and residential_history.current_address else None,
            current_city=residential_history.current_address.city if residential_history and residential_history.current_address else None,
            current_state=residential_history.current_address.state if residential_history and residential_history.current_address else None,
            current_zip=residential_history.current_address.zip if residential_history and residential_history.current_address else None,
            current_move_in_date=residential_history.current_address.move_in_date if residential_history and residential_history.current_address else None,
            current_monthly_rent=residential_history.current_address.monthly_rent if residential_history and residential_history.current_address else None,
            current_reason_for_leaving=residential_history.current_address.reason_for_leaving if residential_history and residential_history.current_address else None,
            
            # Previous Address
            previous_street_address=residential_history.previous_address.street_address if residential_history and residential_history.previous_address else None,
            previous_city=residential_history.previous_address.city if residential_history and residential_history.previous_address else None,
            previous_state=residential_history.previous_address.state if residential_history and residential_history.previous_address else None,
            previous_zip=residential_history.previous_address.zip if residential_history and residential_history.previous_address else None,
            previous_move_in_date=residential_history.previous_address.move_in_date if residential_history and residential_history.previous_address else None,
            previous_move_out_date=residential_history.previous_address.move_out_date if residential_history and residential_history.previous_address else None,
            previous_monthly_rent=residential_history.previous_address.monthly_rent if residential_history and residential_history.previous_address else None,
            previous_reason_for_leaving=residential_history.previous_address.reason_for_leaving if residential_history and residential_history.previous_address else None,
            
            # Landlord Contact
            landlord_name=residential_history.landlord_contact.name if residential_history and residential_history.landlord_contact else None,
            landlord_phone=residential_history.landlord_contact.phone_number if residential_history and residential_history.landlord_contact else None,
            landlord_email=residential_history.landlord_contact.email if residential_history and residential_history.landlord_contact else None,
            
            # Employment
            employer_company_name=employment_income.current_employer.company_name if employment_income and employment_income.current_employer else None,
            employer_job_title=employment_income.current_employer.job_title if employment_income and employment_income.current_employer else None,
            employer_supervisor_name=employment_income.current_employer.supervisor_name if employment_income and employment_income.current_employer else None,
            employment_start_date=employment_income.current_employer.employment_start_date if employment_income and employment_income.current_employer else None,
            monthly_income=employment_income.current_employer.monthly_income if employment_income and employment_income.current_employer else None,
            
            # Additional Income (as JSON)
            additional_income_sources=[income.dict() for income in employment_income.additional_income_sources] if employment_income and employment_income.additional_income_sources else None,
            
            # Bank Info (encrypt sensitive fields)
            bank_name=encryption_service.encrypt(employment_income.bank_account_information.bank_name) if employment_income and employment_income.bank_account_information and employment_income.bank_account_information.bank_name else None,
            account_type=encryption_service.encrypt(employment_income.bank_account_information.account_type) if employment_income and employment_income.bank_account_information and employment_income.bank_account_information.account_type else None,
            routing_number=encryption_service.encrypt(employment_income.bank_account_information.routing_number) if employment_income and employment_income.bank_account_information and employment_income.bank_account_information.routing_number else None,
            account_number=encryption_service.encrypt(employment_income.bank_account_information.account_number) if employment_income and employment_income.bank_account_information and employment_income.bank_account_information.account_number else None,
            
            # Background Check
            background_check_consent=credit_background.consent if credit_background else False,
            ever_convicted_felony=credit_background.criminal_history.ever_convicted_felony if credit_background and credit_background.criminal_history else False,
            criminal_history_details=credit_background.criminal_history.details if credit_background and credit_background.criminal_history else None,
            ever_evicted=credit_background.eviction_history.ever_evicted if credit_background and credit_background.eviction_history else False,
            eviction_history_details=credit_background.eviction_history.details if credit_background and credit_background.eviction_history else None,
            
            # References (as JSON)
            personal_references=[ref.dict() for ref in references.personal_references] if references and references.personal_references else None,
            professional_references=[ref.dict() for ref in references.professional_references] if references and references.professional_references else None,
            
            # Additional Info (as JSON)
            pets=[pet.dict() for pet in additional_info.pets] if additional_info and additional_info.pets else None,
            vehicles=[vehicle.dict() for vehicle in additional_info.vehicles] if additional_info and additional_info.vehicles else None,
            additional_applicants=[app.dict() for app in additional_info.additional_applicants] if additional_info and additional_info.additional_applicants else None,
            
            # Electronic Signature (encrypt sensitive fields)
            electronic_signature_name=encryption_service.encrypt(signature_ack.electronic_signature.full_name) if signature_ack and signature_ack.electronic_signature and signature_ack.electronic_signature.full_name else None,
            electronic_signature_date=signature_ack.electronic_signature.signature_date if signature_ack and signature_ack.electronic_signature else None,
            
            # Terms
            agree_to_lease_terms=signature_ack.terms_acknowledgment.agree_to_lease_terms if signature_ack and signature_ack.terms_acknowledgment else False,
            consent_to_background_credit_checks=signature_ack.terms_acknowledgment.consent_to_background_credit_checks if signature_ack and signature_ack.terms_acknowledgment else False,
            understand_rental_policies=signature_ack.terms_acknowledgment.understand_rental_policies if signature_ack and signature_ack.terms_acknowledgment else False,
            
            # Lease and Payment (encrypt sensitive payment methods)
            lease_reviewed=lease_payment.lease_agreement.reviewed if lease_payment and lease_payment.lease_agreement else False,
            lease_signed=lease_payment.lease_agreement.signed if lease_payment and lease_payment.lease_agreement else False,
            security_deposit_amount=lease_payment.security_deposit_payment.amount_due if lease_payment and lease_payment.security_deposit_payment else None,
            security_deposit_payment_method=encryption_service.encrypt(lease_payment.security_deposit_payment.payment_method) if lease_payment and lease_payment.security_deposit_payment and lease_payment.security_deposit_payment.payment_method else None,
            first_month_rent_amount=lease_payment.first_month_rent.amount_due if lease_payment and lease_payment.first_month_rent else None,
            first_month_rent_payment_method=encryption_service.encrypt(lease_payment.first_month_rent.payment_method) if lease_payment and lease_payment.first_month_rent and lease_payment.first_month_rent.payment_method else None,
        )
        
        # Send confirmation email to user if email provided
        if application.email:
            try:
                email_data = {
                    'application_id': str(application.id),
                    'full_name': application.full_name,
                    'submitted_date': application.created_at.strftime('%B %d, %Y')
                }
                await send_application_confirmation(application.email, email_data)
            except Exception as e:
                print(f"Failed to send confirmation email: {e}")
        
        # Notify admin about new application
        try:
            admin_email_data = {
                'application_id': str(application.id),
                'full_name': application.full_name,
                'email': application.email,
                'phone_number': application.phone_number,
                'submitted_date': application.created_at.strftime('%B %d, %Y'),
                'property_title': property_instance.title if property_instance else "No property specified",
                'property_address': f"{property_instance.address}, {property_instance.city}, {property_instance.state}" if property_instance else None
            }
            await notify_admin_new_application(ADMIN_EMAIL, admin_email_data)
        except Exception as e:
            print(f"Failed to send admin notification: {e}")
        
        # Include property information in response if provided
        property_info = None
        if property_instance:
            property_info = {
                "property_id": str(property_instance.id),
                "title": property_instance.title,
                "address": property_instance.address,
                "city": property_instance.city,
                "state": property_instance.state,
                "price": float(property_instance.price) if property_instance.price else None
            }

        return {
            "success": True,
            "message": "Application submitted successfully",
            "data": {
                "application_id": str(application.id),
                "status": application.status.value,
                "submitted_at": application.created_at.isoformat(),
                "property_info": property_info
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit application: {str(e)}")

async def handle_get_all_applications(status: Optional[str] = None, search: Optional[str] = None):
    """Get all applications for admin (with filtering)"""
    try:
        # Build query
        query = RentalApplication.all()
        
        # Apply filters
        if status:
            query = query.filter(status=status)
        if search:
            # Search by name, email, or application ID
            query = query.filter(
                Q(full_name__icontains=search) | 
                Q(email__icontains=search) |
                Q(id__icontains=search)
            )
        
        # Get applications
        applications = await query.order_by('-created_at')
        
        # Format response
        application_list = []
        for app in applications:
            # Get basic property info if property is linked
            property_basic_info = None
            if app.property_id:
                try:
                    property_instance = await Property.get(id=app.property_id)
                    property_basic_info = {
                        "id": str(property_instance.id),
                        "title": property_instance.title,
                        "property_type": property_instance.property_type,
                        "price": float(property_instance.price) if property_instance.price else None,
                        "address": property_instance.address,
                        "city": property_instance.city,
                        "state": property_instance.state
                    }
                except DoesNotExist:
                    property_basic_info = {"error": "Property not found"}

            application_list.append({
                "id": str(app.id),
                "full_name": app.full_name,
                "email": app.email,
                "phone_number": app.phone_number,
                "status": app.status.value,
                "admin_reply": app.admin_reply,
                "admin_reply_date": app.admin_reply_date.isoformat() if app.admin_reply_date else None,
                "created_at": app.created_at.isoformat(),
                "updated_at": app.updated_at.isoformat(),
                "property_id": str(app.property_id) if app.property_id else None,
                "property_basic_info": property_basic_info
            })
        
        return {
            "success": True,
            "data": {
                "applications": application_list,
                "total": len(application_list)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch applications: {str(e)}")

async def handle_get_application_by_id(application_id: str):
    """Get application by ID (admin only)"""
    try:
        try:
            application = await RentalApplication.get(id=uuid.UUID(application_id))
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Return complete application data
        return {
            "success": True,
            "data": await format_application_data(application)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch application: {str(e)}")

async def handle_admin_reply_to_application(request: Request, application_id: str, reply_data: AdminReplySchema):
    """Handle admin reply to application"""
    try:
        # Get current admin user
        user_payload = await check_for_authentication_cookie(request)
        admin_user_id = user_payload.get("id")  
        admin_user = await User.get(id=uuid.UUID(admin_user_id))
        
        # Get application
        try:
            application = await RentalApplication.get(id=uuid.UUID(application_id))
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Update application
        application.admin_reply = reply_data.reply
        application.admin_reply_date = datetime.now()
        application.replied_by_id = admin_user.id
        
        # Update status if provided
        if reply_data.status:
            application.status = reply_data.status
        
        await application.save()
        
        # Send email to user if email exists
        if application.email:
            try:
                email_data = {
                    'application_id': str(application.id),
                    'full_name': application.full_name,
                    'admin_reply': application.admin_reply,
                    'status': application.status.value,
                    'admin_name': admin_user.full_name if hasattr(admin_user, 'full_name') else admin_user.email
                }
                await send_admin_reply_to_application(application.email, email_data)
            except Exception as e:
                print(f"Failed to send reply email: {e}")
        
        return {
            "success": True,
            "message": "Reply sent successfully and user notified via email",
            "data": {
                "application_id": str(application.id),
                "status": application.status.value,
                "admin_reply": application.admin_reply,
                "reply_date": application.admin_reply_date.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send reply: {str(e)}")

async def handle_update_application_status(request: Request, application_id: str, status: ApplicationStatus):
    """Update application status (admin only)"""
    try:
        # Get current admin user
        user_payload = await check_for_authentication_cookie(request)
        admin_user_id = user_payload.get("id")
        admin_user = await User.get(id=uuid.UUID(admin_user_id))
        
        # Get application
        try:
            application = await RentalApplication.get(id=uuid.UUID(application_id))
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Update status
        old_status = application.status
        application.status = status
        await application.save()
        
        # Send status update email if email exists and status changed
        if application.email and old_status != status:
            try:
                email_data = {
                    'application_id': str(application.id),
                    'full_name': application.full_name,
                    'status': application.status.value
                }
                await send_application_status_update(application.email, email_data)
            except Exception as e:
                print(f"Failed to send status update email: {e}")
        
        return {
            "success": True,
            "message": f"Application status updated to {status.value}",
            "data": {
                "application_id": str(application.id),
                "old_status": old_status.value,
                "new_status": application.status.value,
                "updated_at": application.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")

async def handle_delete_application(request: Request, application_id: str):
    """Delete application (admin only)"""
    try:
        # Get current admin user
        user_payload = await check_for_authentication_cookie(request)
        admin_user_id = user_payload.get("id")
        admin_user = await User.get(id=uuid.UUID(admin_user_id))
        
        # Get application
        try:
            application = await RentalApplication.get(id=uuid.UUID(application_id))
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Store details before deletion
        application_details = {
            'application_id': str(application.id),
            'full_name': application.full_name,
            'email': application.email,
            'status': application.status.value
        }
        
        # Delete application
        await application.delete()
        
        return {
            "success": True,
            "message": "Application deleted successfully",
            "data": {
                "deleted_application_id": application_details['application_id'],
                "deleted_by_admin": admin_user.email,
                "deleted_at": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete application: {str(e)}")