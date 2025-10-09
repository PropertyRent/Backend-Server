import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, Query, Depends
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

from model.contactModel import ContactUs, ContactStatus
from model.userModel import User
from schemas.contactSchemas import ContactUsCreate, ContactUsUpdate, ContactUsResponse, AdminReply
from emailService.contactEmail import (
    send_contact_confirmation_email,
    send_contact_notification_to_admin,
    send_admin_reply_to_user
)


async def create_contact_message(contact_data: ContactUsCreate):
    """Create a new contact us message (accessible by everyone)"""
    try:
        print(f" Creating new contact message from: {contact_data.full_name}")
        
        # Create the contact message
        new_contact = await ContactUs.create(**contact_data.dict())
        print(f" Contact message created with ID: {new_contact.id}")
        
        # Send confirmation email to user
        try:
            await send_contact_confirmation_email(contact_data.email, contact_data.full_name)
            print(" Confirmation email sent to user")
        except Exception as e:
            print(f" Failed to send confirmation email: {e}")
        
        # Send notification to admin
        try:
            contact_dict = {
                "id": str(new_contact.id),
                "full_name": new_contact.full_name,
                "email": new_contact.email,
                "phone": new_contact.phone,
                "message": new_contact.message,
                "created_at": new_contact.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            await send_contact_notification_to_admin(contact_dict)
            print(" Notification email sent to admin")
        except Exception as e:
            print(f" Failed to send admin notification: {e}")
        
        return JSONResponse(
            status_code=HTTP_201_CREATED,
            content={
                "success": True,
                "message": "Your message has been sent successfully. We'll get back to you soon!",
                "data": {
                    "id": str(new_contact.id),
                    "full_name": new_contact.full_name,
                        "email": new_contact.email,
                        "phone": new_contact.phone,
                        "message": new_contact.message,
                    "status": new_contact.status,
                    "created_at": new_contact.created_at.isoformat()
                }
            }
        )
    except Exception as e:
        print(f" Contact message creation failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message. Please try again later."
        )


async def get_all_contact_messages(
    limit: int = Query(20, ge=1, le=100, description="Number of messages to return"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    status: Optional[ContactStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by name or email")
):
    """Get all contact messages (admin only)"""
    try:
        print(f" Fetching contact messages with filters: status={status}, search={search}")
        
        # Build query
        query = ContactUs.all()
        
        # Apply filters
        if status:
            query = query.filter(status=status)
        if search:
            query = query.filter(full_name__icontains=search) | query.filter(email__icontains=search)
        
        # Get total count
        total = await query.count()
        
        # Apply pagination and ordering (newest first)
        contacts = await query.offset(offset).limit(limit).order_by('-created_at')
        
        # Format response
        contact_list = []
        for contact in contacts:
            contact_list.append({
                "id": str(contact.id),
                "full_name": contact.full_name,
                "email": contact.email,
                "phone": contact.phone,
                "message": contact.message,
                "status": contact.status,
                "admin_reply": contact.admin_reply,
                "admin_reply_date": contact.admin_reply_date.isoformat() if contact.admin_reply_date else None,
                "created_at": contact.created_at.isoformat(),
                "updated_at": contact.updated_at.isoformat()
            })
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "data": {
                    "contacts": contact_list,
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
        print(f" Failed to fetch contact messages: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch contact messages"
        )


async def get_contact_message_by_id(contact_id: str):
    """Get a single contact message by ID (admin only)"""
    try:
        # Validate UUID
        try:
            contact_uuid = uuid.UUID(contact_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid contact ID format"
            )
        
        # Fetch contact message
        contact_obj = await ContactUs.get_or_none(id=contact_uuid)
        if not contact_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Contact message not found"
            )
        
        print(f" Fetched contact message: {contact_obj.full_name}")
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "data": {
                    "id": str(contact_obj.id),
                    "full_name": contact_obj.full_name,
                    "email": contact_obj.email,
                    "phone": contact_obj.phone,
                    "message": contact_obj.message,
                    "status": contact_obj.status,
                    "admin_reply": contact_obj.admin_reply,
                    "admin_reply_date": contact_obj.admin_reply_date.isoformat() if contact_obj.admin_reply_date else None,
                    "created_at": contact_obj.created_at.isoformat(),
                    "updated_at": contact_obj.updated_at.isoformat()
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f" Failed to fetch contact message: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch contact message"
        )


async def reply_to_contact_message(contact_id: str, reply_data: AdminReply):
    """Admin reply to contact message"""
    try:
        # Validate UUID
        try:
            contact_uuid = uuid.UUID(contact_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid contact ID format"
            )
        
        # Check if contact exists
        contact_obj = await ContactUs.get_or_none(id=contact_uuid)
        if not contact_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Contact message not found"
            )
        
        print(f" Admin replying to contact message from: {contact_obj.full_name}")
        
        # Update contact with admin reply
        contact_obj.admin_reply = reply_data.message
        contact_obj.admin_reply_date = datetime.now()
        contact_obj.status = ContactStatus.REPLIED
        await contact_obj.save()
        
        # Send reply email to user
        try:
            await send_admin_reply_to_user(
                to_email=contact_obj.email,
                full_name=contact_obj.full_name,
                admin_reply=reply_data.message,
                original_message=contact_obj.message
            )
            print(" Reply email sent to user")
        except Exception as e:
            print(f" Failed to send reply email: {e}")
            # Don't fail the request if email fails
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": "Reply sent successfully",
                "data": {
                    "id": str(contact_obj.id),
                    "full_name": contact_obj.full_name,
                    "email": contact_obj.email,
                    "phone": contact_obj.phone,
                    "message": contact_obj.message,
                    "status": contact_obj.status,
                    "admin_reply": contact_obj.admin_reply,
                    "admin_reply_date": contact_obj.admin_reply_date.isoformat(),
                    "created_at": contact_obj.created_at.isoformat(),
                    "updated_at": contact_obj.updated_at.isoformat()
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f" Failed to send reply: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send reply"
        )


async def update_contact_status(contact_id: str, status_data: ContactUsUpdate):
    """Update contact message status (admin only)"""
    try:
        # Validate UUID
        try:
            contact_uuid = uuid.UUID(contact_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid contact ID format"
            )
        
        # Check if contact exists
        contact_obj = await ContactUs.get_or_none(id=contact_uuid)
        if not contact_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Contact message not found"
            )
        
        # Update only provided fields
        update_data = status_data.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        print(f" Updating contact status for: {contact_obj.full_name}")
        
        # Update the contact
        await contact_obj.update_from_dict(update_data)
        await contact_obj.save()
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": "Contact status updated successfully",
                "data": {
                    "id": str(contact_obj.id),
                    "full_name": contact_obj.full_name,
                    "email": contact_obj.email,
                    "phone": contact_obj.phone,
                    "status": contact_obj.status,
                    "updated_at": contact_obj.updated_at.isoformat()
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f" Contact status update failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update contact status"
        )


async def delete_contact_message(contact_id: str):
    """Delete a contact message (admin only)"""
    try:
        # Validate UUID
        try:
            contact_uuid = uuid.UUID(contact_id)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid contact ID format"
            )
        
        # Check if contact exists
        contact_obj = await ContactUs.get_or_none(id=contact_uuid)
        if not contact_obj:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Contact message not found"
            )
        
        print(f" Deleting contact message from: {contact_obj.full_name}")
        
        # Delete contact
        async with in_transaction():
            await contact_obj.delete()
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "success": True,
                "message": "Contact message deleted successfully"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f" Contact deletion failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete contact message"
        )