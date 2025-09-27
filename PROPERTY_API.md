# Property API Documentation

## Overview
This API provides endpoints for managing properties and their associated media. All endpoints require authentication and appropriate user roles.

## Base URL
```
http://localhost:8001/api
```

## Authentication
All property endpoints require authentication. Users must be logged in with a valid token and have either "user" or "admin" role.

---

## Property Endpoints

### 1. Create Property
**POST** `/properties`

Create a new property listing.

**Request Body:**
```json
{
  "title": "Beautiful 2BR Apartment",
  "description": "Spacious apartment in downtown area",
  "property_type": "apartment",
  "status": "available",
  "furnishing": "furnished",
  "area_sqft": 1200.50,
  "bedrooms": 2,
  "bathrooms": 1,
  "floors": 1,
  "utilities": ["electricity", "water", "internet"],
  "lease_term": "12 months",
  "application_fee": 100.00,
  "amenities": ["gym", "pool", "parking"],
  "pet_policy": "No pets allowed",
  "appliances_included": ["refrigerator", "dishwasher"],
  "property_management_contact": "contact@example.com",
  "website": "https://example.com",
  "price": 2500.00,
  "deposit": 2500.00,
  "address": "123 Main St",
  "city": "New York",
  "state": "NY",
  "pincode": "10001",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "available_from": "2024-01-01T00:00:00"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Property created successfully",
  "data": {
    "id": "uuid",
    "title": "Beautiful 2BR Apartment",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "media": []
  }
}
```

### 2. Update Property
**PUT** `/properties/{property_id}`

Update an existing property. Only provided fields will be updated.

**Request Body:** (Same as create, but all fields optional)
```json
{
  "title": "Updated Property Title",
  "price": 2600.00
}
```

### 3. Delete Property
**DELETE** `/properties/{property_id}`

Delete a property and all its associated media.

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Property deleted successfully"
}
```

### 4. Get All Properties
**GET** `/properties`

Retrieve all properties with filtering and pagination.

**Query Parameters:**
- `limit` (int, 1-100): Number of properties to return (default: 10)
- `offset` (int): Number of properties to skip (default: 0)
- `city` (string): Filter by city
- `property_type` (string): Filter by property type
- `status` (string): Filter by status
- `min_price` (float): Minimum price filter
- `max_price` (float): Maximum price filter
- `bedrooms` (int): Filter by number of bedrooms

**Example:**
```
GET /properties?limit=20&offset=0&city=New York&min_price=2000&max_price=3000&bedrooms=2
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "properties": [...],
    "pagination": {
      "total": 150,
      "limit": 20,
      "offset": 0,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### 5. Get Property by ID
**GET** `/properties/{property_id}`

Retrieve a single property by its ID.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Beautiful 2BR Apartment",
    "description": "Spacious apartment...",
    "price": 2500.00,
    "media": [...]
  }
}
```

---

## Property Media Endpoints

### 1. Add Property Media
**POST** `/properties/media`

Add media (images/videos) to a property.

**Request Body:**
```json
{
  "property_id": "uuid",
  "media_type": "image",
  "url": "https://example.com/image.jpg",
  "is_cover": true
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Property media added successfully",
  "data": {
    "id": "uuid",
    "property_id": "uuid",
    "media_type": "image",
    "url": "https://example.com/image.jpg",
    "is_cover": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 2. Update Property Media
**PUT** `/properties/media/{media_id}`

Update property media information.

**Request Body:**
```json
{
  "is_cover": false,
  "url": "https://example.com/updated-image.jpg"
}
```

### 3. Get Property Media
**GET** `/properties/{property_id}/media`

Get all media for a specific property.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "property_id": "uuid",
      "media_type": "image",
      "url": "https://example.com/image.jpg",
      "is_cover": true,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ]
}
```

### 4. Delete Property Media
**DELETE** `/properties/media/{media_id}`

Delete a specific media item.

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Property media deleted successfully"
}
```

---

## Error Responses

### Common Error Codes:
- `400 Bad Request`: Invalid input data or parameters
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Property or media not found
- `500 Internal Server Error`: Server-side error

**Error Response Format:**
```json
{
  "detail": "Error message description"
}
```

---

## Property Types
Suggested property types:
- `apartment`
- `house`
- `condo`
- `studio`
- `townhouse`
- `loft`
- `duplex`

## Property Status
Suggested status values:
- `available`
- `rented`
- `pending`
- `maintenance`

## Media Types
- `image`
- `video`

---

## Testing the API

You can test the API using tools like Postman, curl, or the FastAPI automatic documentation at:
```
http://localhost:8001/docs
```

### Example curl commands:

**Get all properties:**
```bash
curl -X GET "http://localhost:8001/api/properties" \
  -H "Cookie: token=your_auth_token"
```

**Create a property:**
```bash
curl -X POST "http://localhost:8001/api/properties" \
  -H "Content-Type: application/json" \
  -H "Cookie: token=your_auth_token" \
  -d '{
    "title": "Test Property",
    "property_type": "apartment",
    "status": "available",
    "price": 2000.00
  }'
```