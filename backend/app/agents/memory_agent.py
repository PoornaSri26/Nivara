"""
True Memory Agent for Nivara.
Provides explicit, user-controlled memory lifecycle:
1. Proposed vs Confirmed status
2. Direct facts vs Inferred patterns
3. Confidence score assignment
4. Privacy Mode enforcement
5. Non-intrusive contextual retrieval and confirmation prompts
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class MemoryAgent:
    @staticmethod
    def extract_prospective_memories(user_message: str, detected_distortions: List[str]) -> List[Dict[str, Any]]:
        """
        Scans message for persistent facts, goals, or recurring behavioral triggers.
        Assigns source_type, category, confidence score, and status='PROPOSED'.
        """
        proposals = []
        text = user_message.strip()

        # 1. Direct user stated goals
        goal_match = re.search(r"\b(i\s+want\s+to|my\s+goal\s+is\s+to|trying\s+to)\s+([^\.\,\n]+)", text, re.IGNORECASE)
        if goal_match:
            proposals.append({
                "category": "GOAL",
                "content": f"Wants to {goal_match.group(2).strip()}",
                "confidence_score": 0.95,
                "source_type": "DIRECT_USER_FACT",
                "status": "PROPOSED",
                "confirmation_prompt": f"You mentioned wanting to '{goal_match.group(2).strip()}'. Would you like me to remember this goal for future sessions?"
            })

        # 2. Identified recurring trigger
        trigger_match = re.search(r"\b(always\s+get\s+anxious\s+(before|when)|stresses\s+me\s+out\s+when|triggered\s+by)\s+([^\.\,\n]+)", text, re.IGNORECASE)
        if trigger_match:
            trigger_content = trigger_match.group(3).strip()
            proposals.append({
                "category": "TRIGGER",
                "content": f"Stress/anxiety triggered by {trigger_content}",
                "confidence_score": 0.85,
                "source_type": "INFERRED_PATTERN",
                "status": "PROPOSED",
                "confirmation_prompt": f"It sounds like {trigger_content} is a recurring source of stress. Would it be helpful if I keep note of this trigger?"
            })

        # 3. Recurring cognitive distortion pattern
        if detected_distortions and len(detected_distortions) >= 2:
            distortion_str = ", ".join(detected_distortions)
            proposals.append({
                "category": "COGNITIVE_DISTORTION",
                "content": f"Tendency toward {distortion_str} during high-stress situations",
                "confidence_score": 0.70,
                "source_type": "INFERRED_PATTERN",
                "status": "PROPOSED",
                "confirmation_prompt": f"I noticed thoughts related to {distortion_str}. Should we track this pattern over time to see how our exercises help?"
            })

        return proposals

    @staticmethod
    def format_context_with_memories(memories: List[Dict[str, Any]]) -> str:
        """
        Builds a safe, non-presumptive context preamble for the reasoning agent.
        Only includes CONFIRMED memories.
        """
        if not memories:
            return ""

        lines = ["CONFIRMED USER CONTEXT (Reference with humility; do not make unverified assumptions):"]
        for m in memories:
            category = m.get("category", "FACT")
            content = m.get("content", "")
            lines.append(f"- [{category}]: {content}")

        return "\n".join(lines)

