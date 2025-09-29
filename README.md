# Property Web Backend

A comprehensive FastAPI-based backend application for property management and rental services, featuring integrated media handling, role-based authentication, and complete CRUD operations.

## Project Overview

This backend service provides a robust foundation for property rental and management platforms, offering admin property management capabilities, public property browsing, user authentication, team management, and automated communication systems.

## Tech Stack

- **Framework**: FastAPI 0.117.1+
- **ORM**: Tortoise ORM 0.25.1+ with async PostgreSQL support
- **Database**: PostgreSQL with asyncpg driver
- **Authentication**: JWT tokens with HTTP-only cookies and bcrypt password hashing
- **Email Service**: aiosmtplib for SMTP email delivery
- **File Processing**: Python multipart with Pillow for image compression and base64 storage
- **Validation**: Pydantic 2.11.9+ with email validation support
- **Development**: UV for dependency management and Python 3.11+

## Architecture Overview

The application follows a layered architecture pattern with clear separation of concerns:

### Core Components

**Application Layer** (`main.py`)
- FastAPI application initialization and configuration
- CORS middleware for cross-origin requests
- Session middleware for secure cookie handling
- Route registration with role-based dependencies
- Database connection initialization

**Authentication & Authorization** (`authMiddleware/`)
- JWT token validation and cookie authentication
- Role-based access control (admin/user permissions)
- Request authentication middleware integration

**Business Logic** (`controller/`)
- Property management with integrated media processing
- User account management and authentication flows
- Contact form processing and team member management
- Screening question administration

**Data Models** (`model/`)
- Tortoise ORM models with PostgreSQL backend
- Property model with comprehensive attributes (20+ fields)
- PropertyMedia model for base64 file storage
- User model with role-based permissions
- Relational models for contacts, teams, and screening questions

**API Routes** (`routes/`)
- RESTful endpoint definitions with FastAPI routers
- Admin and public access separation
- Form-data multipart support for file uploads
- Query parameter validation and filtering

**Data Validation** (`schemas/`)
- Pydantic schemas for request/response validation
- Type-safe data serialization and deserialization
- Email format validation and custom validators

### Database Design

The system uses a relational PostgreSQL database with the following key relationships:

- **Users**: Role-based authentication (admin) with email verification
- **Properties**: Comprehensive property information with status management
- **PropertyMedia**: One-to-many relationship with properties for multiple file storage
- **Contacts**: Contact form submissions with admin management capabilities
- **Teams**: Team member information restricted to admin access
- **ScreeningQuestions**: Property application screening system

## Project Structure

```
backend/
├── main.py                     # FastAPI application entry point and configuration
├── pyproject.toml             # UV project dependencies and Python requirements
├── uv.lock                    # Locked dependency versions for reproducible builds
├── .env                       # Environment variables (not in repository)
├── .python-version            # Python version specification
│
├── authMiddleware/            # Authentication and authorization middleware
│   ├── authMiddleware.py      # JWT token validation and cookie authentication
│   └── roleMiddleware.py      # Role-based access control decorators
│
├── config/                    # Configuration and utility modules
│   ├── fileUpload.py          # General media upload with base64 processing
│   └── nodemailer.py          # SMTP email configuration and setup
│
├── controller/                # Business logic and request handlers
│   ├── contactController.py          # Contact form processing
│   ├── propertyController.py         # Property CRUD with integrated media
│   ├── propertyMediaController.py    # Media management utilities
│   ├── screeningQuestionController.py # Application screening logic
│   ├── teamController.py             # Team member management
│   └── userController.py             # User authentication and profile
│
├── dbConnection/              # Database configuration and connection
│   └── dbConfig.py            # Tortoise ORM setup and PostgreSQL connection
│
├── emailService/              # Email delivery services
│   ├── authEmail.py           # Authentication and verification emails
│   └── contactEmail.py        # Contact form notification emails
│
├── model/                     # Tortoise ORM database models
│   ├── contactModel.py        # Contact form data model
│   ├── propertyMediaModel.py  # Property media storage model
│   ├── propertyModel.py       # Main property information model
│   ├── screeningQuestionModel.py # Application screening model
│   ├── teamModel.py           # Team member information model
│   └── userModel.py           # User account and authentication model
│
├── routes/                    # FastAPI router definitions
│   ├── authRoute.py           # Authentication endpoints
│   ├── contactRoute.py        # Contact form and management routes
│   ├── profileRoute.py        # User profile management
│   ├── propertyRoute.py       # Property CRUD with admin/public separation
│   ├── screeningQuestionRoute.py # Screening question management
│   └── teamRoute.py           # Team member administration
│
├── schemas/                   # Pydantic validation schemas
│   ├── contactSchemas.py      # Contact form validation
│   ├── propertyMediaSchemas.py # Media upload validation
│   ├── propertySchemas.py     # Property data validation
│   ├── screeningQuestionSchemas.py # Screening validation
│   ├── teamSchemas.py         # Team member validation
│   └── userSchemas.py         # User registration and profile validation
│
└── services/                  # Utility and helper services
    ├── authServices.py        # JWT token generation and validation utilities
    └── cookieServices.py      # HTTP-only cookie management
```

## API Architecture

### Endpoint Organization

**Authentication Routes** (`/api/auth`)
- Public authentication endpoints for user registration and login
- Email verification and password reset functionality
- Session management with secure cookie handling

