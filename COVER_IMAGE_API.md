# Property Cover Image API

## Overview
Public endpoints to get cover images for properties. These endpoints don't require authentication and can be accessed by anyone.

## Endpoints

### 1. Get Cover Image for Specific Property
```
GET /api/properties/{property_id}/cover-image
```

**Description:** Get the cover image for a specific property.

**Parameters:**
- `property_id` (path): UUID of the property

**Response:**
- Returns the media file where `is_cover=True`
- If no cover image is set, returns the first available image as fallback
- If no images exist, returns 404 error

**Example Request:**
```bash
GET /api/properties/bb069a98-3f27-4122-83f2-01ceaf628723/cover-image
```

**Example Response (Success):**
```json
{
  "success": true,
  "message": "Cover image found",
  "data": {
    "id": "media-uuid-here",
    "property_id": "bb069a98-3f27-4122-83f2-01ceaf628723",
    "media_type": "image",
    "url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
    "is_cover": true,
    "created_at": "2025-09-30T10:00:00",
    "updated_at": "2025-09-30T10:00:00"
  }
}
```

**Example Response (Fallback):**
```json
{
  "success": true,
  "message": "No cover image set, returning first available image",
  "data": {
    "id": "media-uuid-here",
    "property_id": "bb069a98-3f27-4122-83f2-01ceaf628723",
    "media_type": "image",
    "url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
    "is_cover": false,
    "created_at": "2025-09-30T10:00:00",
    "updated_at": "2025-09-30T10:00:00"
  }
}
```

**Example Response (No Images):**
```json
{
  "detail": "No images found for this property"
}
```

### 2. Get All Property Cover Images
```
GET /api/properties/cover-images/all
```

**Description:** Get cover images for all properties that have a cover image set.

**Parameters:** None

**Response:**
- Returns array of all media files where `is_cover=True`
- Includes property title for context

**Example Request:**
```bash
GET /api/properties/cover-images/all
```

**Example Response:**
```json
{
  "success": true,
  "message": "Found 3 cover images",
  "data": [
    {
      "id": "media-uuid-1",
      "property_id": "property-uuid-1",
      "property_title": "Beautiful 2BHK Apartment",
      "media_type": "image",
      "url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
      "is_cover": true,
      "created_at": "2025-09-30T10:00:00",
      "updated_at": "2025-09-30T10:00:00"
    },
    {
      "id": "media-uuid-2",
      "property_id": "property-uuid-2",
      "property_title": "Luxury Villa",
      "media_type": "image",
      "url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
      "is_cover": true,
      "created_at": "2025-09-30T09:30:00",
      "updated_at": "2025-09-30T09:30:00"
    }
  ],
  "total": 2
}
```

## Use Cases

### Frontend Gallery
```javascript
// Get cover image for property card display
fetch('/api/properties/123e4567-e89b-12d3-a456-426614174000/cover-image')
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Display the cover image
      const img = document.createElement('img');
      img.src = data.data.url;
      document.getElementById('property-card').appendChild(img);
    }
  });
```

### Property Showcase
```javascript
// Get all cover images for homepage showcase
fetch('/api/properties/cover-images/all')
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      data.data.forEach(coverImage => {
        // Create property preview cards
        createPropertyCard(coverImage);
      });
    }
  });
```

## Error Handling

### Common Error Responses:

**Invalid Property ID:**
```json
{
  "detail": "Invalid property ID format"
}
```

**Property Not Found:**
```json
{
  "detail": "Property not found"
}
```

**No Images Available:**
```json
{
  "detail": "No images found for this property"
}
```

## Features

✅ **Public Access** - No authentication required  
✅ **Fallback Logic** - Returns first image if no cover is set  
✅ **Base64 Support** - Returns ready-to-use base64 image data  
✅ **Property Context** - Includes property information  
✅ **Error Handling** - Comprehensive error messages  
✅ **Fast Response** - Direct database queries for performance