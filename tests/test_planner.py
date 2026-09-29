"""
Unit tests for Study Planner scheduling algorithm in StudyPilot AI.
"""

import unittest
from datetime import date, timedelta
from services.study_planner import generate_schedule

class TestStudyPlanner(unittest.TestCase):
    def setUp(self):
        self.sample_topics = [
            {"id": 1, "title": "Topic A (Hard)", "difficulty": "Hard", "priority": "High", "estimated_hours": 3.0},
            {"id": 2, "title": "Topic B (Medium)", "difficulty": "Medium", "priority": "Medium", "estimated_hours": 2.0},
            {"id": 3, "title": "Topic C (Easy)", "difficulty": "Easy", "priority": "Low", "estimated_hours": 1.0}
        ]

    def test_future_date_schedule(self):
        target_exam = (date.today() + timedelta(days=14)).isoformat()
        res = generate_schedule(
            topics=self.sample_topics,
            exam_date_str=target_exam,
            daily_hours=2.0,
            study_days_per_week=6,
            buffer_percent=15.0
        )
        self.assertTrue(res["is_valid"])
        self.assertGreater(len(res["schedule_items"]), 0)
        self.assertIn("pace_status", res)
        self.assertIn(res["pace_status"], ["Optimal", "Moderate", "Tight", "Overloaded"])

    def test_past_date_rejected(self):
        target_exam = (date.today() - timedelta(days=2)).isoformat()
        res = generate_schedule(
            topics=self.sample_topics,
            exam_date_str=target_exam,
            daily_hours=2.0
        )
        self.assertFalse(res["is_valid"])
        self.assertIn("error", res)

    def test_topic_priority_ordering(self):
        target_exam = (date.today() + timedelta(days=20)).isoformat()
        res = generate_schedule(
            topics=self.sample_topics,
            exam_date_str=target_exam,
            daily_hours=2.0
        )
        self.assertTrue(res["is_valid"])
        first_study_item = next(it for it in res["schedule_items"] if it.get("topic_id"))
        # Highest priority and hardest topic should be scheduled first
        self.assertEqual(first_study_item["topic_id"], 1)

if __name__ == "__main__":
    unittest.main()
