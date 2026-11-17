"""
Weekly Insight Report Generator for Nivara.
Produces clinician-digestible summaries of user-reported patterns,
cognitive distortion distributions, triggers, and behavioral activation homework.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from collections import Counter

from app.models.schema import MoodLog, ThoughtRecord, BehavioralActivationTask, UserMemory

class WeeklyReportService:
    @staticmethod
    async def generate_weekly_digest(user_id: str, db: AsyncSession) -> Dict[str, Any]:
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        # 1. Fetch Mood logs
        mood_res = await db.execute(
            select(MoodLog).where(MoodLog.user_id == user_id, MoodLog.created_at >= seven_days_ago)
        )
        moods = mood_res.scalars().all()

        # 2. Fetch Thought Records
        tr_res = await db.execute(
            select(ThoughtRecord).where(ThoughtRecord.user_id == user_id, ThoughtRecord.created_at >= seven_days_ago)
        )
        records = tr_res.scalars().all()

        # 3. Fetch Tasks
        task_res = await db.execute(
            select(BehavioralActivationTask).where(BehavioralActivationTask.user_id == user_id, BehavioralActivationTask.created_at >= seven_days_ago)
        )
        tasks = task_res.scalars().all()

        # Analysis
        mood_scores = [m.mood_score for m in moods]
        avg_mood = round(sum(mood_scores) / len(mood_scores), 1) if mood_scores else None
        min_mood = min(mood_scores) if mood_scores else None
        max_mood = max(mood_scores) if mood_scores else None

        distortion_counts = Counter()
        for r in records:
            if r.cognitive_distortions:
                for d in r.cognitive_distortions:
                    distortion_counts[d] += 1

        trigger_counts = Counter()
        for m in moods:
            if m.trigger_note:
                trigger_counts[m.trigger_note] += 1

        completed_tasks = sum(1 for t in tasks if t.status == "COMPLETED")
        total_tasks = len(tasks)

        # Formatted Clinical Markdown Report
        top_distortions_md = "\n".join([f"- **{d}**: {c} occurrences" for d, c in distortion_counts.most_common(3)]) or "- No major distortions recorded this week."
        top_triggers_md = "\n".join([f"- {t} ({c} times)" for t, c in trigger_counts.most_common(3)]) or "- No specific triggers recorded."

        markdown_report = f"""# Nivara: Weekly Self-Reflection & Insight Report
*Period: {(datetime.utcnow() - timedelta(days=7)).strftime('%B %d, %Y')} – {datetime.utcnow().strftime('%B %d, %Y')}*

---

### 1. Emotional Rhythm & Mood Overview
- **Average Mood Score:** {avg_mood if avg_mood is not None else 'N/A'}/10 (Range: {min_mood} to {max_mood})
- **Total Check-Ins Logged:** {len(moods)}

### 2. Cognitive Distortion Distribution
{top_distortions_md}

### 3. Situational Triggers Observed
{top_triggers_md}

### 4. Behavioral Activation & Rhythms
- **Activities Completed:** {completed_tasks} of {total_tasks} planned
- **Consistency Rate:** {round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0}%

---

### Clinician Notes & Discussion Prompts
1. *Notice how mood correlated with reported triggers.*
2. *Examine the most frequent distortion with a compassionate, balanced lens.*
3. *Identify one micro-action to anchor daily routine in the upcoming week.*

> **Clinical Notice:** This report summarizes self-reported observations and correlations. It does not provide medical diagnoses or replace clinical assessment.
"""

        return {
            "user_id": user_id,
            "generated_at": datetime.utcnow().isoformat(),
            "average_mood": avg_mood,
            "total_checkins": len(moods),
            "thought_records_completed": len(records),
            "activities_completed": completed_tasks,
            "total_activities": total_tasks,
            "top_distortions": dict(distortion_counts.most_common(3)),
            "top_triggers": dict(trigger_counts.most_common(3)),
            "markdown_report": markdown_report
        }

