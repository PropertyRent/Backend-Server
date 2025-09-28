# Property Rental Backend System Overview

## System Architecture

This is a comprehensive backend system for a property rental platform built with **FastAPI**, **Tortoise ORM**, and **PostgreSQL/Supabase**. The system includes user management, property listings, team management, and customer communication features.

---

##  Technology Stack

- **Framework**: FastAPI (Python web framework)
- **ORM**: Tortoise ORM (async ORM for Python)
- **Database**: PostgreSQL with Supabase
- **Authentication**: JWT tokens with cookie-based sessions
- **File Storage**: Base64 encoding in database
- **Email Service**: Custom SMTP integration
- **Image Processing**: PIL (Pillow) for image compression
- **Validation**: Pydantic schemas

---

##  Project Structure

```
Backend/
├── main.py                    # FastAPI application entry point
├── pyproject.toml            # Project dependencies
├── PROPERTY_API.md           # Property API documentation
├── CONTACT_API.md            # Contact API documentation
├── 
├── authMiddleware/           # Authentication & authorization
│   ├── authMiddleware.py     # JWT authentication middleware
│   └── roleMiddleware.py     # Role-based access control
├── 
├── config/                   # Configuration files
│   ├── fileUpload.py         # Base64 image upload processing
│   └── nodemailer.py         # Email service configuration
├── 
├── controller/               # Business logic controllers
│   ├── userController.py     # User management
│   ├── propertyController.py # Property CRUD operations
│   ├── propertyMediaController.py # Property media management
│   ├── teamController.py     # Team member management
│   └── contactController.py  # Contact form & admin replies
├── 
├── dbConnection/            # Database configuration
│   └── dbConfig.py          # Tortoise ORM & Supabase setup
├── 
├── emailService/            # Email templates & services
│   ├── authEmail.py         # Authentication emails
│   └── contactEmail.py      # Contact form emails
├── 
├── model/                   # Database models (ORM entities)
│   ├── userModel.py         # User entity
│   ├── propertyModel.py     # Property entity
│   ├── propertyMediaModel.py # Property media entity
│   ├── teamModel.py         # Team member entity
│   └── contactModel.py      # Contact form entity
├── 
├── routes/                  # API route definitions
│   ├── authRoute.py         # Authentication routes
│   ├── profileRoute.py      # User profile routes
│   ├── propertyRoute.py     # Property management routes
│   ├── teamRoute.py         # Team management routes
│   └── contactRoute.py      # Contact form routes
├── 
├── schemas/                 # Pydantic validation schemas
│   ├── userSchemas.py       # User data validation
│   ├── propertySchemas.py   # Property data validation
│   ├── propertyMediaSchemas.py # Property media validation
│   ├── teamSchemas.py       # Team member validation
│   └── contactSchemas.py    # Contact form validation
├── 
└── services/               # Business services
    ├── authServices.py     # Authentication logic
    └── cookieServices.py   # Cookie management
```

---

##  Database Models

### 1. User Model (`userModel.py`)
```python
- id: UUID (primary key)
- email: String (unique)
- password: Hashed string
- full_name: String
- phone: String
- role: Enum (user, admin)
- profile_image: Text (base64)
- is_verified: Boolean
- created_at: DateTime
- updated_at: DateTime
```

### 2. Property Model (`propertyModel.py`)
```python
- id: UUID (primary key)
- title: String
- description: Text
- price: Decimal
- address: String
- city: String
- state: String
- zip_code: String
- country: String
- property_type: Enum
- bedrooms: Integer
- bathrooms: Integer
- area_sqft: Integer
- is_available: Boolean
- amenities: JSON
- rules: JSON
- created_at: DateTime
- updated_at: DateTime
```

### 3. Property Media Model (`propertyMediaModel.py`)
```python
- id: UUID (primary key)
- property_id: UUID (foreign key)
- image_data: Text (base64)
- is_cover_image: Boolean
- created_at: DateTime
```

### 4. Team Model (`teamModel.py`)
```python
- id: UUID (primary key)
- name: String
- age: Integer
- email: String
- phone: String
- position_name: String
- description: Text
- photo: Text (base64)
- created_at: DateTime
- updated_at: DateTime
```

### 5. Contact Model (`contactModel.py`)
```python
- id: UUID (primary key)
- full_name: String
- email: String
- message: Text
- status: Enum (pending, replied, resolved)
- admin_reply: Text (nullable)
- admin_reply_date: DateTime (nullable)
- created_at: DateTime
- updated_at: DateTime
```

---

##  Authentication System

### Features:
- **JWT-based authentication** with HTTP-only cookies
- **Role-based access control** (user, admin)
- **Email verification** system
- **Password reset** functionality
- **Session management** with secure cookies

### Middleware:
- `authMiddleware.py`: Validates JWT tokens from cookies
- `roleMiddleware.py`: Checks user roles for protected routes

---

##  File Upload System

### Base64 Image Storage:
- **Location**: `config/fileUpload.py`
- **Features**:
  - Image validation using python-magic
  - Automatic compression using PIL
  - Base64 encoding for database storage
  - Support for JPEG, PNG, GIF formats
  - File size limits and dimension constraints

### Usage:
- User profile images
- Property media galleries
- Team member photos

---

##  Email System

