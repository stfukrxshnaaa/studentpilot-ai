"""
Flashcards View for StudyPilot AI.
Provides interactive flip-card study mode, spaced repetition review intervals,
AI flashcard deck generation, and Anki-compatible export.
"""

import streamlit as st
from database.db_manager import (
    get_subjects, get_topics, get_flashcards, add_flashcard,
    update_flashcard_review, delete_flashcard
)
from services.ai_service import ai_service
from services.flashcard_service import calculate_next_review
from services.export_service import export_flashcards_csv

def render_flashcards_view():
    st.title("🗂️ Flashcards & Spaced Repetition")
    st.markdown("Reinforce your active recall with interactive flashcard decks powered by spaced repetition intervals.")

    subjects = get_subjects()
    if not subjects:
        st.warning("Please add a subject before viewing flashcards.")
        return

    tab_study, tab_generate, tab_manage = st.tabs(["🧠 Study Deck", "✨ AI Deck Generator", "➕ Manual Add & Export"])

    # ========================================================
    # TAB 1: STUDY DECK
    # ========================================================
    with tab_study:
        # Deck Filter
        col_s, col_t = st.columns(2)
        with col_s:
            subj_options = {"All Subjects": None}
            for s in subjects:
                subj_options[f"{s.get('icon', '📚')} {s['name']} ({s['code']})"] = s["id"]
            sel_subj_label = st.selectbox("Select Subject Deck", list(subj_options.keys()), key="fc_study_subj")
            sel_subj_id = subj_options[sel_subj_label]

        with col_t:
            if sel_subj_id:
                sub_topics = get_topics(subject_id=sel_subj_id)
                top_opts = {"All Topics": None}
                for t in sub_topics:
                    top_opts[t["title"]] = t["id"]
                sel_top_label = st.selectbox("Select Topic Filter", list(top_opts.keys()), key="fc_study_top")
                sel_top_id = top_opts[sel_top_label]
            else:
                sel_top_id = None

        cards = get_flashcards(subject_id=sel_subj_id, topic_id=sel_top_id)

        if not cards:
            st.info("No flashcards found in this deck! Use the **AI Deck Generator** tab to create flashcards instantly.")
        else:
            if "fc_index" not in st.session_state:
                st.session_state["fc_index"] = 0
            if "fc_flipped" not in st.session_state:
                st.session_state["fc_flipped"] = False

            # Bound check
            total_cards = len(cards)
            if st.session_state["fc_index"] >= total_cards:
                st.session_state["fc_index"] = 0

            curr_card = cards[st.session_state["fc_index"]]
            card_num = st.session_state["fc_index"] + 1

            st.markdown(f"**Card {card_num} of {total_cards}** | *Subject: {curr_card.get('subject_name', 'General')}*")
            st.progress(card_num / total_cards)

            # Modern Card Container
            is_flipped = st.session_state["fc_flipped"]
            side_badge = "🔄 BACK: EXPLANATION / ANSWER" if is_flipped else "❓ FRONT: CONCEPT / PROMPT"
            side_color = "#10b981" if is_flipped else "#6366f1"
            display_text = curr_card["answer"] if is_flipped else curr_card["question"]

            st.markdown(f"""
            <div class="flashcard-box">
                <div style="font-size: 12px; font-weight: 700; color: {side_color}; margin-bottom: 12px; text-transform: uppercase;">
                    {side_badge}
                </div>
                <div style="font-size: 20px; font-weight: 600; line-height: 1.5;">
                    {display_text}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Flip Button
            flip_col, _ = st.columns([1, 1])
            with flip_col:
                if st.button("🔄 Flip Flashcard", use_container_width=True, type="primary"):
                    st.session_state["fc_flipped"] = not st.session_state["fc_flipped"]
                    st.rerun()

            # If flipped, show Spaced Repetition rating buttons
            if is_flipped:
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                st.markdown("##### How well did you recall this concept?")
                r1, r2, r3, r4 = st.columns(4)
                
                with r1:
                    if st.button("🔴 Again (<1 day)", use_container_width=True):
                        next_d, _ = calculate_next_review(curr_card["review_count"], "Again")
                        update_flashcard_review(curr_card["id"], "Again", next_d)
                        st.session_state["fc_flipped"] = False
                        st.session_state["fc_index"] = (st.session_state["fc_index"] + 1) % total_cards
                        st.rerun()
                with r2:
                    if st.button("🟡 Hard (2 days)", use_container_width=True):
                        next_d, _ = calculate_next_review(curr_card["review_count"], "Hard")
                        update_flashcard_review(curr_card["id"], "Hard", next_d)
                        st.session_state["fc_flipped"] = False
                        st.session_state["fc_index"] = (st.session_state["fc_index"] + 1) % total_cards
                        st.rerun()
                with r3:
                    if st.button("🟢 Good (4-7 days)", use_container_width=True):
                        next_d, _ = calculate_next_review(curr_card["review_count"], "Good")
                        update_flashcard_review(curr_card["id"], "Good", next_d)
                        st.session_state["fc_flipped"] = False
                        st.session_state["fc_index"] = (st.session_state["fc_index"] + 1) % total_cards
                        st.rerun()
                with r4:
                    if st.button("🔵 Easy (10+ days)", use_container_width=True):
                        next_d, _ = calculate_next_review(curr_card["review_count"], "Easy")
                        update_flashcard_review(curr_card["id"], "Easy", next_d)
                        st.session_state["fc_flipped"] = False
                        st.session_state["fc_index"] = (st.session_state["fc_index"] + 1) % total_cards
                        st.rerun()

            # Navigation Prev / Next
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            nav_l, nav_r = st.columns(2)
            with nav_l:
                if st.button("⬅️ Previous Card", use_container_width=True):
                    st.session_state["fc_flipped"] = False
                    st.session_state["fc_index"] = (st.session_state["fc_index"] - 1) % total_cards
                    st.rerun()
            with nav_r:
                if st.button("Next Card ➡️", use_container_width=True):
                    st.session_state["fc_flipped"] = False
                    st.session_state["fc_index"] = (st.session_state["fc_index"] + 1) % total_cards
                    st.rerun()

    # ========================================================
    # TAB 2: AI FLASHCARD GENERATOR
    # ========================================================
    with tab_generate:
        st.subheader("✨ Generate High-Yield Flashcards with AI")
        st.markdown("Specify a college topic and let AI synthesize concise front/back prompt pairs.")

        with st.form("ai_fc_gen_form"):
            g_c1, g_c2, g_c3 = st.columns([1.5, 2, 1])
            with g_c1:
                target_subj = st.selectbox("Target Course", options=[s["id"] for s in subjects],
                                           format_func=lambda x: next(s["name"] for s in subjects if s["id"] == x))
            with g_c2:
                sub_topics = get_topics(subject_id=target_subj)
                topic_opts = [t["title"] for t in sub_topics] + ["➕ Custom Topic..."]
                chosen_opt = st.selectbox("Select Topic", topic_opts)
                if chosen_opt == "➕ Custom Topic...":
                    gen_topic = st.text_input("Custom Topic Name", placeholder="e.g. Page Replacement Algorithms")
                else:
                    gen_topic = chosen_opt
            with g_c3:
                card_count = st.slider("Number of Cards", 3, 10, 5)

            gen_fc_btn = st.form_submit_button("🚀 Generate Flashcards Deck", type="primary", use_container_width=True)

        if gen_fc_btn:
            if not gen_topic.strip():
                st.error("Please provide a topic.")
            else:
                with st.spinner("🤖 Extracting core formulas, definitions, and concepts..."):
                    subj_name = next(s["name"] for s in subjects if s["id"] == target_subj)
                    generated_cards = ai_service.generate_flashcards(gen_topic, subj_name, count=card_count)
                    
                    saved_count = 0
                    for c in generated_cards:
                        add_flashcard(target_subj, None, c["question"], c["answer"], "Good")
                        saved_count += 1
                        
                    st.success(f"🎉 Generated and saved {saved_count} flashcards to your deck!")
                    st.rerun()

    # ========================================================
    # TAB 3: MANUAL ADD & EXPORT
    # ========================================================
    with tab_manage:
        st.subheader("➕ Manually Add Flashcard")
        with st.form("manual_fc_form", clear_on_submit=True):
            m_c1, m_c2 = st.columns(2)
            with m_c1:
                m_subj = st.selectbox("Subject", options=[s["id"] for s in subjects],
                                      format_func=lambda x: next(s["name"] for s in subjects if s["id"] == x), key="m_fc_sub")
                m_q = st.text_area("Front (Question or Concept Prompt)*", placeholder="What is the time complexity of QuickSort in the average case?")
            with m_c2:
                m_rating = st.selectbox("Initial Rating", ["Good", "Hard", "Easy"])
                m_a = st.text_area("Back (Answer / Explanation)*", placeholder="O(n log n). QuickSort partitions the array around a pivot element.")
                
            m_sub_btn = st.form_submit_button("Add Flashcard", use_container_width=True)
            if m_sub_btn:
                if not m_q.strip() or not m_a.strip():
                    st.error("Both Question and Answer are required.")
                else:
                    add_flashcard(m_subj, None, m_q, m_a, m_rating)
                    st.success("Flashcard added!")
                    st.rerun()

        st.divider()
        st.subheader("📤 Export Deck (Anki / CSV)")
        all_fc = get_flashcards()
        if all_fc:
            csv_fc = export_flashcards_csv(all_fc)
            st.download_button(
                label="📥 Download All Flashcards as CSV",
                data=csv_fc,
                file_name="studypilot_flashcards.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.caption("No flashcards available to export.")
