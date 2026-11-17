"""
State definition for Nivara's conversational state machine.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ConversationState(BaseModel):
    session_id: str
    user_id: str
    current_mode: str = "GUIDED_CBT"  # GUIDED_CBT, JUST_LISTEN, THOUGHT_RECORD, GROUNDING, BEHAVIORAL_ACTIVATION
    exercise_step: Optional[str] = "INIT"  # e.g., "SITUATION", "THOUGHT", "DISTORTION", "EVIDENCE", "ALTERNATIVE"
    user_message: str = ""
    agent_response: str = ""
    
    # Cognitive & Emotional state
    detected_distortions: List[str] = Field(default_factory=list)
    identified_triggers: List[str] = Field(default_factory=list)
    current_mood_score: Optional[int] = None
    
    # Memory interaction
    relevant_memories: List[Dict[str, Any]] = Field(default_factory=list)
    proposed_memories: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Safety and quality
    safety_halt: bool = False
    safety_payload: Optional[Dict[str, Any]] = None
    clinical_rubric_score: Optional[float] = None
    quick_replies: List[str] = Field(default_factory=list)

