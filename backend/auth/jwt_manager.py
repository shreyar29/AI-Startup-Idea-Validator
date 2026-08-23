import jwt
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from core.config import settings
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.logger import get_logger

logger = get_logger(__name__)

security = HTTPBearer(auto_error=False)

class JWTManager:
    @staticmethod
    def _build_payload(data: dict, expires_delta: timedelta, token_type: str = "access") -> dict:
        to_encode = data.copy()
        now = datetime.now(timezone.utc)
        to_encode.update({
            "exp": now + expires_delta,
            "iat": now,
            "nbf": now,
            "jti": str(uuid.uuid4()),
            "type": token_type
        })
        if settings.app.JWT_ISSUER:
            to_encode["iss"] = settings.app.JWT_ISSUER
        if settings.app.JWT_AUDIENCE:
            to_encode["aud"] = settings.app.JWT_AUDIENCE
        return to_encode

    @staticmethod
    def create_access_token(data: dict) -> str:
        payload = JWTManager._build_payload(data, timedelta(minutes=settings.app.ACCESS_TOKEN_EXPIRE_MINUTES), "access")
        return jwt.encode(payload, settings.app.SECRET_KEY, algorithm=settings.app.JWT_ALGORITHM)

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        payload = JWTManager._build_payload(data, timedelta(days=settings.app.REFRESH_TOKEN_EXPIRE_DAYS), "refresh")
        return jwt.encode(payload, settings.app.SECRET_KEY, algorithm=settings.app.JWT_ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            kwargs = {"algorithms": [settings.app.JWT_ALGORITHM]}
            if settings.app.JWT_AUDIENCE:
                kwargs["audience"] = settings.app.JWT_AUDIENCE
            if settings.app.JWT_ISSUER:
                kwargs["issuer"] = settings.app.JWT_ISSUER
                
            payload = jwt.decode(token, settings.app.SECRET_KEY, **kwargs)
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token validation failed: Token has expired")
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.PyJWTError:
            logger.warning("Token validation failed: Invalid token structure or signature")
            raise HTTPException(status_code=401, detail="Could not validate credentials")

    @staticmethod
    def validate_refresh_token(token: str) -> Dict[str, Any]:
        payload = JWTManager.decode_token(token)
        if payload is None or payload.get("type") != "refresh":
            logger.warning("Token validation failed: Expected refresh token but got other/none")
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        return payload

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> Dict[str, Any]:
    if not credentials:
        return {"user_id": "anonymous", "role": "user"}
    token = credentials.credentials
    try:
        payload = JWTManager.decode_token(token)
        if payload is None or "sub" not in payload:
            return {"user_id": "anonymous", "role": "user"}
        return {"user_id": payload["sub"], "email": payload.get("email"), "role": payload.get("role", "user")}
    except:
        return {"user_id": "anonymous", "role": "user"}

class RequireRole:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: Dict[str, Any] = Depends(get_current_user)):
        if current_user.get("role") not in self.allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
