from models.interview import DifficultyLevel

CONSECUTIVE_LOW_LIMIT = 3
UPGRADE_THRESHOLD = 7.5
DOWNGRADE_THRESHOLD = 4.5

def get_next_difficulty(current_difficulty: DifficultyLevel, composite_score: float) -> DifficultyLevel:
    if composite_score >= UPGRADE_THRESHOLD:
        if current_difficulty == DifficultyLevel.EASY:
            return DifficultyLevel.MEDIUM
        elif current_difficulty == DifficultyLevel.MEDIUM:
            return DifficultyLevel.HARD
        return DifficultyLevel.HARD
    elif composite_score <= DOWNGRADE_THRESHOLD:
        if current_difficulty == DifficultyLevel.HARD:
            return DifficultyLevel.MEDIUM
        elif current_difficulty == DifficultyLevel.MEDIUM:
            return DifficultyLevel.EASY
        return DifficultyLevel.EASY
    return current_difficulty

def should_terminate(composite_score: float, consecutive_low_scores: int):
    if consecutive_low_scores >= CONSECUTIVE_LOW_LIMIT:
        return True, f"Performance below threshold for {CONSECUTIVE_LOW_LIMIT} consecutive questions"
    return False, ""

def update_consecutive_low(current_count: int, composite_score: float) -> int:
    if composite_score < DOWNGRADE_THRESHOLD:
        return current_count + 1
    return 0