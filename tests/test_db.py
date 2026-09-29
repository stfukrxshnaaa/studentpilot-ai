"""
Unit tests for Database Manager in StudyPilot AI.
"""

import unittest
import sqlite3
import os
import tempfile
from pathlib import Path

# Override DB path for isolated testing
from database.db_manager import (
    init_db, add_subject, get_subjects, get_subject, update_subject, delete_subject,
    add_topic, get_topics, get_topic, update_topic, update_topic_status, delete_topic,
    create_study_plan, add_study_plan_items, get_study_plans, get_study_plan, get_study_plan_items,
    toggle_plan_item_completion, record_quiz_attempt, get_quiz_attempts,
    add_flashcard, get_flashcards, update_flashcard_review,
    add_note, get_notes, update_note, delete_note,
    log_study_session, get_study_sessions, get_study_metrics
)

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        init_db()

    def test_subject_crud(self):
        s_id = add_subject("Test Physics", "PHYS101", "#FF0000", "🔭", "2026-12-01", 92.0)
        self.assertIsNotNone(s_id)
        
        subj = get_subject(s_id)
        self.assertEqual(subj["name"], "Test Physics")
        self.assertEqual(subj["code"], "PHYS101")
        
        updated = update_subject(s_id, "Advanced Physics", "PHYS101", "#00FF00", "⚛️", "2026-12-05", 95.0)
        self.assertTrue(updated)
        
        subj_up = get_subject(s_id)
        self.assertEqual(subj_up["name"], "Advanced Physics")
        
        # Cleanup
        delete_subject(s_id)
        self.assertIsNone(get_subject(s_id))

    def test_topic_crud(self):
        s_id = add_subject("Algorithms Test", "ALGO99", "#4F46E5", "💻")
        t_id = add_topic(s_id, "Binary Search", "Easy", 1.5, "High", "Not Started", "Logarithmic search")
        self.assertIsNotNone(t_id)

        topic = get_topic(t_id)
        self.assertEqual(topic["title"], "Binary Search")
        self.assertEqual(topic["status"], "Not Started")

        update_topic_status(t_id, "Mastered")
        self.assertEqual(get_topic(t_id)["status"], "Mastered")

        # Cleanup
        delete_topic(t_id)
        delete_subject(s_id)

    def test_study_plan_creation_and_completion(self):
        s_id = add_subject("Chemistry Test", "CHEM10", "#059669", "🧪")
        t_id = add_topic(s_id, "Thermodynamics", "Medium", 2.0)

        plan_id = create_study_plan(s_id, "Midterm Sprint", "2026-11-20", 2.0, 4.0)
        self.assertIsNotNone(plan_id)

        items = [
            {"topic_id": t_id, "scheduled_date": "2026-11-01", "day_number": 1, "session_title": "Enthalpy Intro", "allocated_hours": 2.0, "activity_type": "Study"}
        ]
        add_study_plan_items(plan_id, items)

        fetched_items = get_study_plan_items(plan_id)
        self.assertEqual(len(fetched_items), 1)
        self.assertEqual(fetched_items[0]["is_completed"], 0)

        # Toggle completion
        toggle_plan_item_completion(fetched_items[0]["id"], True)
        updated_items = get_study_plan_items(plan_id)
        self.assertEqual(updated_items[0]["is_completed"], 1)

        # Cleanup
        delete_subject(s_id)

    def test_quiz_and_metrics(self):
        init_db()
        metrics_before = get_study_metrics()
        self.assertIn("total_study_hours", metrics_before)
        self.assertIn("avg_quiz_score", metrics_before)

        # Log session
        log_study_session(None, None, 30, "Focus", "Deep study test")
        metrics_after = get_study_metrics()
        self.assertGreaterEqual(metrics_after["total_study_hours"], metrics_before["total_study_hours"])

if __name__ == "__main__":
    unittest.main()
