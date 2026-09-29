"""
Notes View for StudyPilot AI.
Rich Markdown editor with live preview, AI note enhancements (summarization,
glossary extraction, quiz question generation), search, and multi-format exports.
"""

import streamlit as st
from database.db_manager import (
    get_subjects, get_topics, get_notes, get_note, add_note, update_note, delete_note
)
from services.ai_service import ai_service
from services.export_service import export_note_markdown, export_notes_json

def render_notes_view():
    st.title("✍️ Smart Academic Notes")
    st.markdown("Take Markdown notes, organize by course and topic, and enhance them with AI summaries and exam questions.")

    subjects = get_subjects()
    if not subjects:
        st.warning("Please create at least one subject before writing notes.")
        return

    tab_browse, tab_new = st.tabs(["📖 Browse & Edit Notes", "➕ Create New Note"])

    # ========================================================
    # TAB 1: BROWSE & EDIT
    # ========================================================
    with tab_browse:
        # Search & Filter
        s_col1, s_col2 = st.columns([2, 1])
        with s_col1:
            note_search = st.text_input("🔍 Search Notes by keyword or tag", placeholder="e.g. AVL, Semaphore, Krebs, algorithms...", key="note_search_input")
        with s_col2:
            subj_filter_opts = {"All Subjects": None}
            for s in subjects:
                subj_filter_opts[s["name"]] = s["id"]
            sel_s_label = st.selectbox("Filter by Course", list(subj_filter_opts.keys()), key="note_sub_flt")
            sel_s_id = subj_filter_opts[sel_s_label]

        notes = get_notes(subject_id=sel_s_id, search=note_search)

        if not notes:
            st.info("No notes found matching your criteria. Create a new note in the tab above!")
        else:
            note_labels = {f"{n['title']} ({n.get('subject_name', 'General')})": n["id"] for n in notes}
            selected_note_label = st.selectbox("Select Note to View & Edit", list(note_labels.keys()))
            selected_note_id = note_labels[selected_note_label]
            curr_note = get_note(selected_note_id)

            if curr_note:
                st.subheader(f"📝 {curr_note['title']}")
                st.caption(f"Course: **{curr_note.get('subject_name')}** | Topic: **{curr_note.get('topic_title', 'General')}** | Last Updated: {curr_note.get('created_at', '')[:16]}")
                if curr_note.get("tags"):
                    st.markdown(f"**Tags:** `{curr_note['tags']}`")

                # AI Note Assistant Toolbar
                st.markdown("##### 🤖 AI Note Enhancer")
                ai_act1, ai_act2, ai_act3, ai_act4 = st.columns(4)
                
                ai_action_chosen = None
                with ai_act1:
                    if st.button("🎯 Summarize Note", use_container_width=True):
                        ai_action_chosen = "summarize"
                with ai_act2:
                    if st.button("📚 Extract Glossary", use_container_width=True):
                        ai_action_chosen = "extract_terms"
                with ai_act3:
                    if st.button("❓ Exam Questions", use_container_width=True):
                        ai_action_chosen = "generate_questions"
                with ai_act4:
                    if st.button("🪄 Polish Markdown", use_container_width=True):
                        ai_action_chosen = "polish_markdown"

                if ai_action_chosen:
                    with st.spinner("🤖 AI is analyzing your notes..."):
                        enhancement = ai_service.enhance_notes(curr_note["content"], ai_action_chosen)
                        st.session_state["ai_enhancement_result"] = enhancement

                if "ai_enhancement_result" in st.session_state:
                    st.markdown("<div style='background: rgba(99, 102, 241, 0.08); border-left: 4px solid #6366f1; padding: 14px; border-radius: 8px; margin: 12px 0;'>", unsafe_allow_html=True)
                    st.markdown(st.session_state["ai_enhancement_result"])
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    app_c1, app_c2 = st.columns([1, 1])
                    with app_c1:
                        if st.button("➕ Append to this Note", use_container_width=True):
                            new_content = curr_note["content"] + "\n\n---\n\n" + st.session_state["ai_enhancement_result"]
                            update_note(curr_note["id"], curr_note["title"], new_content, curr_note.get("tags", ""))
                            del st.session_state["ai_enhancement_result"]
                            st.success("Appended enhancement to note!")
                            st.rerun()
                    with app_c2:
                        if st.button("Dismiss AI Result", use_container_width=True):
                            del st.session_state["ai_enhancement_result"]
                            st.rerun()

                st.divider()

                # View & Edit Mode
                mode = st.radio("Display Mode:", ["Side-by-Side (Edit & Preview)", "Preview Only"], horizontal=True)

                if mode.startswith("Side"):
                    ed_col, prev_col = st.columns([1, 1])
                    with ed_col:
                        with st.form("edit_note_form"):
                            e_title = st.text_input("Title", value=curr_note["title"])
                            e_tags = st.text_input("Tags (comma separated)", value=curr_note.get("tags", ""))
                            e_content = st.text_area("Content (Markdown)", value=curr_note["content"], height=380)
                            
                            s_save = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
                            if s_save:
                                update_note(curr_note["id"], e_title, e_content, e_tags)
                                st.success("Note saved successfully!")
                                st.rerun()
                    with prev_col:
                        st.markdown("##### 👁️ Live Rendered Preview")
                        st.markdown(e_content)
                else:
                    st.markdown(curr_note["content"])

                st.divider()

                # Export & Delete Actions
                st.markdown("#### 📤 Export Note")
                ex_c1, ex_c2, del_c = st.columns([1, 1, 1])
                with ex_c1:
                    md_text = export_note_markdown(curr_note)
                    st.download_button(
                        label="📥 Download Markdown (.md)",
                        data=md_text,
                        file_name=f"{curr_note['title'].replace(' ', '_')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                with ex_c2:
                    json_text = export_notes_json([curr_note])
                    st.download_button(
                        label="📄 Download JSON",
                        data=json_text,
                        file_name=f"{curr_note['title'].replace(' ', '_')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                with del_c:
                    if st.button("🗑️ Delete Note", key=f"del_n_{curr_note['id']}", use_container_width=True):
                        delete_note(curr_note["id"])
                        st.toast("Note deleted.")
                        st.rerun()

    # ========================================================
    # TAB 2: CREATE NEW NOTE
    # ========================================================
    with tab_new:
        st.subheader("➕ Create a New Knowledge Entry")
        with st.form("create_note_form", clear_on_submit=True):
            cn_c1, cn_c2 = st.columns(2)
            with cn_c1:
                n_subj = st.selectbox("Subject Course*", options=[s["id"] for s in subjects],
                                      format_func=lambda x: next(s["name"] for s in subjects if s["id"] == x))
                sub_topics = get_topics(subject_id=n_subj)
                top_opts = [("None / General", None)] + [(t["title"], t["id"]) for t in sub_topics]
                n_top = st.selectbox("Link to Topic", options=[t[1] for t in top_opts], format_func=lambda x: next(t[0] for t in top_opts if t[1] == x))
            with cn_c2:
                n_title = st.text_input("Note Title*", placeholder="e.g. Master Theorem for Recurrences")
                n_tags = st.text_input("Tags (comma separated)", placeholder="algorithms, complexity, exam-prep")

            n_content = st.text_area(
                "Note Content (Supports full Markdown, LaTeX math $...$ and code blocks)*",
                placeholder="## Master Theorem Formula\n\nFor recurrence relations of the form:\n$$T(n) = a T(n/b) + f(n)$$\n...",
                height=250
            )

            create_btn = st.form_submit_button("Create Note", type="primary", use_container_width=True)
            if create_btn:
                if not n_title.strip() or not n_content.strip():
                    st.error("Title and Content are required.")
                else:
                    new_id = add_note(n_subj, n_top, n_title, n_content, n_tags)
                    st.success(f"Note '{n_title}' created successfully!")
                    st.rerun()
