"""
Unit tests for Export Service in StudyPilot AI.
"""

import unittest
from services.export_service import (
    export_study_plan_markdown, export_study_plan_html, export_study_plan_csv,
    export_note_markdown, export_notes_json, export_flashcards_csv
)

class TestExportService(unittest.TestCase):
    def setUp(self):
        self.sample_plan = {
            "title": "Finals Sprint",
            "exam_date": "2026-12-01",
            "available_hours_per_day": 2.5,
            "total_allocated_hours": 10.0
        }
        self.sample_items = [
            {"day_number": 1, "scheduled_date": "2026-11-20", "activity_type": "Study", "session_title": "Graph Traversal", "allocated_hours": 2.5, "is_completed": 1}
        ]

    def test_plan_markdown_export(self):
        md = export_study_plan_markdown(self.sample_plan, self.sample_items)
        self.assertIn("# 📅 Finals Sprint", md)
        self.assertIn("Graph Traversal", md)
        self.assertIn("✅ Done", md)

    def test_plan_html_export(self):
        html = export_study_plan_html(self.sample_plan, self.sample_items)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("Finals Sprint", html)
        self.assertIn("badge-done", html)

    def test_plan_csv_export(self):
        csv_str = export_study_plan_csv(self.sample_items)
        self.assertIn("session_title", csv_str)
        self.assertIn("Graph Traversal", csv_str)

    def test_note_export(self):
        sample_note = {
            "title": "AVL Trees",
            "content": "AVL trees are balanced trees.",
            "tags": "trees, algorithms",
            "subject_name": "CS201",
            "topic_title": "Data Structures"
        }
        note_md = export_note_markdown(sample_note)
        self.assertIn("# ✍️ AVL Trees", note_md)
        self.assertIn("CS201", note_md)

        notes_json = export_notes_json([sample_note])
        self.assertIn('"title": "AVL Trees"', notes_json)

if __name__ == "__main__":
    unittest.main()
