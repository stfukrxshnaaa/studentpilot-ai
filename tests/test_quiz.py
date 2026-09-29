"""
Unit tests for Quiz Service grading and evaluation in StudyPilot AI.
"""

import unittest
from services.quiz_service import grade_quiz_attempt

class TestQuizService(unittest.TestCase):
    def setUp(self):
        self.sample_questions = [
            {
                "question": "What is 2 + 2?",
                "options": ["3", "4", "5", "6"],
                "correct_index": 1,
                "explanation": "2 + 2 equals 4."
            },
            {
                "question": "Which is an asymptotic notation?",
                "options": ["Big-O", "Small-Z", "Micro-X", "Mega-Q"],
                "correct_index": 0,
                "explanation": "Big-O notation describes upper bounds."
            }
        ]

    def test_perfect_score(self):
        user_answers = {0: 1, 1: 0} # All correct
        res = grade_quiz_attempt(self.sample_questions, user_answers, elapsed_seconds=45)
        self.assertEqual(res["score"], 2)
        self.assertEqual(res["total_questions"], 2)
        self.assertEqual(res["percentage"], 100.0)
        self.assertEqual(res["letter_grade"], "A+")

    def test_partial_score(self):
        user_answers = {0: 1, 1: 2} # 1 correct, 1 wrong
        res = grade_quiz_attempt(self.sample_questions, user_answers, elapsed_seconds=30)
        self.assertEqual(res["score"], 1)
        self.assertEqual(res["total_questions"], 2)
        self.assertEqual(res["percentage"], 50.0)
        self.assertEqual(res["letter_grade"], "F")

    def test_empty_quiz(self):
        res = grade_quiz_attempt([], {}, elapsed_seconds=0)
        self.assertEqual(res["score"], 0)
        self.assertEqual(res["letter_grade"], "N/A")

if __name__ == "__main__":
    unittest.main()
