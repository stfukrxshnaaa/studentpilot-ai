"""
StudyPilot AI - Main Application Entrypoint.
A production-grade AI-powered study assistant for college students.
"""

import streamlit as st
import os
from config import APP_TITLE, APP_ICON, APP_SUBTITLE, APP_VERSION
from database.db_manager import init_db, get_subjects, get_study_metrics
from database.seed_data import seed_sample_data
from services.ai_service import ai_service
from utils.theme import get_custom_css
from components import (
    render_dashboard,
    render_subjects_view,
    render_planner_view,
    render_ai_tutor,
    render_quiz_view,
    render_flashcards_view,
    render_notes_view,
    render_pomodoro_view,
    render_analytics_view,
    render_settings_view
)

# 1. Page Configuration
st.set_page_config(
    page_title=f"{APP_TITLE} - College Study Copilot",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Database Auto-Initialization
init_db()
if not get_subjects():
    # Automatically seed starter demo data on clean run so the student sees immediate value
    seed_sample_data()

# 3. Theme & Session State Setup
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "dark"

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Dashboard"

def navigate_to(page_name: str):
    """Router helper passed to components for programmatic navigation."""
    st.session_state["current_page"] = page_name
    st.rerun()

# 4. Inject Dynamic CSS
st.markdown(get_custom_css(st.session_state["theme_mode"]), unsafe_allow_html=True)

# 5. Sidebar Navigation
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 10px 0 16px 0;">
        <span style="font-size: 42px;">{APP_ICON}</span>
        <h2 style="margin: 4px 0 0 0; font-weight: 800; font-size: 22px;">{APP_TITLE}</h2>
        <div style="font-size: 11px; opacity: 0.7; letter-spacing: 0.5px;">COLLEGE STUDY COPILOT</div>
    </div>
    """, unsafe_allow_html=True)

    # Provider Mode Badge
    if ai_service.is_live():
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 6px 10px; font-size: 11px; font-weight: 700; color: #10b981; text-align: center; margin-bottom: 12px;">
            🟢 LIVE LLM: {ai_service.provider.upper()}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 6px 10px; font-size: 11px; font-weight: 700; color: #f59e0b; text-align: center; margin-bottom: 12px;">
            🟡 LOCAL DEMO MODE
        </div>
        """, unsafe_allow_html=True)

    # Navigation Menu
    pages = [
        ("📊 Dashboard", "Dashboard"),
        ("📚 Subjects & Topics", "Subjects & Topics"),
        ("📅 Study Planner", "Study Planner"),
        ("🤖 AI Tutor", "AI Tutor"),
        ("📝 AI Quiz Arena", "AI Quiz Arena"),
        ("🗂️ Flashcards", "Flashcards"),
        ("✍️ Smart Notes", "Smart Notes"),
        ("⏱️ Pomodoro Timer", "Pomodoro Timer"),
        ("📈 Progress & Analytics", "Progress & Analytics"),
        ("⚙️ Settings & API", "Settings & API")
    ]

    page_labels = [p[0] for p in pages]
    page_keys = [p[1] for p in pages]

    # Find current selected index
    curr_idx = 0
    if st.session_state["current_page"] in page_keys:
        curr_idx = page_keys.index(st.session_state["current_page"])

    selected_label = st.radio(
        "Navigation",
        options=page_labels,
        index=curr_idx,
        label_visibility="collapsed"
    )
    
    # Update page if changed via radio
    chosen_page_key = page_keys[page_labels.index(selected_label)]
    if chosen_page_key != st.session_state["current_page"]:
        st.session_state["current_page"] = chosen_page_key
        st.rerun()

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    st.divider()

    # Theme Toggle & Footer Stats
    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        st.caption("Theme Mode")
    with col_t2:
        new_theme = st.selectbox(
            "Theme",
            options=["dark", "light"],
            index=0 if st.session_state["theme_mode"] == "dark" else 1,
            label_visibility="collapsed",
            format_func=lambda x: "🌙 Dark" if x == "dark" else "☀️ Light"
        )
        if new_theme != st.session_state["theme_mode"]:
            st.session_state["theme_mode"] = new_theme
            st.rerun()

    # Quick metrics in sidebar footer
    sb_metrics = get_study_metrics()
    st.markdown(f"""
    <div style="font-size: 11px; opacity: 0.65; margin-top: 10px; line-height: 1.6;">
        🔥 Streak: <strong>{sb_metrics['study_streak_days']} days</strong><br/>
        ⏱️ Study Hours: <strong>{sb_metrics['total_study_hours']}h</strong><br/>
        🚀 Version {APP_VERSION}
    </div>
    """, unsafe_allow_html=True)

# 6. Page Router Dispatch
active_page = st.session_state["current_page"]

if active_page == "Dashboard":
    render_dashboard(navigate_to)
elif active_page == "Subjects & Topics":
    render_subjects_view()
elif active_page == "Study Planner":
    render_planner_view()
elif active_page == "AI Tutor":
    render_ai_tutor(navigate_to)
elif active_page == "AI Quiz Arena":
    render_quiz_view()
elif active_page == "Flashcards":
    render_flashcards_view()
elif active_page == "Smart Notes":
    render_notes_view()
elif active_page == "Pomodoro Timer":
    render_pomodoro_view()
elif active_page == "Progress & Analytics":
    render_analytics_view()
elif active_page == "Settings & API":
    render_settings_view()
else:
    render_dashboard(navigate_to)
