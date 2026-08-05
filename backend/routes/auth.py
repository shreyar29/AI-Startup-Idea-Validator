from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import bcrypt
import jwt
from datetime import datetime, timedelta
from core.config import settings
from db import get_db
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

SECRET_KEY = settings.app.SECRET_KEY
ALGORITHM = "HS256"

class UserCredentials(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/signup", response_model=Token)
def signup(user: UserCredentials):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (user.username,))
        if cursor.fetchone():
            logger.warning(f"Signup failed: Username '{user.username}' already registered")
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
        
        logger.info(f"New user registered: {user.username} (ID: {user_id})")
        access_token = create_access_token(data={"sub": user.username, "user_id": user_id})
        return {"access_token": access_token, "token_type": "bearer", "user_id": user_id, "username": user.username}

@router.post("/login", response_model=Token)
def login(user: UserCredentials):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (user.username,))
        row = cursor.fetchone()
        
        if not row:
            logger.warning(f"Login failed: User '{user.username}' not found")
            raise HTTPException(status_code=401, detail="Invalid username or password")
            
        stored_hash = row['password_hash'].encode('utf-8')
        if not bcrypt.checkpw(user.password.encode('utf-8'), stored_hash):
            logger.warning(f"Login failed: Invalid password for '{user.username}'")
            raise HTTPException(status_code=401, detail="Invalid username or password")
            
        logger.info(f"User logged in successfully: {user.username}")
        access_token = create_access_token(data={"sub": row['username'], "user_id": row['id']})
        return {"access_token": access_token, "token_type": "bearer", "user_id": row['id'], "username": row['username']}
