"""
Dual-Gate Safety Orchestrator for Nivara.
Coordinates deterministic regex checks, zero-shot/heuristic risk assessment,
and post-generation clinical guardrails.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.safety.rules import (
    check_deterministic_crisis,
    check_clinical_boundaries,
    check_output_guardrails
)
from app.safety.crisis_resources import get_crisis_response
from app.config import settings

class SafetyAssessment(BaseModel):
    is_safe: bool
    risk_level: str  # "NONE", "LOW", "MODERATE", "CRITICAL"
    risk_score: float = Field(ge=0.0, le=1.0)
    gate_triggered: Optional[str] = None  # "DETERMINISTIC", "CLASSIFIER", "BOUNDARY", "OUTPUT_GUARDRAIL"
    category: Optional[str] = None
    override_response: Optional[str] = None
    crisis_payload: Optional[Dict[str, Any]] = None
    audit_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class SafetyOrchestrator:
    def __init__(self, user_region: str = "US"):
        self.user_region = user_region

    def assess_input(self, user_message: str) -> SafetyAssessment:
        """
        Gate 1: Deterministic Check
        Gate 2: Nuanced Risk Evaluation
        Gate 3: Clinical Boundary Check
        """
        text = user_message.strip()
        if not text:
            return SafetyAssessment(is_safe=True, risk_level="NONE", risk_score=0.0)

        # Gate 1: Deterministic Crisis Check (Immediate Halt)
        if check_deterministic_crisis(text):
            crisis_info = get_crisis_response(self.user_region)
            return SafetyAssessment(
                is_safe=False,
                risk_level="CRITICAL",
                risk_score=1.0,
                gate_triggered="DETERMINISTIC",
                category="CRISIS_SELF_HARM",
                override_response=crisis_info["message"],
                crisis_payload=crisis_info
            )

        # Gate 1.5: Clinical Boundary Violation Check
        is_boundary_violation, category, refusal_msg = check_clinical_boundaries(text)
        if is_boundary_violation:
            return SafetyAssessment(
                is_safe=False,
                risk_level="MODERATE",
                risk_score=0.75,
                gate_triggered="BOUNDARY",
                category=category,
                override_response=refusal_msg,
                crisis_payload=None
            )

        # Gate 2: Heuristic Risk Scoring (Simulating classifier & semantic sentiment)
        risk_score = self._compute_latent_risk(text)
        if risk_score >= settings.CRISIS_CONFIDENCE_THRESHOLD:
            crisis_info = get_crisis_response(self.user_region)
            return SafetyAssessment(
                is_safe=False,
                risk_level="CRITICAL",
                risk_score=risk_score,
                gate_triggered="CLASSIFIER",
                category="PROBABILISTIC_CRISIS",
                override_response=crisis_info["message"],
                crisis_payload=crisis_info
            )

        risk_level = "LOW" if risk_score > 0.3 else "NONE"
        return SafetyAssessment(
            is_safe=True,
            risk_level=risk_level,
            risk_score=risk_score,
            gate_triggered=None,
            category=None,
            override_response=None,
            crisis_payload=None
        )

    def assess_output(self, generated_response: str) -> str:
        """
        Inspects generated response to ensure no clinical advice or ungrounded claims escaped.
        """
        is_safe, sanitized = check_output_guardrails(generated_response)
        return sanitized

    def _compute_latent_risk(self, text: str) -> float:
        """
        Heuristic evaluation of despair, hopelessness, and acute isolation.
        In a production environment, this interfaces with a fine-tuned binary classifier.
        """
        text_lower = text.lower()
        hopeless_cues = [
            "hopeless", "can't go on", "tired of living", "worthless", "nobody cares",
            "giving up completely", "no way out", "hate myself", "burden to everyone",
            "disappear forever", "wish i didn't wake up"
        ]
        score = 0.0
        matches = [cue for cue in hopeless_cues if cue in text_lower]
        if matches:
            score = min(0.35 + (len(matches) * 0.15), 0.85)

        # Explicit negative self-blame + severity markers
        if "disappear forever" in text_lower or "wish i didn't wake up" in text_lower:
            score = max(score, 0.70)

        return round(score, 2)

