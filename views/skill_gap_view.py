import streamlit as st
from utils.auth import get_current_user
from utils.ui_components import render_page_header, render_callout, render_skill_bar
from database.models import get_user_skills, upsert_user_skill, delete_user_skill
from services.career_service import analyze_skill_gaps

def render_skill_gap():
    """Renders Visual Skill Gap Matrix and learning prioritization."""
    user = get_current_user()
    if not user:
        return

    render_page_header(
        title="🧠 Skill Gap Analyzer",
        subtitle="Compare your current skill inventory against standard industry benchmarks for your target role.",
        badge="Competency Matrix"
    )

    user_skills = get_user_skills(user['id'])
    skill_names = [s['skill_name'] for s in user_skills]

    col_ctrl1, col_ctrl2 = st.columns([2, 1])

    with col_ctrl1:
        st.markdown(f"**Target Role:** `{user.get('target_role', 'Software Engineer')}`")
        if st.button("⚡ Run AI Skill Gap Diagnosis", type="primary"):
            with st.spinner("Benchmarking skills against industry expectations..."):
                gap_data = analyze_skill_gaps(skill_names, user.get('target_role', 'Software Engineer'))
                if "error" in gap_data:
                    st.error(gap_data["error"])
                else:
                    for sk in gap_data.get('skills', []):
                        upsert_user_skill(
                            user_id=user['id'],
                            skill_name=sk.get('name'),
                            category=sk.get('category', 'Technical'),
                            status=sk.get('status', 'Need Improvement'),
                            proficiency_score=sk.get('proficiency_score', 50)
                        )
                    st.session_state['skill_gap_recs'] = gap_data.get('priority_recommendations', [])
                    st.success("Skill gap analysis updated!")
                    st.rerun()

    with col_ctrl2:
        with st.expander("➕ Add / Update Custom Skill"):
            new_sk = st.text_input("Skill Name", placeholder="e.g. Docker, React, AWS")
            new_cat = st.selectbox("Category", ["Core Language", "Web Framework", "Database", "DevOps & Cloud", "Architecture", "Soft Skills"])
            new_status = st.selectbox("Current Proficiency Level", ["Mastered", "Strong", "Need Improvement", "Missing"])
            score_map = {"Mastered": 90, "Strong": 75, "Need Improvement": 50, "Missing": 20}
            if st.button("Save Skill", use_container_width=True):
                if new_sk:
                    upsert_user_skill(user['id'], new_sk, new_cat, new_status, score_map[new_status])
                    st.success(f"Added {new_sk}")
                    st.rerun()

    recs = st.session_state.get('skill_gap_recs', [])
    if recs:
        rec_html = "<br>• ".join(recs)
        render_callout(f"<strong>Top Learning Priorities:</strong><br>• {rec_html}", callout_type="info", icon="🎯")

    st.markdown("---")

    # Categories breakdown
    user_skills = get_user_skills(user['id'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    mastered = [s for s in user_skills if s.get('status') == 'Mastered']
    strong = [s for s in user_skills if s.get('status') == 'Strong']
    improve = [s for s in user_skills if s.get('status') == 'Need Improvement']
    missing = [s for s in user_skills if s.get('status') == 'Missing']

    with col1:
        st.markdown("### 🏆 Mastered (85%+)")
        if mastered:
            for s in mastered:
                render_skill_bar(s['skill_name'], "Mastered", s['proficiency_score'], color="emerald")
        else:
            st.markdown("<p style='color: #6B7280; font-size: 0.85rem;'>None recorded</p>", unsafe_allow_html=True)

    with col2:
        st.markdown("### 💪 Strong (65-84%)")
        if strong:
            for s in strong:
                render_skill_bar(s['skill_name'], "Strong", s['proficiency_score'], color="cyan")
        else:
            st.markdown("<p style='color: #6B7280; font-size: 0.85rem;'>None recorded</p>", unsafe_allow_html=True)

    with col3:
        st.markdown("### 📈 Need Improvement")
        if improve:
            for s in improve:
                render_skill_bar(s['skill_name'], "Improving", s['proficiency_score'], color="amber")
        else:
            st.markdown("<p style='color: #6B7280; font-size: 0.85rem;'>None recorded</p>", unsafe_allow_html=True)

    with col4:
        st.markdown("### ❌ Missing (Priority)")
        if missing:
            for s in missing:
                render_skill_bar(s['skill_name'], "Missing", s['proficiency_score'], color="rose")
        else:
            st.markdown("<p style='color: #6B7280; font-size: 0.85rem;'>No critical gaps</p>", unsafe_allow_html=True)
