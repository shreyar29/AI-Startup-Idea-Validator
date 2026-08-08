from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from core.config import settings
from db import get_db
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

SECRET_KEY = settings.app.SECRET_KEY
ALGORITHM = "HS256"
# Assumption: ACCESS_TOKEN_EXPIRE_DAYS is not present in core.config.settings,
# so it remains a module-level constant here to avoid inventing new config mechanics.
ACCESS_TOKEN_EXPIRE_DAYS = 7

class UserCredentials(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, strip_whitespace=True)
    password: str = Field(..., min_length=8, max_length=128)

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str

def create_access_token(data: dict):
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"iat": now, "exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/signup", response_model=Token)
def signup(user: UserCredentials, request: Request):
    request_id = getattr(request.state, "request_id", "unknown")
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (user.username,))
            if cursor.fetchone():
                logger.warning(f"[{request_id}] Signup failed: Username already registered")
                raise HTTPException(status_code=400, detail="Username already registered")
            
            # Hash password
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(user.password.encode('utf-8'), salt)
            
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (user.username, hashed.decode('utf-8'))
            )
            conn.commit()
            user_id = cursor.lastrowid
            
            logger.info(f"[{request_id}] New user registered (ID: {user_id})")
            access_token = create_access_token(data={"sub": user.username, "user_id": user_id})
            return {"access_token": access_token, "token_type": "bearer", "user_id": user_id, "username": user.username}
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"[{request_id}] Internal error during signup")
        raise HTTPException(status_code=500, detail="An internal server error occurred")

@router.post("/login", response_model=Token)
def login(user: UserCredentials, request: Request):
    request_id = getattr(request.state, "request_id", "unknown")
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (user.username,))
            row = cursor.fetchone()
            
            if not row:
                logger.warning(f"[{request_id}] Login failed: Invalid credentials")
                raise HTTPException(status_code=401, detail="Invalid username or password")
                
            stored_hash = row['password_hash'].encode('utf-8')
            if not bcrypt.checkpw(user.password.encode('utf-8'), stored_hash):
                logger.warning(f"[{request_id}] Login failed: Invalid credentials")
                raise HTTPException(status_code=401, detail="Invalid username or password")
                
            logger.info(f"[{request_id}] User logged in successfully (ID: {row['id']})")
            access_token = create_access_token(data={"sub": row['username'], "user_id": row['id']})
            return {"access_token": access_token, "token_type": "bearer", "user_id": row['id'], "username": row['username']}
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"[{request_id}] Internal error during login")
        raise HTTPException(status_code=500, detail="An internal server error occurred")
