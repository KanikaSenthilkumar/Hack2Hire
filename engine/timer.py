def calculate_time_score(time_taken: int, time_limit: int) -> float:
    ratio = time_taken / time_limit
    if ratio <= 0.5:   return 10.0
    elif ratio <= 0.8: return 8.0
    elif ratio <= 1.0: return 6.0
    else: return max(0.0, 6.0 - (ratio - 1.0) * 10)