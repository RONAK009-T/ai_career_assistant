import streamlit as st
import datetime
from utils.auth import get_current_user
from utils.ui_components import render_page_header
from database.models import get_tasks, create_task, update_task, delete_task

def render_tasks():
    """Renders Task Manager with priority indicators, statuses, and filters."""
    user = get_current_user()
    if not user:
        return

    render_page_header(
        title="✅ Task & Productivity Manager",
        subtitle="Organize your career development milestones, coding sprints, and daily responsibilities.",
        badge="Execution Engine"
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### ➕ Add New Task")
        with st.form("new_task_form"):
            task_title = st.text_input("Task Title", placeholder="e.g. Build JWT auth module")
            task_desc = st.text_area("Description", placeholder="Task specifications, sub-items...", height=80)
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"], index=1)
            with t_col2:
                category = st.selectbox("Category", ["Study", "Job Applications", "Coding Project", "Interview Prep", "General"])
            
            due_date = st.date_input("Due Date", min_value=datetime.date.today())
            status = st.selectbox("Initial Status", ["Pending", "In Progress", "Completed"])

            submitted = st.form_submit_button("Add Task", use_container_width=True)
            if submitted:
                if not task_title:
                    st.error("Please enter a task title.")
                else:
                    create_task(
                        user_id=user['id'],
                        title=task_title,
                        description=task_desc,
                        priority=priority,
                        category=category,
                        status=status,
                        due_date=str(due_date)
                    )
                    st.success(f"Task '{task_title}' created!")
                    st.rerun()

    with col2:
        st.markdown("### 📋 Active Tasks")
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            status_filter = st.selectbox("Status", ["All", "Pending", "In Progress", "Completed"])
        with f_col2:
            priority_filter = st.selectbox("Priority Filter", ["All", "Urgent", "High", "Medium", "Low"])
        with f_col3:
            search_query = st.text_input("Search Tasks", placeholder="Keyword...")

        tasks = get_tasks(user['id'], status=status_filter, priority=priority_filter, search_query=search_query)

        if tasks:
            for t in tasks:
                p_badge = {
                    "Urgent": "badge-rose",
                    "High": "badge-amber",
                    "Medium": "badge-cyan",
                    "Low": "badge-emerald"
                }.get(t.get('priority'), 'badge-cyan')

                with st.expander(f"[{t.get('status')}] {t['title']} — Due: {t.get('due_date', 'N/A')}", expanded=t.get('status') != 'Completed'):
                    st.markdown(f"**Description:** {t.get('description') or 'No description'}")
                    st.markdown(f"**Priority:** <span class='nexus-badge {p_badge}'>{t.get('priority')}</span> • **Category:** `{t.get('category')}`", unsafe_allow_html=True)
                    
                    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                    btn_c1, btn_c2, btn_c3 = st.columns(3)
                    with btn_c1:
                        new_stat = "Completed" if t.get('status') != 'Completed' else "Pending"
                        btn_lbl = "Mark Complete ✅" if t.get('status') != 'Completed' else "Reopen ⏳"
                        if st.button(btn_lbl, key=f"t_stat_{t['id']}", use_container_width=True):
                            update_task(t['id'], user['id'], t['title'], t['description'], t['priority'], t['category'], new_stat, t['due_date'])
                            st.rerun()

                    with btn_c2:
                        if t.get('status') != 'In Progress':
                            if st.button("Set In Progress 🚀", key=f"t_prog_{t['id']}", use_container_width=True):
                                update_task(t['id'], user['id'], t['title'], t['description'], t['priority'], t['category'], "In Progress", t['due_date'])
                                st.rerun()

                    with btn_c3:
                        if st.button("🗑️ Delete", key=f"t_del_{t['id']}", use_container_width=True):
                            delete_task(t['id'], user['id'])
                            st.warning("Task removed.")
                            st.rerun()
        else:
            st.info("No tasks found matching current filters.")
