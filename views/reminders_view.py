import streamlit as st
import datetime
from utils.auth import get_current_user
from utils.ui_components import render_page_header
from database.models import get_reminders, create_reminder, toggle_reminder, delete_reminder

def render_reminders():
    """Renders Smart Reminders for interviews, job deadlines, and study sprints."""
    user = get_current_user()
    if not user:
        return

    render_page_header(
        title="⏰ Smart Reminders & Deadlines",
        subtitle="Track upcoming interviews, job submission deadlines, and scheduled study sessions.",
        badge="Notification Center"
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### ➕ Set New Reminder")
        with st.form("new_reminder_form"):
            rem_title = st.text_input("Reminder Title", placeholder="e.g. Technical Interview with Stripe")
            rem_type = st.selectbox("Reminder Category", ["Job Application", "Interview", "Study Session", "Task Deadline", "Custom"])
            due_date = st.date_input("Date", min_value=datetime.date.today())
            due_time = st.time_input("Time", value=datetime.time(10, 0))
            notes = st.text_area("Notes / Meeting Link", placeholder="Zoom link or prep notes...", height=80)

            submitted = st.form_submit_button("Set Reminder", use_container_width=True)
            if submitted:
                if not rem_title:
                    st.error("Please enter a reminder title.")
                else:
                    due_dt_str = f"{due_date} {due_time.strftime('%H:%M')}"
                    create_reminder(user['id'], rem_title, rem_type, due_dt_str, notes)
                    st.success(f"Reminder set for {due_dt_str}!")
                    st.rerun()

    with col2:
        st.markdown("### 🔔 Active Reminders")
        type_filter = st.selectbox("Filter Category", ["All", "Job Application", "Interview", "Study Session", "Task Deadline", "Custom"])
        
        reminders = get_reminders(user['id'], reminder_type=type_filter)
        if reminders:
            for r in reminders:
                is_done = bool(r.get('is_completed'))
                status_icon = "✅" if is_done else "🔔"
                with st.expander(f"{status_icon} {r['title']} — {r['due_date']}", expanded=not is_done):
                    st.markdown(f"**Type:** `{r.get('reminder_type')}`")
                    if r.get('notes'):
                        st.markdown(f"**Notes:** {r['notes']}")

                    btn_c1, btn_c2 = st.columns(2)
                    with btn_c1:
                        lbl = "Mark Incomplete ⏳" if is_done else "Mark Done ✅"
                        if st.button(lbl, key=f"tog_{r['id']}", use_container_width=True):
                            toggle_reminder(r['id'], user['id'], not is_done)
                            st.rerun()
                    with btn_c2:
                        if st.button("🗑️ Delete", key=f"del_rem_{r['id']}", use_container_width=True):
                            delete_reminder(r['id'], user['id'])
                            st.warning("Reminder deleted.")
                            st.rerun()
        else:
            st.info("No reminders found.")
