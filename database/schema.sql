-- ========================================================
-- StudyPilot AI - SQLite Schema
-- ========================================================

PRAGMA foreign_keys = ON;

-- 1. Subjects
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT NOT NULL UNIQUE,
    color TEXT DEFAULT '#4F46E5',
    icon TEXT DEFAULT '📚',
    target_date TEXT,
    target_score REAL DEFAULT 90.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Topics
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    difficulty TEXT DEFAULT 'Medium', -- 'Easy', 'Medium', 'Hard'
    estimated_hours REAL DEFAULT 1.5,
    priority TEXT DEFAULT 'Medium',   -- 'Low', 'Medium', 'High'
    status TEXT DEFAULT 'Not Started', -- 'Not Started', 'In Progress', 'Mastered'
    notes_summary TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- 3. Study Plans
CREATE TABLE IF NOT EXISTS study_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER,
    title TEXT NOT NULL,
    exam_date TEXT NOT NULL,
    available_hours_per_day REAL NOT NULL,
    total_allocated_hours REAL DEFAULT 0,
    status TEXT DEFAULT 'Active', -- 'Active', 'Completed', 'Archived'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE SET NULL
);

-- 4. Study Plan Items (Scheduled daily sessions)
CREATE TABLE IF NOT EXISTS study_plan_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    topic_id INTEGER,
    scheduled_date TEXT NOT NULL,
    day_number INTEGER NOT NULL,
    session_title TEXT NOT NULL,
    allocated_hours REAL NOT NULL,
    activity_type TEXT DEFAULT 'Study', -- 'Study', 'Review', 'Quiz', 'Practice'
    is_completed INTEGER DEFAULT 0,     -- 0 = False, 1 = True
    completed_at TIMESTAMP,
    FOREIGN KEY(plan_id) REFERENCES study_plans(id) ON DELETE CASCADE,
    FOREIGN KEY(topic_id) REFERENCES topics(id) ON DELETE SET NULL
);

-- 5. Quiz Attempts
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER,
    topic_id INTEGER,
    quiz_title TEXT NOT NULL,
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    percentage REAL NOT NULL,
    difficulty TEXT DEFAULT 'Medium',
    time_taken_seconds INTEGER DEFAULT 0,
    details_json TEXT, -- stores array of questions, choices, user answers & explanations
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE SET NULL,
    FOREIGN KEY(topic_id) REFERENCES topics(id) ON DELETE SET NULL
);

-- 6. Flashcards
CREATE TABLE IF NOT EXISTS flashcards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    topic_id INTEGER,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    difficulty_rating TEXT DEFAULT 'Good', -- 'Again', 'Hard', 'Good', 'Easy'
    review_count INTEGER DEFAULT 0,
    last_reviewed_at TIMESTAMP,
    next_review_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY(topic_id) REFERENCES topics(id) ON DELETE SET NULL
);

-- 7. Notes
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    topic_id INTEGER,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY(topic_id) REFERENCES topics(id) ON DELETE SET NULL
);

-- 8. Study Sessions (Pomodoro & Time tracker)
CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER,
    topic_id INTEGER,
    duration_minutes INTEGER NOT NULL,
    session_type TEXT DEFAULT 'Focus', -- 'Focus', 'Short Break', 'Long Break'
    notes TEXT DEFAULT '',
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE SET NULL,
    FOREIGN KEY(topic_id) REFERENCES topics(id) ON DELETE SET NULL
);

-- Helpful Indices for performance
CREATE INDEX IF NOT EXISTS idx_topics_subject ON topics(subject_id);
CREATE INDEX IF NOT EXISTS idx_plan_items_plan ON study_plan_items(plan_id);
CREATE INDEX IF NOT EXISTS idx_notes_subject ON notes(subject_id);
CREATE INDEX IF NOT EXISTS idx_flashcards_subject ON flashcards(subject_id);
CREATE INDEX IF NOT EXISTS idx_sessions_logged ON study_sessions(logged_at);
CREATE INDEX IF NOT EXISTS idx_quizzes_created ON quiz_attempts(created_at);
