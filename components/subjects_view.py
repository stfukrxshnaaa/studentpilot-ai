"""
Subjects & Topics Management View for StudyPilot AI.
Provides full CRUD, search, and multi-criteria filtering for subjects and topics.
"""

import streamlit as st
from datetime import date, timedelta
from database.db_manager import (
    get_subjects, get_subject, add_subject, update_subject, delete_subject,
    get_topics, add_topic, update_topic, update_topic_status, delete_topic
)
from utils.helpers import get_difficulty_badge, get_status_badge, format_countdown

def render_subjects_view():
    st.title("📚 Subjects & Curriculum Management")
    st.markdown("Organize your courses, map out key topics, and monitor your mastery status.")

    tab_topics, tab_subjects = st.tabs(["📝 Topics & Curriculum", "🏛️ Manage Subjects"])

    # ========================================================
    # TAB 1: TOPICS EXPLORER (SEARCH & FILTER)
    # ========================================================
    with tab_topics:
        subjects = get_subjects()
        if not subjects:
            st.warning("⚠️ No subjects created yet. Please create a subject in the 'Manage Subjects' tab or load Demo Data from Settings!")
            return

        # Search and Filter Bar
        st.subheader("🔍 Search & Filter Topics")
        f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns([2, 1.5, 1.2, 1.2, 1.2])
        
        with f_col1:
            search_query = st.text_input("🔎 Search by keyword", placeholder="e.g. Trees, Semaphore, Krebs...", key="topics_search")
            
        with f_col2:
            subj_options = {"All Subjects": None}
            for s in subjects:
                subj_options[f"{s.get('icon', '📚')} {s['name']} ({s['code']})"] = s["id"]
            selected_subj_label = st.selectbox("Filter Subject", list(subj_options.keys()))
            selected_subj_id = subj_options[selected_subj_label]
            
        with f_col3:
            status_filter = st.selectbox("Status", ["All", "Not Started", "In Progress", "Mastered"], key="status_flt")
            
        with f_col4:
            diff_filter = st.selectbox("Difficulty", ["All", "Easy", "Medium", "Hard"], key="diff_flt")
            
        with f_col5:
            prio_filter = st.selectbox("Priority", ["All", "High", "Medium", "Low"], key="prio_flt")

        # Fetch filtered topics
        topics = get_topics(
            subject_id=selected_subj_id,
            status=status_filter,
            difficulty=diff_filter,
            priority=prio_filter,
            search=search_query
        )

        # Quick Add Topic Expander
        with st.expander("➕ Add New Topic", expanded=False):
            with st.form("add_topic_form", clear_on_submit=True):
                at_col1, at_col2 = st.columns([2, 1])
                with at_col1:
                    topic_title = st.text_input("Topic Title*", placeholder="e.g., Dynamic Programming: Knapsack")
                    topic_summary = st.text_area("Key Focus / Syllabus Notes", placeholder="Key theorems, formulas, or lecture topics...")
                with at_col2:
                    target_subj = st.selectbox("Subject*", options=[s["id"] for s in subjects], 
                                               format_func=lambda x: next(s["name"] for s in subjects if s["id"] == x))
                    topic_diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
                    topic_prio = st.selectbox("Priority", ["High", "Medium", "Low"], index=1)
                    topic_hours = st.number_input("Estimated Hours", min_value=0.5, max_value=20.0, value=2.0, step=0.5)
                    topic_status = st.selectbox("Initial Status", ["Not Started", "In Progress", "Mastered"])
                    
                submitted = st.form_submit_button("Save Topic", use_container_width=True)
                if submitted:
                    if not topic_title.strip():
                        st.error("Please enter a topic title.")
                    else:
                        add_topic(target_subj, topic_title, topic_diff, topic_hours, topic_prio, topic_status, topic_summary)
                        st.success(f"Added topic '{topic_title}' successfully!")
                        st.rerun()

        st.markdown(f"**Found {len(topics)} topics matching your filters:**")
        
        if not topics:
            st.info("No topics found matching current criteria. Try adjusting your filters or adding a topic above.")
        else:
            for t in topics:
                with st.container():
                    c_info, c_badges, c_actions = st.columns([3, 2, 2])
                    with c_info:
                        st.markdown(f"### {t['title']}")
                        st.markdown(f"*{t.get('subject_icon', '📚')} {t.get('subject_name')} ({t.get('subject_code')})*")
                        if t.get("notes_summary"):
                            st.caption(t["notes_summary"])
                    with c_badges:
                        st.markdown(f"**Difficulty:** {get_difficulty_badge(t['difficulty'])}", unsafe_allow_html=True)
                        st.markdown(f"**Status:** {get_status_badge(t['status'])}", unsafe_allow_html=True)
                        st.markdown(f"⏱️ **Est:** {t['estimated_hours']} hrs | 🎯 **Priority:** {t['priority']}")
                    with c_actions:
                        # Quick status toggle
                        new_status = st.selectbox(
                            "Update Status", 
                            ["Not Started", "In Progress", "Mastered"], 
                            index=["Not Started", "In Progress", "Mastered"].index(t["status"]),
                            key=f"status_select_{t['id']}"
                        )
                        if new_status != t["status"]:
                            update_topic_status(t["id"], new_status)
                            st.rerun()
                            
                        # Delete button
                        if st.button("🗑️ Delete", key=f"del_topic_{t['id']}"):
                            delete_topic(t["id"])
                            st.toast(f"Deleted {t['title']}")
                            st.rerun()
                    st.divider()

    # ========================================================
    # TAB 2: MANAGE SUBJECTS
    # ========================================================
    with tab_subjects:
        st.subheader("🏛️ Your Academic Subjects")
        
        with st.expander("➕ Add New Subject", expanded=False):
            with st.form("add_subject_form", clear_on_submit=True):
                s1, s2 = st.columns(2)
                with s1:
                    s_name = st.text_input("Course Name*", placeholder="e.g., Computer Networks")
                    s_code = st.text_input("Course Code*", placeholder="e.g., CS401")
                    s_icon = st.selectbox("Subject Icon", ["📚", "💻", "⚙️", "🧬", "📐", "🔬", "📊", "🧪", "🎨", "🏛️"])
                with s2:
                    s_color = st.color_picker("Brand Color", "#4F46E5")
                    s_target_date = st.date_input("Target Exam Date", value=date.today() + timedelta(days=30))
                    s_target_score = st.number_input("Target Score (%)", min_value=50.0, max_value=100.0, value=90.0, step=1.0)
                    
                sub_submit = st.form_submit_button("Create Subject", use_container_width=True)
                if sub_submit:
                    if not s_name.strip() or not s_code.strip():
                        st.error("Course name and course code are required.")
                    else:
                        try:
                            add_subject(s_name, s_code, s_color, s_icon, s_target_date.isoformat(), s_target_score)
                            st.success(f"Added course '{s_name}'!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error adding subject (code might already exist): {e}")

        # List existing subjects
        subjects = get_subjects()
        if subjects:
            for s in subjects:
                topics_in_s = get_topics(subject_id=s["id"])
                countdown_info = format_countdown(s.get("target_date", ""))
                
                with st.expander(f"{s.get('icon', '📚')} {s['name']} ({s['code']}) — {countdown_info}", expanded=False):
                    e_col1, e_col2 = st.columns([2, 1])
                    with e_col1:
                        st.markdown(f"- **Exam Date:** {s.get('target_date', 'Not specified')}")
                        st.markdown(f"- **Target Score:** {s.get('target_score', 90)}%")
                        st.markdown(f"- **Total Topics:** {len(topics_in_s)}")
                    with e_col2:
                        if st.button("🗑️ Delete Subject", key=f"del_subj_{s['id']}"):
                            delete_subject(s["id"])
                            st.toast(f"Deleted {s['name']}")
                            st.rerun()
        else:
            st.info("No subjects found.")
