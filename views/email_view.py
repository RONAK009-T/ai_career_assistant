import streamlit as st
from utils.auth import get_current_user
from utils.ui_components import render_page_header
from services.email_service import generate_professional_email

def render_email_generator():
    """Renders AI Email Generator for job applications, networking, and follow-ups."""
    user = get_current_user()
    if not user:
        return

    render_page_header(
        title="📨 AI Professional Email Generator",
        subtitle="Generate persuasive job applications, recruiter outreach, follow-ups, and thank-you emails with tailored tones.",
        badge="Career Outreach"
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 1. Email Parameters")
        email_type = st.selectbox("Email Type", [
            "Job Application / Cover Letter",
            "Recruiter Follow-Up (Post-Application)",
            "Post-Interview Thank You",
            "Networking & Informational Interview Request",
            "Salary / Offer Negotiation",
            "Professional Inquiry / Leave Request",
            "Custom Outreach"
        ])

        c_t1, c_t2 = st.columns(2)
        with c_t1:
            recipient = st.text_input("Recipient Name / Title", placeholder="Hiring Manager / Sarah Connor")
        with c_t2:
            company = st.text_input("Target Company", placeholder="Google, Acme Corp")

        tone = st.selectbox("Tone & Style", [
            "Professional & Polished",
            "Friendly & Warm",
            "Formal & Executive",
            "Short & Punchy (Under 100 words)",
            "Persuasive & Value-Focused"
        ])

        context = st.text_area("Context / Specific Background", placeholder="Applied for Senior Python Developer 5 days ago; strong match with Django & AWS...", height=100)
        key_points = st.text_area("Key Highlights to Mention", placeholder="3+ years experience, improved API performance by 40%, built open source projects...", height=80)

        if st.button("✨ Generate Professional Email", type="primary", use_container_width=True):
            with st.spinner("Drafting compelling communication..."):
                generated = generate_professional_email(email_type, recipient, company, context, key_points, tone)
                st.session_state['generated_email'] = generated
                st.success("Email generated!")

    with col2:
        st.markdown("### 2. Generated Email Output")
        email_output = st.session_state.get('generated_email', '')
        if email_output:
            st.text_area("Edit / Copy Email", value=email_output, height=420)
        else:
            st.info("Configure your email parameters on the left and click Generate.")
