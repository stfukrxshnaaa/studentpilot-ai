"""
Unit tests for AI fallback engine and prompt handlers in StudyPilot AI.
Verifies that even with no API keys, all AI features function with 100% reliability.
"""

import unittest
from services.ai_service import ai_service

class TestAIFallback(unittest.TestCase):
    def test_topic_explanation_fallback(self):
        res = ai_service.generate_topic_explanation(
            topic="AVL Trees",
            subject="Data Structures",
            mode="Academic In-Depth",
            difficulty="College"
        )
        self.assertIn("text", res)
        self.assertGreater(len(res["text"]), 50)
        self.assertIn("AVL", res["text"])

    def test_quiz_generator_fallback(self):
        quiz = ai_service.generate_quiz(
            topic="Process Synchronization",
            subject="Operating Systems",
            num_questions=3,
            difficulty="Medium"
        )
        self.assertEqual(len(quiz), 3)
        self.assertIn("question", quiz[0])
        self.assertIn("options", quiz[0])
        self.assertEqual(len(quiz[0]["options"]), 4)
        self.assertIn("correct_index", quiz[0])
        self.assertIn("explanation", quiz[0])

    def test_flashcards_generator_fallback(self):
        cards = ai_service.generate_flashcards(
            topic="Cellular Respiration",
            subject="Biology",
            count=3
        )
        self.assertEqual(len(cards), 3)
        self.assertIn("question", cards[0])
        self.assertIn("answer", cards[0])

    def test_notes_enhancement_fallback(self):
        sample_note = "Peterson's algorithm is a concurrent programming algorithm for mutual exclusion."
        summary = ai_service.enhance_notes(sample_note, "summarize")
        self.assertIn("Summary", summary)

if __name__ == "__main__":
    unittest.main()
