"""
Reflection Agent: Cognitive Distortion Detection, Emotional Labeling, and Trigger Mapping.
Based on standard Beck Institute Cognitive Behavioral Therapy taxonomy.
"""

import re
from typing import List, Dict, Any, Tuple

DISTORTION_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "Catastrophizing": {
        "description": "Assuming the worst possible outcome will happen, even when it is improbable.",
        "regex": r"\b(worst\s+(thing|case|day)|everything\s+is\s+ruined|my\s+life\s+is\s+over|disaster|total\s+failure)\b",
        "reframing_prompt": "What is the most realistic outcome, and what is one small thing you can handle?"
    },
    "All-or-Nothing Thinking": {
        "description": "Viewing situations in black-and-white categories with no middle ground.",
        "regex": r"\b(always|never|completely|totally\s+useless|nothing\s+ever\s+works|every\s+single\s+time)\b",
        "reframing_prompt": "Are there any exceptions or shades of grey in this situation?"
    },
    "Mind Reading": {
        "description": "Assuming you know what others are thinking, usually believing they judge you negatively.",
        "regex": r"\b(they\s+(all\s+)?(hate|think\s+i['’]?m|judge)\s+me|i\s+know\s+they\s+think\s+i['’]?m\s+stupid|everyone\s+is\s+laughing)\b",
        "reframing_prompt": "What concrete evidence do you have for what they are thinking versus what is an assumption?"
    },
    "Emotional Reasoning": {
        "description": "Believing that because you feel something strongly, it must be an objective truth.",
        "regex": r"\b(i\s+feel\s+like\s+a\s+failure\s+so\s+i\s+am|i\s+feel\s+guilty\s+so\s+i\s+must\s+have\s+done\s+something\s+wrong|feels\s+hopeless)\b",
        "reframing_prompt": "Remember that emotions are valid signals of how you feel, but feelings are not always objective facts."
    },
    "Should Statements": {
        "description": "Holding rigid, unforgiving rules for yourself or others ('I should', 'I must').",
        "regex": r"\b(i\s+(should|must|ought\s+to)\s+have\s+known|i\s+shouldn['’]?t\s+feel\s+this\s+way|they\s+must\s+always)\b",
        "reframing_prompt": "What if you replaced 'I should' with 'I would prefer to' or 'It is okay if I'm learning'?"
    },
    "Overgeneralization": {
        "description": "Taking a single negative event as a never-ending pattern of defeat.",
        "regex": r"\b(i\s+can\s+never\s+do\s+anything\s+right|nobody\s+likes\s+me|this\s+keeps\s+happening\s+to\s+me)\b",
        "reframing_prompt": "Is this a single difficult moment, or does it truly define every experience?"
    },
    "Personalization": {
        "description": "Holding yourself personally responsible for events outside your control.",
        "regex": r"\b(it['’]?s\s+all\s+my\s+fault|i\s+ruined\s+it\s+for\s+everyone|if\s+only\s+i\s+hadn['’]?t)\b",
        "reframing_prompt": "What other external factors or people contributed to how things turned out?"
    }
}

class ReflectionAgent:
    @staticmethod
    def detect_distortions(text: str) -> List[Dict[str, str]]:
        """
        Scans user text for common cognitive distortions.
        Returns list of detected distortions with description and reframing prompts.
        """
        detected = []
        for name, data in DISTORTION_TAXONOMY.items():
            if re.search(data["regex"], text, re.IGNORECASE):
                detected.append({
                    "name": name,
                    "description": data["description"],
                    "reframing_prompt": data["reframing_prompt"]
                })
        return detected

    @staticmethod
    def extract_triggers(text: str) -> List[str]:
        """
        Extracts situational triggers (e.g. presentation, meeting, argument, deadline).
        """
        trigger_keywords = [
            "presentation", "speech", "meeting", "interview", "deadline", "boss", "manager",
            "exam", "test", "argument", "fight", "breakup", "family", "traffic", "money",
            "finances", "health", "doctor", "email", "phone call"
        ]
        text_lower = text.lower()
        triggers = [t for t in trigger_keywords if t in text_lower]
        return triggers

    @staticmethod
    def generate_balanced_perspective(user_text: str, detected_distortions: List[str]) -> str:
        """
        Produces a therapeutic reflection gently nudging toward balanced thinking.
        """
        if not detected_distortions:
            return "Thank you for sharing that. What feels like the most challenging part of this thought right now?"

        distortion_names = ", ".join(detected_distortions)
        primary = detected_distortions[0]
        reframing = DISTORTION_TAXONOMY.get(primary, {}).get("reframing_prompt", "What would be a more balanced way to look at this?")

        return (
            f"I hear how intense this feels. When you say that, it touches on what CBT calls "
            f"**{primary}**. {reframing}"
        )

