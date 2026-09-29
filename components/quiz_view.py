"""
AI Quiz Arena View for StudyPilot AI.
Generates dynamic MCQ quizzes, provides interactive exam taking, grades submissions,
displays comprehensive explanations, and logs score analytics to SQLite.
"""

import streamlit as st
import time
import json
from database.db_manager import get_subjects, get_topics, record_quiz_attempt, get_quiz_attempts
from services.ai_service import ai_service
from services.quiz_service import grade_quiz_attempt

def render_quiz_view():
    st.title("📝 AI Quiz Arena & Performance Tracker")
    st.markdown("Test your recall and conceptual mastery with AI-generated multiple-choice problem sets.")

    tab_take, tab_history = st.tabs(["🎯 Take a Quiz", "📊 Past Quiz History & Analytics"])

    # ========================================================
    # TAB 1: QUIZ ARENA
    # ========================================================
    with tab_take:
        # Check if quiz is currently in progress
        if "active_quiz" not in st.session_state:
            subjects = get_subjects()
            
            # Setup Card
            st.subheader("⚙️ Configure Quiz Parameters")
            
            c_s, c_t, c_n, c_d = st.columns([1.5, 2, 1, 1])
            with c_s:
                subj_map = {s["name"]: s["id"] for s in subjects} if subjects else {}
                subj_map["General / Cross-Subject"] = None
                
                # Check if navigated with preset from AI tutor
                default_subj_idx = 0
                if "quiz_target_subject" in st.session_state and st.session_state["quiz_target_subject"] in subj_map:
                    default_subj_idx = list(subj_map.keys()).index(st.session_state["quiz_target_subject"])
                selected_subj_name = st.selectbox("Course / Subject", list(subj_map.keys()), index=default_subj_idx)
                selected_subj_id = subj_map[selected_subj_name]

            with c_t:
                default_topic_val = st.session_state.pop("quiz_target_topic", "Binary Search Trees & AVL Balancing")
                if selected_subj_id:
                    topics = get_topics(subject_id=selected_subj_id)
                    topic_choices = [t["title"] for t in topics] + ["➕ Custom Topic..."]
                    ch_top = st.selectbox("Topic", topic_choices)
                    if ch_top == "➕ Custom Topic...":
                        topic_input = st.text_input("Enter Topic", value="Binary Search Trees")
                    else:
                        topic_input = ch_top
                else:
                    topic_input = st.text_input("Enter Topic", value=default_topic_val)

            with c_n:
                num_q = st.selectbox("Questions", [3, 5, 10], index=1)
            with c_d:
                diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if st.button("🚀 Generate & Begin Quiz", type="primary", use_container_width=True):
                if not topic_input.strip():
                    st.error("Please provide a topic.")
                else:
                    with st.spinner("🤖 Crafting rigorous multiple choice questions..."):
                        q_list = ai_service.generate_quiz(
                            topic=topic_input,
                            subject=selected_subj_name,
                            num_questions=num_q,
                            difficulty=diff
                        )
                        st.session_state["active_quiz"] = {
                            "subject_id": selected_subj_id,
                            "subject_name": selected_subj_name,
                            "topic": topic_input,
                            "difficulty": diff,
                            "questions": q_list,
                            "start_time": time.time(),
                            "answers": {}
                        }
                        st.rerun()

        else:
            # Active Quiz Taker
            quiz = st.session_state["active_quiz"]
            questions = quiz["questions"]
            total_q = len(questions)
            
            st.subheader(f"📖 Quiz: {quiz['topic']}")
            st.caption(f"Subject: {quiz['subject_name']} | Difficulty: {quiz['difficulty']} | Total Questions: {total_q}")
            
            with st.form("quiz_answer_form"):
                user_choices = {}
                for idx, q in enumerate(questions):
                    st.markdown(f"**Question {idx + 1} of {total_q}:**")
                    st.markdown(f"#### {q['question']}")
                    
                    options = q.get("options", ["Option A", "Option B", "Option C", "Option D"])
                    choice = st.radio(
                        "Choose your answer:",
                        options=list(range(len(options))),
                        format_func=lambda i, opts=options: opts[i],
                        key=f"q_{idx}",
                        index=None
                    )
                    user_choices[idx] = choice
                    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

                c_sub, c_can = st.columns([1, 1])
                with c_sub:
                    submit_quiz = st.form_submit_button("🏁 Submit Exam for Evaluation", type="primary", use_container_width=True)
                with c_can:
                    cancel_quiz = st.form_submit_button("Cancel & Exit Quiz", use_container_width=True)

            if cancel_quiz:
                del st.session_state["active_quiz"]
                st.rerun()

            if submit_quiz:
                elapsed = int(time.time() - quiz["start_time"])
                results = grade_quiz_attempt(questions, user_choices, elapsed)
                
                # Record to Database
                record_quiz_attempt(
                    subject_id=quiz["subject_id"],
                    topic_id=None,
                    quiz_title=f"{quiz['topic']} ({quiz['difficulty']})",
                    score=results["score"],
                    total_questions=results["total_questions"],
                    percentage=results["percentage"],
                    difficulty=quiz["difficulty"],
                    time_taken_seconds=elapsed,
                    details_json=json.dumps(results["details"])
                )
                
                # Store results for review
                st.session_state["quiz_results"] = results
                del st.session_state["active_quiz"]
                st.rerun()

        # Review Screen if just completed
        if "quiz_results" in st.session_state:
            res = st.session_state["quiz_results"]
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background: rgba(99, 102, 241, 0.1); border: 2px solid {res['badge_color']}; border-radius: 16px; padding: 24px; text-align: center; margin-bottom: 20px;">
                <h1 style="color: {res['badge_color']}; margin: 0; font-size: 42px;">{res['letter_grade']} ({res['percentage']}%)</h1>
                <h3 style="margin: 8px 0; color: {res['badge_color']};">{res['performance_badge']}</h3>
                <p style="margin: 0; opacity: 0.8;">You got <strong>{res['score']} out of {res['total_questions']}</strong> questions correct in {res['elapsed_seconds']} seconds.</p>
            </div>
            """, unsafe_allow_html=True)

            st.subheader("🔍 In-Depth Question Breakdown & Explanations")
            for item in res["details"]:
                status_icon = "✅" if item["is_correct"] else "❌"
                status_text = "Correct" if item["is_correct"] else "Incorrect"
                border_color = "#10b981" if item["is_correct"] else "#ef4444"
                
                st.markdown(f"""
                <div style="border-left: 4px solid {border_color}; background: rgba(148, 163, 184, 0.08); border-radius: 6px; padding: 14px; margin-bottom: 14px;">
                    <strong>{status_icon} Question {item['question_index']}: {item['question']}</strong><br/>
                    <div style="margin-top: 6px; font-size: 14px;">
                        <span>Your Answer: <strong style="color: {border_color};">{item['user_answer']}</strong></span><br/>
                        <span>Correct Answer: <strong style="color: #10b981;">{item['correct_answer']}</strong></span>
                    </div>
                    <div style="margin-top: 10px; font-size: 13px; opacity: 0.9; background: rgba(0,0,0,0.1); padding: 8px; border-radius: 4px;">
                        💡 <strong>Explanation:</strong> {item['explanation']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            if st.button("Take Another Quiz", type="primary", use_container_width=True):
                del st.session_state["quiz_results"]
                st.rerun()

    # ========================================================
    # TAB 2: PAST QUIZ HISTORY & ANALYTICS
    # ========================================================
    with tab_history:
        st.subheader("📜 Past Quiz Attempts")
        attempts = get_quiz_attempts(limit=50)
        
        if not attempts:
            st.info("No past quiz attempts found. Complete your first quiz above to build your performance profile!")
        else:
            # Summary Metrics
            q_scores = [a["percentage"] for a in attempts]
            avg_p = round(sum(q_scores) / len(q_scores), 1)
            best_p = max(q_scores)
            
            c_tot, c_avg, c_best = st.columns(3)
            c_tot.metric("Total Quizzes Completed", len(attempts))
            c_avg.metric("Cumulative Average Score", f"{avg_p}%")
            c_best.metric("Highest Score", f"{best_p}%")

            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            
            for a in attempts:
                pct = a["percentage"]
                color = "#10b981" if pct >= 80 else ("#f59e0b" if pct >= 60 else "#ef4444")
                mins = a["time_taken_seconds"] // 60
                secs = a["time_taken_seconds"] % 60
                
                with st.expander(f"{a['quiz_title']} — {pct}% ({a['created_at'][:10]})", expanded=False):
                    st.markdown(f"- **Score:** {a['score']} / {a['total_questions']} ({pct}%)")
                    st.markdown(f"- **Difficulty:** {a.get('difficulty', 'Medium')}")
                    st.markdown(f"- **Time Spent:** {mins}m {secs}s")
                    st.markdown(f"- **Date:** {a['created_at']}")
                    
                    if a.get("details_json"):
                        try:
                            saved_details = json.loads(a["details_json"])
                            st.markdown("**Review of Questions:**")
                            for qd in saved_details:
                                ic = "✅" if qd.get("is_correct") else "❌"
                                st.markdown(f"- {ic} **{qd.get('question')}** → Answer: `{qd.get('correct_answer')}`")
                        except Exception:
                            pass
