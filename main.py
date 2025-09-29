import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
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

from dbConnection.dbConfig import init_db  

load_dotenv()

PORT = int(os.getenv("PORT", 8001))
FRONTEND_URL = os.getenv("FRONTEND_URL")

app = FastAPI()

# CORS
allowed_origins = [FRONTEND_URL]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
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
    dependencies=[Depends(authorize_roles(["user", "admin"]))],
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
