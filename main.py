import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED

from dbConnection.dbSync import init_db
from middleware.authMiddleware import check_for_authentication_cookie
from middleware.roleMiddleware import authorize_roles
from routes.authRoute.userAuthRoute import router as auth_router
from routes.profileRoute.userProfileRoute import router as user_profile_router

load_dotenv()

PORT = int(os.getenv("PORT", 8001))
FRONTEND_URL = os.getenv("FRONTEND_URL")

app = FastAPI()

allowed_origins = [FRONTEND_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
)


app.add_middleware(SessionMiddleware, secret_key=os.getenv("JWT_SECRET", "supersecret"))

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


@app.on_event("startup")
async def startup_event():
    await init_db()
    print(f" Server running on port {PORT}")

