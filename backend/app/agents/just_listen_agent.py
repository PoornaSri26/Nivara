"""
Just Listen Agent: Non-Directive Empathetic Listening Mode.
Adheres strictly to Rogerian person-centered therapy principles:
- Unconditional positive regard
- Empathetic reflecting and validation
- Strict omission of unsolicited advice, homework, or cognitive restructuring
"""

import random
from typing import List

VALIDATION_OPENERS = [
    "I am here with you, and I hear how much you are carrying.",
    "Thank you for sharing that with me. It takes real courage to put those feelings into words.",
    "That sounds genuinely overwhelming, and it makes complete sense that you feel this way.",
    "I'm listening closely. Please take all the time and space you need.",
    "It sounds like you've been holding onto a lot of tension around this."
]

VALIDATION_FOLLOW_UPS = [
    "Would you like to keep talking about what that felt like, or simply sit with it for a moment?",
    "I am holding space for you—there is no need to fix or solve anything right now.",
    "What feels like the heaviest part of this to carry today?",
    "I'm right here with you. Whatever you are feeling is completely valid."
]

class JustListenAgent:
    @staticmethod
    def respond(user_message: str) -> str:
        """
        Generates an empathetic reflection without offering advice, reframing, or CBT exercises.
        """
        opener = random.choice(VALIDATION_OPENERS)
        follow_up = random.choice(VALIDATION_FOLLOW_UPS)
        
        # Simple extraction of key sentiment words to mirror back warmly
        text_lower = user_message.lower()
        mirror_phrase = ""
        if "exhausted" in text_lower or "tired" in text_lower:
            mirror_phrase = " Hearing how drained and exhausted you are, I just want to honor how hard you have been trying."
        elif "anxious" in text_lower or "scared" in text_lower or "nervous" in text_lower:
            mirror_phrase = " Anxiety can be so physically and emotionally exhausting."
        elif "lonely" in text_lower or "alone" in text_lower:
            mirror_phrase = " Feeling alone with these thoughts is so difficult, but please know you are not alone right now."
        elif "angry" in text_lower or "frustrated" in text_lower:
            mirror_phrase = " Your frustration is completely understandable given what you are experiencing."

        return f"{opener}{mirror_phrase}\n\n{follow_up}"

