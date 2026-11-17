"""
Session Bookmarks and Progress Milestones for Nivara.

Bookmarks  — User can pin any bot message to a personal 'Coping Toolbox'.
Milestones — Celebrate consistency and insight without reducing wellbeing to a score.
"""

from datetime import datetime
import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.database import Base

def _uuid():
    return str(uuid.uuid4())

class SessionBookmark(Base):
    """Saved reflections and helpful responses from chat history."""
    __tablename__ = "session_bookmarks"

    id            = Column(String(36), primary_key=True, default=_uuid)
    user_id       = Column(String(36), ForeignKey("users.id"), nullable=False)
    session_id    = Column(String(36), ForeignKey("sessions.id"), nullable=True)
    message_id    = Column(String(36), nullable=True)
    label         = Column(String(200), nullable=False)  # User-given name
    content       = Column(Text, nullable=False)         # Bookmarked text
    is_in_toolbox = Column(Boolean, default=False)       # In coping toolbox
    created_at    = Column(DateTime, default=datetime.utcnow)

class ProgressMilestone(Base):
    """Celebrate consistency, learning moments, and behavioral successes."""
    __tablename__ = "progress_milestones"

    id          = Column(String(36), primary_key=True, default=_uuid)
    user_id     = Column(String(36), ForeignKey("users.id"), nullable=False)
    title       = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    # STREAK | THOUGHT_RECORD | GROUNDING | MOOD_LOG | BEHAVIORAL | INSIGHT
    category    = Column(String(50), nullable=False, default="STREAK")
    earned_at   = Column(DateTime, default=datetime.utcnow)

