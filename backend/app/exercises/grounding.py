"""
Grounding and Somatic Relaxation Exercises.
Includes:
1. Box Breathing (4-4-4-4)
2. 5-4-3-2-1 Sensory Grounding
"""

from typing import Dict, Any, List

GROUNDING_EXERCISES = {
    "BOX_BREATHING": {
        "title": "Box Breathing (4x4)",
        "duration_seconds": 120,
        "instructions": [
            "Inhale deeply through your nose for 4 seconds.",
            "Hold your breath gently for 4 seconds.",
            "Exhale smoothly through your mouth for 4 seconds.",
            "Rest empty for 4 seconds before the next breath."
        ],
        "rationale": "Box breathing regulates the autonomic nervous system and dampens the sympathetic fight-or-flight response."
    },
    "54321_SENSORY": {
        "title": "5-4-3-2-1 Sensory Reset",
        "duration_seconds": 180,
        "instructions": [
            "Acknowledge 5 things you can SEE around you right now.",
            "Acknowledge 4 things you can physically TOUCH or FEEL (e.g. feet on the floor, texture of your shirt).",
            "Acknowledge 3 distinct sounds you can HEAR.",
            "Acknowledge 2 things you can SMELL.",
            "Acknowledge 1 thing you can TASTE."
        ],
        "rationale": "Sensory grounding interrupts cognitive spirals by redirecting attention to external reality."
    }
}

def get_grounding_exercise(exercise_type: str = "BOX_BREATHING") -> Dict[str, Any]:
    return GROUNDING_EXERCISES.get(exercise_type.upper(), GROUNDING_EXERCISES["BOX_BREATHING"])

