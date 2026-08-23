import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from auth.jwt_manager import JWTManager

# Using Redis if available, else memory fallback for dev
REDIS_URL = os.environ.get("REDIS_URL", "memory://")

def get_user_tier(request: Request) -> str:
    """
    Determines the rate limit bucket based on user tier.
    Parses JWT if present.
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = JWTManager.decode_token(token)
            if payload:
                # Return the tier. Note: normally tier is in JWT or fetched from DB
                return payload.get("tier", "free")
        except Exception:
            pass
    return "anonymous"

def dynamic_rate_limit(request: Request) -> str:
    """
    Returns the dynamic rate limit string based on the user's tier.
    """
    tier = get_user_tier(request)
    
    limits = {
        "anonymous": "3/day",
        "free": "5/day",
        "premium": "50/day",
        "enterprise": "1000/day" # "Unlimited"
    }
    
    return limits.get(tier, "3/day")

# Global slowapi limiter using Redis backend and dynamic rate limit evaluation
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=REDIS_URL if REDIS_URL != "memory://" else None
)
