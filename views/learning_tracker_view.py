import streamlit as st
import datetime
from utils.auth import get_current_user
from utils.ui_components import render_page_header, render_skill_bar
from database.models import get_learning_goals, create_learning_goal, update_learning_progress, delete_learning_goal

def render_learning_tracker():
    """Renders Learning Progress Tracker with goals, hours, lesson checkpoints."""
    user = get_current_user()
    if not user:
        return

    render_page_header(
        title="📈 Learning Goals & Progress Tracker",
        subtitle="Set study objectives, track completed lessons, log study hours, and monitor your curriculum completion.",
        badge="Accountability Engine"
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### ➕ Create Learning Goal")
        with st.form("new_goal_form"):
            topic = st.text_input("Topic / Subject", placeholder="e.g. Django REST API, React, Docker")
            goal_desc = st.text_area("Goal Description", placeholder="Build a full authentication and permission API system", height=80)
            total_lessons = st.number_input("Target Total Lessons / Modules", min_value=1, max_value=200, value=10)
            target_date = st.date_input("Target Completion Date", min_value=datetime.date.today())
            notes = st.text_input("Study Notes / Resources", placeholder="Documentation link or course name")

            submitted = st.form_submit_button("Add Learning Goal", use_container_width=True)
            if submitted:
                if not topic:
                    st.error("Please enter a topic name.")
                else:
                    create_learning_goal(
                        user_id=user['id'],
                        topic=topic,
                        goal_description=goal_desc,
                        total_lessons=total_lessons,
                        target_date=str(target_date),
                        notes=notes
                    )
                    st.success(f"Goal '{topic}' created successfully!")
                    st.rerun()

    with col2:
        st.markdown("### 📊 Active Learning Tracks")
        goals = get_learning_goals(user['id'])
        if goals:
            for g in goals:
                with st.expander(f"📖 {g['topic']} — {g['progress_pct']}% Complete", expanded=True):
                    st.markdown(f"**Description:** {g.get('goal_description', 'No description')}")
                    st.markdown(f"**Target Date:** `{g.get('target_date', 'N/A')}` • **Study Hours:** `{g.get('study_hours', 0.0)} hrs`")
                    
                    # Custom progress bar
                    render_skill_bar(
                        g['topic'],
                        f"{g['completed_lessons']} of {g['total_lessons']} lessons",
                        g['progress_pct'],
                        color="cyan"
                    )

                    # Update sliders
                    with st.form(f"update_goal_{g['id']}"):
                        u_col1, u_col2, u_col3 = st.columns(3)
                        with u_col1:
                            new_lessons = st.number_input("Completed Lessons", min_value=0, max_value=g['total_lessons'], value=min(g['completed_lessons'], g['total_lessons']))
                        with u_col2:
                            new_hours = st.number_input("Study Hours", min_value=0.0, value=float(g['study_hours']), step=0.5)
                        with u_col3:
                            computed_pct = int((new_lessons / g['total_lessons']) * 100)
                            st.metric("New Progress", f"{computed_pct}%")

                        up_notes = st.text_input("Update Notes", value=g.get('notes', ''))
                        
                        btn_c1, btn_c2 = st.columns(2)
                        with btn_c1:
                            if st.form_submit_button("💾 Save Progress", use_container_width=True):
                                update_learning_progress(g['id'], user['id'], computed_pct, new_lessons, new_hours, up_notes)
                                st.success("Progress saved!")
                                st.rerun()
                        with btn_c2:
                            if st.form_submit_button("🗑️ Delete Goal", use_container_width=True):
                                delete_learning_goal(g['id'], user['id'])
                                st.warning(f"Deleted goal {g['topic']}")
                                st.rerun()
        else:
            st.info("No active learning tracks found. Add your first goal using the form on the left!")
