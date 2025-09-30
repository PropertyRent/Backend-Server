import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from authMiddleware.roleMiddleware import authorize_roles
from routes.authRoute import router as auth_router
from routes.profileRoute import router as user_profile_router
from routes.propertyRoute import router as property_router
from routes.teamRoute import router as team_router
from routes.contactRoute import router as contact_router
from routes.screeningQuestionRoute import router as screening_router
from routes.scheduleMeetingRoute import router as meeting_router
from routes.noticeRoute import router as notice_router
from routes.propertyRecommendationRoute import router as recommendation_router
from routes.chatbotRoute import router as chatbot_router

from dbConnection.dbConfig import init_db  

load_dotenv()

PORT = int(os.getenv("PORT", 8001))
FRONTEND_URL = os.getenv("FRONTEND_URL")

app = FastAPI()

# CORS
allowed_origins = [
    FRONTEND_URL,
    "https://satishdev-staging-link.pixbit.me",  # Frontend staging domain
    "http://localhost:5173",  # Local developmen 
]

# Remove None values if FRONTEND_URL is not set
allowed_origins = [origin for origin in allowed_origins if origin is not None]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "*",  # Allow all headers for multipart/form-data uploads
    ],
    expose_headers=["Set-Cookie", "Content-Type"],
)

# Session
app.add_middleware(SessionMiddleware, secret_key=os.getenv("JWT_SECRET", "supersecret"))

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Property Web Backend API", "status": "operational"}

# Test endpoint for CORS debugging
@app.post("/api/test-cors")
async def test_cors():
    return {"message": "CORS test successful", "status": "ok"}

# Manual OPTIONS handler for problematic routes
@app.options("/{path:path}")
async def options_handler(path: str, response: Response):
    response.headers["Access-Control-Allow-Origin"] = "https://satishdev-staging-link.pixbit.me"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return {"message": "OK"}

# Routes
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(
    user_profile_router,
    prefix="/api/user",
    tags=["User"],
    dependencies=[Depends(authorize_roles(["user", "admin"]))],
)
app.include_router(
    property_router,
    prefix="/api",
    tags=["Properties"],
)
app.include_router(
    team_router,
    prefix="/api",
    tags=["Team"],
    dependencies=[Depends(authorize_roles(["admin"]))],  # Only admins can manage team
)

# Contact routes - public contact form, admin management
app.include_router(contact_router, prefix="/api/public", tags=["Contact"])  # Public contact form
app.include_router(
    contact_router,
    prefix="/api/admin",
    tags=["Contact Management"],
    dependencies=[Depends(authorize_roles(["admin"]))],  # Admin contact management
)

# Screening routes - public access and admin management
app.include_router(screening_router, prefix="/api", tags=["Screening Questions"])  # Both public and admin routes

# Meeting scheduling routes - public scheduling, authenticated user management, admin approval
app.include_router(meeting_router, prefix="/api", tags=["Schedule Meetings"])  # Mixed access levels

# Notice routes - admin only for CRUD operations
app.include_router(
    notice_router,
    prefix="/api",
    tags=["Notices"],
    dependencies=[Depends(authorize_roles(["admin"]))],  # Only admins can manage notices
)

# Property recommendation routes - mixed access (public recommendations, admin management)
app.include_router(recommendation_router, prefix="/api", tags=["Property Recommendations"])  # Mixed access levels

# Chatbot routes - public chat interface and admin management
app.include_router(chatbot_router, prefix="/api", tags=["Chatbot"])  # Mixed access levels

init_db(app)

@app.on_event("startup")
async def startup_event():
    print(f"Server running on port {PORT}")

@app.get("/")
async def root():
    return {"message": "Backend API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=PORT, reload=True)
