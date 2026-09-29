"""
AI Tutor View for StudyPilot AI.
Generates comprehensive multi-perspective explanations for any college topic.
Allows saving explanations to notes or generating flashcards on the fly.
"""

import streamlit as st
from database.db_manager import get_subjects, get_topics, add_note, add_flashcard
from services.ai_service import ai_service

def render_ai_tutor(navigate_fn):
    st.title("🤖 AI Tutor & Topic Explainer")
    st.markdown("Master difficult college concepts with personalized, multi-perspective explanations, intuitive analogies, and exam insights.")

    # Status pill for active AI provider
    if ai_service.is_live():
        st.markdown(f'<span class="badge-pill badge-mastered">🟢 Live LLM Active: {ai_service.provider.upper()}</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-pill badge-medium">🟡 Mode: Local Academic Engine (Add API Key in Settings for Live LLM)</span>', unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    subjects = get_subjects()
    
    # Input selection: from syllabus or custom prompt
    c_sub, c_top, c_mode = st.columns([1.5, 2, 1.5])
    
    with c_sub:
        subj_options = {s["name"]: s["id"] for s in subjects} if subjects else {}
        subj_options["Custom / General Subject"] = None
        selected_subj_name = st.selectbox("Subject Area", list(subj_options.keys()))
        selected_subj_id = subj_options[selected_subj_name]
        
    with c_top:
        if selected_subj_id:
            topics_in_subj = get_topics(subject_id=selected_subj_id)
            topic_names = [t["title"] for t in topics_in_subj]
            topic_names.append("➕ Enter Custom Topic...")
            chosen_topic = st.selectbox("Select Topic", topic_names)
            if chosen_topic == "➕ Enter Custom Topic...":
                topic_query = st.text_input("Enter Topic Name", placeholder="e.g. Fourier Transform, Bayes Theorem")
            else:
                topic_query = chosen_topic
        else:
            topic_query = st.text_input("Enter Topic Name", value="Dijkstra Shortest Path Algorithm")
            
    with c_mode:
        explanation_mode = st.selectbox(
            "Explanation Style",
            [
                "Academic In-Depth",
                "ELI5 & Intuitive Analogy",
                "Cheat Sheet & Quick Revision",
                "Real-World Case Study",
                "Common Exam Pitfalls"
            ]
        )

    col_btn, _ = st.columns([1, 2])
    with col_btn:
        generate_btn = st.button("✨ Explain Concept", type="primary", use_container_width=True)

    if generate_btn:
        if not topic_query.strip():
            st.error("Please select or enter a topic to explain.")
        else:
            with st.spinner("🤖 AI Tutor is synthesizing comprehensive breakdown..."):
                subj_for_prompt = selected_subj_name if selected_subj_name != "Custom / General Subject" else "General College Course"
                res = ai_service.generate_topic_explanation(
                    topic=topic_query,
                    subject=subj_for_prompt,
                    mode=explanation_mode,
                    difficulty="College Level"
                )
                st.session_state["current_explanation"] = {
                    "topic": topic_query,
                    "subject": subj_for_prompt,
                    "subject_id": selected_subj_id,
                    "mode": explanation_mode,
                    "text": res["text"],
                    "source": res.get("source", "StudyPilot AI")
                }

    # Display explanation if in state
    if "current_explanation" in st.session_state:
        exp = st.session_state["current_explanation"]
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        # Engine source tag
        st.caption(f"Generated via: **{exp['source']}** | Style: **{exp['mode']}**")
        
        # Render markdown content
        with st.container():
            st.markdown(exp["text"])

        st.divider()

        # Follow-up Actions
        st.subheader("⚡ Next Steps with this Topic")
        a1, a2, a3 = st.columns(3)
        
        with a1:
            if st.button("💾 Save to My Notes", use_container_width=True):
                # Find matching topic_id if possible
                t_id = None
                if exp["subject_id"]:
                    sub_topics = get_topics(subject_id=exp["subject_id"])
                    match = next((t["id"] for t in sub_topics if t["title"] == exp["topic"]), None)
                    t_id = match
                    s_id = exp["subject_id"]
                else:
                    s_id = subjects[0]["id"] if subjects else None
                    
                if s_id:
                    note_title = f"{exp['topic']} ({exp['mode']})"
                    add_note(s_id, t_id, note_title, exp["text"], f"ai-tutor, {exp['mode'].lower()}")
                    st.success("Saved directly into your Notes library!")
                else:
                    st.error("Please create a Subject first to save notes.")

        with a2:
            if st.button("🗂️ Generate 3 Flashcards", use_container_width=True):
                s_id = exp["subject_id"] if exp["subject_id"] else (subjects[0]["id"] if subjects else None)
                if s_id:
                    with st.spinner("Extracting high-yield flashcards..."):
                        cards = ai_service.generate_flashcards(exp["topic"], exp["subject"], count=3)
                        for c in cards:
                            add_flashcard(s_id, None, c["question"], c["answer"], "Good")
                        st.success(f"Added {len(cards)} flashcards to your deck!")
                else:
                    st.error("Please create a Subject first to save flashcards.")

        with a3:
            if st.button("📝 Test with AI Quiz", use_container_width=True):
                st.session_state["quiz_target_topic"] = exp["topic"]
                st.session_state["quiz_target_subject"] = exp["subject"]
                navigate_fn("AI Quiz Arena")
