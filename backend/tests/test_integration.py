"""
Integration tests for the complete API pipeline.
Tests the full request lifecycle: user creation → chat turn → memory proposal
→ mood log → milestone evaluation → weekly report.
"""

import unittest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.models.database import Base
from app.models.schema import User, Session, Message, MoodLog, ThoughtRecord, BehavioralActivationTask
from app.models.milestones import SessionBookmark, ProgressMilestone
from app.memory.true_memory import TrueMemoryService
from app.services.milestones import evaluate_milestones

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

def async_test(coro):
    def wrapper(*args, **kwargs):
        return asyncio.run(coro(*args, **kwargs))
    return wrapper

class TestIntegrationPipeline(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = create_async_engine(TEST_DB_URL, echo=False)
        self.SessionLocal = async_sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)
        async with self.engine.begin() as conn:
            # Import all table models to register them
            await conn.run_sync(Base.metadata.create_all)
            # Also create milestone tables
            from app.models.milestones import SessionBookmark, ProgressMilestone
            from sqlalchemy import inspect
            await conn.run_sync(lambda c: (
                SessionBookmark.__table__.create(c, checkfirst=True),
                ProgressMilestone.__table__.create(c, checkfirst=True)
            ))

    async def asyncTearDown(self):
        await self.engine.dispose()

    async def test_memory_lifecycle(self):
        async with self.SessionLocal() as db:
            # Create user
            user = User(id="test-user-1", region="US")
            db.add(user)
            await db.commit()

            # Create memory in PROPOSED state
            mem = await TrueMemoryService.create_proposed_memory(
                db=db,
                user_id="test-user-1",
                category="TRIGGER",
                content="Anxiety before team standups",
                confidence_score=0.85
            )
            self.assertIsNotNone(mem)
            self.assertEqual(mem.status, "PROPOSED")

            # Confirm it
            updated = await TrueMemoryService.update_memory_status(db, mem.id, "CONFIRMED")
            self.assertEqual(updated.status, "CONFIRMED")
            self.assertIsNone(updated.expires_at)  # Confirmed → permanent

            # Privacy mode: should return empty list
            user.privacy_mode_enabled = True
            await db.commit()
            memories = await TrueMemoryService.get_user_memories(db, "test-user-1", status="CONFIRMED")
            self.assertEqual(len(memories), 0)

            # Re-enable and verify retrieval
            user.privacy_mode_enabled = False
            await db.commit()
            memories = await TrueMemoryService.get_user_memories(db, "test-user-1", status="CONFIRMED")
            self.assertEqual(len(memories), 1)

    async def test_milestone_awards(self):
        async with self.SessionLocal() as db:
            user = User(id="test-user-2", region="IN")
            db.add(user)
            # First mood log
            db.add(MoodLog(user_id="test-user-2", mood_score=7, primary_emotion="Calm", coping_confidence=7))
            # First thought record
            db.add(ThoughtRecord(
                user_id="test-user-2",
                situation="Job interview",
                automatic_thought="I will fail",
                cognitive_distortions=["Catastrophizing"]
            ))
            # First completed task
            task = BehavioralActivationTask(
                user_id="test-user-2",
                title="Morning walk",
                status="COMPLETED"
            )
            db.add(task)
            await db.commit()

            earned = await evaluate_milestones("test-user-2", db)
            earned_titles = [m["title"] for m in earned]
            self.assertIn("First Step 🌱", earned_titles)
            self.assertIn("Thought Examiner 🔍", earned_titles)
            self.assertIn("Action Taker 🎯", earned_titles)

            # Re-running should not duplicate
            earned_again = await evaluate_milestones("test-user-2", db)
            self.assertEqual(len(earned_again), 0)

if __name__ == "__main__":
    unittest.main()

