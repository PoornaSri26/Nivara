"""
7-Column Thought Record Protocol for Cognitive Restructuring.
Step 1: Situation (Who, what, when, where)
Step 2: Automatic Thought (Exact words or image that passed through mind)
Step 3: Initial Emotion & Intensity (0-100%)
Step 4: Cognitive Distortions Identified
Step 5: Evidence Supporting the Thought (Factual only, not feelings)
Step 6: Evidence Against the Thought (Alternative interpretations, past experiences)
Step 7: Balanced Alternative Thought & Re-rated Emotion Intensity
"""

from typing import Dict, Any, List

THOUGHT_RECORD_STEPS = [
    {
        "step_id": "SITUATION",
        "title": "1. The Situation",
        "prompt": "What happened? Describe the specific event, conversation, or moment that triggered this feeling without judgment.",
        "example": "Giving an update in the Monday morning team standup."
    },
    {
        "step_id": "AUTOMATIC_THOUGHT",
        "title": "2. Automatic Thought",
        "prompt": "What thought or mental image immediately popped into your head? What were you telling yourself?",
        "example": "'I stumbled over my words; everyone thinks I am incompetent.'"
    },
    {
        "step_id": "EMOTION",
        "title": "3. Emotions & Intensity",
        "prompt": "What emotions arose, and on a scale of 0 to 100%, how intense were they?",
        "example": "Anxiety: 85%, Embarrassment: 90%"
    },
    {
        "step_id": "DISTORTIONS",
        "title": "4. Cognitive Distortions",
        "prompt": "Look closely at the thought. Does it reflect Catastrophizing, Mind Reading, or All-or-Nothing thinking?",
        "example": "Mind Reading ('everyone thinks I am incompetent') & Catastrophizing."
    },
    {
        "step_id": "EVIDENCE_FOR",
        "title": "5. Evidence That Supports the Thought",
        "prompt": "What objective, factual evidence supports this thought? (Strictly stick to observable facts, not feelings).",
        "example": "I did pause for 5 seconds when answering a question."
    },
    {
        "step_id": "EVIDENCE_AGAINST",
        "title": "6. Evidence Against the Thought",
        "prompt": "What factual evidence contradicts this thought? What would a compassionate friend say?",
        "example": "My manager nodded and thanked me; others also hesitate occasionally; I completed the project on time."
    },
    {
        "step_id": "BALANCED_THOUGHT",
        "title": "7. Balanced Alternative Thought",
        "prompt": "Taking all the evidence into account, what is a more realistic and balanced perspective? Re-rate your emotion intensity now.",
        "example": "'I stumbled briefly, which is normal. The team got the info they needed.' (Anxiety dropped to 30%)."
    }
]

def get_next_step(current_step: str) -> Dict[str, Any]:
    step_ids = [s["step_id"] for s in THOUGHT_RECORD_STEPS]
    try:
        idx = step_ids.index(current_step)
        if idx + 1 < len(THOUGHT_RECORD_STEPS):
            return THOUGHT_RECORD_STEPS[idx + 1]
    except ValueError:
        pass
    return THOUGHT_RECORD_STEPS[0]

