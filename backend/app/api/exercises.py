"""
Exercises & Activity Endpoints: Thought Records, Behavioral Activation, Grounding & Mood Logging.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from datetime import datetime

from app.models.database import get_db
from app.models.schema import ThoughtRecord, BehavioralActivationTask, MoodLog
from app.models.pydantic_models import (
    ThoughtRecordCreate, BehavioralTaskCreate, MoodLogCreate
)
from app.exercises.grounding import get_grounding_exercise
from app.exercises.behavioral_activation import generate_micro_action

router = APIRouter(prefix="/exercises", tags=["Exercises & Logging"])

@router.post("/mood")
async def log_mood(data: MoodLogCreate, db: AsyncSession = Depends(get_db)):
    log = MoodLog(
        user_id=data.user_id,
        session_id=data.session_id,
        mood_score=data.mood_score,
        coping_confidence=data.coping_confidence,
        primary_emotion=data.primary_emotion,
        emotion_tags=data.emotion_tags,
        trigger_note=data.trigger_note
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return {"success": True, "id": log.id, "mood_score": log.mood_score}

@router.post("/thought-record")
async def save_thought_record(data: ThoughtRecordCreate, db: AsyncSession = Depends(get_db)):
    record = ThoughtRecord(
        user_id=data.user_id,
        session_id=data.session_id,
        situation=data.situation,
        automatic_thought=data.automatic_thought,
        emotions=data.emotions,
        cognitive_distortions=data.cognitive_distortions,
        evidence_for=data.evidence_for,
        evidence_against=data.evidence_against,
        alternative_thought=data.alternative_thought,
        outcome_emotion_intensity=data.outcome_emotion_intensity
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return {"success": True, "id": record.id}

@router.get("/thought-records/{user_id}")
async def get_user_thought_records(user_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ThoughtRecord).where(ThoughtRecord.user_id == user_id).order_by(ThoughtRecord.created_at.desc()))
    records = res.scalars().all()
    return records

@router.post("/behavioral-task")
async def create_behavioral_task(data: BehavioralTaskCreate, db: AsyncSession = Depends(get_db)):
    task = BehavioralActivationTask(
        user_id=data.user_id,
        title=data.title,
        activity_type=data.activity_type,
        difficulty_rating=data.difficulty_rating,
        pleasure_rating=data.pleasure_rating,
        status="PENDING",
        notes=data.notes
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return {"success": True, "id": task.id}

@router.post("/behavioral-task/{task_id}/complete")
async def complete_behavioral_task(task_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(BehavioralActivationTask).where(BehavioralActivationTask.id == task_id))
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = "COMPLETED"
    await db.commit()
    return {"success": True, "status": "COMPLETED"}

@router.get("/grounding/{technique}")
async def fetch_grounding_technique(technique: str):
    return get_grounding_exercise(technique)

