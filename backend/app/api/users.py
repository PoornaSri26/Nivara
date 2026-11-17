"""
Users API: User profile management, preferences, and onboarding consent.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.database import get_db
from app.models.schema import User
from app.models.pydantic_models import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Creates a new user profile with consent flag and defaults."""
    user = User(
        display_name=data.display_name,
        email=data.email,
        region=data.region,
        preferences={
            "default_mode": "GUIDED_CBT",
            "homework_reminders": True,
            "weekly_report_enabled": True
        }
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserResponse(
        id=user.id,
        display_name=user.display_name,
        email=user.email,
        privacy_mode_enabled=user.privacy_mode_enabled,
        region=user.region
    )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=user.id,
        display_name=user.display_name,
        email=user.email,
        privacy_mode_enabled=user.privacy_mode_enabled,
        region=user.region
    )

@router.patch("/{user_id}/preferences")
async def update_preferences(user_id: str, preferences: dict, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.preferences = {**(user.preferences or {}), **preferences}
    await db.commit()
    return {"success": True, "preferences": user.preferences}

