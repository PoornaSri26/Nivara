"""
Pydantic schema definitions for API validation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    display_name: str = "Seeker"
    email: Optional[str] = None
    region: str = "US"

class UserResponse(BaseModel):
    id: str
    display_name: str
    email: Optional[str]
    privacy_mode_enabled: bool
    region: str

class ChatMessageRequest(BaseModel):
    session_id: Optional[str] = None
    user_id: str
    content: str
    mode_override: Optional[str] = None  # e.g., "JUST_LISTEN", "THOUGHT_RECORD"
    region: str = "US"

class ChatMessageResponse(BaseModel):
    session_id: str
    reply: str
    sender: str
    mode: str
    is_crisis: bool = False
    crisis_payload: Optional[Dict[str, Any]] = None
    detected_distortions: List[str] = []
    proposed_memories: List[Dict[str, Any]] = []
    suggested_quick_replies: List[str] = []

class MemoryActionRequest(BaseModel):
    action: str  # "CONFIRM", "REJECT", "DELETE", "UPDATE"
    updated_content: Optional[str] = None

class MemoryResponse(BaseModel):
    id: str
    category: str
    content: str
    confidence_score: float
    source_type: str
    status: str
    created_at: str

class MoodLogCreate(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    mood_score: int = Field(ge=1, le=10)
    coping_confidence: int = Field(default=5, ge=1, le=10)
    primary_emotion: str
    emotion_tags: List[str] = []
    trigger_note: Optional[str] = None

class ThoughtRecordCreate(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    situation: str
    automatic_thought: str
    emotions: List[Dict[str, Any]] = []
    cognitive_distortions: List[str] = []
    evidence_for: Optional[str] = None
    evidence_against: Optional[str] = None
    alternative_thought: Optional[str] = None
    outcome_emotion_intensity: Optional[int] = None

class BehavioralTaskCreate(BaseModel):
    user_id: str
    title: str
    activity_type: str = "PLEASURE"
    difficulty_rating: int = 3
    pleasure_rating: int = 3
    notes: Optional[str] = None

