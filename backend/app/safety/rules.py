"""
Deterministic safety rules, clinical boundary validators, and pattern matchers for Nivara.
"""

import re
from typing import List, Tuple, Dict, Any

# 1. Deterministic Crisis & Acute Risk Regexes
CRISIS_PATTERNS = [
    # Suicidal ideation & intent
    r"\b(want|wish|going)\s+to\s+(die|end\s+it\s+all|kill\s+myself|commit\s+suicide)\b",
    r"\b(suicide|suicidal|better\s+off\s+dead|no\s+reason\s+to\s+live)\b",
    r"\bhow\s+to\s+(hang|slit|overdose|kill)\s+myself\b",
    r"\bi\s+(can['’]?t|cannot)\s+take\s+this\s+anymore.*(die|kill)\b",
    r"\bgoodbye\s+everyone.*(sorry|forgive\s+me)\b",
    r"\bplanning\s+my\s+suicide\b",
    # Non-suicidal self injury
    r"\b(cut|cutting|burn|burning|harm|harming)\s+myself\b",
    r"\burg(e|es)\s+to\s+(cut|bleed|self-harm|hurt\s+myself)\b",
    # Violence towards others
    r"\b(going\s+to|want\s+to)\s+(kill|murder|shoot|stab|harm)\s+(someone|them|my\s+\w+)\b",
    # Extreme acute crisis
    r"\bswallowed\s+a\s+bottle\s+of\b",
    r"\bholding\s+a\s+(gun|knife|blade)\b"
]

CRISIS_REGEX = re.compile("|".join(CRISIS_PATTERNS), re.IGNORECASE)

# 2. Clinical Boundary Violations (Requests the AI must refuse / redirect)
BOUNDARY_PATTERNS: Dict[str, Tuple[re.Pattern, str]] = {
    "MEDICATION_PRESCRIPTION": (
        re.compile(r"\b(what\s+dose|dosage|prescribe|should\s+i\s+take|increase\s+my\s+dose\s+of)\s+([a-z\s]+(zoloft|lexapro|prozac|xanax|adderall|sertraline|fluoxetine|wellbutrin|ativan|valium|klonopin|ssri|antidepressant|medication))\b", re.IGNORECASE),
        "I cannot recommend, adjust, or prescribe medications. Please consult your prescribing physician, psychiatrist, or pharmacist regarding any medication questions."
    ),
    "DIAGNOSTIC_LABELING": (
        re.compile(r"\b(do\s+i\s+have|diagnose\s+me\s+with|am\s+i\s+(bipolar|schizophrenic|borderline|clinically\s+depressed|narcissistic))\b", re.IGNORECASE),
        "As an AI wellness companion, I cannot provide psychiatric or medical diagnoses. I can help you explore your thoughts and emotions, but a formal assessment requires a licensed mental health professional."
    ),
    "DELUSION_REINFORCEMENT": (
        re.compile(r"\b(government\s+is\s+tracking\s+my\s+thoughts|microchip\s+in\s+my\s+brain|voices\s+in\s+the\s+walls\s+commanding\s+me|aliens\s+are\s+controlling\s+me)\b", re.IGNORECASE),
        "I hear that you are feeling overwhelmed and frightened right now. While I cannot validate experiences involving tracking or outside forces, I am here to help you focus on grounding exercises and finding calm. If you feel unsafe, speaking with a healthcare professional is strongly recommended."
    )
}

# 3. Output Guardrails: Ensure Nivara never outputs diagnostic claims or prescriptive medical advice
OUTPUT_VIOLATION_PATTERNS = [
    re.compile(r"\byou\s+(have|are\s+suffering\s+from)\s+(clinical\s+depression|bipolar\s+disorder|schizophrenia|bpd|ptsd|ocd)\b", re.IGNORECASE),
    re.compile(r"\byou\s+should\s+(take|increase|decrease|stop\s+taking)\s+(mg|milligrams|pills|dosage|antidepressant)\b", re.IGNORECASE),
]

def check_deterministic_crisis(text: str) -> bool:
    """Returns True if any critical crisis pattern matches."""
    return bool(CRISIS_REGEX.search(text))

def check_clinical_boundaries(text: str) -> Tuple[bool, str, str]:
    """
    Checks if user is requesting out-of-scope medical/clinical intervention.
    Returns: (is_violation, category, refusal_message)
    """
    for category, (pattern, refusal_message) in BOUNDARY_PATTERNS.items():
        if pattern.search(text):
            return True, category, refusal_message
    return False, "", ""

def check_output_guardrails(text: str) -> Tuple[bool, str]:
    """
    Scans generated model output to ensure no accidental medical claims leaked.
    Returns: (is_safe, sanitized_or_original_text)
    """
    for pattern in OUTPUT_VIOLATION_PATTERNS:
        if pattern.search(text):
            sanitized = (
                "I want to support you in exploring your thoughts, but please keep in mind that I cannot "
                "provide a medical diagnosis or prescribe medical treatments. Let's focus on evidence-based "
                "coping tools and thought records, or consult a licensed professional for diagnostic guidance."
            )
            return False, sanitized
    return True, text

