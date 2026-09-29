"""
Quiz Service for StudyPilot AI.
Handles question grading, letter grading, performance analysis, and time tracking.
"""

from typing import Dict, Any, List

def grade_quiz_attempt(
    questions: List[Dict[str, Any]],
    user_selections: Dict[int, int],
    elapsed_seconds: int
) -> Dict[str, Any]:
    """
    Grades user submissions and produces detailed breakdown.
    user_selections is a dict: {question_index: selected_option_index}
    """
    total = len(questions)
    if total == 0:
        return {
            "score": 0,
            "total_questions": 0,
            "percentage": 0.0,
            "letter_grade": "N/A",
            "performance_badge": "N/A",
            "badge_color": "#94A3B8",
            "elapsed_seconds": elapsed_seconds,
            "details": []
        }

    correct_count = 0
    detailed_results = []

    for i, q in enumerate(questions):
        user_idx = user_selections.get(i, -1)
        correct_idx = q.get("correct_index", 0)
        options = q.get("options", [])
        
        is_correct = (user_idx == correct_idx)
        if is_correct:
            correct_count += 1
            
        user_text = options[user_idx] if 0 <= user_idx < len(options) else "Not Answered"
        correct_text = options[correct_idx] if 0 <= correct_idx < len(options) else "N/A"
        
        detailed_results.append({
            "question_index": i + 1,
            "question": q.get("question", ""),
            "options": options,
            "user_index": user_idx,
            "user_answer": user_text,
            "correct_index": correct_idx,
            "correct_answer": correct_text,
            "is_correct": is_correct,
            "explanation": q.get("explanation", "Review core lecture materials.")
        })

    percentage = round((correct_count / total) * 100.0, 1)

    # Letter Grade
    if percentage >= 93:
        letter = "A+"
        badge = "🏆 Mastery Achieved"
        badge_color = "#10B981"
    elif percentage >= 85:
        letter = "A"
        badge = "🌟 Strong Performance"
        badge_color = "#3B82F6"
    elif percentage >= 75:
        letter = "B"
        badge = "👍 Good Understanding"
        badge_color = "#6366F1"
    elif percentage >= 65:
        letter = "C"
        badge = "⚠️ Needs Solidification"
        badge_color = "#F59E0B"
    else:
        letter = "F"
        badge = "🚨 High Priority Review"
        badge_color = "#EF4444"

    return {
        "score": correct_count,
        "total_questions": total,
        "percentage": percentage,
        "letter_grade": letter,
        "performance_badge": badge,
        "badge_color": badge_color,
        "elapsed_seconds": elapsed_seconds,
        "details": detailed_results
    }
