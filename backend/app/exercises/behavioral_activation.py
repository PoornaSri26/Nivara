"""
Behavioral Activation Protocol.
Breaks the lethargy/depression cycle through intentional activity scheduling
rated on Mastery (sense of accomplishment) and Pleasure (enjoyment).
"""

from typing import List, Dict, Any

ACTIVITY_CATEGORIES = {
    "PLEASURE": {
        "title": "Nourishing & Joyful",
        "examples": [
            "Listen to an uplifting album for 15 minutes",
            "Sip a warm cup of herbal tea mindfully without your phone",
            "Take a short walk in nature or around the block",
            "Read one chapter of an engaging book"
        ]
    },
    "MASTERY": {
        "title": "Accomplishment & Micro-Progress",
        "examples": [
            "Clear off your desk or wash 3 dishes",
            "Reply to one brief pending email",
            "Spend 10 minutes organizing one drawer",
            "Prepare fresh ingredients for a meal"
        ]
    },
    "CONNECTION": {
        "title": "Social & Relational",
        "examples": [
            "Send a warm text to a friend or family member",
            "Smile or say hello to a neighbor or barista",
            "Share a memory or photo with a loved one"
        ]
    }
}

def generate_micro_action(category: str = "PLEASURE") -> Dict[str, Any]:
    cat_data = ACTIVITY_CATEGORIES.get(category.upper(), ACTIVITY_CATEGORIES["PLEASURE"])
    return {
        "category": category,
        "title": cat_data["title"],
        "suggested_activities": cat_data["examples"],
        "guidance": "Choose an action so small that your resistance is almost zero. Rating mastery and pleasure afterward helps re-wire automatic avoidance."
    }

