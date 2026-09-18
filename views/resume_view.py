import streamlit as st
import plotly.graph_objects as go
from utils.auth import get_current_user
from utils.file_parser import extract_text_from_file
from utils.validators import validate_uploaded_file
from utils.ui_components import render_page_header, render_callout, render_skill_bar
from database.models import save_resume, save_resume_analysis, get_latest_resume_analysis, get_latest_resume
from services.resume_service import analyze_resume_content

def render_resume_analyzer():
    """Renders Resume Analyzer page with upload, extraction, and AI scoring."""
    user = get_current_user()
    if not user:
        return

    render_page_header(
        title="📄 Resume Analyzer & Diagnostic",
        subtitle="Upload your resume in PDF, DOCX, or TXT format to evaluate structural quality, detect skills, and extract improvement suggestions.",
        badge="AI Powered"
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 1. Upload Resume")
        uploaded_file = st.file_uploader(
            "Select Resume File (PDF, DOCX, TXT)",
            type=["pdf", "docx", "doc", "txt"],
            help="Maximum file size 10MB"
        )

        target_role = st.text_input(
            "Target Job Title / Role for Evaluation",
            value=user.get('target_role', 'Software Engineer')
        )

        if st.button("🚀 Analyze Resume with Gemini AI", type="primary", use_container_width=True):
            if not uploaded_file:
                st.error("Please upload a resume file first.")
            else:
                valid, msg = validate_uploaded_file(uploaded_file, allowed_types="resume")
                if not valid:
                    st.error(msg)
                else:
                    with st.spinner("Extracting resume content and querying Gemini AI..."):
                        raw_text = extract_text_from_file(uploaded_file)
                        if not raw_text or len(raw_text.strip()) < 40:
                            st.error("Failed to extract readable text from the uploaded file. Please ensure the file is not empty or password-protected.")
                        else:
                            resume_id = save_resume(user['id'], uploaded_file.name, uploaded_file.name.split('.')[-1].upper(), raw_text)
                            analysis_data = analyze_resume_content(raw_text, target_role)
                            
                            if "error" in analysis_data and not analysis_data.get("overall_score"):
                                st.error(f"Analysis failed: {analysis_data['error']}")
                            else:
                                save_resume_analysis(user['id'], resume_id, analysis_data)
                                st.success("Resume analyzed successfully!")
                                st.rerun()

    # Load latest analysis
    analysis = get_latest_resume_analysis(user['id'])

    with col2:
        st.markdown("### 2. Resume Quality Gauge")
        if analysis:
            score = analysis.get('overall_score', 75)
            
            # Plotly Gauge Chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Resume Quality Score", 'font': {'size': 18, 'color': '#F9FAFB'}},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': '#9CA3AF'},
                    'bar': {'color': "#10B981"},
                    'bgcolor': "rgba(255, 255, 255, 0.05)",
                    'borderwidth': 1,
                    'bordercolor': "rgba(255, 255, 255, 0.1)",
                    'steps': [
                        {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.2)'},
                        {'range': [50, 75], 'color': 'rgba(245, 158, 11, 0.2)'},
                        {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.2)'}
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
        else:
            st.info("Upload your resume to see your real-time AI quality benchmark.")

    st.markdown("---")

    if analysis:
        st.markdown("## 📊 Comprehensive Resume Report")

        # Summary
        if analysis.get('summary'):
            render_callout(f"<strong>Executive Summary:</strong> {analysis['summary']}", callout_type="info", icon="📝")

        col_s, col_w = st.columns(2)
        with col_s:
            st.markdown("### ✅ Key Strengths")
            for strength in analysis.get('strengths', []):
                st.markdown(f"""
                    <div style="background: rgba(16, 185, 129, 0.08); border-left: 3px solid #10B981; padding: 0.6rem 0.85rem; border-radius: 6px; margin-bottom: 0.4rem; color: #D1FAE5; font-size: 0.9rem;">
                        ✓ {strength}
                    </div>
                """, unsafe_allow_html=True)

        with col_w:
            st.markdown("### ⚠️ Areas for Improvement")
            for weakness in analysis.get('weaknesses', []):
                st.markdown(f"""
                    <div style="background: rgba(239, 68, 68, 0.08); border-left: 3px solid #EF4444; padding: 0.6rem 0.85rem; border-radius: 6px; margin-bottom: 0.4rem; color: #FEE2E2; font-size: 0.9rem;">
                        ⚠ {weakness}
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        # Detected Skills Breakdown
        st.markdown("### 🛠️ Detected Skills Matrix")
        sk_col1, sk_col2 = st.columns(2)
        with sk_col1:
            st.markdown("#### Technical Skills")
            tech_skills = analysis.get('technical_skills', [])
            if tech_skills:
                badges_html = " ".join([f'<span class="nexus-badge badge-emerald" style="margin: 0.2rem;">{s}</span>' for s in tech_skills])
                st.markdown(badges_html, unsafe_allow_html=True)
            else:
                st.markdown("<p style='color: #9CA3AF;'>No explicit technical skills detected.</p>", unsafe_allow_html=True)

        with sk_col2:
            st.markdown("#### Soft Skills")
            soft_skills = analysis.get('soft_skills', [])
            if soft_skills:
                badges_html = " ".join([f'<span class="nexus-badge badge-cyan" style="margin: 0.2rem;">{s}</span>' for s in soft_skills])
                st.markdown(badges_html, unsafe_allow_html=True)
            else:
                st.markdown("<p style='color: #9CA3AF;'>No explicit soft skills detected.</p>", unsafe_allow_html=True)

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        # Actionable Suggestions
        st.markdown("### 💡 Recommended Resume Refinements")
        for sug in analysis.get('suggestions', []):
            st.markdown(f"""
                <div style="background: rgba(6, 182, 212, 0.06); border: 1px solid rgba(6, 182, 212, 0.2); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 0.5rem; color: #CFFAFE;">
                    📌 {sug}
                </div>
            """, unsafe_allow_html=True)
