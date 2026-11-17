"""
SQLAlchemy ORM models for Nivara.
Includes User, Sessions, True Memory, Mood Tracking, Thought Records, and Safety Audits.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.models.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=True)
    display_name = Column(String(100), default="Seeker")
    privacy_mode_enabled = Column(Boolean, default=False)  # When True, memories are neither retrieved nor stored
    region = Column(String(10), default="US")
    preferences = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("UserMemory", back_populates="user", cascade="all, delete-orphan")
    mood_logs = relationship("MoodLog", back_populates="user", cascade="all, delete-orphan")
    thought_records = relationship("ThoughtRecord", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("BehavioralActivationTask", back_populates="user", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    mode = Column(String(50), default="GUIDED_CBT")  # GUIDED_CBT, JUST_LISTEN, THOUGHT_RECORD, GROUNDING, JOURNAL
    state_payload = Column(JSON, default=dict)  # State snapshot for LangGraph resumption
    summary = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    safety_audits = relationship("SafetyAudit", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    sender = Column(String(50), nullable=False)  # USER, NIVARA, SYSTEM, SAFETY_ORCHESTRATOR
    content = Column(Text, nullable=False)
    metadata_payload = Column(JSON, default=dict)  # distortions detected, agent used, rubric score
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="messages")

class UserMemory(Base):
    """
    True Memory architecture with explicit confidence, category, status, and audit trail.
    """
    __tablename__ = "user_memories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    category = Column(String(50), nullable=False)  # TRIGGER, COGNITIVE_DISTORTION, STRENGTH, GOAL, FACT
    content = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False, default=1.0)
    source_type = Column(String(50), nullable=False, default="DIRECT_USER_FACT")  # DIRECT_USER_FACT, INFERRED_PATTERN
    status = Column(String(50), nullable=False, default="PROPOSED")  # PROPOSED, CONFIRMED, REJECTED, EXPIRED
    last_referenced_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    embedding_json = Column(JSON, nullable=True)  # Store mock or calculated vector representation
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="memories")

class MoodLog(Base):
    __tablename__ = "mood_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=True)
    mood_score = Column(Integer, nullable=False)  # 1 to 10
    coping_confidence = Column(Integer, nullable=True, default=5)  # 1 to 10
    primary_emotion = Column(String(50), nullable=False)
    emotion_tags = Column(JSON, default=list)  # e.g., ["anxious", "restless", "fatigued"]
    trigger_note = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="mood_logs")

class ThoughtRecord(Base):
    """
    Clinical 7-Column Thought Record for cognitive restructuring.
    """
    __tablename__ = "thought_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=True)
    situation = Column(Text, nullable=False)
    automatic_thought = Column(Text, nullable=False)
    emotions = Column(JSON, default=list)  # [{"name": "Anxiety", "intensity": 80}]
    cognitive_distortions = Column(JSON, default=list)  # ["Catastrophizing", "Mind Reading"]
    evidence_for = Column(Text, nullable=True)
    evidence_against = Column(Text, nullable=True)
    alternative_thought = Column(Text, nullable=True)
    outcome_emotion_intensity = Column(Integer, nullable=True)  # New rating 0-100
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="thought_records")

class BehavioralActivationTask(Base):
    """
    Behavioral Activation activity scheduling and mastery/pleasure tracking.
    """
    __tablename__ = "behavioral_activation_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    activity_type = Column(String(50), default="PLEASURE")  # PLEASURE, MASTERY, CONNECTION, HEALTH
    scheduled_for = Column(DateTime, nullable=True)
    difficulty_rating = Column(Integer, default=3)  # 1-5
    pleasure_rating = Column(Integer, default=3)    # 1-5
    status = Column(String(50), default="PENDING")   # PENDING, COMPLETED, CANCELLED
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="tasks")

class SafetyAudit(Base):
    """
    Audit log of flagged messages and safety interventions.
    """
    __tablename__ = "safety_audits"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=True)
    user_id = Column(String(36), nullable=True)
    raw_input = Column(Text, nullable=False)
    risk_level = Column(String(50), nullable=False)
    risk_score = Column(Float, nullable=False)
    gate_triggered = Column(String(50), nullable=True)
    category = Column(String(100), nullable=True)
    action_taken = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="safety_audits")

