"""
Database manager for StudyPilot AI.
Provides SQLite connection management and clean CRUD abstractions.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from config import DB_PATH, BASE_DIR

SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"

@contextmanager
def get_connection():
    """Creates a configured SQLite connection context that automatically commits and closes."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
    finally:
        conn.close()

def init_db() -> None:
    """Initializes the database schema if tables do not exist."""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    with get_connection() as conn:
        conn.executescript(schema_sql)
        conn.commit()

# ========================================================
# SUBJECTS CRUD
# ========================================================

def add_subject(name: str, code: str, color: str = "#4F46E5", icon: str = "📚", 
                target_date: Optional[str] = None, target_score: float = 90.0) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO subjects (name, code, color, icon, target_date, target_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name.strip(), code.strip().upper(), color, icon, target_date, target_score))
        conn.commit()
        return cur.lastrowid

def get_subjects() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM subjects ORDER BY name ASC")
        rows = cur.fetchall()
        return [dict(row) for row in rows]

def get_subject(subject_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,))
        row = cur.fetchone()
        return dict(row) if row else None

def update_subject(subject_id: int, name: str, code: str, color: str, icon: str, 
                   target_date: Optional[str], target_score: float) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE subjects 
            SET name = ?, code = ?, color = ?, icon = ?, target_date = ?, target_score = ?
            WHERE id = ?
        """, (name.strip(), code.strip().upper(), color, icon, target_date, target_score, subject_id))
        conn.commit()
        return cur.rowcount > 0

def delete_subject(subject_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        conn.commit()
        return cur.rowcount > 0

# ========================================================
# TOPICS CRUD
# ========================================================

def add_topic(subject_id: int, title: str, difficulty: str = "Medium", 
              estimated_hours: float = 1.5, priority: str = "Medium", 
              status: str = "Not Started", notes_summary: str = "") -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO topics (subject_id, title, difficulty, estimated_hours, priority, status, notes_summary)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (subject_id, title.strip(), difficulty, estimated_hours, priority, status, notes_summary))
        conn.commit()
        return cur.lastrowid

def get_topics(subject_id: Optional[int] = None, status: Optional[str] = None, 
               difficulty: Optional[str] = None, priority: Optional[str] = None, 
               search: Optional[str] = None) -> List[Dict[str, Any]]:
    query = """
        SELECT t.*, s.name as subject_name, s.code as subject_code, s.color as subject_color, s.icon as subject_icon
        FROM topics t
        JOIN subjects s ON t.subject_id = s.id
        WHERE 1=1
    """
    params = []
    if subject_id:
        query += " AND t.subject_id = ?"
        params.append(subject_id)
    if status and status != "All":
        query += " AND t.status = ?"
        params.append(status)
    if difficulty and difficulty != "All":
        query += " AND t.difficulty = ?"
        params.append(difficulty)
    if priority and priority != "All":
        query += " AND t.priority = ?"
        params.append(priority)
    if search:
        query += " AND (t.title LIKE ? OR t.notes_summary LIKE ? OR s.name LIKE ?)"
        s_param = f"%{search.strip()}%"
        params.extend([s_param, s_param, s_param])
    
    query += " ORDER BY t.priority DESC, t.id ASC"
    
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        return [dict(row) for row in rows]

def get_topic(topic_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT t.*, s.name as subject_name, s.code as subject_code, s.color as subject_color
            FROM topics t
            JOIN subjects s ON t.subject_id = s.id
            WHERE t.id = ?
        """, (topic_id,))
        row = cur.fetchone()
        return dict(row) if row else None

def update_topic(topic_id: int, title: str, difficulty: str, estimated_hours: float, 
                 priority: str, status: str, notes_summary: str = "") -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE topics 
            SET title = ?, difficulty = ?, estimated_hours = ?, priority = ?, status = ?, 
                notes_summary = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (title.strip(), difficulty, estimated_hours, priority, status, notes_summary, topic_id))
        conn.commit()
        return cur.rowcount > 0

def update_topic_status(topic_id: int, status: str) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE topics 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (status, topic_id))
        conn.commit()
        return cur.rowcount > 0

