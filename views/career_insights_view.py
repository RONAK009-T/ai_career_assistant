import streamlit as st
from utils.auth import get_current_user
from utils.ui_components import render_page_header, render_callout
from database.models import (
    get_latest_resume_analysis,
    get_user_skills,
    get_learning_goals,
    get_job_applications,
    get_latest_interview_session
)
from services.gemini_service import call_gemini

def render_career_insights():
    """Renders comprehensive holistic AI Career Insights analyzing all user data."""
    user = get_current_user()
    if not user:
        return

    render_page_header(
        title="🧠 AI Holistic Career Insights",
        subtitle="An intelligent 360-degree synthesis of your resume strength, skills, learning progress, and interview performance.",
        badge="Executive Intelligence"
    )

    resume_analysis = get_latest_resume_analysis(user['id'])
    skills = get_user_skills(user['id'])
    goals = get_learning_goals(user['id'])
    apps = get_job_applications(user['id'])
    interview = get_latest_interview_session(user['id'])

    if st.button("🚀 Synthesize 360° AI Career Diagnostic", type="primary", use_container_width=True):
        with st.spinner("Analyzing cross-functional career data..."):
            prompt = f"""
Provide a high-level strategic career guidance report for this candidate:
- Candidate Target Role: {user.get('target_role', 'Software Engineer')}
- Resume Quality Score: {resume_analysis.get('overall_score', 'N/A') if resume_analysis else 'N/A'}
- Mastered/Strong Skills: {', '.join([s['skill_name'] for s in skills if s.get('status') in ['Mastered', 'Strong']]) or 'None recorded'}
- Missing Skills: {', '.join([s['skill_name'] for s in skills if s.get('status') == 'Missing']) or 'None recorded'}
- Active Learning Goals: {', '.join([g['topic'] for g in goals]) or 'None'}
- Job Applications: Total {len(apps)} (Interviews: {len([a for a in apps if a.get('status') == 'Interview'])})

Synthesize a comprehensive Career Diagnostic report with:
1. Executive Career Trajectory Summary
2. Immediate Skill Upgrades (What to learn next)
3. High-Impact Portfolio Project Recommendation
4. Job Search & Outreach Strategy
5. Interview Preparation Focus
"""
            insights = call_gemini(prompt)
            st.session_state['career_insights_report'] = insights

    report = st.session_state.get('career_insights_report')
    if report:
        st.markdown("---")
        st.markdown(report)
    else:
        render_callout("Click 'Synthesize 360° AI Career Diagnostic' above to analyze your profile and generate tailored guidance.", callout_type="info", icon="💡")
