"""
Settings and API Configuration View for StudyPilot AI.
Allows configuring API keys dynamically in the UI without hardcoding,
testing connectivity, and loading/resetting demo starter database records.
"""

import streamlit as st
import os
import sqlite3
from config import DB_PATH, DEFAULT_DB_PATH
from services.ai_service import ai_service
from database.seed_data import seed_sample_data
from database.db_manager import init_db

def render_settings_view():
    st.title("⚙️ Settings & System Configuration")
    st.markdown("Configure your AI model providers, manage persistent SQLite storage, and customize application preferences.")

    tab_api, tab_db, tab_about = st.tabs(["🔑 LLM API Configuration", "💾 Database & Sample Data", "ℹ️ About StudyPilot AI"])

    # ========================================================
    # TAB 1: API CONFIGURATION
    # ========================================================
    with tab_api:
        st.subheader("🤖 AI Provider Settings")
        st.markdown("""
        StudyPilot AI supports **Google Gemini**, **OpenAI**, and **Groq**.
        You can provide API keys via a `.env` file or directly enter them below.
        
        > **Privacy Note:** Keys entered here are stored strictly in your current local session memory and are **never logged, exposed, or transmitted to any third party**.
        """)

        # Current Status Indicator
        active_prov = ai_service.provider
        is_live = ai_service.is_live()

        if is_live:
            st.success(f"🟢 **Live Mode Active**: Connected via **{active_prov.upper()}**")
        else:
            st.info("🟡 **Local Demo Engine Active**: Using built-in collegiate heuristics. Enter an API key below to unlock live real-time LLM inference.")

        with st.form("api_config_form"):
            prov_choice = st.selectbox(
                "Preferred LLM Provider",
                ["Auto-Detect Best Available", "Google Gemini", "OpenAI", "Groq"],
                index=0
            )

            st.markdown("#### Provider API Keys")
            gemini_k = st.text_input("Google Gemini API Key", value=ai_service.gemini_key, type="password", placeholder="AIzaSy...")
            openai_k = st.text_input("OpenAI API Key", value=ai_service.openai_key, type="password", placeholder="sk-proj-...")
            groq_k = st.text_input("Groq API Key", value=ai_service.groq_key, type="password", placeholder="gsk_...")

            save_btn = st.form_submit_button("💾 Save Configuration & Apply", type="primary", use_container_width=True)

        if save_btn:
            p_mapped = "auto"
            if "Gemini" in prov_choice:
                p_mapped = "gemini"
            elif "OpenAI" in prov_choice:
                p_mapped = "openai"
            elif "Groq" in prov_choice:
                p_mapped = "groq"

            ai_service.refresh_keys(
                provider=p_mapped if p_mapped != "auto" else None,
                gemini_key=gemini_k,
                openai_key=openai_k,
                groq_key=groq_k
            )
            st.toast("Configuration updated!")
            st.rerun()

        st.divider()

        # Test Connection Button
        st.subheader("🧪 Test AI Connectivity")
        if st.button("Run Diagnostic Test Query", use_container_width=True):
            with st.spinner("Testing AI generation pipeline..."):
                test_res = ai_service.generate_text(
                    prompt="Define Newton's Second Law of Motion in one sentence.",
                    system_prompt="Be concise."
                )
                st.markdown(f"**Engine Response ({test_res['source']}):**")
                st.markdown(f"> {test_res['text']}")
                if test_res.get("is_demo"):
                    st.caption("ℹ️ Response produced by built-in fallback engine. Provide a valid API key above for live cloud LLM results.")
                else:
                    st.success("✅ Live LLM connection verified successfully!")

    # ========================================================
    # TAB 2: DATABASE MANAGEMENT
    # ========================================================
    with tab_db:
        st.subheader("💾 SQLite Database Management")
        st.markdown(f"- **Database Path:** `{DB_PATH}`")
        
        db_size_kb = 0
        if os.path.exists(DB_PATH):
            db_size_kb = round(os.path.getsize(DB_PATH) / 1024, 2)
        st.markdown(f"- **Current File Size:** `{db_size_kb} KB`")

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        st.subheader("📦 Starter Demo Data")
        st.markdown("Populate your database with rich college starter courses (Data Structures & Algorithms, Operating Systems, Cell Biology), flashcards, notes, and study logs.")

        d_col1, d_col2 = st.columns(2)
        with d_col1:
            if st.button("🌱 Load College Starter Data", type="primary", use_container_width=True):
                seed_sample_data(reset_first=False)
                st.success("Starter data successfully loaded!")
                st.rerun()

        with d_col2:
            if st.button("⚠️ Reset & Clear All Database Records", use_container_width=True):
                if os.path.exists(DB_PATH):
                    try:
                        conn = sqlite3.connect(str(DB_PATH))
                        cur = conn.cursor()
                        cur.execute("PRAGMA foreign_keys = OFF;")
                        tables = ["subjects", "topics", "study_plans", "study_plan_items", "quiz_attempts", "flashcards", "notes", "study_sessions"]
                        for t in tables:
                            cur.execute(f"DELETE FROM {t};")
                        conn.commit()
                        conn.close()
                        init_db()
                        st.warning("Database records have been cleared.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error resetting database: {e}")

    # ========================================================
    # TAB 3: ABOUT
    # ========================================================
    with tab_about:
        st.subheader("🚀 StudyPilot AI v1.0.0")
        st.markdown("""
        **StudyPilot AI** is an intelligent, open-source college study assistant designed to empower university students
        with personalized study schedules, active recall flashcards, AI tutoring, and rigorous performance analytics.
        
        ### Key Architectural Highlights:
        - **100% Offline-Capable**: Built-in collegiate heuristic fallback ensures full app functionality even with zero API keys.
        - **Persistent SQLite Storage**: Foreign-key enforced transactional schema ensures all your notes, schedules, and quizzes persist across reloads.
        - **Export Ready**: Instant export to Markdown, printable HTML, and CSV.
        - **Zero Hardcoded Secrets**: Secure environment variable loading via `.env` and dynamic session configuration.
        """)
