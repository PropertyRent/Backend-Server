# Property Web Backend

A comprehensive FastAPI-based backend application for property management and rental services, featuring intelligent chatbot integration, property recommendations, meeting scheduling, notices management, and complete CRUD operations with advanced media handling.

## Project Overview

This backend service provides a robust foundation for property rental and#### Meeting & Scheduling
```
# Public Routes (No Authentication Required)
POST /api/meetings/schedule           - Schedule property visit (no login required)

# Admin Routes (Authentication + Admin Role Required)
GET    /api/admin/meetings            - Get all scheduled meetings with filtering
PUT    /api/admin/meetings/{id}       - Update meeting status/details
DELETE /api/admin/meetings/{id}       - Delete meeting
GET    /api/admin/meetings/stats      - Get meeting statistics
PUT    /api/admin/meetings/{id}/approve  - Approve meeting with optional notes
PUT    /api/admin/meetings/{id}/reject   - Reject meeting with optional notes  
PUT    /api/admin/meetings/{id}/complete - Mark meeting as completed
POST   /api/admin/meetings/{id}/reply    - Reply to meeting with approve/reject action
```platforms, offering:
- **Admin Property Management**: Complete property CRUD with integrated statistics and analytics
- **Intelligent Chatbot**: Multi-flow conversation engine for property search, inquiries, and support
- **Property Recommendations**: AI-powered property suggestion system
- **Meeting Scheduling**: Automated property visit scheduling with email notifications
- **Notice Management**: Admin-controlled notices and announcements system
- **Advanced Authentication**: Dual-token system with role-based access control
- **Email Integration**: Comprehensive email notifications for all user interactions

## Tech Stack

- **Framework**: FastAPI 0.117.1+ with comprehensive middleware stack
- **ORM**: Tortoise ORM 0.25.1+ with async PostgreSQL support
- **Database**: PostgreSQL with asyncpg driver and advanced query optimization
- **Authentication**: Dual JWT token system (httponly + accessible) with bcrypt hashing
- **Email Service**: aiosmtplib with HTML template support and admin notifications
- **File Processing**: Advanced multipart handling with Pillow for image optimization and base64 storage
- **Chatbot Engine**: Multi-flow conversation management with email collection and admin notifications
- **Validation**: Pydantic 2.11.9+ with comprehensive schema validation
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
- Property management with statistics, recent properties, and integrated media processing
- Intelligent chatbot system with multiple conversation flows (property search, inquiries, scheduling, feedback, bug reports)
- User account management and authentication flows
- Contact form processing and team member management
- Screening question administration and property recommendations
- Meeting scheduling with automated email notifications
- Notice management for admin announcements

**Data Models** (`model/`)
- Tortoise ORM models with PostgreSQL backend
- Property model with comprehensive attributes (20+ fields) and occupancy tracking
- PropertyMedia model for base64 file storage with multiple images per property
- User model with role-based permissions and profile management
- ChatbotModel with conversation flows, message tracking, and session management
- PropertyRecommendation model for AI-powered suggestions
- ScheduleMeeting model for property visit appointments
- Notice model for admin announcements
- Relational models for contacts, teams, and screening questions

**API Routes** (`routes/`)
- RESTful endpoint definitions with FastAPI routers
- Admin and public access separation with role-based middleware
- Advanced multipart form-data support for large file uploads (5-minute timeout)
- Comprehensive chatbot conversation routing with flow management
- Property recommendation endpoints with filtering and analytics
- Meeting scheduling routes with email automation
- Notice management routes for admin announcements
- Query parameter validation and advanced filtering

**Data Validation** (`schemas/`)
- Pydantic schemas for request/response validation
- Type-safe data serialization and deserialization
- Email format validation and custom validators

### Database Design

The system uses a relational PostgreSQL database with the following key relationships:

