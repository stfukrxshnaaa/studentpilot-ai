"""
Helper utilities for StudyPilot AI.
Includes date math, badge HTML generators, and college motivational quotes.
"""

from datetime import datetime, date
import random
from typing import Dict, Any

MOTIVATIONAL_QUOTES = [
    ("“Success is the sum of small efforts, repeated day in and day out.”", "Robert Collier"),
    ("“It always seems impossible until it is done.”", "Nelson Mandela"),
    ("“An investment in knowledge pays the best interest.”", "Benjamin Franklin"),
    ("“You don’t have to be extreme, just consistent.”", "Anonymous"),
    ("“Focus on progress, not perfection.”", "Bill Phillips"),
    ("“The expert in anything was once a beginner.”", "Helen Hayes"),
    ("“Deep work is the superpower of the 21st century.”", "Cal Newport")
]

def get_daily_quote() -> Dict[str, str]:
    """Returns a motivational study tip of the day."""
    quote, author = random.choice(MOTIVATIONAL_QUOTES)
    return {"quote": quote, "author": author}

def format_countdown(target_date_str: str) -> str:
    """Returns human-readable countdown e.g., '14 days left' or 'Tomorrow!'"""
    if not target_date_str:
        return "No date set"
    try:
        target = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        today = date.today()
        diff = (target - today).days
        if diff < 0:
            return f"{abs(diff)} days ago"
        elif diff == 0:
            return "🔥 Today!"
        elif diff == 1:
            return "⏳ Tomorrow!"
        else:
            return f"⏳ {diff} days left"
    except Exception:
        return target_date_str

def get_difficulty_badge(difficulty: str) -> str:
    diff_lower = difficulty.lower()
    if diff_lower == "easy":
        return f'<span class="badge-pill badge-easy">🟢 {difficulty}</span>'
    elif diff_lower == "hard":
        return f'<span class="badge-pill badge-hard">🔴 {difficulty}</span>'
    else:
        return f'<span class="badge-pill badge-medium">🟡 {difficulty}</span>'

def get_status_badge(status: str) -> str:
    st_lower = status.lower()
    if "master" in st_lower:
        return f'<span class="badge-pill badge-mastered">✅ {status}</span>'
    elif "progress" in st_lower:
        return f'<span class="badge-pill badge-progress">⚡ {status}</span>'
    else:
        return f'<span class="badge-pill badge-notstarted">⏳ {status}</span>'
