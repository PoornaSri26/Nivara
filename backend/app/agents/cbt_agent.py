"""
CBT Agent: Socratic Dialogue, Cognitive Restructuring, and Behavioral Experiments.
"""

from typing import Dict, Any, List
from app.exercises.thought_record import THOUGHT_RECORD_STEPS, get_next_step
from app.exercises.behavioral_activation import generate_micro_action
from app.exercises.grounding import get_grounding_exercise

class CBTAgent:
    @staticmethod
    def process_step(current_step: str, user_input: str, detected_distortions: List[str]) -> Dict[str, Any]:
        """
        Drives the interactive 7-column thought record step-by-step.
        """
        next_step_data = get_next_step(current_step)
        
        reply_parts = []
        if current_step == "AUTOMATIC_THOUGHT" and detected_distortions:
            reply_parts.append(f"Noticing that thought, it shows traits of **{', '.join(detected_distortions)}**.")
        elif current_step == "EVIDENCE_FOR":
            reply_parts.append("That's helpful to write down plainly. Now let's balance the scales.")
        elif current_step == "EVIDENCE_AGAINST":
            reply_parts.append("Notice how different it looks when we bring in objective reality.")

        reply_parts.append(f"### {next_step_data['title']}")
        reply_parts.append(next_step_data['prompt'])
        reply_parts.append(f"*Example:* {next_step_data['example']}")

        return {
            "reply": "\n\n".join(reply_parts),
            "next_step": next_step_data["step_id"],
            "suggested_replies": ["I'm ready", "Help me rephrase this", "Skip step"]
        }

    @staticmethod
    def recommend_exercise(mood_score: int, detected_distortions: List[str]) -> Dict[str, Any]:
        """
        Progressive difficulty & matching exercise to emotional state.
        If mood is severe/acute (<= 3), recommend Grounding / Somatic stabilization first.
        If moderate (4-6), recommend Thought Record.
        If stable (7+), recommend Values & Behavioral Activation.
        """
        if mood_score <= 3:
            return {
                "recommended_exercise": "GROUNDING",
                "reason": "When emotional intensity is very high, grounding the body creates safety before engaging in cognitive restructuring.",
                "exercise_data": get_grounding_exercise("BOX_BREATHING")
            }
        elif detected_distortions or (4 <= mood_score <= 6):
            return {
                "recommended_exercise": "THOUGHT_RECORD",
                "reason": "Examining cognitive distortions and weighing evidence is ideal for untangling anxious or self-critical thoughts.",
                "exercise_data": THOUGHT_RECORD_STEPS[0]
            }
        else:
            return {
                "recommended_exercise": "BEHAVIORAL_ACTIVATION",
                "reason": "Building forward momentum and reinforcing positive daily rhythms through small meaningful actions.",
                "exercise_data": generate_micro_action("PLEASURE")
            }

