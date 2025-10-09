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
from routes.applicationRoute import router as application_router
from routes.tidycalProxyRoute import router as tidycal_proxy_router
from routes.maintenanceRequestRoute import router as maintenance_request_router


from dbConnection.dbConfig import init_db  

load_dotenv()

PORT = int(os.getenv("PORT", 8001))
FRONTEND_URL = os.getenv("FRONTEND_URL")

app = FastAPI(
    title="Property Web Backend API",
    description="A comprehensive FastAPI backend for property management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse
import asyncio

class LargeRequestCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        try:
            response = await asyncio.wait_for(call_next(request), timeout=300.0) 
        except asyncio.TimeoutError:
            response = StarletteResponse(
                content='{"detail": "Request timeout - file too large or processing took too long"}',
                status_code=408,
                headers={"content-type": "application/json"}
            )
        except Exception as e:
            response = StarletteResponse(
                content=f'{{"detail": "Server error: {str(e)}"}}',
                status_code=500,
                headers={"content-type": "application/json"}
            )
        origin = request.headers.get("origin")
        if origin in ["https://satishdev-staging-link.pixbit.me", "http://localhost:5173"]:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Expose-Headers"] = "Set-Cookie, Content-Type"
        
        return response

app.add_middleware(LargeRequestCORSMiddleware)

# CORS
allowed_origins = [
    FRONTEND_URL,
    "https://satishdev-staging-link.pixbit.me",  # Frontend staging domain
    "http://localhost:5173",  # Local development
]


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
# Team routes - public GET, admin management for CUD operations
app.include_router(
    team_router,
    prefix="/api",
    tags=["Team"],
    # No dependencies here - route-level auth will be handled individually
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
app.include_router(meeting_router, prefix="/api", tags=["Schedule Meetings"])  


app.include_router(
    notice_router,
    prefix="/api",
    tags=["Notices"],

)

app.include_router(recommendation_router, prefix="/api", tags=["Property Recommendations"])  # Mixed access levels

app.include_router(chatbot_router, prefix="/api", tags=["Chatbot"])  # 
app.include_router(application_router, prefix="/api", tags=["Rental Applications"])  

# TidyCal proxy route - simple pass-through to TidyCal API
app.include_router(tidycal_proxy_router, prefix="/api", tags=["TidyCal Proxy"])



# Maintenance request routes - admin only 
app.include_router(
    maintenance_request_router,
    prefix="/api/admin",
    tags=["Maintenance Requests"],
)


init_db(app)

@app.on_event("startup")
async def startup_event():
    print(f"Server running on port {PORT}")


from fastapi import Form, File, UploadFile
from typing import Optional, List


@app.options("/{path:path}")
async def options_handler(path: str, response: Response):
    response.headers["Access-Control-Allow-Origin"] = "https://satishdev-staging-link.pixbit.me"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return {"message": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=PORT, 
        reload=True,
        timeout_keep_alive=60,  
        timeout_graceful_shutdown=60,
        limit_concurrency=1000,
        limit_max_requests=1000,
        access_log=True,
        use_colors=True
    )
