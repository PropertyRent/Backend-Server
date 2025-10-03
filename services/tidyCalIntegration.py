import os
import uuid
import aiohttp
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from fastapi import HTTPException

class TidyCalIntegration:
    """
    TidyCal API Integration Service for Property Meeting Scheduling
    
    This service integrates with TidyCal to provide professional scheduling
    capabilities for property viewings and meetings.
    """
    
    def __init__(self):
        self.api_key = os.getenv("TIDYCAL_API_KEY")
        self.base_url = "https://api.tidycal.com/v1"
        self.webhook_secret = os.getenv("TIDYCAL_WEBHOOK_SECRET")
        
        if not self.api_key:
            print("⚠️ TidyCal API key not found. Some features will be limited.")
    
    async def create_booking_page(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a custom booking page for a specific property
        
        Args:
            property_data: Dictionary containing property information
            
        Returns:
            Dictionary with booking page details including URL
        """
        if not self.api_key:
            raise HTTPException(status_code=500, detail="TidyCal API key not configured")
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                booking_page_data = {
                    "name": f"Property Viewing - {property_data.get('title', 'Property')}",
                    "description": f"Schedule a viewing for {property_data.get('title', 'this property')} located at {property_data.get('address', 'the specified address')}",
                    "duration": 60,  # 60 minutes default
                    "buffer_before": 15,  # 15 minutes buffer before
                    "buffer_after": 15,   # 15 minutes buffer after
                    "location": property_data.get('address', 'Property Location'),
                    "questions": [
                        {
                            "question": "What is your preferred viewing time?",
                            "type": "text",
                            "required": False
                        },
                        {
                            "question": "Any specific areas of the property you'd like to focus on?",
                            "type": "textarea",
                            "required": False
                        },
                        {
                            "question": "Will you be bringing anyone else to the viewing?",
                            "type": "text",
                            "required": False
                        }
                    ],
                    "custom_fields": {
                        "property_id": str(property_data.get('id', '')),
                        "property_title": property_data.get('title', ''),
                        "property_price": str(property_data.get('price', ''))
                    }
                }
                
                async with session.post(
                    f"{self.base_url}/booking-pages",
                    headers=headers,
                    json=booking_page_data
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        return {
                            "success": True,
                            "booking_page_id": result.get("id"),
                            "booking_url": result.get("booking_url"),
                            "embed_code": result.get("embed_code"),
                            "data": result
                        }
                    else:
                        error_text = await response.text()
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"TidyCal API error: {error_text}"
                        )
                        
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TidyCal integration error: {str(e)}")
    
    async def get_booking_page(self, booking_page_id: str) -> Dict[str, Any]:
        """Get booking page details"""
        if not self.api_key:
            raise HTTPException(status_code=500, detail="TidyCal API key not configured")
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                async with session.get(
                    f"{self.base_url}/booking-pages/{booking_page_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "data": result
                        }
                    else:
                        error_text = await response.text()
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"TidyCal API error: {error_text}"
                        )
                        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching booking page: {str(e)}")
    
    async def get_bookings(self, booking_page_id: Optional[str] = None, 
                          start_date: Optional[date] = None, 
                          end_date: Optional[date] = None) -> Dict[str, Any]:
        """Get bookings from TidyCal"""
        if not self.api_key:
            raise HTTPException(status_code=500, detail="TidyCal API key not configured")
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                params = {}
                if booking_page_id:
                    params["booking_page_id"] = booking_page_id
                if start_date:
                    params["start_date"] = start_date.isoformat()
                if end_date:
                    params["end_date"] = end_date.isoformat()
                
                async with session.get(
                    f"{self.base_url}/bookings",
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "bookings": result.get("data", []),
                            "total": result.get("total", 0)
                        }
                    else:
                        error_text = await response.text()
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"TidyCal API error: {error_text}"
                        )
                        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching bookings: {str(e)}")
    
    async def cancel_booking(self, booking_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Cancel a booking in TidyCal"""
        if not self.api_key:
            raise HTTPException(status_code=500, detail="TidyCal API key not configured")
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                cancel_data = {
                    "reason": reason or "Cancelled by property manager"
                }
                
                async with session.post(
                    f"{self.base_url}/bookings/{booking_id}/cancel",
                    headers=headers,
                    json=cancel_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "message": "Booking cancelled successfully",
                            "data": result
                        }
                    else:
                        error_text = await response.text()
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"TidyCal API error: {error_text}"
                        )
                        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error cancelling booking: {str(e)}")
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify TidyCal webhook signature"""
        if not self.webhook_secret:
            return True  # Skip verification if no secret configured
        
        import hmac
        import hashlib
        
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    
    def generate_embed_code(self, booking_url: str, width: str = "100%", height: str = "600px") -> str:
        """Generate iframe embed code for TidyCal booking page"""
        return f'''<iframe
    src="{booking_url}"
    width="{width}"
    height="{height}"
    frameborder="0"
    scrolling="auto"
    title="Schedule Property Viewing">
</iframe>'''

# Create global instance
tidycal_service = TidyCalIntegration()