"""
Study Planner algorithm and scheduling engine for StudyPilot AI.
Calculates realistic day-by-day study schedules based on hours, deadlines, and priorities.
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

def generate_schedule(
    topics: List[Dict[str, Any]],
    exam_date_str: str,
    daily_hours: float = 2.0,
    study_days_per_week: int = 6,
    buffer_percent: float = 15.0,
    include_quizzes: bool = True
) -> Dict[str, Any]:
    """
    Computes a realistic, structured day-by-day study schedule.
    """
    today = date.today()
    try:
        exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d").date()
    except Exception:
        exam_date = today + timedelta(days=14)

    days_remaining = (exam_date - today).days
    if days_remaining <= 0:
        return {
            "error": "Exam date must be in the future! Please select a date at least tomorrow.",
            "is_valid": False
        }

    # Total potential study days (excluding rest days based on study_days_per_week)
    rest_day_interval = 7 if study_days_per_week == 6 else (4 if study_days_per_week == 5 else 999)
    
    # Priority sorting: High > Medium > Low, then Hard > Medium > Easy
    priority_map = {"High": 3, "Medium": 2, "Low": 1}
    diff_map = {"Hard": 3, "Medium": 2, "Easy": 1}
    
    sorted_topics = sorted(
        topics,
        key=lambda t: (
            priority_map.get(t.get("priority", "Medium"), 2),
            diff_map.get(t.get("difficulty", "Medium"), 2),
            t.get("estimated_hours", 1.5)
        ),
        reverse=True
    )
    
    total_required_hours = sum(t.get("estimated_hours", 1.5) for t in sorted_topics)
    total_potential_hours = days_remaining * daily_hours * (study_days_per_week / 7.0)
    
    # Reserve buffer hours for review
    buffer_hours = total_potential_hours * (buffer_percent / 100.0)
    usable_hours = max(0.5, total_potential_hours - buffer_hours)
    
    # Feasibility analysis
    if total_required_hours <= usable_hours * 0.75:
        pace_status = "Optimal"
        pace_color = "#10B981" # Green
        pace_message = "Comfortable pace! You have ample buffer time for deep revision and rest."
    elif total_required_hours <= usable_hours:
        pace_status = "Moderate"
        pace_color = "#3B82F6" # Blue
        pace_message = "Balanced pace. Stick to your daily hour targets to cover all topics."
    elif total_required_hours <= total_potential_hours:
        pace_status = "Tight"
        pace_color = "#F59E0B" # Amber
        pace_message = "Tight schedule. Minimizes buffer days; requires consistent focus."
    else:
        pace_status = "Overloaded"
        pace_color = "#EF4444" # Red
        pace_message = f"Over capacity! You need ~{round(total_required_hours, 1)} hrs, but only ~{round(total_potential_hours, 1)} hrs are available. Increase daily study hours or focus on High priority topics."

    # Build daily schedule items
    schedule_items = []
    current_day = 1
    current_cal_date = today + timedelta(days=1)
    
    topic_queue = list(sorted_topics)
    completed_topics_in_plan = 0
    days_since_last_review = 0
    
    while current_cal_date < exam_date and (topic_queue or days_since_last_review >= 3):
        # Check if today is a rest day
        if current_day % rest_day_interval == 0 and study_days_per_week < 7:
            schedule_items.append({
                "day_number": current_day,
                "scheduled_date": current_cal_date.isoformat(),
                "topic_id": None,
                "topic_title": "Rest & Mental Recovery",
                "session_title": "Active Recovery & Light Flashcard Review",
                "allocated_hours": min(1.0, daily_hours),
                "activity_type": "Review",
                "is_completed": 0
            })
            current_cal_date += timedelta(days=1)
            current_day += 1
            days_since_last_review = 0
            continue
            
        # Review & Quiz milestone every 4 days or when queue is empty
        if include_quizzes and (days_since_last_review >= 4 or (not topic_queue and completed_topics_in_plan > 0)):
            schedule_items.append({
                "day_number": current_day,
                "scheduled_date": current_cal_date.isoformat(),
                "topic_id": None,
                "topic_title": "Checkpoint Review",
                "session_title": "Mid-Sprint MCQ Quiz & Flashcard Spaced Repetition",
                "allocated_hours": daily_hours,
                "activity_type": "Quiz",
                "is_completed": 0
            })
            current_cal_date += timedelta(days=1)
            current_day += 1
            days_since_last_review = 0
            if not topic_queue:
                break
            continue

        if topic_queue:
            t = topic_queue.pop(0)
            hours_needed = t.get("estimated_hours", 1.5)
            
            # If hours needed exceed daily hours, split into theory & practice
            if hours_needed > daily_hours:
                schedule_items.append({
                    "day_number": current_day,
                    "scheduled_date": current_cal_date.isoformat(),
                    "topic_id": t["id"],
                    "topic_title": t["title"],
                    "session_title": f"Theory & Mechanics: {t['title']}",
                    "allocated_hours": daily_hours,
                    "activity_type": "Study",
                    "is_completed": 0
                })
                # Re-queue remainder
                remainder = round(hours_needed - daily_hours, 1)
                if remainder > 0:
                    t_rem = dict(t)
                    t_rem["estimated_hours"] = remainder
                    t_rem["title"] = f"Practice & Problem Sets: {t['title']}"
                    topic_queue.insert(0, t_rem)
            else:
                schedule_items.append({
                    "day_number": current_day,
                    "scheduled_date": current_cal_date.isoformat(),
                    "topic_id": t["id"],
                    "topic_title": t["title"],
                    "session_title": f"Deep Focus: {t['title']}",
                    "allocated_hours": hours_needed,
                    "activity_type": "Study",
                    "is_completed": 0
                })
                
            completed_topics_in_plan += 1
            days_since_last_review += 1
            current_cal_date += timedelta(days=1)
            current_day += 1
        else:
            break

    # Add final 1 or 2 days for final revision & mock exam before the exam
    if (exam_date - current_cal_date).days >= 1:
        schedule_items.append({
            "day_number": current_day,
            "scheduled_date": (exam_date - timedelta(days=1)).isoformat(),
            "topic_id": None,
            "topic_title": "Final Exam Simulation",
            "session_title": "Full-Length Timed Mock Exam & Formula Sheet Audit",
            "allocated_hours": daily_hours,
            "activity_type": "Quiz",
            "is_completed": 0
        })

    total_allocated_hours = sum(item["allocated_hours"] for item in schedule_items)

    return {
        "is_valid": True,
        "days_remaining": days_remaining,
        "total_required_hours": round(total_required_hours, 1),
        "total_potential_hours": round(total_potential_hours, 1),
        "total_allocated_hours": round(total_allocated_hours, 1),
        "buffer_hours": round(buffer_hours, 1),
        "pace_status": pace_status,
        "pace_color": pace_color,
        "pace_message": pace_message,
        "schedule_items": schedule_items
    }
