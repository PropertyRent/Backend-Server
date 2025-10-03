# 🏠 Property Meeting Booking System

This guide shows how to implement property viewing bookings using TidyCal integration.

## 🎯 How It Works

When users visit a property details page, they can click "Book Schedule Viewing" which redirects them directly to TidyCal for booking.

## 📋 API Endpoints

### 1. Check Property Booking Availability

```http
GET /tidycal/properties/{property_id}/booking-status
```

**Response Example:**
```json
{
  "success": true,
  "data": {
    "property_id": "123e4567-e89b-12d3-a456-426614174000",
    "has_booking_available": true,
    "booking_url": "https://tidycal.com/book/property-viewing-123",
    "booking_redirect_url": "/tidycal/properties/123e4567-e89b-12d3-a456-426614174000/book-viewing",
    "page_name": "Property Viewing - Beautiful Apartment",
    "duration_minutes": 60,
    "description": "Schedule a viewing for this beautiful apartment"
  }
}
```

### 2. Direct Booking Redirect

```http
GET /tidycal/properties/{property_id}/book-viewing
```

This endpoint automatically redirects users to the TidyCal booking page.

### 3. Get Property Details (Enhanced)

The existing property details endpoint at `/properties/{property_id}` now includes booking information when available.

## 🎨 Frontend Implementation

### React Example

```jsx
import React, { useEffect, useState } from 'react';

function PropertyDetails({ propertyId }) {
  const [property, setProperty] = useState(null);
  const [bookingInfo, setBookingInfo] = useState(null);

  useEffect(() => {
    // Fetch property details
    fetch(`/api/properties/${propertyId}`)
      .then(res => res.json())
      .then(data => setProperty(data.data));

    // Check booking availability
    fetch(`/api/tidycal/properties/${propertyId}/booking-status`)
      .then(res => res.json())
      .then(data => setBookingInfo(data.data));
  }, [propertyId]);

  const handleBookViewing = () => {
    if (bookingInfo?.has_booking_available) {
      // Redirect to booking page
      window.location.href = `/api/tidycal/properties/${propertyId}/book-viewing`;
    }
  };

  return (
    <div className="property-details">
      <h1>{property?.title}</h1>
      <p>{property?.description}</p>
      
      {/* Property Details */}
      <div className="property-info">
        <p>Price: ${property?.price}</p>
        <p>Bedrooms: {property?.bedrooms}</p>
        <p>Bathrooms: {property?.bathrooms}</p>
      </div>

      {/* Booking Section */}
      {bookingInfo?.has_booking_available ? (
        <div className="booking-section">
          <h3>Schedule a Viewing</h3>
          <p>{bookingInfo.description}</p>
          <p>Duration: {bookingInfo.duration_minutes} minutes</p>
          
          <button 
            onClick={handleBookViewing}
            className="btn btn-primary"
          >
            📅 Book Schedule Viewing
          </button>
        </div>
      ) : (
        <div className="booking-unavailable">
          <p>Booking not available for this property</p>
        </div>
      )}
    </div>
  );
}
```

### HTML/JavaScript Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>Property Details</title>
    <style>
        .booking-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .booking-btn {
            background: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
        }
        .booking-btn:hover {
            background: #0056b3;
        }
    </style>
</head>
<body>
    <div id="property-details"></div>

    <script>
        async function loadPropertyDetails(propertyId) {
            try {
                // Load property details
                const propertyResponse = await fetch(`/api/properties/${propertyId}`);
                const propertyData = await propertyResponse.json();

                // Check booking availability
                const bookingResponse = await fetch(`/api/tidycal/properties/${propertyId}/booking-status`);
                const bookingData = await bookingResponse.json();

                // Render property details
                const container = document.getElementById('property-details');
                container.innerHTML = `
                    <h1>${propertyData.data.title}</h1>
                    <p>${propertyData.data.description}</p>
                    
                    <div class="property-info">
                        <p><strong>Price:</strong> $${propertyData.data.price}</p>
                        <p><strong>Bedrooms:</strong> ${propertyData.data.bedrooms}</p>
                        <p><strong>Bathrooms:</strong> ${propertyData.data.bathrooms}</p>
                    </div>

                    ${bookingData.data.has_booking_available ? `
                        <div class="booking-section">
                            <h3>Schedule a Viewing</h3>
                            <p>${bookingData.data.description}</p>
                            <p><strong>Duration:</strong> ${bookingData.data.duration_minutes} minutes</p>
                            
                            <button class="booking-btn" onclick="bookViewing('${propertyId}')">
                                📅 Book Schedule Viewing
                            </button>
                        </div>
                    ` : `
                        <div class="booking-unavailable">
                            <p>Booking not available for this property</p>
                        </div>
                    `}
                `;
            } catch (error) {
                console.error('Error loading property details:', error);
            }
        }

        function bookViewing(propertyId) {
            // Redirect to booking page
            window.location.href = `/api/tidycal/properties/${propertyId}/book-viewing`;
        }

        // Load for specific property (replace with actual property ID)
        loadPropertyDetails('123e4567-e89b-12d3-a456-426614174000');
    </script>
</body>
</html>
```

## 🔧 Setup Instructions

### 1. Admin Creates Booking Page

First, an admin needs to create a TidyCal booking page for the property:

```bash
curl -X POST "http://localhost:8001/admin/tidycal/booking-pages?property_id=YOUR_PROPERTY_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "page_name": "Property Viewing - Beautiful Apartment",
    "description": "Schedule a viewing for this beautiful apartment",
    "duration_minutes": 60,
    "buffer_before": 15,
    "buffer_after": 15,
    "is_public": true,
    "custom_questions": [
      {
        "question": "What time of day works best for you?",
        "type": "text",
        "required": false
      }
    ]
  }'
```

### 2. Frontend Integration

Use the endpoints above to:
1. Check if booking is available for a property
2. Show/hide the "Book Schedule Viewing" button
3. Redirect users to TidyCal when they click the button

### 3. User Experience Flow

1. **User visits property details page**
2. **Frontend checks booking availability** (`/tidycal/properties/{id}/booking-status`)
3. **If available, shows "Book Schedule Viewing" button**
4. **User clicks button**
5. **Frontend redirects to** `/tidycal/properties/{id}/book-viewing`
6. **Backend redirects to TidyCal booking page**
7. **User completes booking on TidyCal**
8. **Webhook syncs booking back to your system**

## 🎛️ Admin Management

Admins can manage booking pages through these endpoints:

- `GET /admin/tidycal/booking-pages` - List all booking pages
- `POST /admin/tidycal/booking-pages` - Create new booking page
- `GET /admin/tidycal/analytics` - View booking analytics

## 🔗 Integration Benefits

- **Seamless UX**: Users stay in your app flow until booking
- **Professional Scheduling**: TidyCal handles complex scheduling logic
- **Real-time Sync**: Bookings automatically sync back to your database
- **Analytics**: Track booking performance and popular times
- **Customizable**: Custom questions and branding options

## 🚀 Next Steps

1. Configure TidyCal API credentials
2. Create booking pages for your properties
3. Implement frontend booking buttons
4. Test the full user flow
5. Monitor booking analytics

The system is now ready for property viewing bookings! 🎉