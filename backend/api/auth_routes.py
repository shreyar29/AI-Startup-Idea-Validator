from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, Field, EmailStr, SecretStr
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from auth.auth_service import AuthService
from typing import Dict, Any
from core.rate_limiter import limiter
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

class UserCredentials(BaseModel):
    email: EmailStr = Field(..., max_length=100, description="The user's registered email address.")
    password: SecretStr = Field(..., min_length=8, max_length=128, description="The user's secure password.")

class UserResponse(BaseModel):
    id: int = Field(..., description="Unique user identifier.")
    email: EmailStr = Field(..., description="The user's email address.")
    tier: str = Field(..., description="The user's subscription tier.")

class AuthResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token for API authentication.")
    refresh_token: str = Field(..., description="JWT refresh token to obtain new access tokens.")
    token_type: str = Field(..., description="Token type, usually 'bearer'.")
    user: UserResponse = Field(..., description="User profile details.")

COMMON_RESPONSES = {
    status.HTTP_400_BAD_REQUEST: {"description": "Bad Request (e.g., email already registered or invalid inputs)"},
    status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized (e.g., incorrect password or expired token)"},
    status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Too Many Requests (Rate limit exceeded)"},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"},
}

@router.post(
    "/register",
    summary="Register a new user",
    description="Creates a new user account, hashes the password securely, and returns authentication tokens.",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses=COMMON_RESPONSES
)
@limiter.limit("3/minute")
async def register(request: Request, credentials: UserCredentials, db: AsyncSession = Depends(get_db)):
    req_id = request.headers.get("x-correlation-id") or request.headers.get("x-request-id") or "unknown"
    logger.info(f"[{req_id}] Auth Route: Attempting to register user: {credentials.email}")
    return await AuthService.register_user(db, credentials.email, credentials.password.get_secret_value())

@router.post(
    "/login",
    summary="Authenticate a user",
    description="Validates user credentials and returns JWT access and refresh tokens.",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    responses=COMMON_RESPONSES
)
@limiter.limit("5/minute")
async def login(request: Request, credentials: UserCredentials, db: AsyncSession = Depends(get_db)):
    req_id = request.headers.get("x-correlation-id") or request.headers.get("x-request-id") or "unknown"
    logger.info(f"[{req_id}] Auth Route: Attempting to login user: {credentials.email}")
    return await AuthService.login_user(db, credentials.email, credentials.password.get_secret_value())
