from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from database.db import get_db
from middleware.auth_middleware import authenticate_user, create_access_token, get_password_hash
from schemas.user import UserCreate, UserResponse, Token
from models.user import User
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password
        )
        
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        except Exception as e:
            db.rollback()
            logger.error(f"Database error during user registration: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register user"
            )
        
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during user registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        try:
            access_token = create_access_token(
                data={"sub": user.email}, expires_delta=access_token_expires
            )
        except Exception as e:
            logger.error(f"Error creating access token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generating authentication token"
            )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        # Re-raise HTTP exceptions as they already have appropriate status codes
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )