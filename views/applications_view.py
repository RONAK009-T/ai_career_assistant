import streamlit as st
import datetime
from utils.auth import get_current_user
from utils.ui_components import render_page_header
from database.models import (
    get_job_applications,
    create_job_application,
    update_job_application,
    delete_job_application
)

def render_career_applications():
    """Renders Career Job Application Tracker with pipeline metrics and status progression."""
    user = get_current_user()
    if not user:
        return

    render_page_header(
        title="💼 Job Application Pipeline Tracker",
        subtitle="Manage active job submissions, track interview rounds, salary offers, and conversion metrics.",
        badge="Career Pipeline"
    )

    apps = get_job_applications(user['id'])

    # Statistics Bar
    total_apps = len(apps)
    applied_count = len([a for a in apps if a.get('status') == 'Applied'])
    interviews = len([a for a in apps if a.get('status') == 'Interview'])
    selected = len([a for a in apps if a.get('status') == 'Selected'])
    rejected = len([a for a in apps if a.get('status') == 'Rejected'])

    s_c1, s_c2, s_c3, s_c4, s_c5 = st.columns(5)
    with s_c1:
        st.metric("Total Submitted", total_apps)
    with s_c2:
        st.metric("Under Review", applied_count)
    with s_c3:
        st.metric("Interviews", interviews)
    with s_c4:
        st.metric("Offers / Selected", selected)
    with s_c5:
        st.metric("Archived / Rejected", rejected)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### ➕ Log Job Application")
        with st.form("new_app_form"):
            company = st.text_input("Company Name", placeholder="e.g. Microsoft, Uber")
            position = st.text_input("Role / Title", placeholder="e.g. Python Backend Engineer")
            job_url = st.text_input("Job Posting Link", placeholder="https://careers.company.com/...")
            app_date = st.date_input("Application Date", value=datetime.date.today())
            status = st.selectbox("Current Status", ["Saved", "Applied", "Screening", "Interview", "Selected", "Rejected"])
            interview_date = st.text_input("Interview Date (if scheduled)", placeholder="e.g. 2026-08-25 14:00")
            salary_range = st.text_input("Target Compensation / Range", placeholder="e.g. $120,000 - $140,000")
            notes = st.text_area("Notes", placeholder="Referral info, recruiter contact...", height=70)

            submitted = st.form_submit_button("Add Application", use_container_width=True)
            if submitted:
                if not company or not position:
                    st.error("Please enter both Company and Position.")
                else:
                    create_job_application(
                        user_id=user['id'],
                        company=company,
                        position=position,
                        job_url=job_url,
                        application_date=str(app_date),
                        status=status,
                        interview_date=interview_date,
                        notes=notes,
                        salary_range=salary_range
                    )
                    st.success(f"Application for {company} logged!")
                    st.rerun()

    with col2:
        st.markdown("### 📋 Application Pipeline")
        status_filter = st.selectbox("Filter by Status", ["All", "Saved", "Applied", "Screening", "Interview", "Selected", "Rejected"])
        
        filtered_apps = get_job_applications(user['id'], status=status_filter)
        if filtered_apps:
            for a in filtered_apps:
                st_color = {
                    "Selected": "badge-emerald",
                    "Interview": "badge-cyan",
                    "Screening": "badge-violet",
                    "Applied": "badge-amber",
                    "Rejected": "badge-rose"
                }.get(a.get('status'), 'badge-cyan')

                with st.expander(f"{a['company']} — {a['position']} [{a.get('status')}]"):
                    st.markdown(f"**Applied On:** `{a.get('application_date')}` • **Status:** <span class='nexus-badge {st_color}'>{a.get('status')}</span>", unsafe_allow_html=True)
                    if a.get('salary_range'):
                        st.markdown(f"**Salary / Comp:** `{a.get('salary_range')}`")
                    if a.get('job_url'):
                        st.markdown(f"**Posting Link:** [{a.get('job_url')}]({a.get('job_url')})")
                    if a.get('interview_date'):
                        st.markdown(f"**Upcoming Interview:** `{a.get('interview_date')}`")
                    if a.get('notes'):
                        st.markdown(f"**Notes:** {a.get('notes')}")

                    with st.form(f"update_app_{a['id']}"):
                        up_stat = st.selectbox("Update Status", ["Saved", "Applied", "Screening", "Interview", "Selected", "Rejected"], index=["Saved", "Applied", "Screening", "Interview", "Selected", "Rejected"].index(a.get('status', 'Applied')))
                        up_notes = st.text_input("Update Notes", value=a.get('notes', ''))
                        
                        btn_u1, btn_u2 = st.columns(2)
                        with btn_u1:
                            if st.form_submit_button("💾 Save Update", use_container_width=True):
                                update_job_application(a['id'], user['id'], a['company'], a['position'], a['job_url'], a['application_date'], up_stat, a['interview_date'], up_notes, a['salary_range'])
                                st.success("Updated!")
                                st.rerun()
                        with btn_u2:
                            if st.form_submit_button("🗑️ Delete", use_container_width=True):
                                delete_job_application(a['id'], user['id'])
                                st.warning("Application deleted.")
                                st.rerun()
        else:
            st.info("No applications found.")
