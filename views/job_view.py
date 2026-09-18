import streamlit as st
import datetime
from utils.auth import get_current_user
from utils.ui_components import render_page_header, render_callout, render_skill_bar
from database.models import get_latest_resume, save_job_description, create_job_application, get_job_applications
from services.job_service import analyze_job_description, find_matching_jobs_for_resume
from utils.file_parser import extract_text_from_file
from utils.validators import validate_uploaded_file

def render_job_analyzer():
    """Renders AI Job Matcher (Find all jobs from resume) and custom Job Description Parser."""
    user = get_current_user()
    if not user:
        return

    render_page_header(
        title="💼 AI Job Matcher & Description Analyzer",
        subtitle="Automatically find tailored job opportunities matching your resume, or deep-analyze a specific job description.",
        badge="Market Intelligence & Auto-Match"
    )

    tab_find_jobs, tab_parse_single = st.tabs([
        "🎯 AI Job Finder (Find All Matching Jobs from Resume)",
        "🔍 Single Job Description Analyzer"
    ])

    latest_resume = get_latest_resume(user['id'])

    # =========================================================================
    # TAB 1: FIND ALL MATCHING JOBS FROM RESUME
    # =========================================================================
    with tab_find_jobs:
        st.markdown("### 1. Select Resume Source & Search Filters")
        
        col_r1, col_r2 = st.columns([1, 1])
        
        with col_r1:
            resume_choice = st.radio(
                "Resume Source",
                ["Use Latest Saved Resume" if latest_resume else "Upload New Resume", "Upload / Paste New Resume"],
                index=0 if latest_resume else 1,
                horizontal=True,
                key="find_jobs_resume_src"
            )

            resume_content = ""
            if "Latest" in resume_choice and latest_resume:
                st.markdown(f"""
                    <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
                        📄 <strong>Active Resume:</strong> {latest_resume['filename']} <span style="font-size: 0.8rem; color: #9CA3AF;">({len(latest_resume['raw_text'])} chars)</span>
                    </div>
                """, unsafe_allow_html=True)
                resume_content = latest_resume['raw_text']
            else:
                up_file = st.file_uploader("Upload Resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], key="find_job_uploader")
                if up_file:
                    valid, msg = validate_uploaded_file(up_file)
                    if valid:
                        resume_content = extract_text_from_file(up_file)
                        st.success(f"Loaded {up_file.name}")
                    else:
                        st.error(msg)
                
                custom_resume_text = st.text_area("Or Paste Resume Text", height=100, placeholder="Paste resume text directly...", key="paste_resume_job_find")
                if custom_resume_text.strip():
                    resume_content = custom_resume_text.strip()

        with col_r2:
            target_role = st.text_input(
                "Target Role / Title Preference",
                value=user.get('target_role', 'Python Full Stack Developer'),
                placeholder="e.g. Python Developer, Backend Engineer, Data Scientist"
            )
            
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                work_mode = st.selectbox("Work Mode Filter", ["All", "Remote", "Hybrid", "On-site"], key="job_filter_mode")
            with f_col2:
                exp_level = st.selectbox("Experience Level", ["All", "Entry-Level / Junior", "Mid-Level (2-5 yrs)", "Senior / Lead (5+ yrs)"], key="job_filter_exp")

        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        
        if st.button("🚀 Find All Matching Jobs for My Resume", type="primary", use_container_width=True):
            if not resume_content or len(resume_content.strip()) < 20:
                st.error("Please provide or upload a resume to match against job openings.")
            else:
                with st.spinner(f"Matching candidate resume against active {target_role} market openings..."):
                    results = find_matching_jobs_for_resume(resume_content, target_role, exp_level, work_mode)
                    if "error" in results:
                        st.error(results["error"])
                    else:
                        st.session_state['matched_jobs_result'] = results
                        st.success("Found matching job opportunities!")

        # Display Matched Jobs
        match_data = st.session_state.get('matched_jobs_result')
        if match_data and match_data.get('matched_jobs'):
            st.markdown("---")
            st.markdown("## 🎯 Top Matched Job Openings")
            
            if match_data.get('candidate_summary'):
                render_callout(f"<strong>AI Match Intelligence:</strong> {match_data['candidate_summary']}", callout_type="info", icon="💡")

            # Detected skills pills
            det_skills = match_data.get('detected_skills', [])
            if det_skills:
                pills = " ".join([f'<span class="nexus-badge badge-emerald" style="margin: 0.2rem;">{s}</span>' for s in det_skills])
                st.markdown(f"<div style='margin-bottom: 1.2rem;'><strong>Extracted Resume Skills:</strong> {pills}</div>", unsafe_allow_html=True)

            jobs_list = match_data.get('matched_jobs', [])
            
            for job in jobs_list:
                score = job.get('compatibility_score', 85)
                score_color = "#10B981" if score >= 90 else ("#06B6D4" if score >= 80 else "#F59E0B")
                
                with st.container():
                    st.markdown(f"""
                        <div class="nexus-card" style="border-left: 5px solid {score_color}; margin-bottom: 1.2rem;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem;">
                                <div>
                                    <h3 style="margin: 0; color: #F8FAFC; font-size: 1.25rem;">{job.get('title')}</h3>
                                    <div style="color: #94A3B8; margin-top: 0.25rem; font-size: 0.92rem;">
                                        🏢 <strong style="color: #E2E8F0;">{job.get('company')}</strong> • 📍 {job.get('location_mode')} • ⏳ {job.get('experience_required', 'N/A')}
                                    </div>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 1.7rem; font-weight: 800; color: {score_color};">{score}%</div>
                                    <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;">Compatibility</div>
                                </div>
                            </div>
                            
                            <div style="margin-top: 0.85rem; padding: 0.6rem 0.9rem; background: rgba(0,0,0,0.3); border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); font-size: 0.92rem;">
                                💰 <strong>Expected Compensation:</strong> <span style="color: #34D399; font-weight: 700;">{job.get('salary_range')}</span>
                            </div>

                            <div style="margin-top: 0.85rem; font-size: 0.9rem; color: #E2E8F0;">
                                <strong>Why You Match:</strong> {job.get('why_matched')}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    with st.expander(f"📋 View Full Job Details & Action Items for {job.get('title')}"):
                        c_m1, c_m2 = st.columns(2)
                        with c_m1:
                            st.markdown("#### ✅ Matching Skills")
                            for sk in job.get('matching_skills', []):
                                st.markdown(f"<span class='nexus-badge badge-emerald' style='margin: 0.15rem;'>{sk}</span>", unsafe_allow_html=True)
                        with c_m2:
                            st.markdown("#### ⚠️ Skills to Brush Up")
                            for sk in job.get('missing_skills', []):
                                st.markdown(f"<span class='nexus-badge badge-amber' style='margin: 0.15rem;'>{sk}</span>", unsafe_allow_html=True)

                        st.markdown("#### 🎯 Key Responsibilities")
                        for resp in job.get('key_responsibilities', []):
                            st.markdown(f"- {resp}")

                        st.markdown("#### 📖 Full Description")
                        st.markdown(job.get('full_description', ''))

                        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                        
                        # One-Click Actions: Add to Pipeline & External Apply
                        b_col1, b_col2 = st.columns([1, 1])
                        with b_col1:
                            if st.button(f"💼 Save to My Job Applications Pipeline", key=f"save_pipeline_{job.get('id')}", use_container_width=True):
                                app_id = create_job_application(
                                    user_id=user['id'],
                                    company=job.get('company'),
                                    position=job.get('title'),
                                    job_url=job.get('application_url', ''),
                                    application_date=str(datetime.date.today()),
                                    status="Saved",
                                    notes=f"Matched via AI Job Finder with {score}% Compatibility Score.",
                                    salary_range=job.get('salary_range', '')
                                )
                                st.success(f"Saved {job.get('title')} at {job.get('company')} to your Applications Tracker!")
                        with b_col2:
                            app_url = job.get('application_url', 'https://linkedin.com/jobs')
                            st.markdown(f"""
                                <a href="{app_url}" target="_blank" style="text-decoration: none;">
                                    <div style="background: linear-gradient(135deg, #10B981, #06B6D4); color: white; text-align: center; padding: 0.55rem; border-radius: 8px; font-weight: 700; font-size: 0.9rem;">
                                        🌐 Apply on Company Portal ↗
                                    </div>
                                </a>
                            """, unsafe_allow_html=True)

        elif match_data is None:
            st.info("👆 Upload or select your resume and click 'Find All Matching Jobs for My Resume' to see tailored positions.")

    # =========================================================================
    # TAB 2: SINGLE JOB DESCRIPTION ANALYZER
    # =========================================================================
    with tab_parse_single:
        st.markdown("### 2. Parse Custom Job Description")
        
        col1, col2 = st.columns([1, 1])

        with col1:
            jd_input = st.text_area(
                "Paste Specific Job Description",
                height=250,
                placeholder="Paste the complete job listing requirements, responsibilities, and qualifications here...",
                key="single_jd_input_box"
            )

            if st.button("🔍 Parse Job Listing", type="primary", use_container_width=True, key="btn_parse_single_jd"):
                if not jd_input or len(jd_input.strip()) < 10:
                    st.error("Please provide a valid job description.")
                else:
                    with st.spinner("Deconstructing job requirements and calculating compatibility..."):
                        profile_summary = f"Role: {user.get('target_role')}. Resume Text: {latest_resume['raw_text'][:2000]}" if latest_resume else f"Role: {user.get('target_role')}"
                        parsed = analyze_job_description(jd_input, profile_summary)
                        if "error" in parsed and not parsed.get("job_title"):
                            st.error(f"Analysis failed: {parsed['error']}")
                        else:
                            st.session_state['last_parsed_jd'] = parsed
                            save_job_description(user['id'], parsed.get('job_title', 'Untitled Position'), parsed.get('company', ''), jd_input, parsed)
                            st.success("Job description parsed successfully!")

        with col2:
            st.markdown("### Extracted Metadata & Compatibility")
            parsed = st.session_state.get('last_parsed_jd')
            if parsed:
                compat = parsed.get('compatibility_score', 75)
                compat_color = "#10B981" if compat >= 75 else ("#F59E0B" if compat >= 50 else "#EF4444")
                
                st.markdown(f"""
                    <div class="nexus-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <h3 style="margin: 0; color: #F9FAFB;">{parsed.get('job_title', 'Software Role')}</h3>
                                <p style="color: #9CA3AF; margin: 0.2rem 0;">🏢 {parsed.get('company', 'Not Specified')} • 📍 {parsed.get('location_work_mode', 'Remote / Hybrid')}</p>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.6rem; font-weight: 800; color: {compat_color};">{compat}%</div>
                                <div style="font-size: 0.75rem; color: #9CA3AF;">Compatibility</div>
                            </div>
                        </div>
                        <div style="margin-top: 0.8rem; font-size: 0.9rem; color: #E5E7EB;">
                            💰 <strong>Compensation:</strong> {parsed.get('salary_range', 'Competitive / Not Disclosed')}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Paste a job description on the left and click Parse to extract metadata.")

        parsed = st.session_state.get('last_parsed_jd')
        if parsed:
            st.markdown("---")
            st.markdown("### 📋 Required Skills & Core Tech Stack")
            
            c_req, c_pref = st.columns(2)
            with c_req:
                st.markdown("#### Must-Have Skills")
                for sk in parsed.get('required_skills', []):
                    st.markdown(f"<span class='nexus-badge badge-emerald' style='margin: 0.2rem;'>{sk}</span>", unsafe_allow_html=True)
                    
            with c_pref:
                st.markdown("#### Preferred / Bonus Skills")
                for sk in parsed.get('preferred_skills', []):
                    st.markdown(f"<span class='nexus-badge badge-cyan' style='margin: 0.2rem;'>{sk}</span>", unsafe_allow_html=True)
                    
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            st.markdown("### 🎯 Key Responsibilities")
            for resp in parsed.get('key_responsibilities', []):
                st.markdown(f"- {resp}")
