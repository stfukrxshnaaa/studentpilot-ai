"""
Analytics & Progress Tracking View for StudyPilot AI.
Renders comprehensive Plotly charts for study habits, mastery progress, and quiz trajectories.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database.db_manager import (
    get_study_metrics, get_subjects, get_topics, get_quiz_attempts, get_study_sessions
)

def render_analytics_view():
    st.title("📈 Progress & Learning Analytics")
    st.markdown("Visualize your academic trajectory, study hours, syllabus mastery, and exam readiness.")

    metrics = get_study_metrics()

    # 4 Top Analytics Badges
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Focus Time", f"{metrics['total_study_hours']} hrs")
    c2.metric("Topics Mastered", f"{metrics['mastered_topics']} / {metrics['total_topics']}")
    c3.metric("Quiz Score Average", f"{metrics['avg_quiz_score']}%")
    c4.metric("Consecutive Streak", f"{metrics['study_streak_days']} Days")

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # Row 1: Mastery Donut Chart & Study Hours Bar Chart
    r1_col1, r1_col2 = st.columns([1, 1])

    with r1_col1:
        st.subheader("🎯 Overall Topic Mastery")
        mastered = metrics["mastered_topics"]
        in_prog = metrics["in_progress_topics"]
        not_start = metrics["not_started_topics"]

        if mastered + in_prog + not_start > 0:
            labels = ["Mastered", "In Progress", "Not Started"]
            values = [mastered, in_prog, not_start]
            colors = ["#10B981", "#3B82F6", "#94A3B8"] # Emerald, Blue, Slate

            fig_donut = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=colors),
                textinfo="label+percent",
                hoverinfo="label+value+percent"
            )])
            fig_donut.update_layout(
                showlegend=True,
                margin=dict(t=20, b=20, l=20, r=20),
                height=320,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Plus Jakarta Sans", size=13)
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("No topic data found to generate mastery chart.")

    with r1_col2:
        st.subheader("⏱️ Daily Study Hours (Past 14 Days)")
        sessions = get_study_sessions(days_limit=14)
        
        # Build 14-day date range
        today = datetime.now().date()
        date_list = [(today - timedelta(days=i)).isoformat() for i in range(13, -1, -1)]
        day_hours = {d: 0.0 for d in date_list}

        for sess in sessions:
            if sess.get("logged_at"):
                d_str = sess["logged_at"][:10]
                if d_str in day_hours and sess.get("session_type") == "Focus":
                    day_hours[d_str] += sess["duration_minutes"] / 60.0

        df_hours = pd.DataFrame({
            "Date": list(day_hours.keys()),
            "Hours": [round(h, 2) for h in day_hours.values()]
        })

        fig_bar = px.bar(
            df_hours,
            x="Date",
            y="Hours",
            text="Hours",
            color_discrete_sequence=["#6366F1"]
        )
        fig_bar.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="",
            yaxis_title="Hours Studied",
            font=dict(family="Plus Jakarta Sans")
        )
        fig_bar.update_traces(texttemplate='%{text}h', textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # Row 2: Subject Topic Breakdown & Quiz Performance Trajectory
    r2_col1, r2_col2 = st.columns([1, 1])

    with r2_col1:
        st.subheader("📚 Curriculum Status by Course")
        subjects = get_subjects()
        breakdown_data = []

        for s in subjects:
            s_topics = get_topics(subject_id=s["id"])
            m_cnt = sum(1 for t in s_topics if t["status"] == "Mastered")
            p_cnt = sum(1 for t in s_topics if t["status"] == "In Progress")
            n_cnt = sum(1 for t in s_topics if t["status"] == "Not Started")
            breakdown_data.append({"Course": s["code"], "Status": "Mastered", "Count": m_cnt})
            breakdown_data.append({"Course": s["code"], "Status": "In Progress", "Count": p_cnt})
            breakdown_data.append({"Course": s["code"], "Status": "Not Started", "Count": n_cnt})

        if breakdown_data:
            df_breakdown = pd.DataFrame(breakdown_data)
            fig_stack = px.bar(
                df_breakdown,
                x="Course",
                y="Count",
                color="Status",
                barmode="stack",
                color_discrete_map={
                    "Mastered": "#10B981",
                    "In Progress": "#3B82F6",
                    "Not Started": "#94A3B8"
                }
            )
            fig_stack.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                height=320,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Course Code",
                yaxis_title="Topics Count",
                font=dict(family="Plus Jakarta Sans")
            )
            st.plotly_chart(fig_stack, use_container_width=True)
        else:
            st.info("No courses found to display breakdown.")

    with r2_col2:
        st.subheader("🎯 Quiz Performance Trajectory")
        attempts = get_quiz_attempts(limit=15)
        if attempts:
            df_quiz = pd.DataFrame(attempts)
            df_quiz = df_quiz.sort_values(by="created_at", ascending=True)

            fig_line = px.line(
                df_quiz,
                x="created_at",
                y="percentage",
                markers=True,
                hover_data=["quiz_title", "score", "total_questions"],
                color_discrete_sequence=["#10B981"]
            )
            fig_line.add_hline(y=80, line_dash="dash", line_color="#F59E0B", annotation_text="Target Benchmark (80%)")
            fig_line.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                height=320,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Quiz Date",
                yaxis_title="Score (%)",
                yaxis_range=[0, 105],
                font=dict(family="Plus Jakarta Sans")
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Take quizzes in the AI Quiz Arena to visualize your score progression.")
