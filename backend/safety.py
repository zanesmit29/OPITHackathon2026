#Two layer system
#Layer 1: keyword matching, no API call, catches obvious cases
#Layer 2: LLM evaluation, catches subtle cases keywords miss

# Both crisis events and dangerous topics are logged to separate files


import os
import json 
from datetime import datetime 
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from backend.prompts import (
    is_crisis_message, 
    is_dangerous_topic,
    CRISIS_RESPONSE_TEMPLATE,
    LOW_CONFIDENCE_TEMPLATE
)

load_dotenv()

#Initialize hugging face
hf_client = InferenceClient(token=os.getenv("HF_API_TOKEN"))

#Zero shot classification model
HF_MODEL = "facebook/bart-large-mnli"

#Log files
CRISIS_LOG_FILE = "data/crisis_log.jsonl"
DANGEROUS_LOG_FILE = "data/dangerous_topics_log.jsonl"

def log_event(filepath: str, message: str, detected_by: str, reason: str = ""):
    """
    Logs a safety event to a .jsonl file.
    Each line is a separate JSON object.
    """
    os.makedirs("data", exist_ok=True)
    event = {
        "timestamp": datetime.now().isoformat(),
        "detected_by": detected_by,
        "message": message,
        "reason": reason
    }
    with open(filepath, "a") as f: 
        f.write(json.dumps(event) + "\n")
    print(f"[SAFETY LOG] Event logged to {filepath} - detected by: {detected_by}")


#LABEL SETS
#classification for zero shot model

CRISIS_LABELS = [
    "caregiver expressing suicidal thoughts or self harm",
    "caregiver in immediate danger or threatening violence",
    "caregiver expressing complete hopelessness and inability to continue",
    "caregiver asking a normal caregiving question"
]

DANGEROUS_LABELS = [
    "asking about giving medication, pills, or drugs to a patient",
    "asking to stop or change prescribed medical treatment",
    "asking about physically restraining or sedating a patient at home",
    "general caregiving, behavioral, or emotional support question"
]


#confidence threshold
CONFIDENCE_THRESHOLD = 0.70

def hf_detect_crisis(message: str) -> tuple[bool, str]:
    try:
        result = hf_client.zero_shot_classification(
            text=message,
            candidate_labels=CRISIS_LABELS,
            model=HF_MODEL
        )

        # Result is a list of dicts sorted by score descending
        top_label = result[0]["label"]
        top_score = result[0]["score"]

        is_crisis = (
            top_label != "caregiver asking a normal caregiving question"
            and top_score >= CONFIDENCE_THRESHOLD
        )

        reason = f"{top_label} (confidence: {top_score:.0%})"
        return is_crisis, reason

    except Exception as e:
        print(f"[SAFETY WARNING] HF crisis detection failed: {e}")
        return False, "detection failed"


def hf_detect_dangerous_topic(message: str) -> tuple[bool, str]:
    try:
        result = hf_client.zero_shot_classification(
            text=message,
            candidate_labels=DANGEROUS_LABELS,
            model=HF_MODEL
        )

        top_label = result[0]["label"]
        top_score = result[0]["score"]

        is_dangerous = (
            top_label != "general caregiving, behavioral, or emotional support question"
            and top_score >= CONFIDENCE_THRESHOLD
        )

        reason = f"{top_label} (confidence: {top_score:.0%})"
        return is_dangerous, reason

    except Exception as e:
        print(f"[SAFETY WARNING] HF dangerous topic detection failed: {e}")
        return False, "detection failed"

# MAIN SAFETY CHECK

def run_safety_check(message: str) -> dict:
    """
    Runs all safety layers in order.

    Returns:
        {
            "safe": bool,
            "response": str or None,
            "flag": "crisis" | "dangerous" | None
        }

    Layer 1: keyword check   — instant, no API call
    Layer 2: HF zero-shot    — catches subtle cases
    """

    # CRISIS: Layer 1
    if is_crisis_message(message):
        log_event(CRISIS_LOG_FILE, message, detected_by="keyword")
        return {
            "safe": False,
            "response": CRISIS_RESPONSE_TEMPLATE,
            "flag": "crisis"
        }
    # CRISIS: Layer 2
    crisis_detected, crisis_reason = hf_detect_crisis(message)
    if crisis_detected:
        log_event(
            CRISIS_LOG_FILE, message,
            detected_by="huggingface", reason=crisis_reason
        )
        return {
            "safe": False,
            "response": CRISIS_RESPONSE_TEMPLATE,
            "flag": "crisis"
        }
    
    # DANGEROUS TOPIC: Layer 1
    if is_dangerous_topic(message):
        log_event(DANGEROUS_LOG_FILE, message, detected_by="keyword")
        return {
            "safe": False,
            "response": LOW_CONFIDENCE_TEMPLATE,
            "flag": "dangerous"
        }

    # DANGEROUS TOPIC: Layer 2
    dangerous_detected, dangerous_reason = hf_detect_dangerous_topic(message)
    if dangerous_detected:
        log_event(
            DANGEROUS_LOG_FILE, message,
            detected_by="huggingface", reason=dangerous_reason
        )
        return {
            "safe": False,
            "response": LOW_CONFIDENCE_TEMPLATE,
            "flag": "dangerous"
        }
    
    return {"safe": True, "response": None, "flag": None}