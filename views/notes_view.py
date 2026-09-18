import streamlit as st
from utils.auth import get_current_user
from utils.ui_components import render_page_header
from database.models import get_notes, create_note, update_note, delete_note
from services.gemini_service import call_gemini

def render_notes():
    """Renders Smart Notes Manager with AI summarization, structuring, and action item extraction."""
    user = get_current_user()
    if not user:
        return

    render_page_header(
        title="📝 Smart Notes Manager",
        subtitle="Capture thoughts, study notes, and meeting summaries with AI-assisted enhancement and flashcards.",
        badge="Productivity"
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### ➕ Create Note")
        with st.form("new_note_form"):
            note_title = st.text_input("Title", placeholder="e.g. Django Architecture Best Practices")
            note_cat = st.selectbox("Category", ["Study", "Career", "Interview Prep", "Project Notes", "General"])
            note_content = st.text_area("Content", placeholder="Write your notes or paste text here...", height=200)
            is_pinned = st.checkbox("📌 Pin to Top")

            submitted = st.form_submit_button("Save Note", use_container_width=True)
            if submitted:
                if not note_title or not note_content:
                    st.error("Please enter both title and content.")
                else:
                    create_note(user['id'], note_title, note_content, note_cat, 1 if is_pinned else 0)
                    st.success(f"Note '{note_title}' saved!")
                    st.rerun()

    with col2:
        st.markdown("### 🗂️ Your Saved Notes")
        filter_c1, filter_c2 = st.columns(2)
        with filter_c1:
            cat_filter = st.selectbox("Filter Category", ["All", "Study", "Career", "Interview Prep", "Project Notes", "General"])
        with filter_c2:
            search_query = st.text_input("Search Notes", placeholder="Search by title or keywords...")

        notes = get_notes(user['id'], category=cat_filter, search_query=search_query)

        if notes:
            for n in notes:
                pin_badge = "📌 " if n.get('is_pinned') else ""
                with st.expander(f"{pin_badge}{n['title']} ({n.get('category', 'General')})", expanded=bool(n.get('is_pinned'))):
                    st.markdown(f"*{n.get('updated_at', '')}*")
                    st.markdown(n['content'])

                    if n.get('ai_summary'):
                        st.markdown(f"""
                            <div style="background: rgba(6, 182, 212, 0.08); border-left: 3px solid #06B6D4; padding: 0.6rem 0.85rem; border-radius: 6px; margin: 0.6rem 0; font-size: 0.88rem;">
                                <strong>💡 AI Summary & Action Items:</strong><br>{n['ai_summary']}
                            </div>
                        """, unsafe_allow_html=True)

                    btn_c1, btn_c2, btn_c3 = st.columns(3)
                    with btn_c1:
                        if st.button("✨ AI Summarize & Action Items", key=f"ai_sum_{n['id']}", use_container_width=True):
                            with st.spinner("Enhancing note with AI..."):
                                prompt = f"Summarize these notes into key bullet points and extract concrete action items:\n\n{n['content']}"
                                summary = call_gemini(prompt)
                                update_note(n['id'], user['id'], n['title'], n['content'], n['category'], n['is_pinned'], ai_summary=summary)
                                st.rerun()

                    with btn_c2:
                        pin_label = "Unpin" if n.get('is_pinned') else "Pin to Top"
                        if st.button(pin_label, key=f"pin_{n['id']}", use_container_width=True):
                            update_note(n['id'], user['id'], n['title'], n['content'], n['category'], 0 if n.get('is_pinned') else 1, n.get('ai_summary'))
                            st.rerun()

                    with btn_c3:
                        if st.button("🗑️ Delete", key=f"del_{n['id']}", use_container_width=True):
                            delete_note(n['id'], user['id'])
                            st.warning("Note deleted.")
                            st.rerun()
        else:
            st.info("No notes found matching your criteria.")
