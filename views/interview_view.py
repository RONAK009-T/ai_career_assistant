import streamlit as st
import plotly.graph_objects as go
from utils.auth import get_current_user
from utils.ui_components import render_page_header, render_callout
from database.models import save_interview_session, get_latest_interview_session
from services.interview_service import generate_interview_questions, evaluate_interview_response

def render_interview_coach():
    """Renders AI Mock Interview Coach with technical/HR questions and answer evaluation."""
    user = get_current_user()
    if not user:
        return

    render_page_header(
        title="🎤 AI Mock Interview Coach",
        subtitle="Practice realistic technical, behavioral, and situational interview questions with detailed scoring and answer critique.",
        badge="Interview Simulator"
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 1. Interview Setup")
        target_role = st.text_input("Target Role", value=user.get('target_role', 'Software Engineer'))
        q_type = st.selectbox("Interview Question Category", ["Technical", "Behavioral (STAR)", "HR / General", "Situational / System Design"])
        
        if st.button("🎯 Start Mock Interview Session", type="primary", use_container_width=True):
            with st.spinner("Generating interview questions tailored to your role..."):
                q_data = generate_interview_questions(target_role, q_type, count=3)
                if "error" in q_data:
                    st.error(q_data["error"])
                else:
                    st.session_state['active_interview_session'] = q_data
                    st.session_state['current_q_index'] = 0
                    st.session_state['interview_evaluations'] = {}
                    st.success("Session ready!")

    session_data = st.session_state.get('active_interview_session')
    if session_data and session_data.get('questions'):
        questions = session_data['questions']
        q_idx = st.session_state.get('current_q_index', 0)
        current_q = questions[min(q_idx, len(questions)-1)]

        with col2:
            st.markdown(f"### Question {q_idx + 1} of {len(questions)}")
            st.markdown(f"""
                <div class="nexus-card" style="border-left: 4px solid #06B6D4;">
                    <div style="font-size: 1.05rem; font-weight: 600; color: #F9FAFB;">
                        "{current_q.get('question')}"
                    </div>
                    <div style="font-size: 0.8rem; color: #9CA3AF; margin-top: 0.4rem;">
                        Category: {current_q.get('category', 'General')}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            user_ans = st.text_area("Your Response", placeholder="Type your answer as you would speak it to the interviewer...", height=150, key=f"ans_input_{q_idx}")

            if st.button("Submit Response for AI Scoring", type="primary"):
                if not user_ans or len(user_ans.strip()) < 10:
                    st.error("Please provide a thorough answer before submitting.")
                else:
                    with st.spinner("Evaluating clarity, technical depth, and communication..."):
                        eval_res = evaluate_interview_response(current_q.get('question'), user_ans, target_role)
                        st.session_state['interview_evaluations'][q_idx] = eval_res

        # Evaluation results
        eval_data = st.session_state.get('interview_evaluations', {}).get(q_idx)
        if eval_data and "score" in eval_data:
            st.markdown("---")
            st.markdown("## 📊 AI Interview Evaluation Report")

            score = eval_data.get('score', 0)
            st.markdown(f"""
                <div class="kpi-box" style="max-width: 250px; margin-bottom: 1rem;">
                    <div class="kpi-label">Answer Score</div>
                    <div class="kpi-val">{score}/100</div>
                </div>
            """, unsafe_allow_html=True)

            col_s, col_w = st.columns(2)
            with col_s:
                st.markdown("### ✅ Strengths")
                for s in eval_data.get('strengths', []):
                    st.markdown(f"- {s}")

            with col_w:
                st.markdown("### ⚠️ Areas for Improvement")
                for w in eval_data.get('weaknesses', []):
                    st.markdown(f"- {w}")

            st.markdown("### 🌟 Model Sample Answer")
            st.info(eval_data.get('improved_model_answer', ''))

            if q_idx < len(questions) - 1:
                if st.button("Next Question ➡️"):
                    st.session_state['current_q_index'] = q_idx + 1
                    st.rerun()