- **Users**: Role-based authentication (admin/user) with email verification and profile management
- **Properties**: Comprehensive property information with status management and occupancy tracking
- **PropertyMedia**: One-to-many relationship with properties for multiple file storage (images, documents)
- **ChatbotConversation**: Session-based conversation tracking with flow management
- **ChatbotMessage**: Individual message storage with user responses and timestamps
- **PropertyRecommendation**: AI-powered property suggestions with user preference tracking
- **ScheduleMeeting**: Property visit appointments with automated email notifications
- **Notice**: Admin announcements with priority levels and expiration dates
- **Contacts**: Contact form submissions with admin management capabilities
- **Teams**: Team member information restricted to admin access
- **ScreeningQuestions**: Property application screening system with admin configuration

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
│   ├── contactController.py              # Contact form processing
│   ├── propertyController.py             # Property CRUD with statistics and recent properties
│   ├── propertyMediaController.py        # Media management utilities
│   ├── propertyRecommendationController.py # AI-powered property recommendations
│   ├── scheduleMeetingController.py      # Property visit scheduling with email automation
│   ├── screeningQuestionController.py    # Application screening logic
│   ├── teamController.py                 # Team member management
│   ├── userController.py                 # User authentication and profile
│   ├── noticeController.py               # Admin notices and announcements
│   └── chatbot/                          # Chatbot conversation engine
│       ├── mainChatbotController.py      # Main chatbot flow controller
│       ├── chatbotEngine.py              # Flow definitions and question management
│       ├── conversationController.py     # Session and message management
│       ├── propertySearchController.py   # Property search flow with email collection
│       ├── rentInquiryController.py      # Property inquiry flow
│       ├── scheduleVisitController.py    # Visit scheduling flow
│       ├── chatbotBugReportController.py # Bug reporting flow
│       └── chatbotFeedbackController.py  # Feedback collection flow
│
├── dbConnection/              # Database configuration and connection
│   └── dbConfig.py            # Tortoise ORM setup and PostgreSQL connection
│
├── emailService/              # Email delivery services
│   ├── authEmail.py           # Authentication and verification emails
│   ├── contactEmail.py        # Contact form and chatbot property search notifications
│   ├── meetingEmail.py        # Meeting scheduling email automation
│   ├── recommendationEmail.py # Property recommendation notifications
│   └── chatbotEmail.py        # Chatbot-related email notifications
│
├── model/                     # Tortoise ORM database models
│   ├── contactModel.py        # Contact form data model
│   ├── propertyMediaModel.py  # Property media storage model
│   ├── propertyModel.py       # Main property information model with occupancy tracking
│   ├── propertyRecommendationModel.py # AI property recommendation model
│   ├── scheduleMeetingModel.py # Property visit meeting scheduling model
│   ├── screeningQuestionModel.py # Application screening model
│   ├── teamModel.py           # Team member information model
│   ├── userModel.py           # User account and authentication model
│   ├── noticeModel.py         # Admin notices and announcements model
│   └── chatbotModel.py        # Chatbot conversation and message models
│
├── routes/                    # FastAPI router definitions
│   ├── authRoute.py           # Authentication endpoints
│   ├── contactRoute.py        # Contact form and management routes
│   ├── profileRoute.py        # User profile management
│   ├── propertyRoute.py       # Property CRUD with admin/public separation and statistics
│   ├── propertyRecommendationRoute.py # Property recommendation endpoints
│   ├── scheduleMeetingRoute.py # Meeting scheduling routes with email automation
│   ├── screeningQuestionRoute.py # Screening question management
│   ├── teamRoute.py           # Team member administration
│   ├── noticeRoute.py         # Admin notices and announcements routes
│   └── chatbotRoute.py        # Chatbot conversation endpoints with multi-flow support
│
├── schemas/                   # Pydantic validation schemas
│   ├── contactSchemas.py      # Contact form validation
│   ├── propertyMediaSchemas.py # Media upload validation
│   ├── propertySchemas.py     # Property data validation with comprehensive field validation
│   ├── propertyRecommendationSchemas.py # Property recommendation validation
│   ├── scheduleMeetingSchemas.py # Meeting scheduling validation
│   ├── screeningQuestionSchemas.py # Screening validation
│   ├── teamSchemas.py         # Team member validation
│   ├── userSchemas.py         # User registration and profile validation
│   ├── noticeSchemas.py       # Notice management validation
│   └── chatbotSchemas.py      # Chatbot conversation and response validation
│
└── services/                  # Utility and helper services
    ├── authServices.py        # JWT token generation and validation utilities
    └── cookieServices.py      # Dual-token cookie management (httponly + accessible)
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
2. **Login Process**: Dual JWT token generation (httponly=true + httponly=false cookies)
3. **Request Authentication**: Middleware validates cookies on protected routes
4. **Role Authorization**: Admin/user role separation for restricted endpoints
5. **Password Recovery**: Secure token-based password reset system

### Chatbot Conversation Flows

1. **Property Search Flow**: 
   - 7 comprehensive questions (type, city, budget, bedrooms, pets, move-in, amenities)
   - Email collection for admin notifications
   - Complete preferences summary and team contact commitment

2. **Rent Inquiry Flow**: Dynamic property-specific questions with search capabilities

3. **Schedule Visit Flow**: Appointment booking with automated email confirmations

4. **Bug Report Flow**: Issue categorization with detailed problem tracking

5. **Feedback Flow**: Multi-category service quality assessment

### Media Processing Pipeline

1. **Large File Upload**: Custom CORS middleware with 5-minute timeout for multiple file uploads
2. **Image Processing**: Pillow-based compression and optimization
3. **Base64 Conversion**: Secure storage format for database persistence
4. **Multiple Media Support**: Support for multiple images per property
5. **Integration**: Seamless media attachment during property creation/updates

