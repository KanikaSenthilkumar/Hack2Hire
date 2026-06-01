# This logic is already inside adaptive.py
# Keep this file for clarity

TERMINATION_THRESHOLD = 3.0
CONSECUTIVE_LOW_LIMIT = 3

def check_termination(consecutive_low: int, score: float):
    if consecutive_low >= CONSECUTIVE_LOW_LIMIT:
        return True, f"Failed {CONSECUTIVE_LOW_LIMIT} consecutive questions"
    return False, ""