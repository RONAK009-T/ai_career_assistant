import streamlit as st
from utils.auth import get_current_user
from utils.ui_components import render_page_header, render_callout
from database.models import get_tasks
from services.productivity_service import generate_daily_schedule

def render_productivity_assistant():
    """Renders AI Daily Plan and schedule optimizer based on user tasks."""
    user = get_current_user()
    if not user:
        return

    render_page_header(
        title="⚡ AI Productivity & Daily Schedule Assistant",
        subtitle="Leverage Gemini AI to analyze your pending tasks and synthesize an optimal, time-blocked daily schedule.",
        badge="Executive Coach"
    )

    tasks = get_tasks(user['id'], status="Pending")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 🎯 Daily Focus Configuration")
        focus_goal = st.text_input("Today's Top Priority", placeholder="e.g. Finish Resume + Apply to 3 Companies")
        st.markdown(f"**Active Pending Tasks:** `{len(tasks)} items`")

        if st.button("🤖 Generate AI Daily Plan", type="primary", use_container_width=True):
            with st.spinner("Synthesizing optimal focus blocks and timeline..."):
                plan = generate_daily_schedule(tasks, focus_goal)
                if "error" in plan and not plan.get("schedule"):
                    st.error(f"Plan generation failed: {plan['error']}")
                else:
                    st.session_state['daily_ai_plan'] = plan
                    st.success("Daily AI Schedule ready!")

    with col2:
        st.markdown("### 📅 Optimized Daily Schedule")
        plan = st.session_state.get('daily_ai_plan')
        if plan and plan.get('schedule'):
            render_callout(f"<strong>Top Focus Objective:</strong> {plan.get('top_focus')}", callout_type="info", icon="🎯")

            for item in plan.get('schedule', []):
                t_type = item.get('type', 'Focus')
                color_map = {
                    "Focus": "badge-emerald",
                    "Break": "badge-amber",
                    "Career": "badge-cyan",
                    "Learning": "badge-violet",
                    "Interview": "badge-rose"
                }
                badge_style = color_map.get(t_type, 'badge-cyan')
                
                st.markdown(f"""
                    <div style="background: rgba(17, 24, 39, 0.7); border: 1px solid rgba(255,255,255,0.06); padding: 0.85rem 1.1rem; border-radius: 8px; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: #F9FAFB; font-size: 0.95rem;">⏰ {item.get('time')}</strong>
                            <div style="color: #D1D5DB; margin-top: 0.2rem; font-size: 0.9rem;">{item.get('activity')}</div>
                        </div>
                        <span class="nexus-badge {badge_style}">{t_type}</span>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
            st.markdown("### 💡 Time Management Tips")
            for tip in plan.get('time_management_tips', []):
                st.markdown(f"- {tip}")
        else:
            st.info("Click 'Generate AI Daily Plan' to synthesize your schedule for today.")
