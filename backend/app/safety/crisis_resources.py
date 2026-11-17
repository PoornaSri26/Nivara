"""
Multi-region crisis resources and hotlines for Nivara's emergency safety escalation.
"""

from typing import Dict, Any, List

CRISIS_RESOURCES: Dict[str, Dict[str, Any]] = {
    "US": {
        "region_name": "United States",
        "hotline_name": "Suicide & Crisis Lifeline",
        "phone": "988",
        "sms": "Text HOME to 741741 (Crisis Text Line)",
        "web": "https://988lifeline.org",
        "chat_url": "https://988lifeline.org/chat/"
    },
    "UK": {
        "region_name": "United Kingdom",
        "hotline_name": "Samaritans & NHS 111",
        "phone": "116 123 (Samaritans) or 111 (NHS Mental Health)",
        "sms": "Text SHOUT to 85258",
        "web": "https://www.samaritans.org",
        "chat_url": "https://www.giveusashout.org"
    },
    "CA": {
        "region_name": "Canada",
        "hotline_name": "Suicide Crisis Helpline",
        "phone": "988",
        "sms": "Text 988",
        "web": "https://988.ca",
        "chat_url": "https://988.ca"
    },
    "IN": {
        "region_name": "India",
        "hotline_name": "Tele-MANAS & Vandrevala Foundation",
        "phone": "14416 (Tele-MANAS) or +91 9999 666 555",
        "sms": "N/A",
        "web": "https://telemanas.mohfw.gov.in",
        "chat_url": "https://www.vandrevalafoundation.com"
    },
    "AU": {
        "region_name": "Australia",
        "hotline_name": "Lifeline",
        "phone": "13 11 14",
        "sms": "Text 0477 13 11 14",
        "web": "https://www.lifeline.org.au",
        "chat_url": "https://www.lifeline.org.au/crisis-chat/"
    },
    "INTL": {
        "region_name": "International",
        "hotline_name": "Befrienders Worldwide & IASP",
        "phone": "Please consult local emergency services",
        "sms": "Varies by country",
        "web": "https://www.befrienders.org",
        "chat_url": "https://www.iasp.info/resources/Crisis_Centres/"
    }
}

def get_crisis_response(region: str = "US") -> Dict[str, Any]:
    resource = CRISIS_RESOURCES.get(region.upper(), CRISIS_RESOURCES["US"])
    return {
        "is_crisis": True,
        "message": (
            "I hear how much pain you are carrying right now, and I care deeply about your safety. "
            "Because I am an AI companion and not a human clinician or emergency service, I cannot provide "
            "the support you need in this moment. Please connect with someone who can support you right now:"
        ),
        "primary_resource": resource,
        "secondary_resource": CRISIS_RESOURCES["INTL"],
        "action_required": "EMERGENCY_INTERRUPT",
        "suggested_actions": [
            f"Call {resource['phone']} immediately",
            f"Text: {resource['sms']}",
            "Reach out to a trusted family member, doctor, or go to the nearest emergency room."
        ]
    }

