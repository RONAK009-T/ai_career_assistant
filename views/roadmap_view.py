import streamlit as st
from utils.auth import get_current_user
from utils.ui_components import render_page_header, render_callout
from database.models import get_latest_career_roadmap, save_career_roadmap, get_user_skills
from services.career_service import generate_career_roadmap

def render_career_roadmap():
    """Renders personalized Career Roadmap generator and interactive stages."""
    user = get_current_user()
    if not user:
        return

    render_page_header(
        title="🚀 AI Career Roadmap & Learning Path",
        subtitle="Generate personalized, step-by-step career acceleration roadmaps with progressive milestones, projects, and interview preparation.",
        badge="Career Acceleration"
    )

    career_options = [
        "Full Stack Developer",
        "Python Developer",
        "Backend Engineer",
        "Frontend Engineer (React/Next.js)",
        "Data Scientist",
        "Data Analyst",
        "AI / Machine Learning Engineer",
        "DevOps & Cloud Engineer",
        "Cybersecurity Specialist",
        "Custom..."
    ]

    col_top1, col_top2 = st.columns([2, 1])

    with col_top1:
        target_selection = st.selectbox(
            "Select Target Career Track",
            career_options,
            index=0 if user.get('target_role') not in career_options else career_options.index(user.get('target_role'))
        )
        if target_selection == "Custom...":
            target_role = st.text_input("Enter Custom Career Title", value="Mobile App Developer")
        else:
            target_role = target_selection

    with col_top2:
        exp_level = st.selectbox("Current Experience Level", [
            "Beginner / Student",
            "Junior Developer (1-2 yrs)",
            "Mid-Level Professional (3-5 yrs)",
            "Career Switcher / Transitioning"
        ])

    if st.button("✨ Generate Comprehensive AI Career Roadmap", type="primary", use_container_width=True):
        with st.spinner(f"Designing custom curriculum and milestones for '{target_role}'..."):
            skills = [s['skill_name'] for s in get_user_skills(user['id'])]
            roadmap_data = generate_career_roadmap(target_role, skills, exp_level)
            if "error" in roadmap_data and not roadmap_data.get("stages"):
                st.error(f"Generation failed: {roadmap_data['error']}")
            else:
                save_career_roadmap(user['id'], target_role, roadmap_data)
                st.success("Career roadmap generated and saved!")
                st.rerun()

    # Load latest saved roadmap
    saved = get_latest_career_roadmap(user['id'], target_role) or get_latest_career_roadmap(user['id'])

    if saved and saved.get('roadmap_data'):
        data = saved['roadmap_data']
        st.markdown("---")
        st.markdown(f"## 🗺️ Roadmap: {data.get('target_role', target_role)}")
        st.markdown(f"**Estimated Timeline:** `{data.get('estimated_timeline', '4 - 6 Months')}`")

        # Required Skills
        req_skills = data.get('required_skills', [])
        if req_skills:
            badges = " ".join([f'<span class="nexus-badge badge-cyan" style="margin: 0.2rem;">{s}</span>' for s in req_skills])
            st.markdown(f"<div style='margin-bottom: 1.2rem;'><strong>Core Competencies:</strong> {badges}</div>", unsafe_allow_html=True)

        # 3 Stages
        stages = data.get('stages', [])
        for stage in stages:
            st.markdown(f"""
                <div class="nexus-card" style="border-left: 4px solid #10B981;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                        <h3 style="margin: 0; color: #34D399;">{stage.get('title', 'Stage')}</h3>
                        <span class="nexus-badge badge-emerald">⏳ {stage.get('duration', '4 Weeks')}</span>
                    </div>
                    <p style="color: #E5E7EB; margin-bottom: 0.5rem;">
                        <strong>Key Focus Areas:</strong> {', '.join(stage.get('focus_areas', []))}
                    </p>
                    <p style="color: #9CA3AF; font-size: 0.9rem; margin-bottom: 0.5rem;">
                        <strong>Recommended Topics:</strong> {', '.join(stage.get('recommended_topics', []))}
                    </p>
                    <div style="background: rgba(0,0,0,0.3); padding: 0.75rem 1rem; border-radius: 8px; margin-top: 0.75rem; border: 1px dashed rgba(16,185,129,0.3);">
                        <strong style="color: #FBBF24;">🛠️ Practice Milestone Project:</strong> {stage.get('practice_project', {}).get('title', 'Project')}
                        <div style="color: #D1D5DB; font-size: 0.85rem; margin-top: 0.2rem;">{stage.get('practice_project', {}).get('description', '')}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        col_p, col_i = st.columns(2)
        with col_p:
            st.markdown("### 💼 Portfolio Recommendations")
            for p in data.get('portfolio_recommendations', []):
                st.markdown(f"- {p}")

        with col_i:
            st.markdown("### 🎤 Interview Prep Focus")
            for item in data.get('interview_prep_topics', []):
                st.markdown(f"- {item}")
