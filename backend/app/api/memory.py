"""
True Memory API: User controls, audits, confirmations, and privacy mode toggling.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.database import get_db
from app.models.schema import UserMemory, User
from app.models.pydantic_models import MemoryResponse, MemoryActionRequest
from app.memory.true_memory import TrueMemoryService

router = APIRouter(prefix="/memory", tags=["True Memory"])

@router.get("/list/{user_id}", response_model=List[MemoryResponse])
async def list_memories(user_id: str, status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    memories = await TrueMemoryService.get_user_memories(db, user_id, status)
    return [
        MemoryResponse(
            id=m.id,
            category=m.category,
            content=m.content,
            confidence_score=m.confidence_score,
            source_type=m.source_type,
            status=m.status,
            created_at=m.created_at.isoformat() if m.created_at else ""
        ) for m in memories
    ]

@router.post("/action/{memory_id}")
async def handle_memory_action(
    memory_id: str, 
    request: MemoryActionRequest, 
    db: AsyncSession = Depends(get_db)
):
    action = request.action.upper()
    if action == "DELETE":
        success = await TrueMemoryService.delete_memory(db, memory_id)
        if not success:
            raise HTTPException(status_code=404, detail="Memory not found")
        return {"success": True, "action": "DELETED"}

    elif action in ["CONFIRM", "REJECT", "UPDATE"]:
        target_status = "CONFIRMED" if action in ["CONFIRM", "UPDATE"] else "REJECTED"
        updated = await TrueMemoryService.update_memory_status(
            db, 
            memory_id, 
            target_status, 
            updated_content=request.updated_content
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Memory not found")
        return {"success": True, "status": updated.status, "content": updated.content}

    raise HTTPException(status_code=400, detail="Invalid memory action")

@router.post("/privacy-mode/{user_id}")
async def toggle_privacy_mode(user_id: str, enable: bool, db: AsyncSession = Depends(get_db)):
    user_res = await db.execute(select(User).where(User.id == user_id))
    user = user_res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.privacy_mode_enabled = enable
    await db.commit()
    return {
        "success": True, 
        "privacy_mode_enabled": user.privacy_mode_enabled,
        "message": "Privacy mode active: Nivara will neither read nor save longitudinal memories." if enable else "Privacy mode disabled."
    }

