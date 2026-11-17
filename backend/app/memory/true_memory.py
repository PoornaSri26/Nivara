"""
True Memory Service: Data access, lifecycle, and privacy controls.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schema import UserMemory, User
from app.config import settings

class TrueMemoryService:
    @staticmethod
    async def get_user_memories(
        db: AsyncSession, 
        user_id: str, 
        status: Optional[str] = None
    ) -> List[UserMemory]:
        """
        Retrieves user memories. Respects user privacy mode.
        """
        # Check if user has privacy mode on
        user_res = await db.execute(select(User).where(User.id == user_id))
        user = user_res.scalar_one_or_none()
        if user and user.privacy_mode_enabled:
            return []

        query = select(UserMemory).where(UserMemory.user_id == user_id)
        if status:
            query = query.where(UserMemory.status == status)
        
        result = await db.execute(query.order_by(UserMemory.created_at.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def create_proposed_memory(
        db: AsyncSession,
        user_id: str,
        category: str,
        content: str,
        confidence_score: float,
        source_type: str = "INFERRED_PATTERN"
    ) -> UserMemory:
        # Check user privacy mode
        user_res = await db.execute(select(User).where(User.id == user_id))
        user = user_res.scalar_one_or_none()
        if user and user.privacy_mode_enabled:
            return None

        expires_at = datetime.utcnow() + timedelta(days=settings.PROPOSED_MEMORY_EXPIRATION_DAYS)
        memory = UserMemory(
            user_id=user_id,
            category=category,
            content=content,
            confidence_score=confidence_score,
            source_type=source_type,
            status="PROPOSED",
            expires_at=expires_at
        )
        db.add(memory)
        await db.commit()
        await db.refresh(memory)
        return memory

    @staticmethod
    async def update_memory_status(
        db: AsyncSession,
        memory_id: str,
        new_status: str,
        updated_content: Optional[str] = None
    ) -> Optional[UserMemory]:
        res = await db.execute(select(UserMemory).where(UserMemory.id == memory_id))
        memory = res.scalar_one_or_none()
        if not memory:
            return None

        memory.status = new_status
        if updated_content:
            memory.content = updated_content
            memory.confidence_score = 1.0  # User explicitly confirmed/edited
            memory.source_type = "DIRECT_USER_FACT"

        if new_status == "CONFIRMED":
            memory.expires_at = None  # Permanent until deleted by user

        await db.commit()
        await db.refresh(memory)
        return memory

    @staticmethod
    async def delete_memory(db: AsyncSession, memory_id: str) -> bool:
        res = await db.execute(select(UserMemory).where(UserMemory.id == memory_id))
        memory = res.scalar_one_or_none()
        if not memory:
            return False
        await db.delete(memory)
        await db.commit()
        return True

