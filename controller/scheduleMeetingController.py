import os
import uuid
from typing import List, Optional
from fastapi import HTTPException, Request
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from datetime import datetime, date

from model.scheduleMeetingModel import ScheduleMeeting, MeetingStatus
from model.propertyModel import Property
from model.userModel import User
from schemas.scheduleMeetingSchemas import (
    ScheduleMeetingCreate,
    ScheduleMeetingUpdate,
    ScheduleMeetingResponse,
    ScheduleMeetingWithProperty,
    MeetingStatsResponse
)
from emailService.meetingEmail import (
    send_meeting_request_confirmation,
    send_meeting_approval_email,
    send_meeting_rejection_email,
    send_meeting_completion_email,
    notify_admin_new_meeting
)
from authMiddleware.authMiddleware import check_for_authentication_cookie

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@propertyrent.com")

async def handle_schedule_meeting(request: Optional[Request], meeting_data: ScheduleMeetingCreate):
    """Handle meeting scheduling by users - No login required"""
    try:
        # Verify property exists
        try:
            property_obj = await Property.get(id=meeting_data.property_id)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Since no login is required, user will always be None
        current_user = None
        
        # Create meeting request
        meeting = await ScheduleMeeting.create(
            full_name=meeting_data.full_name,
            email=meeting_data.email,
            phone=meeting_data.phone,
            meeting_date=meeting_data.meeting_date,
            meeting_time=meeting_data.meeting_time,
            property_id=meeting_data.property_id,
            user_id=current_user.id if current_user else None,
            message=meeting_data.message,
            status=MeetingStatus.PENDING
        )
        
        # Prepare email data
        email_data = {
            'full_name': meeting.full_name,
            'meeting_date': meeting.meeting_date.strftime('%B %d, %Y'),
            'meeting_time': meeting.meeting_time.strftime('%I:%M %p'),
            'property_title': property_obj.title,
            'email': meeting.email,
            'phone': meeting.phone,
            'message': meeting.message or 'No additional message'
        }
        
        # Send confirmation email to user
        await send_meeting_request_confirmation(meeting.email, email_data)
        
        # Notify admin about new meeting request
        await notify_admin_new_meeting(ADMIN_EMAIL, email_data)
        
        return {
            "success": True,
            "message": "Meeting request submitted successfully. You will receive a confirmation email shortly.",
            "meeting_id": str(meeting.id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule meeting: {str(e)}")

async def handle_get_user_meetings(request: Request, status: Optional[str] = None):
    """Get meetings for the current logged-in user"""
    try:
        user_payload = await check_for_authentication_cookie(request)
        user_id = user_payload.get("id")
        current_user = await User.get(id=uuid.UUID(user_id))
        
        # Build query
        query = ScheduleMeeting.filter(
            Q(user_id=current_user.id) | Q(email=current_user.email)
        ).prefetch_related('property', 'user', 'approved_by')
        
        if status:
            query = query.filter(status=status)
        
        meetings = await query.all()
        
        # Format response
        result = []
        for meeting in meetings:
            meeting_data = {
                'id': str(meeting.id),
                'full_name': meeting.full_name,
                'email': meeting.email,
                'phone': meeting.phone,
                'meeting_date': meeting.meeting_date,
                'meeting_time': meeting.meeting_time,
                'message': meeting.message,
                'status': meeting.status,
                'approved_at': meeting.approved_at,
                'completed_at': meeting.completed_at,
                'created_at': meeting.created_at,
                'updated_at': meeting.updated_at,
                'property': {
                    'id': str(meeting.property.id),
                    'title': meeting.property.title,
                    'property_type': meeting.property.property_type,
                    'price': float(meeting.property.price),
                    'status': meeting.property.status
                } if meeting.property else None,
                'approved_by': meeting.approved_by.full_name if meeting.approved_by else None
            }
            result.append(meeting_data)
        
        return {
            "success": True,
            "meetings": result,
            "total": len(result)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch meetings: {str(e)}")

async def handle_get_all_meetings_admin(status: Optional[str] = None, property_id: Optional[str] = None):
    """Get all meetings for admin review"""
    try:
        # Build query
        query = ScheduleMeeting.all().prefetch_related('property', 'user', 'approved_by')
        
        if status:
            query = query.filter(status=status)
        
        if property_id:
            query = query.filter(property_id=property_id)
        
        meetings = await query.all()
        
        # Format response
        result = []
        for meeting in meetings:
            meeting_data = {
                'id': str(meeting.id),
                'full_name': meeting.full_name,
                'email': meeting.email,
                'phone': meeting.phone,
                'meeting_date': meeting.meeting_date,
                'meeting_time': meeting.meeting_time,
                'message': meeting.message,
                'status': meeting.status,
                'admin_message': meeting.admin_message,
                'approved_at': meeting.approved_at,
                'completed_at': meeting.completed_at,
                'created_at': meeting.created_at,
                'updated_at': meeting.updated_at,
                'property': {
                    'id': str(meeting.property.id),
                    'title': meeting.property.title,
                    'property_type': meeting.property.property_type,
                    'price': float(meeting.property.price),
                    'status': meeting.property.status,
                    'bedrooms': meeting.property.bedrooms,
                    'bathrooms': meeting.property.bathrooms
                } if meeting.property else None,
                'user': {
                    'id': str(meeting.user.id),
                    'full_name': meeting.user.full_name,
                    'email': meeting.user.email
                } if meeting.user else None,
                'approved_by': meeting.approved_by.full_name if meeting.approved_by else None
            }
            result.append(meeting_data)
        
        return {
            "success": True, 
            "meetings": result,
            "total": len(result)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch meetings: {str(e)}")

async def handle_update_meeting_status(request: Request, meeting_id: str, update_data: ScheduleMeetingUpdate):
    """Update meeting status (admin only)"""
    try:
        user_payload = await check_for_authentication_cookie(request)
        user_id = user_payload.get("id")
        current_user = await User.get(id=uuid.UUID(user_id))
        
        # Get meeting
        try:
            meeting = await ScheduleMeeting.get(id=meeting_id).prefetch_related('property')
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        old_status = meeting.status
        
        # Update meeting
        if update_data.status:
            meeting.status = update_data.status
            
            if update_data.status == MeetingStatus.APPROVED:
                meeting.approved_by_id = current_user.id
                meeting.approved_at = datetime.now()
            elif update_data.status == MeetingStatus.COMPLETED:
                meeting.completed_at = datetime.now()
        
        if update_data.admin_notes is not None:
            meeting.admin_notes = update_data.admin_notes
            
        if update_data.meeting_date:
            meeting.meeting_date = update_data.meeting_date
            
        if update_data.meeting_time:
            meeting.meeting_time = update_data.meeting_time
        
        await meeting.save()
        
        # Send appropriate email if status changed
        if update_data.status and old_status != update_data.status:
            email_data = {
                'full_name': meeting.full_name,
                'meeting_date': meeting.meeting_date.strftime('%B %d, %Y'),
                'meeting_time': meeting.meeting_time.strftime('%I:%M %p'),
                'property_title': meeting.property.title,
                'admin_notes': meeting.admin_notes
            }
            
            if update_data.status == MeetingStatus.APPROVED:
                await send_meeting_approval_email(meeting.email, email_data)
            elif update_data.status == MeetingStatus.REJECTED:
                await send_meeting_rejection_email(meeting.email, email_data)
            elif update_data.status == MeetingStatus.COMPLETED:
                await send_meeting_completion_email(meeting.email, email_data)
        
        return {
            "success": True,
            "message": "Meeting updated successfully",
            "meeting": {
                'id': str(meeting.id),
                'status': meeting.status,
                'admin_notes': meeting.admin_notes,
                'approved_at': meeting.approved_at,
                'completed_at': meeting.completed_at
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update meeting: {str(e)}")

async def handle_get_meeting_by_id(meeting_id: str):
    """Get specific meeting details"""
    try:
        try:
            meeting = await ScheduleMeeting.get(id=meeting_id).prefetch_related('property', 'user', 'approved_by')
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        return {
            "success": True,
            "meeting": {
                'id': str(meeting.id),
                'full_name': meeting.full_name,
                'email': meeting.email,
                'phone': meeting.phone,
                'meeting_date': meeting.meeting_date,
                'meeting_time': meeting.meeting_time,
                'message': meeting.message,
                'status': meeting.status,
                'admin_message': meeting.admin_message,
                'approved_at': meeting.approved_at,
                'completed_at': meeting.completed_at,
                'created_at': meeting.created_at,
                'updated_at': meeting.updated_at,
                'property': {
                    'id': str(meeting.property.id),
                    'title': meeting.property.title,
                    'description': meeting.property.description,
                    'property_type': meeting.property.property_type,
                    'price': float(meeting.property.price),
                    'status': meeting.property.status,
                    'bedrooms': meeting.property.bedrooms,
                    'bathrooms': meeting.property.bathrooms,
                    'area_sqft': float(meeting.property.area_sqft) if meeting.property.area_sqft else None
                } if meeting.property else None,
                'user': {
                    'id': str(meeting.user.id),
                    'full_name': meeting.user.full_name,
                    'email': meeting.user.email
                } if meeting.user else None,
                'approved_by': meeting.approved_by.full_name if meeting.approved_by else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch meeting: {str(e)}")

async def handle_delete_meeting(meeting_id: str):
    """Delete meeting (admin only)"""
    try:
        try:
            meeting = await ScheduleMeeting.get(id=meeting_id)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        await meeting.delete()
        
        return {
            "success": True,
            "message": "Meeting deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete meeting: {str(e)}")

async def handle_get_meeting_stats():
    """Get meeting statistics for admin dashboard"""
    try:
        total_meetings = await ScheduleMeeting.all().count()
        pending_meetings = await ScheduleMeeting.filter(status=MeetingStatus.PENDING).count()
        approved_meetings = await ScheduleMeeting.filter(status=MeetingStatus.APPROVED).count()
        completed_meetings = await ScheduleMeeting.filter(status=MeetingStatus.COMPLETED).count()
        rejected_meetings = await ScheduleMeeting.filter(status=MeetingStatus.REJECTED).count()
        cancelled_meetings = await ScheduleMeeting.filter(status=MeetingStatus.CANCELLED).count()
        
        return {
            "success": True,
            "stats": {
                "total_meetings": total_meetings,
                "pending_meetings": pending_meetings,
                "approved_meetings": approved_meetings,
                "completed_meetings": completed_meetings,
                "rejected_meetings": rejected_meetings,
                "cancelled_meetings": cancelled_meetings
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics: {str(e)}")

async def handle_cancel_meeting(request: Request, meeting_id: str):
    """Allow user to cancel their own meeting"""
    try:
        user_payload = await check_for_authentication_cookie(request)
        user_id = user_payload.get("id")
        current_user = await User.get(id=uuid.UUID(user_id))
        
        try:
            meeting = await ScheduleMeeting.get(id=meeting_id)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        # Check if user owns this meeting
        if meeting.user_id != current_user.id and meeting.email != current_user.email:
            raise HTTPException(status_code=403, detail="You can only cancel your own meetings")
        
        # Check if meeting can be cancelled
        if meeting.status in [MeetingStatus.COMPLETED, MeetingStatus.CANCELLED]:
            raise HTTPException(status_code=400, detail="Meeting cannot be cancelled")
        
        meeting.status = MeetingStatus.CANCELLED
        await meeting.save()
        
        return {
            "success": True,
            "message": "Meeting cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel meeting: {str(e)}")


async def handle_admin_reply_to_meeting(request: Request, meeting_id: str, reply_data):
    """Handle admin reply to meeting request with approve/reject"""
    try:
        # Get current admin user
        user_payload = await check_for_authentication_cookie(request)
        admin_user_id = user_payload.get("id")
        admin_user = await User.get(id=uuid.UUID(admin_user_id))
        
        # Get meeting
        try:
            meeting = await ScheduleMeeting.get(id=uuid.UUID(meeting_id)).prefetch_related('property')
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        # Update meeting with admin message
        meeting.admin_message = reply_data.message
        meeting.admin_reply_date = datetime.now()
        
        # Set status based on action
        if reply_data.action == MeetingStatus.APPROVED:
            meeting.status = MeetingStatus.APPROVED
            # meeting.approved_by_id = admin_user.id  # Uncomment after running migration
            meeting.approved_at = datetime.now()
        elif reply_data.action == MeetingStatus.REJECTED:
            meeting.status = MeetingStatus.REJECTED
            # meeting.rejected_at = datetime.now()  # Uncomment after running migration
        else:
            # If no action or any other case, mark as replied
            meeting.status = MeetingStatus.REPLIED
            # meeting.replied_by_id = admin_user.id  # Uncomment after running migration
            # meeting.replied_at = datetime.now()    # Uncomment after running migration
        
        await meeting.save()
        
        # Prepare email data
        email_data = {
            'full_name': meeting.full_name,
            'meeting_date': meeting.meeting_date.strftime('%B %d, %Y'),
            'meeting_time': meeting.meeting_time.strftime('%I:%M %p'),
            'property_title': meeting.property.title,
            'admin_message': meeting.admin_message,
            'admin_name': admin_user.full_name if hasattr(admin_user, 'full_name') else admin_user.email
        }
        
        # Send appropriate email based on status
        if meeting.status == MeetingStatus.APPROVED:
            await send_meeting_approval_email(meeting.email, email_data)
            message = "Meeting approved and confirmation email sent to user"
        elif meeting.status == MeetingStatus.REJECTED:
            await send_meeting_rejection_email(meeting.email, email_data)
            message = "Meeting rejected and notification email sent to user"
        else:
            # Status is REPLIED - send general reply email
            from emailService.meetingEmail import send_admin_reply_email
            await send_admin_reply_email(meeting.email, email_data)
            message = "Admin reply sent to user and status marked as replied"
        
        return {
            "success": True,
            "message": message,
            "data": {
                "meeting_id": str(meeting.id),
                "status": meeting.status.value,
                "admin_message": meeting.admin_message,
                "admin_reply_date": meeting.admin_reply_date.isoformat(),
                "action_taken": reply_data.action.value if reply_data.action else "message_only"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process admin reply: {str(e)}")


async def handle_admin_approve_meeting(request: Request, meeting_id: str, message_data: Optional[dict] = None):
    """Handle admin approve meeting with optional message"""
    try:
        # Get current admin user
        user_payload = await check_for_authentication_cookie(request)
        admin_user_id = user_payload.get("id")
        admin_user = await User.get(id=uuid.UUID(admin_user_id))
        
        # Get meeting
        try:
            meeting = await ScheduleMeeting.get(id=uuid.UUID(meeting_id)).prefetch_related('property')
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        # Update meeting status
        meeting.status = MeetingStatus.APPROVED
        meeting.approved_by_id = admin_user.id
        meeting.approved_at = datetime.now()
        
        # Add admin message if provided
        if message_data and message_data.get("message"):
            meeting.admin_message = message_data.get("message")
            meeting.admin_reply_date = datetime.now()
        
        await meeting.save()
        
        # Prepare email data
        email_data = {
            'full_name': meeting.full_name,
            'meeting_date': meeting.meeting_date.strftime('%B %d, %Y'),
            'meeting_time': meeting.meeting_time.strftime('%I:%M %p'),
            'property_title': meeting.property.title,
            'admin_message': meeting.admin_message or "Your meeting has been approved!",
            'admin_name': admin_user.full_name if hasattr(admin_user, 'full_name') else admin_user.email
        }
        
        # Send approval email
        await send_meeting_approval_email(meeting.email, email_data)
        
        return {
            "success": True,
            "message": "Meeting approved and confirmation email sent to user",
            "data": {
                "meeting_id": str(meeting.id),
                "status": meeting.status.value,
                "admin_message": meeting.admin_message,
                "approved_at": meeting.approved_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve meeting: {str(e)}")


async def handle_admin_reject_meeting(request: Request, meeting_id: str, message_data: Optional[dict] = None):
    """Handle admin reject meeting with optional message"""
    try:
        # Get current admin user
        user_payload = await check_for_authentication_cookie(request)
        admin_user_id = user_payload.get("id")
        admin_user = await User.get(id=uuid.UUID(admin_user_id))
        
        # Get meeting
        try:
            meeting = await ScheduleMeeting.get(id=uuid.UUID(meeting_id)).prefetch_related('property')
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        # Update meeting status
        meeting.status = MeetingStatus.REJECTED
        
        # Add admin message if provided
        if message_data and message_data.get("message"):
            meeting.admin_message = message_data.get("message")
            meeting.admin_reply_date = datetime.now()
        
        await meeting.save()
        
        # Prepare email data
        email_data = {
            'full_name': meeting.full_name,
            'meeting_date': meeting.meeting_date.strftime('%B %d, %Y'),
            'meeting_time': meeting.meeting_time.strftime('%I:%M %p'),
            'property_title': meeting.property.title,
            'admin_message': meeting.admin_message or "Unfortunately, your meeting request has been rejected.",
            'admin_name': admin_user.full_name if hasattr(admin_user, 'full_name') else admin_user.email
        }
        
        # Send rejection email
        await send_meeting_rejection_email(meeting.email, email_data)
        
        return {
            "success": True,
            "message": "Meeting rejected and notification email sent to user",
            "data": {
                "meeting_id": str(meeting.id),
                "status": meeting.status.value,
                "admin_message": meeting.admin_message,
                "rejected_at": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reject meeting: {str(e)}")


async def handle_admin_complete_meeting(request: Request, meeting_id: str):
    """Handle admin mark meeting as completed"""
    try:
        # Get current admin user
        user_payload = await check_for_authentication_cookie(request)
        admin_user_id = user_payload.get("id")
        admin_user = await User.get(id=uuid.UUID(admin_user_id))
        
        # Get meeting
        try:
            meeting = await ScheduleMeeting.get(id=uuid.UUID(meeting_id)).prefetch_related('property')
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        # Update meeting status
        meeting.status = MeetingStatus.COMPLETED
        meeting.completed_at = datetime.now()
        
        await meeting.save()
        
        # Prepare email data
        email_data = {
            'full_name': meeting.full_name,
            'meeting_date': meeting.meeting_date.strftime('%B %d, %Y'),
            'meeting_time': meeting.meeting_time.strftime('%I:%M %p'),
            'property_title': meeting.property.title,
            'admin_name': admin_user.full_name if hasattr(admin_user, 'full_name') else admin_user.email
        }
        
        # Send completion email
        await send_meeting_completion_email(meeting.email, email_data)
        
        return {
            "success": True,
            "message": "Meeting marked as completed and notification email sent to user",
            "data": {
                "meeting_id": str(meeting.id),
                "status": meeting.status.value,
                "completed_at": meeting.completed_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete meeting: {str(e)}")


async def handle_admin_delete_meeting(request: Request, meeting_id: str):
    """Handle admin delete meeting with notification"""
    try:
        # Get current admin user
        user_payload = await check_for_authentication_cookie(request)
        admin_user_id = user_payload.get("id")
        admin_user = await User.get(id=uuid.UUID(admin_user_id))
        
        # Get meeting with property details
        try:
            meeting = await ScheduleMeeting.get(id=uuid.UUID(meeting_id)).prefetch_related('property')
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        # Store meeting details for email before deletion
        meeting_details = {
            'full_name': meeting.full_name,
            'email': meeting.email,
            'meeting_id': str(meeting.id),
            'meeting_date': meeting.meeting_date.strftime('%B %d, %Y'),
            'meeting_time': meeting.meeting_time.strftime('%I:%M %p'),
            'property_title': meeting.property.title,
            'admin_name': admin_user.full_name if hasattr(admin_user, 'full_name') else admin_user.email
        }
        
        # Delete the meeting
        await meeting.delete()
        
        # Send cancellation email to user
        try:
            from emailService.meetingEmail import send_meeting_cancellation_email
            await send_meeting_cancellation_email(meeting_details['email'], meeting_details)
        except Exception as email_error:
            # Log email error but don't fail the deletion
            print(f"Failed to send cancellation email: {email_error}")
        
        return {
            "success": True,
            "message": "Meeting deleted successfully and cancellation email sent to user",
            "data": {
                "deleted_meeting_id": meeting_details['meeting_id'],
                "user_notified": True,
                "deleted_by_admin": admin_user.email,
                "deleted_at": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete meeting: {str(e)}")