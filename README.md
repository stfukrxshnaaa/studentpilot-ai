# 🚀 StudyPilot AI

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.20+-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

**Your Intelligent College Study Assistant, Exam Strategist, and Active Recall Copilot.**

*Built for college students to master complex coursework, plan realistic study schedules, take AI-graded mock quizzes, and track academic velocity.*

[Features](#-core-features) • [Quickstart](#-quickstart--installation) • [Screenshots](#-ui-tour--screenshots) • [Architecture](#-architecture--design) • [Configuration](#-configuration--llm-providers) • [Test Report](#-test-suite--quality-assurance)

</div>

---

## 🌟 Overview

College students often face an overwhelming volume of lectures, problem sets, and impending exams. **StudyPilot AI** bridges the gap between chaotic syllabus lists and structured academic success.

Unlike static study apps or shallow mockups, **StudyPilot AI** is a fully functional, production-ready system backed by persistent SQLite storage, dynamic scheduling algorithms, multi-perspective AI explanations, interactive MCQ quiz arenas with score tracking, spaced-repetition flashcards, a built-in Pomodoro timer, and Plotly analytics.

> 🔒 **Security First:** Zero hardcoded API keys. All keys are loaded safely from environment variables or configured dynamically in session memory.  
> 💡 **Graceful Offline Mode:** Runs smoothly with or without live API keys thanks to an integrated collegiate heuristic engine.

---

## ✨ Core Features

| Feature | Description |
|---|---|
| **📊 Student Dashboard** | Real-time KPI cards (focus hours, topics mastered, streak, quiz average), upcoming exam countdowns, subject progress bars, and recent activity feed. |
| **📚 Subjects & Topics** | Full CRUD for courses and topics. Tag difficulty (Easy, Medium, Hard), priority (Low, Medium, High), estimated study hours, and syllabus focus notes. |
| **📅 AI Study Planner** | Calculates feasible day-by-day study schedules based on available daily hours and target exam dates. Includes rest days, revision buffers, and interactive checklists. |
| **🤖 AI Tutor & Explainer** | Multi-mode explanations: *Academic In-Depth*, *ELI5 Analogy*, *Cheat Sheet*, *Case Study*, and *Common Exam Pitfalls*. Supports LaTeX math and code blocks. |
| **📝 AI Quiz Arena** | Dynamic MCQ generation with 4 choices per question, instant evaluation, detailed explanations for every option, letter grades (A+ to F), and performance badges. |
| **🗂️ Flashcard Deck & SRS** | Active recall cards with interactive flip animation and Spaced Repetition (Again, Hard, Good, Easy) scheduling intervals. |
| **✍️ Smart Notes** | Rich Markdown note editor with live preview, tagging, and AI assistance (summarize, extract glossaries, generate practice exam questions, format). |
| **⏱️ Pomodoro Focus Timer** | Focus (25m / 50m) and Break (5m / 15m) intervals with audio chime alerts. Completed sessions automatically log to SQLite study history. |
| **📈 Learning Analytics** | Interactive Plotly visualizations: topic mastery donut charts, 14-day study hours bar chart, course curriculum stacked bars, and quiz score trajectory. |
| **🔍 Search & Filter** | Instant full-text search across topics and notes with multi-criteria filters for status, difficulty, priority, and subject. |
| **📤 Multi-Format Exports** | Export study plans to Markdown (`.md`), styled printable HTML, or CSV. Export notes to Markdown or JSON. Export flashcards to Anki CSV. |
| **🌙 Modern Dark / Light UI** | Clean, responsive UI with custom CSS, glassmorphism headers, badge pills, and student-focused typography. |

---

## 📸 UI Tour & Screenshots

```
+--------------------------------------------------------------------------------------------------+
|  🚀 STUDYPILOT AI       [🟢 LIVE LLM: GEMINI]                                   [🌙 Dark | ☀️ Light]|
+--------------------------------------------------------------------------------------------------+
|  📊 Dashboard         |  👋 Welcome back, Scholar!                                               |
|  📚 Subjects & Topics |  "Focus on progress, not perfection." — Bill Phillips                    |
|  📅 Study Planner     +--------------------------------------------------------------------------+
|  🤖 AI Tutor          |  ⏱️ 8.5h Focus  | 🎯 4/12 Topics | 🔥 7 Days Streak | 📝 88% Quiz Avg    |
|  📝 AI Quiz Arena     +--------------------------------------------------------------------------+
|  🗂️ Flashcards        |  ⏳ UPCOMING EXAMS                  |  📊 CURRICULUM PROGRESS            |
|  ✍️ Smart Notes       |  - CS201 Algorithms: ⏳ 21 days left |  - CS201: [██████████░░░] 60%      |
|  ⏱️ Pomodoro Timer    |  - CS305 Operating Systems: 35 days |  - CS305: [██████░░░░░░] 40%      |
|  📈 Analytics         +--------------------------------------------------------------------------+
|  ⚙️ Settings & API    |  ⚡ QUICK ACTIONS: [⏱️ Pomodoro] [🤖 Ask AI] [📝 Quiz] [📅 Study Plan]   |
+--------------------------------------------------------------------------------------------------+
```

### Flashcard Flip Experience
```
+-------------------------------------------------------------+
| Card 2 of 6  |  Subject: Operating Systems                  |
| [====================================>                    ] |
|                                                             |
|   +-----------------------------------------------------+   |
|   |         ❓ FRONT: CONCEPT / PROMPT                  |   |
|   |                                                     |   |
|   |   What are the 4 Coffman conditions for Deadlock?   |   |
|   +-----------------------------------------------------+   |
|                                                             |
|                 [ 🔄 Flip Flashcard ]                       |
|                                                             |
|   Rate recall: [🔴 Again]  [🟡 Hard]  [🟢 Good]  [🔵 Easy]  |
+-------------------------------------------------------------+
```

---

## 🛠️ Architecture & Design

StudyPilot AI is structured into decoupled, modular layers for maintainability and scalability:

```
studypilot-ai/
│
├── app.py                      # Main Streamlit application entrypoint & routing
├── config.py                   # Environment loader, constants, and provider configuration
├── requirements.txt            # Python dependencies
├── .env.example                # Example configuration template (no secrets committed)
├── .gitignore                  # Git exclusions (SQLite db, secrets, pycache)
├── LICENSE                     # MIT License
├── README.md                   # Project documentation
├── TEST_REPORT.md              # Automated test verification results
│
├── database/                   # SQLite Persistent Data Layer
│   ├── __init__.py             # Exports CRUD functions
│   ├── schema.sql              # Clean SQLite DDL schema with foreign keys
│   ├── db_manager.py           # Context-managed connections and transactional CRUD
│   └── seed_data.py            # Realistic starter college courses and sample data
│
├── services/                   # Business Logic & AI Engines
│   ├── __init__.py
│   ├── ai_service.py           # Multi-provider LLM client (Gemini, OpenAI, Groq) + Demo Fallback
│   ├── study_planner.py        # Algorithmic scheduling engine with buffer & pace analysis
│   ├── quiz_service.py         # Exam grading, letter grades, explanations, and metrics
│   ├── flashcard_service.py    # Spaced repetition interval calculator (SM-2 simplified)
│   └── export_service.py       # Exporters to Markdown, printable HTML, CSV, and JSON
│
├── components/                 # Streamlit UI Views
│   ├── __init__.py
│   ├── dashboard_view.py       # Student dashboard & KPI overview
│   ├── subjects_view.py        # Subjects & Topics CRUD with multi-filter search
│   ├── planner_view.py         # Study plan generator, session checklist, and exports
│   ├── ai_tutor_view.py        # Multi-perspective topic explainer
│   ├── quiz_view.py            # Interactive MCQ quiz arena & history
│   ├── flashcards_view.py      # Interactive flip-card deck & spaced repetition
│   ├── notes_view.py           # Markdown note editor with AI enhancements
│   ├── pomodoro_view.py        # Focus timer with chime and session logging
│   ├── analytics_view.py       # Interactive Plotly progress charts
│   └── settings_view.py        # Live API key settings and database manager
│
├── utils/                      # UI Helpers & Styling
│   ├── __init__.py
│   ├── theme.py                # Responsive CSS styles for Dark & Light modes
│   └── helpers.py              # Date countdowns, badge HTML, and motivational quotes
│
└── tests/                      # Automated Test Suite (32 tests)
    ├── __init__.py
    ├── test_db.py              # SQLite CRUD & schema tests
    ├── test_planner.py         # Scheduling algorithm tests
    ├── test_quiz.py            # Quiz grading and scoring tests
    ├── test_ai_fallback.py     # Offline fallback reliability tests
    ├── test_export.py          # Export service tests
    └── test_e2e_features.py    # Comprehensive 14-feature verification suite
```

---

## ⚡ Quickstart & Installation

Follow these steps to set up and run StudyPilot AI on your local machine:

### 1. Prerequisites
- **Python 3.10+** installed ([python.org](https://www.python.org/downloads/))
- **Git** installed ([git-scm.com](https://git-scm.com/))

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/studypilot-ai.git
cd studypilot-ai
```

### 3. Create and Activate Virtual Environment (Recommended)
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. (Optional) Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` to include your Google Gemini, OpenAI, or Groq API key:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```
> *Note: If you skip this step, StudyPilot AI will run automatically in **Local Demo Mode** with built-in collegiate heuristics.*

### 6. Launch StudyPilot AI
```bash
python -m streamlit run app.py
```
Open your browser to: **`http://localhost:8501`**

---

## ⚙️ Configuration & LLM Providers

StudyPilot AI supports 3 live LLM providers and 1 local offline fallback:

| Provider | Supported Models | Environment Variable | Where to Get Key |
|---|---|---|---|
| **Google Gemini** *(Default)* | `gemini-1.5-flash`, `gemini-2.0-flash` | `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/) (Free tier available) |
| **OpenAI** | `gpt-4o-mini`, `gpt-4o` | `OPENAI_API_KEY` | [OpenAI Platform](https://platform.openai.com/) |
| **Groq** | `llama-3.3-70b-versatile` | `GROQ_API_KEY` | [Groq Console](https://console.groq.com/) |
| **Local Demo Engine** | Built-in Heuristics | *None required* | Works 100% offline out-of-the-box |

### Dynamic Key Configuration in UI
You can also configure or update your API keys live inside the app under **⚙️ Settings & API** tab without restarting the server!

---

## 🧪 Test Suite & Quality Assurance

StudyPilot AI includes a comprehensive test suite covering database operations, study planning mathematics, quiz evaluation, fallback engines, exports, and end-to-end features.

To run all 32 automated tests:
```bash
python -m unittest discover -s tests -v
```

Expected output:
```text
test_flashcards_generator_fallback ... ok
test_notes_enhancement_fallback ... ok
test_quiz_generator_fallback ... ok
test_topic_explanation_fallback ... ok
test_quiz_and_metrics ... ok
test_study_plan_creation_and_completion ... ok
test_subject_crud ... ok
test_topic_crud ... ok
test_feature_1_student_dashboard_metrics ... ok
test_feature_2_add_subjects_and_topics ... ok
test_feature_3_create_study_plans ... ok
test_feature_4_ai_generated_explanations ... ok
test_feature_5_ai_quiz_generator ... ok
test_feature_6_mcq_quiz_score_tracking ... ok
test_feature_7_flashcard_generator ... ok
test_feature_8_notes_section ... ok
test_feature_9_progress_tracking_metrics ... ok
test_feature_10_pomodoro_timer ... ok
test_feature_11_search_filter_subjects_and_topics ... ok
test_feature_12_export_study_plan_and_notes ... ok
test_feature_13_dark_light_theme_ui ... ok
test_feature_14_responsive_layout_and_demo_mode ... ok
...
Ran 32 tests in 0.210s

OK
```
See [`TEST_REPORT.md`](TEST_REPORT.md) for full execution logs and coverage details.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
<b>StudyPilot AI</b> — Designed with ❤️ for college students worldwide.
</div>
