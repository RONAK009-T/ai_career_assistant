import streamlit as st
from utils.auth import get_current_user
from utils.file_parser import extract_text_from_file
from utils.validators import validate_uploaded_file
from utils.ui_components import render_page_header, render_callout
from database.models import (
    save_uploaded_document,
    get_user_documents,
    get_document_by_id,
    delete_document,
    save_doc_chat_message,
    get_doc_chat_history
)
from services.pdf_service import ask_pdf_question, summarize_document

def render_pdf_assistant():
    """Renders AI PDF Assistant with document chat, summarization, and flashcard generator."""
    user = get_current_user()
    if not user:
        return

    render_page_header(
        title="📑 AI PDF & Document Assistant",
        subtitle="Upload study materials, research papers, documentation, or job specs. Chat with your documents using strictly grounded AI.",
        badge="Grounded RAG"
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 📤 Upload New Document")
        uploaded_doc = st.file_uploader(
            "Upload Document (PDF, DOCX, TXT, MD)",
            type=["pdf", "docx", "txt", "md"],
            key="doc_uploader"
        )
        if uploaded_doc and st.button("Process & Index Document", type="primary", use_container_width=True):
            valid, msg = validate_uploaded_file(uploaded_doc, allowed_types="document")
            if not valid:
                st.error(msg)
            else:
                with st.spinner("Extracting and indexing text..."):
                    raw_text = extract_text_from_file(uploaded_doc)
                    if not raw_text or len(raw_text.strip()) < 20:
                        st.error("Failed to extract readable text.")
                    else:
                        doc_type = uploaded_doc.name.split('.')[-1].upper()
                        doc_id = save_uploaded_document(user['id'], uploaded_doc.name, doc_type, raw_text)
                        st.success(f"Document '{uploaded_doc.name}' indexed successfully!")
                        st.rerun()

        st.markdown("---")
        st.markdown("### 📚 Your Document Library")
        docs = get_user_documents(user['id'])
        if docs:
            doc_options = {d['id']: f"{d['filename']} ({d['doc_type']})" for d in docs}
            selected_doc_id = st.selectbox(
                "Select Active Document",
                options=list(doc_options.keys()),
                format_func=lambda x: doc_options[x]
            )
            
            if st.button("🗑️ Delete Selected Document", use_container_width=True):
                delete_document(selected_doc_id, user['id'])
                st.warning("Document removed.")
                st.rerun()
        else:
            selected_doc_id = None
            st.info("No documents uploaded yet.")

    with col2:
        if selected_doc_id:
            active_doc = get_document_by_id(selected_doc_id, user['id'])
            st.markdown(f"### 💬 Chat with: `{active_doc['filename']}`")
            
            tab_chat, tab_summary, tab_study = st.tabs(["💬 Document Chat", "📝 AI Summary & Highlights", "🗂️ Flashcards & MCQs"])
            
            with tab_chat:
                # Chat History
                chat_history = get_doc_chat_history(selected_doc_id, user['id'])
                for msg in chat_history:
                    role = msg.get('role', 'user')
                    avatar = "👤" if role == 'user' else "🤖"
                    with st.chat_message(role, avatar=avatar):
                        st.markdown(msg.get('message', ''))

                user_q = st.chat_input("Ask a question about this document...")
                if user_q:
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(user_q)
                    save_doc_chat_message(user['id'], selected_doc_id, "user", user_q)

                    with st.chat_message("assistant", avatar="🤖"):
                        with st.spinner("Analyzing document context..."):
                            bot_reply = ask_pdf_question(active_doc['raw_text'], user_q)
                            st.markdown(bot_reply)
                            save_doc_chat_message(user['id'], selected_doc_id, "assistant", bot_reply)
                            st.rerun()

            with tab_summary:
                if st.button("Generate Executive Document Summary"):
                    with st.spinner("Synthesizing document..."):
                        summary_res = summarize_document(active_doc['raw_text'])
                        st.session_state[f'summary_{selected_doc_id}'] = summary_res

                doc_sum = st.session_state.get(f'summary_{selected_doc_id}')
                if doc_sum:
                    st.markdown("#### 📌 Executive Summary")
                    st.markdown(doc_sum.get('executive_summary', 'No summary generated'))
                    
                    st.markdown("#### 🔑 Key Takeaways")
                    for pt in doc_sum.get('key_takeaways', []):
                        st.markdown(f"- {pt}")

            with tab_study:
                doc_sum = st.session_state.get(f'summary_{selected_doc_id}')
                if not doc_sum:
                    if st.button("Generate Study Flashcards & MCQs"):
                        with st.spinner("Extracting flashcards & MCQs..."):
                            doc_sum = summarize_document(active_doc['raw_text'])
                            st.session_state[f'summary_{selected_doc_id}'] = doc_sum
                
                if doc_sum:
                    st.markdown("#### 🗂️ Flashcards")
                    for fc in doc_sum.get('flashcards', []):
                        with st.expander(f"❓ {fc.get('front')}"):
                            st.markdown(f"**Answer:** {fc.get('back')}")
                            
                    st.markdown("#### 📝 Practice MCQs")
                    for idx, mcq in enumerate(doc_sum.get('mcqs', [])):
                        st.markdown(f"**Q{idx+1}: {mcq.get('question')}**")
                        opt = st.radio(f"Options for Q{idx+1}", mcq.get('options', []), key=f"pdf_mcq_{idx}")
                        if st.button(f"Check Q{idx+1}", key=f"btn_pdf_mcq_{idx}"):
                            if mcq.get('options', []).index(opt) == mcq.get('correct_option_index', 0):
                                st.success("Correct!")
                            else:
                                st.error(f"Incorrect. Explanation: {mcq.get('explanation', '')}")
        else:
            st.info("Upload or select a document on the left to start interacting with it.")