### Email Services:
- **Authentication emails**: Welcome, verification, password reset
- **Contact form emails**: User confirmation, admin notifications, replies
- **Professional HTML templates** with responsive design

### Configuration:
- SMTP integration via `config/nodemailer.py`
- Email templates in `emailService/` directory
- Support for Gmail, Outlook, and custom SMTP servers

---

##  API Routes

### Public Routes (No Authentication):
```
POST /auth/register          # User registration
POST /auth/login             # User login
POST /auth/verify-email      # Email verification
POST /auth/forgot-password   # Password reset request
POST /auth/reset-password    # Password reset
GET  /properties             # Public property listings
GET  /properties/{id}        # Individual property details
GET  /team                   # Team member listings
POST /api/public/contact     # Contact form submission
```

### Protected User Routes (Authentication Required):
```
GET  /profile                # Get user profile
PUT  /profile                # Update user profile
POST /profile/upload-image   # Upload profile image
GET  /user/properties        # User's properties
POST /properties             # Create property (user)
PUT  /properties/{id}        # Update property (user)
```

### Admin Routes (Admin Role Required):
```
GET    /admin/users           # Manage users
DELETE /admin/users/{id}      # Delete users
GET    /admin/properties      # All properties management
DELETE /admin/properties/{id} # Delete any property
GET    /admin/team            # Team management
POST   /admin/team            # Add team members
PUT    /admin/team/{id}       # Update team members
DELETE /admin/team/{id}       # Remove team members
GET    /admin/contact         # View contact messages
POST   /admin/contact/{id}/reply # Reply to messages
PUT    /admin/contact/{id}/status # Update message status
DELETE /admin/contact/{id}    # Delete messages
```

---

##  Key Features

### 1. Property Management
- **Full CRUD operations** for properties
- **Advanced filtering**: price range, location, type, amenities
- **Pagination and sorting**
- **Media gallery management** with cover image selection
- **Availability tracking**

### 2. User Management
- **Secure registration/login** with email verification
- **Profile management** with image upload
- **Role-based permissions**
- **Password security** with bcrypt hashing

### 3. Team Management
- **Team member profiles** with photos and descriptions
- **Position-based organization**
- **Contact information management**
- **Public team directory**

### 4. Contact System
- **Public contact form** for inquiries
- **Admin management interface**
- **Email notifications** for all parties
- **Status tracking** (pending, replied, resolved)
- **Direct email replies** from admin panel

### 5. Media Management
- **Base64 image storage** in database
- **Automatic image compression**
- **Multiple format support**
- **Cover image designation** for properties

---

##  Configuration

### Database Setup (`dbConnection/dbConfig.py`):
```python
TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": "your-supabase-host",
                "port": 5432,
                "user": "postgres",
                "password": "your-password",
                "database": "postgres",
                "statement_cache_size": 0  # Required for pgbouncer
            }
        }
    },
    "apps": {
        "models": {
            "models": [
                "model.userModel",
                "model.propertyModel", 
                "model.propertyMediaModel",
                "model.teamModel",
                "model.contactModel"
            ],
            "default_connection": "default"
        }
    }
}
```

### Environment Variables Required:
```
DATABASE_URL=postgresql://user:password@host:port/database
JWT_SECRET_KEY=your-secret-key
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
```

---

##  Getting Started

### 1. Install Dependencies:
```bash
uv add  install fastapi tortoise-orm asyncpg python-multipart python-magic pillow bcrypt python-jose[cryptography] python-email-validator
```

### 2. Start the Server:
```bash
cd Backend
python main.py
```

### 3. Access API Documentation:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### 4. Test Database Connection:
The server will automatically:
- Connect to Supabase database
- Create all tables if they don't exist
- Display connection status in console

---

##  API Response Format

### Success Response:
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data
  }
}
```

### Error Response:
```json
{
  "detail": "Error message description"
}
```

### Paginated Response:
```json
{
  "success": true,
  "data": {
    "items": [],
    "pagination": {
      "total": 100,
      "limit": 20,
      "offset": 0,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

---

##  Troubleshooting

### Common Issues:

1. **Database Connection Error**:
   - Check Supabase credentials in `dbConfig.py`
   - Ensure `statement_cache_size: 0` for pgbouncer compatibility

2. **Email Not Sending**:
   - Verify SMTP credentials in `config/nodemailer.py`
   - Check if Gmail app passwords are correctly configured

3. **Image Upload Issues**:
   - Ensure python-magic is properly installed
   - Check file size limits in `config/fileUpload.py`

4. **Authentication Problems**:
   - Verify JWT secret key is set
   - Check cookie settings in browser
   - Ensure tokens haven't expired

---

##  Future Enhancements After Clients Concern Charge may apply

### Planned Features:
- [ ] Property booking system
- [ ] Payment integration
- [ ] Real-time notifications
- [ ] Property reviews and ratings
- [ ] Advanced search with maps
- [ ] Property comparison feature
- [ ] Tenant management system
- [ ] Maintenance request tracking

### Technical Improvements:
- [ ] Redis caching for better performance
- [ ] WebSocket support for real-time updates
- [ ] API rate limiting
- [ ] Automated testing suite
- [ ] Docker containerization
- [ ] CI/CD pipeline setup

---

##  API Documentation Files


---

This backend system provides a solid foundation for a property rental platform with all essential features for users, property management, team showcase, and customer communication.