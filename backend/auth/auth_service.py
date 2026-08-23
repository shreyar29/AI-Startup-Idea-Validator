from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from database.models import User
from auth.password_utils import hash_password, verify_password
from auth.jwt_manager import JWTManager
from typing import Dict, Any

from utils.logger import get_logger

logger = get_logger(__name__)

class AuthService:
    @staticmethod
    async def register_user(db: AsyncSession, email: str, password: str) -> Dict[str, Any]:
        try:
            stmt = select(User).where(User.email == email)
            result = await db.execute(stmt)
            if result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Registration failed. Please verify your details.")
                
            hashed_password = hash_password(password)
            new_user = User(email=email, hashed_password=hashed_password)
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            access_token = JWTManager.create_access_token({"sub": new_user.id, "email": new_user.email})
            refresh_token = JWTManager.create_refresh_token({"sub": new_user.id, "email": new_user.email})
            
            logger.info(f"Successful registration for email: {email}")
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": {"id": new_user.id, "email": new_user.email, "tier": new_user.tier}
            }
        except HTTPException:
            await db.rollback()
            raise
        except IntegrityError:
            await db.rollback()
            logger.warning(f"Concurrent registration collision for email: {email}")
            raise HTTPException(status_code=400, detail="Registration failed. Please verify your details.")
        except Exception as e:
            await db.rollback()
            logger.exception("Database error during user registration")
            raise HTTPException(status_code=500, detail="An error occurred during registration.")

    @staticmethod
    async def login_user(db: AsyncSession, email: str, password: str) -> Dict[str, Any]:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(password, user.hashed_password):
            logger.warning(f"Failed login attempt for email: {email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
            
        access_token = JWTManager.create_access_token({"sub": user.id, "email": user.email})
        refresh_token = JWTManager.create_refresh_token({"sub": user.id, "email": user.email})
        
        logger.info(f"Successful login for email: {email}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {"id": user.id, "email": user.email, "tier": user.tier}
        }