def delete_topic(topic_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
        conn.commit()
        return cur.rowcount > 0

# ========================================================
# STUDY PLANS CRUD
# ========================================================

def create_study_plan(subject_id: Optional[int], title: str, exam_date: str, 
                      available_hours_per_day: float, total_allocated_hours: float = 0) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO study_plans (subject_id, title, exam_date, available_hours_per_day, total_allocated_hours)
            VALUES (?, ?, ?, ?, ?)
        """, (subject_id, title.strip(), exam_date, available_hours_per_day, total_allocated_hours))
        conn.commit()
        return cur.lastrowid

def add_study_plan_items(plan_id: int, items: List[Dict[str, Any]]) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        for it in items:
            cur.execute("""
                INSERT INTO study_plan_items 
                (plan_id, topic_id, scheduled_date, day_number, session_title, allocated_hours, activity_type, is_completed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (plan_id, it.get("topic_id"), it["scheduled_date"], it["day_number"], 
                  it["session_title"], it["allocated_hours"], it.get("activity_type", "Study"), 0))
        conn.commit()

def get_study_plans(subject_id: Optional[int] = None) -> List[Dict[str, Any]]:
    query = """
        SELECT p.*, s.name as subject_name, s.code as subject_code, s.color as subject_color,
               COUNT(i.id) as total_items,
               SUM(CASE WHEN i.is_completed = 1 THEN 1 ELSE 0 END) as completed_items
        FROM study_plans p
        LEFT JOIN subjects s ON p.subject_id = s.id
        LEFT JOIN study_plan_items i ON p.id = i.plan_id
        WHERE 1=1
    """
    params = []
    if subject_id:
        query += " AND p.subject_id = ?"
        params.append(subject_id)
    
    query += " GROUP BY p.id ORDER BY p.created_at DESC"
    
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        return [dict(row) for row in rows]

def get_study_plan(plan_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.*, s.name as subject_name, s.code as subject_code, s.color as subject_color
            FROM study_plans p
            LEFT JOIN subjects s ON p.subject_id = s.id
            WHERE p.id = ?
        """, (plan_id,))
        row = cur.fetchone()
        return dict(row) if row else None

def get_study_plan_items(plan_id: int) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT i.*, t.title as topic_title, t.difficulty as topic_difficulty
            FROM study_plan_items i
            LEFT JOIN topics t ON i.topic_id = t.id
            WHERE i.plan_id = ?
            ORDER BY i.scheduled_date ASC, i.day_number ASC, i.id ASC
        """, (plan_id,))
        rows = cur.fetchall()
        return [dict(row) for row in rows]

def toggle_plan_item_completion(item_id: int, is_completed: bool) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        completed_val = 1 if is_completed else 0
        completed_at = datetime.now().isoformat() if is_completed else None
        cur.execute("""
            UPDATE study_plan_items 
            SET is_completed = ?, completed_at = ?
            WHERE id = ?
        """, (completed_val, completed_at, item_id))
        conn.commit()
        return cur.rowcount > 0

def delete_study_plan(plan_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM study_plans WHERE id = ?", (plan_id,))
        conn.commit()
        return cur.rowcount > 0

# ========================================================
# QUIZ ATTEMPTS CRUD
# ========================================================

def record_quiz_attempt(subject_id: Optional[int], topic_id: Optional[int], quiz_title: str,
                        score: int, total_questions: int, percentage: float, 
                        difficulty: str = "Medium", time_taken_seconds: int = 0,
                        details_json: str = "[]") -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO quiz_attempts 
            (subject_id, topic_id, quiz_title, score, total_questions, percentage, difficulty, time_taken_seconds, details_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (subject_id, topic_id, quiz_title.strip(), score, total_questions, percentage, difficulty, time_taken_seconds, details_json))
        conn.commit()
        return cur.lastrowid

def get_quiz_attempts(subject_id: Optional[int] = None, limit: int = 50) -> List[Dict[str, Any]]:
    query = """
        SELECT q.*, s.name as subject_name, s.code as subject_code, s.color as subject_color,
               t.title as topic_title
        FROM quiz_attempts q
        LEFT JOIN subjects s ON q.subject_id = s.id
        LEFT JOIN topics t ON q.topic_id = t.id
        WHERE 1=1
    """
    params = []
    if subject_id:
        query += " AND q.subject_id = ?"
        params.append(subject_id)
    
    query += " ORDER BY q.created_at DESC LIMIT ?"
    params.append(limit)
    
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        return [dict(row) for row in rows]

def get_quiz_attempt(attempt_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT q.*, s.name as subject_name, t.title as topic_title
            FROM quiz_attempts q
            LEFT JOIN subjects s ON q.subject_id = s.id
            LEFT JOIN topics t ON q.topic_id = t.id
            WHERE q.id = ?
        """, (attempt_id,))
        row = cur.fetchone()
        return dict(row) if row else None

# ========================================================
# FLASHCARDS CRUD
# ========================================================

def add_flashcard(subject_id: int, topic_id: Optional[int], question: str, 
                  answer: str, difficulty_rating: str = "Good") -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO flashcards (subject_id, topic_id, question, answer, difficulty_rating, next_review_date)
            VALUES (?, ?, ?, ?, ?, date('now'))
        """, (subject_id, topic_id, question.strip(), answer.strip(), difficulty_rating))
        conn.commit()
        return cur.lastrowid

def get_flashcards(subject_id: Optional[int] = None, topic_id: Optional[int] = None) -> List[Dict[str, Any]]:
    query = """
        SELECT f.*, s.name as subject_name, s.code as subject_code, s.color as subject_color,
               t.title as topic_title
        FROM flashcards f
        JOIN subjects s ON f.subject_id = s.id
        LEFT JOIN topics t ON f.topic_id = t.id
        WHERE 1=1
    """
    params = []
    if subject_id:
        query += " AND f.subject_id = ?"
        params.append(subject_id)
    if topic_id:
        query += " AND f.topic_id = ?"
        params.append(topic_id)
    
    query += " ORDER BY f.id DESC"
    
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        return [dict(row) for row in rows]

def update_flashcard_review(flashcard_id: int, rating: str, next_review_date: str) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE flashcards 
            SET difficulty_rating = ?, 
                review_count = review_count + 1, 
                last_reviewed_at = CURRENT_TIMESTAMP,
                next_review_date = ?
            WHERE id = ?
        """, (rating, next_review_date, flashcard_id))
        conn.commit()
        return cur.rowcount > 0

def delete_flashcard(flashcard_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM flashcards WHERE id = ?", (flashcard_id,))
        conn.commit()
        return cur.rowcount > 0

# ========================================================
# NOTES CRUD
# ========================================================

def add_note(subject_id: int, topic_id: Optional[int], title: str, 
             content: str, tags: str = "") -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO notes (subject_id, topic_id, title, content, tags)
            VALUES (?, ?, ?, ?, ?)
        """, (subject_id, topic_id, title.strip(), content.strip(), tags.strip()))
        conn.commit()
        return cur.lastrowid

def get_notes(subject_id: Optional[int] = None, topic_id: Optional[int] = None, 
              search: Optional[str] = None) -> List[Dict[str, Any]]:
    query = """
        SELECT n.*, s.name as subject_name, s.code as subject_code, s.color as subject_color,
               t.title as topic_title
        FROM notes n
        JOIN subjects s ON n.subject_id = s.id
        LEFT JOIN topics t ON n.topic_id = t.id
        WHERE 1=1
    """
    params = []
    if subject_id:
        query += " AND n.subject_id = ?"
        params.append(subject_id)
    if topic_id:
        query += " AND n.topic_id = ?"
        params.append(topic_id)
    if search:
        query += " AND (n.title LIKE ? OR n.content LIKE ? OR n.tags LIKE ?)"
        s_param = f"%{search.strip()}%"
        params.extend([s_param, s_param, s_param])
    
    query += " ORDER BY n.updated_at DESC"
    
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        return [dict(row) for row in rows]

def get_note(note_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT n.*, s.name as subject_name, s.code as subject_code, t.title as topic_title
            FROM notes n
            JOIN subjects s ON n.subject_id = s.id
            LEFT JOIN topics t ON n.topic_id = t.id
            WHERE n.id = ?
        """, (note_id,))
        row = cur.fetchone()
        return dict(row) if row else None

def update_note(note_id: int, title: str, content: str, tags: str = "", 
                subject_id: Optional[int] = None, topic_id: Optional[int] = None) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        query = """
            UPDATE notes 
            SET title = ?, content = ?, tags = ?, updated_at = CURRENT_TIMESTAMP
        """
        params = [title.strip(), content.strip(), tags.strip()]
        if subject_id is not None:
            query += ", subject_id = ?"
            params.append(subject_id)
        if topic_id is not None:
            query += ", topic_id = ?"
            params.append(topic_id)
        query += " WHERE id = ?"
        params.append(note_id)
        
        cur.execute(query, params)
        conn.commit()
        return cur.rowcount > 0

def delete_note(note_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        return cur.rowcount > 0

# ========================================================
# STUDY SESSIONS & METRICS
# ========================================================

def log_study_session(subject_id: Optional[int], topic_id: Optional[int], 
                      duration_minutes: int, session_type: str = "Focus", 
                      notes: str = "") -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO study_sessions (subject_id, topic_id, duration_minutes, session_type, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (subject_id, topic_id, duration_minutes, session_type, notes.strip()))
        conn.commit()
        return cur.lastrowid

def get_study_sessions(days_limit: int = 30) -> List[Dict[str, Any]]:
    query = """
        SELECT sess.*, s.name as subject_name, s.code as subject_code, s.color as subject_color,
               t.title as topic_title
        FROM study_sessions sess
        LEFT JOIN subjects s ON sess.subject_id = s.id
        LEFT JOIN topics t ON sess.topic_id = t.id
        WHERE sess.logged_at >= datetime('now', ?)
        ORDER BY sess.logged_at DESC
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, (f"-{days_limit} days",))
        rows = cur.fetchall()
        return [dict(row) for row in rows]

def get_study_metrics() -> Dict[str, Any]:
    """Calculates overall KPIs for dashboard and analytics."""
    with get_connection() as conn:
        cur = conn.cursor()
        
        # 1. Total study hours
        cur.execute("""
            SELECT COALESCE(SUM(duration_minutes), 0) / 60.0 as total_hours 
            FROM study_sessions 
            WHERE session_type = 'Focus'
        """)
        total_hours = round(cur.fetchone()["total_hours"], 1)
        
        # 2. Topic mastery counts
        cur.execute("""
            SELECT 
                COUNT(*) as total_topics,
                SUM(CASE WHEN status = 'Mastered' THEN 1 ELSE 0 END) as mastered_topics,
                SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress_topics,
                SUM(CASE WHEN status = 'Not Started' THEN 1 ELSE 0 END) as not_started_topics
            FROM topics
        """)
        topic_stats = dict(cur.fetchone())
        
        # 3. Average quiz score
        cur.execute("""
            SELECT 
                COUNT(*) as total_attempts,
                COALESCE(AVG(percentage), 0) as avg_score 
            FROM quiz_attempts
        """)
        quiz_stats = dict(cur.fetchone())
        
        # 4. Total flashcards count
        cur.execute("SELECT COUNT(*) as total_flashcards FROM flashcards")
        flashcards_count = cur.fetchone()["total_flashcards"]
        
        # 5. Total notes count
        cur.execute("SELECT COUNT(*) as total_notes FROM notes")
        notes_count = cur.fetchone()["total_notes"]
        
        # 6. Active subjects count
        cur.execute("SELECT COUNT(*) as total_subjects FROM subjects")
        subjects_count = cur.fetchone()["total_subjects"]
        
        # 7. Consecutive study streak (days with at least 1 session)
        cur.execute("""
            SELECT DISTINCT date(logged_at) as session_date 
            FROM study_sessions 
            ORDER BY session_date DESC
        """)
        session_dates = [row["session_date"] for row in cur.fetchall()]
        
        streak = 0
        if session_dates:
            today_str = datetime.now().date().isoformat()
            yesterday_str = (datetime.now().date() - timedelta(days=1)).isoformat()
            
            # If the user studied today or yesterday, count streak backwards
            if session_dates[0] in (today_str, yesterday_str):
                curr = datetime.strptime(session_dates[0], "%Y-%m-%d").date()
                streak = 1
                for d_str in session_dates[1:]:
                    d = datetime.strptime(d_str, "%Y-%m-%d").date()
                    if curr - d == timedelta(days=1):
                        streak += 1
                        curr = d
                    else:
                        break
        
        # 8. Upcoming exams countdown
        cur.execute("""
            SELECT name, code, color, target_date, target_score 
            FROM subjects 
            WHERE target_date IS NOT NULL AND target_date != '' AND target_date >= date('now')
            ORDER BY target_date ASC
        """)
        upcoming_exams = [dict(row) for row in cur.fetchall()]
        
        return {
            "total_study_hours": total_hours,
            "total_topics": topic_stats["total_topics"] or 0,
            "mastered_topics": topic_stats["mastered_topics"] or 0,
            "in_progress_topics": topic_stats["in_progress_topics"] or 0,
            "not_started_topics": topic_stats["not_started_topics"] or 0,
            "quiz_attempts": quiz_stats["total_attempts"] or 0,
            "avg_quiz_score": round(quiz_stats["avg_score"], 1),
            "flashcards_count": flashcards_count,
            "notes_count": notes_count,
            "subjects_count": subjects_count,
            "study_streak_days": streak,
            "upcoming_exams": upcoming_exams
        }
