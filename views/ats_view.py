import streamlit as st
import plotly.graph_objects as go
from utils.auth import get_current_user
from utils.file_parser import extract_text_from_file
from utils.validators import validate_uploaded_file
from utils.ui_components import render_page_header, render_callout, render_skill_bar
from database.models import get_latest_resume, get_latest_ats_result, save_ats_result, save_job_description
from services.ats_service import check_ats_compatibility

def render_ats_checker():
    """Renders ATS Score Checker comparing user resume against job description."""
    user = get_current_user()
    if not user:
        return

    render_page_header(
        title="🎯 ATS Score Checker & Keyword Matcher",
        subtitle="Compare your resume against a target job description to compute ATS score, matching keywords, missing competencies, and formatting advice.",
        badge="Recruiter System Simulation"
    )

    latest_resume = get_latest_resume(user['id'])

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 1. Candidate Resume")
        resume_source = st.radio(
            "Resume Source",
            ["Use Latest Saved Resume" if latest_resume else "Upload New Resume", "Upload New Resume"],
            index=0 if latest_resume else 1,
            horizontal=True
        )

        resume_text = ""
        resume_id = None
        if "Latest" in resume_source and latest_resume:
            st.success(f"Loaded: {latest_resume['filename']}")
            resume_text = latest_resume['raw_text']
            resume_id = latest_resume['id']
        else:
            uploaded_res = st.file_uploader("Upload Resume File", type=["pdf", "docx", "txt"], key="ats_resume_uploader")
            if uploaded_res:
                valid, msg = validate_uploaded_file(uploaded_res)
                if valid:
                    resume_text = extract_text_from_file(uploaded_res)
                    st.info(f"Extracted {len(resume_text)} characters from {uploaded_res.name}")
                else:
                    st.error(msg)

        st.markdown("### 2. Target Job Description")
        job_title = st.text_input("Job Title", value=user.get('target_role', 'Software Engineer'), placeholder="e.g. Senior Backend Engineer")
        jd_text = st.text_area("Paste Full Job Description", height=200, placeholder="Paste the job requirements, responsibilities, and qualifications here...")

        if st.button("⚡ Run ATS Compatibility Check", type="primary", use_container_width=True):
            if not resume_text:
                st.error("Please provide or upload a resume.")
            elif not jd_text or len(jd_text.strip()) < 30:
                st.error("Please paste the job description (at least 30 characters).")
            else:
                with st.spinner("Analyzing keyword density, semantic alignment, and ATS passability..."):
                    ats_data = check_ats_compatibility(resume_text, jd_text, job_title)
                    if "error" in ats_data and not ats_data.get("ats_score"):
                        st.error(f"ATS check failed: {ats_data['error']}")
                    else:
                        jd_id = save_job_description(user['id'], job_title, "", jd_text)
                        save_ats_result(user['id'], resume_id, jd_id, job_title, ats_data)
                        st.success("ATS Evaluation Complete!")
                        st.rerun()

    # Load latest ATS results
    ats_result = get_latest_ats_result(user['id'])

    with col2:
        st.markdown("### 3. ATS Match Scoreboard")
        if ats_result:
            score = ats_result.get('ats_score', 0)
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"ATS Score: {ats_result.get('job_title', 'Target Role')}", 'font': {'size': 16, 'color': '#F9FAFB'}},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': '#9CA3AF'},
                    'bar': {'color': "#06B6D4"},
                    'steps': [
                        {'range': [0, 60], 'color': 'rgba(239, 68, 68, 0.2)'},
                        {'range': [60, 80], 'color': 'rgba(245, 158, 11, 0.2)'},
                        {'range': [80, 100], 'color': 'rgba(16, 185, 129, 0.2)'}
                    ]
                }
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#F9FAFB'),
                height=220,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

            # Sub-metrics
            kw_match = ats_result.get('keyword_match_pct', 0)
            sk_match = ats_result.get('skill_match_pct', 0)
            exp_match = ats_result.get('experience_match_pct', 0)
            
            sub_c1, sub_c2, sub_c3 = st.columns(3)
            with sub_c1:
                st.metric("Keywords Match", f"{kw_match}%")
            with sub_c2:
                st.metric("Skills Alignment", f"{sk_match}%")
            with sub_c3:
                st.metric("Experience Fit", f"{exp_match}%")
        else:
            st.info("Run an ATS check above to view your job-specific alignment metrics.")

    if ats_result:
        st.markdown("---")
        st.markdown("## 🔍 Deep Match Analysis")

        col_m, col_g = st.columns(2)
        with col_m:
            st.markdown("### ✅ Matching Skills & Strengths")
            matching_skills = ats_result.get('matching_skills', [])
            if matching_skills:
                m_badges = " ".join([f'<span class="nexus-badge badge-emerald" style="margin: 0.2rem;">{s}</span>' for s in matching_skills])
                st.markdown(m_badges, unsafe_allow_html=True)
            else:
                st.markdown("<p style='color: #9CA3AF;'>No direct matching keywords detected.</p>", unsafe_allow_html=True)

        with col_g:
            st.markdown("### ❌ Missing Keywords & Critical Skills")
            missing_skills = ats_result.get('missing_skills', [])
            missing_kws = ats_result.get('missing_keywords', [])
            all_missing = list(set(missing_skills + missing_kws))
            if all_missing:
                miss_badges = " ".join([f'<span class="nexus-badge badge-rose" style="margin: 0.2rem;">{s}</span>' for s in all_missing])
                st.markdown(miss_badges, unsafe_allow_html=True)
            else:
                st.markdown("<p style='color: #10B981;'>All core job requirements present!</p>", unsafe_allow_html=True)

        st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

        col_warn, col_rec = st.columns(2)
        with col_warn:
            st.markdown("### ⚠️ ATS Formatting & Parsing Warnings")
            for w in ats_result.get('formatting_warnings', []):
                st.markdown(f"""
                    <div style="background: rgba(245, 158, 11, 0.08); border-left: 3px solid #F59E0B; padding: 0.6rem 0.85rem; border-radius: 6px; margin-bottom: 0.4rem; color: #FEF3C7; font-size: 0.88rem;">
                        ⚠ {w}
                    </div>
                """, unsafe_allow_html=True)

        with col_rec:
            st.markdown("### 💡 Strategic Resume Recommendations")
            for r in ats_result.get('recommendations', []):
                st.markdown(f"""
                    <div style="background: rgba(6, 182, 212, 0.08); border-left: 3px solid #06B6D4; padding: 0.6rem 0.85rem; border-radius: 6px; margin-bottom: 0.4rem; color: #CFFAFE; font-size: 0.88rem;">
                        📌 {r}
                    </div>
                """, unsafe_allow_html=True)
