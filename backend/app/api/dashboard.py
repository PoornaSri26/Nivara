"""
Emotional Intelligence Dashboard API: Aggregates longitudinal mood trends,
cognitive distortion distributions, triggers, and coping confidence.
Adheres to clinical guidance: observations are correlations, not clinical conclusions.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from typing import Dict, Any, List
from collections import Counter

from app.models.database import get_db
from app.models.schema import MoodLog, ThoughtRecord, BehavioralActivationTask, UserMemory
from app.services.weekly_report import WeeklyReportService

router = APIRouter(prefix="/dashboard", tags=["EI Dashboard"])

@router.get("/metrics/{user_id}")
async def get_dashboard_metrics(user_id: str, days: int = 30, db: AsyncSession = Depends(get_db)):
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # 1. Longitudinal Mood Logs
    mood_res = await db.execute(
        select(MoodLog)
        .where(MoodLog.user_id == user_id, MoodLog.created_at >= cutoff_date)
        .order_by(MoodLog.created_at.asc())
    )
    mood_logs = mood_res.scalars().all()

    mood_timeline = []
    coping_timeline = []
    emotion_counter = Counter()
    trigger_counter = Counter()

    for m in mood_logs:
        date_str = m.created_at.strftime("%Y-%m-%d")
        mood_timeline.append({
            "date": date_str,
            "score": m.mood_score,
            "primary_emotion": m.primary_emotion
        })
        if m.coping_confidence:
            coping_timeline.append({
                "date": date_str,
                "confidence": m.coping_confidence
            })
        emotion_counter[m.primary_emotion] += 1
        if m.trigger_note:
            trigger_counter[m.trigger_note] += 1

    # 2. Cognitive Distortion Distributions from Thought Records
    tr_res = await db.execute(
        select(ThoughtRecord)
        .where(ThoughtRecord.user_id == user_id, ThoughtRecord.created_at >= cutoff_date)
    )
    thought_records = tr_res.scalars().all()
    distortion_counter = Counter()
    for tr in thought_records:
        if tr.cognitive_distortions:
            for dist in tr.cognitive_distortions:
                distortion_counter[dist] += 1

    # 3. Behavioral Activation Completion Rate
    tasks_res = await db.execute(
        select(BehavioralActivationTask)
        .where(BehavioralActivationTask.user_id == user_id, BehavioralActivationTask.created_at >= cutoff_date)
    )
    tasks = tasks_res.scalars().all()
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == "COMPLETED")
    completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0.0

    # 4. Summary Averages
    avg_mood = round(sum(m.mood_score for m in mood_logs) / len(mood_logs), 1) if mood_logs else None
    avg_coping = round(sum(m.coping_confidence for m in mood_logs if m.coping_confidence) / len(mood_logs), 1) if mood_logs else None

    return {
        "timeframe_days": days,
        "summary": {
            "average_mood_score": avg_mood,
            "average_coping_confidence": avg_coping,
            "total_sessions_logged": len(mood_logs),
            "thought_records_completed": len(thought_records),
            "homework_completion_rate_percent": completion_rate
        },
        "mood_timeline": mood_timeline,
        "coping_confidence_timeline": coping_timeline,
        "frequently_identified_distortions": [
            {"name": k, "count": v} for k, v in distortion_counter.most_common(5)
        ],
        "top_reported_triggers": [
            {"trigger": k, "count": v} for k, v in trigger_counter.most_common(5)
        ],
        "dominant_emotions": [
            {"emotion": k, "count": v} for k, v in emotion_counter.most_common(5)
        ],
        "clinical_disclaimer": (
            "These metrics present user-reported observations and correlations over time. "
            "They are meant to support personal self-reflection and do not represent a psychiatric diagnosis, "
            "severity index, or clinical proof of recovery."
        )
    }

@router.get("/weekly-report/{user_id}")
async def get_weekly_insight_report(user_id: str, db: AsyncSession = Depends(get_db)):
    """Generates the clinical Weekly Reflection & Insight Report."""
    return await WeeklyReportService.generate_weekly_digest(user_id, db)

