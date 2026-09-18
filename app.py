import streamlit as st
from config.settings import APP_NAME, APP_TAGLINE
from database.db import init_db
from utils.auth import init_session, get_current_user, logout_user
from utils.ui_components import apply_custom_css
from services.gemini_service import is_api_key_configured

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()
init_session()
apply_custom_css()

from views.auth_view import render_auth_page
from views.dashboard_view import render_dashboard
from views.resume_view import render_resume_analyzer
from views.ats_view import render_ats_checker
from views.job_view import render_job_analyzer
from views.skill_gap_view import render_skill_gap
from views.roadmap_view import render_career_roadmap
from views.learning_tutor_view import render_learning_assistant
from views.learning_tracker_view import render_learning_tracker
from views.pdf_assistant_view import render_pdf_assistant
from views.notes_view import render_notes
from views.tasks_view import render_tasks
from views.productivity_view import render_productivity_assistant
from views.reminders_view import render_reminders
from views.email_view import render_email_generator
from views.interview_view import render_interview_coach
from views.applications_view import render_career_applications
from views.career_insights_view import render_career_insights
from views.settings_view import render_settings

user = get_current_user()

if not user:
    render_auth_page()
else:
    with st.sidebar:
        has_key = is_api_key_configured()
        ai_badge = '<span class="nexus-badge badge-emerald">⚡ Live Gemini 2.0</span>' if has_key else '<span class="nexus-badge badge-cyan">⚡ Smart AI Engine</span>'

        st.markdown(f"""
            <div style="padding: 0.5rem 0 1rem 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <h2 style="font-size: 1.25rem; font-weight: 800; margin: 0; background: linear-gradient(135deg, #10B981 0%, #06B6D4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                        🤖 NexusAI
                    </h2>
                    {ai_badge}
                </div>
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 0.25rem;">{APP_TAGLINE}</div>
                <div style="margin-top: 0.85rem; padding: 0.6rem 0.8rem; background: rgba(15, 23, 42, 0.7); border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
                    <div style="font-size: 0.9rem; font-weight: 700; color: #F8FAFC;">👤 {user['full_name']}</div>
                    <div style="font-size: 0.75rem; color: #38BDF8; margin-top: 0.1rem;">🎯 {user.get('target_role', 'Developer')}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        pages = {
            "📊 Dashboard": render_dashboard,
            "📄 Resume Analyzer": render_resume_analyzer,
            "🎯 ATS Checker": render_ats_checker,
            "💼 Job Analyzer": render_job_analyzer,
            "🧠 Skill Gap": render_skill_gap,
            "🚀 Career Roadmap": render_career_roadmap,
            "📚 Learning Assistant": render_learning_assistant,
            "📈 Learning Tracker": render_learning_tracker,
            "📑 PDF Assistant": render_pdf_assistant,
            "📝 Notes": render_notes,
            "✅ Tasks": render_tasks,
            "⚡ Productivity Plan": render_productivity_assistant,
            "⏰ Reminders": render_reminders,
            "📨 Email Generator": render_email_generator,
            "🎤 Interview Coach": render_interview_coach,
            "💼 Applications": render_career_applications,
            "💡 Career Insights": render_career_insights,
            "⚙️ Settings": render_settings
        }

        selected_page = st.radio(
            "Navigation",
            list(pages.keys()),
            label_visibility="collapsed"
        )

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Log Out", use_container_width=True):
            logout_user()

    view_func = pages.get(selected_page, render_dashboard)
    view_func()
