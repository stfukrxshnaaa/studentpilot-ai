"""
Pomodoro Timer View for StudyPilot AI.
Provides a functional, customizable focus timer with sound notifications,
subject/topic linkage, and persistent SQLite study session logging.
"""

import streamlit as st
import time
from database.db_manager import get_subjects, get_topics, log_study_session, get_study_sessions

def render_pomodoro_view():
    st.title("⏱️ Pomodoro Focus Timer")
    st.markdown("Harness deep work intervals to maximize retention. Completed focus sessions are automatically recorded in your study analytics.")

    subjects = get_subjects()

    # Session State Setup
    if "pomo_state" not in st.session_state:
        st.session_state["pomo_state"] = "idle" # "idle", "running", "paused"
    if "pomo_seconds_left" not in st.session_state:
        st.session_state["pomo_seconds_left"] = 25 * 60
    if "pomo_total_seconds" not in st.session_state:
        st.session_state["pomo_total_seconds"] = 25 * 60
    if "pomo_mode" not in st.session_state:
        st.session_state["pomo_mode"] = "Focus" # "Focus", "Short Break", "Long Break"

    # Timer Configuration & Linkage
    c_sub, c_top, c_type = st.columns([1.5, 1.5, 1])
    
    with c_sub:
        subj_map = {s["name"]: s["id"] for s in subjects} if subjects else {}
        subj_map["General Study"] = None
        sel_subj_name = st.selectbox("Link to Course", list(subj_map.keys()), key="pomo_subj_select")
        sel_subj_id = subj_map[sel_subj_name]

    with c_top:
        if sel_subj_id:
            sub_topics = get_topics(subject_id=sel_subj_id)
            top_map = {t["title"]: t["id"] for t in sub_topics}
            top_map["General Topic"] = None
            sel_top_name = st.selectbox("Link to Topic", list(top_map.keys()), key="pomo_top_select")
            sel_top_id = top_map[sel_top_name]
        else:
            sel_top_id = None
            st.selectbox("Link to Topic", ["General Study"], disabled=True)

    with c_type:
        timer_mode = st.selectbox(
            "Timer Interval",
            ["Focus (25m)", "Deep Focus (50m)", "Short Break (5m)", "Long Break (15m)"]
        )

    # Preset Durations
    duration_map = {
        "Focus (25m)": ("Focus", 25 * 60),
        "Deep Focus (50m)": ("Focus", 50 * 60),
        "Short Break (5m)": ("Short Break", 5 * 60),
        "Long Break (15m)": ("Long Break", 15 * 60)
    }
    target_mode, target_secs = duration_map[timer_mode]

    # Reset if mode changed while idle
    if st.session_state["pomo_state"] == "idle" and st.session_state["pomo_total_seconds"] != target_secs:
        st.session_state["pomo_total_seconds"] = target_secs
        st.session_state["pomo_seconds_left"] = target_secs
        st.session_state["pomo_mode"] = target_mode

    # Visual Display
    mins = st.session_state["pomo_seconds_left"] // 60
    secs = st.session_state["pomo_seconds_left"] % 60
    time_str = f"{mins:02d}:{secs:02d}"

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Progress Calculation
    progress_frac = 1.0 - (st.session_state["pomo_seconds_left"] / max(1, st.session_state["pomo_total_seconds"]))

    mode_badge = "🎯 FOCUS TIME" if "Focus" in st.session_state["pomo_mode"] else "☕ BREAK TIME"
    mode_color = "#6366f1" if "Focus" in st.session_state["pomo_mode"] else "#10b981"

    st.markdown(f"""
    <div class="timer-display">
        <div style="font-size: 14px; font-weight: 700; color: {mode_color}; text-transform: uppercase; letter-spacing: 1px;">
            {mode_badge}
        </div>
        <div class="timer-digits">
            {time_str}
        </div>
        <div style="font-size: 13px; opacity: 0.8;">
            Working on: <strong>{sel_subj_name}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    st.progress(max(0.0, min(1.0, progress_frac)))

    # Controls
    btn_c1, btn_c2, btn_c3, btn_c4 = st.columns(4)

    with btn_c1:
        if st.session_state["pomo_state"] != "running":
            if st.button("▶️ Start Timer", type="primary", use_container_width=True):
                st.session_state["pomo_state"] = "running"
                st.rerun()
        else:
            if st.button("⏸️ Pause", use_container_width=True):
                st.session_state["pomo_state"] = "paused"
                st.rerun()

    with btn_c2:
        if st.button("🔄 Reset Timer", use_container_width=True):
            st.session_state["pomo_state"] = "idle"
            st.session_state["pomo_seconds_left"] = st.session_state["pomo_total_seconds"]
            st.rerun()

    with btn_c3:
        # Quick log completed 25m session
        if st.button("✅ Complete & Log Session", use_container_width=True):
            duration_done = max(1, int(st.session_state["pomo_total_seconds"] / 60))
            log_study_session(
                subject_id=sel_subj_id,
                topic_id=sel_top_id,
                duration_minutes=duration_done,
                session_type=st.session_state["pomo_mode"],
                notes=f"Deep focus on {sel_subj_name}"
            )
            st.session_state["pomo_state"] = "idle"
            st.session_state["pomo_seconds_left"] = st.session_state["pomo_total_seconds"]
            st.success(f"🎉 Great job! Successfully logged {duration_done} minutes to your study history.")
            # Audio chime notification
            st.components.v1.html("""
            <script>
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                function beep() {
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.frequency.value = 587.33; // D5
                    osc.start();
                    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 1.2);
                    osc.stop(ctx.currentTime + 1.2);
                }
                beep();
            </script>
            """, height=0)
            st.rerun()

    with btn_c4:
        if st.button("⏩ Skip to Next", use_container_width=True):
            if "Focus" in st.session_state["pomo_mode"]:
                st.session_state["pomo_mode"] = "Short Break"
                st.session_state["pomo_total_seconds"] = 5 * 60
                st.session_state["pomo_seconds_left"] = 5 * 60
            else:
                st.session_state["pomo_mode"] = "Focus"
                st.session_state["pomo_total_seconds"] = 25 * 60
                st.session_state["pomo_seconds_left"] = 25 * 60
            st.session_state["pomo_state"] = "idle"
            st.rerun()

    # Active timer countdown loop in Streamlit
    if st.session_state["pomo_state"] == "running":
        time.sleep(1)
        st.session_state["pomo_seconds_left"] -= 1
        if st.session_state["pomo_seconds_left"] <= 0:
            st.session_state["pomo_state"] = "idle"
            st.session_state["pomo_seconds_left"] = st.session_state["pomo_total_seconds"]
            # Auto log
            dur = int(st.session_state["pomo_total_seconds"] / 60)
            log_study_session(sel_subj_id, sel_top_id, dur, st.session_state["pomo_mode"], "Timer finished naturally")
            st.toast(f"🔔 Session complete! {dur} minutes logged.")
        st.rerun()

    st.divider()

    # Recent Sessions Log Table
    st.subheader("📊 Recent Study Sessions")
    recent = get_study_sessions(days_limit=14)
    if recent:
        for sess in recent[:6]:
            icon = "🎯" if "Focus" in sess.get("session_type", "") else "☕"
            st.markdown(f"""
            <div style="border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{icon} {sess.get('session_type')} Session</strong> ({sess['duration_minutes']} min)
                    <div style="font-size: 12px; opacity: 0.7;">{sess.get('subject_name', 'General')} • {sess['logged_at']}</div>
                </div>
                <div style="font-weight: 600; color: #10b981;">
                    +{sess['duration_minutes']} mins
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No sessions recorded yet. Start your first session above!")
