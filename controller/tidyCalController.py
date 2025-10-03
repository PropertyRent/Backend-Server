import uuid
import os
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, Request
from tortoise.exceptions import DoesNotExist
from datetime import datetime, date
import json

from model.tidyCalModel import TidyCalBookingPage, TidyCalBooking, BookingPageStatus
from model.propertyModel import Property
from model.scheduleMeetingModel import ScheduleMeeting
from schemas.tidyCalSchemas import (
    TidyCalBookingPageCreate,
    TidyCalBookingPageUpdate,
    TidyCalBookingPageResponse,
    TidyCalBookingCreate,
    TidyCalBookingUpdate,
    TidyCalBookingResponse,
    TidyCalWebhookEvent,
    TidyCalIntegrationStatus,
    BookingPageEmbedResponse,
    PropertyWithBookingPage,
    BookingAnalytics
)
from services.tidyCalIntegration import tidycal_service
from authMiddleware.authMiddleware import check_for_authentication_cookie

async def create_booking_page_for_property(property_id: str, booking_page_data: TidyCalBookingPageCreate):
    """Create a TidyCal booking page for a specific property"""
    try:
        print(f"🗓️ Creating TidyCal booking page for property: {property_id}")
        
        # Verify property exists
        try:
            property_obj = await Property.get(id=uuid.UUID(property_id))
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Property not found")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid property ID format")
        
        # Check if property already has a booking page
        existing_page = await TidyCalBookingPage.filter(property_id=property_obj.id, status=BookingPageStatus.ACTIVE).first()
        if existing_page:
            raise HTTPException(status_code=400, detail="Property already has an active booking page")
        
        # Prepare property data for TidyCal
        property_data = {
            "id": str(property_obj.id),
            "title": property_obj.title,
            "address": f"{property_obj.address}, {property_obj.city}, {property_obj.state}",
            "price": float(property_obj.price) if property_obj.price else None,
            "description": property_obj.description
        }
        
        # Create booking page in TidyCal
        tidycal_result = await tidycal_service.create_booking_page(property_data)
        
        if not tidycal_result.get("success"):
            raise HTTPException(status_code=500, detail="Failed to create TidyCal booking page")
        
        # Save booking page information locally
        booking_page = await TidyCalBookingPage.create(
            property_id=property_obj.id,
            tidycal_booking_page_id=tidycal_result.get("booking_page_id"),
            booking_url=tidycal_result.get("booking_url"),
            embed_code=tidycal_result.get("embed_code"),
            page_name=booking_page_data.page_name,
            description=booking_page_data.description,
            duration_minutes=booking_page_data.duration_minutes,
            buffer_before=booking_page_data.buffer_before,
            buffer_after=booking_page_data.buffer_after,
            is_public=booking_page_data.is_public,
            custom_questions=booking_page_data.custom_questions,
            notification_settings=booking_page_data.notification_settings,
            status=BookingPageStatus.ACTIVE
        )
        
        print(f"✅ TidyCal booking page created successfully: {booking_page.id}")
        
        return {
            "success": True,
            "message": "Booking page created successfully",
            "data": {
                "id": str(booking_page.id),
                "property_id": str(property_obj.id),
                "property_title": property_obj.title,
                "tidycal_booking_page_id": booking_page.tidycal_booking_page_id,
                "booking_url": booking_page.booking_url,
                "embed_code": booking_page.embed_code,
                "page_name": booking_page.page_name,
                "status": booking_page.status.value,
                "created_at": booking_page.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error creating booking page: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create booking page: {str(e)}")

async def get_property_booking_pages(property_id: Optional[str] = None):
    """Get booking pages for properties"""
    try:
        print(f"🗓️ Fetching booking pages for property: {property_id or 'all'}")
        
        # Build query
        query = TidyCalBookingPage.all().select_related("property")
        
        if property_id:
            try:
                query = query.filter(property_id=uuid.UUID(property_id))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid property ID format")
        
        booking_pages = await query.order_by("-created_at")
        
        # Format response
        pages_data = []
        for page in booking_pages:
            pages_data.append({
                "id": str(page.id),
                "property_id": str(page.property.id),
                "property_title": page.property.title,
                "tidycal_booking_page_id": page.tidycal_booking_page_id,
                "booking_url": page.booking_url,
                "embed_code": page.embed_code,
                "page_name": page.page_name,
                "description": page.description,
                "duration_minutes": page.duration_minutes,
                "buffer_before": page.buffer_before,
                "buffer_after": page.buffer_after,
                "status": page.status.value,
                "is_public": page.is_public,
                "total_bookings": page.total_bookings,
                "last_booking_date": page.last_booking_date.isoformat() if page.last_booking_date else None,
                "created_at": page.created_at.isoformat(),
                "updated_at": page.updated_at.isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "booking_pages": pages_data,
                "total": len(pages_data)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching booking pages: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch booking pages: {str(e)}")

async def get_booking_page_embed_code(booking_page_id: str, width: str = "100%", height: str = "600px"):
    """Get embed code for booking page"""
    try:
        print(f"🗓️ Getting embed code for booking page: {booking_page_id}")
        
        # Get booking page
        try:
            booking_page = await TidyCalBookingPage.get(id=uuid.UUID(booking_page_id)).select_related("property")
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Booking page not found")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid booking page ID format")
        
        # Generate embed code
        embed_code = tidycal_service.generate_embed_code(booking_page.booking_url, width, height)
        
        return {
            "success": True,
            "data": {
                "booking_page_id": str(booking_page.id),
                "property_title": booking_page.property.title,
                "booking_url": booking_page.booking_url,
                "embed_code": embed_code,
                "iframe_width": width,
                "iframe_height": height,
                "custom_styling": {
                    "border": "none",
                    "border-radius": "8px",
                    "box-shadow": "0 4px 6px rgba(0, 0, 0, 0.1)"
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting embed code: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get embed code: {str(e)}")

async def handle_tidycal_webhook(request: Request, webhook_data: dict):
    """Handle TidyCal webhook events"""
    try:
        print(f"🗓️ Processing TidyCal webhook: {webhook_data.get('event_type', 'unknown')}")
        
        # Verify webhook signature (if configured)
        signature = request.headers.get("X-TidyCal-Signature")
        if signature:
            payload = await request.body()
            if not tidycal_service.verify_webhook_signature(payload.decode(), signature):
                raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        event_type = webhook_data.get("event_type")
        booking_data = webhook_data.get("booking_details", {})
        customer_data = webhook_data.get("customer", {})
        tidycal_booking_id = webhook_data.get("booking_id")
        
        if event_type == "booking.created":
            await process_booking_created(tidycal_booking_id, booking_data, customer_data)
        elif event_type == "booking.cancelled":
            await process_booking_cancelled(tidycal_booking_id, booking_data)
        elif event_type == "booking.completed":
            await process_booking_completed(tidycal_booking_id, booking_data)
        elif event_type == "booking.rescheduled":
            await process_booking_rescheduled(tidycal_booking_id, booking_data)
        else:
            print(f"⚠️ Unhandled webhook event type: {event_type}")
        
        return {
            "success": True,
            "message": f"Webhook event '{event_type}' processed successfully",
            "processed_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process webhook: {str(e)}")

async def process_booking_created(tidycal_booking_id: str, booking_data: dict, customer_data: dict):
    """Process new booking creation from TidyCal"""
    try:
        # Find the booking page
        booking_page_id = booking_data.get("booking_page_id")
        booking_page = await TidyCalBookingPage.filter(tidycal_booking_page_id=booking_page_id).first()
        
        if not booking_page:
            print(f"⚠️ Booking page not found for TidyCal ID: {booking_page_id}")
            return
        
        # Create local booking record
        booking = await TidyCalBooking.create(
            tidycal_booking_id=tidycal_booking_id,
            booking_page_id=booking_page.id,
            customer_name=customer_data.get("name", ""),
            customer_email=customer_data.get("email", ""),
            customer_phone=customer_data.get("phone"),
            scheduled_date=datetime.fromisoformat(booking_data.get("start_time")).date(),
            scheduled_time=datetime.fromisoformat(booking_data.get("start_time")).time(),
            duration_minutes=booking_data.get("duration", 60),
            timezone=booking_data.get("timezone", "UTC"),
            customer_notes=booking_data.get("notes"),
            custom_responses=booking_data.get("custom_responses"),
            booking_status="confirmed",
            booking_created_at=datetime.fromisoformat(booking_data.get("created_at"))
        )
        
        # Update booking page statistics
        booking_page.total_bookings += 1
        booking_page.last_booking_date = datetime.now()
        await booking_page.save()
        
        print(f"✅ New booking created: {booking.id}")
        
    except Exception as e:
        print(f"❌ Error processing booking creation: {e}")

async def process_booking_cancelled(tidycal_booking_id: str, booking_data: dict):
    """Process booking cancellation from TidyCal"""
    try:
        booking = await TidyCalBooking.filter(tidycal_booking_id=tidycal_booking_id).first()
        if booking:
            booking.booking_status = "cancelled"
            await booking.save()
            print(f"✅ Booking cancelled: {booking.id}")
    except Exception as e:
        print(f"❌ Error processing booking cancellation: {e}")

async def process_booking_completed(tidycal_booking_id: str, booking_data: dict):
    """Process booking completion from TidyCal"""
    try:
        booking = await TidyCalBooking.filter(tidycal_booking_id=tidycal_booking_id).first()
        if booking:
            booking.booking_status = "completed"
            await booking.save()
            print(f"✅ Booking completed: {booking.id}")
    except Exception as e:
        print(f"❌ Error processing booking completion: {e}")

async def process_booking_rescheduled(tidycal_booking_id: str, booking_data: dict):
    """Process booking rescheduling from TidyCal"""
    try:
        booking = await TidyCalBooking.filter(tidycal_booking_id=tidycal_booking_id).first()
        if booking:
            # Update booking details with new time
            new_datetime = datetime.fromisoformat(booking_data.get("start_time"))
            booking.scheduled_date = new_datetime.date()
            booking.scheduled_time = new_datetime.time()
            await booking.save()
            print(f"✅ Booking rescheduled: {booking.id}")
    except Exception as e:
        print(f"❌ Error processing booking rescheduling: {e}")

async def get_tidycal_integration_status():
    """Get TidyCal integration status and statistics"""
    try:
        total_pages = await TidyCalBookingPage.all().count()
        total_bookings = await TidyCalBooking.all().count()
        
        latest_booking = await TidyCalBooking.all().order_by("-created_at").first()
        last_sync = latest_booking.last_sync_at if latest_booking else None
        
        return {
            "success": True,
            "data": {
                "is_configured": bool(tidycal_service.api_key),
                "api_key_present": bool(tidycal_service.api_key),
                "webhook_configured": bool(tidycal_service.webhook_secret),
                "total_booking_pages": total_pages,
                "total_bookings": total_bookings,
                "last_sync": last_sync.isoformat() if last_sync else None
            }
        }
        
    except Exception as e:
        print(f"❌ Error getting integration status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get integration status: {str(e)}")

async def get_booking_analytics(booking_page_id: Optional[str] = None):
    """Get booking analytics"""
    try:
        query = TidyCalBooking.all()
        
        if booking_page_id:
            try:
                query = query.filter(booking_page_id=uuid.UUID(booking_page_id))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid booking page ID format")
        
        bookings = await query
        
        # Calculate analytics
        total_bookings = len(bookings)
        confirmed_bookings = len([b for b in bookings if b.booking_status == "confirmed"])
        cancelled_bookings = len([b for b in bookings if b.booking_status == "cancelled"])
        completed_bookings = len([b for b in bookings if b.booking_status == "completed"])
        no_show_bookings = len([b for b in bookings if b.booking_status == "no_show"])
        
        # Popular times analysis
        time_counts = {}
        for booking in bookings:
            hour = booking.scheduled_time.hour
            time_slot = f"{hour:02d}:00"
            time_counts[time_slot] = time_counts.get(time_slot, 0) + 1
        
        most_popular_times = [
            {"time": time, "count": count}
            for time, count in sorted(time_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Monthly trends
        monthly_trends = {}
        for booking in bookings:
            month_key = booking.scheduled_date.strftime("%Y-%m")
            monthly_trends[month_key] = monthly_trends.get(month_key, 0) + 1
        
        # Average duration
        total_duration = sum(booking.duration_minutes for booking in bookings)
        average_duration = total_duration / total_bookings if total_bookings > 0 else 0
        
        return {
            "success": True,
            "data": {
                "total_bookings": total_bookings,
                "confirmed_bookings": confirmed_bookings,
                "cancelled_bookings": cancelled_bookings,
                "completed_bookings": completed_bookings,
                "no_show_bookings": no_show_bookings,
                "most_popular_times": most_popular_times,
                "booking_trends": monthly_trends,
                "average_booking_duration": round(average_duration, 1)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting booking analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get booking analytics: {str(e)}")