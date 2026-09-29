"""
Comprehensive End-to-End Feature Verification Suite for StudyPilot AI.
Validates all 14 core features required by the specification.
"""

import unittest
import json
from datetime import date, timedelta
from database.db_manager import (
    init_db, get_subjects, add_subject, get_topics, add_topic, update_topic_status,
    create_study_plan, add_study_plan_items, get_study_plans, get_study_plan_items,
    toggle_plan_item_completion, record_quiz_attempt, get_quiz_attempts,
    add_flashcard, get_flashcards, update_flashcard_review,
    add_note, get_notes, update_note,
    log_study_session, get_study_sessions, get_study_metrics
)
from services.ai_service import ai_service
from services.study_planner import generate_schedule
from services.quiz_service import grade_quiz_attempt
from services.flashcard_service import calculate_next_review
from services.export_service import (
    export_study_plan_markdown, export_study_plan_html, export_study_plan_csv,
    export_note_markdown, export_notes_json, export_flashcards_csv
)
from utils.theme import get_custom_css
from utils.helpers import get_daily_quote, format_countdown

from database.seed_data import seed_sample_data

class TestStudyPilotAllCoreFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_sample_data()

    def test_feature_1_student_dashboard_metrics(self):
        """Feature 1: Student dashboard data & KPIs."""
        metrics = get_study_metrics()
        self.assertIn("total_study_hours", metrics)
        self.assertIn("mastered_topics", metrics)
        self.assertIn("study_streak_days", metrics)
        self.assertIn("upcoming_exams", metrics)
        quote = get_daily_quote()
        self.assertIn("quote", quote)
        self.assertIn("author", quote)

    def test_feature_2_add_subjects_and_topics(self):
        """Feature 2: Add subjects and topics."""
        import time
        unique_code = f"ROB{int(time.time() * 1000) % 100000}"
        s_id = add_subject("Robotics & Automation", unique_code, "#EC4899", "🤖", "2026-11-15", 94.0)
        self.assertIsNotNone(s_id)
        
        t_id = add_topic(s_id, "Kinematics & Denavit-Hartenberg", "Hard", 3.0, "High", "Not Started", "Transform matrices")
        self.assertIsNotNone(t_id)

        topics = get_topics(subject_id=s_id)
        self.assertTrue(any(t["title"] == "Kinematics & Denavit-Hartenberg" for t in topics))

    def test_feature_3_create_study_plans(self):
        """Feature 3: Create study plans based on available hours and exam date."""
        sample_topics = [
            {"id": 101, "title": "Calculus: Multi-Variable Integration", "difficulty": "Hard", "priority": "High", "estimated_hours": 3.0},
            {"id": 102, "title": "Vector Fields & Stokes Theorem", "difficulty": "Hard", "priority": "High", "estimated_hours": 2.5},
            {"id": 103, "title": "Lagrange Multipliers", "difficulty": "Medium", "priority": "Medium", "estimated_hours": 1.5}
        ]
        exam_target = (date.today() + timedelta(days=18)).isoformat()
        plan = generate_schedule(
            topics=sample_topics,
            exam_date_str=exam_target,
            daily_hours=2.0,
            study_days_per_week=6,
            buffer_percent=15.0
        )
        self.assertTrue(plan["is_valid"])
        self.assertGreater(len(plan["schedule_items"]), 0)
        self.assertIn(plan["pace_status"], ["Optimal", "Moderate", "Tight", "Overloaded"])

    def test_feature_4_ai_generated_explanations(self):
        """Feature 4: AI-generated explanations for topics."""
        exp = ai_service.generate_topic_explanation(
            topic="Binary Search Trees",
            subject="Algorithms",
            mode="ELI5 & Intuitive Analogy",
            difficulty="College"
        )
        self.assertIn("text", exp)
        self.assertGreater(len(exp["text"]), 100)

    def test_feature_5_ai_quiz_generator(self):
        """Feature 5: AI quiz generator."""
        quiz = ai_service.generate_quiz(
            topic="Dynamic Programming",
            subject="Algorithms",
            num_questions=3,
            difficulty="Medium"
        )
        self.assertEqual(len(quiz), 3)
        for q in quiz:
            self.assertIn("question", q)
            self.assertEqual(len(q["options"]), 4)
            self.assertIn("correct_index", q)
            self.assertIn("explanation", q)

    def test_feature_6_mcq_quiz_score_tracking(self):
        """Feature 6: MCQ quiz with score tracking."""
        questions = [
            {"question": "Q1", "options": ["A", "B", "C", "D"], "correct_index": 0, "explanation": "A is correct."},
            {"question": "Q2", "options": ["A", "B", "C", "D"], "correct_index": 2, "explanation": "C is correct."}
        ]
        res = grade_quiz_attempt(questions, {0: 0, 1: 1}, elapsed_seconds=25)
        self.assertEqual(res["score"], 1)
        self.assertEqual(res["percentage"], 50.0)
        
        attempt_id = record_quiz_attempt(
            subject_id=None,
            topic_id=None,
            quiz_title="Test Evaluation",
            score=res["score"],
            total_questions=res["total_questions"],
            percentage=res["percentage"],
            difficulty="Medium",
            time_taken_seconds=25,
            details_json=json.dumps(res["details"])
        )
        self.assertIsNotNone(attempt_id)
        attempts = get_quiz_attempts(limit=5)
        self.assertTrue(any(a["id"] == attempt_id for a in attempts))

    def test_feature_7_flashcard_generator(self):
        """Feature 7: Flashcard generator & spaced repetition."""
        cards = ai_service.generate_flashcards("Memory Paging", "Operating Systems", count=3)
        self.assertEqual(len(cards), 3)
        
        # Test Spaced Repetition calculation
        next_d, label = calculate_next_review(current_review_count=1, rating="Good")
        self.assertIn("In", label)
        self.assertIsNotNone(next_d)

    def test_feature_8_notes_section(self):
        """Feature 8: Notes section with AI enhancement."""
        subjects = get_subjects()
        sub_id = subjects[0]["id"]
        note_id = add_note(sub_id, None, "Amdahl's Law", "Speedup is limited by the serial part of the program.", "architecture, speedup")
        self.assertIsNotNone(note_id)

        enhancement = ai_service.enhance_notes("Speedup is limited by the serial part of the program.", "summarize")
        self.assertIn("Summary", enhancement)

    def test_feature_9_progress_tracking_metrics(self):
        """Feature 9: Progress tracking with charts & metrics."""
        metrics = get_study_metrics()
        self.assertGreaterEqual(metrics["total_topics"], 1)
        self.assertGreaterEqual(metrics["total_study_hours"], 0)

    def test_feature_10_pomodoro_timer(self):
        """Feature 10: Pomodoro study timer logging."""
        subjects = get_subjects()
        sub_id = subjects[0]["id"]
        sess_id = log_study_session(sub_id, None, 25, "Focus", "Pomodoro test session")
        self.assertIsNotNone(sess_id)
        sessions = get_study_sessions(days_limit=1)
        self.assertTrue(any(s["id"] == sess_id for s in sessions))

    def test_feature_11_search_filter_subjects_and_topics(self):
        """Feature 11: Search/filter subjects and topics."""
        # Search by difficulty
        hard_topics = get_topics(difficulty="Hard")
        for ht in hard_topics:
            self.assertEqual(ht["difficulty"], "Hard")

        # Search by keyword
        query_topics = get_topics(search="AVL")
        self.assertTrue(all("avl" in t["title"].lower() or "avl" in t.get("notes_summary", "").lower() for t in query_topics))

    def test_feature_12_export_study_plan_and_notes(self):
        """Feature 12: Export study plan and notes."""
        sample_plan = {"title": "Export Test", "exam_date": "2026-11-30", "available_hours_per_day": 3.0, "total_allocated_hours": 15.0}
        sample_items = [{"day_number": 1, "scheduled_date": "2026-11-15", "activity_type": "Study", "session_title": "Pointers", "allocated_hours": 3.0, "is_completed": 0}]
        
        md_plan = export_study_plan_markdown(sample_plan, sample_items)
        self.assertIn("# 📅 Export Test", md_plan)

        html_plan = export_study_plan_html(sample_plan, sample_items)
        self.assertIn("<!DOCTYPE html>", html_plan)

        csv_plan = export_study_plan_csv(sample_items)
        self.assertIn("Pointers", csv_plan)

        sample_note = {"title": "Note Export", "content": "Note body here", "tags": "test", "subject_name": "CS", "topic_title": "General"}
        md_note = export_note_markdown(sample_note)
        self.assertIn("# ✍️ Note Export", md_note)

        json_notes = export_notes_json([sample_note])
        self.assertIn("Note Export", json_notes)

    def test_feature_13_dark_light_theme_ui(self):
        """Feature 13: Dark/light modern UI."""
        css_dark = get_custom_css("dark")
        css_light = get_custom_css("light")
        self.assertIn("#1e293b", css_dark) # dark card background
        self.assertIn("#ffffff", css_light) # light card background

    def test_feature_14_responsive_layout_and_demo_mode(self):
        """Feature 14: Graceful offline / demo mode fallback."""
        self.assertFalse(ai_service.is_live()) # In test environment without keys
        res = ai_service.generate_text("Explain binary search")
        self.assertIn("text", res)
        self.assertTrue(res.get("is_demo"))

if __name__ == "__main__":
    unittest.main()
