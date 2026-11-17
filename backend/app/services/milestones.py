"""
Milestone Engine — awards badges automatically based on user activity.
Milestone logic is fully transparent to users (no hidden gamification).
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.schema import MoodLog, ThoughtRecord, BehavioralActivationTask
from app.models.milestones import ProgressMilestone

MILESTONE_DEFINITIONS = [
    {
        "id": "first_checkin",
        "title": "First Step 🌱",
        "description": "Logged your very first daily mood check-in.",
        "category": "MOOD_LOG",
        "trigger": "mood_logs >= 1"
    },
    {
        "id": "week_streak",
        "title": "7-Day Reflection Streak 🔥",
        "description": "Checked in every day for 7 consecutive days.",
        "category": "STREAK",
        "trigger": "streak_days >= 7"
    },
    {
        "id": "first_thought_record",
        "title": "Thought Examiner 🔍",
        "description": "Completed your first 7-Column Thought Record.",
        "category": "THOUGHT_RECORD",
        "trigger": "thought_records >= 1"
    },
    {
        "id": "five_thought_records",
        "title": "Pattern Spotter ✨",
        "description": "Completed 5 Thought Records — your brain is building new habits.",
        "category": "THOUGHT_RECORD",
        "trigger": "thought_records >= 5"
    },
    {
        "id": "first_task_complete",
        "title": "Action Taker 🎯",
        "description": "Completed your first scheduled behavioral activation activity.",
        "category": "BEHAVIORAL",
        "trigger": "tasks_completed >= 1"
    },
]

async def evaluate_milestones(user_id: str, db: AsyncSession) -> List[Dict[str, Any]]:
    """
    Evaluates which milestones are newly earned.
    Returns list of newly awarded milestone dicts.
    """
    # Gather counts
    mood_res = await db.execute(select(MoodLog).where(MoodLog.user_id == user_id))
    moods = mood_res.scalars().all()
    mood_count = len(moods)

    tr_res = await db.execute(select(ThoughtRecord).where(ThoughtRecord.user_id == user_id))
    tr_count = len(tr_res.scalars().all())

    task_res = await db.execute(
        select(BehavioralActivationTask).where(
            BehavioralActivationTask.user_id == user_id,
            BehavioralActivationTask.status == "COMPLETED"
        )
    )
    tasks_completed = len(task_res.scalars().all())

    # Streak: count consecutive days with at least one mood log
    dates = sorted({m.created_at.date() for m in moods}, reverse=True)
    streak = 0
    today = datetime.utcnow().date()
    for i, d in enumerate(dates):
        if (today - timedelta(days=i)) == d:
            streak += 1
        else:
            break

    context = {
        "mood_logs": mood_count,
        "thought_records": tr_count,
        "tasks_completed": tasks_completed,
        "streak_days": streak,
    }

    # Fetch already-earned milestone IDs
    existing_res = await db.execute(
        select(ProgressMilestone).where(ProgressMilestone.user_id == user_id)
    )
    earned_ids = {m.title for m in existing_res.scalars().all()}

    newly_earned = []
    for mdef in MILESTONE_DEFINITIONS:
        if mdef["title"] in earned_ids:
            continue
        # Evaluate trigger string
        trigger = mdef["trigger"]
        metric, _, threshold = trigger.partition(" >= ")
        if metric.strip() in context and context[metric.strip()] >= int(threshold.strip()):
            milestone = ProgressMilestone(
                user_id=user_id,
                title=mdef["title"],
                description=mdef["description"],
                category=mdef["category"]
            )
            db.add(milestone)
            newly_earned.append({
                "title": mdef["title"],
                "description": mdef["description"],
                "category": mdef["category"]
            })

    if newly_earned:
        await db.commit()

    return newly_earned

