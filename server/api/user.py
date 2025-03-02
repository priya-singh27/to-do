from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from models.user import User
from schemas.user import UserResponse
from middleware.auth_middleware import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == current_user["id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user