"""
Student Dashboard View for StudyPilot AI.
Displays overview KPIs, upcoming exam countdowns, subject progress, and quick action shortcuts.
"""

import streamlit as st
from database.db_manager import get_study_metrics, get_subjects, get_topics, get_quiz_attempts, get_study_sessions
from utils.helpers import get_daily_quote, format_countdown

def render_dashboard(navigate_fn):
    metrics = get_study_metrics()
    quote_info = get_daily_quote()
    
    # Hero Banner
    st.markdown(f"""
    <div class="hero-banner">
        <h1 class="hero-title">👋 Welcome back, Scholar!</h1>
        <p class="hero-subtitle">{quote_info['quote']} — <em>{quote_info['author']}</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 6 Top Metric Cards
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⏱️ Focus Hours</div>
            <div class="metric-value">{metrics['total_study_hours']}h</div>
            <div class="metric-sub">Logged Study Time</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        mastered = metrics['mastered_topics']
        total_t = metrics['total_topics']
        pct_mastered = round((mastered / total_t * 100), 0) if total_t > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🎯 Topics Done</div>
            <div class="metric-value">{mastered}/{total_t}</div>
            <div class="metric-sub">{pct_mastered}% Mastered</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        streak = metrics['study_streak_days']
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔥 Day Streak</div>
            <div class="metric-value">{streak} Days</div>
            <div class="metric-sub">{"Keep the flame alive!" if streak > 0 else "Start today!"}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        avg_score = metrics['avg_quiz_score']
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📝 Quiz Average</div>
            <div class="metric-value">{avg_score}%</div>
            <div class="metric-sub">{metrics['quiz_attempts']} Quizzes Taken</div>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🗂️ Flashcards</div>
            <div class="metric-value">{metrics['flashcards_count']}</div>
            <div class="metric-sub">Active Deck Cards</div>
        </div>
        """, unsafe_allow_html=True)

    with c6:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">✍️ Notes</div>
            <div class="metric-value">{metrics['notes_count']}</div>
            <div class="metric-sub">Knowledge Entries</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Quick Actions Row
    st.subheader("⚡ Quick Actions")
    qa1, qa2, qa3, qa4, qa5 = st.columns(5)
    with qa1:
        if st.button("⏱️ Start Pomodoro", use_container_width=True):
            navigate_fn("Pomodoro Timer")
    with qa2:
        if st.button("🤖 Ask AI Tutor", use_container_width=True):
            navigate_fn("AI Tutor")
    with qa3:
        if st.button("📝 Take AI Quiz", use_container_width=True):
            navigate_fn("AI Quiz Arena")
    with qa4:
        if st.button("📅 Plan Schedule", use_container_width=True):
            navigate_fn("Study Planner")
    with qa5:
        if st.button("➕ Add Topic", use_container_width=True):
            navigate_fn("Subjects & Topics")

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # 2-Column Section: Upcoming Exams & Subject Mastery Progress
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("⏳ Upcoming Exams & Deadlines")
        upcoming = metrics["upcoming_exams"]
        if upcoming:
            for ex in upcoming:
                countdown_str = format_countdown(ex.get("target_date", ""))
                st.markdown(f"""
                <div style="background: rgba(99, 102, 241, 0.08); border-left: 4px solid {ex.get('color', '#6366f1')}; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-size: 16px;">{ex.get('name')} ({ex.get('code')})</strong>
                        <div style="font-size: 13px; opacity: 0.8; margin-top: 4px;">Target Score: <strong>{ex.get('target_score', 90)}%</strong></div>
                    </div>
                    <div style="background: rgba(99, 102, 241, 0.2); padding: 6px 12px; border-radius: 20px; font-weight: 700; font-size: 13px;">
                        {countdown_str}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No upcoming exams set! Go to **Subjects & Topics** to set target exam dates.")

    with col_right:
        st.subheader("📊 Subject Mastery Progress")
        subjects = get_subjects()
        if subjects:
            for s in subjects:
                topics = get_topics(subject_id=s["id"])
                total = len(topics)
                mastered_count = sum(1 for t in topics if t["status"] == "Mastered")
                pct = int((mastered_count / total) * 100) if total > 0 else 0
                
                st.markdown(f"""
                <div style="margin-bottom: 14px;">
                    <div style="display: flex; justify-content: space-between; font-size: 14px; font-weight: 600; margin-bottom: 5px;">
                        <span>{s.get('icon', '📚')} {s['name']} ({s['code']})</span>
                        <span>{mastered_count}/{total} topics ({pct}%)</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(pct / 100.0)
        else:
            st.info("No subjects added yet. Add your first subject to see mastery tracking!")

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # Recent Activity Row
    st.subheader("🕒 Recent Study Activity")
    act_col1, act_col2 = st.columns(2)
    
    with act_col1:
        st.markdown("**Recent Quiz Attempts**")
        recent_quizzes = get_quiz_attempts(limit=4)
        if recent_quizzes:
            for q in recent_quizzes:
                score_color = "#10b981" if q["percentage"] >= 80 else ("#f59e0b" if q["percentage"] >= 60 else "#ef4444")
                st.markdown(f"""
                <div style="border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; font-size: 14px;">{q['quiz_title']}</div>
                        <div style="font-size: 12px; opacity: 0.7;">{q.get('subject_name', 'General')} • {q['created_at'][:10]}</div>
                    </div>
                    <div style="font-weight: 800; font-size: 16px; color: {score_color};">
                        {q['percentage']}% ({q['score']}/{q['total_questions']})
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No quizzes completed yet. Test yourself in the AI Quiz Arena!")
            
    with act_col2:
        st.markdown("**Recent Pomodoro Sessions**")
        recent_sessions = get_study_sessions(days_limit=7)[:4]
        if recent_sessions:
            for sess in recent_sessions:
                st.markdown(f"""
                <div style="border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; font-size: 14px;">⏱️ {sess.get('session_type', 'Focus')} Session ({sess['duration_minutes']} min)</div>
                        <div style="font-size: 12px; opacity: 0.7;">{sess.get('subject_name', 'Study')} • {sess['logged_at'][:16]}</div>
                    </div>
                    <div style="font-size: 13px; font-weight: 600; color: #6366f1;">
                        {sess.get('notes', 'Completed')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No study sessions logged yet. Launch a Pomodoro timer session to start logging!")