### Email Notification System

1. **Chatbot Integration**: Automated admin notifications for property search completions
2. **Meeting Automation**: Confirmation and reminder emails for scheduled visits
3. **Property Recommendations**: Personalized recommendation emails
4. **Admin Alerts**: Comprehensive HTML email templates with structured data tables

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
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASS=your_database_password
DB_HOST=your_database_host
DB_PORT=6543

# JWT Authentication (Dual Token System)
JWT_SECRET=your_secure_jwt_secret_key_minimum_32_characters

# SMTP Email Service (For Admin Notifications)
ADMIN_EMAIL=your_admin_email@domain.com
ADMIN_PASSWORD=your_admin_email_password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_smtp_username
EMAIL_PASS=your_smtp_password
EMAIL_FROM=your_from_email@domain.com

# Application Configuration
FRONTEND_URL=http://localhost:3000
PORT=8002
```

4. **Database Setup**
Ensure PostgreSQL is running.


5. **Start Development Server**
```bash
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

## API Documentation

### Interactive Documentation
- **Swagger UI**: http://127.0.0.1:8002/docs
- **ReDoc**: http://127.0.0.1:8002/redoc

### Core Endpoints

#### Authentication System
```
POST /api/auth/signup                 - User registration with email verification
POST /api/auth/login                  - User authentication with dual-token cookie session
POST /api/auth/logout                 - Session termination and cookie cleanup
POST /api/auth/forgot-password        - Password reset request
POST /api/auth/reset-password/{token} - Password reset confirmation
GET  /api/auth/verify-email/{token}   - Email address verification
POST /api/auth/resend-verification    - Resend verification email
```
#### Property Management
```
# Admin Routes (Authentication + Admin Role Required)
POST   /api/admin/properties/add            - Create property with optional media files
PUT    /api/admin/properties/{property_id}  - Update property with optional media  
DELETE /api/admin/properties/{property_id}  - Delete property and associated media
GET    /api/admin/properties                - Get all properties (admin detailed view)
GET    /api/admin/properties/{property_id}  - Get property by ID (admin view)
GET    /api/admin/properties/stats          - Get property statistics (total, available, recent)
GET    /api/admin/properties/recent         - Get recent properties with media
GET    /api/admin/properties/cover-images   - Get all property cover images
GET    /api/admin/properties/{id}/cover-image - Get specific property cover image

# Public Routes (Authentication Required)
GET /api/properties                    - Get public property listings (filtered)
GET /api/properties/{property_id}      - Get public property details
```

#### Intelligent Chatbot System
```
# Public Chatbot Routes (No Authentication Required)
POST /api/chatbot/start               - Start new conversation or resume existing
POST /api/chatbot/respond             - Send user response and get next question
POST /api/chatbot/satisfaction        - Submit satisfaction rating
GET  /api/chatbot/conversation/{id}   - Get conversation history

# Admin Chatbot Management (Admin Only)
GET    /api/admin/chatbot/conversations     - Get all conversations with analytics
GET    /api/admin/chatbot/messages          - Get all messages with filtering
DELETE /api/admin/chatbot/conversation/{id} - Delete conversation
PUT    /api/admin/chatbot/conversation/{id} - Update conversation status
GET    /api/admin/chatbot/analytics         - Get chatbot usage analytics

# Chatbot Features:
# - Property Search Flow (7 questions + email collection)
# - Rent Inquiry Flow (dynamic property-based questions)
# - Schedule Visit Flow (appointment booking with email notifications)
# - Bug Report Flow (issue categorization and tracking)
# - Feedback Flow (service quality assessment)
```

#### Property Recommendations
```
# Public Routes (Authentication Required)
GET  /api/recommendations               - Get personalized property recommendations
POST /api/recommendations/create       - Create new recommendation request

# Admin Routes (Admin Only)
GET    /api/admin/recommendations       - Get all recommendations with user data
PUT    /api/admin/recommendations/{id}  - Update recommendation status
DELETE /api/admin/recommendations/{id}  - Delete recommendation
```

#### Meeting Scheduling
```
# Public Routes (Authentication Required)
POST /api/meetings/schedule           - Schedule property visit
GET  /api/meetings/user               - Get user's scheduled meetings

# Admin Routes (Admin Only)
GET    /api/admin/meetings            - Get all scheduled meetings
PUT    /api/admin/meetings/{id}       - Update meeting status/details
DELETE /api/admin/meetings/{id}       - Cancel meeting
POST   /api/admin/meetings/{id}/confirm - Confirm meeting with email notification
```

