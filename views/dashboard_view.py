import streamlit as st
import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.auth import get_current_user
from utils.ui_components import render_page_header, render_callout, render_skill_bar
from database.models import (
    get_tasks,
    get_reminders,
    get_latest_resume_analysis,
    get_latest_ats_result,
    get_learning_goals,
    get_user_skills,
    get_user_documents
)

def render_dashboard():
    """Renders the executive main productivity and career dashboard."""
    user = get_current_user()
    if not user:
        return
        
    today_str = datetime.date.today().strftime("%A, %B %d, %Y")
    render_page_header(
        title=f"Welcome back, {user['full_name'].split()[0]}! 👋",
        subtitle=f"Target Role: {user.get('target_role', 'Software Engineer')} • {today_str}",
        badge="Active Workspace"
    )
    
    # Fetch user data
    tasks = get_tasks(user['id'])
    reminders = get_reminders(user['id'], is_completed=False)
    resume_analysis = get_latest_resume_analysis(user['id'])
    ats_result = get_latest_ats_result(user['id'])
    goals = get_learning_goals(user['id'])
    skills = get_user_skills(user['id'])
    documents = get_user_documents(user['id'])
    
    # Calculate KPIs
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.get('status') == 'Completed'])
    pending_tasks = total_tasks - completed_tasks
    
    avg_learning_pct = int(sum(g.get('progress_pct', 0) for g in goals) / len(goals)) if goals else 0
    ats_score = ats_result.get('ats_score', 0) if ats_result else (resume_analysis.get('overall_score', 0) if resume_analysis else 0)
    
    # Productivity score calculation
    task_ratio = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 70
    productivity_score = int(min(100, (task_ratio * 0.5) + (avg_learning_pct * 0.3) + 20))
    
    # --- Top KPI scoreboard ---
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-label">Pending Tasks</div>
                <div class="kpi-val">{pending_tasks}</div>
                <div style="font-size: 0.8rem; color: #9CA3AF;">{completed_tasks} completed</div>
            </div>
        """, unsafe_allow_html=True)
    with kpi_col2:
        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-label">Resume / ATS Score</div>
                <div class="kpi-val">{ats_score}<span style="font-size: 1.1rem; color: #9CA3AF;">/100</span></div>
                <div style="font-size: 0.8rem; color: #10B981;">Quality benchmark</div>
            </div>
        """, unsafe_allow_html=True)
    with kpi_col3:
        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-label">Learning Progress</div>
                <div class="kpi-val">{avg_learning_pct}%</div>
                <div style="font-size: 0.8rem; color: #06B6D4;">Across {len(goals)} active goals</div>
            </div>
        """, unsafe_allow_html=True)
    with kpi_col4:
        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-label">Productivity Index</div>
                <div class="kpi-val">{productivity_score}%</div>
                <div style="font-size: 0.8rem; color: #8B5CF6;">Weekly momentum</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
    
    # --- AI Career & Productivity Recommendation Callout ---
    rec_text = "Focus on containerization (Docker) and REST API integration this week to boost your ATS compatibility for " + user.get('target_role', 'Software Engineer') + " roles."
    if resume_analysis and resume_analysis.get('suggestions'):
        rec_text = resume_analysis['suggestions'][0]
    render_callout(
        f"<strong>AI Career Strategy:</strong> {rec_text}",
        callout_type="info",
        icon="🚀"
    )
    
    # --- Main Dashboard Grid ---
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        # Task Overview
        st.markdown("### 📋 Priority Action Items")
        if tasks:
            for task in tasks[:5]:
                p_color = {
                    "Urgent": "badge-rose",
                    "High": "badge-amber",
                    "Medium": "badge-cyan",
                    "Low": "badge-emerald"
                }.get(task.get('priority'), 'badge-cyan')
                
                status_icon = "✅" if task.get('status') == 'Completed' else "⏳"
                st.markdown(f"""
                    <div style="background: rgba(17, 24, 39, 0.6); border: 1px solid rgba(255,255,255,0.06); padding: 0.85rem 1rem; border-radius: 8px; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-weight: 600; color: #F9FAFB;">{status_icon} {task.get('title')}</span>
                            <div style="font-size: 0.8rem; color: #9CA3AF; margin-top: 0.2rem;">Due: {task.get('due_date', 'No date')} • Category: {task.get('category', 'General')}</div>
                        </div>
                        <span class="nexus-badge {p_color}">{task.get('priority')}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No active tasks! Head over to the Tasks tab to add your daily study or application goals.")
            
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
        # Interactive Learning Progress Chart
        st.markdown("### 📊 Learning Track Breakdown")
        if goals:
            df_goals = pd.DataFrame(goals)
            fig = px.bar(
                df_goals,
                x='progress_pct',
                y='topic',
                orientation='h',
                color='progress_pct',
                color_continuous_scale=['#06B6D4', '#10B981'],
                labels={'progress_pct': 'Progress (%)', 'topic': 'Learning Topic'},
                range_x=[0, 100]
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#F9FAFB'),
                height=220,
                margin=dict(l=10, r=10, t=10, b=10),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No learning goals recorded yet. Visit the Learning Tracker to set your targets.")

    with col_right:
        # Upcoming Reminders
        st.markdown("### ⏰ Upcoming Reminders")
        if reminders:
            for rem in reminders[:4]:
                st.markdown(f"""
                    <div style="background: rgba(245, 158, 11, 0.06); border-left: 3px solid #F59E0B; padding: 0.75rem 1rem; border-radius: 6px; margin-bottom: 0.5rem;">
                        <div style="font-weight: 600; color: #FEF3C7; font-size: 0.9rem;">🔔 {rem.get('title')}</div>
                        <div style="font-size: 0.75rem; color: #D1D5DB; margin-top: 0.2rem;">{rem.get('due_date')} • Type: {rem.get('reminder_type')}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='color: #9CA3AF; font-size: 0.9rem;'>No pending reminders today. You are all caught up!</p>", unsafe_allow_html=True)

        st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)

        # Quick Skills Overview
        st.markdown("### 🧠 Top Skills")
        if skills:
            for sk in skills[:4]:
                color = "emerald" if sk.get('status') == "Mastered" or sk.get('proficiency_score', 0) >= 80 else ("cyan" if sk.get('proficiency_score', 0) >= 60 else "amber")
                render_skill_bar(sk.get('skill_name'), sk.get('status', 'Good'), sk.get('proficiency_score', 50), color=color)
        else:
            # Default placeholder skills
            render_skill_bar("Python", "Strong", 80, color="emerald")
            render_skill_bar("Django", "Good", 70, color="cyan")
            render_skill_bar("Docker", "Beginner", 35, color="amber")
            
        st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)

        # Recent Documents
        st.markdown("### 📑 Uploaded Documents")
        if documents:
            for doc in documents[:3]:
                st.markdown(f"""
                    <div style="font-size: 0.85rem; color: #9CA3AF; padding: 0.35rem 0;">
                        📄 <strong>{doc.get('filename')}</strong> <span style="font-size: 0.75rem;">({doc.get('doc_type')})</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='color: #6B7280; font-size: 0.85rem;'>No documents uploaded yet.</p>", unsafe_allow_html=True)
