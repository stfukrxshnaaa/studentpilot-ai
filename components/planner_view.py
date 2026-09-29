"""
Study Planner View for StudyPilot AI.
Generates, tracks, and exports realistic study plans based on available daily hours and exam deadlines.
"""

import streamlit as st
from datetime import date, timedelta
from database.db_manager import (
    get_subjects, get_topics, create_study_plan, add_study_plan_items,
    get_study_plans, get_study_plan, get_study_plan_items,
    toggle_plan_item_completion, delete_study_plan
)
from services.study_planner import generate_schedule
from services.export_service import export_study_plan_markdown, export_study_plan_html, export_study_plan_csv

def render_planner_view():
    st.title("📅 AI Study Schedule & Exam Planner")
    st.markdown("Synthesize an optimized, day-by-day curriculum timeline tailored to your daily available study hours and exam deadlines.")

    sub_plans = get_study_plans()
    
    # 2 Tabs: New Plan Generator & Saved Plans Tracker
    tab_create, tab_saved = st.tabs(["✨ Generate New Plan", f"📋 Active & Saved Plans ({len(sub_plans)})"])

    # ========================================================
    # TAB 1: CREATE NEW PLAN
    # ========================================================
    with tab_create:
        subjects = get_subjects()
        if not subjects:
            st.warning("Please add at least one Subject with topics before creating a study plan.")
            return

        with st.form("plan_generator_form"):
            st.subheader("1. Curriculum Scope & Target Parameters")
            p_col1, p_col2, p_col3 = st.columns(3)
            
            with p_col1:
                subj_map = {f"{s.get('icon', '📚')} {s['name']} ({s['code']})": s["id"] for s in subjects}
                selected_subj_label = st.selectbox("Select Subject", list(subj_map.keys()))
                selected_subj_id = subj_map[selected_subj_label]
                selected_subj_obj = next(s for s in subjects if s["id"] == selected_subj_id)
                
            with p_col2:
                # Default to subject target exam date if present
                def_date = date.today() + timedelta(days=21)
                if selected_subj_obj.get("target_date"):
                    try:
                        def_date = date.fromisoformat(selected_subj_obj["target_date"])
                    except Exception:
                        pass
                exam_date = st.date_input("Target Exam Date*", value=def_date, min_value=date.today() + timedelta(days=1))
                
            with p_col3:
                plan_title = st.text_input("Plan Name*", value=f"{selected_subj_obj['code']} Mastery Sprint")

            st.subheader("2. Time Availability & Strategy")
            t_col1, t_col2, t_col3 = st.columns(3)
            with t_col1:
                daily_hours = st.slider("Available Daily Study Time (Hours)", min_value=0.5, max_value=8.0, value=2.5, step=0.5)
            with t_col2:
                study_days_week = st.selectbox("Study Days Per Week", [5, 6, 7], index=1, help="6 days = 1 rest day per week")
            with t_col3:
                buffer_pct = st.slider("Buffer & Revision Reserve (%)", min_value=0, max_value=30, value=15, step=5, help="Reserves days for mock tests and review")

            filter_scope = st.radio(
                "Topics to Include:",
                ["Uncompleted Topics Only (Not Started + In Progress)", "All Subject Topics"],
                index=0,
                horizontal=True
            )

            generate_btn = st.form_submit_button("🚀 Generate Optimized Study Schedule", use_container_width=True)

        if generate_btn:
            # Fetch topics
            all_topics = get_topics(subject_id=selected_subj_id)
            if filter_scope.startswith("Uncompleted"):
                selected_topics = [t for t in all_topics if t["status"] != "Mastered"]
            else:
                selected_topics = all_topics
                
            if not selected_topics:
                st.warning("No eligible topics found for this subject! If all topics are marked Mastered, select 'All Subject Topics'.")
            else:
                schedule_res = generate_schedule(
                    topics=selected_topics,
                    exam_date_str=exam_date.isoformat(),
                    daily_hours=daily_hours,
                    study_days_per_week=study_days_week,
                    buffer_percent=buffer_pct,
                    include_quizzes=True
                )
                
                if not schedule_res.get("is_valid"):
                    st.error(schedule_res.get("error", "Failed to generate schedule."))
                else:
                    st.session_state["preview_plan"] = {
                        "subject_id": selected_subj_id,
                        "title": plan_title,
                        "exam_date": exam_date.isoformat(),
                        "daily_hours": daily_hours,
                        "schedule_res": schedule_res
                    }
                    st.success("🎉 Optimized Study Plan generated successfully! Review below and click 'Save to My Plans'.")

        # Preview Section if generated
        if "preview_plan" in st.session_state:
            p_data = st.session_state["preview_plan"]
            res = p_data["schedule_res"]
            
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            st.markdown(f"### 📋 Preview: {p_data['title']}")
            
            # Pace Banner
            st.markdown(f"""
            <div style="background: rgba(99, 102, 241, 0.1); border-left: 5px solid {res['pace_color']}; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <h4 style="margin: 0; color: {res['pace_color']};">Feasibility: {res['pace_status']} Pace</h4>
                <p style="margin: 5px 0 0 0; font-size: 14px;">{res['pace_message']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Days Until Exam", f"{res['days_remaining']} days")
            m2.metric("Curriculum Workload", f"{res['total_required_hours']} hrs")
            m3.metric("Study Capacity", f"{res['total_potential_hours']} hrs")
            m4.metric("Revision Buffer", f"{res['buffer_hours']} hrs")

            # Schedule Table
            items = res["schedule_items"]
            st.markdown(f"**Day-by-Day Timeline ({len(items)} sessions):**")
            
            for item in items:
                act_icon = "📖" if item["activity_type"] == "Study" else ("📝" if item["activity_type"] == "Quiz" else "🔄")
                st.markdown(f"""
                <div style="border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 8px; padding: 10px 16px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>Day {item['day_number']} ({item['scheduled_date']})</strong> — {act_icon} {item['session_title']}
                    </div>
                    <div style="font-weight: 700; color: #6366f1;">
                        {item['allocated_hours']} hrs
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Save Button
            save_col1, save_col2 = st.columns([1, 1])
            with save_col1:
                if st.button("💾 Save to My Plans & Start Tracking", type="primary", use_container_width=True):
                    plan_id = create_study_plan(
                        subject_id=p_data["subject_id"],
                        title=p_data["title"],
                        exam_date=p_data["exam_date"],
                        available_hours_per_day=p_data["daily_hours"],
                        total_allocated_hours=res["total_allocated_hours"]
                    )
                    add_study_plan_items(plan_id, items)
                    del st.session_state["preview_plan"]
                    st.success("Study plan saved! Switched to Active Plans view.")
                    st.rerun()
            with save_col2:
                if st.button("Discard Preview", use_container_width=True):
                    del st.session_state["preview_plan"]
                    st.rerun()

    # ========================================================
    # TAB 2: ACTIVE & SAVED PLANS
    # ========================================================
    with tab_saved:
        saved_plans = get_study_plans()
        if not saved_plans:
            st.info("You don't have any active study plans yet. Use the 'Generate New Plan' tab above to build your first plan!")
            return

        plan_titles = {f"{p['title']} ({p.get('subject_code', 'General')})": p["id"] for p in saved_plans}
        chosen_plan_label = st.selectbox("Select Study Plan to View & Track", list(plan_titles.keys()))
        chosen_plan_id = plan_titles[chosen_plan_label]
        
        current_plan = get_study_plan(chosen_plan_id)
        plan_items = get_study_plan_items(chosen_plan_id)

        if current_plan:
            # Plan Header
            total_items = len(plan_items)
            completed_items = sum(1 for it in plan_items if it.get("is_completed"))
            pct_completed = int((completed_items / total_items * 100)) if total_items > 0 else 0
            
            st.subheader(f"📌 {current_plan['title']}")
            st.markdown(f"- **Target Exam Date:** {current_plan['exam_date']} | **Daily Hours:** {current_plan['available_hours_per_day']}h | **Total Hours:** {current_plan['total_allocated_hours']}h")
            
            # Progress bar
            st.markdown(f"**Plan Completion:** {completed_items}/{total_items} sessions ({pct_completed}%)")
            st.progress(pct_completed / 100.0)

            # Export Buttons Row (Feature 12: Export study plan)
            st.markdown("#### 📤 Export Study Plan")
            ex_col1, ex_col2, ex_col3, del_col = st.columns([1, 1, 1, 1])
            
            with ex_col1:
                md_content = export_study_plan_markdown(current_plan, plan_items)
                st.download_button(
                    label="📥 Export Markdown (.md)",
                    data=md_content,
                    file_name=f"{current_plan['title'].replace(' ', '_')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            with ex_col2:
                html_content = export_study_plan_html(current_plan, plan_items)
                st.download_button(
                    label="🖨️ Export Printable (HTML)",
                    data=html_content,
                    file_name=f"{current_plan['title'].replace(' ', '_')}.html",
                    mime="text/html",
                    use_container_width=True
                )
            with ex_col3:
                csv_content = export_study_plan_csv(plan_items)
                st.download_button(
                    label="📊 Export CSV",
                    data=csv_content,
                    file_name=f"{current_plan['title'].replace(' ', '_')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with del_col:
                if st.button("🗑️ Delete Plan", key=f"del_plan_{chosen_plan_id}", use_container_width=True):
                    delete_study_plan(chosen_plan_id)
                    st.toast("Study plan deleted.")
                    st.rerun()

            st.divider()

            # Interactive Checklist
            st.markdown("### 📝 Session Checklist")
            st.caption("Check off study blocks as you complete them to track your adherence.")

            for it in plan_items:
                is_done = bool(it.get("is_completed"))
                act_badge = "📖 Study" if it.get("activity_type") == "Study" else ("📝 Quiz" if it.get("activity_type") == "Quiz" else "🔄 Review")
                
                check_col, details_col, hours_col = st.columns([0.5, 4, 1])
                with check_col:
                    checked = st.checkbox("", value=is_done, key=f"plan_item_chk_{it['id']}")
                    if checked != is_done:
                        toggle_plan_item_completion(it["id"], checked)
                        st.rerun()
                with details_col:
                    strike_start = "~~" if is_done else ""
                    strike_end = "~~" if is_done else ""
                    st.markdown(f"{strike_start}**Day {it['day_number']} ({it['scheduled_date']})** — `{act_badge}` {it['session_title']}{strike_end}")
                    if it.get("topic_title"):
                        st.caption(f"Topic: {it['topic_title']}")
                with hours_col:
                    st.markdown(f"**{it['allocated_hours']} hrs**")
                st.markdown("<div style='border-bottom: 1px dashed rgba(148, 163, 184, 0.2); margin: 6px 0;'></div>", unsafe_allow_html=True)