#### Notice Management
```
# Public Routes (No Authentication Required)
GET    /api/notices/active            - Get active notices only with filtering and pagination

# Admin Routes (Authentication + Admin Role Required)
GET    /api/notices                   - Get all notices (Admin Only)
POST   /api/notices                   - Create new notice with optional file upload (Admin Only)
PUT    /api/notices/{id}              - Update notice with optional file upload (Admin Only)
DELETE /api/notices/{id}              - Delete notice (Admin Only)
GET    /api/notices/{id}              - Get notice by ID (Admin Only)
```

#### User Management
```
GET  /api/user/profile    - Get user profile (Authentication Required)
PUT  /api/user/profile    - Update user profile (Authentication Required)
```

#### Team Management
```
# Public Routes (No Authentication Required)
GET    /api/team          - Get all team members with filtering and pagination
GET    /api/team/{id}     - Get team member by ID

# Admin Routes (Authentication + Admin Role Required)
POST   /api/team          - Add team member with optional photo upload (Admin Only)
PUT    /api/team/{id}     - Update team member with optional photo upload (Admin Only)
DELETE /api/team/{id}     - Remove team member (Admin Only)
```

#### Contact Management
```
POST /api/public/contact  - Submit contact form (Public)
GET  /api/admin/contacts  - Get contact submissions (Admin Only)
PUT  /api/admin/contacts/{id} - Update contact status (Admin Only)
DELETE /api/admin/contacts/{id} - Delete contact submission (Admin Only)
```

#### Screening Questions
```
GET    /api/screening     - Get screening questions (Public)
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

## Key Features

###  Property Management
- **Comprehensive CRUD**: Full property lifecycle managementment with 20+ attributes
- **Advanced Media Handling**: Multiple image uploads with base64 storage and optimization
- **Property Statistics**: Real-time analytics including total properties, availability rates, and recent listings
- **Occupancy Tracking**: Automated status management and availability monitoring

### Intelligent Chatbot System
- **Multi-Flow Conversations**: 5 distinct conversation flows for different user needs
- **Property Search**: 7-step guided search with email collection and admin notifications
- **Dynamic Responses**: Context-aware questioning based on user selections
- **Session Management**: Persistent conversations with message history
- **Admin Analytics**: Comprehensive conversation tracking and user interaction analytics

###  Email Integration
- **Automated Notifications**: Admin alerts for chatbot completions, meeting bookings, and recommendations
- **HTML Templates**: Professional email formatting with structured data tables
- **SMTP Configuration**: Flexible email service setup with Gmail integration
- **Notification Categories**: Separate email services for different business functions

###  Advanced Authentication
- **Dual Token System**: Both HTTP-only and accessible JWT tokens for different use cases
- **Role-Based Access**: Admin/user role separation with middleware enforcement
- **Secure Sessions**: Session middleware with cookie-based authentication
- **Password Security**: bcrypt hashing with token-based recovery

###  Analytics & Recommendations
- **Property Statistics**: Comprehensive property analytics dashboard
- **AI Recommendations**: Intelligent property suggestion system
- **User Behavior Tracking**: Chatbot interaction analytics and user preference analysis
- **Performance Metrics**: Response time monitoring and system health tracking

###  Meeting & Scheduling
- **Automated Booking**: Property visit scheduling with email confirmations
- **Calendar Integration**: Meeting management with status tracking
- **Notification System**: Automated reminders and confirmations
- **Admin Oversight**: Complete meeting lifecycle management

## Development Guidelines

### Code Organization
- Follow Python PEP 8 style guidelines with comprehensive type hints
- Implement consistent error handling patterns across all controllers
- Maintain clear separation between routes, controllers, models, and services
- Use async/await patterns throughout for optimal performance

### Database Operations
- Use Tortoise ORM async/await patterns for all database interactions
- Implement proper transaction handling for complex operations
- Follow database migration best practices with version control
- Maintain referential integrity with foreign key constraints and indexes

### API Design
- RESTful endpoint design with consistent naming conventions
- Comprehensive input validation using Pydantic schemas
- Proper HTTP status codes and error responses
- Role-based access control with middleware enforcement

### Testing & Quality
- Comprehensive error handling with informative error messages
- Input validation at multiple levels (schema, controller, model)
- Logging and monitoring for production deployments
- Performance optimization for large file uploads and database queries

## Deployment Considerations

### Production Setup
- Configure proper environment variables for production
- Set up database connection pooling for high traffic
- Implement proper logging and monitoring
- Configure reverse proxy (nginx) for static file serving
- Set up SSL certificates for HTTPS

### Performance Optimization
- Database indexing for frequently queried fields
- Caching strategies for static data
- Connection pooling for database and external services
- Async processing for email notifications and heavy operations

## License

This project is licensed under the MIT License. See LICENSE file for details.