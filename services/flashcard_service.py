"""
Flashcard Service for StudyPilot AI.
Provides spaced repetition scheduling intervals based on user mastery ratings.
"""

from datetime import date, timedelta
from typing import Tuple

def calculate_next_review(current_review_count: int, rating: str) -> Tuple[str, str]:
    """
    Computes next review date based on rating (Again, Hard, Good, Easy)
    using an intuitive Spaced Repetition (SRS) interval formula.
    Returns: (next_date_str, interval_label)
    """
    today = date.today()
    
    if rating == "Again":
        days = 1
        label = "Tomorrow"
    elif rating == "Hard":
        days = 2
        label = "In 2 days"
    elif rating == "Good":
        multiplier = max(1, current_review_count)
        days = min(30, 3 + (multiplier * 2))
        label = f"In {days} days"
    elif rating == "Easy":
        multiplier = max(1, current_review_count)
        days = min(60, 6 + (multiplier * 4))
        label = f"In {days} days"
    else:
        days = 3
        label = "In 3 days"
        
    next_date = today + timedelta(days=days)
    return next_date.isoformat(), label