**Admin Property Management** (`/api/admin/properties`)
- Complete property CRUD operations restricted to admin users
- Integrated media upload supporting multiple files per property
- Property status management (available, rented, maintenance)
- Comprehensive property details with location and amenity information

**Public Property Access** (`/api/properties`)
- Public property browsing with filtered information
- Property search and filtering capabilities
- Read-only access to approved property listings

**User Profile Management** (`/api/user`)
- Authenticated user profile access and updates
- User preference management and account settings

**Team Administration** (`/api/team`)
- Admin-only team member management
- Team information and role assignment

**Contact Management**
- Public contact form submission (`/api/public/contact`)
- Admin contact review and management (`/api/admin/contact`)

**Screening Questions** (`/api/screening`)
- Property application screening system
- Admin management of screening criteria

### Authentication Flow

1. **User Registration**: Email validation with verification token
2. **Login Process**: JWT token generation with HTTP-only cookie storage
3. **Request Authentication**: Middleware validates cookies on protected routes
4. **Role Authorization**: Admin/user role separation for restricted endpoints
5. **Password Recovery**: Secure token-based password reset system

### Media Processing Pipeline

1. **File Upload**: Multipart form-data reception with validation
2. **Image Processing**: Pillow-based compression and optimization
3. **Base64 Conversion**: Secure storage format for database persistence
4. **Integration**: Seamless media attachment during property creation/updates

## Installation and Setup

### Prerequisites

- Python 3.11 or higher
- UV package manager
- PostgreSQL database instance
- SMTP email service (Gmail recommended)

### Installation Steps

1. **Clone Repository**
```bash
git clone <repository-url>
cd property-web-backend
```

2. **Install Dependencies**
```bash
uv sync
```

3. **Environment Configuration**
Create `.env` file with required variables:
```env
# Database Configuration
DB_NAME=your name
DB_USER=your user name
DB_PASS=your pass 
DB_HOST=your host
DB_PORT=6543

# JWT Authentication
JWT_SECRET=your_secure_jwt_secret_key


# SMTP Email Service
ADMIN_EMAIL=your admin email
ADMIN_PASSWORD=you admin pass
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=same as admin for now
EMAIL_PASS=same as admin for now
EMAIL_FROM=same as admin for now

# Application Configuration
FRONTEND_URL=http://localhost:3000
PORT=8001
```

4. **Database Setup**
Ensure PostgreSQL is running.


5. **Start Development Server**
```bash
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

## API Documentation

### Interactive Documentation
- **Swagger UI**: http://127.0.0.1:8001/docs
- **ReDoc**: http://127.0.0.1:8001/redoc

### Core Endpoints

#### Authentication System
```
POST /api/auth/signup                 - User registration with email verification
POST /api/auth/login                  - User authentication with cookie session
POST /api/auth/logout                 - Session termination
POST /api/auth/forgot-password        - Password reset request
POST /api/auth/reset-password/{token} - Password reset confirmation
GET  /api/auth/verify-email/{token}   - Email address verification
POST /api/auth/resend-verification    - Resend verification email
```

#### Property Management
```
# Admin Routes (Authentication + Admin Role Required)
POST /api/admin/properties/add            - Create property with optional media
PUT  /api/admin/properties/{property_id}  - Update property with optional media  
DELETE /api/admin/properties/{property_id} - Delete property and associated media
GET  /api/admin/properties                - Get all properties (admin detailed view)
GET  /api/admin/properties/{property_id}  - Get property by ID (admin view)

# Public Routes (Authentication Required)
GET /api/properties                    - Get public property listings (filtered)
GET /api/properties/{property_id}      - Get public property details
```

#### User Management
```
GET  /api/user/profile    - Get user profile (Authentication Required)
PUT  /api/user/profile    - Update user profile (Authentication Required)
```

#### Team Administration
```
GET    /api/team          - Get team members (Admin Only)
POST   /api/team          - Add team member (Admin Only)
PUT    /api/team/{id}     - Update team member (Admin Only)
DELETE /api/team/{id}     - Remove team member (Admin Only)
```

#### Contact Management
```
POST /api/public/contact  - Submit contact form (Public)
GET  /api/admin/contacts  - Get contact submissions (Admin Only)
PUT  /api/admin/contacts/{id} - Update contact status (Admin Only)
```

#### Screening Questions
```
GET    /api/screening     - Get screening questions
POST   /api/screening     - Create screening question (Admin Only)
PUT    /api/screening/{id} - Update screening question (Admin Only)
DELETE /api/screening/{id} - Delete screening question (Admin Only)
```



### Development Configuration

For development environments, ensure the following:
- PostgreSQL database is accessible and properly configured
- SMTP credentials are valid (Gmail App Password recommended)
- Frontend URL matches your development frontend server
- CORS origins are properly configured for cross-origin requests

## Development Guidelines

### Code Organization
- Follow Python PEP 8 style guidelines
- Use type hints throughout the codebase
- Implement consistent error handling patterns
- Maintain clear separation between routes, controllers, and models

### Database Operations
- Use Tortoise ORM async/await patterns
- Implement proper transaction handling for complex operations
- Follow database migration best practices
- Maintain referential integrity with foreign key constraints




## License

This project is licensed under the MIT License. See LICENSE file for details.