import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED


from authMiddleware.authMiddleware import check_for_authentication_cookie
from authMiddleware.roleMiddleware import authorize_roles
from routes.authRoute import router as auth_router
from routes.profileRoute import router as user_profile_router
from routes.propertyRoute import router as property_router
from routes.teamRoute import router as team_router
from routes.contactRoute import router as contact_router

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

# Auth middleware
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/user"):
        token = request.cookies.get("token")
        if not token or not check_for_authentication_cookie(token):
            return JSONResponse(
                status_code=HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required"},
            )
    response = await call_next(request)
    return response

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

init_db(app)

@app.on_event("startup")
async def startup_event():
    print(f"Server running on port {PORT}")
@app.get("/")
async def root():
    return {"message": "API is running"}
