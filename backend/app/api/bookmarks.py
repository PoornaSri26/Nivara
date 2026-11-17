"""
Bookmarks & Coping Toolbox API.
Allows users to save helpful reflections, balanced thoughts, or grounding
exercises to a personal, searchable coping toolbox.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.models.database import get_db
from app.models.milestones import SessionBookmark

router = APIRouter(prefix="/bookmarks", tags=["Coping Toolbox & Bookmarks"])

class BookmarkCreate(BaseModel):
    user_id: str
    session_id: str | None = None
    label: str
    content: str
    is_in_toolbox: bool = True

class BookmarkResponse(BaseModel):
    id: str
    label: str
    content: str
    is_in_toolbox: bool
    created_at: str

@router.post("/", response_model=BookmarkResponse)
async def save_bookmark(data: BookmarkCreate, db: AsyncSession = Depends(get_db)):
    bm = SessionBookmark(
        user_id=data.user_id,
        session_id=data.session_id,
        label=data.label,
        content=data.content,
        is_in_toolbox=data.is_in_toolbox
    )
    db.add(bm)
    await db.commit()
    await db.refresh(bm)
    return BookmarkResponse(
        id=bm.id,
        label=bm.label,
        content=bm.content,
        is_in_toolbox=bm.is_in_toolbox,
        created_at=bm.created_at.isoformat()
    )

@router.get("/toolbox/{user_id}", response_model=List[BookmarkResponse])
async def get_coping_toolbox(user_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(SessionBookmark)
        .where(SessionBookmark.user_id == user_id, SessionBookmark.is_in_toolbox == True)
        .order_by(SessionBookmark.created_at.desc())
    )
    items = res.scalars().all()
    return [
        BookmarkResponse(
            id=b.id, label=b.label, content=b.content,
            is_in_toolbox=b.is_in_toolbox,
            created_at=b.created_at.isoformat()
        ) for b in items
    ]

@router.delete("/{bookmark_id}")
async def delete_bookmark(bookmark_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(SessionBookmark).where(SessionBookmark.id == bookmark_id))
    bm = res.scalar_one_or_none()
    if not bm:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    await db.delete(bm)
    await db.commit()
    return {"success": True}

