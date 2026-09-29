# Database package initialization
from .db_manager import (
    init_db,
    add_subject, get_subjects, get_subject, update_subject, delete_subject,
    add_topic, get_topics, get_topic, update_topic, update_topic_status, delete_topic,
    create_study_plan, add_study_plan_items, get_study_plans, get_study_plan, get_study_plan_items,
    toggle_plan_item_completion, delete_study_plan,
    record_quiz_attempt, get_quiz_attempts, get_quiz_attempt,
    add_flashcard, get_flashcards, update_flashcard_review, delete_flashcard,
    add_note, get_notes, get_note, update_note, delete_note,
    log_study_session, get_study_sessions, get_study_metrics
)
